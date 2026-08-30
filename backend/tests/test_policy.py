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

def test_model_certainty_boundary_margin_mathematical_derivation():
    """Regression test: verifies that model certainty is mathematically derived from distance to decision boundary (0.50) and scaled by completeness."""
    from app.ml.uncertainty import compute_uncertainty_breakdown

    patient = Patient(
        patient_id="TEST-MATH-01",
        name="Test Math",
        age_years=58,
        population_profile="adult",
        chief_complaint="Chest discomfort",
        first_time_patient=False,
        history_available=True
    )
    obs = Observation(
        observation_id="OBS-M1",
        patient_id="TEST-MATH-01",
        heart_rate=118.0,
        respiratory_rate=26.0,
        systolic_bp=98.0,
        diastolic_bp=62.0,
        spo2=91.0,
        temperature_c=37.3
    )

    # 1. Borderline probability 0.496 (Risk score 49.6/100) -> distance |0.496 - 0.500| = 0.004 -> 0.004 * 200 = 0.8%
    unc_borderline = compute_uncertainty_breakdown(patient, obs, calibrated_prob=0.496085, completeness=100.0, has_conflict=False)
    assert unc_borderline.model_certainty == 0.8
    assert any("decision boundary margin is 0.8%" in f or "50% threshold" in f for f in unc_borderline.contributing_factors)

    # 2. Maximum entropy / exact boundary 0.500 -> distance 0.0 -> margin = 0.0%
    unc_boundary = compute_uncertainty_breakdown(patient, obs, calibrated_prob=0.500, completeness=100.0, has_conflict=False)
    assert unc_boundary.model_certainty == 0.0

    # 3. Decisive high risk 0.950 -> distance 0.450 -> margin = 0.450 * 200 = 90.0%
    unc_high = compute_uncertainty_breakdown(patient, obs, calibrated_prob=0.950, completeness=100.0, has_conflict=False)
    assert unc_high.model_certainty == 90.0

    # 4. Decisive low risk 0.050 -> distance 0.450 -> margin = 0.450 * 200 = 90.0%
    unc_low = compute_uncertainty_breakdown(patient, obs, calibrated_prob=0.050, completeness=100.0, has_conflict=False)
    assert unc_low.model_certainty == 90.0

    # 5. Incomplete data penalty: 0.950 on 50% completeness -> 90.0 * 0.50 = 45.0%
    unc_incomplete = compute_uncertainty_breakdown(patient, obs, calibrated_prob=0.950, completeness=50.0, has_conflict=False)
    assert unc_incomplete.model_certainty == 45.0

# ==============================================================================
# MODEL ARTIFACT FAILURE & DETERMINISTIC FALLBACK TEST SUITE
# ==============================================================================

def test_fallback_scoring_when_artifacts_unavailable():
    """TEST A & C: Verifies that when model artifacts are unavailable, system enters FALLBACK mode and never claims calibrated ML."""
    from app.ml.risk_model import MLRiskScoringEngine
    from app.policy.action_policy import evaluate_patient_triage

    # Instantiate engine with non-existent artifact dir
    fallback_engine = MLRiskScoringEngine(artifact_dir="non_existent_dir_123")
    assert fallback_engine.model_available is False
    assert fallback_engine.model_status == "FALLBACK"
    assert fallback_engine.model_source == "deterministic-fallback"

    patient = Patient(
        patient_id="PT-FALLBACK-01",
        name="Fallback Test",
        age_years=45,
        population_profile="adult",
        chief_complaint="Shortness of breath",
        first_time_patient=False,
        history_available=True
    )
    obs = Observation(
        observation_id="OBS-FB1",
        patient_id="PT-FALLBACK-01",
        heart_rate=112.0,
        respiratory_rate=24.0,
        systolic_bp=120.0,
        diastolic_bp=80.0,
        spo2=92.0,
        temperature_c=37.0
    )

    pred = fallback_engine.predict_risk(patient, obs)
    assert pred["model_status"] == "FALLBACK"
    assert pred["model_available"] is False
    assert pred["model_source"] == "deterministic-fallback"
    assert "risk_score" in pred
    assert pred["risk_score"] > 0

def test_triage_decision_preserves_model_status_and_truthful_wording():
    """TEST C: Verifies triage decision explanation uses truthful wording under fallback mode."""
    from app.ml.risk_model import risk_engine
    from app.policy.action_policy import evaluate_patient_triage

    patient = Patient(
        patient_id="PT-TEST-STATUS",
        name="Status Test",
        age_years=30,
        population_profile="adult",
        chief_complaint="Minor laceration",
        first_time_patient=False,
        history_available=True
    )
    obs = Observation(
        observation_id="OBS-ST1",
        patient_id="PT-TEST-STATUS",
        heart_rate=72.0,
        respiratory_rate=16.0,
        systolic_bp=120.0,
        diastolic_bp=80.0,
        spo2=99.0,
        temperature_c=36.8
    )

    res = evaluate_patient_triage(patient, obs)
    assert res.model_status in ["CALIBRATED_ML", "FALLBACK"]
    assert res.model_available in [True, False]
    assert res.model_source in ["calibrated_model", "deterministic-fallback"]

    if not res.model_available:
        assert "calibrated ML model" not in res.explanation
        assert "fallback" in res.explanation.lower()
    else:
        assert "calibrated ML model" in res.explanation


