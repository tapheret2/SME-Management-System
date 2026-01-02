"""Payment model."""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, Enum, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from decimal import Decimal

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class PaymentType(str, enum.Enum):
    INCOMING = "incoming"  # From customer (收款)
    OUTGOING = "outgoing"  # To supplier (付款)


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK = "bank"
    OTHER = "other"


class Payment(Base, UUIDMixin, TimestampMixin):
    """Payment model for tracking AR/AP."""
    __tablename__ = "payments"
    
    payment_number = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(Enum(PaymentType), nullable=False)
    method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("sales_orders.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(15, 0), nullable=False)
    notes = Column(Text, nullable=True)
    payment_date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="payments")
    supplier = relationship("Supplier", back_populates="payments")
    order = relationship("SalesOrder", back_populates="payments")
    creator = relationship("User", back_populates="payments", foreign_keys=[created_by])
    
    __table_args__ = (
        Index("idx_payments_payment_date", "payment_date"),
        Index("idx_payments_type", "type"),
        Index("idx_payments_customer_id", "customer_id"),
        Index("idx_payments_supplier_id", "supplier_id"),
    )
    
    def __repr__(self):
        return f"<Payment {self.payment_number} {self.type.value} {self.amount}>"
