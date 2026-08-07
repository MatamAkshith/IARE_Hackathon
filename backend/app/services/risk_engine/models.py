from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RiskSeverity(str, Enum):
    """
    Five-tier severity classification mapped from the 0-100 risk score.

    Score ranges:
        SAFE     :   0 – 20   (clean or insufficient evidence)
        LOW      :  21 – 40   (minor indicators, likely benign)
        MEDIUM   :  41 – 70   (notable signals, warrants monitoring)
        HIGH     :  71 – 90   (strong indicators of malicious intent)
        CRITICAL :  91 – 100  (confirmed or near-certain phishing/impersonation)
    """
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskFactor(BaseModel):
    """
    A single explainable contributor to the overall risk score.

    Attributes:
        name               : Short, human-readable factor label.
        score_contribution : Raw points this factor adds to the score (>= 0).
        description        : Sentence explaining why this factor was triggered.
        weight             : The configured weight for this factor category.
        evidence_key       : The specific evidence key that triggered this factor.
    """
    name: str
    score_contribution: float = Field(ge=0.0)
    description: str
    weight: float = Field(default=1.0, ge=0.0)
    evidence_key: Optional[str] = None


class RiskBreakdown(BaseModel):
    """
    Categorized grouping of RiskFactor objects by evidence domain.
    Each category key maps to the list of factors that fired within it.
    Missing / unevaluated categories are represented by an empty list.
    """
    domain_intelligence: List[RiskFactor] = Field(default_factory=list)
    dns_whois: List[RiskFactor] = Field(default_factory=list)
    tls_certificate: List[RiskFactor] = Field(default_factory=list)
    html_content: List[RiskFactor] = Field(default_factory=list)
    threat_intelligence: List[RiskFactor] = Field(default_factory=list)

    def all_factors(self) -> List[RiskFactor]:
        """Returns a flat list of every factor across all categories."""
        return (
            self.domain_intelligence
            + self.dns_whois
            + self.tls_certificate
            + self.html_content
            + self.threat_intelligence
        )

    def total_contribution(self) -> float:
        """Sums raw score contributions across all categories."""
        return sum(f.score_contribution for f in self.all_factors())


class Recommendation(BaseModel):
    """
    An actionable analyst recommendation derived from triggered risk factors.

    Attributes:
        action      : Short imperative phrase describing what to do.
        priority    : 'immediate', 'high', 'medium', or 'low'.
        description : Full sentence explaining the rationale and steps.
        factor      : Name of the triggering RiskFactor (for traceability).
    """
    action: str
    priority: str  # 'immediate' | 'high' | 'medium' | 'low'
    description: str
    factor: Optional[str] = None


class RiskScore(BaseModel):
    """
    The complete, explainable risk assessment for a single indicator.

    Attributes:
        indicator       : The URL, domain, or IP that was evaluated.
        overall_score   : Normalized 0-100 risk score.
        severity        : Severity tier mapped from overall_score.
        breakdown       : Category-level explainability breakdown.
        recommendations : Prioritized list of analyst action recommendations.
        factor_count    : Total number of risk factors that fired.
        timestamp       : UTC timestamp of when the score was calculated.
        explanation     : Top-level human-readable summary sentence.
    """
    indicator: str
    overall_score: float = Field(ge=0.0, le=100.0)
    severity: RiskSeverity
    breakdown: RiskBreakdown
    recommendations: List[Recommendation] = Field(default_factory=list)
    factor_count: int = Field(default=0, ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    explanation: str = ""
