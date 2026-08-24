# Safety, Uncertainty and Fail-Safe Design

## 1. Core principle

> When the system knows less, it must not pretend to know more.

## 2. Safety states

### RECOMMEND

Used when:
- data is sufficiently complete,
- inputs are consistent,
- model/policy confidence is acceptable,
- no safety condition requires escalation.

### REASSESS

Used when:
- the patient is already waiting,
- a meaningful change is detected,
- a configured reassessment condition is met.

### ESCALATE

Used when:
- a safety flag is triggered,
- uncertainty is material,
- data is insufficient for a safe recommendation,
- a potentially serious presentation conflicts with low model confidence.

### ABSTAIN

Used when:
- the system cannot safely provide a recommendation.

When abstaining, the UI must say:
- why it abstained,
- what information is missing,
- what the clinician can do next.

## 3. Data completeness

Define completeness as:

```text
available required inputs / required inputs
```

This is a workflow metric, not a medical quality score.

Example:

```text
Required for prototype profile:
8
Available:
3

Data completeness:
37.5%
```

## 4. Input conflict

Example:

```text
SpO2 = 99%
Observation note = "cyanotic appearance"
```

The system should not silently choose one.

It should:
- mark the conflict,
- request verification,
- escalate/review according to policy.

## 5. Missing-history behavior

For a first-time patient:

```text
history_available = false
```

The system should:
- show "first-time / no prior record",
- reduce data completeness,
- identify missing high-value history fields,
- avoid pretending that unknown history is negative.

## 6. Under-triage bias

The prototype uses a conservative policy:

```text
high uncertainty + non-low estimated risk → escalate/review
```

The product should show this visibly.

Example UI:

> Estimated risk: MODERATE  
> Confidence: LOW  
> Action: ESCALATE FOR CLINICIAN REVIEW

## 7. Worst-case scenarios to test

- contradictory observations,
- missing history,
- missing vital,
- delayed vital update,
- sudden deterioration,
- pediatric profile,
- geriatric profile,
- surge workload,
- duplicate patient event,
- stale observation.

## 8. Safety logging

Every safety action should capture:
- patient ID,
- event type,
- trigger,
- prior state,
- new state,
- confidence,
- policy version,
- actor,
- timestamp.

## 9. No autonomous final decisions

The system must never:
- lock a patient into a care pathway,
- hide an alternative,
- disable override,
- silently downgrade after an uncertain prediction.

## 10. Explainability requirement

For every recommendation show:

1. key inputs,
2. data quality,
3. uncertainty,
4. reason,
5. action.

This supports independent human review. FDA guidance for clinical decision-support software emphasizes enabling healthcare professionals to independently review the basis of recommendations, including relevant inputs, methods, data limitations and known/unknown information. citeturn802599search36
