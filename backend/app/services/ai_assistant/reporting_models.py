from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceSummary(BaseModel):
    """
    Structured summary of the technical evidence gathered for an indicator.
    """
    indicator: str = Field(..., description="The target URL, domain, or IP")
    overall_confidence: str = Field(..., description="Consensus evidence confidence level (e.g. HIGH/MEDIUM/LOW)")
    observations_count: int = Field(default=0, description="Total number of resolved key-value observations")
    domain_age_days: Optional[int] = Field(None, description="Age of the domain in days")
    registrar: Optional[str] = Field(None, description="Domain registrar name")
    ssl_valid: Optional[bool] = Field(None, description="Whether the SSL/TLS certificate is valid")
    tls_issuer: Optional[str] = Field(None, description="SSL/TLS certificate issuer")
    has_login_form: Optional[bool] = Field(None, description="Whether the webpage hosts a login form")
    forms_count: Optional[int] = Field(None, description="Total HTML forms found on the page")
    virustotal_verdict: Optional[str] = Field(None, description="VirusTotal reputation feed verdict")
    overall_verdict: Optional[str] = Field(None, description="Consensus verdict from threat intelligence")
    top_findings: List[str] = Field(default_factory=list, description="Top key findings extracted from observations")


class RecommendationSummary(BaseModel):
    """
    Prioritized action plan recommended for containment and mitigation.
    """
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate containment actions (priority: immediate/high)")
    mitigation_steps: List[str] = Field(default_factory=list, description="Medium/long-term mitigation and analysis steps")


class ExecutiveSummary(BaseModel):
    """
    High-level, business-oriented report summary for executive leadership.
    """
    indicator: str = Field(..., description="Target indicator under review")
    overall_risk_rating: str = Field(..., description="Risk severity tier (SAFE/LOW/MEDIUM/HIGH/CRITICAL)")
    overall_score: float = Field(..., description="0-100 normalized risk score value")
    campaign_associated: bool = Field(default=False, description="Whether the indicator is part of a coordinated campaign")
    campaign_name: Optional[str] = Field(None, description="Name of the correlated campaign, if any")
    key_findings: List[str] = Field(default_factory=list, description="Top high-level critical risk indicators")
    business_impact: str = Field(..., description="Estimated risk exposure and impact to brand/users")
    recommended_action_summary: str = Field(..., description="Executive summary of remediation requirements")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of report creation")


class AnalystReport(BaseModel):
    """
    Detailed, technical investigation report for Security Operations Center (SOC) analysts.
    """
    indicator: str = Field(..., description="The indicator under investigation")
    risk_score: float = Field(..., description="0-100 normalized risk score")
    severity: str = Field(..., description="Risk severity level")
    risk_assessment_explanation: str = Field(..., description="Top-level explanation from the risk engine")
    evidence_summary: EvidenceSummary = Field(..., description="Technical evidence observations summary")
    campaign_id: Optional[str] = Field(None, description="Unique identifier of correlated campaign, if any")
    campaign_members: List[str] = Field(default_factory=list, description="Other indicators linked to the same campaign")
    shared_infrastructure: List[str] = Field(default_factory=list, description="Details of overlapping footprint connections")
    recommendations: RecommendationSummary = Field(..., description="Detailed mitigation recommendations")
    timeline_events: List[str] = Field(default_factory=list, description="Audit trail events representing evidence processing history")
    conclusion: str = Field(..., description="Security analyst conclusion and final threat assessment")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of report creation")
