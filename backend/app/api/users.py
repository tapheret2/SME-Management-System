from fastapi import APIRouter, HTTPException, status
from typing import List

from app.api.deps import DBSession, AdminOnly
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.auth import hash_password, create_user
from app.services.audit import log_create, log_update, log_delete

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
async def list_users(db: DBSession, current_user: AdminOnly):
    """
    List all users (Admin only).
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(request: UserCreate, db: DBSession, current_user: AdminOnly):
    """
    Create a new user (Admin only).
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role
    )
    
    # Audit log
    log_create(db, current_user.id, "user", user.id, {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value
    })
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: DBSession, current_user: AdminOnly):
    """
    Get a specific user by ID (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, request: UserUpdate, db: DBSession, current_user: AdminOnly):
    """
    Update a user (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_values = {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active
    }
    
    # Update fields
    if request.email is not None:
        # Check if email is taken
        existing = db.query(User).filter(User.email == request.email, User.id != user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = request.email
    
    if request.full_name is not None:
        user.full_name = request.full_name
    
    if request.role is not None:
        user.role = request.role
    
    if request.is_active is not None:
        user.is_active = request.is_active
    
    if request.password is not None:
        user.hashed_password = hash_password(request.password)
    
    db.commit()
    db.refresh(user)
    
    # Audit log
    log_update(db, current_user.id, "user", user.id, old_values, {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active
    })
    
    return user


@router.delete("/{user_id}")
async def deactivate_user(user_id: int, db: DBSession, current_user: AdminOnly):
    """
    Deactivate a user (Admin only). Does not delete, just sets is_active=False.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_values = {"is_active": user.is_active}
    user.is_active = False
    db.commit()
    
    # Audit log
    log_update(db, current_user.id, "user", user.id, old_values, {"is_active": False})
    
    return {"message": "User deactivated successfully"}
