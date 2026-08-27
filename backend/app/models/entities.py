"""
SQLAlchemy models for AcuityFlow AI.
Aligned with docs/DATA_SCHEMA.md.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Synthetic fictional name
    age_years = Column(Integer, nullable=True)
    population_profile = Column(String, nullable=False, default="adult")  # pediatric, adult, geriatric
    sex = Column(String, nullable=True)
    arrival_mode = Column(String, default="walk_in")  # walk_in, ambulance, referral, other
    first_time_patient = Column(Boolean, default=False)
    history_available = Column(Boolean, default=True)
    known_conditions = Column(JSON, default=list)  # List of condition strings
    
    # Presentation
    chief_complaint = Column(String, nullable=False)
    symptom_text = Column(Text, nullable=True)
    symptom_duration_minutes = Column(Integer, nullable=True)
    pain_score = Column(Float, nullable=True)
    observed_cues = Column(JSON, default=list)  # E.g., ["cyanotic appearance", "diaphoretic"]
    
    # Waiting queue tracking
    arrival_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    waiting_minutes = Column(Integer, default=0)
    current_status = Column(String, default="WAITING")  # WAITING, ATTENDING, ADMITTED, DISCHARGED
    current_priority = Column(String, default="MODERATE")  # IMMEDIATE, HIGH, MODERATE, LOW, REVIEW
    current_action = Column(String, default="RECOMMEND")   # RECOMMEND, REASSESS, ESCALATE, ABSTAIN
    current_confidence = Column(Float, default=75.0)
    current_risk_score = Column(Float, default=30.0)
    
    # Flags
    needs_reassessment = Column(Boolean, default=False)
    reassessment_reasons = Column(JSON, default=list)
    
    # Relationships
    observations = relationship("Observation", back_populates="patient", cascade="all, delete-orphan", order_by="Observation.timestamp.desc()")
    triage_results = relationship("TriageResult", back_populates="patient", cascade="all, delete-orphan", order_by="TriageResult.timestamp.desc()")
    decisions = relationship("ClinicianDecision", back_populates="patient", cascade="all, delete-orphan", order_by="ClinicianDecision.timestamp.desc()")

class Observation(Base):
    __tablename__ = "observations"

    observation_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    heart_rate = Column(Float, nullable=True)
    respiratory_rate = Column(Float, nullable=True)
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    measurement_source = Column(String, default="device")  # device, clinician, self_reported
    observation_notes = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="observations")

class TriageResult(Base):
    __tablename__ = "triage_results"

    result_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    risk_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    data_completeness = Column(Float, nullable=False)
    priority = Column(String, nullable=False)  # IMMEDIATE, HIGH, MODERATE, LOW, REVIEW
    action = Column(String, nullable=False)    # RECOMMEND, REASSESS, ESCALATE, ABSTAIN
    
    safety_flags = Column(JSON, default=list)
    key_signals = Column(JSON, default=list)
    missing_information = Column(JSON, default=list)
    explanation = Column(Text, nullable=True)
    
    population_profile = Column(String, nullable=False)
    policy_version = Column(String, default="v2.0.0-prototype")
    model_version = Column(String, default="ml-baseline-v1")

    patient = relationship("Patient", back_populates="triage_results")

class ClinicianDecision(Base):
    __tablename__ = "clinician_decisions"

    decision_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False, index=True)
    clinician_id = Column(String, nullable=False)
    actor_role = Column(String, default="nurse")  # nurse, supervisor, admin
    
    ai_priority = Column(String, nullable=False)
    ai_confidence = Column(Float, nullable=True)
    clinician_action = Column(String, nullable=False)  # accept, override, escalate
    final_priority = Column(String, nullable=False)
    override_reason = Column(String, nullable=True)
    clinician_note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="decisions")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    audit_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    actor_id = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)  # nurse, supervisor, admin, system
    event_type = Column(String, nullable=False)  # login, patient_view, triage, reassessment, override, config_change, surge_toggle
    patient_id = Column(String, nullable=True, index=True)
    
    recommendation = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    decision = Column(String, nullable=True)
    override_reason = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    
    policy_version = Column(String, default="v2.0.0-prototype")
    model_version = Column(String, default="ml-baseline-v1")
