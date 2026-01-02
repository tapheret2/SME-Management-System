"""Product schemas with UUID support."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    unit: str = Field(default="cái", max_length=20)
    cost_price: Decimal = Field(default=Decimal("0"), ge=0)
    sell_price: Decimal = Field(default=Decimal("0"), ge=0)
    min_stock: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    current_stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=20)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    sell_price: Optional[Decimal] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: UUID
    sku: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    unit: str
    cost_price: Decimal
    sell_price: Decimal
    current_stock: int
    min_stock: int
    is_active: bool
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int


class LowStockProduct(BaseModel):
    id: UUID
    sku: str
    name: str
    current_stock: int
    min_stock: int
    
    model_config = {"from_attributes": True}
