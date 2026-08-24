# AGENTS.md — AcuityFlow Round 2 Build Contract

This file is the **non-negotiable instruction set** for Codex, Antigravity, Kiro, Cursor or any other coding agent working on AcuityFlow.

## 1. Mission

Implement the product described in `docs/PRODUCT_SPEC.md` and the policy described in `docs/TRIAGE_POLICY.md`.

Do not redesign the problem unless the human owner explicitly asks.

## 2. Source-of-truth hierarchy

When sources conflict, follow this order:

1. The official Accenture Round 2 case supplied by the project owner.
2. `docs/PRODUCT_SPEC.md`
3. `docs/TRIAGE_POLICY.md`
4. `docs/SAFETY_UNCERTAINTY.md`
5. `docs/DATA_SCHEMA.md`
6. Official standards/docs linked in `docs/SOURCE_OF_TRUTH.md`
7. Peer-reviewed evidence referenced in `docs/SOURCE_OF_TRUTH.md`
8. General model knowledge

A lower-ranked source must never silently override a higher-ranked source.

## 3. Anti-hallucination rules

### Clinical thresholds
Never invent a clinical threshold and present it as medical truth.

If a threshold is not explicitly present in the case, an approved source, or a project configuration entry:

- do not hard-code it as a clinical fact;
- implement it as a clearly labeled **illustrative prototype rule**;
- put it in configuration;
- show the prototype disclaimer;
- add `TODO: CLINICAL VALIDATION REQUIRED`.

### Model performance
Never invent accuracy, AUROC, sensitivity, specificity, calibration, latency, cost savings or clinical impact.

Only show metrics that were actually computed by the evaluation scripts.

### Patient outcomes
Never claim the system prevents death, guarantees safety, reduces waiting time by a specific amount, or improves clinical outcomes unless the number comes from an actual experiment and is labeled as simulated prototype evidence.

### Regulation
Never claim the prototype is HIPAA compliant, DPDP compliant, MDR/FDA cleared, or production-ready.

Use language such as:
- "prototype privacy controls",
- "designed for auditability",
- "production deployment would require legal, security and clinical validation."

### Medical language
Use:
- triage recommendation,
- urgency/priority recommendation,
- risk signal,
- reassessment recommendation,
- decision support,
- clinician review.

Avoid:
- diagnosis,
- treatment decision,
- autonomous clinical decision,
- replaces nurse/doctor.

## 4. LLM rules

Gemini or another LLM may be used for:

- free-text symptom extraction,
- normalization,
- summarization,
- explanation drafting.

LLM output must NOT be the sole authority for:
- triage priority,
- emergency severity,
- escalation,
- clinician override logging.

Structured rules and the risk engine own those decisions.

## 5. Safety rule

When uncertainty increases, behavior must become **more conservative**, not less.

The system may:
- escalate,
- request more information,
- abstain,
- require human review.

It must not "guess low" simply because information is missing.

## 6. Time-of-intake rule

Only use inputs that would realistically be available at the time the recommendation is made.

Do not use downstream outcomes such as:
- final diagnosis,
- ICU admission,
- discharge disposition,
- later laboratory results,
- treatment response,

as inputs to initial triage.

## 7. Population rule

Do not use one universal adult-style scoring function without a population profile.

Every patient must resolve to one of:
- pediatric,
- adult,
- geriatric,

using a configuration-driven population policy.

The exact demographic boundaries are **prototype assumptions**, not universal clinical truth.

## 8. Human authority

Every actionable recommendation must expose:
- recommendation,
- confidence,
- key contributing inputs,
- data-quality status,
- action reason.

The clinician can:
- accept,
- override,
- escalate.

Every override is logged with timestamp, user role, old recommendation, new decision and reason.

## 9. Data rules

Use synthetic data only.

Do not add:
- real names,
- phone numbers,
- addresses,
- real medical-record identifiers,
- real patient photographs,
- copied identifiable clinical notes.

## 10. Architecture discipline

Prefer a modular monolith over microservices.

Do not add a dependency unless:
- it solves a demonstrated need,
- it reduces complexity,
- or it is required by the case.

## 11. Cost discipline

Google Cloud credits are limited.

Use cloud only where it materially strengthens the prototype:
- Vertex AI for bounded Gemini calls,
- Cloud Run for a realistic hosted backend if useful.

Avoid:
- always-on VMs,
- GKE/Kubernetes,
- idle database clusters,
- unnecessary managed services.

Set a billing budget/alert and cap service instances where supported.

## 12. Definition of done

A feature is not done because it exists.

It is done only when:
- it is reachable from the UI,
- it works with test data,
- it has a meaningful test,
- it has a clear failure behavior,
- it respects these rules,
- it does not create unsupported clinical claims.

## 13. Final agent behavior

Before writing code, inspect:
- `README.md`
- `docs/PRODUCT_SPEC.md`
- `docs/TRIAGE_POLICY.md`
- `docs/SAFETY_UNCERTAINTY.md`
- `docs/DATA_SCHEMA.md`
- `docs/TEST_CASES.md`

If a required decision is missing, stop and ask the human owner rather than inventing one.
