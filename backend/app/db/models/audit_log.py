"""
AuditLogRecord — Stage E.2

Immutable append-only audit log for all authentication events.
Written by the auth endpoints and the JWT validation dependency.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class AuditLogRecord(Base):
    """Authentication audit log table."""

    __tablename__ = "auth_audit_logs"

    # Action types accepted
    # login_success | login_failed | logout | session_expired | invalid_token
    action = Column(String(64), nullable=False, index=True)

    user_id = Column(String(64), nullable=True, index=True)   # nullable for invalid-token events
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)

    # Event timestamp (server-side, not relying on client clock)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
