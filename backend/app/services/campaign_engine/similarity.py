"""
SimilarityEngine — Stage 7.2

Evaluates similarity metrics between two evidence records using a collection
of registered correlation strategies. Outputs a normalized match score [0.0, 1.0]
and lists the triggered evidence.
"""

from typing import Any, Dict, List
import logging

from app.services.campaign_engine.models import CorrelationResult, CorrelationEvidence
from app.services.campaign_engine.correlators import (
    InfrastructureCorrelator,
    TlsCorrelator,
    WhoisCorrelator,
    HtmlCorrelator,
)

logger = logging.getLogger("app.services.campaign_engine.similarity")

# ─────────────────────────────────────────────────────────────────────────── #
# Feature Correlation Weights (Sum = 100)                                     #
# ─────────────────────────────────────────────────────────────────────────── #
_FEATURE_WEIGHTS: Dict[str, float] = {
    # Infrastructure (Max: 40)
    "shared_ip":                   25.0,
    "shared_dns_records":          10.0,
    "shared_asn":                   5.0,
    
    # TLS Certificate (Max: 30)
    "shared_tls_serial":           20.0,
    "shared_tls_subject":           5.0,
    "shared_tls_issuer":            5.0,
    
    # WHOIS Registry (Max: 15)
    "shared_registrant_org":        8.0,
    "shared_registrar":             4.0,
    "shared_domain_creation_date":  3.0,
    
    # HTML Content (Max: 15)
    "shared_page_title":            8.0,
    "shared_html_structure_hash":   5.0,
    "shared_forms_count":           2.0,
}


class SimilarityEngine:
    """
    Registers correlators and evaluates match scores between two investigations.
    """

    def __init__(self, threshold: float = 0.40) -> None:
        """
        Parameters
        ----------
        threshold : The normalized similarity score threshold [0.0, 1.0]
                    above which two investigations are considered correlated.
                    Default is 0.40 (40% match).
        """
        self.threshold = threshold
        self._correlators = [
            InfrastructureCorrelator(),
            TlsCorrelator(),
            WhoisCorrelator(),
            HtmlCorrelator(),
        ]
        logger.info(
            f"[SimilarityEngine] Initialized with {len(self._correlators)} correlators. "
            f"Correlation threshold: {self.threshold * 100:.0f}%."
        )

    def compare_evidence(
        self,
        evidence_a: Dict[str, Any],
        evidence_b: Dict[str, Any],
    ) -> CorrelationResult:
        """
        Compares two sets of resolved observations, calculates a cumulative
        similarity match score, and returns a CorrelationResult.
        """
        matched_evidence: List[CorrelationEvidence] = []
        raw_score = 0.0

        # Execute each correlator
        for correlator in self._correlators:
            try:
                hits = correlator.correlate_pair(evidence_a, evidence_b)
                if hits:
                    matched_evidence.extend(hits)
            except Exception as exc:
                logger.error(
                    f"Error running correlator '{correlator.strategy_name}': {exc}",
                    exc_info=True
                )

        # Calculate score based on matched feature weights
        for hit in matched_evidence:
            weight = _FEATURE_WEIGHTS.get(hit.type, 0.0)
            raw_score += weight

        # Normalize score to [0.0, 1.0] as constrained by match_score validation
        normalized_score = min(1.0, max(0.0, raw_score / 100.0))
        is_correlated = normalized_score >= self.threshold

        indicator_a = evidence_a.get("indicator", "unknown")
        indicator_b = evidence_b.get("indicator", "unknown")
        
        logger.info(
            f"[compare_evidence] Comparison between '{indicator_a}' and '{indicator_b}': "
            f"score={normalized_score * 100:.1f}%, correlated={is_correlated}, "
            f"matched_hits={len(matched_evidence)}."
        )

        return CorrelationResult(
            is_correlated=is_correlated,
            match_score=normalized_score,
            evidence=matched_evidence
        )
