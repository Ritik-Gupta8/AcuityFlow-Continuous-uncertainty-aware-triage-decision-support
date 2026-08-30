# Product Specification — AcuityFlow AI

## 1. User

Primary user:

> Emergency-department triage nurse / authorized clinical staff member.

Secondary users:

- charge nurse / supervisor,
- clinical operations manager,
- privacy/security administrator.

## 2. Core problem

Emergency departments operate with incomplete information, variable patient populations, changing queue pressure, and patients whose condition can change while waiting.

The product is therefore not merely a first-pass triage calculator.

It is a **continuous decision-support workflow**.

## 3. Product promise

AcuityFlow gives staff a concise, explainable view of:

- current priority recommendation,
- why the system is recommending it,
- how confident the system is,
- what information is missing,
- whether a safety escalation is triggered,
- which waiting patients require reassessment.

## 4. Primary workflow

```text
Patient arrives
    ↓
Rapid intake
    ↓
Data-quality check
    ↓
Population profile
    ↓
Safety checks
    ↓
Structured risk model
    ↓
Decision fusion
    ↓
Recommendation + confidence
    ↓
Clinician accepts / overrides / escalates
    ↓
Audit event
    ↓
Patient enters/continues waiting queue
    ↓
Reassessment engine
    ↓
New recommendation when conditions change
```

## 5. Required screens

### 5.1 Command Center

Show:
- queue size,
- severity distribution,
- patients needing attention,
- surge status,
- reassessment alerts.

### 5.2 Patient Intake / Detail

Show:
- patient demographics,
- chief complaint,
- current observations,
- prior-history availability,
- data completeness.

### 5.3 Triage Recommendation

Show:
- priority,
- confidence,
- top contributing signals,
- safety flags,
- missing information,
- recommended next action.

### 5.4 Explainability

Show:
- source inputs,
- policy/model contribution,
- known unknowns,
- uncertainty reasons.

### 5.5 Reassessment

Show:
- before/after observations,
- trajectory change,
- reason for alert,
- recommended reassessment urgency.

### 5.6 Clinician Override

Show:
- AI recommendation,
- clinician decision,
- required override reason,
- optional notes.

### 5.7 Audit Trail

Show:
- decision timeline,
- actor,
- recommendation vs final,
- override justifications,
- security/safety events.

### 5.8 Bounded Free-Text Symptom Extraction (Human Confirmation Flow)

```text
Free Text
    ↓
Symptom Extractor (POST /api/nlp/extract-symptoms)
    ↓
Validated Structured Extraction (Symptoms, Duration, Ambiguity)
    ↓
Clinician Review & Confirmation / Edit
    ↓
Existing Triage Pipeline (Safety Gate + ML Risk Model + Uncertainty + Action Policy)
```

**Key Safety Guarantees:**
- Extractor output is presented strictly as a suggestion.
- Extractor never assigns autonomous triage priority or urgency bands.
- Validated structured symptoms feed into the existing deterministic safety gate and ML risk model.
- Extractor failure gracefully falls back to manual entry without disrupting the triage workflow.

### 5.9 Surge Mode

Show:
- normal volume,
- 3× surge scenario,
- attention queue,
- changed prioritization behavior.

## 6. Killer feature

### AcuityWatch

A waiting-queue monitoring loop that looks for:
- deterioration in newly recorded observations,
- worsening risk trajectory,
- reassessment deadlines crossed under the prototype policy,
- high-uncertainty patients who remain untreated/reviewed.

It does not silently change the clinical decision.

It **raises a visible reassessment recommendation**.

## 7. Secondary differentiators

1. **AcuityGuard** — safety gate.
2. **AcuityExplain** — knowns/unknowns + explanation.
3. **AcuityAdapt** — population and hospital configuration.
4. **AcuityAudit** — human decision trace.
5. **AcuitySurge** — workflow adapts to surge pressure.

## 8. Non-goals

- diagnosis,
- treatment prescription,
- automatic discharge,
- autonomous bed assignment,
- autonomous staff assignment,
- direct patient chatbot,
- real patient deployment.

## 9. Acceptance criteria

A reviewer should be able to verify these without reading the code:

- 20+ synthetic cases can be scored.
- At least one pediatric case uses a pediatric profile.
- At least one geriatric case uses a geriatric profile.
- At least one zero-history case shows low data completeness.
- At least one ambiguous case results in uncertainty-aware escalation.
- 3× surge changes the queue behavior.
- A deterioration event causes re-triage.
- A clinician can override.
- The override is persisted and visible in the audit trail.
- Confidence is visible on every recommendation.
