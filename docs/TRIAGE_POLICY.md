# Triage Policy — Prototype Only

## 0. Safety notice

This document defines an **illustrative prototype policy**, not a clinical protocol.

No threshold, weight or category below is presented as a medical standard.

Where a threshold is required for the prototype, it must be:
- configurable,
- labeled as illustrative,
- versioned,
- accompanied by `clinical_validation_required: true`.

## 1. Output model

The engine produces:

```text
risk_score            0..100
confidence_score      0..100
data_completeness     0..100
safety_flags          []
population_profile    pediatric | adult | geriatric
priority              IMMEDIATE | HIGH | MODERATE | LOW | REVIEW
action                RECOMMEND | REASSESS | ESCALATE | ABSTAIN
```

`REVIEW`, `ESCALATE` and `ABSTAIN` are safety states, not severity labels.

## 2. Feature groups

### A. Structured observations
- heart rate,
- respiratory rate,
- blood pressure,
- SpO2,
- temperature,
- pain score.

### B. Patient context
- age,
- arrival mode,
- relevant history availability,
- pregnancy field when applicable,
- known conditions when voluntarily provided.

### C. Presentation
- chief complaint,
- symptom duration,
- free-text symptom description,
- observed cues.

### D. Data quality
- field completeness,
- conflicting values,
- stale measurements,
- unknown/first-time status.

## 3. Population profiles

Use a configuration object rather than a hard-coded clinical standard.

```text
Profile:
  pediatric
  adult
  geriatric
```

Each profile can specify:
- feature availability,
- rule activation,
- weighting strategy,
- confidence adjustment,
- escalation behavior.

The exact age boundaries are a **project assumption** and must be shown in configuration, not presented as universal medical truth.

## 4. Hybrid decision pipeline

```text
Input
  ↓
Normalize
  ↓
Data quality
  ↓
Population profile
  ↓
Safety rules
  ↓
Risk model
  ↓
Fuse outputs
  ↓
Uncertainty policy
  ↓
Action
```

## 5. Illustrative risk bands

For the demo only:

```text
0–24   LOW
25–49  MODERATE
50–74  HIGH
75–100 IMMEDIATE
```

These are **synthetic demonstration bands**.

Do not describe them as a validated triage scale.

## 6. Escalation overrides

The action policy can override the risk band.

Illustrative policy:

```text
IF critical_safety_flag:
    action = ESCALATE

ELSE IF confidence < configured_min_confidence:
    action = ESCALATE

ELSE IF data_completeness < configured_min_completeness
        AND risk_band >= MODERATE:
    action = ESCALATE

ELSE IF conflicting_inputs:
    action = ABSTAIN

ELSE:
    action = RECOMMEND
```

## 7. Why escalation is preferred

The system design explicitly requires the prototype to bias toward escalation under uncertainty because under-triage has asymmetric cost.

Therefore:

> **Uncertainty must never silently convert into a lower-priority recommendation.**

## 8. Model choice

Start with a simple baseline:

1. logistic regression,
2. compare with XGBoost,
3. keep XGBoost only if evaluation shows a useful improvement without unacceptable complexity.

The model is not the product.

The safety/decision policy is the product.

## 9. LLM use

Gemini is allowed only for:
- extracting structured symptom attributes from free text,
- summarizing known inputs,
- generating clinician-facing explanations from structured fields.

Example:

```text
raw text
  ↓
LLM extraction
  ↓
validated structured object
  ↓
risk engine
```

Never:

```text
raw text
  ↓
LLM
  ↓
final triage level
```

## 10. Confidence policy

Confidence should be derived from a documented combination of:
- model certainty,
- input completeness,
- input consistency,
- population-profile coverage,
- rule/model agreement.

It must not be a fabricated number.

## 11. Prototype disclaimer

Every model/policy page must visibly state:

> Synthetic / illustrative policy — not for clinical use.
