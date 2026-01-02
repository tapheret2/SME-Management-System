from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.api.deps import DBSession, CurrentUser
from app.models.stock import StockMovement, StockMovementType
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.stock import (
    StockInCreate, StockOutCreate, StockAdjustCreate,
    StockMovementResponse, StockMovementListResponse
)
from app.services.audit import log_create

router = APIRouter(prefix="/stock", tags=["Stock"])


def build_movement_response(movement: StockMovement, db: DBSession) -> StockMovementResponse:
    """Build StockMovementResponse from StockMovement."""
    product = db.query(Product).filter(Product.id == movement.product_id).first()
    supplier = None
    order = None
    
    if movement.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == movement.supplier_id).first()
    
    return StockMovementResponse(
        id=movement.id,
        product_id=movement.product_id,
        product_name=product.name if product else None,
        product_sku=product.sku if product else None,
        supplier_id=movement.supplier_id,
        supplier_name=supplier.name if supplier else None,
        order_id=movement.order_id,
        order_number=movement.order.order_number if movement.order else None,
        type=movement.type,
        quantity=movement.quantity,
        stock_before=movement.stock_before,
        stock_after=movement.stock_after,
        reason=movement.reason,
        created_by=movement.created_by,
        creator_name=movement.creator.full_name if movement.creator else None,
        created_at=movement.created_at
    )


@router.get("", response_model=StockMovementListResponse)
async def list_stock_movements(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    product_id: Optional[int] = None,
    type: Optional[StockMovementType] = None
):
    """
    List all stock movements with pagination and filters.
    """
    query = db.query(StockMovement)
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    
    if type:
        query = query.filter(StockMovement.type == type)
    
    total = query.count()
    movements = query.order_by(StockMovement.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    items = [build_movement_response(m, db) for m in movements]
    
    return StockMovementListResponse(items=items, total=total, page=page, size=size)


@router.post("/in", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
async def stock_in(request: StockInCreate, db: DBSession, current_user: CurrentUser):
    """
    Record stock coming in (purchase, return).
    """
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if request.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == request.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
    
    stock_before = product.current_stock
    product.current_stock += request.quantity
    
    movement = StockMovement(
        product_id=request.product_id,
        supplier_id=request.supplier_id,
        type=StockMovementType.IN,
        quantity=request.quantity,
        stock_before=stock_before,
        stock_after=product.current_stock,
        reason=request.reason or "Stock in",
        created_by=current_user.id
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    
    # Audit log
    log_create(db, current_user.id, "stock_movement", movement.id, {
        "type": "in",
        "product_id": request.product_id,
        "quantity": request.quantity
    })
    
    return build_movement_response(movement, db)


@router.post("/out", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
async def stock_out(request: StockOutCreate, db: DBSession, current_user: CurrentUser):
    """
    Record stock going out (manual deduction).
    """
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.current_stock < request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {product.current_stock}"
        )
    
    stock_before = product.current_stock
    product.current_stock -= request.quantity
    
    movement = StockMovement(
        product_id=request.product_id,
        order_id=request.order_id,
        type=StockMovementType.OUT,
        quantity=request.quantity,
        stock_before=stock_before,
        stock_after=product.current_stock,
        reason=request.reason or "Stock out",
        created_by=current_user.id
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    
    # Audit log
    log_create(db, current_user.id, "stock_movement", movement.id, {
        "type": "out",
        "product_id": request.product_id,
        "quantity": request.quantity
    })
    
    return build_movement_response(movement, db)


@router.post("/adjust", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
async def stock_adjust(request: StockAdjustCreate, db: DBSession, current_user: CurrentUser):
    """
    Adjust stock (can be positive or negative).
    """
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stock_before = product.current_stock
    new_stock = stock_before + request.quantity
    
    if new_stock < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Adjustment would result in negative stock ({new_stock})"
        )
    
    product.current_stock = new_stock
    
    movement = StockMovement(
        product_id=request.product_id,
        type=StockMovementType.ADJUST,
        quantity=request.quantity,
        stock_before=stock_before,
        stock_after=product.current_stock,
        reason=request.reason,
        created_by=current_user.id
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    
    # Audit log
    log_create(db, current_user.id, "stock_movement", movement.id, {
        "type": "adjust",
        "product_id": request.product_id,
        "quantity": request.quantity,
        "reason": request.reason
    })
    
    return build_movement_response(movement, db)
