"""
Reassessment Queue API.
Exposes patients requiring immediate clinician attention due to deterioration or overdue wait times.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.entities import Patient, User
from app.schemas.schemas import PatientOut
from app.reassessment.monitor import reassessment_monitor

router = APIRouter(prefix="/reassessment", tags=["Reassessment Queue"])

@router.get("/queue", response_model=List[PatientOut])
def get_attention_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    """Returns patients flagged for reassessment or with active deterioration."""
    patients = db.query(Patient).all()
    attention_list = []

    for p in patients:
        needs_reassess, reasons, score = reassessment_monitor.evaluate_patient_reassessment(p)
        if needs_reassess or p.needs_reassessment:
            p.needs_reassessment = True
            p.reassessment_reasons = list(set(p.reassessment_reasons + reasons))
            attention_list.append((p, score))

    # Sort highest attention priority score first
    attention_list.sort(key=lambda item: item[1], reverse=True)
    return [item[0] for item in attention_list]
