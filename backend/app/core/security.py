"""
ThreatLens Security Utilities — Stage E.3 & E.4

Provides passkey hashing (bcrypt), JWT generation / validation,
and backend role-based access control (RBAC) dependency classes.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.api.deps import get_current_user
from app.db.models.employee import EmployeeRecord

logger = logging.getLogger("app.core.security")

# ── Passkey hashing ──────────────────────────────────────────────────────────

def hash_passkey(plain: str) -> str:
    """Return a bcrypt hash of the given plaintext passkey."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_passkey(plain: str, hashed: str) -> bool:
    """Return True when *plain* matches the stored bcrypt *hashed* value."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT generation & validation ──────────────────────────────────────────────
def create_access_token(
    user_id: str,
    role: str,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Create a signed HS256 JWT.

    Claims:
      sub   — user_id (subject)
      role  — employee role string
      iat   — issued-at (UTC)
      exp   — expiry (UTC, configured via JWT_EXPIRE_MINUTES)
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload: dict = {
        "sub": user_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    logger.debug(f"[create_access_token] Issued token for user_id='{user_id}' role='{role}'")
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT.

    Raises:
        JWTError — if signature is invalid, token is expired, or malformed.

    Returns:
        The decoded payload dict (including 'sub' and 'role').
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


# ── Role-Based Access Control (RBAC) Dependency ──────────────────────────────

class RoleChecker:
    """
    FastAPI dependency to authorize requests based on a list of permitted roles.
    Returns 403 Forbidden if the user's role is not in the list.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: EmployeeRecord = Depends(get_current_user)
    ) -> EmployeeRecord:
        if current_user.role not in self.allowed_roles:
            logger.warning(
                f"[RBAC] Access denied for user_id='{current_user.user_id}' "
                f"with role='{current_user.role}'. Required one of: {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this resource"
            )
        return current_user
