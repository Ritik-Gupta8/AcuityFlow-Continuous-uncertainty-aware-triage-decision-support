"""
Structured Risk Scoring & Explainability Baseline (AcuityExplain).
Estimates underlying risk score (0..100) and model certainty.
TODO: CLINICAL VALIDATION REQUIRED.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
from app.core.config import settings
from app.models.entities import Patient, Observation

class RiskScoringEngine:
    def __init__(self):
        # Baseline model weights (Illustrative weights calibrated for synthetic triage)
        # TODO: CLINICAL VALIDATION REQUIRED
        self.weights = {
            "hr_dev": 0.22,
            "rr_dev": 0.25,
            "spo2_dev": 0.28,
            "bp_dev": 0.15,
            "temp_dev": 0.10,
        }

    def _calculate_vital_deviations(self, patient: Patient, obs: Optional[Observation]) -> Tuple[float, List[str], Dict[str, float]]:
        """
        Calculates normalized vital deviation penalties according to population profile.
        """
        if not obs:
            return 30.0, ["Vitals unavailable - baseline uncertainty applied"], {}

        profile = patient.population_profile or "adult"
        thresholds = settings.VITAL_THRESHOLDS.get(profile, settings.VITAL_THRESHOLDS["adult"])
        
        raw_risk = 10.0  # Baseline intercept
        contributions = {}
        signals = []

        # Heart Rate
        if obs.heart_rate is not None:
            if obs.heart_rate > thresholds["hr_warning_high"]:
                dev = min(1.0, (obs.heart_rate - thresholds["hr_warning_high"]) / 40.0)
                score = dev * 100 * self.weights["hr_dev"]
                raw_risk += score
                contributions["Heart Rate"] = round(score, 1)
            elif obs.heart_rate < thresholds["hr_warning_low"]:
                dev = min(1.0, (thresholds["hr_warning_low"] - obs.heart_rate) / 20.0)
                score = dev * 100 * self.weights["hr_dev"]
                raw_risk += score
                contributions["Heart Rate (Low)"] = round(score, 1)

        # Respiratory Rate
        if obs.respiratory_rate is not None:
            if obs.respiratory_rate > thresholds["rr_warning_high"]:
                dev = min(1.0, (obs.respiratory_rate - thresholds["rr_warning_high"]) / 15.0)
                score = dev * 100 * self.weights["rr_dev"]
                raw_risk += score
                contributions["Respiratory Rate"] = round(score, 1)
            elif obs.respiratory_rate < thresholds["rr_warning_low"]:
                dev = min(1.0, (thresholds["rr_warning_low"] - obs.respiratory_rate) / 5.0)
                score = dev * 100 * self.weights["rr_dev"]
                raw_risk += score
                contributions["Respiratory Rate (Low)"] = round(score, 1)

        # SpO2
        if obs.spo2 is not None:
            if obs.spo2 < 95.0:
                dev = min(1.0, (95.0 - obs.spo2) / 10.0)
                score = dev * 100 * self.weights["spo2_dev"]
                raw_risk += score
                contributions["SpO2 Hypoxia"] = round(score, 1)

        # Blood Pressure (Systolic)
        if obs.systolic_bp is not None:
            if obs.systolic_bp > thresholds["sys_bp_warning_high"]:
                dev = min(1.0, (obs.systolic_bp - thresholds["sys_bp_warning_high"]) / 50.0)
                score = dev * 100 * self.weights["bp_dev"]
                raw_risk += score
                contributions["Systolic BP High"] = round(score, 1)
            elif obs.systolic_bp < thresholds["sys_bp_warning_low"]:
                dev = min(1.0, (thresholds["sys_bp_warning_low"] - obs.systolic_bp) / 30.0)
                score = dev * 100 * self.weights["bp_dev"]
                raw_risk += score
                contributions["Systolic BP Low"] = round(score, 1)

        # Temperature
        if obs.temperature_c is not None:
            if obs.temperature_c > thresholds["temp_warning_high"]:
                dev = min(1.0, (obs.temperature_c - thresholds["temp_warning_high"]) / 2.5)
                score = dev * 100 * self.weights["temp_dev"]
                raw_risk += score
                contributions["Temperature"] = round(score, 1)

        # Pain Score impact
        if patient.pain_score is not None and patient.pain_score >= 7:
            pain_add = min(15.0, (patient.pain_score - 6) * 3.5)
            raw_risk += pain_add
            contributions["Severe Pain"] = round(pain_add, 1)

        return min(100.0, max(0.0, raw_risk)), signals, contributions

    def score_patient(self, patient: Patient, latest_obs: Optional[Observation], completeness: float) -> Tuple[float, float, Dict[str, float]]:
        """
        Calculates risk score (0..100), confidence score (0..100), and feature contributions.
        Confidence is penalized when data completeness is low or presentation is ambiguous.
        """
        raw_risk, _, contributions = self._calculate_vital_deviations(patient, latest_obs)

        # Confidence calculation
        # Baseline confidence derived from completeness and consistency
        base_confidence = completeness * 0.7 + 25.0
        
        # Penalties for first-time patient or ambiguous presentation
        if patient.first_time_patient or not patient.history_available:
            base_confidence -= 15.0
            
        cues = [c.lower() for c in (patient.observed_cues or [])]
        if "confusion" in (patient.symptom_text or "").lower() or any("dizziness" in c for c in cues):
            base_confidence -= 10.0

        confidence = round(max(20.0, min(95.0, base_confidence)), 1)
        risk_score = round(raw_risk, 1)

        return risk_score, confidence, contributions

risk_engine = RiskScoringEngine()
