"""
Model Training and Calibration Pipeline.
Trains Logistic Regression baseline and Gradient Boosting comparison models.
Calibrates probabilities and exports model artifacts.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
    accuracy_score, brier_score_loss, confusion_matrix
)

def build_preprocessing_pipeline(numeric_features, categorical_features):
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", num_pipeline, numeric_features),
        ("cat", cat_pipeline, categorical_features)
    ])
    
    return preprocessor

def train_and_evaluate(data_path: str = "ml/data/synthetic_cohort.csv"):
    df = pd.read_csv(data_path)

    numeric_features = [
        "age", "heart_rate", "respiratory_rate", "systolic_bp",
        "diastolic_bp", "spo2", "temperature_c", "pain_score", "symptom_duration_mins"
    ]
    categorical_features = ["profile", "history_available", "first_time_patient"]

    X = df[numeric_features + categorical_features]
    y = df["high_acuity_target"]

    # 70% Train, 15% Validation, 15% Test Split
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1765, random_state=42, stratify=y_temp)

    preprocessor = build_preprocessing_pipeline(numeric_features, categorical_features)

    # 1. Train Baseline Logistic Regression
    lr_base = LogisticRegression(max_iter=1000, random_state=42)
    lr_pipeline = Pipeline([
        ("prep", preprocessor),
        ("clf", lr_base)
    ])
    lr_pipeline.fit(X_train, y_train)

    # 2. Train 5-Fold Calibrated Logistic Regression on train split
    calibrated_lr = CalibratedClassifierCV(estimator=lr_pipeline, method="sigmoid", cv=5)
    calibrated_lr.fit(X_train, y_train)

    # 3. Train Gradient Boosting Classifier for comparison
    gb_clf = HistGradientBoostingClassifier(random_state=42, max_iter=100)
    # Fit preprocessor on train for GB
    X_train_prep = preprocessor.fit_transform(X_train)
    X_test_prep = preprocessor.transform(X_test)
    gb_clf.fit(X_train_prep, y_train)

    # Evaluate Models on Held-out Test Set
    def compute_metrics(model, X_eval, y_eval, is_prep=False):
        if is_prep:
            probs = model.predict_proba(X_eval)[:, 1]
            preds = model.predict(X_eval)
        else:
            probs = model.predict_proba(X_eval)[:, 1]
            preds = model.predict(X_eval)

        return {
            "accuracy": round(float(accuracy_score(y_eval, preds)), 4),
            "roc_auc": round(float(roc_auc_score(y_eval, probs)), 4),
            "macro_f1": round(float(f1_score(y_eval, preds, average="macro")), 4),
            "high_acuity_recall": round(float(recall_score(y_eval, preds, pos_label=1)), 4),
            "high_acuity_precision": round(float(precision_score(y_eval, preds, pos_label=1, zero_division=0)), 4),
            "brier_score": round(float(brier_score_loss(y_eval, probs)), 4)
        }

    lr_raw_metrics = compute_metrics(lr_pipeline, X_test, y_test)
    lr_cal_metrics = compute_metrics(calibrated_lr, X_test, y_test)
    gb_metrics = compute_metrics(gb_clf, X_test_prep, y_test, is_prep=True)

    metrics_report = {
        "dataset": {
            "total_records": len(df),
            "train_records": len(X_train),
            "val_records": len(X_val),
            "test_records": len(X_test),
            "synthetic_disclaimer": "Metrics calculated on synthetic demonstration cohort only."
        },
        "logistic_regression_uncalibrated": lr_raw_metrics,
        "logistic_regression_calibrated": lr_cal_metrics,
        "gradient_boosting_comparison": gb_metrics,
        "selected_runtime_model": "logistic_regression_calibrated"
    }

    # Save artifacts
    os.makedirs("ml/artifacts", exist_ok=True)
    joblib.dump(calibrated_lr, "ml/artifacts/calibrated_model.joblib")
    joblib.dump(lr_pipeline, "ml/artifacts/base_pipeline.joblib")

    with open("ml/artifacts/evaluation_metrics.json", "w") as f:
        json.dump(metrics_report, f, indent=2)

    print("--- Training & Evaluation Complete ---")
    print(json.dumps(metrics_report, indent=2))

if __name__ == "__main__":
    train_and_evaluate()
