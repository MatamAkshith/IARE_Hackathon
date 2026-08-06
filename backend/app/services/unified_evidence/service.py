from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.services.unified_evidence.models import (
    UnifiedEvidence,
    EvidenceCategory,
    EvidenceConfidence,
    EvidenceSource,
    EvidenceMetadata,
    AuditTrail,
)
from app.services.unified_evidence.normalizer import EvidenceNormalizer
from app.services.unified_evidence.confidence import EvidenceConfidenceEngine
from app.services.unified_evidence.timeline import EvidenceTimelineBuilder

logger = logging.getLogger("app.services.unified_evidence.service")


class BaseMergeStrategy(ABC):
    """Abstract base for all evidence merge strategies."""

    @abstractmethod
    def merge(
        self,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
        conflict_resolutions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Merge internal and external evidence into a single resolved dict."""


class UnifiedEvidenceService:
    """
    Orchestrates the full five-step unified evidence pipeline:
      1. Merge (conflict resolution + deduplication)
      2. Normalize (type casting + URL standardization)
      3. Item-level confidence scoring
      4. Overall confidence consensus
      5. Audit trail timeline generation
    """

    def __init__(self) -> None:
        # Local import of DefaultMergeStrategy to avoid circular import at module load
        from app.services.unified_evidence.strategy import DefaultMergeStrategy
        self._strategy: BaseMergeStrategy = DefaultMergeStrategy()
        self._normalizer = EvidenceNormalizer()
        self._confidence_engine = EvidenceConfidenceEngine()
        self._timeline_builder = EvidenceTimelineBuilder()

    def process_evidence(
        self,
        indicator: str,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
    ) -> UnifiedEvidence:
        """
        Processes raw internal feature extraction data and external threat intelligence
        data into a single, normalized, confidence-scored UnifiedEvidence object
        with a complete audit trail.

        Raises:
            RuntimeError: If any stage of the pipeline fails unrecoverably.
        """
        logger.info(f"[process_evidence] Starting pipeline for indicator: '{indicator}'")
        now = datetime.now(timezone.utc)

        try:
            # Step 1 — Merge
            conflict_resolutions: List[str] = []
            resolved_observations = self._strategy.merge(
                internal_data=internal_data,
                external_data=external_data,
                conflict_resolutions=conflict_resolutions,
            )

            # Step 2 — Normalize
            normalized_observations, normalization_logs = self._normalizer.normalize(
                resolved_observations
            )

            # Step 3 — Item-level confidence
            item_confidences: Dict[str, EvidenceConfidence] = {
                k: self._confidence_engine.evaluate_item_confidence(
                    key=k,
                    value=v,
                    internal_data=internal_data,
                    external_data=external_data,
                )
                for k, v in normalized_observations.items()
            }

            # Step 4 — Overall confidence consensus
            overall_confidence = self._confidence_engine.calculate_overall_confidence(
                item_confidences
            )

            # Step 5 — Audit trail
            audit_trail: AuditTrail = self._timeline_builder.generate_audit_trail(
                internal_data=internal_data,
                external_data=external_data,
                conflict_resolutions=conflict_resolutions,
                normalization_logs=normalization_logs,
                investigation_start=now,
            )

        except Exception as exc:
            logger.exception(
                f"[process_evidence] Pipeline failure for indicator '{indicator}': {exc}"
            )
            raise RuntimeError(
                f"Evidence processing pipeline failed for indicator '{indicator}': {exc}"
            ) from exc

        # Build source attribution list
        sources = self._build_sources(external_data=external_data, timestamp=now)

        metadata = EvidenceMetadata(
            severity="info",
            tags=["merged", "normalized"],
            raw_data={},
            conflict_resolutions=conflict_resolutions,
            item_confidences=item_confidences,
            normalization_logs=normalization_logs,
        )

        indicator_type = _detect_indicator_type(indicator)

        logger.info(
            f"[process_evidence] Pipeline complete for '{indicator}': "
            f"type={indicator_type}, confidence={overall_confidence.value}, "
            f"keys={len(normalized_observations)}, events={len(audit_trail.events)}."
        )

        return UnifiedEvidence(
            indicator=indicator,
            indicator_type=indicator_type,
            internal_evidence=internal_data,
            external_evidence=external_data,
            resolved_observations=normalized_observations,
            sources=sources,
            overall_confidence=overall_confidence,
            metadata=metadata,
            audit_trail=audit_trail,
            timestamp=now,
        )

    # ------------------------------------------------------------------ #
    # Persistence methods                                                 #
    # ------------------------------------------------------------------ #

    def save_evidence(self, db: Session, evidence: UnifiedEvidence):
        """
        Persists a UnifiedEvidence Pydantic object to the database.
        The audit_trail is serialized into metadata_json for storage.
        Returns the saved UnifiedEvidenceRecord ORM instance.
        """
        from app.db.models.unified_evidence import UnifiedEvidenceRecord

        sources_json = [
            {"name": s.name, "category": s.category.value, "timestamp": s.timestamp.isoformat()}
            for s in evidence.sources
        ]

        audit_trail_json: Optional[Dict[str, Any]] = None
        if evidence.audit_trail:
            audit_trail_json = {
                "investigation_start": evidence.audit_trail.investigation_start.isoformat(),
                "events": [
                    {
                        "timestamp": e.timestamp.isoformat(),
                        "source": e.source,
                        "event_type": e.event_type,
                        "description": e.description,
                        "key_affected": e.key_affected,
                    }
                    for e in evidence.audit_trail.events
                ],
            }

        metadata_json: Dict[str, Any] = {
            "severity": evidence.metadata.severity,
            "tags": evidence.metadata.tags,
            "conflict_resolutions": evidence.metadata.conflict_resolutions,
            "normalization_logs": evidence.metadata.normalization_logs,
            "item_confidences": {k: v.value for k, v in evidence.metadata.item_confidences.items()},
            "audit_trail": audit_trail_json,
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

        logger.info(
            f"Persisted UnifiedEvidenceRecord id={record.id} for indicator: '{evidence.indicator}'."
        )
        return record

    def get_evidence_by_indicator(self, db: Session, indicator: str) -> List:
        """
        Retrieves all unified evidence records for an indicator, ordered by
        timestamp descending (most recent first).
        """
        from app.db.models.unified_evidence import UnifiedEvidenceRecord

        records = (
            db.query(UnifiedEvidenceRecord)
            .filter(UnifiedEvidenceRecord.indicator == indicator)
            .order_by(UnifiedEvidenceRecord.timestamp.desc())
            .all()
        )

        logger.info(
            f"Retrieved {len(records)} evidence record(s) for indicator: '{indicator}'."
        )
        return records

    # ------------------------------------------------------------------ #
    # Private helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_sources(
        external_data: Dict[str, Any], timestamp: datetime
    ) -> List[EvidenceSource]:
        """Constructs the list of EvidenceSource attribution objects."""
        _NAMED_PROVIDERS = frozenset({
            "VirusTotal", "PhishTank", "URLHaus",
            "AbuseIPDB", "AlienVault OTX", "AlienVault",
        })

        sources: List[EvidenceSource] = [
            EvidenceSource(
                name="Internal Extraction",
                category=EvidenceCategory.INTERNAL,
                timestamp=timestamp,
            )
        ]

        if "provider_responses" in external_data and isinstance(
            external_data["provider_responses"], dict
        ):
            for name in external_data["provider_responses"]:
                sources.append(
                    EvidenceSource(
                        name=name,
                        category=EvidenceCategory.EXTERNAL,
                        timestamp=timestamp,
                    )
                )
        else:
            named = [k for k in external_data if k in _NAMED_PROVIDERS]
            for name in named:
                sources.append(
                    EvidenceSource(
                        name=name,
                        category=EvidenceCategory.EXTERNAL,
                        timestamp=timestamp,
                    )
                )
            if not named:
                sources.append(
                    EvidenceSource(
                        name="External Threat Intel",
                        category=EvidenceCategory.EXTERNAL,
                        timestamp=timestamp,
                    )
                )

        return sources


# ------------------------------------------------------------------ #
# Module-level helpers                                               #
# ------------------------------------------------------------------ #

def _detect_indicator_type(indicator: str) -> str:
    """
    Heuristically classifies an indicator string as 'url', 'ip', or 'domain'.
    """
    if "://" in indicator:
        return "url"
    if not indicator.replace(".", "").isalpha() and (
        indicator.count(".") == 3 or ":" in indicator
    ):
        return "ip"
    if "." in indicator:
        return "domain"
    return "url"
