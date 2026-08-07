from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Index
from app.db.base_class import Base


class RiskAssessmentRecord(Base):
    """
    SQLAlchemy ORM model for persisting completed Risk Assessment results.

    Stores the full RiskScore output including the explainability breakdown
    and analyst recommendations for historical retrieval and trend analysis.
    """
    __tablename__ = "risk_assessment_records"

    # Override base id — keep auto-increment integer PK
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Core indicator fields
    indicator = Column(String(2048), nullable=False, index=True)
    indicator_type = Column(String(32), nullable=False, default="url")

    # Scoring outputs
    overall_score = Column(Float, nullable=False, default=0.0)
    severity = Column(String(32), nullable=False, default="safe")

    # JSON payloads for full explainability
    breakdown = Column(JSON, nullable=True)           # RiskBreakdown serialized
    recommendations = Column(JSON, nullable=True)     # List[Recommendation] serialized
    explanation = Column(Text, nullable=True)

    # Source reference — links back to the UnifiedEvidence that triggered this
    unified_evidence_indicator = Column(String(2048), nullable=True, index=True)

    # Timestamp of when the assessment was computed
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Composite index for fast history queries by indicator + timestamp
    __table_args__ = (
        Index("ix_risk_assessment_indicator_timestamp", "indicator", "timestamp"),
    )
