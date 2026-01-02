from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.api.deps import DBSession, CurrentUser
from app.models.order import SalesOrder, OrderLine, OrderStatus
from app.models.product import Product
from app.models.customer import Customer
from app.models.stock import StockMovement, StockMovementType
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate, OrderResponse,
    OrderListResponse, OrderLineResponse
)
from app.services.audit import log_create, log_update

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_order_number(db: DBSession) -> str:
    """Generate a unique order number."""
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(SalesOrder).filter(
        SalesOrder.order_number.like(f"SO{today}%")
    ).count()
    return f"SO{today}{count + 1:04d}"


def calculate_order_totals(order: SalesOrder):
    """Recalculate order totals from line items."""
    subtotal = sum(line.line_total for line in order.line_items)
    order.subtotal = subtotal
    order.total = subtotal - order.discount


def build_order_response(order: SalesOrder, db: DBSession) -> OrderResponse:
    """Build OrderResponse from SalesOrder."""
    line_items = []
    for line in order.line_items:
        product = db.query(Product).filter(Product.id == line.product_id).first()
        line_items.append(OrderLineResponse(
            id=line.id,
            product_id=line.product_id,
            quantity=line.quantity,
            unit_price=line.unit_price,
            discount=line.discount,
            line_total=line.line_total,
            product_name=product.name if product else None,
            product_sku=product.sku if product else None
        ))
    
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_id=order.customer_id,
        customer_name=customer.name if customer else None,
        created_by=order.created_by,
        creator_name=order.creator.full_name if order.creator else None,
        status=order.status,
        subtotal=order.subtotal,
        discount=order.discount,
        total=order.total,
        paid_amount=order.paid_amount,
        remaining_amount=order.remaining_amount,
        notes=order.notes,
        order_date=order.order_date,
        created_at=order.created_at,
        updated_at=order.updated_at,
        line_items=line_items
    )


@router.get("", response_model=OrderListResponse)
async def list_orders(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """
    List all orders with pagination and filters.
    """
    query = db.query(SalesOrder)
    
    if status:
        query = query.filter(SalesOrder.status == status)
    
    if customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)
    
    if date_from:
        query = query.filter(SalesOrder.order_date >= date_from)
    
    if date_to:
        query = query.filter(SalesOrder.order_date <= date_to)
    
    total = query.count()
    orders = query.order_by(SalesOrder.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    items = [build_order_response(order, db) for order in orders]
    
    return OrderListResponse(items=items, total=total, page=page, size=size)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(request: OrderCreate, db: DBSession, current_user: CurrentUser):
    """
    Create a new order (draft status).
    """
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create order
    order = SalesOrder(
        order_number=generate_order_number(db),
        customer_id=request.customer_id,
        created_by=current_user.id,
        status=OrderStatus.DRAFT,
        discount=request.discount,
        notes=request.notes,
        order_date=request.order_date or datetime.now()
    )
    db.add(order)
    db.flush()
    
    # Add line items
    for line_data in request.line_items:
        product = db.query(Product).filter(Product.id == line_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {line_data.product_id} not found")
        
        line_total = (line_data.quantity * line_data.unit_price) - line_data.discount
        line = OrderLine(
            order_id=order.id,
            product_id=line_data.product_id,
            quantity=line_data.quantity,
            unit_price=line_data.unit_price,
            discount=line_data.discount,
            line_total=line_total
        )
        db.add(line)
    
    db.flush()
    calculate_order_totals(order)
    db.commit()
    db.refresh(order)
    
    # Audit log
    log_create(db, current_user.id, "order", order.id, {
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "total": str(order.total)
    })
    
    return build_order_response(order, db)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: DBSession, current_user: CurrentUser):
    """
    Get a specific order by ID.
    """
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return build_order_response(order, db)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, request: OrderUpdate, db: DBSession, current_user: CurrentUser):
    """
    Update an order (only in draft status).
    """
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != OrderStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only draft orders can be updated"
        )
    
    old_values = {
        "customer_id": order.customer_id,
        "discount": str(order.discount),
        "notes": order.notes
    }
    
    if request.customer_id is not None:
        customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        order.customer_id = request.customer_id
    
    if request.discount is not None:
        order.discount = request.discount
    
    if request.notes is not None:
        order.notes = request.notes
    
    calculate_order_totals(order)
    db.commit()
    db.refresh(order)
    
    # Audit log
    log_update(db, current_user.id, "order", order.id, old_values, request.model_dump(exclude_unset=True))
    
    return build_order_response(order, db)


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: int, request: OrderStatusUpdate, db: DBSession, current_user: CurrentUser):
    """
    Update order status with validation.
    Status flow: draft -> confirmed -> shipped -> completed
                 draft -> cancelled
    """
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = order.status
    new_status = request.status
    
    # Validate status transitions
    valid_transitions = {
        OrderStatus.DRAFT: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPED: [OrderStatus.COMPLETED],
        OrderStatus.COMPLETED: [],
        OrderStatus.CANCELLED: []
    }
    
    if new_status not in valid_transitions.get(old_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {old_status.value} to {new_status.value}"
        )
    
    # Handle stock deduction on confirm
    if new_status == OrderStatus.CONFIRMED:
        for line in order.line_items:
            product = db.query(Product).filter(Product.id == line.product_id).first()
            if not product:
                continue
            
            if product.current_stock < line.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name}. Available: {product.current_stock}"
                )
            
            # Create stock movement
            stock_before = product.current_stock
            product.current_stock -= line.quantity
            
            movement = StockMovement(
                product_id=product.id,
                order_id=order.id,
                type=StockMovementType.OUT,
                quantity=line.quantity,
                stock_before=stock_before,
                stock_after=product.current_stock,
                reason=f"Order {order.order_number}",
                created_by=current_user.id
            )
            db.add(movement)
        
        # Update customer debt
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if customer:
            customer.total_debt += order.total
    
    # Handle stock restoration on cancel (if was confirmed)
    if new_status == OrderStatus.CANCELLED and old_status in [OrderStatus.CONFIRMED, OrderStatus.SHIPPED]:
        for line in order.line_items:
            product = db.query(Product).filter(Product.id == line.product_id).first()
            if not product:
                continue
            
            stock_before = product.current_stock
            product.current_stock += line.quantity
            
            movement = StockMovement(
                product_id=product.id,
                order_id=order.id,
                type=StockMovementType.IN,
                quantity=line.quantity,
                stock_before=stock_before,
                stock_after=product.current_stock,
                reason=f"Order {order.order_number} cancelled",
                created_by=current_user.id
            )
            db.add(movement)
        
        # Reduce customer debt
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if customer:
            customer.total_debt -= (order.total - order.paid_amount)
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    # Audit log
    log_update(db, current_user.id, "order", order.id, 
               {"status": old_status.value}, 
               {"status": new_status.value})
    
    return build_order_response(order, db)


@router.delete("/{order_id}")
async def cancel_order(order_id: int, db: DBSession, current_user: CurrentUser):
    """
    Cancel an order (sets status to cancelled).
    """
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order in {order.status.value} status"
        )
    
    # Use status update logic
    return await update_order_status(
        order_id, 
        OrderStatusUpdate(status=OrderStatus.CANCELLED), 
        db, 
        current_user
    )
