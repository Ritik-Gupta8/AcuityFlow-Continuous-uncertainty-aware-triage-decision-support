# Evaluation Plan

## 1. What to evaluate

Do not optimize only for average accuracy.

Measure five dimensions:

1. recommendation consistency,
2. uncertainty behavior,
3. safety/escalation behavior,
4. workflow usefulness,
5. system performance.

## 2. ML metrics

If an ML model is trained, calculate only metrics supported by actual experiments:

- accuracy,
- macro F1,
- precision/recall,
- confusion matrix,
- ROC-AUC where appropriate.

For safety-oriented analysis also inspect:
- recall for the synthetic "high/critical" class,
- confusion cases,
- calibration or reliability where implemented.

Never invent numbers.

## 3. Policy metrics

These are especially important.

### Uncertainty escalation rate

```text
uncertain cases escalated
/
all uncertain cases
```

### Missing-data protection

```text
cases with missing key inputs that avoided silent low-risk recommendation
/
cases with missing key inputs
```

### Deterioration detection

```text
synthetic deterioration events surfaced
/
synthetic deterioration events
```

### Override capture rate

```text
logged overrides
/
submitted overrides
```

## 4. Queue simulation metrics

Under normal and 3× surge simulations record:
- queue size,
- high-priority waiting count,
- overdue reassessments,
- detected deterioration events,
- clinician-visible attention queue size.

Do not claim that a synthetic reduction proves real-world wait-time improvement.

## 5. Compare policies

Run at least:

### Baseline
Simple risk model only.

### AcuityFlow
Risk model + safety rules + uncertainty + population profile + re-triage.

The comparison should answer:

> Does the safety-aware policy produce safer prototype behavior than the simple baseline?

## 6. Evaluation split

If training a model:
- generate train/test data independently,
- avoid patient duplication across splits,
- do not leak downstream outcome fields.

If synthetic data are generated from templates, vary templates enough to avoid trivial memorization.

## 7. Demo evidence

The final video and README should show actual evidence from the running prototype:
- screenshots,
- test output,
- audit events,
- surge mode,
- a deterioration event,
- an override.

No simulated metric may be presented as a measured real-world outcome.
