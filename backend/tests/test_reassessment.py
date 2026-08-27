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
