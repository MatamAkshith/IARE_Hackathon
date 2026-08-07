"""
RecommendationEngine — Stage 6.3

Maps fired RiskFactors and overall RiskSeverity to prioritized, actionable
analyst recommendations. All logic is deterministic and rule-based.

Design principles:
  - Factor name matching is exact (matching the name strings defined in rules.py).
  - Recommendations are deduplicated — the same action is never added twice.
  - Recommendations are sorted by priority: immediate > high > medium > low.
  - Severity-level catch-all recommendations are always appended last,
    providing baseline guidance even when no specific factors fired.
"""

import logging
from typing import List

from app.services.risk_engine.models import Recommendation, RiskFactor, RiskSeverity

logger = logging.getLogger("app.services.risk_engine.recommendations")

# Priority ordering for sorting
_PRIORITY_ORDER = {"immediate": 0, "high": 1, "medium": 2, "low": 3}


class RecommendationEngine:
    """
    Inspects triggered RiskFactors and the overall severity level to produce
    a deduplicated, priority-sorted list of Recommendation objects.
    """

    # ── Factor-level recommendation rules ──────────────────────────────────── #
    # Maps the exact RiskFactor.name to a (action, priority, description) tuple.
    _FACTOR_RULES: dict = {
        # Threat Intelligence
        "VirusTotal: Malicious Verdict": (
            "Block indicator at perimeter",
            "immediate",
            "VirusTotal consensus marks this indicator as malicious. Block the URL/domain/IP "
            "immediately at the firewall, web proxy, and DNS resolvers.",
        ),
        "VirusTotal: Suspicious Verdict": (
            "Flag for analyst review",
            "high",
            "VirusTotal flagged this indicator as suspicious. Queue for manual analyst review "
            "and consider temporary quarantine pending investigation.",
        ),
        "PhishTank: Confirmed Phish": (
            "Report and block phishing URL",
            "immediate",
            "PhishTank confirms this is a live phishing URL. Block immediately and submit to "
            "your email security gateway and browser protection feeds.",
        ),
        "URLHaus: Active Malware URL": (
            "Isolate and block malware endpoint",
            "immediate",
            "URLHaus reports this as an active malware distribution URL. Block at all egress "
            "points and check endpoint logs for prior connections.",
        ),
        "AbuseIPDB: High Abuse Confidence": (
            "Block IP at firewall",
            "high",
            "AbuseIPDB confidence is very high for this IP. Add to IP blocklist and review "
            "inbound/outbound connection logs for lateral movement.",
        ),
        "AlienVault OTX: Multiple Threat Pulses": (
            "Cross-reference with threat intel feeds",
            "medium",
            "Indicator appears in multiple OTX pulses. Correlate with internal SIEM logs and "
            "submit to your threat intelligence sharing platform.",
        ),

        # Domain Intelligence
        "Very Young Domain": (
            "Investigate domain registration",
            "high",
            "Domain was registered very recently — a primary phishing indicator. "
            "Investigate registrant details via WHOIS and monitor for brand impersonation.",
        ),
        "Young Domain": (
            "Monitor domain activity",
            "medium",
            "Domain is less than 6 months old. Apply heightened monitoring and consider "
            "flagging in email security gateways.",
        ),
        "Suspicious TLD": (
            "Treat domain with elevated suspicion",
            "medium",
            "Domain uses a TLD commonly abused for phishing. Apply strict email filtering "
            "and warn end-users about interactions with this domain.",
        ),
        "IP-Based URL": (
            "Block IP-based URL access",
            "high",
            "URL uses a raw IP address instead of a hostname — a classic phishing tactic. "
            "Block access and investigate the hosting IP for infrastructure reuse.",
        ),

        # DNS / WHOIS
        "No MX Records": (
            "Flag as potential impersonation domain",
            "medium",
            "Domain has no MX records, indicating it was not set up for legitimate email. "
            "This is common for squatted impersonation domains.",
        ),
        "No NS Records": (
            "Investigate DNS anomaly",
            "medium",
            "Missing NS records indicate DNS misconfiguration or a parked/inactive domain "
            "being used as a redirect or staging host.",
        ),
        "WHOIS Privacy Enabled": (
            "Request WHOIS transparency",
            "low",
            "Registrant details are redacted. Submit a WHOIS disclosure request if legally "
            "required, and note this as a risk amplifier.",
        ),

        # TLS
        "Invalid TLS Certificate": (
            "Warn users about unsafe connection",
            "high",
            "TLS certificate is invalid or self-signed. Notify affected users, block access "
            "via web proxy, and investigate if this is brand impersonation.",
        ),
        "Free / Automated CA Certificate": (
            "Flag certificate source",
            "low",
            "Free CA certificates are trivially obtained. Combined with other signals, "
            "this elevates concern. Log the issuer for pattern analysis.",
        ),
        "Certificate Near Expiry": (
            "Check for throwaway site pattern",
            "low",
            "Certificate expires soon — consistent with a short-lived phishing site. "
            "Expedite investigation before the domain pivots infrastructure.",
        ),

        # HTML / Content
        "Login / Credential Form Detected": (
            "Test for credential harvesting",
            "high",
            "Page contains a login form. Submit a honeypot credential and monitor for "
            "exfiltration. Block access for end-users immediately.",
        ),
        "Password Input Field(s) Detected": (
            "Prevent credential submission",
            "high",
            "Password input fields indicate credential harvesting intent. Block the URL "
            "at the proxy and issue a user advisory.",
        ),
        "High Number of Forms": (
            "Inspect page for data collection",
            "medium",
            "Multiple forms suggest aggressive data collection. Capture a screenshot for "
            "evidence and review all form action destinations.",
        ),
        "Suspicious Page Title": (
            "Review page content for lure text",
            "medium",
            "Page title contains phishing lure keywords. Download the full page source for "
            "analysis and check for brand logo/trademark abuse.",
        ),
    }

    def generate(
        self,
        factors: List[RiskFactor],
        severity: RiskSeverity,
    ) -> List[Recommendation]:
        """
        Generates a deduplicated, priority-sorted list of Recommendation objects
        from the triggered risk factors and overall severity.

        Parameters
        ----------
        factors  : All fired RiskFactor objects (across all categories).
        severity : Overall RiskSeverity of the assessment.

        Returns
        -------
        List[Recommendation] sorted by priority (immediate → low).
        """
        recommendations: List[Recommendation] = []
        seen_actions: set = set()

        # Sort factors by score_contribution descending so the highest-impact
        # factors drive the first (highest-priority) recommendations.
        sorted_factors = sorted(factors, key=lambda f: f.score_contribution, reverse=True)

        for factor in sorted_factors:
            rule = self._FACTOR_RULES.get(factor.name)
            if not rule:
                continue
            action, priority, description = rule
            if action in seen_actions:
                continue  # deduplicate
            seen_actions.add(action)
            recommendations.append(Recommendation(
                action=action,
                priority=priority,
                description=description,
                factor=factor.name,
            ))

        # Severity-level catch-all — always append baseline guidance
        catch_all = self._severity_catchall(severity)
        if catch_all and catch_all.action not in seen_actions:
            recommendations.append(catch_all)

        # Sort: immediate → high → medium → low
        recommendations.sort(key=lambda r: _PRIORITY_ORDER.get(r.priority, 99))

        logger.info(
            f"[generate] Generated {len(recommendations)} recommendation(s) "
            f"for severity='{severity.value}', factors_count={len(factors)}."
        )

        return recommendations

    @staticmethod
    def _severity_catchall(severity: RiskSeverity) -> Recommendation:
        """Returns a baseline catch-all recommendation based on severity tier."""
        _CATCHALL: dict = {
            RiskSeverity.CRITICAL: Recommendation(
                action="Initiate incident response",
                priority="immediate",
                description=(
                    "Risk score is CRITICAL. Initiate your full incident response playbook: "
                    "isolate affected systems, preserve evidence, notify security leadership, "
                    "and begin brand impersonation takedown procedures."
                ),
                factor=None,
            ),
            RiskSeverity.HIGH: Recommendation(
                action="Escalate to security team",
                priority="high",
                description=(
                    "Risk score is HIGH. Escalate immediately to the security operations team. "
                    "Enforce blocking rules across all perimeter controls and track in your SIEM."
                ),
                factor=None,
            ),
            RiskSeverity.MEDIUM: Recommendation(
                action="Queue for analyst triage",
                priority="medium",
                description=(
                    "Risk score is MEDIUM. Add to analyst triage queue within 24 hours. "
                    "Apply enhanced monitoring and consider pre-emptive user advisories."
                ),
                factor=None,
            ),
            RiskSeverity.LOW: Recommendation(
                action="Log and monitor",
                priority="low",
                description=(
                    "Risk score is LOW. Log the indicator in your threat intelligence platform "
                    "and monitor for escalating activity over the next 7 days."
                ),
                factor=None,
            ),
            RiskSeverity.SAFE: Recommendation(
                action="No immediate action required",
                priority="low",
                description=(
                    "Risk score is SAFE. No threat signals detected. Continue routine monitoring "
                    "and re-evaluate if new intelligence becomes available."
                ),
                factor=None,
            ),
        }
        return _CATCHALL.get(severity, _CATCHALL[RiskSeverity.SAFE])
