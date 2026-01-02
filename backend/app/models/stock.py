from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class StockMovementType(str, enum.Enum):
    IN = "in"        # Stock coming in (purchase, return)
    OUT = "out"      # Stock going out (sale, damage)
    ADJUST = "adjust"  # Manual adjustment


class StockMovement(Base):
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relations
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)  # For stock in
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)  # For stock out (sales)
    
    # Movement details
    type = Column(SQLEnum(StockMovementType), nullable=False)
    quantity = Column(Integer, nullable=False)  # Positive for in, negative for out
    stock_before = Column(Integer, nullable=False)
    stock_after = Column(Integer, nullable=False)
    
    reason = Column(Text, nullable=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", backref="stock_movements")
    supplier = relationship("Supplier", backref="stock_movements")
    order = relationship("SalesOrder", backref="stock_movements")
    creator = relationship("User", backref="created_movements")
    
    def __repr__(self):
        return f"<StockMovement {self.type.value} {self.quantity}>"
