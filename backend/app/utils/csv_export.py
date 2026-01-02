import io
import csv
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Optional

from app.api.deps import DBSession, CurrentUser
from app.models.product import Product
from app.models.order import SalesOrder, OrderStatus
from app.models.payment import Payment

router = APIRouter(prefix="/export", tags=["Export"])


def generate_csv(data: list[dict], fieldnames: list[str]) -> io.StringIO:
    """Generate CSV from list of dicts."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)
    return output


@router.get("/products")
async def export_products(db: DBSession, current_user: CurrentUser):
    """
    Export all products to CSV.
    """
    products = db.query(Product).all()
    
    data = [
        {
            "sku": p.sku,
            "name": p.name,
            "category": p.category or "",
            "unit": p.unit,
            "cost_price": str(p.cost_price),
            "sell_price": str(p.sell_price),
            "current_stock": p.current_stock,
            "min_stock": p.min_stock,
            "is_active": "Yes" if p.is_active else "No",
            "created_at": p.created_at.isoformat()
        }
        for p in products
    ]
    
    fieldnames = ["sku", "name", "category", "unit", "cost_price", "sell_price", 
                  "current_stock", "min_stock", "is_active", "created_at"]
    
    output = generate_csv(data, fieldnames)
    
    filename = f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/orders")
async def export_orders(
    db: DBSession,
    current_user: CurrentUser,
    status: Optional[OrderStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """
    Export orders to CSV.
    """
    query = db.query(SalesOrder)
    
    if status:
        query = query.filter(SalesOrder.status == status)
    if date_from:
        query = query.filter(SalesOrder.order_date >= date_from)
    if date_to:
        query = query.filter(SalesOrder.order_date <= date_to)
    
    orders = query.order_by(SalesOrder.order_date.desc()).all()
    
    data = [
        {
            "order_number": o.order_number,
            "customer": o.customer.name if o.customer else "",
            "status": o.status.value,
            "subtotal": str(o.subtotal),
            "discount": str(o.discount),
            "total": str(o.total),
            "paid_amount": str(o.paid_amount),
            "remaining": str(o.remaining_amount),
            "order_date": o.order_date.isoformat(),
            "created_by": o.creator.full_name if o.creator else ""
        }
        for o in orders
    ]
    
    fieldnames = ["order_number", "customer", "status", "subtotal", "discount", 
                  "total", "paid_amount", "remaining", "order_date", "created_by"]
    
    output = generate_csv(data, fieldnames)
    
    filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/payments")
async def export_payments(
    db: DBSession,
    current_user: CurrentUser,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """
    Export payments to CSV.
    """
    query = db.query(Payment)
    
    if date_from:
        query = query.filter(Payment.payment_date >= date_from)
    if date_to:
        query = query.filter(Payment.payment_date <= date_to)
    
    payments = query.order_by(Payment.payment_date.desc()).all()
    
    data = [
        {
            "payment_number": p.payment_number,
            "type": p.type.value,
            "method": p.method.value,
            "amount": str(p.amount),
            "customer": p.customer.name if p.customer else "",
            "supplier": p.supplier.name if p.supplier else "",
            "order": p.order.order_number if p.order else "",
            "payment_date": p.payment_date.isoformat(),
            "notes": p.notes or "",
            "created_by": p.creator.full_name if p.creator else ""
        }
        for p in payments
    ]
    
    fieldnames = ["payment_number", "type", "method", "amount", "customer", 
                  "supplier", "order", "payment_date", "notes", "created_by"]
    
    output = generate_csv(data, fieldnames)
    
    filename = f"payments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
