"""Supplier model."""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Index

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
    
    __table_args__ = (
        Index("idx_suppliers_name", "name"),
    )
    
    def __repr__(self):
        return f"<Supplier {self.code}: {self.name}>"
