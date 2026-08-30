"""
Simulation & Demo Controls API.
Enables advancing simulated time, triggering deterioration events, and toggling 3x surge mode.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, Base, engine
from app.core.security import require_role
from app.models.entities import Patient, Observation, AuditEvent, TriageResult, User
from app.ml.risk_model import risk_engine
from app.schemas.schemas import AdvanceTimeRequest, SurgeToggleRequest, InjectVitalsRequest, SimulationStatus
from app.reassessment.monitor import reassessment_monitor
from app.policy.action_policy import evaluate_patient_triage
from app.data.seed_cases import seed_database, populate_surge_patients, remove_surge_patients

router = APIRouter(prefix="/simulation", tags=["Simulation Controls"])

# In-memory surge state
SIMULATION_STATE = {
    "surge_active": False,
    "current_time_offset_minutes": 0,
}

@router.get("/status", response_model=SimulationStatus)
def get_simulation_status():
    return {
        "surge_active": SIMULATION_STATE["surge_active"],
        "time_offset_minutes": SIMULATION_STATE["current_time_offset_minutes"],
        "model_status": risk_engine.model_status,
        "model_available": risk_engine.model_available,
        "model_source": risk_engine.model_source,
        "disclaimer": "Simulated Environment • Synthetic Data"
    }

@router.post("/advance-time")
def advance_simulated_time(
    req: AdvanceTimeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    """Advances waiting time for all waiting patients and recomputes reassessments."""
    SIMULATION_STATE["current_time_offset_minutes"] += req.minutes
    patients = db.query(Patient).filter(Patient.current_status == "WAITING").all()
    
    updated_count = 0
    reassessment_triggered = 0

    for p in patients:
        p.waiting_minutes += req.minutes
        needs_reassess, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(p)
        if needs_reassess:
            p.needs_reassessment = True
            p.reassessment_reasons = reasons
            reassessment_triggered += 1
        updated_count += 1

    # Log Audit Event
    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id="simulation-engine",
        actor_role="system",
        event_type="time_advance",
        patient_id=None,
        recommendation=None,
        confidence=None,
        decision="TIME_ADVANCE",
        override_reason=None,
        details={
            "minutes_advanced": req.minutes,
            "total_offset": SIMULATION_STATE["current_time_offset_minutes"],
            "patients_affected": updated_count,
            "reassessments_triggered": reassessment_triggered
        },
        policy_version="v2.0.0-prototype",
        model_version="ml-baseline-v1"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "advanced_minutes": req.minutes,
        "total_offset_minutes": SIMULATION_STATE["current_time_offset_minutes"],
        "reassessments_triggered": reassessment_triggered
    }

@router.post("/surge")
def toggle_surge_mode(
    req: SurgeToggleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    """Toggles 3x surge mode status and dynamically scales arrival workload."""
    SIMULATION_STATE["surge_active"] = req.surge_active
    
    if req.surge_active:
        populate_surge_patients(db)
    else:
        remove_surge_patients(db)

    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=current_user.username,
        actor_role=current_user.role,
        event_type="surge_toggle",
        patient_id=None,
        recommendation=None,
        confidence=None,
        decision="SURGE_TOGGLE",
        override_reason=None,
        details={"surge_active": req.surge_active, "multiplier": 3.0 if req.surge_active else 1.0},
        policy_version="v2.0.0-prototype",
        model_version="ml-baseline-v1"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "surge_active": req.surge_active,
        "message": "3x Surge mode activated: queue volume scaled 3x (72 patients) with attention-first prioritization" if req.surge_active else "Standard queue mode restored (24 patients)"
    }

@router.post("/inject-deterioration")
def inject_deterioration_vitals(
    req: InjectVitalsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    """Injects deteriorating vital signs into a patient (e.g. PT-021) to demo continuous re-triage."""
    patient = db.query(Patient).filter(Patient.patient_id == req.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # If vitals aren't specified, apply preset deterioration
    is_pt21 = (patient.patient_id == "PT-021")
    hr = req.heart_rate if req.heart_rate is not None else (118.0 if is_pt21 else 122.0)
    rr = req.respiratory_rate if req.respiratory_rate is not None else (26.0 if is_pt21 else 28.0)
    sbp = req.systolic_bp if req.systolic_bp is not None else (98.0 if is_pt21 else 94.0)
    dbp = req.diastolic_bp if req.diastolic_bp is not None else (62.0 if is_pt21 else 60.0)
    spo2 = req.spo2 if req.spo2 is not None else (91.0 if is_pt21 else 89.0)
    temp = req.temperature_c if req.temperature_c is not None else (37.3 if is_pt21 else 37.9)

    new_obs = Observation(
        observation_id=f"OBS-{uuid.uuid4().hex[:8]}",
        patient_id=patient.patient_id,
        timestamp=datetime.now(timezone.utc),
        heart_rate=hr,
        respiratory_rate=rr,
        systolic_bp=sbp,
        diastolic_bp=dbp,
        spo2=spo2,
        temperature_c=temp,
        measurement_source="device",
        observation_notes=req.notes or ("Simulated acute deterioration injection" if is_pt21 else "Simulated deterioration injection")
    )
    db.add(new_obs)
    if new_obs not in patient.observations:
        patient.observations.append(new_obs)
    db.flush()

    # Re-evaluate triage and reassessment
    eval_result = evaluate_patient_triage(patient, new_obs)
    patient.ai_priority = eval_result.priority
    patient.ai_workflow_action = eval_result.action
    patient.ai_confidence = eval_result.confidence_score
    patient.ai_risk_score = eval_result.risk_score
    if patient.clinician_action != "override":
        patient.effective_priority = eval_result.priority
        patient.current_priority = eval_result.priority
    else:
        patient.effective_priority = patient.clinician_decision
        patient.current_priority = patient.clinician_decision
    patient.current_action = eval_result.action
    patient.current_confidence = eval_result.confidence_score
    patient.current_risk_score = eval_result.risk_score

    needs_reassess, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    patient.needs_reassessment = True  # Explicitly flag deterioration
    patient.reassessment_reasons = reasons if reasons else ["Deteriorating vital signs detected"]

    # Persist updated TriageResult
    triage_record = TriageResult(
        result_id=f"TR-{patient.patient_id}-{uuid.uuid4().hex[:6]}",
        patient_id=patient.patient_id,
        timestamp=datetime.now(timezone.utc),
        risk_score=eval_result.risk_score,
        confidence_score=eval_result.confidence_score,
        data_completeness=eval_result.data_completeness,
        priority=eval_result.priority,
        action=eval_result.action,
        safety_flags=eval_result.safety_flags,
        key_signals=eval_result.key_signals,
        missing_information=eval_result.missing_information,
        explanation=eval_result.explanation,
        population_profile=eval_result.population_profile,
        policy_version="v2.0.0-prototype",
        model_version=eval_result.model_version,
        model_status=eval_result.model_status,
        model_available=eval_result.model_available,
        model_source=eval_result.model_source
    )
    db.add(triage_record)

    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=current_user.username,
        actor_role=current_user.role,
        event_type="deterioration_injected",
        patient_id=patient.patient_id,
        recommendation=eval_result.priority,
        confidence=eval_result.confidence_score,
        decision="REASSESS",
        override_reason=None,
        details={"injected_vitals": {"hr": hr, "spo2": spo2, "sbp": sbp, "rr": rr}, "risk_score": eval_result.risk_score},
        policy_version="v2.0.0-prototype",
        model_version="ml-baseline-v1"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "patient_id": patient.patient_id,
        "new_priority": eval_result.priority,
        "needs_reassessment": True,
        "reasons": patient.reassessment_reasons
    }

@router.post("/reset")
def reset_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    """Resets database and re-seeds 24 test cases and demo users."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_database(db)
    SIMULATION_STATE["surge_active"] = False
    SIMULATION_STATE["current_time_offset_minutes"] = 0
    return {"status": "success", "message": "Database reset and seeded with 24 test cases and default accounts."}
