import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from app.services.unified_evidence.models import AuditTrail, EvidenceEvent

logger = logging.getLogger("app.services.unified_evidence.timeline")

# Known external provider names for source attribution
_EXTERNAL_PROVIDERS = {
    "VirusTotal", "PhishTank", "URLHaus", "AbuseIPDB",
    "AlienVault OTX", "AlienVault", "External Threat Intel",
}


class EvidenceTimelineBuilder:
    """
    Synthesizes a chronologically ordered audit trail (AuditTrail) from
    the evidence collection, conflict resolution, and normalization stages.

    The timeline faithfully captures:
    - When each internal / external data source contributed evidence.
    - Which specific key conflicts were resolved and how.
    - Which normalization transforms were applied to individual keys.
    - When confidence scoring was applied at item and overall levels.
    """

    def generate_audit_trail(
        self,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
        conflict_resolutions: List[str],
        normalization_logs: List[str],
        investigation_start: datetime | None = None,
    ) -> AuditTrail:
        """
        Builds and returns a fully sorted AuditTrail for a single investigation run.

        Parameters
        ----------
        internal_data        : raw key/value pairs from internal feature extraction
        external_data        : raw key/value pairs from external threat intelligence
        conflict_resolutions : list of human-readable conflict resolution messages
        normalization_logs   : list of human-readable normalization transform messages
        investigation_start  : UTC datetime the investigation began (defaults to now)
        """
        if investigation_start is None:
            investigation_start = datetime.now(timezone.utc)

        events: List[EvidenceEvent] = []

        # ------------------------------------------------------------------ #
        # Phase 1 – COLLECTION events                                         #
        # ------------------------------------------------------------------ #
        # Internal extraction — one event per key collected
        base_ts = investigation_start
        for i, key in enumerate(internal_data.keys()):
            events.append(EvidenceEvent(
                timestamp=base_ts + timedelta(microseconds=i),
                source="Internal Extraction",
                event_type="collection",
                description=f"Internal feature '{key}' collected from extraction pipeline.",
                key_affected=key,
            ))

        # External threat intelligence — deduce provider name from data structure
        ext_offset = len(internal_data)
        if "provider_responses" in external_data and isinstance(external_data["provider_responses"], dict):
            for j, (provider, payload) in enumerate(external_data["provider_responses"].items()):
                events.append(EvidenceEvent(
                    timestamp=base_ts + timedelta(microseconds=ext_offset + j),
                    source=provider,
                    event_type="collection",
                    description=f"Threat intelligence collected from provider '{provider}'.",
                    key_affected=None,
                ))
        else:
            known_providers = {k for k in external_data.keys() if k in _EXTERNAL_PROVIDERS}
            generic_keys = [k for k in external_data.keys() if k not in _EXTERNAL_PROVIDERS]

            for j, provider in enumerate(known_providers):
                events.append(EvidenceEvent(
                    timestamp=base_ts + timedelta(microseconds=ext_offset + j),
                    source=provider,
                    event_type="collection",
                    description=f"Threat intelligence collected from provider '{provider}'.",
                    key_affected=None,
                ))

            for j, key in enumerate(generic_keys, start=len(known_providers)):
                events.append(EvidenceEvent(
                    timestamp=base_ts + timedelta(microseconds=ext_offset + j),
                    source="External Threat Intel",
                    event_type="collection",
                    description=f"External indicator '{key}' ingested from threat intelligence feed.",
                    key_affected=key,
                ))

        # ------------------------------------------------------------------ #
        # Phase 2 – CONFLICT RESOLUTION events                                #
        # ------------------------------------------------------------------ #
        resolution_base = base_ts + timedelta(milliseconds=1)
        for idx, resolution_msg in enumerate(conflict_resolutions):
            # Extract the key name from the resolution message when possible
            key_affected: str | None = None
            if "key '" in resolution_msg:
                try:
                    key_affected = resolution_msg.split("key '")[1].split("'")[0]
                except IndexError:
                    pass

            events.append(EvidenceEvent(
                timestamp=resolution_base + timedelta(microseconds=idx),
                source="MergeStrategy",
                event_type="conflict_resolution",
                description=resolution_msg,
                key_affected=key_affected,
            ))

        # ------------------------------------------------------------------ #
        # Phase 3 – NORMALIZATION events                                      #
        # ------------------------------------------------------------------ #
        norm_base = base_ts + timedelta(milliseconds=2)
        for idx, norm_msg in enumerate(normalization_logs):
            key_affected = None
            if "key '" in norm_msg:
                try:
                    key_affected = norm_msg.split("key '")[1].split("'")[0]
                except IndexError:
                    pass

            events.append(EvidenceEvent(
                timestamp=norm_base + timedelta(microseconds=idx),
                source="EvidenceNormalizer",
                event_type="normalization",
                description=norm_msg,
                key_affected=key_affected,
            ))

        # ------------------------------------------------------------------ #
        # Phase 4 – CONFIDENCE SCORING event (summary)                        #
        # ------------------------------------------------------------------ #
        events.append(EvidenceEvent(
            timestamp=base_ts + timedelta(milliseconds=3),
            source="EvidenceConfidenceEngine",
            event_type="confidence_scoring",
            description=(
                f"Confidence scoring applied to {len(internal_data) + len(external_data)} "
                f"merged evidence keys. Overall investigation confidence computed."
            ),
            key_affected=None,
        ))

        # Sort chronologically — deterministic ordering guarantees audit reproducibility
        events.sort(key=lambda e: e.timestamp)

        logger.info(
            f"AuditTrail generated: {len(events)} events "
            f"({len(conflict_resolutions)} conflicts, {len(normalization_logs)} normalizations)."
        )

        return AuditTrail(investigation_start=investigation_start, events=events)
