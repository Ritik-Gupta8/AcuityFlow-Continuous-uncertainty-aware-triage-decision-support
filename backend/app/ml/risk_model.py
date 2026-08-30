"""
Structured Risk Scoring & Runtime Model Execution.
Loads calibrated scikit-learn model artifacts from ml/artifacts/.
Returns structured risk predictions, calibrated probabilities, and feature attributions.
TODO: CLINICAL VALIDATION REQUIRED.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from app.models.entities import Patient, Observation

class MLRiskScoringEngine:
    def __init__(self, artifact_dir: str = "ml/artifacts"):
        self.artifact_dir = artifact_dir
        self.calibrated_model = None
        self.base_pipeline = None
        self.model_version = "calibrated-lr-v1.0.0-synthetic"
        self.model_status = "FALLBACK"
        self.model_available = False
        self.model_source = "deterministic-fallback"
        self._load_artifacts()

    def _load_artifacts(self):
        calibrated_path = os.path.join(self.artifact_dir, "calibrated_model.joblib")
        base_path = os.path.join(self.artifact_dir, "base_pipeline.joblib")

        # Check relative to backend or root
        if not os.path.exists(calibrated_path):
            alt_cal = os.path.join("..", self.artifact_dir, "calibrated_model.joblib")
            alt_base = os.path.join("..", self.artifact_dir, "base_pipeline.joblib")
            if os.path.exists(alt_cal):
                calibrated_path = alt_cal
                base_path = alt_base

        if os.path.exists(calibrated_path) and os.path.exists(base_path):
            try:
                self.calibrated_model = joblib.load(calibrated_path)
                self.base_pipeline = joblib.load(base_path)
                self.model_status = "CALIBRATED_ML"
                self.model_available = True
                self.model_source = "calibrated_model"
                self.model_version = "calibrated-lr-v1.0.0-synthetic"
                print(f"[AcuityFlow ML] Loaded runtime model artifacts from {calibrated_path}")
            except Exception as e:
                self.calibrated_model = None
                self.base_pipeline = None
                self.model_status = "FALLBACK"
                self.model_available = False
                self.model_source = "deterministic-fallback"
                self.model_version = "fallback-parametric-baseline"
                print(f"[AcuityFlow ML] Error loading artifacts: {e}. Fallback to parametric baseline.")
        else:
            self.calibrated_model = None
            self.base_pipeline = None
            self.model_status = "FALLBACK"
            self.model_available = False
            self.model_source = "deterministic-fallback"
            self.model_version = "fallback-parametric-baseline"
            print("[AcuityFlow ML] Artifacts not found. Using fallback scoring.")

    def _build_feature_row(self, patient: Patient, obs: Optional[Observation]) -> pd.DataFrame:
        """Constructs a single-row DataFrame aligned with training schema."""
        row = {
            "age": patient.age_years if patient.age_years is not None else np.nan,
            "heart_rate": obs.heart_rate if obs and obs.heart_rate is not None else np.nan,
            "respiratory_rate": obs.respiratory_rate if obs and obs.respiratory_rate is not None else np.nan,
            "systolic_bp": obs.systolic_bp if obs and obs.systolic_bp is not None else np.nan,
            "diastolic_bp": obs.diastolic_bp if obs and obs.diastolic_bp is not None else np.nan,
            "spo2": obs.spo2 if obs and obs.spo2 is not None else np.nan,
            "temperature_c": obs.temperature_c if obs and obs.temperature_c is not None else np.nan,
            "pain_score": patient.pain_score if patient.pain_score is not None else np.nan,
            "symptom_duration_mins": patient.symptom_duration_minutes if patient.symptom_duration_minutes is not None else np.nan,
            "profile": patient.population_profile or "adult",
            "history_available": int(bool(patient.history_available)) if patient.history_available is not None else 1,
            "first_time_patient": int(bool(patient.first_time_patient)) if patient.first_time_patient is not None else 0
        }
        return pd.DataFrame([row])

    def predict_risk(self, patient: Patient, latest_obs: Optional[Observation]) -> Dict[str, Any]:
        """
        Runs model inference and returns probability, risk score, and top feature signals.
        """
        df_row = self._build_feature_row(patient, latest_obs)

        if self.calibrated_model is not None:
            try:
                # Calibrated probability of high acuity
                calibrated_prob = float(self.calibrated_model.predict_proba(df_row)[0, 1])
                raw_prob = float(self.base_pipeline.predict_proba(df_row)[0, 1]) if self.base_pipeline else calibrated_prob
                
                # Scale calibrated probability into a 0..100 continuous risk score with vital adjustment
                base_risk = calibrated_prob * 100.0
                
                # Top feature attribution via Logistic Regression coefficients
                top_features = self._extract_feature_attributions(df_row)
                
                return {
                    "risk_score": round(base_risk, 1),
                    "raw_probability": round(raw_prob, 4),
                    "calibrated_probability": round(calibrated_prob, 4),
                    "model_status": "CALIBRATED_ML",
                    "model_available": True,
                    "model_source": "calibrated_model",
                    "model_version": self.model_version,
                    "population_profile": patient.population_profile or "adult",
                    "top_features": top_features
                }
            except Exception as e:
                print(f"[AcuityFlow ML] Prediction error: {e}. Fallback to rule-based estimate.")

        # Robust Fallback if model artifact is unavailable
        return self._fallback_score(patient, latest_obs)

    def _extract_feature_attributions(self, df_row: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extracts top positive risk contributors from linear weights."""
        if not self.base_pipeline or not hasattr(self.base_pipeline.named_steps["clf"], "coef_"):
            return []

        try:
            clf = self.base_pipeline.named_steps["clf"]
            prep = self.base_pipeline.named_steps["prep"]
            X_trans = prep.transform(df_row)[0]
            feature_names = prep.get_feature_names_out()
            coefs = clf.coef_[0]

            contributions = []
            for name, val, coef in zip(feature_names, X_trans, coefs):
                impact = float(val * coef)
                if impact > 0.1:  # Only report signals that increase risk
                    clean_name = name.replace("num__", "").replace("cat__", "").replace("_", " ").title()
                    contributions.append({
                        "feature": clean_name,
                        "impact_weight": round(impact, 2)
                    })

            contributions.sort(key=lambda x: x["impact_weight"], reverse=True)
            return contributions[:4]
        except Exception:
            return []

    def _fallback_score(self, patient: Patient, obs: Optional[Observation]) -> Dict[str, Any]:
        """Fallback scoring function if model artifact is missing."""
        score = 20.0
        signals = []
        if obs:
            if obs.spo2 and obs.spo2 < 94: score += 30; signals.append({"feature": "Low SpO2", "impact_weight": 2.5})
            if obs.heart_rate and obs.heart_rate > 105: score += 20; signals.append({"feature": "Elevated HR", "impact_weight": 1.8})
            if obs.respiratory_rate and obs.respiratory_rate > 22: score += 20; signals.append({"feature": "Tachypnea", "impact_weight": 1.5})
        prob = min(0.99, max(0.01, score / 100.0))
        return {
            "risk_score": round(score, 1),
            "raw_probability": round(prob, 4),
            "calibrated_probability": round(prob, 4),
            "model_status": "FALLBACK",
            "model_available": False,
            "model_source": "deterministic-fallback",
            "model_version": "fallback-parametric-baseline",
            "population_profile": patient.population_profile or "adult",
            "top_features": signals
        }

risk_engine = MLRiskScoringEngine()
