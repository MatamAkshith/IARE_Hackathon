from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ThreatVerdict(str, Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"

class ThreatMatch(BaseModel):
    matched_name: str
    category: str
    confidence: float
    raw_tags: List[str]

class ProviderResponse(BaseModel):
    provider_name: str
    verdict: ThreatVerdict
    matches: List[ThreatMatch]
    raw_response: Dict[str, Any]
    error: Optional[str] = None
    response_time_ms: int

class ThreatEvidence(BaseModel):
    responses: Dict[str, ProviderResponse]
    execution_status: str
    timestamp: str
