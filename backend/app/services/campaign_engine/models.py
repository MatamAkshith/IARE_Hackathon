from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CampaignSeverity(str, Enum):
    """
    Indicates the potential impact and threat level of a campaign.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CampaignStatus(str, Enum):
    """
    Represents the operational state of a campaign tracking lifecycle.
    """
    ACTIVE = "active"
    MITIGATED = "mitigated"
    MONITORING = "monitoring"
    DORMANT = "dormant"


class CampaignMember(BaseModel):
    """
    Represents an individual indicator (URL, Domain, or IP) associated
    with a coordinated phishing campaign.
    """
    indicator: str
    indicator_type: str  # 'url' | 'domain' | 'ip'
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    added_reason: str
    resolved_observations: Dict[str, Any] = Field(default_factory=dict)


class CorrelationEvidence(BaseModel):
    """
    Details of overlapping evidence that connects members of a campaign.
    """
    type: str  # e.g., 'shared_ip', 'shared_ns', 'ssl_issuer', 'favicon_hash', 'html_similarity'
    value: str
    confidence: str  # 'high' | 'medium' | 'low'
    description: str


class CorrelationResult(BaseModel):
    """
    The output of a similarity or infrastructure matching computation.
    """
    is_correlated: bool
    match_score: float = Field(ge=0.0, le=1.0)
    evidence: List[CorrelationEvidence] = Field(default_factory=list)


class CampaignSummary(BaseModel):
    """
    Statistical summary of the scale and lifecycle of a campaign.
    """
    total_indicators: int
    first_seen: datetime
    last_seen: datetime
    primary_ttp_tags: List[str] = Field(default_factory=list)


class Campaign(BaseModel):
    """
    The root domain model representing a coordinated phishing campaign.
    """
    campaign_id: str
    name: str
    status: CampaignStatus = CampaignStatus.MONITORING
    severity: CampaignSeverity = CampaignSeverity.LOW
    members: List[CampaignMember] = Field(default_factory=list)
    summary: CampaignSummary
    shared_infrastructure: List[CorrelationEvidence] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
