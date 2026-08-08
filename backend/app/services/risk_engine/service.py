from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

from app.services.risk_engine.config import (
    CATEGORY_EVIDENCE_KEYS,
    SEVERITY_THRESHOLDS,
)
from app.services.risk_engine.models import (
    RiskBreakdown,
    RiskFactor,
    RiskScore,
    RiskSeverity,
)
from app.services.risk_engine.recommendations import RecommendationEngine
from app.services.risk_engine.validator import RiskValidator

logger = logging.getLogger("app.services.risk_engine.service")


def _map_severity(score: float) -> RiskSeverity:
    """Maps a 0-100 score to a RiskSeverity tier using config thresholds."""
    for threshold, severity_str in SEVERITY_THRESHOLDS:
        if score >= threshold:
            return RiskSeverity(severity_str)
    return RiskSeverity.SAFE


def _build_explanation(
    score: float,
    severity: RiskSeverity,
    factors: List[RiskFactor],
    confidence: str,
    was_calibrated: bool,
) -> str:
    """Generates a concise human-readable summary of risk evaluation."""
    if not factors:
        return (
            f"No risk signals detected. Overall risk score is {score:.1f}/100 ({severity.value.upper()})."
        )
    top = sorted(factors, key=lambda f: f.score_contribution, reverse=True)
    top_names = ", ".join(f.name for f in top[:3])
    base = (
        f"Risk score {score:.1f}/100 — severity {severity.value.upper()}. "
        f"Top contributing factors: {top_names}."
    )
    return base


class RiskScoringService:
    """
    RiskScoringService — Core orchestrator for the Explainable Risk Engine.
    Implements a telemetry-driven, dynamic generalized phishing evaluation scoring engine.
    """

    def __init__(self) -> None:
        self._recommendation_engine = RecommendationEngine()
        self._validator = RiskValidator()
        logger.info("RiskScoringService initialized.")

    def calculate_risk(
        self,
        unified_evidence: Union[Dict[str, Any], Any],
    ) -> RiskScore:
        evidence, indicator = self._extract_evidence(unified_evidence)
        confidence = self._extract_confidence(unified_evidence)

        logger.info(f"[calculate_risk] Starting dynamic risk evaluation for indicator: '{indicator}'")

        # ── Step 0: Whitelist check (SAFE / 0.0) ───────────────────────────── #
        if indicator:
            ind_lower = indicator.lower()
            host = ind_lower.split("://")[-1].split("/")[0]
            if host == "vardhaman.org" or host.endswith(".vardhaman.org"):
                logger.info(f"[calculate_risk] Whitelisted domain '{indicator}' — returning SAFE/0.0.")
                return RiskScore(
                    indicator=indicator,
                    overall_score=0.0,
                    severity=RiskSeverity.SAFE,
                    breakdown=RiskBreakdown(),
                    recommendations=self._recommendation_engine.generate([], RiskSeverity.SAFE),
                    factor_count=0,
                    timestamp=datetime.now(timezone.utc),
                    explanation="Official whitelisted college domain.",
                )

        # If no evidence is present at all, return SAFE / 0.0
        if not self._validator.validate_evidence(evidence):
            return RiskScore(
                indicator=indicator,
                overall_score=0.0,
                severity=RiskSeverity.SAFE,
                breakdown=RiskBreakdown(),
                recommendations=self._recommendation_engine.generate([], RiskSeverity.SAFE),
                factor_count=0,
                timestamp=datetime.now(timezone.utc),
                explanation="No risk signals detected. Evidence was empty or malformed.",
            )

        ind_lower = indicator.lower() if indicator else ""
        host = ind_lower.split("://")[-1].split("/")[0] if ind_lower else ""

        domain_factors: List[RiskFactor] = []
        dns_factors: List[RiskFactor] = []
        whois_factors: List[RiskFactor] = []
        tls_factors: List[RiskFactor] = []
        html_factors: List[RiskFactor] = []
        ti_factors: List[RiskFactor] = []

        # ── 1. Target Brand & Intent Heuristics (0-25 pts) ────────────────── #
        monitored_brands = ["microsoft", "google", "amazon", "paypal", "infosys", "vardhaman", "vmeg"]
        official_brand_domains = {
            "google": ["google.com", "google.co.in", "google.net", "youtube.com", "googleblog.com"],
            "microsoft": ["microsoft.com", "office.com", "live.com", "azure.com", "windows.net", "microsoft-auth.com"],
            "amazon": ["amazon.com", "amazon.in", "aws.amazon.com", "media-amazon.com"],
            "paypal": ["paypal.com", "paypal.in", "paypalobjects.com"],
            "infosys": ["infosys.com", "infosys.co.in"],
            "vardhaman": ["vardhaman.org"],
            "vmeg": ["vardhaman.org"]
        }

        has_brand_keyword = any(brand in host for brand in monitored_brands)
        is_brand_impersonation = False
        if has_brand_keyword:
            is_official = False
            for brand in monitored_brands:
                if brand in host:
                    official_list = official_brand_domains.get(brand, [])
                    for d in official_list:
                        if host == d or host.endswith("." + d):
                            is_official = True
                            break
            if not is_official:
                is_brand_impersonation = True

        domain_contrib = 0.0
        if is_brand_impersonation:
            domain_contrib += 15.0
            domain_factors.append(RiskFactor(
                name="Brand Impersonation Detection",
                score_contribution=15.0,
                description="The domain name is unauthorizedly impersonating a registered enterprise brand.",
                weight=15.0,
                evidence_key="indicator"
            ))

        suspicious_keywords = ["login", "password", "verify", "update", "employee", "payroll", "benefits", "confirm", "account", "secure", "auth", "signin", "support", "portal"]
        keyword_count = sum(1 for kw in suspicious_keywords if kw in host)
        if keyword_count > 0:
            kw_contrib = min(keyword_count * 3.0, 10.0)
            domain_contrib += kw_contrib
            domain_factors.append(RiskFactor(
                name="Deceptive Keyword(s) in Hostname",
                score_contribution=kw_contrib,
                description=f"Hostname contains {keyword_count} phishing-sensitive keywords.",
                weight=10.0,
                evidence_key="indicator"
            ))

        if host.count('-') >= 2:
            domain_contrib += 10.0
            domain_factors.append(RiskFactor(
                name="Suspicious Multi-Hyphen Structure",
                score_contribution=10.0,
                description="The domain name uses multiple hyphenations, commonly seen in typosquatting campaigns.",
                weight=10.0,
                evidence_key="indicator"
            ))

        subdomains = host.split('.')
        if len(subdomains) > 3:
            domain_contrib += 5.0
            domain_factors.append(RiskFactor(
                name="High Subdomain Count",
                score_contribution=5.0,
                description="Domain structure includes multiple levels of subdomains which can obscure the root authority.",
                weight=5.0,
                evidence_key="indicator"
            ))

        domain_score = min(domain_contrib, 25.0)

        # ── 2. DNS Intelligence (0-15 pts) ────────────────────────────────── #
        dns_contrib = 0.0
        mx_records = evidence.get("mx_records")
        if mx_records is None or not mx_records or mx_records == [] or mx_records == "":
            dns_contrib += 10.0
            dns_factors.append(RiskFactor(
                name="Missing MX Records",
                score_contribution=10.0,
                description="No active mail exchange records exist for this domain name.",
                weight=10.0,
                evidence_key="mx_records"
            ))

        has_age_anomaly = False
        age = evidence.get("domain_age_days")
        if age is not None:
            try:
                if int(age) < 30:
                    has_age_anomaly = True
            except (ValueError, TypeError):
                pass

        if has_age_anomaly:
            dns_contrib += 10.0
            dns_factors.append(RiskFactor(
                name="Recently Created Domain",
                score_contribution=10.0,
                description=f"Domain age is under 30 days ({age} days).",
                weight=10.0,
                evidence_key="domain_age_days"
            ))

        ns = evidence.get("nameservers")
        if ns and any(x in str(ns).lower() for x in ["disposable", "suspicious", "free"]):
            dns_contrib += 10.0
            dns_factors.append(RiskFactor(
                name="Suspicious Name Server Host",
                score_contribution=10.0,
                description="Domain is delegated to a low-reputation or disposable nameserver provider.",
                weight=10.0,
                evidence_key="nameservers"
            ))

        dns_score = min(dns_contrib, 15.0)

        # ── 3. WHOIS Signals (0-15 pts) ───────────────────────────────────── #
        whois_contrib = 0.0
        whois_privacy = evidence.get("whois_privacy") or evidence.get("registrant_redacted")
        if whois_privacy is True:
            whois_contrib += 10.0
            whois_factors.append(RiskFactor(
                name="WHOIS Registration Privacy Enabled",
                score_contribution=10.0,
                description="Registrant ownership details are hidden behind a proxy service.",
                weight=10.0,
                evidence_key="whois_privacy"
            ))

        reg_date = evidence.get("whois_registration_date") or evidence.get("creation_date")
        if reg_date:
            whois_contrib += 10.0
            whois_factors.append(RiskFactor(
                name="Fresh Registration Date Signal",
                score_contribution=10.0,
                description="WHOIS creation date matches recent domain registration trends.",
                weight=10.0,
                evidence_key="whois_registration_date"
            ))

        registrar = str(evidence.get("registrar") or "").lower()
        if registrar and any(x in registrar for x in ["namecheap", "freenom", "cheap", "privacy", "reg"]):
            whois_contrib += 10.0
            whois_factors.append(RiskFactor(
                name="Low-Reputation Registrar Service",
                score_contribution=10.0,
                description="Domain is registered through a low-reputation or high-abuse registrar.",
                weight=10.0,
                evidence_key="registrar"
            ))

        whois_score = min(whois_contrib, 15.0)

        # ── 4. SSL Analysis (0-15 pts) ────────────────────────────────────── #
        ssl_contrib = 0.0
        ssl_valid = evidence.get("ssl_valid")
        tls_issuer = str(evidence.get("tls_issuer") or "").lower()
        is_self_signed = "self signed" in tls_issuer or "expired" in tls_issuer or "fake" in tls_issuer
        if ssl_valid is False or ssl_valid is None or is_self_signed:
            ssl_contrib += 15.0
            tls_factors.append(RiskFactor(
                name="Invalid/Missing TLS Certificate",
                score_contribution=15.0,
                description="No valid SSL/TLS certificate was present or issuer is untrusted.",
                weight=15.0,
                evidence_key="ssl_valid"
            ))

        ssl_expiring = evidence.get("ssl_expiring_soon")
        if ssl_expiring is True:
            ssl_contrib += 10.0
            tls_factors.append(RiskFactor(
                name="SSL Certificate Expiring Soon",
                score_contribution=10.0,
                description="The domain's cryptographic certificate will expire in a few days.",
                weight=10.0,
                evidence_key="ssl_expiring_soon"
            ))

        ssl_score = min(ssl_contrib, 15.0)

        # ── 5. HTML Indicators (0-15 pts) ─────────────────────────────────── #
        html_contrib = 0.0
        has_login_form = evidence.get("has_login_form")
        if has_login_form is True:
            html_contrib += 10.0
            html_factors.append(RiskFactor(
                name="Login Forms Detected",
                score_contribution=10.0,
                description="HTML parser discovered credential submission forms.",
                weight=10.0,
                evidence_key="has_login_form"
            ))

        pwd_inputs = evidence.get("password_inputs")
        pwd_inputs_count = 0
        if pwd_inputs:
            try:
                pwd_inputs_count = int(pwd_inputs)
            except (ValueError, TypeError):
                pass

        if pwd_inputs_count > 0:
            html_contrib += 10.0
            html_factors.append(RiskFactor(
                name="Password Input Field Presence",
                score_contribution=10.0,
                description=f"HTML content includes {pwd_inputs} password text fields.",
                weight=10.0,
                evidence_key="password_inputs"
            ))

        brand_visual = evidence.get("brand_visual_match")
        if brand_visual is True:
            html_contrib += 10.0
            html_factors.append(RiskFactor(
                name="Impersonated Brand Visual Match",
                score_contribution=10.0,
                description="The page styling or logos mimic the targeted brand visual identity.",
                weight=10.0,
                evidence_key="brand_visual_match"
            ))

        html_score = min(html_contrib, 15.0)

        # ── 6. Threat Intelligence (0-15 pts) ─────────────────────────────── #
        ti_contrib = 0.0
        vt_verdict = str(evidence.get("virustotal_verdict") or "").lower().strip()
        pt_verdict = evidence.get("phishtank_verdict")
        uh_verdict = evidence.get("urlhaus_verdict")

        is_phish_pt = False
        if isinstance(pt_verdict, bool) and pt_verdict:
            is_phish_pt = True
        elif isinstance(pt_verdict, str) and pt_verdict.lower() in ("true", "phishing", "malicious"):
            is_phish_pt = True

        is_malicious_uh = False
        if isinstance(uh_verdict, str) and uh_verdict.lower() in ("malicious", "online", "active"):
            is_malicious_uh = True

        if vt_verdict in ("malicious", "phishing", "suspicious") or is_phish_pt or is_malicious_uh:
            ti_contrib += 15.0
            ti_factors.append(RiskFactor(
                name="Active Threat Feed Match",
                score_contribution=15.0,
                description="Indicator is flagged active in third-party threat intelligence databases.",
                weight=15.0,
                evidence_key="virustotal_verdict"
            ))

        shared_infra = evidence.get("shared_infra_match")
        if shared_infra:
            ti_contrib += 10.0
            ti_factors.append(RiskFactor(
                name="Shared Malicious Infrastructure ASN",
                score_contribution=10.0,
                description="Indicator shares hosting space with known malicious hosts.",
                weight=10.0,
                evidence_key="shared_infra_match"
            ))

        campaign_overlap = evidence.get("campaign_overlap") or evidence.get("campaign_id") is not None
        if campaign_overlap:
            ti_contrib += 15.0
            ti_factors.append(RiskFactor(
                name="Correlated Campaign Overlap",
                score_contribution=15.0,
                description="Indicator is clustered under a known malicious campaign group.",
                weight=15.0,
                evidence_key="campaign_overlap"
            ))

        ti_score = min(ti_contrib, 15.0)

        # Base Sum
        base_sum = 5.0 + domain_score + dns_score + whois_score + ssl_score + html_score + ti_score

        # ── Escalation Rules ──────────────────────────────────────────────── #
        bonus = 0.0
        # Escalation Rule 1: Brand Impersonation AND Credential Form (Login Form or Password inputs) -> Add +20 bonus
        has_credentials_form = (has_login_form is True) or (pwd_inputs_count > 0)
        if is_brand_impersonation and has_credentials_form:
            bonus += 20.0
            html_factors.append(RiskFactor(
                name="Impersonation & Credential Form Escalation",
                score_contribution=20.0,
                description="Combination of brand impersonation and password/login entry triggers critical risk bonus.",
                weight=20.0,
                evidence_key="has_login_form"
            ))

        final_score = base_sum + bonus

        # Escalation Rule 2: Minimum 75 if multiple keywords or combinations appear
        suspicious_combos = ["login", "password", "verify", "update", "employee", "payroll", "benefits", "confirm", "account"]
        has_combo_kw = any(kw in host for kw in suspicious_combos)
        if has_combo_kw:
            if final_score < 75.0:
                final_score = 75.0
                domain_factors.append(RiskFactor(
                    name="Phishing Keyword Minimum Score Enforced",
                    score_contribution=75.0 - base_sum,
                    description="Suspicious combination of targeting keywords guarantees at least HIGH severity.",
                    weight=10.0,
                    evidence_key="indicator"
                ))

        # Escalation Rule 3: Minimum 80 if domain belongs to existing campaign
        if campaign_overlap:
            if final_score < 80.0:
                final_score = 80.0
                ti_factors.append(RiskFactor(
                    name="Campaign Overlap Minimum Score Enforced",
                    score_contribution=80.0 - base_sum,
                    description="Coordinated campaign overlap status automatically enforces HIGH severity.",
                    weight=15.0,
                    evidence_key="campaign_overlap"
                ))

        was_calibrated = False

        # Clamp between 0.0 and 100.0
        final_score = self._validator.enforce_boundaries(final_score)

        # Map to severity
        severity = _map_severity(final_score)

        # Assemble breakdown
        breakdown = RiskBreakdown(
            domain_intelligence=domain_factors,
            dns_whois=dns_factors + whois_factors,
            tls_certificate=tls_factors,
            html_content=html_factors,
            threat_intelligence=ti_factors,
        )


        all_factors = breakdown.all_factors()

        explanation = _build_explanation(
            final_score, severity, all_factors, confidence, was_calibrated,
        )

        recommendations = self._recommendation_engine.generate(
            factors=all_factors,
            severity=severity,
        )

        return RiskScore(
            indicator=indicator,
            overall_score=final_score,
            severity=severity,
            breakdown=breakdown,
            recommendations=recommendations,
            factor_count=len(all_factors),
            timestamp=datetime.now(timezone.utc),
            explanation=explanation,
        )

    # ── Private helpers ───────────────────────────────────────────────────── #

    @staticmethod
    def _extract_evidence(
        unified_evidence: Union[Dict[str, Any], Any]
    ) -> tuple[Dict[str, Any], str]:
        if isinstance(unified_evidence, dict):
            indicator = unified_evidence.get("indicator", "unknown")
            return unified_evidence, indicator

        try:
            resolved = dict(getattr(unified_evidence, "resolved_observations", {}) or {})
            indicator = getattr(unified_evidence, "indicator", "unknown")

            if hasattr(unified_evidence, "indicator_type"):
                resolved.setdefault("indicator_type", unified_evidence.indicator_type)
            resolved.setdefault("indicator", indicator)

            for source_attr in ("internal_evidence", "external_evidence"):
                src = getattr(unified_evidence, source_attr, None) or {}
                for k, v in src.items():
                    resolved.setdefault(k, v)

            return resolved, indicator
        except Exception as exc:
            logger.warning(f"_extract_evidence fallback to empty dict: {exc}")
            return {}, "unknown"

    @staticmethod
    def _extract_confidence(unified_evidence: Union[Dict[str, Any], Any]) -> str:
        if isinstance(unified_evidence, dict):
            conf = unified_evidence.get("overall_confidence", "unknown")
        else:
            conf = getattr(unified_evidence, "overall_confidence", "unknown")
        
        if hasattr(conf, "value"):
            return str(conf.value).lower().strip()
        conf_str = str(conf).lower().strip()
        if "high" in conf_str:
            return "high"
        if "medium" in conf_str:
            return "medium"
        if "low" in conf_str:
            return "low"
        return conf_str
