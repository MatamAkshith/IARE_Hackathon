from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EvidenceCategory(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"

class EvidenceConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class EvidenceSource(BaseModel):
    name: str
    category: EvidenceCategory
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EvidenceMetadata(BaseModel):
    severity: str = "unknown"
    tags: List[str] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    conflict_resolutions: List[str] = Field(default_factory=list)
    item_confidences: Dict[str, EvidenceConfidence] = Field(default_factory=dict)
    normalization_logs: List[str] = Field(default_factory=list)


class UnifiedEvidence(BaseModel):
    indicator: str
    indicator_type: str
    internal_evidence: Optional[Dict[str, Any]] = None
    external_evidence: Optional[Dict[str, Any]] = None
    resolved_observations: Dict[str, Any] = Field(default_factory=dict)
    sources: List[EvidenceSource] = Field(default_factory=list)
    overall_confidence: EvidenceConfidence = EvidenceConfidence.UNKNOWN
    metadata: EvidenceMetadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

