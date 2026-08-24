# Google Cloud Credit Strategy

## 1. Project-owner screenshot snapshot

The supplied Google Cloud billing screenshot shows:

- Free Trial: approximately **₹28,316.24 remaining** at the time of the screenshot.
- Original Free Trial value: approximately **₹28,320.75**.
- Free Trial end date shown: **October 9, 2026**.
- Multiple "Google Developer Program premium benefit" credit entries of approximately **₹944.03** each with later expiry dates.

These values are a snapshot of the account and can change. Verify in the console before making a paid deployment.

## 2. What to spend credits on

### Priority 1 — Vertex AI / Gemini

Use for:
- symptom text structuring,
- concise explanation generation,
- optional ambiguity summarization.

Do not use it for:
- unrestricted triage decisions,
- large-volume synthetic-data generation,
- unnecessary repeated prompts.

Google documents Gemini through Vertex AI, and model pricing is usage-based. citeturn385348search1turn385348search0

### Priority 2 — Cloud Run

Use Cloud Run for:
- the FastAPI backend,
- optionally a small frontend/backend container.

Cloud Run scales to zero by default and supports max-instance controls. citeturn398916search0turn398916search7

### Priority 3 — Cloud Storage (optional)

Use only if a concrete artifact-storage need appears.

## 3. Avoid spending credits on

- GKE/Kubernetes,
- always-on Compute Engine VMs,
- large Cloud SQL instances,
- BigQuery unless an actual analytical feature needs it,
- multiple duplicate environments,
- image/video generation,
- excessive LLM calls.

## 4. Recommended data storage

Use:
- local PostgreSQL or Supabase for development,
- optionally a small managed PostgreSQL deployment only if cloud architecture materially improves the demo.

Do not move the project to a managed database just to use credits.

## 5. Cost-control configuration

For Cloud Run:
- request-based billing,
- minimum instances = 0 unless there is a proven latency requirement,
- conservative maximum instances.

Cloud Run's default scale-to-zero behavior and request-based billing are appropriate for a short-lived prototype demo. citeturn398916search0turn398916search6

## 6. Budget

Create a billing budget and alert thresholds.

Important:
- a budget alert is not automatically a spending cap,
- keep a manual shutdown checklist,
- inspect billing after major test sessions.

Google explicitly notes that alerts-only budgets do not automatically prevent additional usage. citeturn398916search3

## 7. Cost principle

> Spend cloud credits where the judge can see a meaningful product capability.

Good:
- "This explanation is produced by Vertex AI from structured model outputs."

Bad:
- "We use six Google Cloud services because we can."
