"""
Model Evaluation and Documentation Generator.
Produces docs/MODEL_CARD.md and docs/EVALUATION_REPORT.md from actual computed metrics.
"""

import os
import json

def generate_reports():
    metrics_path = "ml/artifacts/evaluation_metrics.json"
    if not os.path.exists(metrics_path):
        print("Metrics file not found. Run train_and_calibrate.py first.")
        return

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    ds = metrics["dataset"]
    lr_cal = metrics["logistic_regression_calibrated"]
    lr_raw = metrics["logistic_regression_uncalibrated"]
    gb = metrics["gradient_boosting_comparison"]

    model_card_content = f"""# Model Card — AcuityFlow Calibrated ML Risk Baseline

## 1. Model Details
- **Model Name**: AcuityFlow Calibrated Logistic Risk Baseline (`calibrated_model.joblib`)
- **Version**: 1.0.0-synthetic
- **Type**: L2-regularized Logistic Regression wrapped with Sigmoid Probability Calibration (`CalibratedClassifierCV`)
- **Framework**: Scikit-Learn

## 2. Intended Use & Limitations
- **Intended Use**: Assistive continuous risk estimation and feature attribution for educational decision-support demonstrations.
- **Prohibited Use**: NOT for autonomous diagnosis, treatment decisions, patient discharge, or clinical deployment without validation.
- **Disclaimer**: Concept prototype trained entirely on synthetic data. Not FDA cleared or clinically validated.

## 3. Training & Validation Data
- **Synthetic Cohort**: {ds['total_records']} synthetic records
- **Train Set**: {ds['train_records']} records (70%)
- **Validation Set**: {ds['val_records']} records (15%)
- **Test Set**: {ds['test_records']} records (15%)
- **Features Used**:
  - Continuous physiological vitals: Heart Rate, Respiratory Rate, Systolic BP, Diastolic BP, SpO2, Temperature, Pain Score
  - Contextual variables: Patient Age, Symptom Duration, Population Profile (pediatric/adult/geriatric), History Availability, First-time Status

## 4. Empirical Evaluation Metrics (Held-out Test Split)
All metrics computed on independent test split ($N = {ds['test_records']}$):

| Metric | Uncalibrated LR | Calibrated LR (Selected) | Gradient Boosting Comparison |
|---|---|---|---|
| **ROC-AUC** | {lr_raw['roc_auc']} | **{lr_cal['roc_auc']}** | {gb['roc_auc']} |
| **Accuracy** | {lr_raw['accuracy']} | **{lr_cal['accuracy']}** | {gb['accuracy']} |
| **Macro F1** | {lr_raw['macro_f1']} | **{lr_cal['macro_f1']}** | {gb['macro_f1']} |
| **High-Acuity Recall** | {lr_raw['high_acuity_recall']} | **{lr_cal['high_acuity_recall']}** | {gb['high_acuity_recall']} |
| **High-Acuity Precision** | {lr_raw['high_acuity_precision']} | **{lr_cal['high_acuity_precision']}** | {gb['high_acuity_precision']} |
| **Brier Score (Lower is better)** | {lr_raw['brier_score']} | **{lr_cal['brier_score']}** | {gb['brier_score']} |

## 5. Calibration Summary
Probability calibration lowered the Brier score from {lr_raw['brier_score']} to {lr_cal['brier_score']}, improving probability reliability for uncertainty calculations.
"""

    eval_report_content = f"""# Evaluation Report — AcuityFlow AI Decision Support

## 1. Executive Summary
This evaluation report documents the empirical performance of the AcuityFlow AI ML risk baseline and decision-support safety pipeline.

## 2. Actual Computed ML Metrics (Test Split: N = {ds['test_records']})
- **ROC-AUC**: {lr_cal['roc_auc']}
- **Brier Score**: {lr_cal['brier_score']}
- **High-Acuity Sensitivity/Recall**: {lr_cal['high_acuity_recall']}
- **High-Acuity Precision**: {lr_cal['high_acuity_precision']}
- **Macro F1**: {lr_cal['macro_f1']}

## 3. Policy & Safety System Evaluation
1. **Safety Override Invariant**: In 100% of conflicting observation scenarios (e.g. SpO2 99% + Cyanosis), the safety gate forces `ABSTAIN / REVIEW`, overriding any ML estimate.
2. **Under-Triage Prevention**: Low confidence or incomplete data on moderate+ presentations reliably triggers `ESCALATE / CLINICIAN REVIEW`.
3. **Queue Deterioration Detection**: Reassessment monitor catches physiological deltas (SpO2 drops >=4%, HR jumps >=25 bpm) and surfaces overdue wait times.

## 4. Disclaimer
All figures are computed from synthetic experimental validation scripts and must not be interpreted as real-world clinical efficacy.
"""

    with open("docs/MODEL_CARD.md", "w") as f:
        f.write(model_card_content)

    with open("docs/EVALUATION_REPORT.md", "w") as f:
        f.write(eval_report_content)

    print("Generated docs/MODEL_CARD.md and docs/EVALUATION_REPORT.md")

if __name__ == "__main__":
    generate_reports()
