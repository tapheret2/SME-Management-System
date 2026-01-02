"""Stock Movement model."""
import enum
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.base import UUIDMixin


class MovementType(str, enum.Enum):
    IN = "in"        # Stock received (from supplier or adjustment)
    OUT = "out"      # Stock shipped (to customer or adjustment)
    ADJUST = "adjust"  # Inventory adjustment


class StockMovement(Base, UUIDMixin):
    """Stock movement tracking - only has created_at (no updates)."""
    __tablename__ = "stock_movements"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("sales_orders.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    stock_before = Column(Integer, nullable=False)
    stock_after = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="stock_movements")
    supplier = relationship("Supplier", back_populates="stock_movements")
    order = relationship("SalesOrder", back_populates="stock_movements")
    creator = relationship("User", back_populates="stock_movements", foreign_keys=[created_by])
    
    __table_args__ = (
        Index("idx_stock_movements_product_id", "product_id"),
        Index("idx_stock_movements_created_at", "created_at"),
        Index("idx_stock_movements_type", "type"),
    )
    
    def __repr__(self):
        return f"<StockMovement {self.type.value} {self.quantity} of product {self.product_id}>"
