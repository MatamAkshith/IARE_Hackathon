from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

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
    status: str = "success"  # "success" | "no_result" | "unavailable" | "rate_limited"
    response_time_ms: int

class ThreatEvidence(BaseModel):
    responses: Dict[str, ProviderResponse]
    execution_status: str
    timestamp: str

class AggregatedThreatEvidence(BaseModel):
    indicator: str
    indicator_type: str
    overall_verdict: ThreatVerdict
    total_providers: int
    successful_providers: int
    failed_providers: int
    malicious_count: int
    suspicious_count: int
    clean_count: int
    provider_responses: Dict[str, ProviderResponse]
    timestamp: datetime
