from sqlalchemy import Column, Integer, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Feature(Base):
    scan_id = Column(Integer, ForeignKey("scan.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(JSON, nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="features")
