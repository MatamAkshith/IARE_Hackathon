"""
Abstract base interface for all category-level risk evaluators.

Each concrete evaluator is responsible for a single evidence domain
(e.g., Domain Intelligence, Threat Intelligence) and produces a list
of RiskFactor objects representing the factors that fired.

Design contract:
  - evaluate() MUST NOT raise; it should return an empty list on failure.
  - evaluate() receives the full resolved_observations dict and may safely
    access any key using .get() with a default.
  - evaluate() is stateless and idempotent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.services.risk_engine.models import RiskFactor


class BaseRiskEvaluator(ABC):
    """
    Abstract base class for a single-category risk evaluator.

    Subclasses implement evaluate() to inspect specific evidence keys
    and return a list of fired RiskFactor objects.
    """

    #: Human-readable name of the category this evaluator handles.
    category: str = "unknown"

    #: Maximum raw score this evaluator can contribute before normalization.
    #: Used by the service to compute the dynamic denominator for 0-100 scaling.
    max_contribution: float = 0.0

    @abstractmethod
    def evaluate(self, evidence: Dict[str, Any]) -> List[RiskFactor]:
        """
        Evaluate the relevant slice of evidence and return fired risk factors.

        Parameters
        ----------
        evidence : The resolved_observations dict from UnifiedEvidence.

        Returns
        -------
        List of RiskFactor objects for every rule that fired.
        An empty list means no risk signals were found in this category.
        """

    def safe_evaluate(self, evidence: Dict[str, Any]) -> List[RiskFactor]:
        """
        Defensive wrapper around evaluate() that catches any uncaught exception
        and returns an empty list, ensuring the pipeline never crashes on a
        single evaluator failure.
        """
        try:
            return self.evaluate(evidence)
        except Exception as exc:  # noqa: BLE001
            import logging
            logging.getLogger(f"app.services.risk_engine.{self.category}").warning(
                f"Evaluator '{self.category}' failed gracefully: {exc}"
            )
            return []
