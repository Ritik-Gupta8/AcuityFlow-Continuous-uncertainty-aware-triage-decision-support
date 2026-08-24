# AcuityFlow AI — decision-support syste

## Purpose

AcuityFlow AI is a **prototype decision-support system**.

The prototype helps emergency-department staff:

1. structure incomplete intake information,
2. produce a triage-priority recommendation,
3. expose uncertainty and missing information,
4. bias toward escalation when uncertainty could hide risk,
5. continuously monitor patients in the waiting queue,
6. trigger reassessment when risk or wait-time conditions change,
7. preserve clinician authority through accept/override/escalate actions,
8. maintain an auditable decision trail,
9. adapt the workflow to different hospital populations, staffing and surge conditions.

## Critical scope statement

This is a **synthetic, educational hackathon prototype**.

It is **not a medical device, not clinically validated, not intended for diagnosis or treatment, and not for use with real patient data**.

All thresholds, weights, simulated outcomes and evaluation results must be labeled as **illustrative prototype policy** unless backed by an explicit external source listed in `docs/SOURCE_OF_TRUTH.md`.

## Product thesis

> **AcuityFlow does not replace triage judgment. It continuously surfaces what deserves attention, why, and how certain the system is.**

## Killer feature

### Continuous risk-aware re-triage

The core differentiator is not the initial score.

The system watches the waiting queue for:

- worsening newly-recorded observations,
- meaningful risk-trajectory changes,
- overdue reassessments relative to the prototype's severity policy,
- low-confidence / incomplete-data cases.

When these conditions occur, the system raises a **reassessment recommendation** for a clinician.

## Prototype requirements from the supplied case

The prototype must demonstrate:

- at least 15–20 simulated records,
- one ambiguous presentation,
- one pediatric case,
- one geriatric case,
- one zero-history patient,
- a simulated 3× surge,
- explicit uncertainty/confidence,
- at least one clinician override with logging,
- waiting-queue monitoring,
- escalation-biased behavior under uncertainty,
- population-specific logic,
- reviewable/overridable recommendations,
- a privacy/data-protection story,
- an architecture that can scale across hospital profiles.

## Deliberate technology boundary

### Must build

- React + TypeScript frontend
- FastAPI backend
- deterministic safety/policy engine
- synthetic patient data
- lightweight structured risk model (XGBoost or logistic baseline; choose after evaluation)
- confidence / data-completeness layer
- re-triage engine
- surge mode
- override + audit trail
- test/evaluation suite
- optional Gemini integration for symptom extraction and explanation
- optional Google Cloud deployment

### Do NOT build in Round 2

- autonomous diagnosis,
- treatment recommendation,
- real-patient integration,
- real hospital deployment,
- production clinical certification,
- Kubernetes,
- complex microservices,
- unnecessary agents,
- large-scale data warehouse,
- computer vision unless the case later requires it.

## Suggested repository layout

```text
acuityflow-ai/
├── frontend/
├── backend/
├── ml/
├── data/
├── docs/
├── tests/
├── AGENTS.md
└── README.md
```

See the documents under `docs/` before coding.
