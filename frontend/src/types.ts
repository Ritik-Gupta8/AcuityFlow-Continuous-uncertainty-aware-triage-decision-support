export interface Observation {
  observation_id: string;
  patient_id: string;
  timestamp: string;
  heart_rate: number | null;
  respiratory_rate: number | null;
  systolic_bp: number | null;
  diastolic_bp: number | null;
  spo2: number | null;
  temperature_c: number | null;
  measurement_source: string;
  observation_notes?: string | null;
}

export interface Patient {
  patient_id: string;
  name: string;
  age_years: number | null;
  population_profile: 'pediatric' | 'adult' | 'geriatric';
  sex: string | null;
  arrival_mode: string;
  first_time_patient: boolean;
  history_available: boolean;
  known_conditions: string[];
  chief_complaint: string;
  symptom_text?: string | null;
  symptom_duration_minutes?: number | null;
  pain_score?: number | null;
  observed_cues: string[];
  arrival_time: string;
  waiting_minutes: number;
  current_status: string;

  // 1. AI Recommendation State (Immutable from Triage Model)
  ai_priority?: 'IMMEDIATE' | 'HIGH' | 'MODERATE' | 'LOW' | 'REVIEW';
  ai_workflow_action?: 'RECOMMEND' | 'REASSESS' | 'ESCALATE' | 'ABSTAIN';
  ai_confidence?: number;
  ai_risk_score?: number;

  // 2. Clinician Decision & Override State (Separate from AI)
  clinician_decision?: 'IMMEDIATE' | 'HIGH' | 'MODERATE' | 'LOW' | 'REVIEW' | null;
  clinician_action?: 'accept' | 'override' | 'escalate' | null;
  override_reason?: string | null;

  // 3. Operational Effective Priority & Workflow State
  effective_priority?: 'IMMEDIATE' | 'HIGH' | 'MODERATE' | 'LOW' | 'REVIEW';
  reassessment_state?: string;

  current_priority: 'IMMEDIATE' | 'HIGH' | 'MODERATE' | 'LOW' | 'REVIEW';
  current_action: 'RECOMMEND' | 'REASSESS' | 'ESCALATE' | 'ABSTAIN';
  current_confidence: number;
  current_risk_score: number;
  needs_reassessment: boolean;
  reassessment_reasons: string[];
  observations: Observation[];
}

export interface TriageResult {
  result_id: string;
  patient_id: string;
  timestamp: string;
  risk_score: number;
  confidence_score: number;
  data_completeness: number;
  priority: 'IMMEDIATE' | 'HIGH' | 'MODERATE' | 'LOW' | 'REVIEW';
  action: 'RECOMMEND' | 'REASSESS' | 'ESCALATE' | 'ABSTAIN';
  safety_flags: string[];
  key_signals: string[];
  missing_information: string[];
  explanation: string;
  population_profile: string;
  policy_version: string;
  model_version: string;
  disclaimer: string;
}

export interface ClinicianDecisionPayload {
  clinician_id: string;
  actor_role: string;
  clinician_action: 'accept' | 'override' | 'escalate';
  final_priority: 'IMMEDIATE' | 'HIGH' | 'MODERATE' | 'LOW' | 'REVIEW';
  override_reason?: string;
  clinician_note?: string;
}

export interface AuditEvent {
  audit_id: string;
  timestamp: string;
  actor_id: string;
  actor_role: string;
  event_type: string;
  patient_id?: string | null;
  recommendation?: string | null;
  confidence?: number | null;
  decision?: string | null;
  override_reason?: string | null;
  details: Record<string, any>;
  policy_version: string;
  model_version: string;
}

export interface SimulationStatus {
  surge_active: boolean;
  time_offset_minutes: number;
  disclaimer: string;
}

export interface SymptomExtractionResult {
  symptoms: string[];
  duration_minutes?: number | null;
  extracted_by: string;
  is_ambiguous: boolean;
}

