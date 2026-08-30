"""
Shared Pytest Fixtures — AcuityFlow AI.
Configures in-memory test database with StaticPool and seeds demo users & patients.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.data.seed_cases import seed_database
from app.models.entities import User, Patient, Observation, TriageResult, ClinicianDecision, AuditEvent
from app.core.security import hash_password

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_shared_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database(db)
    
    # Add inactive user for negative RBAC testing
    if not db.query(User).filter(User.username == "inactive999").first():
        inactive_user = User(
            user_id="usr-inactive-999",
            username="inactive999",
            password_hash=hash_password("Password@123"),
            role="nurse",
            is_active=False
        )
        db.add(inactive_user)
        db.commit()
    db.close()
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client():
    client = TestClient(app)
    res = client.post("/api/auth/login", json={"username": "nurse101", "password": "Password@123"})
    if res.status_code == 200:
        client.headers["Authorization"] = f"Bearer {res.json()['access_token']}"
    return client
