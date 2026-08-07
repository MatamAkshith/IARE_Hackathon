"""
BaseCorrelationStrategy — Stage 7.2

Defines the abstract interface for all correlation strategies used by the
Campaign Correlation Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.services.campaign_engine.models import CorrelationResult, CorrelationEvidence


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
    def correlate_pair(
        self,
        evidence_a: Dict[str, Any],
        evidence_b: Dict[str, Any],
    ) -> List[CorrelationEvidence]:
        """
        Compares two evidence packages and returns a list of matched CorrelationEvidence.
        """
        pass

    def correlate(
        self,
        current_evidence: Dict[str, Any],
        historical_evidence_list: List[Dict[str, Any]],
    ) -> CorrelationResult:
        """
        Evaluates similarity or infrastructure overlaps between the active
        evidence and a collection of historical evidence records.
        """
        all_evidence: List[CorrelationEvidence] = []
        for hist in historical_evidence_list:
            ev_list = self.correlate_pair(current_evidence, hist)
            if ev_list:
                all_evidence.extend(ev_list)

        # Deduplicate evidence based on type and value
        seen = set()
        deduped_evidence: List[CorrelationEvidence] = []
        for ev in all_evidence:
            key = (ev.type, ev.value)
            if key not in seen:
                seen.add(key)
                deduped_evidence.append(ev)

        is_correlated = len(deduped_evidence) > 0
        return CorrelationResult(
            is_correlated=is_correlated,
            match_score=1.0 if is_correlated else 0.0,
            evidence=deduped_evidence
        )
