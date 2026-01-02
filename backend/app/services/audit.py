from typing import Optional
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    entity_type: str,
    entity_id: int,
    action: str,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None
) -> AuditLog:
    """Create an audit log entry."""
    log = AuditLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_values=old_values,
        new_values=new_values
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def log_create(db: Session, user_id: int, entity_type: str, entity_id: int, new_values: dict) -> AuditLog:
    """Log a create action."""
    return create_audit_log(db, user_id, entity_type, entity_id, "create", new_values=new_values)


def log_update(db: Session, user_id: int, entity_type: str, entity_id: int, old_values: dict, new_values: dict) -> AuditLog:
    """Log an update action."""
    return create_audit_log(db, user_id, entity_type, entity_id, "update", old_values=old_values, new_values=new_values)


def log_delete(db: Session, user_id: int, entity_type: str, entity_id: int, old_values: dict) -> AuditLog:
    """Log a delete action."""
    return create_audit_log(db, user_id, entity_type, entity_id, "delete", old_values=old_values)
