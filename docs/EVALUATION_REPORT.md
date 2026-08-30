# Evaluation Report — AcuityFlow AI Decision Support

## 1. Executive Summary
This evaluation report documents the empirical performance of the AcuityFlow AI ML risk baseline and decision-support safety pipeline.

## 2. Dataset Splits & Leakage Prevention Protocol
- **Total Synthetic Cohort**: 2500 synthetic records (`SYN-00001` through `SYN-02500`)
- **Training Set ($N_{train}$)**: **1749** records (70.0%)
- **Validation Set ($N_{val}$)**: **376** records (15.0%)
- **Held-out Test Set ($N_{test}$)**: **375** records (15.0%)
- **Random Seed**: Fixed `random_state = 42` (with target stratification across all split stages)

### Zero Train/Test Leakage Guarantee
1. **Preprocessing Pipeline Isolation**: All transformers (`SimpleImputer`, `StandardScaler`, `OneHotEncoder`) are fit strictly on `X_train` inside the scikit-learn pipeline (`Pipeline.fit(X_train, y_train)`).
2. **Independent Test Evaluation**: The test split ($N = 375$) is strictly transformed and evaluated post-fitting. The test set is never used during parameter optimization or probability calibration folds (`CalibratedClassifierCV(cv=5)` on `X_train`).
3. **Showcase Scenarios Non-Contamination**: The 24 showcase demonstration patients (`PT-001` to `PT-024`) are maintained exclusively in `backend/app/data/seed_cases.py` for runtime validation. Zero showcase scenarios exist in or were used to train the ML risk model.

## 3. Actual Computed ML Metrics (Test Split: N = 375)
- **ROC-AUC**: 0.9122
- **Brier Score**: 0.085
- **High-Acuity Sensitivity/Recall**: 0.5139
- **High-Acuity Precision**: 0.7551
- **Macro F1**: 0.7684

## 4. Policy & Safety System Evaluation
1. **Safety Override Invariant**: In 100% of conflicting observation scenarios (e.g. SpO2 99% + Cyanosis), the safety gate forces `ABSTAIN / REVIEW`, overriding any ML estimate.
2. **Under-Triage Prevention**: Low confidence or incomplete data on moderate+ presentations reliably triggers `ESCALATE / CLINICIAN REVIEW`.
3. **Queue Deterioration Detection**: Reassessment monitor catches physiological deltas (SpO2 drops >=4%, HR jumps >=25 bpm) and surfaces overdue wait times.

## 5. Disclaimer
All figures are computed from synthetic experimental validation scripts and must not be interpreted as real-world clinical efficacy.
