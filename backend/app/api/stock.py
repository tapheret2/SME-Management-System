"""Stock movements API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.stock import StockMovement, MovementType
from app.models.user import User
from app.schemas.stock import (
    StockInCreate, StockOutCreate, StockAdjustCreate,
    StockMovementResponse, StockMovementListResponse
)
from app.api.deps import get_current_user


router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("", response_model=StockMovementListResponse)
def list_movements(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    product_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """List stock movements with pagination."""
    query = db.query(StockMovement).order_by(StockMovement.created_at.desc())
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return StockMovementListResponse(items=items, total=total)


@router.post("/in", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def stock_in(
    data: StockInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record stock in (receiving)."""
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stock_before = product.current_stock
    product.current_stock += data.quantity
    
    movement = StockMovement(
        product_id=product.id,
        created_by=current_user.id,
        type=MovementType.IN,
        quantity=data.quantity,
        stock_before=stock_before,
        stock_after=product.current_stock,
        reason=data.reason
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.post("/out", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def stock_out(
    data: StockOutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record stock out."""
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.current_stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    stock_before = product.current_stock
    product.current_stock -= data.quantity
    
    movement = StockMovement(
        product_id=product.id,
        created_by=current_user.id,
        type=MovementType.OUT,
        quantity=data.quantity,
        stock_before=stock_before,
        stock_after=product.current_stock,
        reason=data.reason
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.post("/adjust", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def stock_adjust(
    data: StockAdjustCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Adjust stock (can be positive or negative)."""
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.current_stock + data.quantity < 0:
        raise HTTPException(status_code=400, detail="Adjustment would result in negative stock")
    
    stock_before = product.current_stock
    product.current_stock += data.quantity
    
    movement = StockMovement(
        product_id=product.id,
        created_by=current_user.id,
        type=MovementType.ADJUST,
        quantity=data.quantity,
        stock_before=stock_before,
        stock_after=product.current_stock,
        reason=data.reason
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement
