from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional

from app.api.deps import DBSession, CurrentUser
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.services.audit import log_create, log_update, log_delete

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None
):
    """
    List all customers with pagination and search.
    """
    query = db.query(Customer)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_pattern)) |
            (Customer.code.ilike(search_pattern)) |
            (Customer.phone.ilike(search_pattern))
        )
    
    total = query.count()
    items = query.order_by(Customer.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return CustomerListResponse(items=items, total=total, page=page, size=size)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(request: CustomerCreate, db: DBSession, current_user: CurrentUser):
    """
    Create a new customer.
    """
    # Check if code already exists
    existing = db.query(Customer).filter(Customer.code == request.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer code already exists"
        )
    
    customer = Customer(**request.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    # Audit log
    log_create(db, current_user.id, "customer", customer.id, request.model_dump())
    
    return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: DBSession, current_user: CurrentUser):
    """
    Get a specific customer by ID.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, request: CustomerUpdate, db: DBSession, current_user: CurrentUser):
    """
    Update a customer.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    old_values = {
        "code": customer.code,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "address": customer.address,
        "notes": customer.notes
    }
    
    # Check if new code is taken
    if request.code is not None and request.code != customer.code:
        existing = db.query(Customer).filter(Customer.code == request.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer code already exists"
            )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    # Audit log
    log_update(db, current_user.id, "customer", customer.id, old_values, update_data)
    
    return customer


@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: DBSession, current_user: CurrentUser):
    """
    Delete a customer.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check if customer has orders
    if customer.orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete customer with existing orders"
        )
    
    old_values = {
        "code": customer.code,
        "name": customer.name
    }
    
    db.delete(customer)
    db.commit()
    
    # Audit log
    log_delete(db, current_user.id, "customer", customer_id, old_values)
    
    return {"message": "Customer deleted successfully"}
