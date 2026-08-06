from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DomainBase(BaseModel):
    url: str
    is_legitimate: bool = False

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
    url: Optional[str] = None
    is_legitimate: Optional[bool] = None

class DomainResponse(DomainBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
