"""
Authentication REST API — Stage E.3 & E.4

Endpoints:
  POST /auth/login   — validate user_id + passkey, check brute force lockout, issue JWT, write audit log
  POST /auth/logout  — invalidate session on client, write audit log
  GET  /auth/me      — return current employee info from validated JWT
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import verify_passkey, create_access_token
from app.db.models.employee import EmployeeRecord
from app.db.models.audit_log import AuditLogRecord

logger = logging.getLogger("app.api.v1.endpoints.auth")
router = APIRouter()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

# ── Request / Response schemas ───────────────────────────────────────────────

class LoginRequest(BaseModel):
    user_id: str
    passkey: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class MeResponse(BaseModel):
    user_id: str
    role: str
    account_status: str
    last_login_at: Any = None


# ── Helper ───────────────────────────────────────────────────────────────────

def _write_audit(
    db: Session,
    action: str,
    request: Request,
    user_id: str | None = None,
) -> None:
    """Append an immutable audit log entry."""
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
        logger.warning(f"[_write_audit] Failed to write audit log ({action}): {exc}")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(
    *,
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Authenticate an enterprise employee.

    Validates user_id + passkey against the pre-provisioned accounts table.
    Locks account after 5 consecutive failed attempts.
    """
    logger.info(f"[login] Login attempt for user_id='{payload.user_id}'")

    employee = db.query(EmployeeRecord).filter(
        EmployeeRecord.user_id == payload.user_id
    ).first()

    now = datetime.now(timezone.utc)

    # If employee exists, check lockout status
    if employee:
        # Check if account is temporarily locked via locked_until
        if employee.locked_until:
            if employee.locked_until > now:
                # Still locked
                locked_remaining = int((employee.locked_until - now).total_seconds())
                logger.warning(f"[login] Login rejected: user_id='{payload.user_id}' is temporarily locked for {locked_remaining}s")
                _write_audit(db, "login_failed", request, user_id=payload.user_id)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account is locked. Try again later."
                )
            else:
                # Lock expired, reset status
                employee.locked_until = None
                if employee.account_status == "locked":
                    employee.account_status = "active"
                db.add(employee)
                db.commit()

        if employee.account_status != "active":
            logger.warning(f"[login] Login rejected: user_id='{payload.user_id}' status is '{employee.account_status}'")
            _write_audit(db, "login_failed", request, user_id=payload.user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {employee.account_status}"
            )

    # Perform verification
    if not employee or not verify_passkey(payload.passkey, employee.passkey_hash):
        logger.warning(f"[login] Failed credentials for user_id='{payload.user_id}'")
        _write_audit(db, "login_failed", request, user_id=payload.user_id)

        if employee:
            employee.failed_login_attempts += 1
            if employee.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                employee.account_status = "locked"
                employee.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
                logger.warning(f"[login] User ID '{payload.user_id}' locked out due to {MAX_FAILED_ATTEMPTS} failed attempts.")
                _write_audit(db, "account_locked", request, user_id=payload.user_id)
            db.add(employee)
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Login success: reset counters
    employee.failed_login_attempts = 0
    employee.locked_until = None
    employee.last_login_at = now
    db.add(employee)
    db.commit()

    # Issue JWT
    token = create_access_token(user_id=employee.user_id, role=employee.role)

    _write_audit(db, "login_success", request, user_id=employee.user_id)
    logger.info(f"[login] Successful login for user_id='{employee.user_id}' role='{employee.role}'")

    return TokenResponse(
        access_token=token,
        user_id=employee.user_id,
        role=employee.role,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    *,
    request: Request,
    current_user: EmployeeRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Terminate the authenticated session.
    """
    logger.info(f"[logout] User '{current_user.user_id}' logging out")
    _write_audit(db, "logout", request, user_id=current_user.user_id)
    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: EmployeeRecord = Depends(get_current_user),
) -> Any:
    """Return the profile of the currently authenticated employee."""
    return MeResponse(
        user_id=current_user.user_id,
        role=current_user.role,
        account_status=current_user.account_status,
        last_login_at=current_user.last_login_at,
    )


class AutoLogoutRequest(BaseModel):
    token: str
    user_id: str


@router.post("/auto-logout", status_code=status.HTTP_200_OK)
def auto_logout(
    *,
    request: Request,
    payload: AutoLogoutRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    轻量级 Beacon 自动登出处理器。当浏览器标签页关闭时，
    前端发送 sendBeacon 请求，后端写入 auto_logout 审计日志。
    """
    logger.info(f"[auto_logout] Browser tab closed for user_id='{payload.user_id}'")
    _write_audit(db, "auto_logout", request, user_id=payload.user_id)
    return {"detail": "Auto logout recorded successfully."}
