from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List

from app.api.deps import DBSession, CurrentUser
from app.models.product import Product
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ProductListResponse, LowStockProductResponse
)
from app.services.audit import log_create, log_update, log_delete

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = True
):
    """
    List all products with pagination and filters.
    """
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_pattern)) |
            (Product.sku.ilike(search_pattern))
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    total = query.count()
    items = query.order_by(Product.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    # Add is_low_stock computed property
    result_items = []
    for item in items:
        item_dict = ProductResponse.model_validate(item).model_dump()
        item_dict["is_low_stock"] = item.is_low_stock
        result_items.append(ProductResponse(**item_dict))
    
    return ProductListResponse(items=result_items, total=total, page=page, size=size)


@router.get("/low-stock", response_model=List[LowStockProductResponse])
async def get_low_stock_products(db: DBSession, current_user: CurrentUser):
    """
    Get all products with low stock.
    """
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.current_stock <= Product.min_stock
    ).all()
    return products


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(request: ProductCreate, db: DBSession, current_user: CurrentUser):
    """
    Create a new product.
    """
    # Check if SKU already exists
    existing = db.query(Product).filter(Product.sku == request.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product SKU already exists"
        )
    
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Audit log
    log_create(db, current_user.id, "product", product.id, request.model_dump())
    
    # Return with computed property
    result = ProductResponse.model_validate(product).model_dump()
    result["is_low_stock"] = product.is_low_stock
    return ProductResponse(**result)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: DBSession, current_user: CurrentUser):
    """
    Get a specific product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    result = ProductResponse.model_validate(product).model_dump()
    result["is_low_stock"] = product.is_low_stock
    return ProductResponse(**result)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, request: ProductUpdate, db: DBSession, current_user: CurrentUser):
    """
    Update a product.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    old_values = {
        "sku": product.sku,
        "name": product.name,
        "category": product.category,
        "unit": product.unit,
        "cost_price": str(product.cost_price),
        "sell_price": str(product.sell_price),
        "min_stock": product.min_stock,
        "is_active": product.is_active
    }
    
    # Check if new SKU is taken
    if request.sku is not None and request.sku != product.sku:
        existing = db.query(Product).filter(Product.sku == request.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product SKU already exists"
            )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    # Audit log
    log_update(db, current_user.id, "product", product.id, old_values, {k: str(v) for k, v in update_data.items()})
    
    result = ProductResponse.model_validate(product).model_dump()
    result["is_low_stock"] = product.is_low_stock
    return ProductResponse(**result)


@router.delete("/{product_id}")
async def deactivate_product(product_id: int, db: DBSession, current_user: CurrentUser):
    """
    Deactivate a product (soft delete).
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    old_values = {"is_active": product.is_active}
    product.is_active = False
    db.commit()
    
    # Audit log
    log_update(db, current_user.id, "product", product.id, old_values, {"is_active": False})
    
    return {"message": "Product deactivated successfully"}
