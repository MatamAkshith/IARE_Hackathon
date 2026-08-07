from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.ai_assistant.models import ResponseType
from app.services.unified_evidence.models import UnifiedEvidence
from app.services.risk_engine.models import RiskScore
from app.services.campaign_engine.models import Campaign


class SuggestedAction(BaseModel):
    """
    Represents an actionable recommendation or link suggested by the AI.
    """
    label: str = Field(..., description="Short button text or label for the action")
    action_type: str = Field(..., description="Action type identifier (e.g. 'pivot', 'mitigate', 'export')")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Metadata payload needed to execute the action")


class AssistantMessage(BaseModel):
    """
    A single message in the AI assistant conversation history.
    """
    role: str = Field(..., description="Role of the sender ('user', 'assistant', 'system')")
    content: str = Field(..., description="Message text content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of the message")


class InvestigationContext(BaseModel):
    """
    The structured context representing all collected data about the indicator.
    Used to supply the AI model with ground-truth evidence.
    """
    indicator: str = Field(..., description="The indicator URL, domain, or IP being investigated")
    evidence: Optional[UnifiedEvidence] = Field(None, description="Unified evidence and observation data")
    risk_assessment: Optional[RiskScore] = Field(None, description="Risk assessment score and breakdown")
    campaign_details: Optional[Campaign] = Field(None, description="Correlated campaign membership and metadata")


class AssistantResponse(BaseModel):
    """
    The output response from the AI assistant.
    """
    message: AssistantMessage = Field(..., description="The main response message content")
    suggested_actions: List[SuggestedAction] = Field(default_factory=list, description="Actions recommended by the AI based on the context")
    response_type: ResponseType = Field(default=ResponseType.CHAT, description="Format type of the response")
