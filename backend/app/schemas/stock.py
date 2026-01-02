from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.stock import StockMovementType


class StockMovementBase(BaseModel):
    product_id: int
    type: StockMovementType
    quantity: int = Field(..., gt=0)
    reason: Optional[str] = None


class StockInCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    supplier_id: Optional[int] = None
    reason: Optional[str] = None


class StockOutCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    order_id: Optional[int] = None
    reason: Optional[str] = None


class StockAdjustCreate(BaseModel):
    product_id: int
    quantity: int  # Can be positive or negative
    reason: str = Field(..., min_length=1)


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    order_id: Optional[int] = None
    order_number: Optional[str] = None
    type: StockMovementType
    quantity: int
    stock_before: int
    stock_after: int
    reason: Optional[str] = None
    created_by: int
    creator_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StockMovementListResponse(BaseModel):
    items: list[StockMovementResponse]
    total: int
    page: int
    size: int
