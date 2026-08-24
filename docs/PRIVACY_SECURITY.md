# Privacy and Security — Prototype

## 1. Jurisdiction assumption

For the prototype, assume **India** as the demonstration jurisdiction.

The project should reference:
- Digital Personal Data Protection Act, 2023,
- Digital Personal Data Protection Rules, 2025,

but must not claim that this student prototype is legally compliant.

MeitY published the 2025 Rules and an enforcement timeline in November 2025; different provisions have different commencement timelines. Production deployment therefore requires a current legal review rather than copying a generic "DPDP compliant" badge. citeturn354030search0turn354030search14

## 2. Data minimization

For the prototype:
- use synthetic patients,
- collect only fields required for the demo,
- do not collect real identifiers,
- do not persist real clinical records.

## 3. Access control

Roles:

### Nurse
- view queue,
- view assigned patient,
- submit triage decision,
- override recommendation.

### Supervisor
- all nurse capabilities,
- audit/override review,
- queue monitoring.

### Admin
- hospital profile configuration,
- policy version management,
- user/role management.

## 4. Security controls to demonstrate

- authenticated sessions,
- role-based authorization,
- server-side authorization checks,
- parameter validation,
- input sanitization,
- secrets in environment variables,
- HTTPS in deployment,
- audit logging,
- least-privilege database access.

## 5. Audit

Log:
- login/logout,
- patient view,
- triage request,
- recommendation,
- reassessment alert,
- override,
- configuration change,
- access denial.

FHIR's AuditEvent resource is explicitly intended for security/audit logging and includes event type, time, outcome, source and involved entities. citeturn802599search0turn802599search5

## 6. Retention

For the prototype:
- keep synthetic audit records for the demo,
- define retention as a configurable policy,
- do not claim a legal retention period unless validated for the deployment jurisdiction.

## 7. AI data handling

If Gemini/Vertex AI is used:
- send only the minimum synthetic text needed,
- never send real patient data,
- keep the prompt constrained to the required task,
- never ask the model for diagnosis/treatment.

Vertex AI provides enterprise security/privacy features, but the prototype still must avoid real sensitive patient data. citeturn385348search5

## 8. Privacy UI

Add a small "Data Protection" panel showing:

```text
✓ Synthetic/de-identified prototype data
✓ Role-based access
✓ Auditable clinical actions
✓ Minimal-data principle
✓ No autonomous clinical decision
```

Do not label this panel "DPDP compliant".
