from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.api.deps import DBSession, CurrentUser
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse, SupplierListResponse
from app.services.audit import log_create, log_update, log_delete

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=SupplierListResponse)
async def list_suppliers(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None
):
    """
    List all suppliers with pagination and search.
    """
    query = db.query(Supplier)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Supplier.name.ilike(search_pattern)) |
            (Supplier.code.ilike(search_pattern)) |
            (Supplier.phone.ilike(search_pattern))
        )
    
    total = query.count()
    items = query.order_by(Supplier.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return SupplierListResponse(items=items, total=total, page=page, size=size)


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(request: SupplierCreate, db: DBSession, current_user: CurrentUser):
    """
    Create a new supplier.
    """
    # Check if code already exists
    existing = db.query(Supplier).filter(Supplier.code == request.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier code already exists"
        )
    
    supplier = Supplier(**request.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    
    # Audit log
    log_create(db, current_user.id, "supplier", supplier.id, request.model_dump())
    
    return supplier


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: int, db: DBSession, current_user: CurrentUser):
    """
    Get a specific supplier by ID.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(supplier_id: int, request: SupplierUpdate, db: DBSession, current_user: CurrentUser):
    """
    Update a supplier.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    old_values = {
        "code": supplier.code,
        "name": supplier.name,
        "phone": supplier.phone,
        "email": supplier.email,
        "address": supplier.address,
        "notes": supplier.notes
    }
    
    # Check if new code is taken
    if request.code is not None and request.code != supplier.code:
        existing = db.query(Supplier).filter(Supplier.code == request.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier code already exists"
            )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    db.commit()
    db.refresh(supplier)
    
    # Audit log
    log_update(db, current_user.id, "supplier", supplier.id, old_values, update_data)
    
    return supplier


@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: int, db: DBSession, current_user: CurrentUser):
    """
    Delete a supplier.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Check if supplier has stock movements
    if supplier.stock_movements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete supplier with existing stock movements"
        )
    
    old_values = {
        "code": supplier.code,
        "name": supplier.name
    }
    
    db.delete(supplier)
    db.commit()
    
    # Audit log
    log_delete(db, current_user.id, "supplier", supplier_id, old_values)
    
    return {"message": "Supplier deleted successfully"}
