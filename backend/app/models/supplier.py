"""Supplier model."""
from sqlalchemy import Column, String, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Supplier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "suppliers"
    
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    total_payable = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    
    # Relationships
    stock_movements = relationship("StockMovement", back_populates="supplier")
    payments = relationship("Payment", back_populates="supplier")
    
    __table_args__ = (
        Index("idx_suppliers_name", "name"),
    )
    
    def __repr__(self):
        return f"<Supplier {self.code}: {self.name}>"
