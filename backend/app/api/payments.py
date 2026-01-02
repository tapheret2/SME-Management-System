from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.api.deps import DBSession, CurrentUser
from app.models.payment import Payment, PaymentType, PaymentMethod
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.order import SalesOrder
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse,
    ReceivablesResponse, PayablesResponse, DebtSummary
)
from app.services.audit import log_create, log_update, log_delete

router = APIRouter(prefix="/payments", tags=["Payments"])


def generate_payment_number(db: DBSession, payment_type: PaymentType) -> str:
    """Generate a unique payment number."""
    prefix = "PI" if payment_type == PaymentType.INCOMING else "PO"
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Payment).filter(
        Payment.payment_number.like(f"{prefix}{today}%")
    ).count()
    return f"{prefix}{today}{count + 1:04d}"


def build_payment_response(payment: Payment, db: DBSession) -> PaymentResponse:
    """Build PaymentResponse from Payment."""
    customer_name = None
    supplier_name = None
    order_number = None
    
    if payment.customer_id:
        customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
        customer_name = customer.name if customer else None
    
    if payment.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == payment.supplier_id).first()
        supplier_name = supplier.name if supplier else None
    
    if payment.order_id:
        order = db.query(SalesOrder).filter(SalesOrder.id == payment.order_id).first()
        order_number = order.order_number if order else None
    
    return PaymentResponse(
        id=payment.id,
        payment_number=payment.payment_number,
        type=payment.type,
        method=payment.method,
        amount=payment.amount,
        customer_id=payment.customer_id,
        customer_name=customer_name,
        supplier_id=payment.supplier_id,
        supplier_name=supplier_name,
        order_id=payment.order_id,
        order_number=order_number,
        notes=payment.notes,
        payment_date=payment.payment_date,
        created_by=payment.created_by,
        creator_name=payment.creator.full_name if payment.creator else None,
        created_at=payment.created_at
    )


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: Optional[PaymentType] = None,
    customer_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """
    List all payments with pagination and filters.
    """
    query = db.query(Payment)
    
    if type:
        query = query.filter(Payment.type == type)
    
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    
    if supplier_id:
        query = query.filter(Payment.supplier_id == supplier_id)
    
    if date_from:
        query = query.filter(Payment.payment_date >= date_from)
    
    if date_to:
        query = query.filter(Payment.payment_date <= date_to)
    
    total = query.count()
    payments = query.order_by(Payment.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    items = [build_payment_response(p, db) for p in payments]
    
    return PaymentListResponse(items=items, total=total, page=page, size=size)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(request: PaymentCreate, db: DBSession, current_user: CurrentUser):
    """
    Create a new payment.
    """
    # Validate based on type
    if request.type == PaymentType.INCOMING:
        if not request.customer_id:
            raise HTTPException(status_code=400, detail="Customer ID required for incoming payment")
        customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    else:  # OUTGOING
        if not request.supplier_id:
            raise HTTPException(status_code=400, detail="Supplier ID required for outgoing payment")
        supplier = db.query(Supplier).filter(Supplier.id == request.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Validate order if provided
    if request.order_id:
        order = db.query(SalesOrder).filter(SalesOrder.id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
    
    payment = Payment(
        payment_number=generate_payment_number(db, request.type),
        type=request.type,
        method=request.method,
        amount=request.amount,
        customer_id=request.customer_id,
        supplier_id=request.supplier_id,
        order_id=request.order_id,
        notes=request.notes,
        payment_date=request.payment_date or datetime.now(),
        created_by=current_user.id
    )
    db.add(payment)
    
    # Update debt balances
    if request.type == PaymentType.INCOMING and request.customer_id:
        customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
        if customer:
            customer.total_debt -= request.amount
    
    if request.type == PaymentType.OUTGOING and request.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == request.supplier_id).first()
        if supplier:
            supplier.total_payable -= request.amount
    
    # Update order paid amount
    if request.order_id:
        order = db.query(SalesOrder).filter(SalesOrder.id == request.order_id).first()
        if order:
            order.paid_amount += request.amount
    
    db.commit()
    db.refresh(payment)
    
    # Audit log
    log_create(db, current_user.id, "payment", payment.id, {
        "payment_number": payment.payment_number,
        "type": payment.type.value,
        "amount": str(payment.amount)
    })
    
    return build_payment_response(payment, db)


@router.get("/receivables", response_model=ReceivablesResponse)
async def get_receivables(db: DBSession, current_user: CurrentUser):
    """
    Get accounts receivable summary (money customers owe us).
    """
    customers = db.query(Customer).filter(Customer.total_debt > 0).all()
    
    items = []
    total = Decimal(0)
    
    for customer in customers:
        items.append(DebtSummary(
            entity_id=customer.id,
            entity_code=customer.code,
            entity_name=customer.name,
            total_amount=customer.total_debt,
            paid_amount=Decimal(0),  # Simplified for MVP
            remaining_amount=customer.total_debt
        ))
        total += customer.total_debt
    
    return ReceivablesResponse(items=items, total_receivables=total)


@router.get("/payables", response_model=PayablesResponse)
async def get_payables(db: DBSession, current_user: CurrentUser):
    """
    Get accounts payable summary (money we owe suppliers).
    """
    suppliers = db.query(Supplier).filter(Supplier.total_payable > 0).all()
    
    items = []
    total = Decimal(0)
    
    for supplier in suppliers:
        items.append(DebtSummary(
            entity_id=supplier.id,
            entity_code=supplier.code,
            entity_name=supplier.name,
            total_amount=supplier.total_payable,
            paid_amount=Decimal(0),  # Simplified for MVP
            remaining_amount=supplier.total_payable
        ))
        total += supplier.total_payable
    
    return PayablesResponse(items=items, total_payables=total)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: DBSession, current_user: CurrentUser):
    """
    Get a specific payment by ID.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return build_payment_response(payment, db)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(payment_id: int, request: PaymentUpdate, db: DBSession, current_user: CurrentUser):
    """
    Update a payment (limited fields).
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    old_values = {
        "method": payment.method.value,
        "notes": payment.notes,
        "payment_date": payment.payment_date.isoformat() if payment.payment_date else None
    }
    
    if request.method is not None:
        payment.method = request.method
    
    if request.notes is not None:
        payment.notes = request.notes
    
    if request.payment_date is not None:
        payment.payment_date = request.payment_date
    
    db.commit()
    db.refresh(payment)
    
    # Audit log
    log_update(db, current_user.id, "payment", payment.id, old_values, request.model_dump(exclude_unset=True))
    
    return build_payment_response(payment, db)


@router.delete("/{payment_id}")
async def delete_payment(payment_id: int, db: DBSession, current_user: CurrentUser):
    """
    Delete a payment (reverses debt adjustments).
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Reverse debt adjustments
    if payment.type == PaymentType.INCOMING and payment.customer_id:
        customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
        if customer:
            customer.total_debt += payment.amount
    
    if payment.type == PaymentType.OUTGOING and payment.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == payment.supplier_id).first()
        if supplier:
            supplier.total_payable += payment.amount
    
    # Reverse order paid amount
    if payment.order_id:
        order = db.query(SalesOrder).filter(SalesOrder.id == payment.order_id).first()
        if order:
            order.paid_amount -= payment.amount
    
    old_values = {
        "payment_number": payment.payment_number,
        "type": payment.type.value,
        "amount": str(payment.amount)
    }
    
    db.delete(payment)
    db.commit()
    
    # Audit log
    log_delete(db, current_user.id, "payment", payment_id, old_values)
    
    return {"message": "Payment deleted successfully"}
