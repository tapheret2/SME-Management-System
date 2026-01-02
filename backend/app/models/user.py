"""User model with RBAC."""
import enum
from sqlalchemy import Column, String, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)
    is_active = Column(Boolean, default=True)
    refresh_token = Column(Text, nullable=True)
    
    # Relationships
    orders = relationship("SalesOrder", back_populates="creator", foreign_keys="SalesOrder.created_by")
    payments = relationship("Payment", back_populates="creator", foreign_keys="Payment.created_by")
    stock_movements = relationship("StockMovement", back_populates="creator", foreign_keys="StockMovement.created_by")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
