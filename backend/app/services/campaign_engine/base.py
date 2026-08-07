"""
BaseCorrelationStrategy — Stage 7.1

Defines the abstract interface for all correlation strategies used by the
Campaign Correlation Engine. Subclasses will implement concrete algorithms
(e.g., matching IPs, nameservers, HTML structural similarities, or favicon hashes).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.services.campaign_engine.models import CorrelationResult


class BaseCorrelationStrategy(ABC):
    """
    Abstract base interface for a single campaign correlation strategy.
    
    Each strategy class analyzes one or more specific dimensions of indicator
    evidence (e.g., network details, webpage content similarity, DNS configuration)
    to check for overlap.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """
        Returns the unique identifier string of the strategy (e.g., 'shared_ip').
        """
        pass

    @abstractmethod
    def correlate(
        self,
        current_evidence: Dict[str, Any],
        historical_evidence_list: List[Dict[str, Any]],
    ) -> CorrelationResult:
        """
        Evaluates similarity or infrastructure overlaps between the active
        evidence and a collection of historical evidence records.

        Parameters
        ----------
        current_evidence         : Flat dictionary representing the current investigation features.
        historical_evidence_list : List of flat dictionaries representing past investigation features.

        Returns
        -------
        CorrelationResult containing the boolean verdict, similarity score, and details
        of the overlapping evidence matched.
        """
        pass
