"""
Campaign ORM Models — Stage 7.5

Defines CampaignRecord and CampaignMemberRecord tables mapping the Campaign Correlation
Engine's state to SQLAlchemy models for database persistence.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class CampaignRecord(Base):
    """
    ORM model for the campaigns table.
    Stores metadata, status, severity, and aggregated summary details of a campaign.
    """
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    severity = Column(String(32), nullable=False, default="low")
    summary_json = Column(JSON, nullable=True)
    shared_infrastructure_json = Column(JSON, nullable=True)

    # Relationships
    members = relationship(
        "CampaignMemberRecord",
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class CampaignMemberRecord(Base):
    """
    ORM model for the campaign_members table.
    Stores indicator URL/IP associations and the evidence snapshot that linked them.
    """
    __tablename__ = "campaign_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(
        String(64),
        ForeignKey("campaigns.campaign_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    indicator = Column(String(2048), nullable=False, index=True)
    indicator_type = Column(String(32), nullable=False, default="url")
    added_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    added_reason = Column(Text, nullable=True)
    resolved_observations_json = Column(JSON, nullable=True)

    # Relationships
    campaign = relationship("CampaignRecord", back_populates="members")
