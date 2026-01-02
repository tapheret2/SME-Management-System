from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.payment import PaymentType, PaymentMethod


class PaymentBase(BaseModel):
    type: PaymentType
    method: PaymentMethod = PaymentMethod.CASH
    amount: Decimal = Field(..., gt=0)
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    order_id: Optional[int] = None
    notes: Optional[str] = None
    payment_date: Optional[datetime] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    method: Optional[PaymentMethod] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = None
    payment_date: Optional[datetime] = None


class PaymentResponse(PaymentBase):
    id: int
    payment_number: str
    customer_name: Optional[str] = None
    supplier_name: Optional[str] = None
    order_number: Optional[str] = None
    created_by: int
    creator_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    page: int
    size: int


class DebtSummary(BaseModel):
    entity_id: int
    entity_code: str
    entity_name: str
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal


class ReceivablesResponse(BaseModel):
    items: list[DebtSummary]
    total_receivables: Decimal


class PayablesResponse(BaseModel):
    items: list[DebtSummary]
    total_payables: Decimal
