"""
EmployeeRecord — Stage E.1 & E.2

Stores pre-provisioned enterprise employee accounts.
Public registration is strictly disabled.  Only accounts seeded by the
system administrator (via seed_employees.py) can log in.
"""

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.db.base_class import Base


class EmployeeRecord(Base):
    """Enterprise employee account table."""

    __tablename__ = "employees"

    # Override id PK with a string user_id (e.g. "analyst01")
    id = None  # type: ignore[assignment]  # drop inherited integer PK
    user_id = Column(String(64), primary_key=True, index=True, nullable=False)

    passkey_hash = Column(String(256), nullable=False)
    role = Column(String(64), nullable=False, default="analyst")

    # account_status: "active" | "disabled" | "locked"
    account_status = Column(String(32), nullable=False, default="active")

    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Stage E.4: Brute-Force Protection
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Standard audit timestamps (not inherited because we overrode id)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
