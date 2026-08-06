from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any

from app.services.unified_evidence.models import (
    UnifiedEvidence,
    EvidenceCategory,
    EvidenceConfidence,
    EvidenceSource,
    EvidenceMetadata
)

class BaseMergeStrategy(ABC):
    @abstractmethod
    def merge(
        self,
        indicator: str,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any]
    ) -> UnifiedEvidence:
        """
        Merge strategy interface for unified evidence payload synthesis.
        """
        pass

class UnifiedEvidenceService:
    def process_evidence(
        self,
        indicator: str,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any]
    ) -> UnifiedEvidence:
        """
        Processes and maps raw internal feature extraction data and external threat intelligence
        data into a single unified evidence representation.
        
        Note: Currently implemented as a structural placeholder. Complex merging strategies
        will be deployed in Stage 5.2.
        """
        now = datetime.now(timezone.utc)
        
        dummy_sources = [
            EvidenceSource(name="internal_extractor", category=EvidenceCategory.INTERNAL, timestamp=now),
            EvidenceSource(name="external_threat_intel", category=EvidenceCategory.EXTERNAL, timestamp=now),
        ]
        
        dummy_metadata = EvidenceMetadata(
            severity="info",
            tags=["placeholder"],
            raw_data={}
        )
        
        # Simple indicator type detection (url, domain, ip)
        indicator_type = "url"
        if "://" in indicator:
            indicator_type = "url"
        elif not indicator.replace(".", "").isalpha() and (indicator.count(".") == 3 or ":" in indicator):
            indicator_type = "ip"
        elif "." in indicator:
            indicator_type = "domain"

            
        return UnifiedEvidence(
            indicator=indicator,
            indicator_type=indicator_type,
            internal_evidence=internal_data,
            external_evidence=external_data,
            sources=dummy_sources,
            overall_confidence=EvidenceConfidence.UNKNOWN,
            metadata=dummy_metadata,
            timestamp=now
        )
