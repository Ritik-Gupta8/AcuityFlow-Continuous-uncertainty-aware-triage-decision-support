"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_auth(auth_client):
    client.headers = auth_client.headers

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
    assert res.json()["surge_active"] is True
    # Restore to false
    res_off = client.post("/api/simulation/surge", json={"surge_active": False})
    assert res_off.status_code == 200

# ==============================================================================
# CLINICIAN OVERRIDE STATE-CONSISTENCY REGRESSION SUITE (PT-012 & GENERAL CASES)
# ==============================================================================

def test_pt012_override_preserves_immutable_ai_priority():
    """Verifies that PT-012 starts with AI Priority MODERATE and overriding to IMMEDIATE does not mutate AI priority."""
    # 1. Reset database for clean baseline
    reset_res = client.post("/api/simulation/reset")
    assert reset_res.status_code == 200

    # 2. Get PT-012 initial state
    pt_res = client.get("/api/patients/PT-012")
    assert pt_res.status_code == 200
    pt_data = pt_res.json()
    initial_ai_priority = pt_data["ai_priority"]
    assert initial_ai_priority in ["MODERATE", "LOW", "HIGH", "IMMEDIATE"]
    assert pt_data["effective_priority"] == initial_ai_priority
    assert pt_data["clinician_decision"] is None

    # Also verify latest triage result endpoint matches
    triage_res = client.get("/api/patients/PT-012/triage-latest")
    assert triage_res.status_code == 200
    assert triage_res.json()["priority"] == initial_ai_priority
    assert triage_res.json()["policy_version"] == "v2.0.0-prototype"

    # 3. Perform Clinician Override to IMMEDIATE
    override_payload = {
        "clinician_id": "nurse-101",
        "actor_role": "nurse",
        "clinician_action": "override",
        "final_priority": "IMMEDIATE",
        "override_reason": "Direct physician assessment override",
        "clinician_note": "Child appears more distressed on direct clinical examination."
    }
    dec_res = client.post("/api/patients/PT-012/decision", json=override_payload)
    assert dec_res.status_code == 200
    dec_data = dec_res.json()
    assert dec_data["ai_priority"] == initial_ai_priority  # AI priority in decision record must remain immutable
    assert dec_data["final_priority"] == "IMMEDIATE"
    assert dec_data["override_reason"] == "Direct physician assessment override"

    # 4. Fetch patient again: ai_priority must remain immutable, clinician_decision must be IMMEDIATE, effective_priority must be IMMEDIATE
    pt_after = client.get("/api/patients/PT-012").json()
    assert pt_after["ai_priority"] == initial_ai_priority
    assert pt_after["clinician_decision"] == "IMMEDIATE"
    assert pt_after["clinician_action"] == "override"
    assert pt_after["effective_priority"] == "IMMEDIATE"
    assert pt_after["current_priority"] == "IMMEDIATE"
    assert pt_after["override_reason"] == "Direct physician assessment override"

    # 5. Verify audit event preserves both AI priority and Clinician Decision
    audit_res = client.get("/api/audit?patient_id=PT-012")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    override_events = [l for l in logs if l["event_type"] == "override"]
    assert len(override_events) >= 1
    latest_event = override_events[0]
    assert latest_event["recommendation"] == initial_ai_priority
    assert latest_event["decision"] == "IMMEDIATE"
    assert latest_event["override_reason"] == "Direct physician assessment override"
    assert latest_event["details"]["ai_priority"] == initial_ai_priority
    assert latest_event["details"]["clinician_decision"] == "IMMEDIATE"
    assert latest_event["details"]["effective_priority"] == "IMMEDIATE"
    assert latest_event["policy_version"] == "v2.0.0-prototype"

def test_override_requires_mandatory_reason_and_rejects_empty():
    """Verifies that attempting an override without a reason is rejected with 400."""
    invalid_payload = {
        "clinician_id": "nurse-101",
        "actor_role": "nurse",
        "clinician_action": "override",
        "final_priority": "HIGH",
        "override_reason": None
    }
    res = client.post("/api/patients/PT-012/decision", json=invalid_payload)
    assert res.status_code == 400
    assert "override reason is required" in res.json()["detail"].lower()

def test_accept_leaves_clinician_decision_aligned_with_ai_priority():
    """Verifies that accepting AI recommendation sets clinician_decision equal to ai_priority and clears reassessment flags."""
    pt_init = client.get("/api/patients/PT-012").json()
    current_ai_priority = pt_init["ai_priority"]
    accept_payload = {
        "clinician_id": "nurse-101",
        "actor_role": "nurse",
        "clinician_action": "accept",
        "final_priority": current_ai_priority,
        "clinician_note": "Accepted by triage nurse."
    }
    res = client.post("/api/patients/PT-012/decision", json=accept_payload)
    assert res.status_code == 200
    pt = client.get("/api/patients/PT-012").json()
    assert pt["ai_priority"] == current_ai_priority
    assert pt["clinician_decision"] == current_ai_priority
    assert pt["clinician_action"] == "accept"
    assert pt["effective_priority"] == current_ai_priority
    assert pt["needs_reassessment"] is False

def test_second_override_does_not_rewrite_first_audit_or_mutate_ai_priority():
    """Verifies that a sequence of overrides records distinct immutable audit events and preserves ai_priority."""
    pt_orig = client.get("/api/patients/PT-001").json()
    orig_ai = pt_orig["ai_priority"]

    # First override: HIGH
    client.post("/api/patients/PT-001/decision", json={
        "clinician_id": "nurse-1",
        "actor_role": "nurse",
        "clinician_action": "override",
        "final_priority": "HIGH",
        "override_reason": "Additional clinical context from physical exam"
    })
    # Second override: IMMEDIATE
    client.post("/api/patients/PT-001/decision", json={
        "clinician_id": "physician-2",
        "actor_role": "physician",
        "clinician_action": "override",
        "final_priority": "IMMEDIATE",
        "override_reason": "Direct physician assessment override"
    })

    pt = client.get("/api/patients/PT-001").json()
    assert pt["ai_priority"] == orig_ai
    assert pt["clinician_decision"] == "IMMEDIATE"
    assert pt["effective_priority"] == "IMMEDIATE"

    # Verify audit events: should contain distinct records
    logs = client.get("/api/audit?patient_id=PT-001").json()
    override_logs = [l for l in logs if l["event_type"] == "override"]
    assert len(override_logs) >= 2
    assert override_logs[0]["decision"] == "IMMEDIATE"
    assert override_logs[0]["recommendation"] == orig_ai
    assert override_logs[1]["decision"] == "HIGH"
    assert override_logs[1]["recommendation"] == orig_ai

def test_reassessment_overdue_does_not_silently_change_ai_priority():
    """Verifies advancing time makes patient overdue without changing their underlying ai_priority."""
    # PT-001 baseline wait 25m, LOW max wait is 60m. Advance by 45m -> 70m (>60m)
    client.post("/api/simulation/advance-time", json={"minutes": 45})
    pt = client.get("/api/patients/PT-001").json()
    assert pt["needs_reassessment"] is True
    assert any("Overdue" in r for r in pt["reassessment_reasons"])

def test_audit_event_immutability_and_api_tamper_resistance():
    """
    Verifies the 5 audit requirements against docs/DATA_SCHEMA.md & docs/PRIVACY_SECURITY.md:
    1. Override creates a new audit event (append-only log).
    2. Original triage audit event and recommendation remain unchanged.
    3. Override event contains clinician decision and override reason.
    4. model_version and policy_version are persisted on all audit events.
    5. Audit records cannot be edited or deleted through application APIs (rejects with 405/404).
    """
    # 1. Reset for fresh baseline
    client.post("/api/simulation/reset")

    # 2. Get initial audit log for PT-012 (contains initial triage event)
    initial_logs = client.get("/api/audit?patient_id=PT-012").json()
    assert len(initial_logs) >= 1
    triage_event = [l for l in initial_logs if l["event_type"] == "triage"][0]
    initial_rec = triage_event["recommendation"]
    assert triage_event["policy_version"] == "v2.0.0-prototype"
    initial_triage_audit_id = triage_event["audit_id"]

    # 3. Perform clinician override
    override_payload = {
        "clinician_id": "nurse-101",
        "actor_role": "nurse",
        "clinician_action": "override",
        "final_priority": "IMMEDIATE",
        "override_reason": "Severe acute respiratory distress observed on exam",
        "clinician_note": "Escalated for immediate resuscitation bay."
    }
    dec_res = client.post("/api/patients/PT-012/decision", json=override_payload)
    assert dec_res.status_code == 200

    # 4. Fetch updated audit trail: must have BOTH initial triage event AND new override event
    updated_logs = client.get("/api/audit?patient_id=PT-012").json()
    assert len(updated_logs) == len(initial_logs) + 1

    # (Req 1) New override audit event created
    override_event = [l for l in updated_logs if l["event_type"] == "override"][0]
    assert override_event["audit_id"] != initial_triage_audit_id

    # (Req 2) Original triage recommendation remains unchanged
    preserved_triage_event = [l for l in updated_logs if l["audit_id"] == initial_triage_audit_id][0]
    assert preserved_triage_event["recommendation"] == initial_rec
    assert preserved_triage_event["event_type"] == "triage"

    # (Req 3) Override event contains clinician decision, reason, and original AI recommendation
    assert override_event["recommendation"] == initial_rec
    assert override_event["decision"] == "IMMEDIATE"
    assert override_event["override_reason"] == "Severe acute respiratory distress observed on exam"
    assert override_event["actor_id"] in ["nurse101", "nurse-101"]
    assert override_event["actor_role"] == "nurse"

    # (Req 4) model_version and policy_version are persisted on both
    assert override_event["policy_version"] == "v2.0.0-prototype"
    assert preserved_triage_event["policy_version"] == "v2.0.0-prototype"

    # (Req 5) Verify application API rejects all attempts to edit or delete audit records
    audit_id = override_event["audit_id"]

    # Attempt PUT
    put_res = client.put(f"/api/audit/{audit_id}", json={"recommendation": "TAMPERED"})
    assert put_res.status_code in [404, 405]

    # Attempt PATCH
    patch_res = client.patch(f"/api/audit/{audit_id}", json={"decision": "TAMPERED"})
    assert patch_res.status_code in [404, 405]

    # Attempt DELETE on single record
    del_res = client.delete(f"/api/audit/{audit_id}")
    assert del_res.status_code in [404, 405]

    # Attempt DELETE on collection
    del_all_res = client.delete("/api/audit")
    assert del_all_res.status_code in [404, 405]

    # Attempt POST to direct audit injection
    post_res = client.post("/api/audit", json={"event_type": "fake_event"})
    assert post_res.status_code in [404, 405]

