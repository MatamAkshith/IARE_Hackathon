"""
Concrete Campaign Correlation Strategies — Stage 7.2

Implements Infrastructure, TLS, WHOIS, and HTML content correlators
subclassing BaseCorrelationStrategy. Each correlator returns a list of
CorrelationEvidence when matches/overlaps are found between two evidence dicts.
"""

from typing import Any, Dict, List, Set
import logging

from app.services.campaign_engine.base import BaseCorrelationStrategy
from app.services.campaign_engine.models import CorrelationEvidence

logger = logging.getLogger("app.services.campaign_engine.correlators")


def _clean_str(val: Any) -> str:
    """Helper to sanitize and standardize string values for exact comparison."""
    if val is None:
        return ""
    return str(val).strip().lower()


def _compare_lists(list_a: Any, list_b: Any) -> Set[str]:
    """Finds intersection of two lists/sets after cleaning and standardizing strings."""
    if not list_a or not list_b:
        return set()
    
    set_a = {_clean_str(x) for x in list_a if x}
    set_b = {_clean_str(x) for x in list_b if x}
    
    # Filter out empty values and return intersection
    return {x for x in set_a.intersection(set_b) if x}


class InfrastructureCorrelator(BaseCorrelationStrategy):
    """
    Correlates indicators based on IP address, ASN, and DNS A/AAAA records.
    """

    @property
    def strategy_name(self) -> str:
        return "infrastructure"

    def correlate_pair(
        self,
        evidence_a: Dict[str, Any],
        evidence_b: Dict[str, Any],
    ) -> List[CorrelationEvidence]:
        evidence_list: List[CorrelationEvidence] = []

        # 1. Compare IP address
        ip_a = _clean_str(evidence_a.get("ip_address") or evidence_a.get("ip"))
        ip_b = _clean_str(evidence_b.get("ip_address") or evidence_b.get("ip"))
        
        if ip_a and ip_b and ip_a == ip_b:
            logger.debug(f"[InfrastructureCorrelator] Shared IP address match: '{ip_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_ip",
                value=ip_a,
                confidence="high",
                description=f"Both indicators resolve to the same hosting IP address: '{ip_a}'"
            ))

        # 2. Compare ASN
        asn_a = _clean_str(evidence_a.get("asn") or evidence_a.get("autonomous_system_number"))
        asn_b = _clean_str(evidence_b.get("asn") or evidence_b.get("autonomous_system_number"))

        if asn_a and asn_b and asn_a == asn_b:
            logger.debug(f"[InfrastructureCorrelator] Shared ASN match: '{asn_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_asn",
                value=asn_a,
                confidence="low",
                description=f"Both indicators are hosted within the same Autonomous System Network: '{asn_a}'"
            ))

        # 3. Compare DNS A/AAAA records (if stored as lists/sets)
        dns_a = evidence_a.get("dns_a_records") or evidence_a.get("a_records") or []
        dns_b = evidence_b.get("dns_a_records") or evidence_b.get("a_records") or []
        shared_dns = _compare_lists(dns_a, dns_b)

        if shared_dns:
            val_str = ", ".join(sorted(shared_dns))
            logger.debug(f"[InfrastructureCorrelator] Shared DNS A records match: '{val_str}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_dns_records",
                value=val_str,
                confidence="high",
                description=f"Both indicators share the following DNS resolving A/AAAA records: {val_str}"
            ))

        return evidence_list


class TlsCorrelator(BaseCorrelationStrategy):
    """
    Correlates indicators based on peer TLS/SSL certificate serial numbers,
    issuer details, and subject strings.
    """

    @property
    def strategy_name(self) -> str:
        return "tls"

    def correlate_pair(
        self,
        evidence_a: Dict[str, Any],
        evidence_b: Dict[str, Any],
    ) -> List[CorrelationEvidence]:
        evidence_list: List[CorrelationEvidence] = []

        # 1. Compare certificate serial number (Strongest cert correlation)
        serial_a = _clean_str(evidence_a.get("tls_serial") or evidence_a.get("cert_serial"))
        serial_b = _clean_str(evidence_b.get("tls_serial") or evidence_b.get("cert_serial"))

        if serial_a and serial_b and serial_a == serial_b:
            logger.debug(f"[TlsCorrelator] Shared TLS serial match: '{serial_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_tls_serial",
                value=serial_a,
                confidence="high",
                description=f"Both indicators share the exact TLS certificate serial number: '{serial_a}'"
            ))

        # 2. Compare certificate subject (CN or Organization name matches)
        subj_a = _clean_str(evidence_a.get("tls_subject") or evidence_a.get("cert_subject"))
        subj_b = _clean_str(evidence_b.get("tls_subject") or evidence_b.get("cert_subject"))

        if subj_a and subj_b and subj_a == subj_b:
            logger.debug(f"[TlsCorrelator] Shared TLS subject match: '{subj_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_tls_subject",
                value=subj_a,
                confidence="medium",
                description=f"Both indicators share the TLS certificate subject Common Name (CN): '{subj_a}'"
            ))

        # 3. Compare certificate issuer
        issuer_a = _clean_str(evidence_a.get("tls_issuer") or evidence_a.get("cert_issuer"))
        issuer_b = _clean_str(evidence_b.get("tls_issuer") or evidence_b.get("cert_issuer"))

        # Skip matching if it's a common issuer like Let's Encrypt unless other signals match,
        # but to keep it deterministic and simple: check equality but mark as low confidence.
        if issuer_a and issuer_b and issuer_a == issuer_b:
            # Only report if it's not empty/null
            logger.debug(f"[TlsCorrelator] Shared TLS issuer match: '{issuer_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_tls_issuer",
                value=issuer_a,
                confidence="low",
                description=f"Both indicators share the same TLS certificate authority issuer: '{issuer_a}'"
            ))

        return evidence_list


class WhoisCorrelator(BaseCorrelationStrategy):
    """
    Correlates indicators based on WHOIS registrar, registrant organization,
    and creation/registration dates.
    """

    @property
    def strategy_name(self) -> str:
        return "whois"

    def correlate_pair(
        self,
        evidence_a: Dict[str, Any],
        evidence_b: Dict[str, Any],
    ) -> List[CorrelationEvidence]:
        evidence_list: List[CorrelationEvidence] = []

        # 1. Compare registrant organization
        org_a = _clean_str(evidence_a.get("registrant_org") or evidence_a.get("org"))
        org_b = _clean_str(evidence_b.get("registrant_org") or evidence_b.get("org"))

        # Filter out privacy services or redacted values
        ignored_orgs = {"redacted", "privacy", "not available", "redacted for privacy", "privacy service"}
        is_valid_org = lambda o: o and not any(ign in o for ign in ignored_orgs)

        if is_valid_org(org_a) and is_valid_org(org_b) and org_a == org_b:
            logger.debug(f"[WhoisCorrelator] Shared registrant organization match: '{org_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_registrant_org",
                value=org_a,
                confidence="high",
                description=f"Both domains are registered to the same registrant organization: '{org_a}'"
            ))

        # 2. Compare registrar
        reg_a = _clean_str(evidence_a.get("registrar"))
        reg_b = _clean_str(evidence_b.get("registrar"))

        # Registrar is a weaker link (many sites use Namecheap, GoDaddy, etc.)
        if reg_a and reg_b and reg_a == reg_b:
            logger.debug(f"[WhoisCorrelator] Shared registrar match: '{reg_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_registrar",
                value=reg_a,
                confidence="low",
                description=f"Both domains were registered via the same registrar authority: '{reg_a}'"
            ))

        # 3. Compare creation date (exact match or same-day registration)
        created_a = _clean_str(evidence_a.get("domain_creation_date") or evidence_a.get("creation_date") or evidence_a.get("created_at"))
        created_b = _clean_str(evidence_b.get("domain_creation_date") or evidence_b.get("creation_date") or evidence_b.get("created_at"))

        # Only check if length is sufficient to represent a date
        if created_a and created_b and len(created_a) >= 10 and len(created_b) >= 10:
            # Compare first 10 characters (YYYY-MM-DD)
            date_a = created_a[:10]
            date_b = created_b[:10]
            if date_a == date_b:
                logger.debug(f"[WhoisCorrelator] Shared domain creation date match: '{date_a}'")
                evidence_list.append(CorrelationEvidence(
                    type="shared_domain_creation_date",
                    value=date_a,
                    confidence="medium",
                    description=f"Both domains were registered on the exact same date: '{date_a}'"
                ))

        return evidence_list


class HtmlCorrelator(BaseCorrelationStrategy):
    """
    Correlates indicators based on HTML webpage features: page title, forms count,
    and structural hashes.
    """

    @property
    def strategy_name(self) -> str:
        return "html"

    def correlate_pair(
        self,
        evidence_a: Dict[str, Any],
        evidence_b: Dict[str, Any],
    ) -> List[CorrelationEvidence]:
        evidence_list: List[CorrelationEvidence] = []

        # 1. Compare HTML Page Title
        title_a = _clean_str(evidence_a.get("page_title") or evidence_a.get("title"))
        title_b = _clean_str(evidence_b.get("page_title") or evidence_b.get("title"))

        # Skip generic titles
        generic_titles = {"welcome", "index", "home", "login", "signin", "error", "404"}
        is_valid_title = lambda t: t and t not in generic_titles and len(t) > 3

        if is_valid_title(title_a) and is_valid_title(title_b) and title_a == title_b:
            logger.debug(f"[HtmlCorrelator] Shared HTML page title match: '{title_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_page_title",
                value=title_a,
                confidence="medium",
                description=f"Both pages render with the identical HTML page title: '{title_a}'"
            ))

        # 2. Compare HTML Structural Hash / Template signature
        hash_a = _clean_str(evidence_a.get("html_structure_hash") or evidence_a.get("structural_hash"))
        hash_b = _clean_str(evidence_b.get("html_structure_hash") or evidence_b.get("structural_hash"))

        if hash_a and hash_b and hash_a == hash_b:
            logger.debug(f"[HtmlCorrelator] Shared HTML structure hash match: '{hash_a}'")
            evidence_list.append(CorrelationEvidence(
                type="shared_html_structure_hash",
                value=hash_a,
                confidence="high",
                description=f"Both pages share the identical structural HTML structure template signature hash: '{hash_a}'"
            ))

        # 3. Compare Forms Count
        forms_a = evidence_a.get("forms_count")
        forms_b = evidence_b.get("forms_count")

        if forms_a is not None and forms_b is not None:
            try:
                count_a = int(forms_a)
                count_b = int(forms_b)
                # Only check if forms count is non-trivial (> 0) and matches
                if count_a > 0 and count_a == count_b:
                    logger.debug(f"[HtmlCorrelator] Shared forms count match: {count_a}")
                    evidence_list.append(CorrelationEvidence(
                        type="shared_forms_count",
                        value=str(count_a),
                        confidence="low",
                        description=f"Both pages contain the identical number of active web forms: {count_a}"
                    ))
            except (ValueError, TypeError):
                pass

        return evidence_list
