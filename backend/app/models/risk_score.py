from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class RiskScore(Base):
    scan_id = Column(Integer, ForeignKey("scan.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="risk_scores")
