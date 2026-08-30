"""
AcuityFlow AI Core Configuration.
NOTE: All clinical thresholds, scoring weights, and population boundaries defined here
are illustrative prototype rules designed for prototype/educational demonstration.
TODO: CLINICAL VALIDATION REQUIRED - NOT FOR CLINICAL USE.
"""

from typing import Dict, Any, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AcuityFlow AI"
    VERSION: str = "2.0.0-prototype"
    DESCRIPTION: str = "Continuous, uncertainty-aware triage decision-support prototype."
    PROTOTYPE_DISCLAIMER: str = "Concept prototype • Synthetic data • Not for clinical diagnosis or treatment • Clinical validation required."
    
    DATABASE_URL: str = "sqlite:///./acuityflow.db"

    # Authentication & JWT Configuration (Prototype defaults)
    JWT_SECRET_KEY: str = "acuityflow-prototype-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 120
    
    # Population boundaries (Illustrative prototype assumptions)
    # TODO: CLINICAL VALIDATION REQUIRED
    PEDIATRIC_MAX_AGE: int = 17
    GERIATRIC_MIN_AGE: int = 65
    
    # Vital normal/critical ranges (Illustrative prototype thresholds)
    # TODO: CLINICAL VALIDATION REQUIRED
    VITAL_THRESHOLDS: Dict[str, Dict[str, Any]] = {
        "adult": {
            "hr_critical_high": 130,
            "hr_warning_high": 100,
            "hr_warning_low": 50,
            "hr_critical_low": 40,
            "rr_critical_high": 30,
            "rr_warning_high": 22,
            "rr_warning_low": 10,
            "rr_critical_low": 8,
            "spo2_critical_low": 90,
            "spo2_warning_low": 94,
            "sys_bp_critical_high": 180,
            "sys_bp_warning_high": 140,
            "sys_bp_warning_low": 90,
            "sys_bp_critical_low": 80,
            "temp_critical_high": 39.5,
            "temp_warning_high": 38.0,
            "temp_warning_low": 35.5,
        },
        "pediatric": {
            "hr_critical_high": 160,
            "hr_warning_high": 130,
            "hr_warning_low": 70,
            "hr_critical_low": 55,
            "rr_critical_high": 40,
            "rr_warning_high": 30,
            "rr_warning_low": 15,
            "rr_critical_low": 12,
            "spo2_critical_low": 92,
            "spo2_warning_low": 95,
            "sys_bp_critical_high": 140,
            "sys_bp_warning_high": 120,
            "sys_bp_warning_low": 80,
            "sys_bp_critical_low": 70,
            "temp_critical_high": 39.0,
            "temp_warning_high": 38.0,
            "temp_warning_low": 36.0,
        },
        "geriatric": {
            "hr_critical_high": 120,
            "hr_warning_high": 95,
            "hr_warning_low": 50,
            "hr_critical_low": 40,
            "rr_critical_high": 28,
            "rr_warning_high": 22,
            "rr_warning_low": 10,
            "rr_critical_low": 8,
            "spo2_critical_low": 91,
            "spo2_warning_low": 94,
            "sys_bp_critical_high": 180,
            "sys_bp_warning_high": 150,
            "sys_bp_warning_low": 95,
            "sys_bp_critical_low": 85,
            "temp_critical_high": 38.5,
            "temp_warning_high": 37.8,
            "temp_warning_low": 35.0,
        }
    }
    
    # Priority Risk Bands (Illustrative demo bands 0-100)
    # TODO: CLINICAL VALIDATION REQUIRED
    RISK_BANDS: Dict[str, tuple[int, int]] = {
        "LOW": (0, 24),
        "MODERATE": (25, 49),
        "HIGH": (50, 74),
        "IMMEDIATE": (75, 100)
    }
    
    # Reassessment Wait Time Thresholds in minutes (Illustrative prototype policy)
    # TODO: CLINICAL VALIDATION REQUIRED
    REASSESSMENT_WINDOWS_MINUTES: Dict[str, int] = {
        "IMMEDIATE": 0,    # Continuous / Immediate attention
        "HIGH": 15,        # 15 minutes max
        "MODERATE": 15,    # 15 minutes max policy window
        "LOW": 60,         # 60 minutes max
        "REVIEW": 15       # 15 minutes max for clinician review
    }
    
    # Uncertainty thresholds for Escalation Bias
    # TODO: CLINICAL VALIDATION REQUIRED
    MIN_CONFIDENCE_THRESHOLD: float = 65.0       # Confidence below this biases to ESCALATE
    MIN_COMPLETENESS_THRESHOLD: float = 60.0     # Completeness below this on moderate+ risk biases to ESCALATE
    
    # Surge simulation configuration
    SURGE_MULTIPLIER: float = 3.0

    class Config:
        case_sensitive = True

settings = Settings()
