"""
RiskValidator — Stage 6.5

Provides three safety gates for the risk scoring pipeline:

1. validate_evidence()    — rejects empty/malformed evidence before evaluation.
2. calibrate_score()      — scales the raw score by the evidence confidence level.
3. enforce_boundaries()   — deterministically clamps the final score to [0.0, 100.0].

These gates are called by RiskScoringService.calculate_risk() around the
core evaluator logic, ensuring no edge case can produce an out-of-range,
NaN, or infinity score.
"""

import logging
import math
from typing import Any, Dict

from app.services.risk_engine.config import (
    CONFIDENCE_MULTIPLIERS,
    DEFAULT_CONFIDENCE_MULTIPLIER,
)

logger = logging.getLogger("app.services.risk_engine.validator")


class RiskValidator:
    """
    Stateless validation and calibration utilities for the risk pipeline.
    All methods are safe to call on arbitrary input — they never raise.
    """

    # ── Gate 1: Evidence validation ───────────────────────────────────────── #

    @staticmethod
    def validate_evidence(evidence: Dict[str, Any]) -> bool:
        """
        Checks whether the evidence dict contains any meaningful data
        that the evaluators can process.

        Returns True if valid (continue pipeline), False if invalid
        (short-circuit to SAFE / 0.0).

        Invalid conditions:
        - evidence is None, not a dict, or empty.
        - All values are None, empty strings, or empty lists.
        - evidence contains only the 'indicator' key with no actual data.
        """
        if not evidence or not isinstance(evidence, dict):
            logger.warning("validate_evidence: evidence is None, empty, or not a dict.")
            return False

        # Filter out the 'indicator' key itself — it's metadata, not evidence
        data_keys = {k: v for k, v in evidence.items() if k != "indicator"}

        if not data_keys:
            logger.warning("validate_evidence: evidence contains only the indicator key, no data.")
            return False

        # Check if every value is effectively null
        has_meaningful_value = any(
            v is not None and v != "" and v != []
            for v in data_keys.values()
        )

        if not has_meaningful_value:
            logger.warning("validate_evidence: all evidence values are null/empty.")
            return False

        logger.debug(f"validate_evidence: {len(data_keys)} data key(s) validated OK.")
        return True

    # ── Gate 2: Confidence calibration ────────────────────────────────────── #

    @staticmethod
    def calibrate_score(raw_score: float, confidence: str) -> float:
        """
        Scales the raw normalized score by the confidence multiplier.

        A "high" confidence evidence passes the score through at 1.0×.
        Lower confidence levels reduce the score proportionally, preventing
        low-reliability evidence from generating falsely alarming scores.

        Parameters
        ----------
        raw_score  : The 0-100 normalized score before calibration.
        confidence : The overall_confidence string from UnifiedEvidence
                     (expected values: 'high', 'medium', 'low', 'unknown').

        Returns
        -------
        The calibrated score (still needs enforce_boundaries() afterward).
        """
        key = confidence.lower().strip() if isinstance(confidence, str) else "unknown"
        multiplier = CONFIDENCE_MULTIPLIERS.get(key, DEFAULT_CONFIDENCE_MULTIPLIER)

        calibrated = raw_score * multiplier

        if multiplier < 1.0:
            logger.info(
                f"calibrate_score: {raw_score:.2f} × {multiplier} "
                f"(confidence='{key}') → {calibrated:.2f}"
            )

        return calibrated

    # ── Gate 3: Boundary enforcement ──────────────────────────────────────── #

    @staticmethod
    def enforce_boundaries(score: float) -> float:
        """
        Deterministically clamps the score to [0.0, 100.0].

        Also handles NaN, infinity, and non-numeric values by mapping them
        to 0.0 with a warning.
        """
        if not isinstance(score, (int, float)) or math.isnan(score) or math.isinf(score):
            logger.warning(
                f"enforce_boundaries: non-numeric or infinite score '{score}' clamped to 0.0."
            )
            return 0.0

        clamped = max(0.0, min(100.0, float(score)))
        clamped = round(clamped, 2)

        if clamped != round(float(score), 2):
            logger.debug(f"enforce_boundaries: score {score:.2f} clamped to {clamped:.2f}.")

        return clamped
