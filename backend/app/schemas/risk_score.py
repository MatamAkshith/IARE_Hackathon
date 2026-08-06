from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class RiskScoreBase(BaseModel):
    scan_id: int
    score: int
    explanation: Optional[str] = None

class RiskScoreCreate(RiskScoreBase):
    pass

class RiskScoreUpdate(BaseModel):
    scan_id: Optional[int] = None
    score: Optional[int] = None
    explanation: Optional[str] = None

class RiskScoreResponse(RiskScoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
