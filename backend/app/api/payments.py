"""Payments API endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.order import SalesOrder
from app.models.payment import Payment, PaymentType, PaymentMethod
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse, ARAPSummary
)
from app.api.deps import get_current_user


router = APIRouter(prefix="/payments", tags=["payments"])


def generate_payment_number() -> str:
    """Generate unique payment number."""
    now = datetime.now()
    return f"PAY-{now.strftime('%Y%m%d%H%M%S')}"


@router.get("", response_model=PaymentListResponse)
def list_payments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    payment_type: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    supplier_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """List payments with filtering."""
    query = db.query(Payment)
    
    if payment_type:
        query = query.filter(Payment.type == PaymentType(payment_type))
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    if supplier_id:
        query = query.filter(Payment.supplier_id == supplier_id)
    
    query = query.order_by(Payment.payment_date.desc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return PaymentListResponse(items=items, total=total)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a payment and update debts."""
    # Validate based on type
    if data.type == "incoming" and not data.customer_id:
        raise HTTPException(status_code=400, detail="Customer ID required for incoming payment")
    if data.type == "outgoing" and not data.supplier_id:
        raise HTTPException(status_code=400, detail="Supplier ID required for outgoing payment")
    
    payment = Payment(
        payment_number=generate_payment_number(),
        type=PaymentType(data.type),
        method=PaymentMethod(data.method),
        customer_id=data.customer_id,
        supplier_id=data.supplier_id,
        order_id=data.order_id,
        created_by=current_user.id,
        amount=data.amount,
        notes=data.notes
    )
    db.add(payment)
    
    # Update customer debt or order paid amount
    if data.type == "incoming" and data.customer_id:
        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if customer:
            customer.total_debt -= data.amount
    
    # Update order paid_amount if linked
    if data.order_id:
        order = db.query(SalesOrder).filter(SalesOrder.id == data.order_id).first()
        if order:
            order.paid_amount += data.amount
    
    # Update supplier payable
    if data.type == "outgoing" and data.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == data.supplier_id).first()
        if supplier:
            supplier.total_payable -= data.amount
    
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/ar-ap", response_model=ARAPSummary)
def get_arap_summary(
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get accounts receivable/payable summary."""
    # Total receivables (customer debts)
    receivables = db.query(func.coalesce(func.sum(Customer.total_debt), 0)).scalar()
    customer_count = db.query(Customer).filter(Customer.total_debt > 0).count()
    
    # Total payables (supplier debts)
    payables = db.query(func.coalesce(func.sum(Supplier.total_payable), 0)).scalar()
    supplier_count = db.query(Supplier).filter(Supplier.total_payable > 0).count()
    
    return ARAPSummary(
        total_receivables=Decimal(str(receivables)),
        customer_count=customer_count,
        total_payables=Decimal(str(payables)),
        supplier_count=supplier_count
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get a single payment."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
