from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem, CartItem, Product, User
from app.schemas import (
    CheckoutRequest, BuyNowRequest, OrderOut, OrderItemOut, OrderStatusUpdate
)
from app.deps import get_current_user, require_buyer, require_seller, require_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

VALID_TRANSITIONS = {
    "pending": "confirmed",
    "confirmed": "shipped",
    "shipped": "delivered",
}


def _to_order_out(order: Order, seller_id: Optional[int] = None) -> OrderOut:
    items_out = []
    total = 0.0
    for item in order.items:
        # If seller_id is given (and not admin), filter items to only that seller's products
        if seller_id is not None and item.product and item.product.seller_id != seller_id:
            continue
        subtotal = round(item.unit_price * item.quantity, 2)
        total += subtotal
        items_out.append(
            OrderItemOut(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )

    # Use calculated total if items were filtered, or original total
    display_total = round(total, 2) if seller_id is not None else order.total

    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total=display_total,
        shipping_address=order.shipping_address,
        destination_country=order.destination_country,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items_out,
        buyer_name=order.user.full_name if order.user else None,
        buyer_email=order.user.email if order.user else None,
    )


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(
    checkout_in: CheckoutRequest,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty. Add items before checking out.",
        )

    # Validate ALL stock first before making any modifications
    for ci in cart_items:
        product = ci.product
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{ci.product.name if ci.product else 'Unknown'}' is no longer available.",
            )
        if product.stock < ci.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock}, in cart: {ci.quantity}.",
            )

    # Transaction: Deduct stock, build order and order items, clear cart
    total_amount = 0.0
    for ci in cart_items:
        ci.product.stock -= ci.quantity
        total_amount += ci.product.price * ci.quantity

    order = Order(
        user_id=current_user.id,
        status="pending",
        total=round(total_amount, 2),
        shipping_address=checkout_in.shipping_address,
        destination_country=checkout_in.destination_country,
    )
    db.add(order)
    db.flush()

    for ci in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=ci.product.id,
            product_name=ci.product.name,
            unit_price=ci.product.price,
            quantity=ci.quantity,
        )
        db.add(order_item)

    # Clear user's cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()

    db.commit()
    db.refresh(order)
    return _to_order_out(order)


@router.post("/buy-now", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def buy_now(
    buy_in: BuyNowRequest,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == buy_in.product_id).first()
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or unavailable.",
        )

    if product.stock < buy_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for '{product.name}'. Available: {product.stock}, requested: {buy_in.quantity}.",
        )

    # Deduct stock and create order in single transaction
    product.stock -= buy_in.quantity
    total_amount = round(product.price * buy_in.quantity, 2)

    order = Order(
        user_id=current_user.id,
        status="pending",
        total=total_amount,
        shipping_address=buy_in.shipping_address,
        destination_country=buy_in.destination_country,
    )
    db.add(order)
    db.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        unit_price=product.price,
        quantity=buy_in.quantity,
    )
    db.add(order_item)

    db.commit()
    db.refresh(order)
    return _to_order_out(order)


@router.get("/my", response_model=List[OrderOut])
def get_my_orders(
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.id.desc()).all()
    return [_to_order_out(o) for o in orders]


@router.get("/received", response_model=List[OrderOut])
def get_received_orders(
    seller: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    if seller.role == "admin":
        orders = db.query(Order).order_by(Order.id.desc()).all()
        return [_to_order_out(o) for o in orders]

    # Seller sees orders containing their products (only their items returned)
    orders = db.query(Order).join(OrderItem).join(Product).filter(
        Product.seller_id == seller.id
    ).distinct().order_by(Order.id.desc()).all()

    return [_to_order_out(o, seller_id=seller.id) for o in orders]


@router.get("", response_model=List[OrderOut])
def get_all_orders(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).order_by(Order.id.desc()).all()
    return [_to_order_out(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if current_user.role == "admin":
        return _to_order_out(order)

    if current_user.role == "buyer":
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot view orders belonging to other buyers.",
            )
        return _to_order_out(order)

    if current_user.role == "seller":
        # Check if seller has items in this order
        has_items = any(
            item.product and item.product.seller_id == current_user.id
            for item in order.items
        )
        if not has_items:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have items in this order.",
            )
        return _to_order_out(order, seller_id=current_user.id)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if current_user.role == "seller":
        # Ensure seller owns products in this order
        has_items = any(
            item.product and item.product.seller_id == current_user.id
            for item in order.items
        )
        if not has_items:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update status for orders that do not contain your items.",
            )

    target_status = status_in.status
    current_status = order.status

    if current_status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update status of a cancelled order.",
        )

    expected_next = VALID_TRANSITIONS.get(current_status)
    if not expected_next or target_status != expected_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition. Cannot skip from '{current_status}' to '{target_status}'. Expected next status: '{expected_next}'.",
        )

    order.status = target_status
    db.commit()
    db.refresh(order)

    seller_filter = current_user.id if current_user.role == "seller" else None
    return _to_order_out(order, seller_id=seller_filter)


@router.patch("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Permission check: buyer can cancel own order; admin can cancel any
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own orders.",
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order in '{order.status}' status. Only 'pending' orders can be cancelled.",
        )

    # Return stock to products
    for item in order.items:
        if item.product:
            item.product.stock += item.quantity

    order.status = "cancelled"
    db.commit()

    return {"message": "Order cancelled successfully and stock has been restored."}
