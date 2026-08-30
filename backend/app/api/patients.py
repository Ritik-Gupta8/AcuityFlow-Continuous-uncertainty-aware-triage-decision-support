"""
Patient Management API.
Endpoints for retrieving patient lists, patient details, and adding vitals.
"""

from typing import List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.entities import Patient, Observation, TriageResult, AuditEvent, User
from app.schemas.schemas import PatientOut, ObservationCreate, ObservationOut, TriageResultOut, PatientSymptomsUpdate
from app.policy.action_policy import evaluate_patient_triage
from app.reassessment.monitor import reassessment_monitor

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=List[PatientOut])
def list_patients(
    surge: bool = Query(False, description="Sort attention-first for 3x surge mode"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    patients = db.query(Patient).all()
    
    # Calculate attention scores for sorting
    def get_sort_key(p: Patient):
        _, _, attention_score = reassessment_monitor.evaluate_patient_reassessment(p)
        return attention_score

    if surge:
        # In surge mode: high attention score first, deteriorating first
        patients.sort(key=get_sort_key, reverse=True)
    else:
        # Standard ED ordering: arrival order / severity
        priority_order = {"IMMEDIATE": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3, "REVIEW": 4}
        patients.sort(key=lambda p: (priority_order.get(p.current_priority, 5), -p.waiting_minutes))

    return patients

@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/{patient_id}/observations", response_model=ObservationOut)
def add_patient_observation(
    patient_id: str,
    obs_in: ObservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_obs = Observation(
        observation_id=f"OBS-{uuid.uuid4().hex[:8]}",
        patient_id=patient_id,
        timestamp=datetime.now(timezone.utc),
        heart_rate=obs_in.heart_rate,
        respiratory_rate=obs_in.respiratory_rate,
        systolic_bp=obs_in.systolic_bp,
        diastolic_bp=obs_in.diastolic_bp,
        spo2=obs_in.spo2,
        temperature_c=obs_in.temperature_c,
        measurement_source=obs_in.measurement_source,
        observation_notes=obs_in.observation_notes
    )
    db.add(new_obs)
    db.flush()

    # Re-evaluate triage recommendation
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

    # Re-evaluate continuous reassessment monitor
    needs_reassess, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    patient.needs_reassessment = needs_reassess
    patient.reassessment_reasons = reasons

    # Store Triage Result
    triage_record = TriageResult(
        result_id=f"TR-{uuid.uuid4().hex[:8]}",
        patient_id=patient_id,
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

    # Log Audit Event with authenticated user identity
    audit = AuditEvent(
        audit_id=f"AUD-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=current_user.username,
        actor_role=current_user.role,
        event_type="observation_update",
        patient_id=patient_id,
        recommendation=eval_result.priority,
        confidence=eval_result.confidence_score,
        decision=eval_result.action,
        override_reason=None,
        details={"reassessment_triggered": needs_reassess, "reasons": reasons, "risk_score": eval_result.risk_score},
        policy_version="v2.0.0-prototype",
        model_version="ml-baseline-v1"
    )
    db.add(audit)
    db.commit()

    return new_obs

@router.get("/{patient_id}/triage-latest", response_model=TriageResultOut)
def get_latest_triage_result(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    result = db.query(TriageResult).filter(TriageResult.patient_id == patient_id).order_by(TriageResult.timestamp.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="No triage result found for patient")
    return result

@router.post("/{patient_id}/symptoms", response_model=PatientOut)
def update_patient_symptoms(
    patient_id: str,
    payload: PatientSymptomsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["nurse", "supervisor", "admin"]))
):
    """
    Updates patient clinical cues with confirmed extracted symptoms.
    Feeds validated structured data directly into existing deterministic & ML triage pipeline.
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient.observed_cues = payload.symptoms
    if payload.narrative_text is not None:
        patient.symptom_text = payload.narrative_text
    if payload.duration_minutes is not None:
        patient.symptom_duration_minutes = payload.duration_minutes

    latest_obs = db.query(Observation).filter(Observation.patient_id == patient_id).order_by(Observation.timestamp.desc()).first()

    # Re-evaluate triage recommendation with confirmed structured symptoms
    eval_result = evaluate_patient_triage(patient, latest_obs)
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

    # Re-evaluate continuous reassessment monitor
    needs_reassess, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    patient.needs_reassessment = needs_reassess
    patient.reassessment_reasons = reasons

    triage_record = TriageResult(
        result_id=f"TR-{uuid.uuid4().hex[:8]}",
        patient_id=patient_id,
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
        event_type="structured_symptoms_confirmed",
        patient_id=patient_id,
        recommendation=eval_result.priority,
        confidence=eval_result.confidence_score,
        decision=eval_result.action,
        override_reason=None,
        details={"confirmed_symptoms": payload.symptoms, "duration_minutes": payload.duration_minutes, "risk_score": eval_result.risk_score},
        policy_version="v2.0.0-prototype",
        model_version="ml-baseline-v1"
    )
    db.add(audit)
    db.commit()
    db.refresh(patient)
    return patient
