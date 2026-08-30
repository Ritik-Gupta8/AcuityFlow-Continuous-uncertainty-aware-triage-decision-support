# Test Cases — 24 Synthetic Patients

## Purpose

These cases are designed to test the prototype against explicit safety, edge-case, and continuous re-triage requirements.

They are **not clinical benchmark cases**.

The "expected behavior" column is a prototype-behavior assertion, not a medical diagnosis.

## Test matrix

| ID | Profile | History | Presentation | Clinical Scenario | Expected prototype behavior |
|---|---|---|---|---|---|
| PT-001 | Adult | Full | straightforward | baseline | RECOMMEND |
| PT-002 | Adult | Full | straightforward | baseline | RECOMMEND |
| PT-003 | Adult | Partial | chest-related symptoms | incomplete data | HIGH / review |
| PT-004 | Adult | Full | abdominal symptoms | baseline | RECOMMEND |
| PT-005 | Adult | None | weakness | zero-history | ESCALATE / review |
| PT-006 | Adult | Partial | dizziness | ambiguity | REVIEW |
| PT-007 | Adult | Full | respiratory symptoms | trend test | RECOMMEND |
| PT-008 | Adult | Full | pain presentation | baseline | RECOMMEND |
| PT-009 | Adult | Partial | overlapping symptoms | ambiguity | ESCALATE |
| PT-010 | Adult | Full | worsening observations | deterioration | REASSESS |
| PT-011 | Pediatric | None | fever + lethargy | pediatric profile | PROFILE-SPECIFIC REVIEW |
| PT-012 | Pediatric | Full | injury | pediatric profile | PROFILE-SPECIFIC RECOMMEND |
| PT-013 | Pediatric | Partial | respiratory complaint | pediatric uncertainty | ESCALATE / review |
| PT-014 | Pediatric | None | vomiting + lethargy | zero-history | ESCALATE / review |
| PT-015 | Geriatric | Full | weakness | geriatric presentation | PROFILE-SPECIFIC REVIEW |
| PT-016 | Geriatric | Partial | dizziness | missing history | ESCALATE |
| PT-017 | Geriatric | None | confusion + weakness | ambiguity | ESCALATE |
| PT-018 | Geriatric | Full | respiratory complaint | baseline | RECOMMEND |
| PT-019 | Adult | Full | observation conflict | conflicting data | ABSTAIN / review |
| PT-020 | Adult | Partial | stale vitals | data quality | REASSESS |
| PT-021 | Adult | Full | worsening over time | waiting queue | REASSESS |
| PT-022 | Adult | None | symptom text only | sparse intake | ESCALATE / review |
| PT-023 | Pediatric | Partial | waiting + change | queue monitoring | REASSESS |
| PT-024 | Geriatric | Partial | waiting + risk rise | queue monitoring | REASSESS |

## Required special cases

### PT-005 — zero-history adult

Must show:
- history unavailable,
- reduced completeness,
- no silent assumption that unknown history is negative,
- targeted missing-information prompt.

### PT-011 — pediatric

Must show:
- pediatric profile selected,
- pediatric policy version displayed,
- no adult profile leakage.

### PT-017 — geriatric ambiguous

Must show:
- low/medium confidence,
- ambiguity explanation,
- escalation/review rather than false certainty.

### PT-019 — conflicting data

Must show:
- conflict flag,
- no silent data selection,
- review/abstention.

### PT-021 — waiting deterioration

Must show:
- previous state,
- new observation,
- trajectory change,
- reassessment recommendation.

### PT-023 / PT-024 — waiting queue

Must show:
- queue age,
- reassessment state,
- clinician attention queue.

## 3× surge scenario

Create a simulation mode:

```text
NORMAL
baseline queue and staffing

SURGE
3× incoming volume
```

Under surge:
- more patients are in the attention queue,
- the UI reduces low-value detail on the main command center,
- deteriorating patients are surfaced first,
- overdue reassessments are surfaced,
- low-confidence cases remain visible,
- recommendations remain clinician-overridable.

## Override test

At least one case must produce:

```text
AI: HIGH
Clinician: MODERATE
Reason: Additional clinical context
```

or another plausible synthetic override.

The system must persist:
- original recommendation,
- new clinician decision,
- reason,
- actor,
- timestamp.

## Test philosophy

Passing means:

> the system behaves safely and predictably under the designed prototype policy.

Passing does NOT mean:

> the system is clinically accurate or ready for deployment.
