from datetime import datetime, timezone
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.entities import Patient, ClinicianDecision, AuditEvent, User
from app.schemas.schemas import ClinicianDecisionCreate, ClinicianDecisionOut

router = APIRouter(prefix="/patients", tags=["Decisions & Overrides"])

@router.post("/{patient_id}/decision", response_model=ClinicianDecisionOut)
def record_clinician_decision(
    patient_id: str,
    decision_in: ClinicianDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # If action is an override, require an explicit reason
    if decision_in.clinician_action == "override" and not decision_in.override_reason:
        raise HTTPException(status_code=400, detail="An override reason is required when overriding AI recommendation.")

    # 1. Authoritative Actor Identity from Authenticated Session (Client cannot spoof)
    actor_id = current_user.username
    actor_role = current_user.role

    # 2. Source of Truth: Read immutable AI recommendation
    ai_priority_val = patient.ai_priority or "MODERATE"
    ai_confidence_val = patient.ai_confidence if patient.ai_confidence is not None else patient.current_confidence
    ai_risk_score_val = patient.ai_risk_score if patient.ai_risk_score is not None else patient.current_risk_score

    decision_record = ClinicianDecision(
        decision_id=f"DEC-{uuid.uuid4().hex[:8]}",
        patient_id=patient_id,
        clinician_id=actor_id,
        actor_role=actor_role,
        ai_priority=ai_priority_val,
        ai_confidence=ai_confidence_val,
        clinician_action=decision_in.clinician_action,
        final_priority=decision_in.final_priority,
        override_reason=decision_in.override_reason,
        clinician_note=decision_in.clinician_note,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(decision_record)

    # 3. Update human decision and operational effective priority without mutating ai_priority!
    if decision_in.clinician_action == "override":
        patient.clinician_decision = decision_in.final_priority
        patient.clinician_action = "override"
        patient.override_reason = decision_in.override_reason
        patient.effective_priority = decision_in.final_priority
        patient.current_priority = decision_in.final_priority
    elif decision_in.clinician_action == "accept":
        patient.clinician_decision = ai_priority_val
        patient.clinician_action = "accept"
        patient.override_reason = None
        patient.effective_priority = ai_priority_val
        patient.current_priority = ai_priority_val
        patient.needs_reassessment = False
        patient.reassessment_reasons = []
        patient.reassessment_state = "NORMAL"
    elif decision_in.clinician_action == "escalate":
        patient.clinician_decision = decision_in.final_priority
        patient.clinician_action = "escalate"
        patient.override_reason = decision_in.override_reason or "Clinician manual escalation"
        patient.effective_priority = decision_in.final_priority
        patient.current_priority = decision_in.final_priority

    # 4. Record to Audit Log with Authoritative Authenticated Identity
    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=actor_id,
        actor_role=actor_role,
        event_type="override" if decision_in.clinician_action == "override" else "clinician_decision",
        patient_id=patient_id,
        recommendation=ai_priority_val,
        confidence=ai_confidence_val,
        decision=decision_in.final_priority,
        override_reason=decision_in.override_reason,
        details={
            "ai_priority": ai_priority_val,
            "ai_risk_score": ai_risk_score_val,
            "ai_confidence": ai_confidence_val,
            "clinician_decision": decision_in.final_priority,
            "effective_priority": patient.effective_priority,
            "override_reason": decision_in.override_reason,
            "action": decision_in.clinician_action,
            "clinician_note": decision_in.clinician_note
        },
        policy_version="v2.0.0-prototype",
        model_version="ml-baseline-v1"
    )
    db.add(audit)
    db.commit()
    db.refresh(decision_record)

    return decision_record

@router.get("/{patient_id}/decisions", response_model=List[ClinicianDecisionOut])
def get_patient_decisions(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    """Retrieves all clinician decision history for a patient."""
    return db.query(ClinicianDecision).filter(ClinicianDecision.patient_id == patient_id).order_by(ClinicianDecision.timestamp.desc()).all()
