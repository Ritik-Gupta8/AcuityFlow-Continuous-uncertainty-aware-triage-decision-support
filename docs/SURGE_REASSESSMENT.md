# Surge and Reassessment Design

## 1. Purpose

Round 2 explicitly requires the system to behave under a simulated 3× surge and to monitor waiting patients for deterioration or overdue reassessment.

## 2. Simulation

Define:

```text
surge_multiplier = 3.0
```

This means:

```text
simulated_arrivals = baseline_arrivals × 3
```

This is an operational simulation parameter, not a hospital benchmark.

## 3. Surge-mode behavior

### Normal mode
- full patient detail,
- normal attention queue,
- standard refresh cadence.

### Surge mode
- compact queue view,
- attention-first ordering,
- deterioration alerts pinned to top,
- overdue reassessment badges,
- low-confidence cases surfaced,
- lower-priority detail collapsed.

The system must not silently change clinical priority thresholds just because surge mode is active.

It changes **workflow prioritization**, not medical truth.

## 4. Attention score

Use a transparent operational attention score:

```text
attention_priority =
    deterioration_flag
    + reassessment_due
    + low_confidence
    + current_priority
```

The exact weights are prototype configuration.

The UI must explain why a patient appears at the top.

## 5. Reassessment triggers

A patient waiting in the queue can trigger:

### Vital-change trigger
A newer observation is meaningfully worse than the previous observation under the selected prototype rules.

### Wait-time trigger
A patient crosses the prototype's configured reassessment window.

### Risk-trajectory trigger
The risk engine produces a meaningful upward change.

### Uncertainty trigger
A patient remains in a low-confidence state and the required information has not been resolved.

## 6. Reassessment output

Example:

```text
PATIENT #1042

Previous:
HIGH
Confidence 89%

New:
Risk trajectory ↑
Confidence 93%

Action:
REASSESS NOW

Reasons:
- new observation change
- waiting policy threshold reached
```

## 7. Important distinction

The reassessment engine does NOT diagnose deterioration.

It identifies a **workflow event requiring clinician attention**.

## 8. Simulation controls

The prototype should support:

```text
Advance 5 min
Advance 10 min
Inject new vitals
Activate surge
Run queue simulation
```

This makes the behavior easy to demonstrate.
