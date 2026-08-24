# Implementation Plan

## Phase 0 — Freeze the product contract

Read:
- PRODUCT_SPEC.md
- TRIAGE_POLICY.md
- SAFETY_UNCERTAINTY.md
- DATA_SCHEMA.md
- TEST_CASES.md
- SOURCE_OF_TRUTH.md

Do not code new features until the agent confirms it understands these documents.

## Phase 1 — Backend policy engine

Build:
- schemas,
- validation,
- completeness calculation,
- population-profile resolver,
- deterministic safety policy,
- risk-band policy,
- action policy,
- audit events.

## Phase 2 — Synthetic dataset

Create:
- 24+ cases,
- repeated-observation timelines,
- 3× surge scenario,
- required special cases.

## Phase 3 — ML baseline

Build:
- baseline logistic regression,
- XGBoost comparison,
- evaluation script,
- model artifact,
- SHAP explanation if model retained.

Keep model inputs limited to information available at triage.

## Phase 4 — Reassessment engine

Implement:
- observation comparison,
- wait-time trigger,
- risk-trajectory trigger,
- uncertainty trigger,
- event creation.

## Phase 5 — API

Suggested endpoints:

```text
GET    /health
GET    /patients
GET    /patients/{id}
POST   /triage
POST   /patients/{id}/observations
POST   /patients/{id}/reassess
POST   /patients/{id}/override
GET    /patients/{id}/audit
POST   /simulation/surge
POST   /simulation/advance-time
```

## Phase 6 — Frontend

Build:
- command center,
- patient detail,
- triage card,
- explanation,
- uncertainty,
- reassessment alert,
- override modal,
- audit trail,
- surge mode.

## Phase 7 — Optional Gemini

Only after deterministic behavior works.

Use Gemini for:
- free-text extraction,
- explanation generation.

Add fallback behavior:

```text
Gemini unavailable
    ↓
deterministic template explanation
```

The product must still function.

## Phase 8 — Deployment

Preferred:
- Docker
- Cloud Run
- frontend deployed separately or served by backend

Use max-instance controls and request-based billing where appropriate. citeturn398916search0turn398916search7

## Phase 9 — Verification

Run:
- unit tests,
- policy tests,
- scenario tests,
- surge test,
- override test,
- authorization test,
- audit test.

## Phase 10 — Submission assets

Prepare:
- README,
- architecture diagram,
- demo video,
- 20+ case summary,
- evaluation output,
- limitations,
- deployment instructions,
- public repository.
