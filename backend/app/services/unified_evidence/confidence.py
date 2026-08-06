import logging
from typing import Any, Dict

from app.services.unified_evidence.models import EvidenceConfidence

logger = logging.getLogger("app.services.unified_evidence.confidence")

# External threat intelligence keys that carry HIGH signal reliability
_CRITICAL_EXTERNAL_KEYS = frozenset({
    "virustotal_verdict",
    "phishtank_verdict",
    "urlhaus_verdict",
    "overall_verdict",
    "abuse_confidence_score",
    "pulse_count",
    "raw_response",
    "provider_responses",
    "abuseipdb_verdict",
    "alienvault_verdict",
})

# Internally extracted heuristic keys that carry MEDIUM signal reliability
_INTERNAL_HEURISTIC_KEYS = frozenset({
    "has_login_form",
    "domain_age_days",
    "ssl_valid",
    "ns_records",
    "mx_records",
    "forms_count",
    "password_inputs",
    "extracted_emails",
})

# Numeric weight map used for consensus calculation
_CONFIDENCE_WEIGHTS: Dict[EvidenceConfidence, int] = {
    EvidenceConfidence.HIGH: 3,
    EvidenceConfidence.MEDIUM: 2,
    EvidenceConfidence.LOW: 1,
    EvidenceConfidence.UNKNOWN: 0,
}


class EvidenceConfidenceEngine:
    """
    Assigns reliability levels to individual evidence items and derives an
    overall investigation confidence score via weighted consensus.
    """

    def evaluate_item_confidence(
        self,
        key: str,
        value: Any,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
    ) -> EvidenceConfidence:
        """
        Evaluates the source and reliability of a single evidence item.

        Priority order:
          1. None / empty value → UNKNOWN
          2. Key is a critical external TI indicator OR present in external_data → HIGH
          3. Key is a known internal heuristic OR present in internal_data → MEDIUM
          4. Fallback → LOW
        """
        if value is None or value == "":
            return EvidenceConfidence.UNKNOWN

        if key in _CRITICAL_EXTERNAL_KEYS or key in external_data:
            logger.debug(f"Item '{key}' assigned HIGH confidence (external TI indicator).")
            return EvidenceConfidence.HIGH

        if key in _INTERNAL_HEURISTIC_KEYS or key in internal_data:
            logger.debug(f"Item '{key}' assigned MEDIUM confidence (internal heuristic).")
            return EvidenceConfidence.MEDIUM

        logger.debug(f"Item '{key}' assigned LOW confidence (unknown source).")
        return EvidenceConfidence.LOW

    def calculate_overall_confidence(
        self,
        item_confidences: Dict[str, EvidenceConfidence],
    ) -> EvidenceConfidence:
        """
        Derives overall investigation confidence via weighted consensus.

        Fast-path: If any single item carries HIGH confidence, the overall
        investigation is flagged HIGH immediately (critical-signal promotion).
        Otherwise, the weighted average of all items determines the level.
        """
        if not item_confidences:
            return EvidenceConfidence.UNKNOWN

        levels = list(item_confidences.values())

        # Fast-path: any HIGH indicator promotes the entire investigation
        if EvidenceConfidence.HIGH in levels:
            logger.info("Overall confidence: HIGH (critical-signal promotion).")
            return EvidenceConfidence.HIGH

        total = sum(_CONFIDENCE_WEIGHTS[c] for c in levels)
        avg = total / len(levels)

        if avg >= 2.0:
            result = EvidenceConfidence.MEDIUM
        elif avg >= 1.0:
            result = EvidenceConfidence.LOW
        else:
            result = EvidenceConfidence.UNKNOWN

        logger.info(f"Overall confidence: {result.value} (weighted avg score: {avg:.2f}).")
        return result
