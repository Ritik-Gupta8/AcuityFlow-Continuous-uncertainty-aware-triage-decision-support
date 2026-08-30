"""
Audit Trail API.
Exposes FHIR-inspired security and clinical decision audit log events.

Architecture Note:
- Application/API Layer: Strictly read-only query interface. Audit events are recorded
  exclusively via internal domain services (triage, clinician override, vital updates,
  and simulation events). No update, edit, or delete endpoints exist.
- Immutability Disclaimer: In this prototype, append-only behavior is enforced at the
  application and API layers. Production deployment requires database-level WORM
  (Write Once Read Many) storage or cryptographically verifiable ledger audit logging.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entities import AuditEvent, User
from app.schemas.schemas import AuditEventOut

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("", response_model=List[AuditEventOut])
def get_audit_trail(
    patient_id: Optional[str] = Query(None, description="Filter by specific patient ID"),
    limit: int = Query(50, description="Max records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If unrestricted system-wide audit query, require supervisor or admin role
    if not patient_id and current_user.role.lower() not in ["supervisor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied — nurses can only inspect patient-specific audit history. Supervisor or Admin role required for full audit explorer."
        )

    query = db.query(AuditEvent)
    if patient_id:
        query = query.filter(AuditEvent.patient_id == patient_id)
    return query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()
