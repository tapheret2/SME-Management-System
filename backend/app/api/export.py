import logging
import traceback
import csv
from io import StringIO
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Response, Query, HTTPException

from sqlalchemy.orm import Session
from app.api.deps import get_current_user

logger = logging.getLogger("sme")

from app.database import get_db
from app.models.product import Product
from app.models.order import SalesOrder, OrderStatus
from app.models.payment import Payment
from app.api.deps import get_current_user


router = APIRouter(prefix="/export", tags=["export"])


@router.get("/products")
def export_products(
    db: Session = Depends(get_db)
):
    """Export products as CSV."""
    logger.info("Export products endpoint hit")
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        
        output = StringIO()
        # output.write('\ufeff') # Removed BOM to avoid proxy issues
        writer = csv.writer(output)
        writer.writerow(["SKU", "Tên sản phẩm", "Danh mục", "Đơn vị", "Giá vốn", "Giá bán", "Tồn kho", "Tồn tối thiểu"])
        
        for p in products:
            try:
                writer.writerow([p.sku, p.name, p.category or "", p.unit, p.cost_price, p.sell_price, p.current_stock, p.min_stock])
            except Exception as row_error:
                logger.error(f"Error writing product row {p.id}: {row_error}")
                continue
        
        content = output.getvalue()
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=products_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    except Exception as e:
        logger.error(f"Export products error: {e}", exc_info=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
def export_orders(
    order_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export orders as CSV."""
    try:
        query = db.query(SalesOrder).filter(SalesOrder.deleted_at == None)
        if order_status:
            query = query.filter(SalesOrder.status == OrderStatus(order_status))
        
        orders = query.order_by(SalesOrder.order_date.desc()).all()
        
        output = StringIO()
        # output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(["Mã đơn", "Ngày đặt", "Trạng thái", "Tổng tiền", "Đã thanh toán", "Còn lại", "Ghi chú"])
        
        for o in orders:
            try:
                # Handle enum safely
                status_val = o.status.value if hasattr(o.status, 'value') else str(o.status)
                
                writer.writerow([
                    o.order_number, 
                    o.order_date.strftime("%Y-%m-%d %H:%M"), 
                    status_val,
                    o.total, 
                    o.paid_amount, 
                    o.remaining_amount,
                    o.notes or ""
                ])
            except Exception as row_error:
                logger.error(f"Error writing order row {o.id}: {row_error}")
                continue
        
        content = output.getvalue()
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=orders_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    except Exception as e:
        logger.error(f"Export orders error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments")
def export_payments(
    payment_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export payments as CSV."""
    try:
        query = db.query(Payment)
        if payment_type:
            query = query.filter(Payment.type == payment_type)
        
        payments = query.order_by(Payment.payment_date.desc()).all()
        
        output = StringIO()
        # output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(["Mã phiếu", "Ngày", "Loại", "Phương thức", "Số tiền", "Ghi chú"])
        
        for p in payments:
            try:
                # Handle enum values safely
                p_type = p.type.value if hasattr(p.type, 'value') else str(p.type)
                p_method = p.method.value if hasattr(p.method, 'value') else str(p.method)
                
                writer.writerow([
                    p.payment_number, 
                    p.payment_date.strftime("%Y-%m-%d %H:%M"), 
                    p_type,
                    p_method,
                    p.amount,
                    p.notes or ""
                ])
            except Exception as row_error:
                logger.error(f"Error writing payment row {p.id}: {row_error}")
                continue
        
        content = output.getvalue()
        return Response(
            content=content,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=payments_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    except Exception as e:
        logger.error(f"Export payments error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
