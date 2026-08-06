import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import tldextract
import whois
import dns.resolver

logger = logging.getLogger("app.services.domain_intel")

class DomainIntelService:
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Ensure the input has a valid http/https scheme.
        If missing, defaults to https.
        """
        trimmed = url.strip()
        if not trimmed.lower().startswith(("http://", "https://")):
            return f"https://{trimmed}"
        return trimmed

    @staticmethod
    def extract_domain_info(url: str) -> Dict[str, Any]:
        """
        Parse subdomain, domain, and TLD from the URL using tldextract.
        """
        extracted = tldextract.extract(url)
        subdomain = extracted.subdomain
        domain = extracted.domain
        suffix = extracted.suffix
        
        full_domain = f"{domain}.{suffix}"
        if subdomain:
            full_domain = f"{subdomain}.{full_domain}"

        return {
            "subdomain": subdomain or None,
            "domain_name": domain or None,
            "tld": suffix or None,
            "registered_domain": f"{domain}.{suffix}" if domain and suffix else None,
            "full_domain": full_domain
        }

    @staticmethod
    def resolve_dns(domain: str) -> Dict[str, List[str]]:
        """
        Query DNS records (A, MX, NS) for the given domain.
        Returns empty lists on failure.
        """
        records = {"A": [], "MX": [], "NS": []}
        
        # A records
        try:
            answers = dns.resolver.resolve(domain, "A")
            records["A"] = [str(rdata) for rdata in answers]
        except Exception as e:
            logger.debug(f"Failed to resolve A records for {domain}: {e}")

        # MX records
        try:
            answers = dns.resolver.resolve(domain, "MX")
            records["MX"] = [str(rdata.exchange).rstrip(".") for rdata in answers]
        except Exception as e:
            logger.debug(f"Failed to resolve MX records for {domain}: {e}")

        # NS records
        try:
            answers = dns.resolver.resolve(domain, "NS")
            records["NS"] = [str(rdata.target).rstrip(".") for rdata in answers]
        except Exception as e:
            logger.debug(f"Failed to resolve NS records for {domain}: {e}")

        return records

    @staticmethod
    def query_whois(domain: str) -> Dict[str, Any]:
        """
        Execute WHOIS lookup using python-whois.
        Returns empty/None dict if WHOIS fails.
        """
        whois_data = {
            "registrar": None,
            "creation_date": None,
            "expiration_date": None,
            "name_servers": [],
            "domain_age_days": None
        }

        try:
            w = whois.whois(domain)
            whois_data["registrar"] = w.get("registrar")

            # Handle creation date (can be single datetime, list, or None)
            c_date = w.get("creation_date")
            parsed_c_date = None
            if isinstance(c_date, list):
                # Pick the first valid datetime
                valid_dates = [d for d in c_date if isinstance(d, datetime)]
                if valid_dates:
                    parsed_c_date = valid_dates[0]
            elif isinstance(c_date, datetime):
                parsed_c_date = c_date

            if parsed_c_date:
                whois_data["creation_date"] = parsed_c_date.isoformat()
                # Calculate domain age in days
                now = datetime.now(parsed_c_date.tzinfo or timezone.utc)
                # Ensure parsed_c_date has timezone if now does
                c_date_tz = parsed_c_date.replace(tzinfo=parsed_c_date.tzinfo or timezone.utc)
                age_delta = now - c_date_tz
                whois_data["domain_age_days"] = max(0, age_delta.days)

            # Handle expiration date (can be single datetime, list, or None)
            exp_date = w.get("expiration_date")
            parsed_exp_date = None
            if isinstance(exp_date, list):
                valid_dates = [d for d in exp_date if isinstance(d, datetime)]
                if valid_dates:
                    parsed_exp_date = valid_dates[0]
            elif isinstance(exp_date, datetime):
                parsed_exp_date = exp_date

            if parsed_exp_date:
                whois_data["expiration_date"] = parsed_exp_date.isoformat()

            # Handle name servers
            n_servers = w.get("name_servers")
            if isinstance(n_servers, list):
                whois_data["name_servers"] = [str(ns).lower() for ns in n_servers]
            elif isinstance(n_servers, str):
                whois_data["name_servers"] = [n_servers.lower()]

        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {e}")

        return whois_data

    def extract_intelligence(self, url: str) -> Dict[str, Any]:
        """
        Accepts a raw URL, normalizes it, extracts domain parts, resolves DNS,
        and retrieves WHOIS info.
        """
        normalized_url = self.normalize_url(url)
        domain_parts = self.extract_domain_info(normalized_url)
        target_domain = domain_parts["registered_domain"] or domain_parts["full_domain"]

        dns_records = self.resolve_dns(target_domain)
        whois_records = self.query_whois(target_domain)

        return {
            "url": normalized_url,
            "domain_parts": domain_parts,
            "dns": dns_records,
            "whois": whois_records
        }
