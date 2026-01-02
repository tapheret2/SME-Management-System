"""Audit service for logging entity changes."""
import json
from typing import Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: UUID,
    user_id: UUID,
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None
):
    """Log an action to audit trail. Minimal and non-blocking."""
    audit = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        before_data=json.dumps(before_data, default=str) if before_data else None,
        after_data=json.dumps(after_data, default=str) if after_data else None
    )
    db.add(audit)
    # Note: commit handled by caller to avoid extra DB roundtrip


def entity_snapshot(obj, fields: list[str]) -> dict:
    """Create minimal snapshot of entity for audit."""
    return {f: getattr(obj, f, None) for f in fields if hasattr(obj, f)}
