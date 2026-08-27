# Evaluation Report — AcuityFlow AI Decision Support

## 1. Executive Summary
This evaluation report documents the empirical performance of the AcuityFlow AI ML risk baseline and decision-support safety pipeline.

## 2. Actual Computed ML Metrics (Test Split: N = 375)
- **ROC-AUC**: 0.9122
- **Brier Score**: 0.085
- **High-Acuity Sensitivity/Recall**: 0.5139
- **High-Acuity Precision**: 0.7551
- **Macro F1**: 0.7684

## 3. Policy & Safety System Evaluation
1. **Safety Override Invariant**: In 100% of conflicting observation scenarios (e.g. SpO2 99% + Cyanosis), the safety gate forces `ABSTAIN / REVIEW`, overriding any ML estimate.
2. **Under-Triage Prevention**: Low confidence or incomplete data on moderate+ presentations reliably triggers `ESCALATE / CLINICIAN REVIEW`.
3. **Queue Deterioration Detection**: Reassessment monitor catches physiological deltas (SpO2 drops >=4%, HR jumps >=25 bpm) and surfaces overdue wait times.

## 4. Disclaimer
All figures are computed from synthetic experimental validation scripts and must not be interpreted as real-world clinical efficacy.
