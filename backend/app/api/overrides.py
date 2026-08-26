"""
Clinician Decision & Override API.
Handles clinician authority, manual priority adjustments, and audit logging.
"""

from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Patient, ClinicianDecision, AuditEvent
from app.schemas.schemas import ClinicianDecisionCreate, ClinicianDecisionOut

router = APIRouter(prefix="/patients", tags=["Decisions & Overrides"])

@router.post("/{patient_id}/decision", response_model=ClinicianDecisionOut)
def record_clinician_decision(
    patient_id: str,
    decision_in: ClinicianDecisionCreate,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # If action is an override, require an explicit reason
    if decision_in.clinician_action == "override" and not decision_in.override_reason:
        raise HTTPException(status_code=400, detail="An override reason is required when overriding AI recommendation.")

    decision_record = ClinicianDecision(
        decision_id=f"DEC-{uuid.uuid4().hex[:8]}",
        patient_id=patient_id,
        clinician_id=decision_in.clinician_id,
        actor_role=decision_in.actor_role,
        ai_priority=patient.current_priority,
        ai_confidence=patient.current_confidence,
        clinician_action=decision_in.clinician_action,
        final_priority=decision_in.final_priority,
        override_reason=decision_in.override_reason,
        clinician_note=decision_in.clinician_note,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(decision_record)

    # Update patient's active priority
    old_priority = patient.current_priority
    patient.current_priority = decision_in.final_priority
    if decision_in.clinician_action == "accept":
        patient.needs_reassessment = False
        patient.reassessment_reasons = []

    # Record to Audit Log (FHIR-inspired structure)
    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=decision_in.clinician_id,
        actor_role=decision_in.actor_role,
        event_type="override" if decision_in.clinician_action == "override" else "clinician_decision",
        patient_id=patient_id,
        recommendation=old_priority,
        confidence=patient.current_confidence,
        decision=decision_in.final_priority,
        override_reason=decision_in.override_reason,
        details={
            "action": decision_in.clinician_action,
            "clinician_note": decision_in.clinician_note
        }
    )
    db.add(audit)
    db.commit()

    return decision_record
