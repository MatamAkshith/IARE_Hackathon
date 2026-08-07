import logging
from datetime import datetime
from typing import Any, Optional

from app.services.ai_assistant.schemas import InvestigationContext
from app.services.unified_evidence.models import UnifiedEvidence
from app.services.risk_engine.models import RiskScore
from app.services.campaign_engine.models import Campaign

logger = logging.getLogger("app.services.ai_assistant.context_builder")


def _fmt(val: Any) -> str:
    """
    Helper to format values, mapping empty/None values to 'Not Available'.
    """
    if val is None or val == "" or val == [] or val == {}:
        return "Not Available"
    if isinstance(val, list):
        return ", ".join(str(x) for x in val)
    if isinstance(val, datetime):
        return val.isoformat()
    return str(val)


class InvestigationContextBuilder:
    """
    Aggregates threat intelligence features, explainable risk details, and campaign
    correlation footprints to build a structured context package for the AI assistant.
    """

    def build_context(
        self,
        indicator: str,
        evidence: Optional[Any] = None,
        risk_assessment: Optional[Any] = None,
        campaign_details: Optional[Any] = None,
    ) -> InvestigationContext:
        """
        Accepts raw/model investigation data, handles validation, and returns an
        InvestigationContext schema. Handles missing attributes gracefully.
        """
        logger.info(f"Building investigation context for indicator: '{indicator}'")

        parsed_evidence = None
        if evidence is not None:
            if isinstance(evidence, UnifiedEvidence):
                parsed_evidence = evidence
            elif isinstance(evidence, dict):
                try:
                    parsed_evidence = UnifiedEvidence.model_validate(evidence)
                except Exception as e:
                    logger.warning(f"Failed to validate evidence dict: {e}")
            else:
                try:
                    parsed_evidence = UnifiedEvidence.model_validate(evidence)
                except Exception as e:
                    logger.warning(f"Failed to parse evidence model: {e}")

        parsed_risk = None
        if risk_assessment is not None:
            if isinstance(risk_assessment, RiskScore):
                parsed_risk = risk_assessment
            elif isinstance(risk_assessment, dict):
                try:
                    parsed_risk = RiskScore.model_validate(risk_assessment)
                except Exception as e:
                    logger.warning(f"Failed to validate risk dict: {e}")
            else:
                try:
                    parsed_risk = RiskScore.model_validate(risk_assessment)
                except Exception as e:
                    logger.warning(f"Failed to parse risk model: {e}")

        parsed_campaign = None
        if campaign_details is not None:
            if isinstance(campaign_details, Campaign):
                parsed_campaign = campaign_details
            elif isinstance(campaign_details, dict):
                try:
                    parsed_campaign = Campaign.model_validate(campaign_details)
                except Exception as e:
                    logger.warning(f"Failed to validate campaign dict: {e}")
            else:
                try:
                    parsed_campaign = Campaign.model_validate(campaign_details)
                except Exception as e:
                    logger.warning(f"Failed to parse campaign model: {e}")

        return InvestigationContext(
            indicator=indicator,
            evidence=parsed_evidence,
            risk_assessment=parsed_risk,
            campaign_details=parsed_campaign,
        )

    def generate_system_prompt(self, context: InvestigationContext) -> str:
        """
        Serializes the structured context and injects it into a comprehensive
        base prompt template designed for security analyst LLM generation.
        """
        logger.debug(f"Assembling system prompt for indicator: '{context.indicator}'")

        # Extract structured metrics
        risk_score = context.risk_assessment.overall_score if context.risk_assessment else 0.0
        severity = _fmt(context.risk_assessment.severity.value if context.risk_assessment and hasattr(context.risk_assessment.severity, 'value') else (context.risk_assessment.severity if context.risk_assessment else 'SAFE')).upper()
        
        # Collect IOCs
        iocs_list = [context.indicator]
        obs = context.evidence.resolved_observations if context.evidence else {}
        if obs.get("ip_address"):
            iocs_list.append(obs["ip_address"])
        iocs = ", ".join(iocs_list)

        # Domain metadata
        domain_metadata = (
            f"Registrar: {_fmt(obs.get('registrar'))} | "
            f"Age: {_fmt(obs.get('domain_age_days') or obs.get('age_days'))} days | "
            f"Title: {_fmt(obs.get('page_title') or obs.get('title'))}"
        )

        # Campaign info
        camp = context.campaign_details
        if camp:
            campaign_info = (
                f"Campaign ID: {_fmt(camp.campaign_id)} | "
                f"Name: {_fmt(camp.name)} | "
                f"Severity: {_fmt(camp.severity.value if hasattr(camp.severity, 'value') else camp.severity).upper()} | "
                f"Status: {_fmt(camp.status.value if hasattr(camp.status, 'value') else camp.status).upper()} | "
                f"Total members: {len(camp.members)}"
            )
        else:
            campaign_info = "No associated campaign (isolated threat outlier)."

        lines = [
            "You are ThreatLens AI, a specialized Tier-2 Security Co-pilot and Phishing/Brand Impersonation Investigator.",
            "Analyze the target indicator using the factual, structured investigation context provided below.",
            "Do not hallucinate features or make assumptions beyond the scope of this structured evidence.",
            "",
            f"=== TARGET INDICATOR under investigation: {context.indicator} ===",
            "",
            "=== STRUCTURED BACKEND CONTEXT ===",
            f"Risk Score: {risk_score:.1f}/100",
            f"Severity: {severity}",
            f"IOCs: {iocs}",
            f"Domain Metadata: {domain_metadata}",
            f"Campaign Info: {campaign_info}",
            "",
            f"=== TARGET INDICATOR under investigation: {context.indicator} ===",
        ]

        # 1. Target Indicator Details
        if context.evidence:
            lines.append(f"Indicator Type: {_fmt(context.evidence.indicator_type)}")
            lines.append(f"Evidence Consensus Confidence: {_fmt(context.evidence.overall_confidence.value if hasattr(context.evidence.overall_confidence, 'value') else context.evidence.overall_confidence)}")
        else:
            lines.append("Indicator Type: Not Available")
            lines.append("Evidence Consensus Confidence: Not Available")

        # 2. Risk Assessment Engine Details
        lines.append("\n[RISK SCORING ASSESSMENT]")
        if context.risk_assessment:
            ra = context.risk_assessment
            lines.append(f"Overall Risk Score: {ra.overall_score:.1f}/100")
            lines.append(f"Risk Severity Tier: {severity}")
            lines.append(f"Primary Verdict Rationale: {_fmt(ra.explanation)}")
            
            lines.append("\nFired Risk Rules & Factors:")
            factors = ra.breakdown.all_factors() if ra.breakdown else []
            if factors:
                for f in factors:
                    lines.append(f"  - [{f.name}] Contributed: {f.score_contribution:.1f} pts | {f.description}")
            else:
                lines.append("  - No indicators triggered any risk scoring rules.")

            lines.append("\nActionable SOC Recommendations:")
            if ra.recommendations:
                for r in ra.recommendations:
                    lines.append(f"  - [{_fmt(r.priority).upper()}] {r.action} (Reason: {r.description})")
            else:
                lines.append("  - No recommended actions generated.")
        else:
            lines.append("Risk Assessment Scoring: Not Available")

        # 3. Unified Evidence (Resolved Observations)
        lines.append("\n[UNIFIED EVIDENCE OBSERVATIONS]")
        if context.evidence and context.evidence.resolved_observations:
            # DNS & WHOIS
            lines.append("DNS & WHOIS Registrar Data:")
            lines.append(f"  - Registrar: {_fmt(obs.get('registrar'))}")
            lines.append(f"  - Creation Date: {_fmt(obs.get('creation_date'))}")
            lines.append(f"  - Expiration Date: {_fmt(obs.get('expiration_date'))}")
            lines.append(f"  - Domain Age (Days): {_fmt(obs.get('domain_age_days') or obs.get('age_days'))}")
            lines.append(f"  - MX Records: {_fmt(obs.get('mx_records'))}")
            lines.append(f"  - NS Records: {_fmt(obs.get('ns_records'))}")
            lines.append(f"  - WHOIS Privacy Enabled: {_fmt(obs.get('whois_privacy') or obs.get('registrant_redacted'))}")

            # TLS Certificate
            lines.append("TLS Certificate Properties:")
            lines.append(f"  - TLS Handshake Valid: {_fmt(obs.get('ssl_valid'))}")
            lines.append(f"  - TLS Certificate Issuer: {_fmt(obs.get('tls_issuer') or obs.get('cert_issuer'))}")
            lines.append(f"  - TLS Days to Expiry: {_fmt(obs.get('cert_days_remaining'))}")

            # HTML Webpage Analysis
            lines.append("Webpage HTML Extraction Elements:")
            lines.append(f"  - Page Title Tag: {_fmt(obs.get('page_title') or obs.get('title'))}")
            lines.append(f"  - Password Form Elements: {_fmt(obs.get('password_inputs'))}")
            lines.append(f"  - Has Login Form: {_fmt(obs.get('has_login_form'))}")
            lines.append(f"  - Total Forms Count: {_fmt(obs.get('forms_count'))}")

            # Threat Intel Feeds
            lines.append("External Reputation Threat Intelligence:")
            lines.append(f"  - Consolidated Feeds Verdict: {_fmt(obs.get('overall_verdict'))}")
            lines.append(f"  - VirusTotal Classification: {_fmt(obs.get('virustotal_verdict'))}")
            lines.append(f"  - PhishTank Classification: {_fmt(obs.get('phishtank_verdict'))}")
            lines.append(f"  - URLHaus Classification: {_fmt(obs.get('urlhaus_verdict'))}")
            lines.append(f"  - AbuseIPDB Confidence: {_fmt(obs.get('abuse_confidence_score'))}")
            lines.append(f"  - AlienVault OTX Pulses Count: {_fmt(obs.get('pulse_count'))}")
        else:
            lines.append("Unified observations and feature extraction records: Not Available")

        # 4. Campaign Correlation
        lines.append("\n[CAMPAIGN CLUSTERING CORRELATION]")
        if context.campaign_details:
            lines.append(f"Campaign ID: {_fmt(camp.campaign_id)}")
            lines.append(f"Campaign Alias Name: {_fmt(camp.name)}")
            lines.append(f"Operational Tracking Status: {_fmt(camp.status.value if hasattr(camp.status, 'value') else camp.status).upper()}")
            lines.append(f"Assigned Campaign Threat Severity: {_fmt(camp.severity.value if hasattr(camp.severity, 'value') else camp.severity).upper()}")
            lines.append(f"Total Correlated Member Indicators: {_fmt(camp.summary.total_indicators if camp.summary else len(camp.members))}")

            lines.append("\nShared Infrastructure Footprints Overlaps:")
            if camp.shared_infrastructure:
                for inf in camp.shared_infrastructure:
                    lines.append(f"  - [{_fmt(inf.type).upper()}] Value: {_fmt(inf.value)} | confidence={_fmt(inf.confidence)} | {inf.description}")
            else:
                lines.append("  - No active overlaps found with shared registrar/IP/TLS certificate infrastructure.")

            lines.append("\nCoordinated Campaign Members (Sample):")
            if camp.members:
                for idx, mb in enumerate(camp.members[:10]):
                    lines.append(f"  - {mb.indicator} (type={mb.indicator_type})")
                if len(camp.members) > 10:
                    lines.append(f"  - ... and {len(camp.members) - 10} other linked indicator(s)")
            else:
                lines.append("  - No active members registered to this cluster.")
        else:
            lines.append("No campaigns associated. This indicator behaves as an isolated outlier and is not correlated to broader attacker group infrastructures.")

        # AI Instruction Footer
        lines.extend([
            "",
            "=== AI RESPONDING INSTRUCTIONS ===",
            "You are a SOC Analyst reporting on deterministic backend metrics.",
            f"You MUST base your summary strictly on the provided Risk Score ({risk_score:.1f}) and Severity ({severity}).",
            "Do NOT state the risk is negligible if the Severity is HIGH or CRITICAL.",
            f"Explicitly list the provided IOCs in your report: {iocs}.",
            "Maintain a highly technical, objective tone.",
            "Synthesize the risk factors and explain clearly why this indicator is safe or malicious.",
            "Map out any overlaps or campaigns that suggest an active brand threat.",
            "Recommend specific containment or mitigation actions (e.g. block IP, report URL, revoke TLS, alert user).",
        ])

        return "\n".join(lines)
