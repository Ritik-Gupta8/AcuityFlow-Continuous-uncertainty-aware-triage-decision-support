"""
Pydantic schemas for request and response validation.
Aligned with docs/DATA_SCHEMA.md.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# --- Observation Schemas ---
class ObservationBase(BaseModel):
    heart_rate: Optional[float] = Field(None, description="Heart rate in bpm")
    respiratory_rate: Optional[float] = Field(None, description="Respiratory rate in breaths/min")
    systolic_bp: Optional[float] = Field(None, description="Systolic blood pressure in mmHg")
    diastolic_bp: Optional[float] = Field(None, description="Diastolic blood pressure in mmHg")
    spo2: Optional[float] = Field(None, description="Oxygen saturation in %")
    temperature_c: Optional[float] = Field(None, description="Temperature in Celsius")
    measurement_source: str = Field("device", description="device | clinician | self_reported")
    observation_notes: Optional[str] = None

class ObservationCreate(ObservationBase):
    pass

class ObservationOut(ObservationBase):
    observation_id: str
    patient_id: str
    timestamp: datetime

    class Config:
        from_attributes = True

# --- Patient Schemas ---
class PatientBase(BaseModel):
    patient_id: str
    name: str
    age_years: Optional[int] = None
    population_profile: str = "adult"  # pediatric | adult | geriatric
    sex: Optional[str] = None
    arrival_mode: str = "walk_in"  # walk_in | ambulance | referral | other
    first_time_patient: bool = False
    history_available: bool = True
    known_conditions: List[str] = []
    
    chief_complaint: str
    symptom_text: Optional[str] = None
    symptom_duration_minutes: Optional[int] = None
    pain_score: Optional[float] = None
    observed_cues: List[str] = []

class PatientCreate(PatientBase):
    initial_observations: Optional[ObservationCreate] = None

class PatientOut(PatientBase):
    arrival_time: datetime
    waiting_minutes: int
    current_status: str
    current_priority: str
    current_action: str
    current_confidence: float
    current_risk_score: float
    needs_reassessment: bool
    reassessment_reasons: List[str] = []
    observations: List[ObservationOut] = []

    class Config:
        from_attributes = True

# --- Triage Result Schemas ---
class TriageResultOut(BaseModel):
    result_id: str
    patient_id: str
    timestamp: datetime
    risk_score: float
    confidence_score: float
    data_completeness: float
    priority: str  # IMMEDIATE | HIGH | MODERATE | LOW | REVIEW
    action: str    # RECOMMEND | REASSESS | ESCALATE | ABSTAIN
    safety_flags: List[str]
    key_signals: List[str]
    missing_information: List[str]
    explanation: Optional[str]
    population_profile: str
    policy_version: str
    model_version: str
    disclaimer: str = "Synthetic / illustrative policy — not for clinical diagnosis or treatment."

    class Config:
        from_attributes = True

# --- Clinician Decision & Override Schemas ---
class ClinicianDecisionCreate(BaseModel):
    clinician_id: str = "nurse-101"
    actor_role: str = "nurse"  # nurse | supervisor | admin
    clinician_action: str  # accept | override | escalate
    final_priority: str    # IMMEDIATE | HIGH | MODERATE | LOW | REVIEW
    override_reason: Optional[str] = None
    clinician_note: Optional[str] = None

class ClinicianDecisionOut(BaseModel):
    decision_id: str
    patient_id: str
    clinician_id: str
    actor_role: str
    ai_priority: str
    ai_confidence: Optional[float]
    clinician_action: str
    final_priority: str
    override_reason: Optional[str]
    clinician_note: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

# --- Audit Event Schemas ---
class AuditEventOut(BaseModel):
    audit_id: str
    timestamp: datetime
    actor_id: str
    actor_role: str
    event_type: str
    patient_id: Optional[str]
    recommendation: Optional[str]
    confidence: Optional[float]
    decision: Optional[str]
    override_reason: Optional[str]
    details: Dict[str, Any] = {}
    policy_version: str
    model_version: str

    class Config:
        from_attributes = True

# --- Simulation & Reassessment Schemas ---
class AdvanceTimeRequest(BaseModel):
    minutes: int = 10

class SurgeToggleRequest(BaseModel):
    surge_active: bool

class InjectVitalsRequest(BaseModel):
    patient_id: str
    heart_rate: Optional[float] = None
    respiratory_rate: Optional[float] = None
    systolic_bp: Optional[float] = None
    spo2: Optional[float] = None
    temperature_c: Optional[float] = None
    notes: Optional[str] = "Simulated deterioration injection"
