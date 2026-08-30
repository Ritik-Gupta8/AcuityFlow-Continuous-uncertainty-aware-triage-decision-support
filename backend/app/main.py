"""
AcuityFlow AI Backend Entrypoint.
Continuous, uncertainty-aware triage decision-support prototype.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.data.seed_cases import seed_database
from app.api.patients import router as patients_router
from app.api.overrides import router as overrides_router
from app.api.reassessment import router as reassessment_router
from app.api.simulation import router as simulation_router
from app.api.audit import router as audit_router
from app.api.nlp import router as nlp_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router

from datetime import datetime, timezone
import uuid
from app.ml.risk_model import risk_engine
from app.models.entities import AuditEvent

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed database on startup if empty & log fallback audit event if artifacts missing
db = SessionLocal()
try:
    seed_database(db)
    if not risk_engine.model_available:
        existing_log = db.query(AuditEvent).filter(AuditEvent.event_type == "model_artifact_missing_fallback").first()
        if not existing_log:
            audit = AuditEvent(
                audit_id=f"AUD-STARTUP-FALLBACK",
                timestamp=datetime.now(timezone.utc),
                actor_id="system",
                actor_role="system",
                event_type="model_artifact_missing_fallback",
                patient_id=None,
                recommendation=None,
                confidence=None,
                decision="FALLBACK_MODE_ACTIVE",
                override_reason=None,
                details={
                    "model_status": "FALLBACK",
                    "model_available": False,
                    "model_source": "deterministic-fallback",
                    "message": "Calibrated ML artifact unavailable. System operating on deterministic safety fallback."
                },
                policy_version="v2.0.0-prototype",
                model_version="fallback-parametric-baseline"
            )
            db.add(audit)
            db.commit()
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(auth_router, prefix="")  # Direct /auth/login and /auth/me
app.include_router(admin_router, prefix="/api")
app.include_router(patients_router, prefix="/api")
app.include_router(overrides_router, prefix="/api")
app.include_router(reassessment_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(nlp_router, prefix="/api")
app.include_router(nlp_router, prefix="")  # Supports direct POST /nlp/extract-symptoms as well

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "model_status": risk_engine.model_status,
        "model_available": risk_engine.model_available,
        "model_source": risk_engine.model_source,
        "disclaimer": settings.PROTOTYPE_DISCLAIMER
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to AcuityFlow AI Decision Support API",
        "docs": "/docs",
        "disclaimer": settings.PROTOTYPE_DISCLAIMER
    }
