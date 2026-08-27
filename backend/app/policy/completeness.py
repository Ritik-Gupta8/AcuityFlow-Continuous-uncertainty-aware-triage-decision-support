"""
Data Completeness & Missing Information Engine.
Calculates workflow completeness ratio and lists specific missing high-value inputs.
TODO: CLINICAL VALIDATION REQUIRED.
"""

from typing import Tuple, List, Optional
from app.models.entities import Patient, Observation

def calculate_data_completeness(patient: Patient, latest_obs: Optional[Observation]) -> Tuple[float, List[str]]:
    """
    Computes percentage completeness across key intake & observation fields.
    Returns (completeness_score 0..100, missing_information list).
    """
    required_fields = [
        ("age", patient.age_years is not None),
        ("chief_complaint", bool(patient.chief_complaint)),
        ("history_available", patient.history_available and not patient.first_time_patient),
        ("heart_rate", latest_obs is not None and latest_obs.heart_rate is not None),
        ("respiratory_rate", latest_obs is not None and latest_obs.respiratory_rate is not None),
        ("blood_pressure", latest_obs is not None and (latest_obs.systolic_bp is not None or latest_obs.diastolic_bp is not None)),
        ("spo2", latest_obs is not None and latest_obs.spo2 is not None),
        ("temperature", latest_obs is not None and latest_obs.temperature_c is not None),
    ]

    total = len(required_fields)
    present = sum(1 for _, is_present in required_fields if is_present)
    
    missing = []
    if patient.age_years is None:
        missing.append("Patient age missing")
    if not patient.history_available or patient.first_time_patient:
        missing.append("Prior medical history unavailable (First-time / zero-history presentation)")
    if latest_obs is None or latest_obs.heart_rate is None:
        missing.append("Heart rate observation missing")
    if latest_obs is None or latest_obs.respiratory_rate is None:
        missing.append("Respiratory rate observation missing")
    if latest_obs is None or (latest_obs.systolic_bp is None and latest_obs.diastolic_bp is None):
        missing.append("Blood pressure measurement missing")
    if latest_obs is None or latest_obs.spo2 is None:
        missing.append("SpO2 oxygen saturation missing")
    if latest_obs is None or latest_obs.temperature_c is None:
        missing.append("Body temperature measurement missing")

    completeness_score = round((present / total) * 100.0, 1)
    return completeness_score, missing
