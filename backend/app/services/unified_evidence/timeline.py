import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from app.services.unified_evidence.models import AuditTrail, EvidenceEvent

logger = logging.getLogger("app.services.unified_evidence.timeline")

# Known named external providers for source attribution
_EXTERNAL_PROVIDERS: frozenset = frozenset({
    "VirusTotal", "PhishTank", "URLHaus", "AbuseIPDB",
    "AlienVault OTX", "AlienVault", "External Threat Intel",
})


def _extract_key_from_message(message: str) -> Optional[str]:
    """
    Extracts the affected key name from a resolution or normalization log message.
    Expects the pattern: "... key 'some_key': ...".
    Returns None if the pattern is not found.
    """
    if "key '" in message:
        try:
            return message.split("key '")[1].split("'")[0]
        except IndexError:
            pass
    return None


class EvidenceTimelineBuilder:
    """
    Synthesizes a chronologically ordered AuditTrail from all four evidence
    processing phases: collection, conflict resolution, normalization, and
    confidence scoring.

    The timeline provides complete provenance and traceability, recording:
    - Which internal / external sources contributed each evidence key.
    - Which key conflicts were resolved and how.
    - Which normalization transforms were applied.
    - When confidence scoring was completed.
    """

    def generate_audit_trail(
        self,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
        conflict_resolutions: List[str],
        normalization_logs: List[str],
        investigation_start: Optional[datetime] = None,
    ) -> AuditTrail:
        """
        Builds and returns a fully sorted AuditTrail for a single investigation run.

        Parameters
        ----------
        internal_data        : raw key/value pairs from internal feature extraction
        external_data        : raw key/value pairs from external threat intelligence
        conflict_resolutions : human-readable conflict resolution messages from MergeStrategy
        normalization_logs   : human-readable normalization transform messages from EvidenceNormalizer
        investigation_start  : UTC datetime the investigation began (defaults to utcnow)
        """
        if investigation_start is None:
            investigation_start = datetime.now(timezone.utc)

        events: List[EvidenceEvent] = []
        base_ts = investigation_start

        # ------------------------------------------------------------------ #
        # Phase 1 — COLLECTION                                                #
        # ------------------------------------------------------------------ #
        for i, key in enumerate(internal_data):
            events.append(EvidenceEvent(
                timestamp=base_ts + timedelta(microseconds=i),
                source="Internal Extraction",
                event_type="collection",
                description=f"Internal feature '{key}' collected from extraction pipeline.",
                key_affected=key,
            ))

        ext_offset = len(internal_data)

        # Structured provider_responses payload (e.g., from aggregator)
        if "provider_responses" in external_data and isinstance(external_data["provider_responses"], dict):
            for j, provider in enumerate(external_data["provider_responses"]):
                events.append(EvidenceEvent(
                    timestamp=base_ts + timedelta(microseconds=ext_offset + j),
                    source=provider,
                    event_type="collection",
                    description=f"Threat intelligence collected from provider '{provider}'.",
                    key_affected=None,
                ))
        else:
            # Flat external dict: split known provider keys from generic indicator keys
            known = [k for k in external_data if k in _EXTERNAL_PROVIDERS]
            generic = [k for k in external_data if k not in _EXTERNAL_PROVIDERS]

            for j, provider in enumerate(known):
                events.append(EvidenceEvent(
                    timestamp=base_ts + timedelta(microseconds=ext_offset + j),
                    source=provider,
                    event_type="collection",
                    description=f"Threat intelligence collected from provider '{provider}'.",
                    key_affected=None,
                ))
            for j, key in enumerate(generic, start=len(known)):
                events.append(EvidenceEvent(
                    timestamp=base_ts + timedelta(microseconds=ext_offset + j),
                    source="External Threat Intel",
                    event_type="collection",
                    description=f"External indicator '{key}' ingested from threat intelligence feed.",
                    key_affected=key,
                ))

        # ------------------------------------------------------------------ #
        # Phase 2 — CONFLICT RESOLUTION                                       #
        # ------------------------------------------------------------------ #
        resolution_base = base_ts + timedelta(milliseconds=1)
        for idx, msg in enumerate(conflict_resolutions):
            events.append(EvidenceEvent(
                timestamp=resolution_base + timedelta(microseconds=idx),
                source="MergeStrategy",
                event_type="conflict_resolution",
                description=msg,
                key_affected=_extract_key_from_message(msg),
            ))

        # ------------------------------------------------------------------ #
        # Phase 3 — NORMALIZATION                                             #
        # ------------------------------------------------------------------ #
        norm_base = base_ts + timedelta(milliseconds=2)
        for idx, msg in enumerate(normalization_logs):
            events.append(EvidenceEvent(
                timestamp=norm_base + timedelta(microseconds=idx),
                source="EvidenceNormalizer",
                event_type="normalization",
                description=msg,
                key_affected=_extract_key_from_message(msg),
            ))

        # ------------------------------------------------------------------ #
        # Phase 4 — CONFIDENCE SCORING (summary event)                        #
        # ------------------------------------------------------------------ #
        events.append(EvidenceEvent(
            timestamp=base_ts + timedelta(milliseconds=3),
            source="EvidenceConfidenceEngine",
            event_type="confidence_scoring",
            description=(
                f"Confidence scoring applied to "
                f"{len(internal_data) + len(external_data)} input evidence keys. "
                f"Overall investigation confidence computed."
            ),
            key_affected=None,
        ))

        # Sort chronologically for deterministic audit reproducibility
        events.sort(key=lambda e: e.timestamp)

        logger.info(
            f"AuditTrail generated: {len(events)} events "
            f"({len(conflict_resolutions)} conflict(s), {len(normalization_logs)} normalization(s))."
        )

        return AuditTrail(investigation_start=investigation_start, events=events)
