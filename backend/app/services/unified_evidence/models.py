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


class EvidenceEvent(BaseModel):
    """
    A single timestamped event in the investigation's audit trail.
    Captures what happened, when it happened, which source triggered it,
    and which evidence key was affected (if any).
    """
    timestamp: datetime
    source: str
    event_type: str  # e.g. 'collection', 'normalization', 'conflict_resolution', 'confidence_scoring'
    description: str
    key_affected: Optional[str] = None


class AuditTrail(BaseModel):
    """
    The full chronological history of all events that occurred during evidence processing.
    Provides complete provenance and traceability for each investigation.
    """
    investigation_start: datetime
    events: List[EvidenceEvent] = Field(default_factory=list)


class UnifiedEvidence(BaseModel):
    indicator: str
    indicator_type: str
    internal_evidence: Optional[Dict[str, Any]] = None
    external_evidence: Optional[Dict[str, Any]] = None
    resolved_observations: Dict[str, Any] = Field(default_factory=dict)
    sources: List[EvidenceSource] = Field(default_factory=list)
    overall_confidence: EvidenceConfidence = EvidenceConfidence.UNKNOWN
    metadata: EvidenceMetadata
    audit_trail: Optional[AuditTrail] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
