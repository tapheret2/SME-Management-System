"""Payment model."""
import enum
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Enum, ForeignKey, Index, DateTime, Boolean
from sqlalchemy.sql import func

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin, UUID


class PaymentType(str, enum.Enum):
    INCOMING = "incoming"  # From customer
    OUTGOING = "outgoing"  # To supplier


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK = "bank"
    OTHER = "other"


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"
    
    payment_number = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(Enum(PaymentType), nullable=False)
    method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False)
    customer_id = Column(UUID(), ForeignKey("customers.id"), nullable=True)
    supplier_id = Column(UUID(), ForeignKey("suppliers.id"), nullable=True)
    order_id = Column(UUID(), ForeignKey("sales_orders.id"), nullable=True)
    created_by = Column(UUID(), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    is_settlement = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_payments_payment_date", "payment_date"),
        Index("idx_payments_type", "type"),
        Index("idx_payments_customer_id", "customer_id"),
        Index("idx_payments_supplier_id", "supplier_id"),
    )
    
    def __repr__(self):
        return f"<Payment {self.payment_number}>"
