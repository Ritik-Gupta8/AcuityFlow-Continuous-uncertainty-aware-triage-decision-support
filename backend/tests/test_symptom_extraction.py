"""
Tests for Bounded Free-Text Symptom Extraction & Human Confirmation Pipeline.
Verifies that:
1. Valid free-text extraction returns structured symptoms & duration
2. Empty inputs and oversized inputs are rejected with validation errors
3. Dizziness + weakness triggers ambiguity flags
4. Extraction endpoint NEVER returns an autonomous triage priority
5. Structured symptoms can be confirmed/edited before triage evaluation
6. Downstream Safety Gate and ML pipeline remain authoritative
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.symptom_extractor import extract_symptoms_from_narrative
from app.models.entities import Patient, Observation
from app.policy.action_policy import evaluate_patient_triage

client = TestClient(app)

# --- 1. Unit Tests for Extractor Engine ---

def test_symptom_extractor_dizziness_and_weakness():
    text = "Patient reports dizziness and weakness since this morning."
    res = extract_symptoms_from_narrative(text)
    
    assert "Dizziness" in res["symptoms"]
    assert "Weakness" in res["symptoms"]
    assert res["duration_minutes"] == 240
    assert res["is_ambiguous"] is True
    assert res["extracted_by"] == "local-rule-parser"

def test_symptom_extractor_chest_pain_and_sob():
    text = "Patient has severe chest pain and shortness of breath for 2 hours."
    res = extract_symptoms_from_narrative(text)
    
    assert "Chest pain" in res["symptoms"]
    assert "Shortness of breath" in res["symptoms"]
    assert res["duration_minutes"] == 120
    assert res["is_ambiguous"] is False

def test_symptom_extractor_empty_string():
    res = extract_symptoms_from_narrative("")
    assert res["symptoms"] == []
    assert res["duration_minutes"] is None
    assert res["is_ambiguous"] is False

# --- 2. API Endpoint Tests ---

def test_api_extract_symptoms_valid():
    payload = {"text": "Patient reports dizziness and weakness since this morning."}
    res = client.post("/api/nlp/extract-symptoms", json=payload)
    
    assert res.status_code == 200
    data = res.json()
    assert "Dizziness" in data["symptoms"]
    assert "Weakness" in data["symptoms"]
    assert data["duration_minutes"] == 240
    assert data["is_ambiguous"] is True
    
    # Non-negotiable: Never return triage priority from extractor
    assert "priority" not in data
    assert "triage_priority" not in data
    assert "action" not in data

def test_api_extract_symptoms_empty_rejected():
    res = client.post("/api/nlp/extract-symptoms", json={"text": "   "})
    assert res.status_code in [400, 422]

def test_api_extract_symptoms_oversized_rejected():
    huge_text = "Patient " * 200  # > 1000 chars
    res = client.post("/api/nlp/extract-symptoms", json={"text": huge_text})
    assert res.status_code in [400, 422]

# --- 3. End-to-End Pipeline Integration (Human Confirmation & Triage) ---

def test_extracted_symptoms_feed_into_triage_pipeline():
    # 1. Clinician extracts symptoms
    raw_text = "Elderly patient feeling unusually dizzy and weak since morning."
    extraction = extract_symptoms_from_narrative(raw_text)
    assert extraction["is_ambiguous"] is True
    
    # 2. Clinician confirms & edits symptoms into Patient record
    patient = Patient(
        patient_id="TEST-NLP-1",
        name="NLP Test Patient",
        age_years=78,
        population_profile="geriatric",
        history_available=False,
        first_time_patient=True,
        chief_complaint="Dizziness and generalized weakness",
        symptom_text=raw_text,
        observed_cues=extraction["symptoms"]  # ["Dizziness", "Weakness"]
    )
    obs = Observation(observation_id="OBS-NLP-1", heart_rate=98.0, respiratory_rate=20.0, systolic_bp=135.0, spo2=94.0)

    # 3. Triage policy runs on structured inputs
    result = evaluate_patient_triage(patient, obs)
    
    # Ambiguous symptoms + zero history on geriatric presentation must escalate for review
    assert result.priority in ["MODERATE", "HIGH", "REVIEW"]
    assert result.action == "ESCALATE"
    assert any("ambiguous" in f.lower() or "first-time" in f.lower() for f in result.uncertainty_details["contributing_factors"])

def test_patient_symptoms_update_endpoint():
    # Update PT-001 with extracted cues
    payload = {
        "symptoms": ["Dizziness", "Weakness"],
        "narrative_text": "Updated intake note: patient feels dizzy and weak.",
        "duration_minutes": 240
    }
    res = client.post("/api/patients/PT-001/symptoms", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Dizziness" in data["observed_cues"]
    assert "Weakness" in data["observed_cues"]
