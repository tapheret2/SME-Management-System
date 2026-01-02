"""Orders API endpoints with proper transaction handling."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import SalesOrder, SalesOrderItem, OrderStatus, STATUS_TRANSITIONS
from app.models.stock import StockMovement, MovementType
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate, 
    OrderResponse, OrderListResponse
)
from app.api.deps import get_current_user
from app.services.audit import log_action

logger = logging.getLogger("sme")
router = APIRouter(prefix="/orders", tags=["orders"])


def generate_order_number() -> str:
    """Generate unique order number with microseconds to prevent collision."""
    now = datetime.now()
    return f"SO-{now.strftime('%Y%m%d%H%M%S%f')}"


@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order_status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """List orders with filtering."""
    query = db.query(SalesOrder).filter(SalesOrder.deleted_at == None)
    
    if order_status:
        query = query.filter(SalesOrder.status == OrderStatus(order_status))
    if customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)
    
    query = query.order_by(SalesOrder.order_date.desc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return OrderListResponse(items=items, total=total)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order with proper transaction handling."""
    try:
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found")
        
        # Create order
        order = SalesOrder(
            order_number=generate_order_number(),
            customer_id=data.customer_id,
            created_by=current_user.id,
            discount=data.discount,
            notes=data.notes
        )
        db.add(order)
        db.flush()
        
        # Add line items
        for item_data in data.line_items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {item_data.product_id} not found")
            if not product.is_active:
                raise HTTPException(status_code=400, detail=f"Product {product.sku} is inactive")
            
            line_item = SalesOrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount=item_data.discount,
                line_total=(item_data.unit_price * item_data.quantity) - item_data.discount
            )
            db.add(line_item)
        
        db.flush()
        order.calculate_totals()
        
        # Audit log
        log_action(db, "create", "order", order.id, current_user.id,
                   after_data={"order_number": order.order_number, "total": str(order.total)})
        
        db.commit()
        db.refresh(order)
        return order
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Order creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Order creation failed")


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get a single order with line items."""
    order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id,
        SalesOrder.deleted_at == None
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update order status with workflow validation and transaction handling."""
    try:
        order = db.query(SalesOrder).filter(
            SalesOrder.id == order_id,
            SalesOrder.deleted_at == None
        ).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        new_status = OrderStatus(data.status)
        old_status = order.status.value
        
        if not order.can_transition_to(new_status):
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot transition from {order.status.value} to {new_status.value}"
            )
        
        # Handle stock changes
        if new_status == OrderStatus.CONFIRMED and order.status == OrderStatus.DRAFT:
            # Deduct stock on confirm
            for item in order.line_items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product.current_stock < item.quantity:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Insufficient stock for {product.sku}"
                    )
                
                stock_before = product.current_stock
                product.current_stock -= item.quantity
                
                movement = StockMovement(
                    product_id=product.id,
                    created_by=current_user.id,
                    type=MovementType.OUT,
                    quantity=item.quantity,
                    stock_before=stock_before,
                    stock_after=product.current_stock,
                    reason=f"Order {order.order_number}"
                )
                db.add(movement)
        
        elif new_status == OrderStatus.CANCELLED and order.status == OrderStatus.CONFIRMED:
            # Restore stock on cancel
            for item in order.line_items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                stock_before = product.current_stock
                product.current_stock += item.quantity
                
                movement = StockMovement(
                    product_id=product.id,
                    created_by=current_user.id,
                    type=MovementType.IN,
                    quantity=item.quantity,
                    stock_before=stock_before,
                    stock_after=product.current_stock,
                    reason=f"Cancelled order {order.order_number}"
                )
                db.add(movement)
        
        order.status = new_status
        
        # Audit log for status change
        log_action(db, "status_change", "order", order.id, current_user.id,
                   before_data={"status": old_status},
                   after_data={"status": new_status.value})
        
        db.commit()
        db.refresh(order)
        return order
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Order status update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Status update failed")


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Soft delete an order."""
    order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id,
        SalesOrder.deleted_at == None
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.deleted_at = datetime.utcnow()
    db.commit()
    return None
