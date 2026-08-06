import logging
from datetime import datetime, timezone
from typing import Any, Dict
from app.services.domain_intel import DomainIntelService
from app.services.network_intel import NetworkIntelService
from app.services.webpage_intel import WebpageIntelService

logger = logging.getLogger("app.services.feature_aggregator")

class FeatureAggregationService:
    def __init__(self) -> None:
        self.domain_service = DomainIntelService()
        self.network_service = NetworkIntelService()
        self.webpage_service = WebpageIntelService()

    def aggregate_features(self, url: str) -> Dict[str, Any]:
        """
        Orchestrate features extraction for URL across Domain, Network, and Webpage services.
        Aggregates outputs into a single, validated evidence object, catching errors gracefully.
        """
        errors = {}
        status = "success"

        # 1. Domain Intelligence
        try:
            domain_intel = self.domain_service.extract_intelligence(url)
        except Exception as e:
            logger.error(f"DomainIntelService failed: {e}")
            domain_intel = {}
            errors["domain_intelligence"] = str(e)
            status = "partial_success"

        # 2. Network Intelligence
        try:
            # DomainIntelService normalizes the URL. We can use normalized url or pass raw
            normalized_url = domain_intel.get("url", url)
            network_intel = self.network_service.extract_network_intelligence(normalized_url)
        except Exception as e:
            logger.error(f"NetworkIntelService failed: {e}")
            network_intel = {}
            errors["network_intelligence"] = str(e)
            status = "partial_success"

        # 3. Webpage Intelligence
        try:
            normalized_url = domain_intel.get("url", url)
            webpage_intel = self.webpage_service.extract_webpage_intelligence(normalized_url)
            # If fetch_html returns None, let's treat it as a partial failure/warning
            if not webpage_intel.get("metadata", {}).get("title") and not webpage_intel.get("structure", {}).get("total_forms"):
                # Check if fetched HTML was empty
                html_fetched = self.webpage_service.fetch_html(normalized_url)
                if not html_fetched:
                    errors["webpage_intelligence"] = "Failed to fetch HTML content (host offline or request timeout)"
                    status = "partial_success"
        except Exception as e:
            logger.error(f"WebpageIntelService failed: {e}")
            webpage_intel = {}
            errors["webpage_intelligence"] = str(e)
            status = "partial_success"

        if len(errors) == 3:
            status = "failed"

        return {
            "domain_intelligence": domain_intel,
            "network_intelligence": network_intel,
            "webpage_intelligence": webpage_intel,
            "metadata": {
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "errors": errors
            }
        }
