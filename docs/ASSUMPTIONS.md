# Assumptions Register

This file prevents assumptions from turning into hidden "facts".

## A1 — Jurisdiction

Assumption:
- India is the prototype demonstration jurisdiction.

Reason:
- project team is based in India.

Implication:
- use privacy language aligned with DPDP context,
- do not claim legal compliance.

Status:
- ASSUMED; legal review required for deployment.

## A2 — Data

Assumption:
- all prototype patient data is synthetic.

Status:
- REQUIRED.

## A3 — Triage scale

Assumption:
- use a five-band output for demonstration:
  IMMEDIATE / HIGH / MODERATE / LOW / REVIEW.

Status:
- SYNTHETIC PROTOTYPE CHOICE.

## A4 — Population groups

Assumption:
- pediatric / adult / geriatric profiles.

Exact boundaries:
- configurable,
- not presented as universal clinical definitions.

## A5 — Confidence

Assumption:
- confidence is a composite workflow signal based on model certainty, data completeness and consistency.

Status:
- PROTOTYPE DESIGN.

## A6 — Surge

Assumption:
- 3× surge is represented by multiplying simulated incoming volume by 3.

Status:
- PROTOTYPE SIMULATION.

## A7 — Wait-time policy

Assumption:
- reassessment windows are configured per priority profile.

Do not hard-code medical time limits from general knowledge.

Status:
- CONFIGURABLE / CLINICAL VALIDATION REQUIRED.

## A8 — Hospital profiles

Assumption:
- one core engine with configurable:
  - daily volume,
  - staffing,
  - departments,
  - population mix,
  - escalation policy.

Status:
- PRODUCT DESIGN.

## A9 — Gemini

Assumption:
- Gemini is useful for extracting and explaining language, not owning the final triage decision.

Status:
- ARCHITECTURAL DECISION.

## A10 — Cloud

Assumption:
- use Google Cloud only where it strengthens the demo.

Status:
- COST CONTROL.

## Rule

Any new assumption must be added here before it is implemented.
