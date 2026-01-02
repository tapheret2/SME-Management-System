"""AuditLog model."""
import enum
from sqlalchemy import Column, String, Text, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base
from app.models.base import UUIDMixin, UUID


class ActionType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    STATUS_CHANGE = "status_change"
    DELETE = "delete"


class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"
    
    action = Column(String(20), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(), nullable=False)
    user_id = Column(UUID(), nullable=False)
    before_data = Column(Text, nullable=True)  # JSON string
    after_data = Column(Text, nullable=True)   # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}:{self.entity_id}>"
