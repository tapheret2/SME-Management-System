"""Order schemas."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class OrderLineCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount: Decimal = Field(default=Decimal("0"), ge=0)


class OrderLineResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    quantity: int
    unit_price: Decimal
    discount: Decimal
    line_total: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_id: UUID
    line_items: list[OrderLineCreate]
    discount: Decimal = Field(default=Decimal("0"), ge=0)
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    discount: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(draft|confirmed|shipped|completed|cancelled)$")


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    customer_id: UUID
    customer_name: Optional[str] = None
    created_by: UUID
    creator_name: Optional[str] = None
    status: str
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    notes: Optional[str] = None
    order_date: datetime
    line_items: list[OrderLineResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderListItem(BaseModel):
    id: UUID
    order_number: str
    customer_id: UUID
    status: str
    total: Decimal
    paid_amount: Decimal
    order_date: datetime
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: list[OrderListItem]
    total: int
