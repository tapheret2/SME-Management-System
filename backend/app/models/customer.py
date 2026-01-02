"""Customer model."""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Index

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Customer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "customers"
    
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    total_debt = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    
    __table_args__ = (
        Index("idx_customers_name", "name"),
    )
    
    def __repr__(self):
        return f"<Customer {self.code}: {self.name}>"
