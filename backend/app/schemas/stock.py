"""Stock movement schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class StockInCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    reason: Optional[str] = None


class StockOutCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    reason: Optional[str] = None


class StockAdjustCreate(BaseModel):
    product_id: UUID
    quantity: int  # Can be positive or negative
    reason: str = Field(..., min_length=1)


class StockMovementResponse(BaseModel):
    id: UUID
    product_id: UUID
    created_by: UUID
    type: str
    quantity: int
    stock_before: int
    stock_after: int
    reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockMovementListResponse(BaseModel):
    items: list[StockMovementResponse]
    total: int
