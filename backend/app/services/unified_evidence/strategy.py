import logging
from typing import Any, Dict, List, Optional

from app.services.unified_evidence.service import BaseMergeStrategy

logger = logging.getLogger("app.services.unified_evidence.strategy")


class DefaultMergeStrategy(BaseMergeStrategy):
    def merge(
        self,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
        conflict_resolutions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Merges internal evidence and external threat intel data.

        Conflict Resolution Rule: When a key exists in both datasets with differing values,
        the external_data value takes priority and the override is recorded for traceability.

        Deduplication: Identical overlapping key-value pairs are stored only once.
        """
        if conflict_resolutions is None:
            conflict_resolutions = []

        resolved: Dict[str, Any] = {}

        # 1. Seed with all raw keys to preserve nested categories for standard access
        for k, v in internal_data.items():
            resolved[k] = v
            logger.debug(f"Collected internal key '{k}'.")

        # 2. Extract and flatten internal telemetry features to support down-pipeline evaluators
        # Domain intelligence
        dom_intel = internal_data.get("domain_intelligence") or {}
        if dom_intel:
            if dom_intel.get("url"):
                resolved["url"] = dom_intel["url"]
            parts = dom_intel.get("domain_parts") or {}
            if parts.get("domain_name"):
                resolved["domain_name"] = parts["domain_name"]
            if parts.get("tld"):
                resolved["tld"] = parts["tld"]
            dns_rec = dom_intel.get("dns") or {}
            if "A" in dns_rec:
                resolved["a_records"] = dns_rec["A"]
                if dns_rec["A"] and not resolved.get("ip_address"):
                    resolved["ip_address"] = dns_rec["A"][0]
            if "MX" in dns_rec:
                resolved["mx_records"] = dns_rec["MX"]
            if "NS" in dns_rec:
                resolved["ns_records"] = dns_rec["NS"]
            whois_rec = dom_intel.get("whois") or {}
            if whois_rec:
                if whois_rec.get("registrar"):
                    resolved["whois_registrar"] = whois_rec["registrar"]
                    resolved["registrar"] = whois_rec["registrar"]
                if whois_rec.get("creation_date"):
                    resolved["whois_creation_date"] = whois_rec["creation_date"]
                    resolved["creation_date"] = whois_rec["creation_date"]
                if whois_rec.get("expiration_date"):
                    resolved["whois_expiration_date"] = whois_rec["expiration_date"]
                    resolved["expiry_date"] = whois_rec["expiration_date"]
                if whois_rec.get("domain_age_days") is not None:
                    resolved["domain_age_days"] = whois_rec["domain_age_days"]
                
                # Check for private or redacted registrant / privacy
                registrar = whois_rec.get("registrar") or ""
                if any(x in str(registrar).lower() for x in ("private", "redact", "protect")):
                    resolved["whois_privacy"] = True
                    resolved["registrant_redacted"] = True

        # Network intelligence
        net_intel = internal_data.get("network_intelligence") or {}
        if net_intel:
            dns_res = net_intel.get("dns_resolution") or {}
            if dns_res.get("ip_address"):
                resolved["ip_address"] = dns_res["ip_address"]
            if dns_res.get("reverse_dns"):
                resolved["reverse_dns"] = dns_res["reverse_dns"]
            ssl_c = net_intel.get("ssl_cert") or {}
            if ssl_c:
                resolved["ssl_valid"] = ssl_c.get("ssl_available", False)
                resolved["ssl_available"] = ssl_c.get("ssl_available", False)
                if ssl_c.get("issuer"):
                    resolved["ssl_issuer"] = ssl_c["issuer"]
                    resolved["tls_issuer"] = ssl_c["issuer"]
                    resolved["cert_issuer"] = ssl_c["issuer"]
                if ssl_c.get("common_name"):
                    resolved["ssl_common_name"] = ssl_c["common_name"]
                if ssl_c.get("days_until_expiry") is not None:
                    resolved["ssl_days_remaining"] = ssl_c["days_until_expiry"]
                    resolved["cert_days_remaining"] = ssl_c["days_until_expiry"]
            http_c = net_intel.get("http_characteristics") or {}
            if http_c:
                if http_c.get("status_code") is not None:
                    resolved["http_status_code"] = http_c["status_code"]
                if http_c.get("final_url"):
                    resolved["final_url"] = http_c["final_url"]

        # Webpage intelligence
        web_intel = internal_data.get("webpage_intelligence") or {}
        if web_intel:
            meta = web_intel.get("metadata") or {}
            if meta.get("title"):
                resolved["page_title"] = meta["title"]
                resolved["title"] = meta["title"]
            struct = web_intel.get("structure") or {}
            if struct:
                resolved["has_login_form"] = struct.get("is_login_form_detected", False)
                resolved["is_login_form_detected"] = struct.get("is_login_form_detected", False)
                resolved["password_inputs"] = 1 if struct.get("has_password_field", False) else 0
                resolved["has_password_field"] = struct.get("has_password_field", False)
                resolved["forms_count"] = struct.get("total_forms", 0)
                resolved["total_forms"] = struct.get("total_forms", 0)

        # Overlay external evidence, enforcing external-wins conflict rule
        for k, v in external_data.items():
            if k in resolved:
                if resolved[k] != v:
                    old_val = resolved[k]
                    resolved[k] = v
                    note = (
                        f"Conflict resolved for key '{k}': "
                        f"prioritized external value '{v}' over internal value '{old_val}'"
                    )
                    conflict_resolutions.append(note)
                    logger.debug(note)
                # else: identical value — already deduplicated, no action needed
            else:
                resolved[k] = v
                logger.debug(f"Ingested external key '{k}'.")

        logger.info(
            f"Merge complete: {len(resolved)} keys resolved, "
            f"{len(conflict_resolutions)} conflict(s) encountered."
        )
        return resolved
