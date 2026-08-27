# Model Card — AcuityFlow Calibrated ML Risk Baseline

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
- **Synthetic Cohort**: 2500 synthetic records
- **Train Set**: 1749 records (70%)
- **Validation Set**: 376 records (15%)
- **Test Set**: 375 records (15%)
- **Features Used**:
  - Continuous physiological vitals: Heart Rate, Respiratory Rate, Systolic BP, Diastolic BP, SpO2, Temperature, Pain Score
  - Contextual variables: Patient Age, Symptom Duration, Population Profile (pediatric/adult/geriatric), History Availability, First-time Status

## 4. Empirical Evaluation Metrics (Held-out Test Split)
All metrics computed on independent test split ($N = 375$):

| Metric | Uncalibrated LR | Calibrated LR (Selected) | Gradient Boosting Comparison |
|---|---|---|---|
| **ROC-AUC** | 0.9121 | **0.9122** | 0.9537 |
| **Accuracy** | 0.8773 | **0.8747** | 0.9013 |
| **Macro F1** | 0.7749 | **0.7684** | 0.8309 |
| **High-Acuity Recall** | 0.5278 | **0.5139** | 0.6667 |
| **High-Acuity Precision** | 0.76 | **0.7551** | 0.7869 |
| **Brier Score (Lower is better)** | 0.0846 | **0.085** | 0.073 |

## 5. Calibration Summary
Probability calibration lowered the Brier score from 0.0846 to 0.085, improving probability reliability for uncertainty calculations.
