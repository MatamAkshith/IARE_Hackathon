from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Session

from app.services.unified_evidence.models import (
    UnifiedEvidence,
    EvidenceCategory,
    EvidenceConfidence,
    EvidenceSource,
    EvidenceMetadata
)
from app.services.unified_evidence.normalizer import EvidenceNormalizer
from app.services.unified_evidence.confidence import EvidenceConfidenceEngine

logger = logging.getLogger("app.services.unified_evidence.service")

class BaseMergeStrategy(ABC):
    @abstractmethod
    def merge(
        self,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
        conflict_resolutions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Merge strategy interface for unified evidence payload synthesis.
        """
        pass

class UnifiedEvidenceService:
    def __init__(self) -> None:
        # Import inside __init__ to avoid circular dependency with strategy.py
        from app.services.unified_evidence.strategy import DefaultMergeStrategy
        self._strategy = DefaultMergeStrategy()
        self._normalizer = EvidenceNormalizer()
        self._confidence_engine = EvidenceConfidenceEngine()

    def process_evidence(
        self,
        indicator: str,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any]
    ) -> UnifiedEvidence:
        """
        Processes, maps, normalizes, and scores raw internal feature extraction data and external threat
        intelligence data into a single unified evidence representation.
        """
        now = datetime.now(timezone.utc)
        logger.info(f"Starting evidence processing and normalization for indicator: {indicator}")

        # Step 1: Merge data (applies DefaultMergeStrategy)
        conflict_resolutions: List[str] = []
        resolved_observations = self._strategy.merge(
            internal_data=internal_data,
            external_data=external_data,
            conflict_resolutions=conflict_resolutions
        )

        if conflict_resolutions:
            logger.info(f"Conflicts resolved during merge for {indicator}: {len(conflict_resolutions)} issues resolved.")
            for res in conflict_resolutions:
                logger.debug(f"  Conflict Resolution: {res}")

        # Step 2: Normalize the resolved_observations
        normalized_observations, normalization_logs = self._normalizer.normalize(resolved_observations)

        # Step 3: Calculate individual item confidences
        item_confidences: Dict[str, EvidenceConfidence] = {}
        for k, v in normalized_observations.items():
            item_confidences[k] = self._confidence_engine.evaluate_item_confidence(
                key=k,
                value=v,
                internal_data=internal_data,
                external_data=external_data
            )

        # Step 4: Calculate overall confidence
        overall_confidence = self._confidence_engine.calculate_overall_confidence(item_confidences)

        # Map sources attribution
        sources = [
            EvidenceSource(name="Internal Extraction", category=EvidenceCategory.INTERNAL, timestamp=now)
        ]

        # Extract specific external providers if present
        if "provider_responses" in external_data and isinstance(external_data["provider_responses"], dict):
            for provider_name in external_data["provider_responses"].keys():
                sources.append(
                    EvidenceSource(name=provider_name, category=EvidenceCategory.EXTERNAL, timestamp=now)
                )
        else:
            for k in external_data.keys():
                if k in ["VirusTotal", "PhishTank", "URLHaus", "AbuseIPDB", "AlienVault OTX", "AlienVault"]:
                    sources.append(
                        EvidenceSource(name=k, category=EvidenceCategory.EXTERNAL, timestamp=now)
                    )
            if len(sources) == 1:
                sources.append(
                    EvidenceSource(name="External Threat Intel", category=EvidenceCategory.EXTERNAL, timestamp=now)
                )

        metadata = EvidenceMetadata(
            severity="info",
            tags=["merged", "normalized"],
            raw_data={},
            conflict_resolutions=conflict_resolutions,
            item_confidences=item_confidences,
            normalization_logs=normalization_logs
        )

        # Simple indicator type detection
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
            resolved_observations=normalized_observations,
            sources=sources,
            overall_confidence=overall_confidence,
            metadata=metadata,
            timestamp=now
        )

    def save_evidence(
        self,
        db: Session,
        evidence: UnifiedEvidence
    ):
        """
        Persists a UnifiedEvidence Pydantic object to the database.
        Returns the saved UnifiedEvidenceRecord ORM instance.
        """
        from app.db.models.unified_evidence import UnifiedEvidenceRecord

        # Serialize sources to JSON-safe list of dicts
        sources_json = [
            {"name": s.name, "category": s.category.value, "timestamp": s.timestamp.isoformat()}
            for s in evidence.sources
        ]

        # Serialize item_confidences to JSON-safe dict
        item_confidences_json = {k: v.value for k, v in evidence.metadata.item_confidences.items()}

        metadata_json = {
            "severity": evidence.metadata.severity,
            "tags": evidence.metadata.tags,
            "conflict_resolutions": evidence.metadata.conflict_resolutions,
            "normalization_logs": evidence.metadata.normalization_logs,
            "item_confidences": item_confidences_json,
        }

        record = UnifiedEvidenceRecord(
            indicator=evidence.indicator,
            indicator_type=evidence.indicator_type,
            resolved_observations=evidence.resolved_observations,
            internal_evidence=evidence.internal_evidence,
            external_evidence=evidence.external_evidence,
            sources=sources_json,
            overall_confidence=evidence.overall_confidence.value,
            metadata_json=metadata_json,
            timestamp=evidence.timestamp,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        logger.info(f"Persisted UnifiedEvidenceRecord id={record.id} for indicator: {evidence.indicator}")
        return record

    def get_evidence_by_indicator(
        self,
        db: Session,
        indicator: str
    ) -> List:
        """
        Retrieves historical unified evidence records for a specific indicator,
        ordered by timestamp descending (most recent first).
        """
        from app.db.models.unified_evidence import UnifiedEvidenceRecord

        records = (
            db.query(UnifiedEvidenceRecord)
            .filter(UnifiedEvidenceRecord.indicator == indicator)
            .order_by(UnifiedEvidenceRecord.timestamp.desc())
            .all()
        )

        logger.info(f"Retrieved {len(records)} evidence record(s) for indicator: {indicator}")
        return records
