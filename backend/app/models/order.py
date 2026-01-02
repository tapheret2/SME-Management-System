"""SalesOrder and SalesOrderItem models."""
import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Integer, Text, Numeric, Enum, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin, UUID


class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


STATUS_TRANSITIONS = {
    OrderStatus.DRAFT: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.SHIPPED: [OrderStatus.COMPLETED],
    OrderStatus.COMPLETED: [],
    OrderStatus.CANCELLED: [],
}


class SalesOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sales_orders"
    
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(UUID(), ForeignKey("customers.id"), nullable=False)
    created_by = Column(UUID(), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT, nullable=False)
    subtotal = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    discount = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    total = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    paid_amount = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    notes = Column(Text, nullable=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    line_items = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_sales_orders_order_date", "order_date"),
        Index("idx_sales_orders_status", "status"),
        Index("idx_sales_orders_customer_id", "customer_id"),
    )
    
    @property
    def remaining_amount(self) -> Decimal:
        return self.total - self.paid_amount
    
    def can_transition_to(self, new_status: OrderStatus) -> bool:
        return new_status in STATUS_TRANSITIONS.get(self.status, [])
    
    def calculate_totals(self):
        self.subtotal = sum(item.line_total for item in self.line_items)
        self.total = self.subtotal - self.discount
    
    def __repr__(self):
        return f"<SalesOrder {self.order_number}>"


class SalesOrderItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sales_order_items"
    
    order_id = Column(UUID(), ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(15, 0), nullable=False)
    discount = Column(Numeric(15, 0), default=Decimal("0"), nullable=False)
    line_total = Column(Numeric(15, 0), nullable=False)
    
    # Relationships
    order = relationship("SalesOrder", back_populates="line_items")
    
    __table_args__ = (
        Index("idx_order_items_order_id", "order_id"),
        Index("idx_order_items_product_id", "product_id"),
    )
    
    def calculate_total(self):
        self.line_total = (self.unit_price * self.quantity) - self.discount
    
    def __repr__(self):
        return f"<SalesOrderItem order={self.order_id}>"
