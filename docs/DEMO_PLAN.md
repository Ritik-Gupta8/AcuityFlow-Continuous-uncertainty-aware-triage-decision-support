# Prototype Demo Plan

## Goal

The demo must make one thing unforgettable:

> **AcuityFlow catches a meaningful change in a waiting patient and brings the clinician back into the loop.**

## 1. Demo sequence

### Scene 1 — Command Center

Show:
- 20+ simulated patients,
- queue distribution,
- current attention queue.

### Scene 2 — Ambiguous case

Open a geriatric patient with:
- partial history,
- non-specific symptoms,
- conflicting/limited information.

Show:
- estimated risk,
- low confidence,
- escalation.

### Scene 3 — Pediatric case

Switch patient.

Show:
- pediatric profile,
- different configuration,
- recommendation and confidence.

### Scene 4 — Zero-history

Show:
- no prior record,
- low data completeness,
- missing information prompt,
- conservative escalation.

### Scene 5 — Activate 3× surge

Show:
- queue volume increase,
- attention queue behavior changes,
- deterioration and overdue reassessment alerts move to top.

### Scene 6 — Killer moment

Patient #1042:

Initial:
```text
HIGH
confidence high
```

After simulated time:
```text
new observations
risk trajectory ↑
```

System:
```text
REASSESS NOW
```

### Scene 7 — Human decision

Click:
```text
OVERRIDE
```

Select:
```text
Additional clinical context
```

Show the audit entry.

## 2. Visual emphasis

The video should not be a tour of every page.

Spend the most time on:
- uncertainty,
- deterioration,
- human override,
- surge behavior.

## 3. Talking points

### Opening
"Emergency triage is a moving target, not a one-time score."

### Middle
"AcuityFlow combines structured risk, data quality and population-specific policy."

### Killer moment
"We don't wait for the next formal triage cycle to notice that the patient has changed."

### Human control
"The system can recommend, escalate or abstain; the clinician remains accountable."

### Close
"From static triage to continuous, explainable decision support."

## 4. Prototype disclosure

Always include:

> Concept prototype • synthetic data • not for clinical use
