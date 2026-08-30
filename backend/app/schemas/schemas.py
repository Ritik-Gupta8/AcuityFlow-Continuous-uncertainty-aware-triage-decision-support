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
    
    # Explicit Domain Model Fields
    ai_priority: str = "MODERATE"
    ai_workflow_action: str = "RECOMMEND"
    ai_confidence: float = 75.0
    ai_risk_score: float = 30.0
    
    clinician_decision: Optional[str] = None
    clinician_action: Optional[str] = None
    override_reason: Optional[str] = None
    
    effective_priority: str = "MODERATE"
    reassessment_state: str = "NORMAL"

    current_priority: str
    current_action: str
    current_confidence: float
    current_risk_score: float
    needs_reassessment: bool
    reassessment_reasons: List[str] = []
    observations: List[ObservationOut] = []

    class Config:
        from_attributes = True

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
    model_status: str = "CALIBRATED_ML"
    model_available: bool = True
    model_source: str = "calibrated_model"
    disclaimer: str = "Synthetic / illustrative policy — not for clinical diagnosis or treatment."

    class Config:
        from_attributes = True

# --- Authentication & User Schemas ---
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str

class UserOut(BaseModel):
    user_id: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field("nurse", pattern="^(nurse|supervisor|admin)$")

# --- Clinician Decision & Override Schemas ---
class ClinicianDecisionCreate(BaseModel):
    clinician_id: Optional[str] = None  # Ignored in favor of authenticated user token
    actor_role: Optional[str] = None    # Ignored in favor of authenticated user token
    clinician_action: str               # accept | override | escalate
    final_priority: str                 # IMMEDIATE | HIGH | MODERATE | LOW | REVIEW
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

# --- Admin Configuration Schemas ---
class AdminConfigOut(BaseModel):
    project_name: str
    version: str
    pediatric_max_age: int
    geriatric_min_age: int
    min_confidence_threshold: float
    min_completeness_threshold: float
    disclaimer: str

class AdminConfigUpdate(BaseModel):
    pediatric_max_age: Optional[int] = Field(None, ge=1, le=25)
    geriatric_min_age: Optional[int] = Field(None, ge=50, le=100)

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
    minutes: int = Field(15, ge=1, le=120)

class SurgeToggleRequest(BaseModel):
    surge_active: bool

class SimulationStatus(BaseModel):
    surge_active: bool
    time_offset_minutes: int
    model_status: str = "CALIBRATED_ML"
    model_available: bool = True
    model_source: str = "calibrated_model"
    disclaimer: str = "Synthetic simulation environment for decision support validation."

SimulationAdvanceTime = AdvanceTimeRequest
SimulationSurgeToggle = SurgeToggleRequest

# --- NLP Symptom Extraction Schemas ---
class SymptomExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Raw narrative presentation text")

class SymptomExtractionResponse(BaseModel):
    symptoms: List[str]
    duration_minutes: Optional[int] = None
    extracted_by: str = "local-rule-parser"
    is_ambiguous: bool = False

class PatientSymptomsUpdate(BaseModel):
    symptoms: List[str]
    narrative_text: Optional[str] = None
    duration_minutes: Optional[int] = None

class InjectVitalsRequest(BaseModel):
    patient_id: str
    heart_rate: Optional[float] = None
    respiratory_rate: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    spo2: Optional[float] = None
    temperature_c: Optional[float] = None
    notes: Optional[str] = "Simulated deterioration injection"
