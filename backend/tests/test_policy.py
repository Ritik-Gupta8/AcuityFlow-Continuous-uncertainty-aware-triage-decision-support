"""
Unit tests for AcuityFlow policy, safety gate, and uncertainty rules.
"""

import pytest
from app.models.entities import Patient, Observation
from app.policy.population import resolve_population_profile
from app.policy.completeness import calculate_data_completeness
from app.policy.safety_gate import evaluate_safety_gate
from app.policy.action_policy import evaluate_patient_triage

def test_population_profile_resolution():
    assert resolve_population_profile(4) == "pediatric"
    assert resolve_population_profile(17) == "pediatric"
    assert resolve_population_profile(18) == "adult"
    assert resolve_population_profile(45) == "adult"
    assert resolve_population_profile(65) == "geriatric"
    assert resolve_population_profile(82) == "geriatric"
    assert resolve_population_profile(None) == "adult"

def test_data_completeness_zero_history():
    patient = Patient(
        patient_id="TEST-01",
        name="Test Zero History",
        age_years=35,
        population_profile="adult",
        chief_complaint="Weakness",
        first_time_patient=True,
        history_available=False
    )
    obs = Observation(
        observation_id="OBS-01",
        patient_id="TEST-01",
        heart_rate=80.0,
        respiratory_rate=16.0,
        systolic_bp=120.0,
        diastolic_bp=80.0,
        spo2=98.0,
        temperature_c=36.8
    )
    completeness, missing = calculate_data_completeness(patient, obs)
    assert completeness < 100.0
    assert any("First-time / zero-history" in m for m in missing)

def test_safety_gate_conflict_detection():
    # SpO2 = 99% with observed cyanotic cues
    patient = Patient(
        patient_id="TEST-02",
        name="Test Conflict",
        age_years=40,
        population_profile="adult",
        chief_complaint="Shortness of breath",
        observed_cues=["Cyanotic appearance"]
    )
    obs = Observation(
        observation_id="OBS-02",
        patient_id="TEST-02",
        spo2=99.0,
        heart_rate=80.0,
        respiratory_rate=20.0
    )
    flags, has_conflict, conflict_reasons, _ = evaluate_safety_gate(patient, obs)
    assert has_conflict is True
    assert len(conflict_reasons) > 0
    
    # Decision fusion must ABSTAIN and set priority to REVIEW
    result = evaluate_patient_triage(patient, obs)
    assert result.action == "ABSTAIN"
    assert result.priority == "REVIEW"

def test_uncertainty_escalation_bias():
    # Low confidence presentation with moderate risk must escalate
    patient = Patient(
        patient_id="TEST-03",
        name="Test Ambiguous",
        age_years=85,
        population_profile="geriatric",
        chief_complaint="Confusion and weakness",
        first_time_patient=True,
        history_available=False,
        observed_cues=["Unsteady gait"],
        symptom_text="Acute confusion and fatigue"
    )
    obs = Observation(
        observation_id="OBS-03",
        patient_id="TEST-03",
        heart_rate=96.0,
        respiratory_rate=20.0,
        systolic_bp=138.0,
        spo2=93.0,
        temperature_c=37.7
    )
    result = evaluate_patient_triage(patient, obs)
    assert result.action == "ESCALATE"
    assert result.confidence_score < 70.0
