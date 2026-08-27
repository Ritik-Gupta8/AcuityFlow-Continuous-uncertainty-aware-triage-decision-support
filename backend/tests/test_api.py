"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_get_seeded_patients():
    res = client.get("/api/patients")
    assert res.status_code == 200
    patients = res.json()
    assert len(patients) >= 24
    patient_ids = [p["patient_id"] for p in patients]
    assert "PT-001" in patient_ids
    assert "PT-005" in patient_ids
    assert "PT-011" in patient_ids
    assert "PT-019" in patient_ids
    assert "PT-021" in patient_ids

def test_clinician_override_and_audit():
    # Submit an override on PT-001
    override_payload = {
        "clinician_id": "nurse-test",
        "actor_role": "nurse",
        "clinician_action": "override",
        "final_priority": "MODERATE",
        "override_reason": "Additional clinical context from physical examination",
        "clinician_note": "Patient appears more stable than initial score suggested."
    }
    res = client.post("/api/patients/PT-001/decision", json=override_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["final_priority"] == "MODERATE"
    assert data["override_reason"] == "Additional clinical context from physical examination"

    # Verify override is persisted in audit trail
    audit_res = client.get("/api/audit?patient_id=PT-001")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) > 0
    assert any(l["event_type"] == "override" for l in logs)

def test_advance_time_simulation():
    res = client.post("/api/simulation/advance-time", json={"minutes": 15})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["advanced_minutes"] == 15

def test_surge_toggle_simulation():
    res = client.post("/api/simulation/surge", json={"surge_active": True})
    assert res.status_code == 200
    data = res.json()
    assert data["surge_active"] is True
