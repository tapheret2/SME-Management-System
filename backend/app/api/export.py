"""CSV Export endpoints."""
import csv
from io import StringIO
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.order import SalesOrder, OrderStatus
from app.models.payment import Payment
from app.api.deps import get_current_user


router = APIRouter(prefix="/export", tags=["export"])


@router.get("/products.csv")
def export_products(
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Export products as CSV."""
    products = db.query(Product).filter(Product.is_active == True).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["SKU", "Tên sản phẩm", "Danh mục", "Đơn vị", "Giá vốn", "Giá bán", "Tồn kho", "Tồn tối thiểu"])
    
    for p in products:
        writer.writerow([p.sku, p.name, p.category or "", p.unit, p.cost_price, p.sell_price, p.current_stock, p.min_stock])
    
    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=products_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@router.get("/orders.csv")
def export_orders(
    order_status: Optional[str] = None,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Export orders as CSV."""
    query = db.query(SalesOrder).filter(SalesOrder.deleted_at == None)
    if order_status:
        query = query.filter(SalesOrder.status == OrderStatus(order_status))
    
    orders = query.order_by(SalesOrder.order_date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Mã đơn", "Ngày đặt", "Trạng thái", "Tổng tiền", "Đã thanh toán", "Còn lại", "Ghi chú"])
    
    for o in orders:
        writer.writerow([
            o.order_number, 
            o.order_date.strftime("%Y-%m-%d %H:%M"), 
            o.status.value,
            o.total, 
            o.paid_amount, 
            o.remaining_amount,
            o.notes or ""
        ])
    
    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=orders_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@router.get("/payments.csv")
def export_payments(
    payment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Export payments as CSV."""
    query = db.query(Payment)
    if payment_type:
        query = query.filter(Payment.type == payment_type)
    
    payments = query.order_by(Payment.payment_date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Mã phiếu", "Ngày", "Loại", "Phương thức", "Số tiền", "Ghi chú"])
    
    for p in payments:
        writer.writerow([
            p.payment_number, 
            p.payment_date.strftime("%Y-%m-%d %H:%M"), 
            p.type.value,
            p.method.value,
            p.amount,
            p.notes or ""
        ])
    
    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=payments_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
