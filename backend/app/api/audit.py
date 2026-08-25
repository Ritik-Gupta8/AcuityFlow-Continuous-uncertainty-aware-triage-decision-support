"""
Audit Trail API.
Exposes FHIR-inspired security and clinical decision audit log events.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import AuditEvent
from app.schemas.schemas import AuditEventOut

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("", response_model=List[AuditEventOut])
def get_audit_trail(
    patient_id: str = Query(None, description="Filter by specific patient ID"),
    limit: int = Query(50, description="Max records to return"),
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if patient_id:
        query = query.filter(AuditEvent.patient_id == patient_id)
    return query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()
