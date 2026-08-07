"""
Centralized Risk Engine Configuration — Stage 6.5

All tunable weights, thresholds, and multipliers are defined here so that
calibration changes require editing only this single file.

Design:
  - RISK_WEIGHTS: per-category max contribution to the raw score (sum = 100).
  - CONFIDENCE_MULTIPLIERS: scales the normalized score based on evidence reliability.
  - SEVERITY_THRESHOLDS: score → RiskSeverity tier mapping boundaries.
"""

# ─────────────────────────────────────────────────────────────────────────── #
# Category Weight Configuration                                               #
#                                                                              #
# Adjusting these values changes how much each evidence domain can             #
# influence the final 0-100 risk score.  The sum MUST equal 100.              #
# ─────────────────────────────────────────────────────────────────────────── #

RISK_WEIGHTS: dict[str, float] = {
    "domain_intelligence": 25.0,
    "dns_whois":           15.0,
    "tls_certificate":     15.0,
    "html_content":        20.0,
    "threat_intelligence": 25.0,
}

# Pre-computed total — used as the denominator for 0-100 normalization
TOTAL_WEIGHT: float = sum(RISK_WEIGHTS.values())


# ─────────────────────────────────────────────────────────────────────────── #
# Confidence Multipliers                                                       #
#                                                                              #
# After normalizing the raw score to 0-100, the result is multiplied by        #
# the factor corresponding to the evidence's overall confidence level.         #
# This ensures low-confidence evidence produces a proportionally reduced       #
# risk score, preventing false alarms from unreliable data.                    #
# ─────────────────────────────────────────────────────────────────────────── #

CONFIDENCE_MULTIPLIERS: dict[str, float] = {
    "high":    1.00,   # Full trust — score passes through unchanged
    "medium":  0.85,   # Moderate trust — 15% reduction
    "low":     0.60,   # Low trust — 40% reduction
    "unknown": 0.50,   # No confidence signal — 50% reduction
}

# Default multiplier when the confidence key is not found in the map
DEFAULT_CONFIDENCE_MULTIPLIER: float = 0.75


# ─────────────────────────────────────────────────────────────────────────── #
# Severity Threshold Configuration                                             #
#                                                                              #
# Evaluated top-down: the first threshold the score meets or exceeds           #
# determines the severity tier.                                                #
# ─────────────────────────────────────────────────────────────────────────── #

SEVERITY_THRESHOLDS: list[tuple[float, str]] = [
    (86.0, "critical"),
    (66.0, "high"),
    (41.0, "medium"),
    (16.0, "low"),
    ( 0.0, "safe"),
]


# ─────────────────────────────────────────────────────────────────────────── #
# Evidence Category Key Maps (for dynamic denominator calculation)             #
# ─────────────────────────────────────────────────────────────────────────── #

CATEGORY_EVIDENCE_KEYS: dict[str, frozenset] = {
    "domain_intelligence": frozenset({
        "domain_age_days", "ip_address", "indicator", "url",
    }),
    "dns_whois": frozenset({
        "mx_records", "ns_records", "whois_privacy", "registrant_redacted",
    }),
    "tls_certificate": frozenset({
        "ssl_valid", "tls_issuer", "cert_issuer", "cert_days_remaining",
    }),
    "html_content": frozenset({
        "has_login_form", "password_inputs", "forms_count", "page_title", "title",
    }),
    "threat_intelligence": frozenset({
        "virustotal_verdict", "phishtank_verdict", "urlhaus_verdict",
        "abuse_confidence_score", "pulse_count", "overall_verdict",
    }),
}
