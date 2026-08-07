import logging
from datetime import datetime, timezone
from typing import List, Tuple

from app.services.ai_assistant.schemas import AssistantResponse, AssistantMessage, SuggestedAction, InvestigationContext
from app.services.ai_assistant.models import ResponseType

logger = logging.getLogger("app.services.ai_assistant.reasoning")


class InvestigationReasoningService:
    """
    Deterministic AI reasoning engine that analyzes context indicators,
    evaluates campaign infrastructure connections, maps remediation priorities,
    and handles conversational analyst questions using keyword routing.
    """

    def analyze_context(self, context: InvestigationContext) -> List[SuggestedAction]:
        """
        Evaluates risk factors and campaign infrastructure signals from the context
        and returns a deduplicated list of SuggestedActions.
        """
        actions = []
        if not context:
            return actions

        # 1. Inspect Risk Assessment Engine findings
        risk = context.risk_assessment
        if risk:
            if risk.overall_score >= 90.0:
                actions.append(SuggestedAction(
                    label="Block Indicator",
                    action_type="block",
                    payload={"indicator": context.indicator, "reason": f"Critical risk score: {risk.overall_score:.1f}/100"}
                ))
                actions.append(SuggestedAction(
                    label="Escalate Alert",
                    action_type="escalate",
                    payload={"indicator": context.indicator, "severity": "critical", "score": risk.overall_score}
                ))
            elif risk.overall_score >= 70.0:
                actions.append(SuggestedAction(
                    label="Escalate Alert",
                    action_type="escalate",
                    payload={"indicator": context.indicator, "severity": "high", "score": risk.overall_score}
                ))
            elif risk.overall_score >= 41.0:
                actions.append(SuggestedAction(
                    label="Triage Queue",
                    action_type="triage",
                    payload={"indicator": context.indicator, "severity": "medium", "score": risk.overall_score}
                ))

            # Add prioritised action recommendations
            for rec in risk.recommendations:
                if rec.priority in ("immediate", "high"):
                    actions.append(SuggestedAction(
                        label=f"Mitigation: {rec.action}",
                        action_type="mitigate",
                        payload={"action": rec.action, "priority": rec.priority, "description": rec.description}
                    ))

        # 2. Inspect Evidence resolved observations
        evidence = context.evidence
        if evidence and evidence.resolved_observations:
            obs = evidence.resolved_observations

            # Domain age checks
            domain_age = obs.get("domain_age_days") or obs.get("age_days")
            if domain_age is not None and isinstance(domain_age, (int, float)) and domain_age <= 30:
                actions.append(SuggestedAction(
                    label="Report Registrar Abuse",
                    action_type="report_registrar",
                    payload={"domain": context.indicator, "registrar": obs.get("registrar"), "age_days": domain_age}
                ))

            # Login form or password detection check
            if obs.get("has_login_form") or obs.get("password_inputs", 0) > 0:
                actions.append(SuggestedAction(
                    label="Inspect Login Forms",
                    action_type="inspect_forms",
                    payload={"url": context.indicator, "forms_count": obs.get("forms_count", 0)}
                ))

            # Certificate issues check
            if obs.get("ssl_valid") is False:
                actions.append(SuggestedAction(
                    label="Inspect Certificate Chains",
                    action_type="inspect_tls",
                    payload={"domain": context.indicator, "issuer": obs.get("tls_issuer")}
                ))

        # 3. Inspect Campaign clustering info
        camp = context.campaign_details
        if camp:
            # Shared IP block suggested
            shared_ips = [inf.value for inf in camp.shared_infrastructure if inf.type == "shared_ip"]
            actions.append(SuggestedAction(
                label="Block Campaign Infrastructure",
                action_type="block_infra",
                payload={"campaign_id": camp.campaign_id, "shared_ips": shared_ips}
            ))

            if len(camp.members) > 1:
                actions.append(SuggestedAction(
                    label="Pivot Correlated Indicators",
                    action_type="pivot_campaign",
                    payload={"campaign_id": camp.campaign_id, "members_count": len(camp.members)}
                ))

        # Deduplicate suggestions by label + action_type
        seen = set()
        deduped = []
        for act in actions:
            key = (act.label, act.action_type)
            if key not in seen:
                seen.add(key)
                deduped.append(act)

        return deduped

    def answer_question(self, query: str, context: InvestigationContext) -> AssistantResponse:
        """
        Routes query strings using simple keyword detection, building structured responses.
        """
        logger.info(f"Answering query: '{query}' for indicator: '{context.indicator}'")
        query_lower = query.lower().strip()

        # Intent classification
        if any(w in query_lower for w in ("why", "risky", "risk", "threat", "severity", "score", "malicious")):
            content, confidence = self._explain_risk(context)
        elif any(w in query_lower for w in ("infrastructure", "shared", "campaign", "overlap", "related", "member")):
            content, confidence = self._explain_campaign(context)
        elif any(w in query_lower for w in ("investigate", "next", "todo", "recommendation", "action", "step")):
            content, confidence = self._explain_recommendations(context)
        else:
            content, confidence = self._default_explanation(context)

        # Build actions matching the context
        suggested_actions = self.analyze_context(context)

        return AssistantResponse(
            message=AssistantMessage(
                role="assistant",
                content=f"**Confidence Estimation: {confidence}**\n\n{content}",
                timestamp=datetime.now(timezone.utc)
            ),
            suggested_actions=suggested_actions,
            response_type=ResponseType.CHAT
        )

    # -------------------------------------------------------------------------
    # Intent Explanation Helpers
    # -------------------------------------------------------------------------

    def _explain_risk(self, context: InvestigationContext) -> Tuple[str, str]:
        """Provides dynamic technical analysis of why an indicator is safe/risky."""
        risk = context.risk_assessment
        if not risk:
            return f"No explainable risk scoring dataset is currently available for **{context.indicator}**.", "Low"

        factors = risk.breakdown.all_factors() if risk.breakdown else []
        if factors:
            factor_lines = []
            for f in factors:
                factor_lines.append(f"- **{f.name}** (contribution: {f.score_contribution:.1f} pts) - {f.description}")
            factor_str = "\n".join(factor_lines)
        else:
            factor_str = "No specific negative heuristics or risk scoring rules were triggered."

        content = (
            f"The indicator **{context.indicator}** has an overall threat score of **{risk.overall_score:.1f}/100**, placing it in the **{risk.severity.value.upper()}** severity tier.\n\n"
            f"**Verdict Rationale:** {risk.explanation}\n\n"
            f"**Triggered Heuristics Breakdown:**\n{factor_str}"
        )
        return content, "High"

    def _explain_campaign(self, context: InvestigationContext) -> Tuple[str, str]:
        """Analyzes active campaign memberships and footprints overlaps."""
        camp = context.campaign_details
        if not camp:
            return f"The indicator **{context.indicator}** is not currently linked to any known coordinated phishing campaigns. It behaves as an isolated threat outlier.", "Medium"

        members = [f"- `{m.indicator}` ({m.indicator_type})" for m in camp.members[:5]]
        members_str = "\n".join(members)
        if len(camp.members) > 5:
            members_str += f"\n- ... and {len(camp.members) - 5} other linked campaign domains/IPs"

        infra_lines = []
        if camp.shared_infrastructure:
            for inf in camp.shared_infrastructure:
                infra_lines.append(f"- **[{inf.type.upper()}]** `{inf.value}` (confidence: {inf.confidence}) — {inf.description}")
            infra_str = "\n".join(infra_lines)
        else:
            infra_str = "No active infrastructure elements are shared between these domains."

        content = (
            f"This indicator is connected to a coordinated phishing campaign named **{camp.name}** (ID: `{camp.campaign_id}`) with status **{camp.status.value.upper()}** and severity **{camp.severity.value.upper()}**.\n\n"
            f"**Linked Campaign Members ({len(camp.members)} total):**\n{members_str}\n\n"
            f"**Shared Infrastructure Overlaps:**\n{infra_str}"
        )
        return content, "High"

    def _explain_recommendations(self, context: InvestigationContext) -> Tuple[str, str]:
        """Extracts priority-sorted analyst containment tasks."""
        risk = context.risk_assessment
        if not risk or not risk.recommendations:
            return f"No prioritized analyst mitigation guidelines were generated for **{context.indicator}**.", "Low"

        rec_lines = []
        for r in risk.recommendations:
            rec_lines.append(f"- **[{r.priority.upper()}]** {r.action}: {r.description}")
        rec_str = "\n".join(rec_lines)

        content = (
            f"Here are the recommended mitigation and containment tasks for indicator **{context.indicator}**:\n\n"
            f"{rec_str}"
        )
        return content, "High"

    def _default_explanation(self, context: InvestigationContext) -> Tuple[str, str]:
        """General overview fallback explanation."""
        risk = context.risk_assessment
        camp = context.campaign_details

        severity = risk.severity.value.upper() if risk else "UNKNOWN"
        score = f"{risk.overall_score:.1f}/100" if risk else "N/A"
        campaign_info = f"Linked to campaign **{camp.name}**" if camp else "Isolated outlier"

        content = (
            f"This is ThreatLens AI Assistant checking the indicator: **{context.indicator}**.\n\n"
            f"- **Overall Risk Rating:** {severity} (Score: {score})\n"
            f"- **Attribution Status:** {campaign_info}\n\n"
            f"You can ask me specific questions like:\n"
            f"- *'Why is this URL risky?'*\n"
            f"- *'What infrastructure is shared?'*\n"
            f"- *'What should an analyst investigate next?'*"
        )
        return content, "Medium"
