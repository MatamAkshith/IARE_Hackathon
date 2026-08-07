"""
Campaign Correlation Engine (Milestone 7)
=========================================
Architectural foundation and abstractions for linking multiple individual
investigations into coordinated threat campaigns using infrastructure overlap,
content similarity, and behavioral analysis.
"""

from app.services.campaign_engine.models import (
    CampaignSeverity,
    CampaignStatus,
    CampaignMember,
    CorrelationEvidence,
    CorrelationResult,
    CampaignSummary,
    Campaign,
)
from app.services.campaign_engine.schemas import (
    CampaignCreate,
    CampaignUpdate,
    AddCampaignMemberRequest,
    CampaignResponse,
)
from app.services.campaign_engine.base import BaseCorrelationStrategy
from app.services.campaign_engine.service import CampaignCorrelationService

__all__ = [
    "CampaignSeverity",
    "CampaignStatus",
    "CampaignMember",
    "CorrelationEvidence",
    "CorrelationResult",
    "CampaignSummary",
    "Campaign",
    "CampaignCreate",
    "CampaignUpdate",
    "AddCampaignMemberRequest",
    "CampaignResponse",
    "BaseCorrelationStrategy",
    "CampaignCorrelationService",
]
