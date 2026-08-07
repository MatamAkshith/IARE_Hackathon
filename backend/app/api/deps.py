import logging
from typing import Generator, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories import (
    domain_repo,
    scan_repo,
    campaign_repo,
    feature_repo,
    risk_score_repo,
)

logger = logging.getLogger("app.api.deps")
_bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> "EmployeeRecord":  # type: ignore[name-defined]
    """
    FastAPI dependency that validates the Bearer JWT and returns the EmployeeRecord.

    Writes an 'invalid_token' audit log entry on every failed validation.
    On success updates nothing — the login endpoint handles last_login_at.
    """
    from app.core.security import decode_access_token
    from app.db.models.employee import EmployeeRecord
    from app.db.models.audit_log import AuditLogRecord

    def _write_audit(action: str, user_id: Optional[str] = None) -> None:
        try:
            entry = AuditLogRecord(
                action=action,
                user_id=user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
            db.add(entry)
            db.commit()
        except Exception as exc:
            logger.warning(f"[get_current_user] Failed to write audit log: {exc}")

    if not credentials or not credentials.credentials:
        _write_audit("invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub", "")
    except JWTError as exc:
        logger.warning(f"[get_current_user] JWT validation failed: {exc}")
        _write_audit("invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employee = db.query(EmployeeRecord).filter(
        EmployeeRecord.user_id == user_id
    ).first()

    if not employee:
        _write_audit("invalid_token", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if employee.account_status != "active":
        _write_audit("invalid_token", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {employee.account_status}",
        )

    return employee
