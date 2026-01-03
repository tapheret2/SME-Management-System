"""Payment schemas."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    type: str = Field(..., pattern="^(incoming|outgoing)$")
    method: str = Field(default="cash", pattern="^(cash|bank|other)$")
    customer_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    amount: Decimal = Field(..., gt=0)
    is_settlement: bool = Field(default=False)
    notes: Optional[str] = None


class PaymentUpdate(BaseModel):
    method: Optional[str] = Field(None, pattern="^(cash|bank|other)$")
    amount: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    payment_number: str
    type: str
    method: str
    customer_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    created_by: UUID
    amount: Decimal
    is_settlement: bool
    notes: Optional[str] = None
    payment_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int


class ARAPSummary(BaseModel):
    total_receivables: Decimal
    customer_count: int
    total_payables: Decimal
    supplier_count: int
