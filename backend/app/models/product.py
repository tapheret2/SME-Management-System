from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    unit = Column(String(50), default="cái", nullable=False)  # pcs, kg, etc.
    
    # Pricing (VND - no decimals)
    cost_price = Column(Numeric(15, 0), default=0, nullable=False)
    sell_price = Column(Numeric(15, 0), default=0, nullable=False)
    
    # Inventory
    current_stock = Column(Integer, default=0, nullable=False)
    min_stock = Column(Integer, default=0, nullable=False)  # Low stock threshold
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    @property
    def is_low_stock(self) -> bool:
        return self.current_stock <= self.min_stock
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"
