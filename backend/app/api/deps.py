from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth import decode_token, get_user_by_id


# Security scheme
security = HTTPBearer()

# Type aliases
DBSession = Annotated[Session, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: DBSession
) -> User:
    """Get the current authenticated user from the JWT token."""
    token = credentials.credentials
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = get_user_by_id(db, payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker


# Pre-defined role dependencies
AdminOnly = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
ManagerOrAdmin = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))]
AllRoles = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF))]
