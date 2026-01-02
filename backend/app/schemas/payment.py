"""Payment schemas with UUID support."""
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
    customer_name: Optional[str] = None
    supplier_id: Optional[UUID] = None
    supplier_name: Optional[str] = None
    order_id: Optional[UUID] = None
    created_by: UUID
    amount: Decimal
    notes: Optional[str] = None
    payment_date: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int


# AR/AP Summaries
class DebtSummaryItem(BaseModel):
    entity_id: UUID
    entity_code: str
    entity_name: str
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal


class ReceivablesResponse(BaseModel):
    items: list[DebtSummaryItem]
    total_receivables: Decimal


class PayablesResponse(BaseModel):
    items: list[DebtSummaryItem]
    total_payables: Decimal
