"""StockMovement model."""
import enum
from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, Index, DateTime
from sqlalchemy.sql import func

from app.database import Base
from app.models.base import UUIDMixin, UUID


class MovementType(str, enum.Enum):
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"


class StockMovement(Base, UUIDMixin):
    __tablename__ = "stock_movements"
    
    product_id = Column(UUID(), ForeignKey("products.id"), nullable=False)
    created_by = Column(UUID(), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    stock_before = Column(Integer, nullable=False)
    stock_after = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_stock_movements_product_id", "product_id"),
        Index("idx_stock_movements_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<StockMovement {self.type.value} {self.quantity}>"
