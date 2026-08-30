"""
AcuityFlow AI Administrative Endpoints.
Accessible ONLY to users with the 'admin' role.
Demonstrates server-side RBAC enforcement and configuration audit logging.
"""

import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import require_role, hash_password
from app.models.entities import User, AuditEvent
from app.schemas.schemas import AdminConfigOut, AdminConfigUpdate, UserOut, UserCreate

router = APIRouter(prefix="/admin", tags=["Administrative & Configuration Management"])

@router.get("/config", response_model=AdminConfigOut)
def get_system_config(current_user: User = Depends(require_role(["admin"]))):
    """Retrieves operational and population configuration. Admin role required."""
    return AdminConfigOut(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        pediatric_max_age=settings.PEDIATRIC_MAX_AGE,
        geriatric_min_age=settings.GERIATRIC_MIN_AGE,
        min_confidence_threshold=settings.MIN_CONFIDENCE_THRESHOLD,
        min_completeness_threshold=settings.MIN_COMPLETENESS_THRESHOLD,
        disclaimer=settings.PROTOTYPE_DISCLAIMER
    )

@router.post("/config", response_model=AdminConfigOut)
def update_system_config(
    update_req: AdminConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Updates illustrative demographic boundaries and logs a config_change audit event. Admin role required."""
    changes = {}
    if update_req.pediatric_max_age is not None:
        old_ped = settings.PEDIATRIC_MAX_AGE
        settings.PEDIATRIC_MAX_AGE = update_req.pediatric_max_age
        changes["pediatric_max_age"] = {"old": old_ped, "new": update_req.pediatric_max_age}
        
    if update_req.geriatric_min_age is not None:
        old_ger = settings.GERIATRIC_MIN_AGE
        settings.GERIATRIC_MIN_AGE = update_req.geriatric_min_age
        changes["geriatric_min_age"] = {"old": old_ger, "new": update_req.geriatric_min_age}
    
    # Audit log the configuration change
    config_audit = AuditEvent(
        audit_id=f"AUD-CFG-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=current_user.user_id,
        actor_role=current_user.role,
        event_type="config_change",
        patient_id=None,
        recommendation=None,
        confidence=None,
        decision="CONFIG_UPDATED",
        override_reason="Admin configuration update",
        details=changes
    )
    db.add(config_audit)
    db.commit()
    
    return AdminConfigOut(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        pediatric_max_age=settings.PEDIATRIC_MAX_AGE,
        geriatric_min_age=settings.GERIATRIC_MIN_AGE,
        min_confidence_threshold=settings.MIN_CONFIDENCE_THRESHOLD,
        min_completeness_threshold=settings.MIN_COMPLETENESS_THRESHOLD,
        disclaimer=settings.PROTOTYPE_DISCLAIMER
    )

@router.get("/users", response_model=List[UserOut])
def list_system_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Lists all registered prototype users. Admin role required."""
    return db.query(User).all()

@router.post("/users", response_model=UserOut)
def create_system_user(
    user_req: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Creates a new prototype user with hashed password. Admin role required."""
    existing = db.query(User).filter(User.username == user_req.username.strip().lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    
    new_user = User(
        user_id=f"usr-{uuid.uuid4().hex[:8]}",
        username=user_req.username.strip().lower(),
        password_hash=hash_password(user_req.password),
        role=user_req.role.lower(),
        is_active=True
    )
    db.add(new_user)
    
    audit = AuditEvent(
        audit_id=f"AUD-USR-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=current_user.user_id,
        actor_role=current_user.role,
        event_type="user_created",
        patient_id=None,
        recommendation=None,
        confidence=None,
        decision="USER_CREATED",
        override_reason=None,
        details={"created_user": new_user.username, "role": new_user.role}
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)
    return new_user
