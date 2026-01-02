from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.DRAFT, nullable=False)
    
    # Amounts (VND)
    subtotal = Column(Numeric(15, 0), default=0, nullable=False)
    discount = Column(Numeric(15, 0), default=0, nullable=False)
    total = Column(Numeric(15, 0), default=0, nullable=False)
    paid_amount = Column(Numeric(15, 0), default=0, nullable=False)
    
    notes = Column(Text, nullable=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    customer = relationship("Customer", backref="orders")
    creator = relationship("User", backref="created_orders")
    line_items = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    
    @property
    def remaining_amount(self) -> int:
        return int(self.total) - int(self.paid_amount)
    
    def __repr__(self):
        return f"<SalesOrder {self.order_number}>"


class OrderLine(Base):
    __tablename__ = "order_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(15, 0), nullable=False)
    discount = Column(Numeric(15, 0), default=0, nullable=False)
    line_total = Column(Numeric(15, 0), nullable=False)
    
    # Relationships
    order = relationship("SalesOrder", back_populates="line_items")
    product = relationship("Product", backref="order_lines")
    
    def __repr__(self):
        return f"<OrderLine order={self.order_id} product={self.product_id}>"
