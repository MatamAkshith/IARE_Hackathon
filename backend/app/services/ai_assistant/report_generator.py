import logging
from datetime import datetime, timezone
from typing import List

from app.services.ai_assistant.schemas import InvestigationContext
from app.services.ai_assistant.reporting_models import (
    ExecutiveSummary,
    AnalystReport,
    EvidenceSummary,
    RecommendationSummary,
)

logger = logging.getLogger("app.services.ai_assistant.report_generator")


class ReportGeneratorService:
    """
    Generates structured reports for security analysts and executive sponsors
    using the available investigation context.
    """

    def generate_analyst_report(self, context: InvestigationContext) -> AnalystReport:
        """
        Compiles detailed technical facts, timeline audits, infrastructure overlaps,
        and recommendations for security operations center (SOC) analysts.
        """
        logger.info(f"Generating analyst report for indicator: '{context.indicator}'")

        # 1. Build Evidence Summary
        evidence = context.evidence
        obs = evidence.resolved_observations if evidence else {}
        top_findings = self._compile_findings(context)

        ev_summary = EvidenceSummary(
            indicator=context.indicator,
            overall_confidence=str(getattr(evidence, "overall_confidence", "UNKNOWN")),
            observations_count=len(obs) if obs else 0,
            domain_age_days=obs.get("domain_age_days") or obs.get("age_days"),
            registrar=obs.get("registrar"),
            ssl_valid=obs.get("ssl_valid"),
            tls_issuer=obs.get("tls_issuer") or obs.get("cert_issuer"),
            has_login_form=obs.get("has_login_form"),
            forms_count=obs.get("forms_count"),
            virustotal_verdict=obs.get("virustotal_verdict"),
            overall_verdict=obs.get("overall_verdict"),
            top_findings=top_findings,
        )

        # 2. Build Campaign Details
        camp = context.campaign_details
        campaign_id = camp.campaign_id if camp else None
        campaign_members = [m.indicator for m in camp.members] if camp else []
        shared_infra = [f"{inf.type.upper()}: {inf.value}" for inf in camp.shared_infrastructure] if camp else []

        # 3. Build Recommendation Summary
        risk = context.risk_assessment
        imm_actions = []
        mit_steps = []
        if risk and risk.recommendations:
            for r in risk.recommendations:
                if r.priority in ("immediate", "high"):
                    imm_actions.append(f"{r.action} - {r.description}")
                else:
                    mit_steps.append(f"{r.action} - {r.description}")
        else:
            if risk and risk.overall_score >= 70.0:
                imm_actions.append("Escalate alert to perimeter blocking.")
            else:
                mit_steps.append("Log and continue standard network traffic monitoring.")

        rec_summary = RecommendationSummary(
            immediate_actions=imm_actions,
            mitigation_steps=mit_steps,
        )

        # 4. Extract Timeline Events
        timeline_events = []
        if evidence and evidence.audit_trail and evidence.audit_trail.events:
            for ev in evidence.audit_trail.events:
                timestamp_str = ev.timestamp.isoformat() if isinstance(ev.timestamp, datetime) else str(ev.timestamp)
                timeline_events.append(f"[{timestamp_str}] {ev.source} ({ev.event_type}): {ev.description}")

        # 5. Formulate Technical Conclusion
        conclusion = self._formulate_conclusion(context)

        return AnalystReport(
            indicator=context.indicator,
            risk_score=risk.overall_score if risk else 0.0,
            severity=str(getattr(risk, "severity", "SAFE")),
            risk_assessment_explanation=risk.explanation if risk else "No risk assessment data available.",
            evidence_summary=ev_summary,
            campaign_id=campaign_id,
            campaign_members=campaign_members,
            shared_infrastructure=shared_infra,
            recommendations=rec_summary,
            timeline_events=timeline_events,
            conclusion=conclusion,
            created_at=datetime.now(timezone.utc),
        )

    def generate_executive_summary(self, context: InvestigationContext) -> ExecutiveSummary:
        """
        Creates high-level business risk context, potential brand impacts,
        and action plans for C-level presentation.
        """
        logger.info(f"Generating executive summary for indicator: '{context.indicator}'")

        risk = context.risk_assessment
        camp = context.campaign_details

        severity_val = str(getattr(risk, "severity", "SAFE")).upper()
        overall_score = risk.overall_score if risk else 0.0

        is_threat = overall_score >= 70.0 or severity_val in ("HIGH", "CRITICAL")
        
        # Compile executive key findings
        key_findings = []
        if is_threat:
            key_findings.append(f"High risk phishing signals identified for indicator: {context.indicator}.")
        if risk and risk.explanation:
            key_findings.append(risk.explanation)
        
        evidence = context.evidence
        if evidence and evidence.resolved_observations:
            obs = evidence.resolved_observations
            if obs.get("has_login_form"):
                key_findings.append("Suspicious webpage hosts a login input form indicating potential credential harvesting.")
            if obs.get("ssl_valid") is False:
                key_findings.append("Webpage TLS certificate is invalid, creating insecure connections.")

        if not key_findings:
            key_findings.append("No active risk factors or brand threats were identified.")

        # Determine Business Impact
        if is_threat:
            impact = (
                "Critical threat. Left unmitigated, this domain could deceive employees or customers "
                "into exposing critical enterprise login credentials, resulting in unauthorized cloud "
                "data access or credential compromise."
            )
        else:
            impact = (
                "Negligible current business risk. The indicator does not display anomalous brand "
                "spoofing or malicious reputation activity at this time."
            )

        # Formulate Action Plan Summary
        action_plan_lines = []
        if risk and risk.recommendations:
            action_plan_lines.append(f"Immediate: {[r.action for r in risk.recommendations if r.priority == 'immediate'] or ['Triage alert']}")
            action_plan_lines.append("Proceed with perimeter firewall containment and DNS blocking.")
        else:
            action_plan_lines.append("Monitor indicator activity within routine audit logs.")

        action_summary = " ".join(action_plan_lines)

        return ExecutiveSummary(
            indicator=context.indicator,
            overall_risk_rating=severity_val,
            overall_score=overall_score,
            campaign_associated=camp is not None,
            campaign_name=camp.name if camp else None,
            key_findings=key_findings,
            business_impact=impact,
            recommended_action_summary=action_summary,
            created_at=datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # Helper functions
    # -------------------------------------------------------------------------

    def _compile_findings(self, context: InvestigationContext) -> List[str]:
        findings = []
        evidence = context.evidence
        if not evidence or not evidence.resolved_observations:
            return ["No evidence observations recorded."]

        obs = evidence.resolved_observations

        # Age
        age = obs.get("domain_age_days") or obs.get("age_days")
        if age is not None:
            findings.append(f"Domain registered {age} days ago.")

        # SSL
        if obs.get("ssl_valid") is False:
            findings.append("Insecure certificate / SSL validation failed.")
        elif obs.get("ssl_valid") is True:
            findings.append(f"Valid TLS certificate issued by {obs.get('tls_issuer') or obs.get('cert_issuer') or 'unknown issuer'}.")

        # Webpage content details
        if obs.get("has_login_form"):
            findings.append("Webpage contains form structures designed to capture user inputs.")
        if obs.get("password_inputs", 0) > 0:
            findings.append(f"Detected {obs.get('password_inputs')} password input fields.")

        # Threat Intel
        verdict = obs.get("overall_verdict")
        if verdict and verdict not in ("clean", "unknown"):
            findings.append(f"External reputation engines classified domain status as '{verdict}'.")

        # Campaign info
        camp = context.campaign_details
        if camp:
            findings.append(f"Correlated to attacker campaign '{camp.name}' sharing infrastructure overlaps.")

        if not findings:
            findings.append("Indicator behaves as standard benign web traffic.")

        return findings

    def _formulate_conclusion(self, context: InvestigationContext) -> str:
        risk = context.risk_assessment
        camp = context.campaign_details

        if not risk:
            return "Unable to compile formal conclusion due to missing risk assessment metrics."

        if risk.overall_score >= 90.0:
            conclusion = (
                f"Critical risk confirmed. This indicator shows a pattern of brand impersonation. "
                f"It is highly recommended to block this host immediately."
            )
        elif risk.overall_score >= 70.0:
            conclusion = (
                f"High probability of malicious intent. The combination of domain indicators, "
                f"reputation verdicts, and page structures indicates an active phishing risk."
            )
        elif risk.overall_score >= 41.0:
            conclusion = (
                f"Medium risk. The indicator exhibits suspicious features. Regular monitoring is recommended."
            )
        else:
            conclusion = (
                f"Safe/Low risk. The indicator does not pose a threat to brand assets at this time."
            )

        if camp:
            conclusion += f" Attributed to campaign group '{camp.name}' (ID: {camp.campaign_id})."

        return conclusion
