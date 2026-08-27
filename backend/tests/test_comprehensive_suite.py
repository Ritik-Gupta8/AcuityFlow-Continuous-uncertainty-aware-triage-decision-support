"""
Comprehensive AcuityFlow AI Verification Test Suite.
Tests 30+ critical requirements across ML, safety gates, uncertainty engine,
population divergence, continuous reassessment, surge simulation, and audit trails.
"""

import os
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.entities import Patient, Observation
from app.policy.population import resolve_population_profile
from app.policy.completeness import calculate_data_completeness
from app.policy.safety_gate import evaluate_safety_gate
from app.policy.action_policy import evaluate_patient_triage
from app.ml.risk_model import risk_engine
from app.ml.uncertainty import compute_uncertainty_breakdown
from app.reassessment.monitor import reassessment_monitor
from app.main import app

client = TestClient(app)

# --- 1. Population Profile Resolution & Divergence ---

def test_01_population_profile_resolution():
    assert resolve_population_profile(4) == "pediatric"
    assert resolve_population_profile(17) == "pediatric"
    assert resolve_population_profile(18) == "adult"
    assert resolve_population_profile(45) == "adult"
    assert resolve_population_profile(65) == "geriatric"
    assert resolve_population_profile(88) == "geriatric"
    assert resolve_population_profile(None) == "adult"

def test_02_population_specific_behavior_differs():
    # Identical vitals (HR 145, RR 32) represent critical distress for adult, but expected range for a crying infant/toddler
    obs = Observation(observation_id="OBS-T1", patient_id="T1", heart_rate=145.0, respiratory_rate=32.0, spo2=96.0)
    
    p_adult = Patient(patient_id="P-ADULT", name="Adult", age_years=35, population_profile="adult", chief_complaint="Fever")
    p_pediatric = Patient(patient_id="P-PED", name="Child", age_years=3, population_profile="pediatric", chief_complaint="Fever")

    flags_adult, _, _, _ = evaluate_safety_gate(p_adult, obs)
    flags_pediatric, _, _, _ = evaluate_safety_gate(p_pediatric, obs)

    # Adult triggers critical tachycardia (threshold 130), whereas pediatric warning threshold is 130 and critical is 160
    assert any("Critical Tachycardia" in f for f in flags_adult)
    assert not any("Critical Tachycardia" in f for f in flags_pediatric)

# --- 2. Data Completeness & Zero-History ---

def test_03_data_completeness_calculation():
    patient = Patient(patient_id="P-FULL", name="Full", age_years=30, history_available=True, first_time_patient=False, chief_complaint="Pain")
    obs = Observation(observation_id="O1", patient_id="P-FULL", heart_rate=75.0, respiratory_rate=16.0, systolic_bp=120.0, diastolic_bp=80.0, spo2=98.0, temperature_c=36.8)
    comp, missing = calculate_data_completeness(patient, obs)
    assert comp == 100.0
    assert len(missing) == 0

def test_04_first_time_zero_history_patient():
    patient = Patient(patient_id="PT-005", name="Epsilon", age_years=47, history_available=False, first_time_patient=True, chief_complaint="Weakness")
    obs = Observation(observation_id="O2", patient_id="PT-005", heart_rate=92.0, respiratory_rate=18.0, systolic_bp=108.0, spo2=96.0, temperature_c=37.0)
    comp, missing = calculate_data_completeness(patient, obs)
    assert comp < 100.0
    assert any("First-time / zero-history" in m for m in missing)

# --- 3. Safety Gate & Conflict Detection ---

def test_05_conflicting_data_triggers_abstain():
    # SpO2 99% with Cyanotic cues
    patient = Patient(patient_id="PT-019", name="Tau", age_years=34, chief_complaint="SOB", observed_cues=["Cyanotic appearance"])
    obs = Observation(observation_id="O3", patient_id="PT-019", spo2=99.0, heart_rate=90.0, respiratory_rate=22.0)
    result = evaluate_patient_triage(patient, obs)
    assert result.action == "ABSTAIN"
    assert result.priority == "REVIEW"
    assert any("contradicts" in f.lower() for f in result.safety_flags)

def test_06_critical_safety_flag_overrides_ml():
    # Patient with severe bradycardia (HR 38)
    patient = Patient(patient_id="P-CRIT", name="Crit", age_years=40, chief_complaint="Dizziness")
    obs = Observation(observation_id="O4", patient_id="P-CRIT", heart_rate=38.0, respiratory_rate=16.0, systolic_bp=110.0, spo2=98.0)
    result = evaluate_patient_triage(patient, obs)
    assert result.action == "ESCALATE"
    assert result.priority in ["HIGH", "IMMEDIATE"]
    assert any("Critical Bradycardia" in f for f in result.safety_flags)

# --- 4. ML Model & Probability Calibration ---

def test_07_ml_model_artifacts_load():
    assert risk_engine is not None
    assert risk_engine.calibrated_model is not None or risk_engine.base_pipeline is not None

def test_08_ml_prediction_reproducibility():
    patient = Patient(patient_id="P-REP", name="Rep", age_years=50, history_available=True, first_time_patient=False, chief_complaint="Chest pain")
    obs = Observation(observation_id="O5", patient_id="P-REP", heart_rate=105.0, respiratory_rate=22.0, systolic_bp=145.0, spo2=94.0, temperature_c=37.1)
    
    pred1 = risk_engine.predict_risk(patient, obs)
    pred2 = risk_engine.predict_risk(patient, obs)
    assert pred1["calibrated_probability"] == pred2["calibrated_probability"]
    assert pred1["risk_score"] == pred2["risk_score"]

def test_09_calibration_produces_bounded_probabilities():
    patient = Patient(patient_id="P-BOUND", name="Bound", age_years=25, chief_complaint="Sprain")
    obs = Observation(observation_id="O6", patient_id="P-BOUND", heart_rate=70.0, respiratory_rate=14.0, systolic_bp=115.0, spo2=99.0, temperature_c=36.6)
    pred = risk_engine.predict_risk(patient, obs)
    assert 0.0 <= pred["calibrated_probability"] <= 1.0
    assert 0.0 <= pred["raw_probability"] <= 1.0

# --- 5. Uncertainty Subsystem & Non-Downgrade Invariant ---

def test_10_uncertainty_breakdown_components():
    patient = Patient(patient_id="P-UNC", name="Unc", age_years=85, history_available=False, first_time_patient=True, chief_complaint="Confusion", observed_cues=["Unsteady gait"])
    obs = Observation(observation_id="O7", patient_id="P-UNC", heart_rate=95.0, respiratory_rate=20.0, systolic_bp=135.0, spo2=93.0)
    unc = compute_uncertainty_breakdown(patient, obs, calibrated_prob=0.52, completeness=60.0, has_conflict=False)
    
    assert unc.model_certainty < 50.0  # Near 0.5 decision boundary
    assert unc.data_reliability == 60.0
    assert unc.workflow_confidence < settings.MIN_CONFIDENCE_THRESHOLD

def test_11_low_confidence_never_downgrades_risk():
    # Borderline risk near decision threshold with ambiguous presentation -> must escalate for review
    patient = Patient(
        patient_id="P-SAFE",
        name="Safe",
        age_years=82,
        history_available=False,
        first_time_patient=True,
        chief_complaint="Acute confusion and dizziness",
        observed_cues=["Disoriented", "Unsteady gait"]
    )
    obs = Observation(
        observation_id="O8",
        patient_id="P-SAFE",
        heart_rate=102.0,
        respiratory_rate=21.0,
        systolic_bp=142.0,
        spo2=94.0
    )
    result = evaluate_patient_triage(patient, obs)
    assert result.priority in ["MODERATE", "HIGH", "REVIEW"]
    assert result.action == "ESCALATE"

# --- 6. Continuous Reassessment (AcuityWatch) ---

def test_12_reassessment_on_spo2_drop():
    now = datetime.now(timezone.utc)
    patient = Patient(patient_id="PT-021", name="Phi", current_priority="MODERATE", waiting_minutes=25)
    obs1 = Observation(observation_id="O9a", patient_id="PT-021", timestamp=now - timedelta(minutes=15), spo2=96.0, heart_rate=86.0)
    obs2 = Observation(observation_id="O9b", patient_id="PT-021", timestamp=now, spo2=91.0, heart_rate=118.0)
    patient.observations = [obs2, obs1]

    needs_reassessment, reasons, attention_score = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassessment is True
    assert any("SpO2 dropped" in r for r in reasons)
    assert attention_score > 120

def test_13_reassessment_on_overdue_wait_time():
    patient = Patient(patient_id="P-OVERDUE", name="Overdue", current_priority="HIGH", waiting_minutes=25, observations=[])
    needs_reassessment, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassessment is True
    assert any("Overdue" in r for r in reasons)

# --- 7. API Endpoints, Surge & Clinician Overrides ---

def test_14_api_list_patients():
    res = client.get("/api/patients")
    assert res.status_code == 200
    patients = res.json()
    assert len(patients) >= 24

def test_15_api_surge_mode_toggle():
    res = client.post("/api/simulation/surge", json={"surge_active": True})
    assert res.status_code == 200
    assert res.json()["surge_active"] is True
    
    # List in surge mode
    res_surge = client.get("/api/patients?surge=true")
    assert res_surge.status_code == 200

def test_16_api_advance_time_simulation():
    res = client.post("/api/simulation/advance-time", json={"minutes": 15})
    assert res.status_code == 200
    assert res.json()["advanced_minutes"] == 15

def test_17_api_clinician_override_persists_to_audit():
    override_payload = {
        "clinician_id": "nurse-202",
        "actor_role": "nurse",
        "clinician_action": "override",
        "final_priority": "IMMEDIATE",
        "override_reason": "Additional clinical context from physical exam",
        "clinician_note": "Immediate senior review required."
    }
    res = client.post("/api/patients/PT-021/decision", json=override_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["final_priority"] == "IMMEDIATE"

    # Verify audit trail contains the event
    audit_res = client.get("/api/audit?patient_id=PT-021")
    assert audit_res.status_code == 200
    audits = audit_res.json()
    assert any(a["event_type"] == "override" and a["decision"] == "IMMEDIATE" for a in audits)

def test_18_override_requires_mandatory_reason():
    invalid_payload = {
        "clinician_id": "nurse-202",
        "actor_role": "nurse",
        "clinician_action": "override",
        "final_priority": "HIGH",
        "override_reason": "",
        "clinician_note": "No reason provided"
    }
    res = client.post("/api/patients/PT-001/decision", json=invalid_payload)
    assert res.status_code == 400

def test_19_reassessment_queue_endpoint():
    res = client.get("/api/reassessment/queue")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_20_simulation_reset():
    res = client.post("/api/simulation/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

# --- 8. Canonical Acceptance Cases (PT-001 to PT-024) ---

@pytest.mark.parametrize("pt_id,expected_profile", [
    ("PT-001", "adult"),
    ("PT-005", "adult"),
    ("PT-011", "pediatric"),
    ("PT-012", "pediatric"),
    ("PT-015", "geriatric"),
    ("PT-017", "geriatric"),
    ("PT-019", "adult"),
    ("PT-021", "adult"),
    ("PT-024", "geriatric")
])
def test_acceptance_patient_profiles(pt_id, expected_profile):
    res = client.get(f"/api/patients/{pt_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["population_profile"] == expected_profile
