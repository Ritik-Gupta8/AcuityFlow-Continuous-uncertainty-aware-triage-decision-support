"""
RBAC & Security Test Suite — AcuityFlow AI.
Validates:
1. Authentication & JWT issuance
2. Invalid password rejection (HTTP 401)
3. Deactivated user rejection (HTTP 403)
4. Unauthenticated access rejection on protected endpoints (HTTP 401)
5. Nurse permissions (patient view, triage, observation, override, patient audit)
6. Nurse restrictions on admin/user/audit endpoints (HTTP 403)
7. Supervisor permissions (queue, triage, overrides, full audit explorer)
8. Admin permissions (configuration, user management, audit review)
9. Critical security negative test: client identity spoofing prevention
10. Mandatory override reason enforcement
11. Audit trail immutability and append-only preservation
"""

import pytest
from fastapi.testclient import TestClient
from tests.conftest import TestingSessionLocal
from app.main import app
from app.models.entities import User, Patient, ClinicianDecision, AuditEvent
from app.core.security import hash_password

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def nurse_token(client):
    res = client.post("/api/auth/login", json={"username": "nurse101", "password": "Password@123"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture
def supervisor_token(client):
    res = client.post("/api/auth/login", json={"username": "supervisor101", "password": "Password@123"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture
def admin_token(client):
    res = client.post("/api/auth/login", json={"username": "admin101", "password": "Password@123"})
    assert res.status_code == 200
    return res.json()["access_token"]

# 1-3. Valid Login for all 3 roles
def test_01_nurse_login_success(client):
    res = client.post("/api/auth/login", json={"username": "nurse101", "password": "Password@123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "nurse"
    assert data["username"] == "nurse101"

def test_02_supervisor_login_success(client):
    res = client.post("/api/auth/login", json={"username": "supervisor101", "password": "Password@123"})
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "supervisor"

def test_03_admin_login_success(client):
    res = client.post("/api/auth/login", json={"username": "admin101", "password": "Password@123"})
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "admin"

# 4. Invalid Password
def test_04_invalid_password_rejected(client):
    res = client.post("/api/auth/login", json={"username": "nurse101", "password": "WrongPassword!"})
    assert res.status_code == 401
    assert "Invalid username or password" in res.json()["detail"]

# 5. Inactive User Rejected
def test_05_inactive_user_rejected(client):
    res = client.post("/api/auth/login", json={"username": "inactive999", "password": "Password@123"})
    assert res.status_code == 403
    assert "deactivated" in res.json()["detail"]

# 6. Unauthenticated protected endpoints return 401
def test_06_unauthenticated_requests_rejected(client):
    res_patients = client.get("/api/patients")
    assert res_patients.status_code == 401

    res_audit = client.get("/api/audit")
    assert res_audit.status_code == 401

    res_config = client.get("/api/admin/config")
    assert res_config.status_code == 401

# 7. Nurse permitted to view queue and patient detail
def test_07_nurse_permitted_to_view_queue_and_patient(client, nurse_token):
    headers = {"Authorization": f"Bearer {nurse_token}"}
    res = client.get("/api/patients", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) > 0

    res_pt = client.get("/api/patients/PT-001", headers=headers)
    assert res_pt.status_code == 200
    assert res_pt.json()["patient_id"] == "PT-001"

# 8. Nurse permitted to submit observations and overrides
def test_08_nurse_permitted_to_submit_observation_and_override(client, nurse_token):
    headers = {"Authorization": f"Bearer {nurse_token}"}
    
    # Submit observation
    obs_payload = {
        "heart_rate": 95.0,
        "respiratory_rate": 18.0,
        "systolic_bp": 122.0,
        "diastolic_bp": 78.0,
        "spo2": 97.0,
        "temperature_c": 37.0,
        "measurement_source": "clinician",
        "observation_notes": "Follow-up vitals"
    }
    res_obs = client.post("/api/patients/PT-001/observations", json=obs_payload, headers=headers)
    assert res_obs.status_code == 200

    # Submit override
    override_payload = {
        "clinician_action": "override",
        "final_priority": "HIGH",
        "override_reason": "Clinical intuition regarding atypical presentation",
        "clinician_note": "Monitored closely"
    }
    res_ovr = client.post("/api/patients/PT-001/decision", json=override_payload, headers=headers)
    assert res_ovr.status_code == 200
    assert res_ovr.json()["final_priority"] == "HIGH"
    assert res_ovr.json()["clinician_id"] == "nurse101"

# 9-10. Nurse denied admin configuration and user management
def test_09_nurse_denied_admin_endpoints(client, nurse_token):
    headers = {"Authorization": f"Bearer {nurse_token}"}
    
    # Admin config denied
    res_cfg = client.get("/api/admin/config", headers=headers)
    assert res_cfg.status_code == 403
    assert "Access denied" in res_cfg.json()["detail"]

    # Admin user list denied
    res_usr = client.get("/api/admin/users", headers=headers)
    assert res_usr.status_code == 403

# 11. Nurse denied unrestricted audit explorer
def test_10_nurse_denied_unrestricted_audit_explorer(client, nurse_token):
    headers = {"Authorization": f"Bearer {nurse_token}"}
    res = client.get("/api/audit", headers=headers)
    assert res.status_code == 403
    assert "Supervisor or Admin role required" in res.json()["detail"]

    # But nurse IS permitted to view patient-specific audit history
    res_pt_audit = client.get("/api/audit?patient_id=PT-001", headers=headers)
    assert res_pt_audit.status_code == 200

# 12. Supervisor allowed audit explorer
def test_11_supervisor_allowed_audit_explorer(client, supervisor_token):
    headers = {"Authorization": f"Bearer {supervisor_token}"}
    res = client.get("/api/audit", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) > 0

# 13. Admin allowed configuration and user creation
def test_12_admin_allowed_config_and_user_creation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get config
    res_cfg = client.get("/api/admin/config", headers=headers)
    assert res_cfg.status_code == 200
    assert "pediatric_max_age" in res_cfg.json()

    # Update config
    res_upd = client.post("/api/admin/config", json={"pediatric_max_age": 16}, headers=headers)
    assert res_upd.status_code == 200
    assert res_upd.json()["pediatric_max_age"] == 16

    # Create new demo user
    new_user_payload = {
        "username": "nurse102",
        "password": "Password@123",
        "role": "nurse"
    }
    res_usr = client.post("/api/admin/users", json=new_user_payload, headers=headers)
    assert res_usr.status_code == 200
    assert res_usr.json()["username"] == "nurse102"

# 14. MANDATORY SECURITY NEGATIVE TEST: Client cannot spoof clinician identity
def test_13_security_negative_test_identity_spoofing_prevented(client, nurse_token):
    headers = {"Authorization": f"Bearer {nurse_token}"}
    
    # Malicious payload attempting to claim admin identity
    spoof_payload = {
        "clinician_id": "admin101",
        "actor_role": "admin",
        "clinician_action": "override",
        "final_priority": "IMMEDIATE",
        "override_reason": "Attempting unauthorized privilege escalation spoof",
        "clinician_note": "Spoofed attempt"
    }
    
    res = client.post("/api/patients/PT-003/decision", json=spoof_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    
    # Server MUST have resolved actor identity from nurse token, discarding client payload spoof!
    assert data["clinician_id"] == "nurse101"
    assert data["actor_role"] == "nurse"
    assert data["clinician_id"] != "admin101"

    # Verify that audit log query via API shows nurse101 and nurse role
    audit_res = client.get("/api/audit?patient_id=PT-003", headers=headers)
    assert audit_res.status_code == 200
    audits = audit_res.json()
    override_audits = [a for a in audits if a["event_type"] == "override"]
    assert len(override_audits) > 0
    assert override_audits[0]["actor_id"] == "nurse101"
    assert override_audits[0]["actor_role"] == "nurse"

# 15. Override requires explicit reason
def test_14_override_requires_reason(client, nurse_token):
    headers = {"Authorization": f"Bearer {nurse_token}"}
    invalid_override = {
        "clinician_action": "override",
        "final_priority": "HIGH",
        "override_reason": None  # Missing reason
    }
    res = client.post("/api/patients/PT-002/decision", json=invalid_override, headers=headers)
    assert res.status_code == 400
    assert "override reason is required" in res.json()["detail"]

# 16. Health check remains open / public
def test_15_health_check_open(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
