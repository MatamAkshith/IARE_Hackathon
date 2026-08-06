from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Domain(Base):
    url = Column(String(2048), nullable=False, unique=True, index=True)
    is_legitimate = Column(Boolean, default=False, nullable=False)

    # Relationships
    scans = relationship("Scan", back_populates="domain", cascade="all, delete-orphan")
