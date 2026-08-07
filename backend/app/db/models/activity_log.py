"""
ActivityLogRecord — Stage E.5

Immutable append-only activity log for all analyst actions on ThreatLens.
Tracks specific operations: Dashboard access, scans, AI assistant queries, reports.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class ActivityLogRecord(Base):
    """Enterprise analyst activity log table."""

    __tablename__ = "analyst_activity_logs"

    user_id = Column(String(64), nullable=False, index=True)
    
    # Activity types:
    # "dashboard_view" | "scan_create" | "scan_view" | "campaign_view" | "ai_assistant_query" | "report_export"
    activity_type = Column(String(64), nullable=False, index=True)
    
    # Associated indicator or entity ID
    target_identifier = Column(String(256), nullable=True)

    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
