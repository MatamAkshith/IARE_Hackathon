from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class CampaignResponse(CampaignBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
