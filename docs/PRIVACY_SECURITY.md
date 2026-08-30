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

## 3. Role-Based Access Control (RBAC) Implementation

The prototype implements server-side backend-enforced RBAC using HS256 JWT access tokens and PBKDF2-HMAC-SHA256 password hashing.

### Authorization Workflow
```text
Authentication
  ↓ (POST /api/auth/login with valid password hash)
User Identity & Claims
  ↓ (sub: user_id, username, role)
Backend Role Resolution & Authorization
  ↓ (FastAPI get_current_user & require_role dependencies)
Allowed Action
  ↓ (HTTP 200/201 on permitted action, HTTP 403 on role denial, HTTP 401 on unauthenticated)
Authoritative Audit Event
  ↓ (actor_id & actor_role populated strictly from verified token, client body spoofing discarded)
```

### Supported Roles & Matrix

| Capability / Endpoint | Nurse (`nurse101`) | Supervisor (`supervisor101`) | Admin (`admin101`) |
|---|:---:|:---:|:---:|
| **Patient Queue & Detail** (`GET /api/patients`) | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Triage & Observations** (`POST /api/patients/{id}/obs`) | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Clinician Overrides** (`POST /api/patients/{id}/decision`) | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Patient Audit History** (`GET /api/audit?patient_id=...`) | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Full Audit Trail Explorer** (`GET /api/audit`) | ❌ Denied (403) | ✅ Allowed | ✅ Allowed |
| **Surge / Advance Time** (`POST /api/simulation/...`) | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| **Demographic Policy Config** (`GET/POST /api/admin/config`) | ❌ Denied (403) | ❌ Denied (403) | ✅ Allowed |
| **User Administration** (`GET/POST /api/admin/users`) | ❌ Denied (403) | ❌ Denied (403) | ✅ Allowed |

### Synthetic Demo Accounts (Default Password: `Password@123`)
- `nurse101`: Frontline Emergency Department Triage Nurse
- `supervisor101`: ED Charge Nurse / Triage Shift Supervisor
- `admin101`: Clinical Engineering & System Administrator

### Identity Spoofing Protection
Clinician identity (`actor_id`, `actor_role`) for overrides and observation updates is authoritatively resolved from the authenticated JWT session on the server. Client attempts to pass spoofed `clinician_id` or `actor_role` values in request bodies are discarded.

## 4. Security controls demonstrated

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
