from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import Product, Category, User, OrderItem
from app.schemas import ProductCreate, ProductUpdate, ProductOut, CategoryOut
from app.deps import get_current_user, require_seller, require_admin, get_optional_current_user

router = APIRouter(prefix="/products", tags=["Products & Catalogue"])


def _to_product_out(p: Product) -> ProductOut:
    return ProductOut(
        id=p.id,
        seller_id=p.seller_id,
        category_id=p.category_id,
        name=p.name,
        description=p.description,
        price=p.price,
        stock=p.stock,
        light_requirement=p.light_requirement,
        pet_safe=p.pet_safe,
        tree_purpose=p.tree_purpose,
        image_url=p.image_url,
        is_active=p.is_active,
        created_at=p.created_at,
        updated_at=p.updated_at,
        category_name=p.category.name if p.category else None,
        seller_name=p.seller.full_name if p.seller else None,
    )


@router.get("/categories", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.id.asc()).all()


@router.get("", response_model=List[ProductOut])
def list_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    light_requirement: Optional[str] = None,
    pet_safe: Optional[bool] = None,
    tree_purpose: Optional[str] = None,
    include_inactive: bool = False,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    # Inactive products visible only to admins if explicitly requested
    if include_inactive and current_user and current_user.role == "admin":
        pass
    else:
        query = query.filter(Product.is_active == True)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if light_requirement:
        query = query.filter(Product.light_requirement == light_requirement.lower())

    if pet_safe is not None:
        query = query.filter(Product.pet_safe == pet_safe)

    if tree_purpose:
        if tree_purpose.lower() == "none":
            query = query.filter(Product.tree_purpose.is_(None))
        else:
            query = query.filter(Product.tree_purpose == tree_purpose.lower())

    products = query.order_by(Product.id.desc()).all()
    return [_to_product_out(p) for p in products]


@router.get("/seller/me", response_model=List[ProductOut])
def list_seller_listings(
    seller: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    if seller.role == "admin":
        # Admin viewing all listings
        products = db.query(Product).order_by(Product.id.desc()).all()
    else:
        products = db.query(Product).filter(Product.seller_id == seller.id).order_by(Product.id.desc()).all()
    return [_to_product_out(p) for p in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return _to_product_out(product)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == product_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified category does not exist",
        )

    tree_purp = product_in.tree_purpose
    if tree_purp == "none":
        tree_purp = None

    product = Product(
        seller_id=current_user.id,
        category_id=product_in.category_id,
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        stock=product_in.stock,
        light_requirement=product_in.light_requirement,
        pet_safe=product_in.pet_safe,
        tree_purpose=tree_purp,
        image_url=product_in.image_url,
        is_active=product_in.is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return _to_product_out(product)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Check ownership (unless admin)
    if current_user.role != "admin" and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own listings",
        )

    update_data = product_in.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        cat = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified category does not exist",
            )

    if "tree_purpose" in update_data and update_data["tree_purpose"] == "none":
        update_data["tree_purpose"] = None

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return _to_product_out(product)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Check ownership (unless admin)
    if current_user.role != "admin" and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own listings",
        )

    # Check if product is in any past orders
    has_orders = db.query(OrderItem).filter(OrderItem.product_id == product_id).first() is not None
    if has_orders:
        product.is_active = False
        db.commit()
        return {
            "message": "Product is in past orders; it was hidden instead so order history stays correct.",
            "action": "hidden",
            "is_active": False,
        }

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully.", "action": "deleted"}


@router.patch("/{product_id}/toggle-active", response_model=ProductOut)
def toggle_product_active(
    product_id: int,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if current_user.role != "admin" and product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own listings",
        )

    product.is_active = not product.is_active
    db.commit()
    db.refresh(product)
    return _to_product_out(product)
