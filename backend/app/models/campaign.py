from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Campaign(Base):
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1024), nullable=True)
    status = Column(String(50), default="active", nullable=False)

    # Relationships
    scans = relationship("Scan", back_populates="campaign")
