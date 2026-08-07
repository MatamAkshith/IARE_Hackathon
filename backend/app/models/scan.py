from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Scan(Base):
    domain_id = Column(Integer, ForeignKey("domain.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaign.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), default="pending", nullable=False)
    # E.2: Track which employee initiated this investigation (nullable for legacy rows)
    initiated_by = Column(String(64), nullable=True, index=True)

    # Relationships
    domain = relationship("Domain", back_populates="scans")
    campaign = relationship("Campaign", back_populates="scans")
    features = relationship("Feature", back_populates="scan", cascade="all, delete-orphan")
    risk_scores = relationship("RiskScore", back_populates="scan", cascade="all, delete-orphan")
