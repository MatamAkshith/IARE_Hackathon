from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ScanBase(BaseModel):
    domain_id: int
    campaign_id: Optional[int] = None
    status: str = "pending"

class ScanCreate(ScanBase):
    pass

class ScanUpdate(BaseModel):
    domain_id: Optional[int] = None
    campaign_id: Optional[int] = None
    status: Optional[str] = None

class ScanResponse(ScanBase):
    id: int
    campaign_name: Optional[str] = None
    campaign_uid: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
