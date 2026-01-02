from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # What
    entity_type = Column(String(100), nullable=False)  # e.g., "product", "order"
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # e.g., "create", "update", "delete"
    
    # Changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # When
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}:{self.entity_id}>"
