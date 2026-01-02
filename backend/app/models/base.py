"""Base mixins for SQLAlchemy models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func


class UUIDMixin:
    """Mixin that adds UUID primary key."""
    
    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""
    
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )


class SoftDeleteMixin:
    """Mixin that adds soft delete support via deleted_at."""
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True)
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    def soft_delete(self):
        """Mark the record as deleted."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
