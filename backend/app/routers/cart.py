from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CartItem, Product, User
from app.schemas import (
    CartItemAdd, CartItemUpdate, CartItemOut, CartSummaryOut, ProductOut
)
from app.deps import require_buyer
from app.routers.products import _to_product_out

router = APIRouter(prefix="/cart", tags=["Cart"])


def _to_cart_item_out(ci: CartItem) -> CartItemOut:
    prod_out = _to_product_out(ci.product)
    item_total = round(ci.quantity * ci.product.price, 2)
    return CartItemOut(
        id=ci.id,
        user_id=ci.user_id,
        product_id=ci.product_id,
        quantity=ci.quantity,
        product=prod_out,
        item_total=item_total,
    )


@router.get("", response_model=CartSummaryOut)
def get_cart(
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    # Filter out items where product may have been deleted or deactivated
    valid_items = [ci for ci in items if ci.product is not None]
    items_out = [_to_cart_item_out(ci) for ci in valid_items]
    total = sum(i.item_total for i in items_out)
    return CartSummaryOut(
        items=items_out,
        total=round(total, 2),
        currency="NPR"
    )


@router.post("", response_model=CartItemOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_in: CartItemAdd,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or currently unavailable",
        )

    if product.stock < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is currently out of stock",
        )

    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item_in.product_id
    ).first()

    if existing_item:
        new_quantity = existing_item.quantity + item_in.quantity
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add {item_in.quantity} more. Total in cart ({new_quantity}) would exceed available stock ({product.stock}).",
            )
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return _to_cart_item_out(existing_item)

    if item_in.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity ({item_in.quantity}) exceeds available stock ({product.stock}).",
        )

    new_cart_item = CartItem(
        user_id=current_user.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return _to_cart_item_out(new_cart_item)


@router.put("/{item_id}", response_model=CartItemOut)
def update_cart_item(
    item_id: int,
    item_in: CartItemUpdate,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    product = cart_item.product
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This product is no longer active.",
        )

    if item_in.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity ({item_in.quantity}) exceeds available stock ({product.stock}).",
        )

    cart_item.quantity = item_in.quantity
    db.commit()
    db.refresh(cart_item)
    return _to_cart_item_out(cart_item)


@router.delete("/{item_id}")
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("")
def clear_cart(
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
