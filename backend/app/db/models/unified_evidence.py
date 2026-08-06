from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from app.db.base_class import Base


class UnifiedEvidenceRecord(Base):
    """
    SQLAlchemy ORM model for persisting UnifiedEvidence objects.
    Stores the merged, normalized, and confidence-scored evidence for an indicator.
    """
    __tablename__ = "unified_evidence_records"

    # Override base id to keep auto-increment integer PK
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Core indicator fields
    indicator = Column(String(2048), nullable=False, index=True)
    indicator_type = Column(String(32), nullable=False, default="url")

    # Evidence data stored as JSON columns
    resolved_observations = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)
    internal_evidence = Column(JSON, nullable=True)
    external_evidence = Column(JSON, nullable=True)

    # Confidence and metadata
    overall_confidence = Column(String(32), nullable=False, default="unknown")
    metadata_json = Column(JSON, nullable=True)

    # Timestamp of when this evidence was processed
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Composite index: indicator + timestamp for fast history queries
    __table_args__ = (
        Index("ix_unified_evidence_indicator_timestamp", "indicator", "timestamp"),
    )
