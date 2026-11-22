from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models import Order, OrderItem, User, Product, Diagnosis, Symptom
from app.schemas import AdminReportOut, TopProductReport, CommonDiagnosisReport
from app.deps import require_admin
from app.routers.products import _to_product_out

router = APIRouter(prefix="/reports", tags=["Admin Reports"])


@router.get("", response_model=AdminReportOut)
def get_admin_reports(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # 1. Total sales volume excluding cancelled orders
    total_sales_val = db.query(func.coalesce(func.sum(Order.total), 0.0)).filter(
        Order.status != "cancelled"
    ).scalar()

    # 2. Orders breakdown by status
    status_counts = {"pending": 0, "confirmed": 0, "shipped": 0, "delivered": 0, "cancelled": 0}
    orders_group = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    for status_str, count in orders_group:
        if status_str in status_counts:
            status_counts[status_str] = count
        else:
            status_counts[status_str] = count

    # 3. Users count breakdown by role
    role_counts = {"buyer": 0, "seller": 0, "admin": 0}
    users_group = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    for role_str, count in users_group:
        role_counts[role_str] = count

    # 4. Top selling products (from non-cancelled orders)
    top_items_query = db.query(
        OrderItem.product_id,
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label("total_qty"),
        func.sum(OrderItem.unit_price * OrderItem.quantity).label("total_revenue")
    ).join(Order, OrderItem.order_id == Order.id).filter(
        Order.status != "cancelled"
    ).group_by(
        OrderItem.product_id, OrderItem.product_name
    ).order_by(
        desc("total_qty")
    ).limit(5).all()

    top_products = [
        TopProductReport(
            product_id=row.product_id,
            product_name=row.product_name,
            total_quantity_sold=int(row.total_qty),
            total_revenue=round(float(row.total_revenue), 2)
        )
        for row in top_items_query
    ]

    # 5. Most common diagnoses
    common_diag_query = db.query(
        Diagnosis.symptom_id,
        Symptom.plant_part,
        Symptom.observation,
        Symptom.diagnosis,
        func.count(Diagnosis.id).label("diag_count")
    ).join(Symptom, Diagnosis.symptom_id == Symptom.id).group_by(
        Diagnosis.symptom_id, Symptom.plant_part, Symptom.observation, Symptom.diagnosis
    ).order_by(
        desc("diag_count")
    ).limit(5).all()

    common_diagnoses = [
        CommonDiagnosisReport(
            symptom_id=row.symptom_id,
            plant_part=row.plant_part,
            observation=row.observation,
            diagnosis=row.diagnosis,
            count=int(row.diag_count)
        )
        for row in common_diag_query
    ]

    # 6. Low stock count and products list (stock <= 5)
    low_stock_query = db.query(Product).filter(
        Product.is_active == True,
        Product.stock <= 5
    ).order_by(Product.stock.asc()).all()

    low_stock_count = len(low_stock_query)
    low_stock_products = [_to_product_out(p) for p in low_stock_query]

    return AdminReportOut(
        total_sales=round(float(total_sales_val), 2),
        orders_by_status=status_counts,
        users_by_role=role_counts,
        top_products=top_products,
        common_diagnoses=common_diagnoses,
        low_stock_count=low_stock_count,
        low_stock_products=low_stock_products,
    )
