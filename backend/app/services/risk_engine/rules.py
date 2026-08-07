"""
Concrete risk evaluator implementations — one per evidence category.

Weight configuration guide
--------------------------
All category max-contribution weights are imported from config.py.
Adjusting RISK_WEIGHTS in config.py automatically re-scales the final
0-100 score across the entire engine.

When evidence for a category is entirely absent, its max_contribution is
excluded from the denominator so the score remains correctly scaled.
"""

import logging
from typing import Any, Dict, List, Optional

from app.services.risk_engine.base import BaseRiskEvaluator
from app.services.risk_engine.config import RISK_WEIGHTS, TOTAL_WEIGHT
from app.services.risk_engine.models import RiskFactor

logger = logging.getLogger("app.services.risk_engine.rules")


# ─────────────────────────────────────────────────────────────────────────── #
# Helper                                                                      #
# ─────────────────────────────────────────────────────────────────────────── #

def _get(evidence: Dict[str, Any], key: str, default=None):
    """Convenience accessor with a None-safe default."""
    return evidence.get(key, default)


def _factor(
    name: str,
    score: float,
    description: str,
    weight: float,
    key: Optional[str] = None,
) -> RiskFactor:
    return RiskFactor(
        name=name,
        score_contribution=score,
        description=description,
        weight=weight,
        evidence_key=key,
    )


# ─────────────────────────────────────────────────────────────────────────── #
# 1. Domain Intelligence Evaluator                                            #
# ─────────────────────────────────────────────────────────────────────────── #

class DomainIntelEvaluator(BaseRiskEvaluator):
    """
    Evaluates domain-level indicators:
      - Domain age (very young domains are a strong phishing signal)
      - Suspicious TLD usage
      - Homoglyph / lookalike domain patterns
      - IP-based URL (no hostname)
    """

    category = "domain_intelligence"
    max_contribution = RISK_WEIGHTS["domain_intelligence"]

    # Score weights
    _W_VERY_YOUNG_DOMAIN  = 12.0   # < 30 days old
    _W_YOUNG_DOMAIN       =  8.0   # 30–180 days old
    _W_SUSPICIOUS_TLD     =  7.0
    _W_IP_URL             =  6.0

    # Suspicious TLDs commonly abused in phishing campaigns
    _SUSPICIOUS_TLDS = frozenset({
        ".tk", ".ml", ".ga", ".cf", ".gq",   # Freenom TLDs
        ".xyz", ".top", ".club", ".online",
        ".site", ".website", ".live", ".fun",
        ".pw", ".cc", ".su",
    })

    def evaluate(self, evidence: Dict[str, Any]) -> List[RiskFactor]:
        factors: List[RiskFactor] = []

        # --- Domain age ---
        age = _get(evidence, "domain_age_days")
        if age is not None:
            try:
                age = int(age)
                if age < 30:
                    factors.append(_factor(
                        name="Very Young Domain",
                        score=self._W_VERY_YOUNG_DOMAIN,
                        description=f"Domain is only {age} day(s) old. Newly registered domains are a primary phishing indicator.",
                        weight=self._W_VERY_YOUNG_DOMAIN,
                        key="domain_age_days",
                    ))
                elif age < 180:
                    factors.append(_factor(
                        name="Young Domain",
                        score=self._W_YOUNG_DOMAIN,
                        description=f"Domain is {age} days old (<6 months). Young domains carry elevated phishing risk.",
                        weight=self._W_YOUNG_DOMAIN,
                        key="domain_age_days",
                    ))
            except (ValueError, TypeError):
                logger.debug(f"domain_age_days value '{age}' is not numeric; skipping age rule.")

        # --- Suspicious TLD ---
        indicator = _get(evidence, "indicator") or _get(evidence, "url") or ""
        if isinstance(indicator, str) and indicator:
            for tld in self._SUSPICIOUS_TLDS:
                host = indicator.split("://")[-1].split("/")[0].lower()
                if host.endswith(tld):
                    factors.append(_factor(
                        name="Suspicious TLD",
                        score=self._W_SUSPICIOUS_TLD,
                        description=f"Domain uses TLD '{tld}' which is commonly abused for phishing and fraud.",
                        weight=self._W_SUSPICIOUS_TLD,
                        key="indicator",
                    ))
                    break

        # --- IP-based URL ---
        ip = _get(evidence, "ip_address")
        if ip and isinstance(ip, str):
            host = indicator.split("://")[-1].split("/")[0] if indicator else ""
            if host == ip:
                factors.append(_factor(
                    name="IP-Based URL",
                    score=self._W_IP_URL,
                    description=f"URL uses a raw IP address ({ip}) instead of a domain name, a common phishing tactic.",
                    weight=self._W_IP_URL,
                    key="ip_address",
                ))

        # --- Target Brand Impersonation via Lexical Heuristics ---
        if isinstance(indicator, str) and indicator:
            ind_lower = indicator.lower()
            host = ind_lower.split("://")[-1].split("/")[0]
            brands = ["microsoft", "google", "amazon", "paypal", "github", "vardhaman"]
            suspicious = ["login", "verify", "auth", "secure", "update", "account", "portal"]
            matched_brand = any(brand in host for brand in brands)
            matched_suspicious = any(kw in host for kw in suspicious)
            if matched_brand and matched_suspicious:
                factors.append(_factor(
                    name="Target Brand Impersonation via Lexical Heuristics",
                    score=25.0,
                    description="Domain name contains a targeted enterprise brand combined with suspicious phishing keywords.",
                    weight=25.0,
                    key="indicator",
                ))

        logger.debug(f"DomainIntelEvaluator: {len(factors)} factor(s) fired.")
        return factors


# ─────────────────────────────────────────────────────────────────────────── #
# 2. DNS / WHOIS Evaluator                                                    #
# ─────────────────────────────────────────────────────────────────────────── #

class DnsWhoisEvaluator(BaseRiskEvaluator):
    """
    Evaluates DNS and WHOIS signals:
      - Missing MX records (no email infra — suspicious for impersonation)
      - Missing NS records (DNS misconfiguration)
      - WHOIS privacy / redacted registrant
    """

    category = "dns_whois"
    max_contribution = RISK_WEIGHTS["dns_whois"]

    _W_NO_MX      = 6.0
    _W_NO_NS      = 5.0
    _W_WHOIS_PRIV = 4.0

    def evaluate(self, evidence: Dict[str, Any]) -> List[RiskFactor]:
        factors: List[RiskFactor] = []

        # --- Missing MX records ---
        mx = _get(evidence, "mx_records")
        if mx is not None:
            if not mx or mx == [] or mx == "":
                factors.append(_factor(
                    name="No MX Records",
                    score=self._W_NO_MX,
                    description="Domain has no MX records. Legitimate brands always have email infrastructure.",
                    weight=self._W_NO_MX,
                    key="mx_records",
                ))

        # --- Missing NS records ---
        ns = _get(evidence, "ns_records")
        if ns is not None:
            if not ns or ns == [] or ns == "":
                factors.append(_factor(
                    name="No NS Records",
                    score=self._W_NO_NS,
                    description="Domain has no NS records. This is anomalous and indicates DNS misconfiguration.",
                    weight=self._W_NO_NS,
                    key="ns_records",
                ))

        # --- WHOIS privacy protection ---
        whois_privacy = _get(evidence, "whois_privacy") or _get(evidence, "registrant_redacted")
        if whois_privacy is True:
            factors.append(_factor(
                name="WHOIS Privacy Enabled",
                score=self._W_WHOIS_PRIV,
                description="Registrant information is redacted. Privacy-protected domains are common in phishing.",
                weight=self._W_WHOIS_PRIV,
                key="whois_privacy",
            ))

        logger.debug(f"DnsWhoisEvaluator: {len(factors)} factor(s) fired.")
        return factors


# ─────────────────────────────────────────────────────────────────────────── #
# 3. TLS Certificate Evaluator                                                #
# ─────────────────────────────────────────────────────────────────────────── #

class TlsCertificateEvaluator(BaseRiskEvaluator):
    """
    Evaluates TLS certificate signals:
      - Invalid / missing TLS certificate
      - Certificate issued by a known low-assurance free CA
      - Very short certificate validity (< 30 days remaining)
      - Subject CN mismatch with the indicator domain
    """

    category = "tls_certificate"
    max_contribution = RISK_WEIGHTS["tls_certificate"]

    _W_INVALID_TLS    = 10.0
    _W_FREE_CA        =  3.0
    _W_SHORT_VALIDITY =  2.0

    # Free / automated CAs that require zero identity verification
    _FREE_CA_PATTERNS = frozenset({
        "let's encrypt", "zerossl", "buypass", "sectigo automated",
    })

    def evaluate(self, evidence: Dict[str, Any]) -> List[RiskFactor]:
        factors: List[RiskFactor] = []

        # --- TLS validity ---
        ssl_valid = _get(evidence, "ssl_valid")
        if ssl_valid is False:
            factors.append(_factor(
                name="Invalid TLS Certificate",
                score=self._W_INVALID_TLS,
                description="The site's TLS certificate is invalid, self-signed, or expired — a strong phishing signal.",
                weight=self._W_INVALID_TLS,
                key="ssl_valid",
            ))

        # --- Free / automated CA ---
        tls_issuer = _get(evidence, "tls_issuer") or _get(evidence, "cert_issuer") or ""
        if isinstance(tls_issuer, str):
            issuer_lower = tls_issuer.lower()
            for ca_pattern in self._FREE_CA_PATTERNS:
                if ca_pattern in issuer_lower:
                    factors.append(_factor(
                        name="Free / Automated CA Certificate",
                        score=self._W_FREE_CA,
                        description=f"Certificate issued by '{tls_issuer}'. Free CAs are trivially obtained and commonly used in phishing.",
                        weight=self._W_FREE_CA,
                        key="tls_issuer",
                    ))
                    break

        # --- Short remaining validity ---
        days_remaining = _get(evidence, "cert_days_remaining")
        if days_remaining is not None:
            try:
                remaining = int(days_remaining)
                if 0 < remaining < 30:
                    factors.append(_factor(
                        name="Certificate Near Expiry",
                        score=self._W_SHORT_VALIDITY,
                        description=f"TLS certificate expires in {remaining} day(s). Near-expiry certs indicate poor maintenance or a throwaway site.",
                        weight=self._W_SHORT_VALIDITY,
                        key="cert_days_remaining",
                    ))
            except (ValueError, TypeError):
                pass

        logger.debug(f"TlsCertificateEvaluator: {len(factors)} factor(s) fired.")
        return factors


# ─────────────────────────────────────────────────────────────────────────── #
# 4. HTML / Content Evaluator                                                 #
# ─────────────────────────────────────────────────────────────────────────── #

class HtmlContentEvaluator(BaseRiskEvaluator):
    """
    Evaluates HTML and page-content signals:
      - Presence of login/credential-harvesting forms
      - Password input fields
      - High number of external resources (CDN obfuscation)
      - Suspicious page title keywords
    """

    category = "html_content"
    max_contribution = RISK_WEIGHTS["html_content"]

    _W_LOGIN_FORM    = 10.0
    _W_PASSWORD_INP  =  5.0
    _W_MANY_FORMS    =  3.0
    _W_SUSP_TITLE    =  2.0

    # Keywords in page titles frequently associated with credential phishing
    _SUSPICIOUS_TITLE_KEYWORDS = frozenset({
        "login", "sign in", "verify", "account", "secure",
        "update", "confirm", "password", "credential",
    })

    def evaluate(self, evidence: Dict[str, Any]) -> List[RiskFactor]:
        factors: List[RiskFactor] = []

        # --- Login form present ---
        has_login_form = _get(evidence, "has_login_form")
        if has_login_form is True:
            factors.append(_factor(
                name="Login / Credential Form Detected",
                score=self._W_LOGIN_FORM,
                description="Page contains a login or credential-harvesting form — primary characteristic of phishing pages.",
                weight=self._W_LOGIN_FORM,
                key="has_login_form",
            ))

        # --- Password inputs ---
        pwd_inputs = _get(evidence, "password_inputs")
        if pwd_inputs is not None:
            try:
                count = int(pwd_inputs)
                if count > 0:
                    factors.append(_factor(
                        name="Password Input Field(s) Detected",
                        score=self._W_PASSWORD_INP,
                        description=f"Page contains {count} password input field(s). Credential harvesting pages always include these.",
                        weight=self._W_PASSWORD_INP,
                        key="password_inputs",
                    ))
            except (ValueError, TypeError):
                pass

        # --- High form count ---
        forms_count = _get(evidence, "forms_count")
        if forms_count is not None:
            try:
                count = int(forms_count)
                if count > 3:
                    factors.append(_factor(
                        name="High Number of Forms",
                        score=self._W_MANY_FORMS,
                        description=f"Page contains {count} HTML forms — unusually high for a legitimate page.",
                        weight=self._W_MANY_FORMS,
                        key="forms_count",
                    ))
            except (ValueError, TypeError):
                pass

        # --- Suspicious page title ---
        page_title = _get(evidence, "page_title") or _get(evidence, "title") or ""
        if isinstance(page_title, str) and page_title:
            lower_title = page_title.lower()
            for kw in self._SUSPICIOUS_TITLE_KEYWORDS:
                if kw in lower_title:
                    factors.append(_factor(
                        name="Suspicious Page Title",
                        score=self._W_SUSP_TITLE,
                        description=f"Page title '{page_title}' contains the keyword '{kw}' commonly used in phishing lures.",
                        weight=self._W_SUSP_TITLE,
                        key="page_title",
                    ))
                    break

        logger.debug(f"HtmlContentEvaluator: {len(factors)} factor(s) fired.")
        return factors


# ─────────────────────────────────────────────────────────────────────────── #
# 5. Threat Intelligence Evaluator                                            #
# ─────────────────────────────────────────────────────────────────────────── #

class ThreatIntelEvaluator(BaseRiskEvaluator):
    """
    Evaluates external threat intelligence signals:
      - VirusTotal verdict (malicious / suspicious)
      - PhishTank in-database positive
      - URLHaus active malware URL
      - AbuseIPDB high confidence score
      - AlienVault OTX pulse matches
    """

    category = "threat_intelligence"
    max_contribution = RISK_WEIGHTS["threat_intelligence"]

    _W_VT_MALICIOUS      = 15.0
    _W_VT_SUSPICIOUS     =  8.0
    _W_PHISHTANK         = 10.0
    _W_URLHAUS           = 10.0
    _W_ABUSEIPDB_HIGH    =  8.0
    _W_ALIENVAULT_PULSES =  5.0

    def evaluate(self, evidence: Dict[str, Any]) -> List[RiskFactor]:
        factors: List[RiskFactor] = []

        # --- VirusTotal verdict ---
        vt_verdict = _get(evidence, "virustotal_verdict") or ""
        if isinstance(vt_verdict, str):
            vt_lower = vt_verdict.lower().strip()
            if vt_lower == "malicious":
                factors.append(_factor(
                    name="VirusTotal: Malicious Verdict",
                    score=self._W_VT_MALICIOUS,
                    description="VirusTotal consensus verdict is 'malicious'. Multiple AV engines flagged this indicator.",
                    weight=self._W_VT_MALICIOUS,
                    key="virustotal_verdict",
                ))
            elif vt_lower in ("suspicious", "phishing"):
                factors.append(_factor(
                    name="VirusTotal: Suspicious Verdict",
                    score=self._W_VT_SUSPICIOUS,
                    description=f"VirusTotal consensus verdict is '{vt_verdict}'. Indicator flagged as suspicious by AV engines.",
                    weight=self._W_VT_SUSPICIOUS,
                    key="virustotal_verdict",
                ))

        # --- PhishTank verdict ---
        pt_verdict = _get(evidence, "phishtank_verdict")
        if isinstance(pt_verdict, bool) and pt_verdict:
            factors.append(_factor(
                name="PhishTank: Confirmed Phish",
                score=self._W_PHISHTANK,
                description="Indicator is confirmed in the PhishTank database as a known phishing URL.",
                weight=self._W_PHISHTANK,
                key="phishtank_verdict",
            ))
        elif isinstance(pt_verdict, str) and pt_verdict.lower() in ("true", "phishing", "malicious"):
            factors.append(_factor(
                name="PhishTank: Confirmed Phish",
                score=self._W_PHISHTANK,
                description="Indicator is confirmed in the PhishTank database as a known phishing URL.",
                weight=self._W_PHISHTANK,
                key="phishtank_verdict",
            ))

        # --- URLHaus verdict ---
        uh_verdict = _get(evidence, "urlhaus_verdict")
        if isinstance(uh_verdict, str) and uh_verdict.lower() in ("malicious", "online", "active"):
            factors.append(_factor(
                name="URLHaus: Active Malware URL",
                score=self._W_URLHAUS,
                description=f"URLHaus reports this URL as '{uh_verdict}' — an active malware distribution or phishing endpoint.",
                weight=self._W_URLHAUS,
                key="urlhaus_verdict",
            ))

        # --- AbuseIPDB score ---
        abuse_score = _get(evidence, "abuse_confidence_score")
        if abuse_score is not None:
            try:
                score_val = float(abuse_score)
                if score_val >= 70:
                    factors.append(_factor(
                        name="AbuseIPDB: High Abuse Confidence",
                        score=self._W_ABUSEIPDB_HIGH,
                        description=f"AbuseIPDB confidence score is {score_val:.0f}% — IP is strongly associated with malicious activity.",
                        weight=self._W_ABUSEIPDB_HIGH,
                        key="abuse_confidence_score",
                    ))
            except (ValueError, TypeError):
                pass

        # --- AlienVault OTX pulses ---
        pulse_count = _get(evidence, "pulse_count")
        if pulse_count is not None:
            try:
                count = int(pulse_count)
                if count >= 3:
                    factors.append(_factor(
                        name="AlienVault OTX: Multiple Threat Pulses",
                        score=self._W_ALIENVAULT_PULSES,
                        description=f"Indicator appears in {count} AlienVault OTX threat intelligence pulses.",
                        weight=self._W_ALIENVAULT_PULSES,
                        key="pulse_count",
                    ))
            except (ValueError, TypeError):
                pass

        logger.debug(f"ThreatIntelEvaluator: {len(factors)} factor(s) fired.")
        return factors


# ─────────────────────────────────────────────────────────────────────────── #
# Registry — ordered list of all evaluators                                   #
# ─────────────────────────────────────────────────────────────────────────── #

ALL_EVALUATORS: List[BaseRiskEvaluator] = [
    DomainIntelEvaluator(),
    DnsWhoisEvaluator(),
    TlsCertificateEvaluator(),
    HtmlContentEvaluator(),
    ThreatIntelEvaluator(),
]

# Total maximum raw contribution (denominator for 0-100 normalization)
# Sourced from config.py TOTAL_WEIGHT for consistency
TOTAL_MAX_CONTRIBUTION: float = TOTAL_WEIGHT
