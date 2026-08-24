# Source of Truth and Evidence Register

## 1. Primary product source

### Accenture Innovation Challenge 2026 — Problem 2: PatientTriage.ai

The supplied Round-2 case is the highest-priority source for:
- required behaviors,
- minimum prototype expectations,
- challenge framing,
- problem constraints.

No external article can override the challenge requirements.

## 2. Standards

### HL7 FHIR R4 — Observation

FHIR Observation represents measurements and simple assertions about a patient. citeturn802599search3

Use this as conceptual grounding for observation data.

### HL7 FHIR R4 — AuditEvent

FHIR AuditEvent is a record for security/audit-relevant events and includes event timing, outcome, source and entities involved. citeturn802599search0turn802599search5

Use it as conceptual grounding for the audit trail.

## 3. Clinical decision support design

### FDA Clinical Decision Support Guidance

FDA guidance states that CDS intended to support healthcare professionals should enable independent review of the basis for recommendations and should communicate relevant patient-specific information, inputs, methods and known/unknown limitations. citeturn802599search36

We use this as design guidance, not as a declaration that the prototype is FDA-regulated or cleared.

## 4. India privacy context

### MeitY — Digital Personal Data Protection Act 2023

Official Gazette publication confirms the Act and its purpose around processing digital personal data. citeturn354030search15

### MeitY — Digital Personal Data Protection Rules 2025

MeitY published the final Rules in November 2025 and an enforcement timeline. citeturn354030search0turn354030search14

Use these only for high-level privacy architecture; obtain legal review for deployment.

## 5. Google Cloud / Gemini

### Vertex AI documentation

Google documents Gemini use through Vertex AI, including the Gen AI SDK, enterprise controls and multiple model families. citeturn385348search1turn385348search5

### Vertex AI pricing

Google publishes model-specific pricing; pricing changes over time, so the implementation should not hard-code cost assumptions into the product. citeturn385348search0

## 6. Cloud Run

Cloud Run can scale to zero by default and is billed based on usage; maximum instances can be configured for cost control. citeturn398916search0turn398916search7

## 7. Billing guardrail

Google Cloud budgets can trigger alerts, but alert-only budgets do not automatically cap spending. Use them together with service limits/max-instance controls and manual shutdown discipline. citeturn398916search3turn398916search7

## 8. Evidence rule

Every material claim in:
- README,
- UI,
- demo video,
- pitch deck,

must be one of:

### CASE
Directly required or stated by the Accenture case.

### VERIFIED
Supported by an official or peer-reviewed source linked here.

### MEASURED
Computed by our own running prototype and stored in evaluation output.

### ASSUMED
A clearly labeled project assumption.

### SYNTHETIC
Generated only for demonstration/testing.

If a claim does not fit one of these categories, remove it or mark it as unknown.
