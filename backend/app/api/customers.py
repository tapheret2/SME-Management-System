"""Customers API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.customer import Customer
from app.models.order import SalesOrder
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.api.deps import get_current_user
from app.helpers import sanitize_like


router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """List customers with pagination."""
    query = db.query(Customer)
    
    if search:
        safe_search = sanitize_like(search)
        query = query.filter(
            or_(
                Customer.code.ilike(f"%{safe_search}%"),
                Customer.name.ilike(f"%{safe_search}%"),
                Customer.phone.ilike(f"%{safe_search}%")
            )
        )
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return CustomerListResponse(items=items, total=total)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Create a new customer."""
    existing = db.query(Customer).filter(Customer.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer code already exists")
    
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Get a single customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Update a customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
    
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    _current_user = Depends(get_current_user)
):
    """Delete a customer (checks for existing orders first)."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # P2 Fix: Check for existing orders before delete
    has_orders = db.query(SalesOrder).filter(SalesOrder.customer_id == customer_id).first()
    if has_orders:
        raise HTTPException(status_code=400, detail="Cannot delete customer with existing orders")
    
    db.delete(customer)
    db.commit()
    return None
