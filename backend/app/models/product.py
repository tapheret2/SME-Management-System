"""Product model."""
from sqlalchemy import Column, String, Integer, Boolean, Numeric, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"
    
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    unit = Column(String(20), default="cái", nullable=False)
    cost_price = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    sell_price = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    current_stock = Column(Integer, default=0, nullable=False)
    min_stock = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    order_items = relationship("SalesOrderItem", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")
    
    __table_args__ = (
        Index("idx_products_category", "category"),
        Index("idx_products_is_active", "is_active"),
    )
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is below minimum stock level."""
        return self.current_stock <= self.min_stock
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"
