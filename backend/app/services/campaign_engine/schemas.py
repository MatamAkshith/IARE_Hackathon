from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.campaign_engine.models import (
    CampaignStatus,
    CampaignSeverity,
    CampaignMember,
    CampaignSummary,
    CorrelationEvidence,
)


class CampaignCreate(BaseModel):
    """
    Schema for creating a new coordinated Campaign registry.
    """
    name: str = Field(..., min_length=3, max_length=256, description="Descriptive name of the campaign")
    status: Optional[CampaignStatus] = Field(default=CampaignStatus.MONITORING)
    severity: Optional[CampaignSeverity] = Field(default=CampaignSeverity.LOW)
    initial_indicator: str = Field(..., description="First malicious indicator to seed the campaign")
    initial_indicator_type: str = Field(..., description="Type of the initial indicator (url, domain, ip)")
    added_reason: str = Field(..., description="Reason for associating the initial indicator to the campaign")


class CampaignUpdate(BaseModel):
    """
    Schema for updating metadata attributes of an active Campaign.
    """
    name: Optional[str] = Field(None, min_length=3, max_length=256)
    status: Optional[CampaignStatus] = None
    severity: Optional[CampaignSeverity] = None


class AddCampaignMemberRequest(BaseModel):
    """
    Schema for adding a new indicator member to an existing campaign.
    """
    indicator: str = Field(..., description="The indicator URL/Domain/IP to link")
    indicator_type: str = Field(..., description="The indicator type (url, domain, ip)")
    added_reason: str = Field(..., description="Analytical justification for linking this indicator")
    resolved_observations: Dict[str, Any] = Field(default_factory=dict, description="Observations data snapshot")


class CampaignResponse(BaseModel):
    """
    API Response representation of a Campaign.
    """
    id: int
    campaign_id: str
    name: str
    status: CampaignStatus
    severity: CampaignSeverity
    members: List[CampaignMember]
    summary: CampaignSummary
    shared_infrastructure: List[CorrelationEvidence]
    created_at: datetime
    updated_at: datetime
    confidence: Optional[int] = None
    unique_iocs_count: Optional[int] = None
    max_score: Optional[float] = None

    class Config:
        from_attributes = True
