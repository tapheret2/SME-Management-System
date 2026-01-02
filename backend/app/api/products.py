"""Products API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.product import Product
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ProductListResponse, LowStockProduct
)
from app.api.deps import get_current_user
from app.helpers import sanitize_like


router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """List products with pagination and filtering."""
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if search:
        safe_search = sanitize_like(search)
        query = query.filter(
            or_(Product.sku.ilike(f"%{safe_search}%"), Product.name.ilike(f"%{safe_search}%"))
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return ProductListResponse(items=items, total=total)


@router.get("/low-stock", response_model=list[LowStockProduct])
def get_low_stock_products(
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get products with stock at or below minimum level."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.current_stock <= Product.min_stock
    ).all()
    return products


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Create a new product."""
    existing = db.query(Product).filter(Product.sku == data.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get a single product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Update a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Check SKU uniqueness if updating
    if "sku" in update_data and update_data["sku"] != product.sku:
        existing = db.query(Product).filter(Product.sku == update_data["sku"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Soft delete a product (set is_active=False)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    db.commit()
    return None
