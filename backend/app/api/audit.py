"""Audit API endpoint."""
from typing import Optional
from uuid import UUID
from datetime import datetime
import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.audit import AuditLog
from app.api.deps import require_admin


router = APIRouter(prefix="/audit", tags=["audit"])


class AuditLogResponse(BaseModel):
    id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    user_id: UUID
    before_data: Optional[dict] = None
    after_data: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int


@router.get("", response_model=AuditListResponse)
def list_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin = Depends(require_admin)
):
    """List audit logs (admin only)."""
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    
    total = query.count()
    logs = query.offset((page - 1) * size).limit(size).all()
    
    # Parse JSON strings back to dicts for response
    items = []
    for log in logs:
        items.append(AuditLogResponse(
            id=log.id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            user_id=log.user_id,
            before_data=json.loads(log.before_data) if log.before_data else None,
            after_data=json.loads(log.after_data) if log.after_data else None,
            created_at=log.created_at
        ))
    
    return AuditListResponse(items=items, total=total)
