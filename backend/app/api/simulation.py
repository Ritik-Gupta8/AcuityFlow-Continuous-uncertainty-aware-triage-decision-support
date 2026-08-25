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
from app.models.entities import Patient, Observation, AuditEvent
from app.schemas.schemas import AdvanceTimeRequest, SurgeToggleRequest, InjectVitalsRequest
from app.reassessment.monitor import reassessment_monitor
from app.policy.action_policy import evaluate_patient_triage
from app.data.seed_cases import seed_database

router = APIRouter(prefix="/simulation", tags=["Simulation Controls"])

# In-memory surge state
SIMULATION_STATE = {
    "surge_active": False,
    "current_time_offset_minutes": 0,
}

@router.get("/status")
def get_simulation_status():
    return {
        "surge_active": SIMULATION_STATE["surge_active"],
        "time_offset_minutes": SIMULATION_STATE["current_time_offset_minutes"],
        "disclaimer": "Simulated Environment • Synthetic Data"
    }

@router.post("/advance-time")
def advance_simulated_time(req: AdvanceTimeRequest, db: Session = Depends(get_db)):
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
        details={
            "minutes_advanced": req.minutes,
            "total_offset": SIMULATION_STATE["current_time_offset_minutes"],
            "patients_affected": updated_count,
            "reassessments_triggered": reassessment_triggered
        }
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
def toggle_surge_mode(req: SurgeToggleRequest, db: Session = Depends(get_db)):
    """Toggles 3x surge mode status."""
    SIMULATION_STATE["surge_active"] = req.surge_active
    
    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id="supervisor-201",
        actor_role="supervisor",
        event_type="surge_toggle",
        details={"surge_active": req.surge_active, "multiplier": 3.0 if req.surge_active else 1.0}
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "surge_active": req.surge_active,
        "message": "3x Surge mode activated: attention queue prioritized" if req.surge_active else "Standard queue mode restored"
    }

@router.post("/inject-deterioration")
def inject_deterioration_vitals(req: InjectVitalsRequest, db: Session = Depends(get_db)):
    """Injects deteriorating vital signs into a patient (e.g. PT-021) to demo continuous re-triage."""
    patient = db.query(Patient).filter(Patient.patient_id == req.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # If vitals aren't specified, apply a preset deterioration
    hr = req.heart_rate or 122.0
    rr = req.respiratory_rate or 28.0
    sbp = req.systolic_bp or 94.0
    spo2 = req.spo2 or 89.0
    temp = req.temperature_c or 37.9

    new_obs = Observation(
        observation_id=f"OBS-{uuid.uuid4().hex[:8]}",
        patient_id=patient.patient_id,
        timestamp=datetime.now(timezone.utc),
        heart_rate=hr,
        respiratory_rate=rr,
        systolic_bp=sbp,
        diastolic_bp=60.0,
        spo2=spo2,
        temperature_c=temp,
        measurement_source="device",
        observation_notes=req.notes or "Simulated deterioration injection"
    )
    db.add(new_obs)
    db.flush()

    # Re-evaluate triage and reassessment
    eval_result = evaluate_patient_triage(patient, new_obs)
    patient.current_priority = eval_result.priority
    patient.current_action = eval_result.action
    patient.current_confidence = eval_result.confidence_score
    patient.current_risk_score = eval_result.risk_score

    needs_reassess, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    patient.needs_reassessment = True  # Explicitly flag deterioration
    patient.reassessment_reasons = reasons if reasons else ["Deteriorating vital signs detected"]

    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id="simulation-engine",
        actor_role="system",
        event_type="deterioration_injected",
        patient_id=patient.patient_id,
        recommendation=eval_result.priority,
        confidence=eval_result.confidence_score,
        decision="REASSESS",
        details={"injected_vitals": {"hr": hr, "spo2": spo2, "sbp": sbp}}
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
def reset_database(db: Session = Depends(get_db)):
    """Resets database and re-seeds 24 test cases."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_database(db)
    SIMULATION_STATE["surge_active"] = False
    SIMULATION_STATE["current_time_offset_minutes"] = 0
    return {"status": "success", "message": "Database reset and reseeded with 24 test cases."}
