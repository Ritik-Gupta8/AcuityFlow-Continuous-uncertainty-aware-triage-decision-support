# Implementation Gaps & Upgrade Plan

This document details the gaps identified in the prototype and the architectural upgrades required.

## Gap 1: ML Model Pipeline & True Artifact Loading
- **Current Gap**: `backend/app/ml/risk_model.py` is a manual weighted scoring function without trained parameters or saved artifacts.
- **Required Upgrade**:
  1. Build a synthetic cohort generator (`ml/data_generation/generate_dataset.py`) producing 2,000+ synthetic records with a fixed random seed, diverse population profiles, and controlled noise.
  2. Implement an offline training script (`ml/training/train_model.py`) that fits a Logistic Regression baseline and optionally compares XGBoost/GradientBoosting with proper train/validation/test splits.
  3. Fit a probability calibration layer (`ml/training/calibrate_model.py`) using `CalibratedClassifierCV` or isotonic regression, outputting `.joblib` model and calibration artifacts in `ml/artifacts/`.
  4. Update `backend/app/ml/risk_model.py` to load the trained model and calibration layer at runtime and output `{ "risk_score": 0..100, "raw_probability": float, "calibrated_probability": float, "model_version": str, "population_profile": str, "top_features": list }`.

## Gap 2: Uncertainty Subsystem
- **Current Gap**: Confidence is calculated with a single hard-coded formula: `completeness * 0.7 + 25 - penalties`.
- **Required Upgrade**:
  1. Create `backend/app/ml/uncertainty.py` combining:
     - **Model Certainty**: Distance from decision boundary / calibrated probability certainty.
     - **Data Completeness**: Weighted completeness of critical intake parameters.
     - **Consistency**: Agreement between measured vitals and clinical cues.
     - **Profile Support**: Demographically-adjusted confidence boundaries.
  2. Enforce the invariant: **low confidence must never downgrade a patient's priority**.

## Gap 3: Distinct Population-Specific Policy Behaviors
- **Current Gap**: Demographic age boundaries resolve correctly, but pediatric and geriatric profiles need deeper differentiation in feature weights, vital sensitivity, and escalation rules.
- **Required Upgrade**:
  - Update `backend/app/policy/population.py` and `backend/app/core/config.py` to ensure population profiles explicitly adjust vital penalty weights, missing-data tolerance, and escalation triggers.

## Gap 4: Transparent Documentation
- **Current Gap**: Missing formal model documentation and synthetic data generation records.
- **Required Upgrade**:
  - Create `docs/SYNTHETIC_DATA_GENERATION.md`
  - Create `docs/MODEL_CARD.md`
  - Create `docs/EVALUATION_REPORT.md`
  - Create `docs/IMPLEMENTATION_AUDIT.md`
  - Create `docs/FINAL_IMPLEMENTATION_REPORT.md`

## Gap 5: Test Suite Expansion
- **Current Gap**: Test suite contains 11 tests.
- **Required Upgrade**:
  - Expand test suite to 30+ tests covering model loading, calibration, reproducibility, uncertainty calculations, population divergence, edge cases, 24 acceptance cases, reassessment triggers, overrides, and audit trails.
