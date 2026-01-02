from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PaymentType(str, enum.Enum):
    INCOMING = "incoming"  # From customer
    OUTGOING = "outgoing"  # To supplier


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK = "bank"
    OTHER = "other"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Type
    type = Column(SQLEnum(PaymentType), nullable=False)
    method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CASH, nullable=False)
    
    # Relations (one of customer_id or supplier_id should be set)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)
    
    # Amount (VND)
    amount = Column(Numeric(15, 0), nullable=False)
    
    notes = Column(Text, nullable=True)
    payment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    customer = relationship("Customer", backref="payments")
    supplier = relationship("Supplier", backref="payments")
    order = relationship("SalesOrder", backref="payments")
    creator = relationship("User", backref="created_payments")
    
    def __repr__(self):
        return f"<Payment {self.payment_number} {self.type.value}>"
