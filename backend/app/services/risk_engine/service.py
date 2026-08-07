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
    if was_calibrated:
        base += f" (Score calibrated for '{confidence}' confidence evidence.)"
    return base


class RiskScoringService:
    """
    RiskScoringService — Core orchestrator for the Explainable Risk Engine.
    Implements a telemetry-driven, dynamic cumulative scoring engine.
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
        tls_factors: List[RiskFactor] = []
        html_factors: List[RiskFactor] = []
        ti_factors: List[RiskFactor] = []

        raw_score = 0.0

        # ── 1. Target Brand Impersonation Rules (+40 points) ────────────────── #
        monitored_brands = ["microsoft", "google", "amazon", "paypal", "infosys", "vardhaman"]
        official_brand_domains = {
            "google": ["google.com", "google.co.in", "google.net", "youtube.com", "googleblog.com"],
            "microsoft": ["microsoft.com", "office.com", "live.com", "azure.com", "windows.net", "microsoft-auth.com"],
            "amazon": ["amazon.com", "amazon.in", "aws.amazon.com", "media-amazon.com"],
            "paypal": ["paypal.com", "paypal.in", "paypalobjects.com"],
            "infosys": ["infosys.com", "infosys.co.in"],
            "vardhaman": ["vardhaman.org"]
        }

        is_impersonation = False
        for brand in monitored_brands:
            if brand in host:
                # If it's the official domain (or subdomain) of the brand, it is not impersonation
                official_list = official_brand_domains.get(brand, [])
                is_official = False
                for d in official_list:
                    if host == d or host.endswith("." + d):
                        is_official = True
                        break
                if not is_official:
                    is_impersonation = True
                    break

        if is_impersonation:
            domain_factors.append(RiskFactor(
                name="Target Brand Impersonation Detected",
                score_contribution=40.0,
                description="Domain name contains a targeted enterprise brand without authorization.",
                weight=40.0,
                evidence_key="indicator"
            ))
            raw_score += 40.0

        # ── 2. TLS Certificate Rules (+30 points) ─────────────────────────── #
        ssl_valid = evidence.get("ssl_valid")
        tls_issuer = str(evidence.get("tls_issuer") or evidence.get("cert_issuer") or "").lower()
        is_self_signed = "self signed" in tls_issuer or "expired" in tls_issuer or "fake" in tls_issuer
        
        # Missing TLS certificate or invalid/self-signed cert
        if ssl_valid is False or is_self_signed or ssl_valid is None:
            tls_factors.append(RiskFactor(
                name="Invalid or Missing TLS Certificate",
                score_contribution=30.0,
                description="The site's TLS certificate is invalid, missing, or self-signed.",
                weight=30.0,
                evidence_key="ssl_valid"
            ))
            raw_score += 30.0
        elif "let's encrypt" in tls_issuer or "zerossl" in tls_issuer or "buypass" in tls_issuer:
            tls_factors.append(RiskFactor(
                name="Free / Automated CA Certificate",
                score_contribution=5.0,
                description="Certificate issued by a free/automated CA. Free CAs require no identity verification.",
                weight=5.0,
                evidence_key="tls_issuer"
            ))
            raw_score += 5.0

        # ── 3. DNS / MX Record Rules (+30 points) ──────────────────────────── #
        mx_records = evidence.get("mx_records")
        has_mx = True
        if mx_records is not None:
            if not mx_records or mx_records == [] or mx_records == "":
                has_mx = False
        else:
            has_mx = False

        sensitive_keywords = ['login', 'verify', 'auth', 'portal', 'erp', 'secure', 'employee', 'benefits', 'student', 'gradebook', 'results']
        contains_sensitive_kw = any(kw in host for kw in sensitive_keywords)

        if not has_mx and contains_sensitive_kw:
            dns_factors.append(RiskFactor(
                name="Missing MX Records on Sensitive Target",
                score_contribution=30.0,
                description="Domain name contains sensitive authentication keywords but lacks MX email server records.",
                weight=30.0,
                evidence_key="mx_records"
            ))
            raw_score += 30.0
        elif not has_mx:
            dns_factors.append(RiskFactor(
                name="No MX Records",
                score_contribution=5.0,
                description="Domain has no MX records. Legitimate brands always have email infrastructure.",
                weight=5.0,
                evidence_key="mx_records"
            ))
            raw_score += 5.0

        # ── 4. Domain Structure & Entropy Rules (+20 points) ────────────────── #
        def calculate_entropy(s: str) -> float:
            import math
            if not s:
                return 0.0
            entropy = 0.0
            for x in set(s):
                p_x = s.count(x) / len(s)
                entropy += - p_x * math.log2(p_x)
            return entropy

        domain_part = host.split('.')[0] if '.' in host else host
        is_multi_hyphenated = host.count('-') >= 2
        is_high_entropy = calculate_entropy(domain_part) >= 4.0
        kw_count = sum(1 for kw in sensitive_keywords if kw in host)
        is_keyword_stacking = kw_count >= 2

        if (is_multi_hyphenated or is_high_entropy or is_keyword_stacking):
            domain_factors.append(RiskFactor(
                name="Suspicious Domain Structure or Keyword Stacking",
                score_contribution=20.0,
                description="Domain name is high-entropy, multi-hyphenated, or contains stacked keywords.",
                weight=20.0,
                evidence_key="indicator"
            ))
            raw_score += 20.0

        # Check for suspicious TLDs
        suspicious_tlds = (".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club", ".online", ".site", ".website", ".live", ".fun", ".pw", ".cc", ".su")
        if any(host.endswith(tld) for tld in suspicious_tlds):
            domain_factors.append(RiskFactor(
                name="Suspicious TLD",
                score_contribution=10.0,
                description="Domain uses a top-level domain commonly abused for phishing.",
                weight=10.0,
                evidence_key="indicator"
            ))
            raw_score += 10.0

        # ── 5. WHOIS Domain Age Rules (+20 points) ─────────────────────────── #
        age = evidence.get("domain_age_days")
        if age is not None:
            try:
                age_days = int(age)
                if age_days < 30:
                    domain_factors.append(RiskFactor(
                        name="Very Young Domain",
                        score_contribution=20.0,
                        description=f"Domain was registered only {age_days} day(s) ago.",
                        weight=20.0,
                        evidence_key="domain_age_days"
                    ))
                    raw_score += 20.0
                elif age_days < 180:
                    domain_factors.append(RiskFactor(
                        name="Young Domain",
                        score_contribution=10.0,
                        description=f"Domain was registered {age_days} days ago (<6 months).",
                        weight=10.0,
                        evidence_key="domain_age_days"
                    ))
                    raw_score += 10.0
            except (ValueError, TypeError):
                pass

        # ── 6. Threat Feed Detection (+50 points) ────────────────────── #
        vt_verdict = str(evidence.get("virustotal_verdict") or "").lower().strip()
        pt_verdict = evidence.get("phishtank_verdict")
        uh_verdict = evidence.get("urlhaus_verdict")

        is_phish_pt = False
        if isinstance(pt_verdict, bool) and pt_verdict:
            is_phish_pt = True
        elif isinstance(pt_verdict, str) and pt_verdict.lower() in ("true", "phishing", "malicious"):
            is_phish_pt = True

        has_ti_match = (
            vt_verdict in ("malicious", "phishing", "suspicious") or 
            is_phish_pt or 
            (isinstance(uh_verdict, str) and uh_verdict.lower() in ("malicious", "online", "active"))
        )
        
        if has_ti_match:
            ti_factors.append(RiskFactor(
                name="Positive Threat Intelligence Match",
                score_contribution=50.0,
                description="Indicator is flagged as malicious by one or more external threat intelligence feeds.",
                weight=50.0,
                evidence_key="virustotal_verdict"
            ))
            raw_score += 50.0

        # ── 7. HTML / Content Rules ────────────────────────────────────────── #
        has_login_form = evidence.get("has_login_form")
        if has_login_form is True:
            html_factors.append(RiskFactor(
                name="Login / Credential Form Detected",
                score_contribution=10.0,
                description="Page contains a login or credential-harvesting form — primary characteristic of phishing pages.",
                weight=10.0,
                evidence_key="has_login_form"
            ))
            raw_score += 10.0

        pwd_inputs = evidence.get("password_inputs")
        if pwd_inputs is not None:
            try:
                count = int(pwd_inputs)
                if count > 0:
                    html_factors.append(RiskFactor(
                        name="Password Input Field(s) Detected",
                        score_contribution=5.0,
                        description=f"Page contains {count} password input field(s).",
                        weight=5.0,
                        evidence_key="password_inputs"
                    ))
                    raw_score += 5.0
            except (ValueError, TypeError):
                pass

        # WHOIS Privacy / redacted registrant
        whois_privacy = evidence.get("whois_privacy") or evidence.get("registrant_redacted")
        if whois_privacy is True:
            dns_factors.append(RiskFactor(
                name="WHOIS Privacy Enabled",
                score_contribution=5.0,
                description="Registrant information is redacted. Privacy-protected domains are common in phishing.",
                weight=5.0,
                evidence_key="whois_privacy"
            ))
            raw_score += 5.0

        # Calibrate raw score by confidence
        calibrated_score = self._validator.calibrate_score(raw_score, confidence)
        was_calibrated = calibrated_score != raw_score

        # Clamp between 0.0 and 100.0
        final_score = self._validator.enforce_boundaries(calibrated_score)

        # Map to severity
        severity = _map_severity(final_score)

        # Assemble breakdown
        breakdown = RiskBreakdown(
            domain_intelligence=domain_factors,
            dns_whois=dns_factors,
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
