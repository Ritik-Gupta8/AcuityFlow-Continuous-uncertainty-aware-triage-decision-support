"""
Unit tests for continuous reassessment monitor (AcuityWatch).
"""

from datetime import datetime, timezone, timedelta
from app.models.entities import Patient, Observation
from app.reassessment.monitor import reassessment_monitor

def test_deterioration_vital_drop():
    now = datetime.now(timezone.utc)
    patient = Patient(
        patient_id="TEST-RETRIAGE-01",
        name="Test Deterioration",
        current_priority="MODERATE",
        waiting_minutes=20
    )
    obs1 = Observation(
        observation_id="OBS-1",
        patient_id="TEST-RETRIAGE-01",
        timestamp=now - timedelta(minutes=15),
        heart_rate=80.0,
        respiratory_rate=16.0,
        systolic_bp=130.0,
        spo2=97.0
    )
    obs2 = Observation(
        observation_id="OBS-2",
        patient_id="TEST-RETRIAGE-01",
        timestamp=now,
        heart_rate=115.0,  # Spiked +35
        respiratory_rate=26.0, # Spiked +10
        systolic_bp=95.0,  # Dropped -35
        spo2=91.0          # Dropped -6%
    )
    patient.observations = [obs2, obs1]

    needs_reassessment, reasons, attention_score = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassessment is True
    assert len(reasons) >= 3
    assert attention_score > 150

def test_overdue_wait_time():
    # Patient with HIGH priority waiting over 15 minutes
    patient = Patient(
        patient_id="TEST-OVERDUE-01",
        name="Test Overdue",
        current_priority="HIGH",
        waiting_minutes=25,
        observations=[]
    )
    needs_reassessment, reasons, attention_score = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassessment is True
    assert any("Overdue" in r for r in reasons)

def test_pt021_initial_state_is_baseline_and_overdue_only():
    """Verifies that PT-021 starts with baseline vitals only and is flagged for overdue wait-time without fake deterioration."""
    now = datetime.now(timezone.utc)
    patient = Patient(
        patient_id="PT-021",
        name="Patient Phi (Synthetic - Killer Demo Deterioration)",
        current_priority="MODERATE",
        waiting_minutes=28
    )
    obs_baseline = Observation(
        observation_id="OBS-21-1",
        patient_id="PT-021",
        timestamp=now - timedelta(minutes=28),
        heart_rate=86.0,
        respiratory_rate=18.0,
        systolic_bp=138.0,
        diastolic_bp=88.0,
        spo2=96.0,
        temperature_c=36.9
    )
    patient.observations = [obs_baseline]

    needs_reassess, reasons, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassess is True
    # Must have overdue trigger (28m > 15m window)
    assert any("Overdue for clinical reassessment: Waiting 28m" in r for r in reasons)
    # Must NOT have any deterioration flags before injection
    assert not any("Deterioration:" in r for r in reasons)

def test_pt021_lifecycle_simulation_injection():
    """Verifies that when a newer observation is injected, the deterioration event triggers with exact vital deltas."""
    now = datetime.now(timezone.utc)
    patient = Patient(
        patient_id="PT-021",
        name="Patient Phi (Synthetic - Killer Demo Deterioration)",
        current_priority="MODERATE",
        waiting_minutes=28
    )
    obs_baseline = Observation(
        observation_id="OBS-21-1",
        patient_id="PT-021",
        timestamp=now - timedelta(minutes=28),
        heart_rate=86.0,
        respiratory_rate=18.0,
        systolic_bp=138.0,
        diastolic_bp=88.0,
        spo2=96.0,
        temperature_c=36.9
    )
    obs_deteriorated = Observation(
        observation_id="OBS-21-2",
        patient_id="PT-021",
        timestamp=now,
        heart_rate=118.0,
        respiratory_rate=26.0,
        systolic_bp=98.0,
        diastolic_bp=62.0,
        spo2=91.0,
        temperature_c=37.3
    )
    # Newest observation first
    patient.observations = [obs_deteriorated, obs_baseline]

    needs_reassess, reasons, attention_score = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassess is True
    # Both overdue and deterioration triggers must be active
    assert any("Overdue for clinical reassessment" in r for r in reasons)
    assert any("Deterioration: SpO2 dropped from 96.0% to 91.0% (-5.0%)" in r for r in reasons)
    assert any("Deterioration: Heart rate spiked from 86.0 to 118.0 bpm (+32.0 bpm)" in r for r in reasons)
    assert any("Deterioration: Systolic BP fell from 138.0 to 98.0 mmHg (-40.0 mmHg)" in r for r in reasons)
    assert any("Deterioration: Respiratory rate increased from 18.0 to 26.0/min" in r for r in reasons)
    assert attention_score >= 100

def test_advance_time_alone_does_not_trigger_deterioration_until_injected():
    """Proves that advancing waiting time from 28m to 43m to 60m keeps overdue status without creating fake deterioration events."""
    now = datetime.now(timezone.utc)
    patient = Patient(
        patient_id="PT-021",
        name="Patient Phi",
        current_priority="MODERATE",
        waiting_minutes=28
    )
    obs_baseline = Observation(
        observation_id="OBS-21-1",
        patient_id="PT-021",
        timestamp=now - timedelta(minutes=28),
        heart_rate=86.0,
        respiratory_rate=18.0,
        systolic_bp=138.0,
        diastolic_bp=88.0,
        spo2=96.0,
        temperature_c=36.9
    )
    patient.observations = [obs_baseline]

    # At 28 minutes: overdue only, NO deterioration
    needs_reassess, reasons_28, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassess is True
    assert any("Overdue for clinical reassessment" in r for r in reasons_28)
    assert not any("Deterioration:" in r for r in reasons_28)

    # Advance time by +15 minutes (to 43 minutes)
    patient.waiting_minutes = 43
    needs_reassess_43, reasons_43, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassess_43 is True
    assert any("Waiting 43m" in r for r in reasons_43)
    assert not any("Deterioration:" in r for r in reasons_43)

    # Advance time to 60 minutes
    patient.waiting_minutes = 60
    needs_reassess_60, reasons_60, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassess_60 is True
    assert any("Waiting 60m" in r for r in reasons_60)
    assert not any("Deterioration:" in r for r in reasons_60)

    # NOW inject actual worsening observation (OBS-2)
    obs_deteriorated = Observation(
        observation_id="OBS-21-2",
        patient_id="PT-021",
        timestamp=now,
        heart_rate=118.0,
        respiratory_rate=26.0,
        systolic_bp=98.0,
        diastolic_bp=62.0,
        spo2=91.0,
        temperature_c=37.3
    )
    patient.observations.insert(0, obs_deteriorated)

    # Now deterioration event MUST be triggered
    needs_reassess_post, reasons_post, _ = reassessment_monitor.evaluate_patient_reassessment(patient)
    assert needs_reassess_post is True
    assert any("Deterioration: SpO2 dropped from 96.0% to 91.0%" in r for r in reasons_post)
    assert any("Deterioration: Heart rate spiked from 86.0 to 118.0 bpm" in r for r in reasons_post)


