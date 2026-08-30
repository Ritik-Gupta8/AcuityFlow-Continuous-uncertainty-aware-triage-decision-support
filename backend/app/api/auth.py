"""
AcuityFlow AI Authentication Endpoints.
Provides user login (JWT issuance) and authenticated session verification (/auth/me).
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import User, AuditEvent
from app.schemas.schemas import LoginRequest, TokenResponse, UserOut
from app.core.security import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates username and password against PBKDF2 hash and returns an HS256 JWT access token.
    Logs an audit event for login.
    """
    user = db.query(User).filter(User.username == req.username.strip().lower()).first()
    
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )
    
    token = create_access_token({
        "sub": user.user_id,
        "username": user.username,
        "role": user.role
    })
    
    # Audit log the authentication event
    login_audit = AuditEvent(
        audit_id=f"AUD-LOGIN-{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(timezone.utc),
        actor_id=user.user_id,
        actor_role=user.role,
        event_type="login",
        patient_id=None,
        recommendation=None,
        confidence=None,
        decision="LOGIN_SUCCESS",
        override_reason=None,
        details={"username": user.username, "role": user.role}
    )
    db.add(login_audit)
    db.commit()
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username,
        role=user.role
    )

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Returns profile for currently authenticated user."""
    return current_user
