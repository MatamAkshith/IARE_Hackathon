"""
Risk Scoring Engine (Milestone 6)
==================================
Provides explainable, weighted, rule-based risk assessment of indicators
using standardized UnifiedEvidence from Milestone 5.

Public surface:
  - RiskScoringService   : main orchestrator
  - RiskScore            : complete scored result
  - RiskSeverity         : severity enum (SAFE → CRITICAL)
  - RiskBreakdown        : category-level factor groupings
  - RiskFactor           : individual explainable contribution
"""

from app.services.risk_engine.models import (
    RiskSeverity,
    RiskFactor,
    RiskBreakdown,
    RiskScore,
)
from app.services.risk_engine.service import RiskScoringService

__all__ = [
    "RiskSeverity",
    "RiskFactor",
    "RiskBreakdown",
    "RiskScore",
    "RiskScoringService",
]
