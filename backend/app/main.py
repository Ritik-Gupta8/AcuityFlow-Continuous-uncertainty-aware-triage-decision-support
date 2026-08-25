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

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed database on startup if empty
db = SessionLocal()
try:
    seed_database(db)
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
app.include_router(patients_router, prefix="/api")
app.include_router(overrides_router, prefix="/api")
app.include_router(reassessment_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(audit_router, prefix="/api")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "disclaimer": settings.PROTOTYPE_DISCLAIMER
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to AcuityFlow AI Decision Support API",
        "docs": "/docs",
        "disclaimer": settings.PROTOTYPE_DISCLAIMER
    }
