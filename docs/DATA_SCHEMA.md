# Data Schema — Synthetic Prototype

## 1. Patient

```yaml
patient_id: string
age_years: integer | null
population_profile: pediatric | adult | geriatric
sex: string | null
arrival_mode: walk_in | ambulance | referral | other
first_time_patient: boolean
history_available: boolean
```

## 2. Presentation

```yaml
chief_complaint: string
symptom_text: string
symptom_duration_minutes: integer | null
pain_score: number | null
observed_cues: [string]
```

## 3. Observations

```yaml
timestamp: ISO-8601
heart_rate: number | null
respiratory_rate: number | null
systolic_bp: number | null
diastolic_bp: number | null
spo2: number | null
temperature_c: number | null
measurement_source: device | clinician | self_reported
```

## 4. Triage result

```yaml
risk_score: number
confidence_score: number
data_completeness: number
priority: IMMEDIATE | HIGH | MODERATE | LOW | REVIEW
action: RECOMMEND | REASSESS | ESCALATE | ABSTAIN
safety_flags: [string]
key_signals: [string]
missing_information: [string]
population_profile: string
policy_version: string
model_version: string
```

## 5. Human decision

```yaml
decision_id: string
patient_id: string
clinician_id: string
ai_priority: string
clinician_action: accept | override | escalate
override_reason: string | null
clinician_note: string | null
timestamp: ISO-8601
```

## 6. Reassessment event

```yaml
event_id: string
patient_id: string
trigger_type: vital_change | wait_time | risk_trajectory | uncertainty
previous_result: object
new_observation_id: string | null
recommended_action: REASSESS | ESCALATE
timestamp: ISO-8601
```

## 7. Audit event

FHIR R4 includes an `AuditEvent` resource intended for security/audit logging, including event type, recorded time, outcome, source and involved entities. This prototype uses a simplified internal structure inspired by those concepts rather than claiming full FHIR conformance. citeturn802599search0turn802599search5

```yaml
audit_id: string
timestamp: ISO-8601
actor_id: string
actor_role: nurse | supervisor | admin | system
event_type: login | patient_view | triage | reassessment | override | config_change
patient_id: string | null
recommendation: string | null
confidence: number | null
decision: string | null
override_reason: string | null
policy_version: string
model_version: string
```

## 8. FHIR-inspired mapping

| Prototype object | FHIR concept |
|---|---|
| Patient | Patient |
| Vitals / measurements | Observation |
| Risk result | RiskAssessment concept |
| Security/audit event | AuditEvent |
| Clinical encounter | Encounter |

FHIR `Observation` represents measurements and simple assertions about a patient, while `AuditEvent` records security/audit-relevant events. citeturn802599search3turn802599search5

## 9. Synthetic data rules

Every record must be:
- fictional,
- reproducible,
- clearly labeled synthetic,
- free of real identifying information.
