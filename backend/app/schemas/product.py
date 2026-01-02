from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    unit: str = Field(default="cái", max_length=50)
    cost_price: Decimal = Field(default=0, ge=0)
    sell_price: Decimal = Field(default=0, ge=0)
    min_stock: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    current_stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    sell_price: Optional[Decimal] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    current_stock: int
    is_active: bool
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    size: int


class LowStockProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    current_stock: int
    min_stock: int

    class Config:
        from_attributes = True
