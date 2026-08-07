"""
RiskScoringService — Core orchestrator for the Explainable Risk Engine.

Pipeline (per request):
  0. Validate evidence (short-circuit to SAFE if empty/malformed).
  1. Extract evidence dict from UnifiedEvidence or accept a plain dict.
  2. Run each registered evaluator via safe_evaluate() (never crashes).
  3. Sum raw contributions; track which categories were present (dynamic denominator).
  4. Normalize to 0-100 scale using the adjusted denominator.
  5. Calibrate score by evidence confidence level.
  6. Enforce strict 0-100 boundaries.
  7. Map score to RiskSeverity tier.
  8. Generate prioritized analyst recommendations via RecommendationEngine.
  9. Assemble RiskScore with full RiskBreakdown and explainability.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

from app.services.risk_engine.config import (
    CATEGORY_EVIDENCE_KEYS,
    SEVERITY_THRESHOLDS,
)
from app.services.risk_engine.models import (
    RiskBreakdown,
    RiskFactor,
    RiskScore,
    RiskSeverity,
    Recommendation,
)
from app.services.risk_engine.recommendations import RecommendationEngine
from app.services.risk_engine.rules import (
    ALL_EVALUATORS,
    TOTAL_MAX_CONTRIBUTION,
    DomainIntelEvaluator,
    DnsWhoisEvaluator,
    TlsCertificateEvaluator,
    HtmlContentEvaluator,
    ThreatIntelEvaluator,
)
from app.services.risk_engine.validator import RiskValidator

logger = logging.getLogger("app.services.risk_engine.service")


# ─────────────────────────────────────────────────────────────────────────── #
# Severity mapping (driven by config.py thresholds)                            #
# ─────────────────────────────────────────────────────────────────────────── #

_SEVERITY_MAP = {s: RiskSeverity(s) for _, s in SEVERITY_THRESHOLDS}


def _map_severity(score: float) -> RiskSeverity:
    """Maps a 0-100 score to a RiskSeverity tier using config thresholds."""
    for threshold, severity_str in SEVERITY_THRESHOLDS:
        if score >= threshold:
            return RiskSeverity(severity_str)
    return RiskSeverity.SAFE


def _build_explanation(
    score: float,
    severity: RiskSeverity,
    factors: List[RiskFactor],
    confidence: str,
    was_calibrated: bool,
) -> str:
    """Generates a concise top-level human-readable summary."""
    if not factors:
        return (
            f"No risk signals detected. Overall risk score is {score:.1f}/100 ({severity.value.upper()})."
        )
    top = sorted(factors, key=lambda f: f.score_contribution, reverse=True)
    top_names = ", ".join(f.name for f in top[:3])
    base = (
        f"Risk score {score:.1f}/100 — severity {severity.value.upper()}. "
        f"Top contributing factors: {top_names}."
    )
    if was_calibrated:
        base += f" (Score calibrated for '{confidence}' confidence evidence.)"
    return base


class RiskScoringService:
    """
    Orchestrates the full risk scoring pipeline with validation and calibration.

    Usage:
        service = RiskScoringService()
        score = service.calculate_risk(unified_evidence)
        print(score.overall_score, score.severity, score.explanation)
    """

    def __init__(self) -> None:
        self._evaluators = ALL_EVALUATORS
        self._recommendation_engine = RecommendationEngine()
        self._validator = RiskValidator()
        logger.info(
            f"RiskScoringService initialized with {len(self._evaluators)} evaluator(s). "
            f"Total max raw contribution: {TOTAL_MAX_CONTRIBUTION:.1f}."
        )

    def calculate_risk(
        self,
        unified_evidence: Union[Dict[str, Any], Any],
    ) -> RiskScore:
        """
        Calculates an explainable risk score for the given evidence.

        Parameters
        ----------
        unified_evidence : Either a UnifiedEvidence Pydantic model or a plain dict.
                           If a model, resolved_observations and top-level fields are
                           merged into a single flat evidence dict for evaluation.

        Returns
        -------
        RiskScore with overall_score, severity, breakdown, recommendations, and explanation.
        """
        evidence, indicator = self._extract_evidence(unified_evidence)
        confidence = self._extract_confidence(unified_evidence)

        logger.info(f"[calculate_risk] Starting risk evaluation for indicator: '{indicator}'")

        # ── Step 0: Validate evidence ─────────────────────────────────────── #
        if not self._validator.validate_evidence(evidence):
            logger.info(
                f"[calculate_risk] Empty/invalid evidence for '{indicator}' — returning SAFE/0.0."
            )
            return RiskScore(
                indicator=indicator,
                overall_score=0.0,
                severity=RiskSeverity.SAFE,
                breakdown=RiskBreakdown(),
                recommendations=self._recommendation_engine.generate([], RiskSeverity.SAFE),
                factor_count=0,
                timestamp=datetime.now(timezone.utc),
                explanation="No risk signals detected. Evidence was empty or malformed.",
            )

        # ── Step 1: Run all evaluators ────────────────────────────────────── #
        domain_factors:  List[RiskFactor] = []
        dns_factors:     List[RiskFactor] = []
        tls_factors:     List[RiskFactor] = []
        html_factors:    List[RiskFactor] = []
        ti_factors:      List[RiskFactor] = []

        present_max = 0.0  # dynamic denominator based on categories with data

        for evaluator in self._evaluators:
            results = evaluator.safe_evaluate(evidence)

            # Track which categories have any evidence key present (for denominator)
            category_has_data = self._category_has_evidence(evaluator.category, evidence)

            if category_has_data:
                present_max += evaluator.max_contribution

            if isinstance(evaluator, DomainIntelEvaluator):
                domain_factors = results
            elif isinstance(evaluator, DnsWhoisEvaluator):
                dns_factors = results
            elif isinstance(evaluator, TlsCertificateEvaluator):
                tls_factors = results
            elif isinstance(evaluator, HtmlContentEvaluator):
                html_factors = results
            elif isinstance(evaluator, ThreatIntelEvaluator):
                ti_factors = results

        # ── Step 2: Assemble breakdown ────────────────────────────────────── #
        breakdown = RiskBreakdown(
            domain_intelligence=domain_factors,
            dns_whois=dns_factors,
            tls_certificate=tls_factors,
            html_content=html_factors,
            threat_intelligence=ti_factors,
        )

        all_factors = breakdown.all_factors()
        raw_total = breakdown.total_contribution()

        # ── Step 3: Normalize to 0-100 ────────────────────────────────────── #
        denominator = present_max if present_max > 0 else TOTAL_MAX_CONTRIBUTION
        normalized_score = min(100.0, (raw_total / denominator) * 100.0)
        normalized_score = round(normalized_score, 2)

        # ── Step 4: Calibrate by evidence confidence ──────────────────────── #
        calibrated_score = self._validator.calibrate_score(normalized_score, confidence)
        was_calibrated = calibrated_score != normalized_score

        # ── Step 5: Enforce strict boundaries ─────────────────────────────── #
        final_score = self._validator.enforce_boundaries(calibrated_score)

        # ── Step 6: Map to severity ───────────────────────────────────────── #
        severity = _map_severity(final_score)

        # ── Step 7: Build explanation ─────────────────────────────────────── #
        explanation = _build_explanation(
            final_score, severity, all_factors, confidence, was_calibrated,
        )

        # ── Step 8: Generate analyst recommendations ──────────────────────── #
        recommendations = self._recommendation_engine.generate(
            factors=all_factors,
            severity=severity,
        )

        logger.info(
            f"[calculate_risk] Evaluation complete for '{indicator}': "
            f"raw={normalized_score:.2f}, calibrated={calibrated_score:.2f}, "
            f"final={final_score:.2f}, severity={severity.value}, confidence='{confidence}', "
            f"factors={len(all_factors)}, recommendations={len(recommendations)}, "
            f"denominator={denominator:.2f}."
        )

        return RiskScore(
            indicator=indicator,
            overall_score=final_score,
            severity=severity,
            breakdown=breakdown,
            recommendations=recommendations,
            factor_count=len(all_factors),
            timestamp=datetime.now(timezone.utc),
            explanation=explanation,
        )

    # ── Private helpers ───────────────────────────────────────────────────── #

    @staticmethod
    def _extract_evidence(
        unified_evidence: Union[Dict[str, Any], Any]
    ) -> tuple[Dict[str, Any], str]:
        """
        Normalizes input to a flat evidence dict and extracts the indicator string.

        Accepts:
        - A plain dict (used directly as evidence).
        - A UnifiedEvidence Pydantic model (merges resolved_observations with
          top-level indicator fields).
        """
        if isinstance(unified_evidence, dict):
            indicator = unified_evidence.get("indicator", "unknown")
            return unified_evidence, indicator

        # Pydantic model path
        try:
            resolved = dict(getattr(unified_evidence, "resolved_observations", {}) or {})
            indicator = getattr(unified_evidence, "indicator", "unknown")

            # Inject top-level model fields into the flat dict for evaluators
            if hasattr(unified_evidence, "indicator_type"):
                resolved.setdefault("indicator_type", unified_evidence.indicator_type)
            resolved.setdefault("indicator", indicator)

            # Also inject internal/external evidence keys not yet in resolved
            for source_attr in ("internal_evidence", "external_evidence"):
                src = getattr(unified_evidence, source_attr, None) or {}
                for k, v in src.items():
                    resolved.setdefault(k, v)

            return resolved, indicator
        except Exception as exc:
            logger.warning(f"_extract_evidence fallback to empty dict: {exc}")
            return {}, "unknown"

    @staticmethod
    def _extract_confidence(unified_evidence: Union[Dict[str, Any], Any]) -> str:
        """
        Extracts the overall confidence level from the evidence payload.
        Returns 'unknown' if not found.
        """
        if isinstance(unified_evidence, dict):
            return str(unified_evidence.get("overall_confidence", "unknown"))
        return str(getattr(unified_evidence, "overall_confidence", "unknown"))

    @staticmethod
    def _category_has_evidence(category: str, evidence: Dict[str, Any]) -> bool:
        """
        Determines whether any evidence keys relevant to a category are present.
        Uses the centralized CATEGORY_EVIDENCE_KEYS from config.py.
        """
        keys = CATEGORY_EVIDENCE_KEYS.get(category, frozenset())
        return any(k in evidence for k in keys)
