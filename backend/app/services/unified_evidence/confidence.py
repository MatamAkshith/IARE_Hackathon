from typing import Any, Dict
from app.services.unified_evidence.models import EvidenceConfidence

class EvidenceConfidenceEngine:
    def evaluate_item_confidence(
        self,
        key: str,
        value: Any,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any]
    ) -> EvidenceConfidence:
        """
        Evaluates the source and reliability of individual data points to assign a confidence level.
        """
        # Malformed or empty values get UNKNOWN
        if value is None or value == "":
            return EvidenceConfidence.UNKNOWN

        # Critical external threat intelligence indicators
        critical_external_keys = [
            "virustotal_verdict",
            "phishtank_verdict",
            "urlhaus_verdict",
            "overall_verdict",
            "abuse_confidence_score",
            "pulse_count",
            "raw_response",
            "provider_responses",
            "abuseipdb_verdict",
            "alienvault_verdict"
        ]

        if key in critical_external_keys or key in external_data:
            return EvidenceConfidence.HIGH

        # Heuristic rules or features from internal extraction
        internal_keys = [
            "has_login_form",
            "domain_age_days",
            "ssl_valid",
            "ns_records",
            "mx_records",
            "forms_count",
            "password_inputs",
            "extracted_emails"
        ]
        
        if key in internal_keys or key in internal_data:
            return EvidenceConfidence.MEDIUM

        return EvidenceConfidence.LOW

    def calculate_overall_confidence(
        self,
        item_confidences: Dict[str, EvidenceConfidence]
    ) -> EvidenceConfidence:
        """
        Calculates consensus overall confidence.
        If any item has HIGH confidence, overall is HIGH.
        Otherwise, average score determines consensus.
        """
        if not item_confidences:
            return EvidenceConfidence.UNKNOWN

        confidences_list = list(item_confidences.values())
        if EvidenceConfidence.HIGH in confidences_list:
            return EvidenceConfidence.HIGH

        confidence_values = {
            EvidenceConfidence.HIGH: 3,
            EvidenceConfidence.MEDIUM: 2,
            EvidenceConfidence.LOW: 1,
            EvidenceConfidence.UNKNOWN: 0
        }
        
        total_score = sum(confidence_values[c] for c in confidences_list)
        avg_score = total_score / len(confidences_list)

        if avg_score >= 2.0:
            return EvidenceConfidence.MEDIUM
        elif avg_score >= 1.0:
            return EvidenceConfidence.LOW
        else:
            return EvidenceConfidence.UNKNOWN
