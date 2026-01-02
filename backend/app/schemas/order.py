from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus


# Order Line schemas
class OrderLineBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount: Decimal = Field(default=0, ge=0)


class OrderLineCreate(OrderLineBase):
    pass


class OrderLineUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount: Optional[Decimal] = Field(None, ge=0)


class OrderLineResponse(OrderLineBase):
    id: int
    line_total: Decimal
    product_name: Optional[str] = None
    product_sku: Optional[str] = None

    class Config:
        from_attributes = True


# Order schemas
class OrderBase(BaseModel):
    customer_id: int
    notes: Optional[str] = None
    order_date: Optional[datetime] = None


class OrderCreate(OrderBase):
    line_items: list[OrderLineCreate] = Field(default_factory=list)
    discount: Decimal = Field(default=0, ge=0)


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    notes: Optional[str] = None
    discount: Optional[Decimal] = Field(None, ge=0)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer_name: Optional[str] = None
    created_by: int
    creator_name: Optional[str] = None
    status: OrderStatus
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    notes: Optional[str] = None
    order_date: datetime
    created_at: datetime
    updated_at: datetime
    line_items: list[OrderLineResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    size: int
