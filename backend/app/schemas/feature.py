from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class FeatureBase(BaseModel):
    scan_id: int
    key: str
    value: Optional[Any] = None

class FeatureCreate(FeatureBase):
    pass

class FeatureUpdate(BaseModel):
    scan_id: Optional[int] = None
    key: Optional[str] = None
    value: Optional[Any] = None

class FeatureResponse(FeatureBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
