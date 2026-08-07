import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import asyncio

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ThreatEvidence, ProviderResponse, ThreatVerdict, AggregatedThreatEvidence



from app.core.config import settings
from app.services.threat_intel.providers.virustotal import VirusTotalProvider
from app.services.threat_intel.providers.phishtank import PhishTankProvider
from app.services.threat_intel.providers.urlhaus import URLHausProvider
from app.services.threat_intel.providers.abuseipdb import AbuseIPDBProvider
from app.services.threat_intel.providers.alienvault import AlienVaultProvider

logger = logging.getLogger("app.services.threat_intel.service")

class ThreatIntelService:
    def __init__(self) -> None:
        self._providers: Dict[str, BaseThreatIntelProvider] = {}
        
        # Instantiate and auto-register VirusTotal if enabled
        vt_provider = VirusTotalProvider(api_key=settings.VIRUSTOTAL_API_KEY)
        if vt_provider.is_enabled:
            self.register_provider(vt_provider)

        # Instantiate and auto-register PhishTank
        pt_provider = PhishTankProvider(api_key=settings.PHISHTANK_API_KEY)
        if pt_provider.is_enabled:
            self.register_provider(pt_provider)

        # Instantiate and auto-register URLHaus
        uh_provider = URLHausProvider()
        if uh_provider.is_enabled:
            self.register_provider(uh_provider)

        # Instantiate and auto-register AbuseIPDB if enabled
        ab_provider = AbuseIPDBProvider(api_key=settings.ABUSEIPDB_API_KEY)
        if ab_provider.is_enabled:
            self.register_provider(ab_provider)

        # Instantiate and auto-register AlienVault OTX if enabled
        av_provider = AlienVaultProvider(api_key=settings.ALIENVAULT_OTX_API_KEY)
        if av_provider.is_enabled:
            self.register_provider(av_provider)

        logger.info(f"Initialized ThreatIntelService. Active providers: {list(self._providers.keys())}")





    def register_provider(self, provider: BaseThreatIntelProvider) -> None:
        """
        Register a threat intelligence provider.
        """
        self._providers[provider.provider_name] = provider
        logger.info(f"Registered threat intel provider: {provider.provider_name}")

    def get_providers(self) -> List[BaseThreatIntelProvider]:
        """
        Get all registered providers.
        """
        return list(self._providers.values())

    def get_enabled_providers(self) -> List[BaseThreatIntelProvider]:
        """
        Get all registered and enabled providers.
        """
        return [p for p in self.get_providers() if p.is_enabled]

    async def lookup_url(self, url: str) -> ThreatEvidence:
        """
        Query all enabled registered providers to check the status of a URL.
        """
        providers = self.get_enabled_providers()
        if not providers:
            return ThreatEvidence(
                responses={},
                execution_status="no_providers_enabled",
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        responses: Dict[str, ProviderResponse] = {}
        errors = {}

        # Query all providers concurrently using asyncio.gather
        tasks = [p.lookup_url(url) for p in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                logger.error(f"Provider {provider.provider_name} URL lookup failed: {result}")
                errors[provider.provider_name] = str(result)
                # Save dummy/failed response
                responses[provider.provider_name] = ProviderResponse(
                    provider_name=provider.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=str(result),
                    status="unavailable",
                    response_time_ms=0
                )
            else:
                responses[provider.provider_name] = result

        status = "success"
        if errors:
            status = "failed" if len(errors) == len(providers) else "partial_success"

        return ThreatEvidence(
            responses=responses,
            execution_status=status,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    async def lookup_domain(self, domain: str) -> ThreatEvidence:
        """
        Query all enabled registered providers to check the status of a domain.
        """
        providers = self.get_enabled_providers()
        if not providers:
            return ThreatEvidence(
                responses={},
                execution_status="no_providers_enabled",
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        responses: Dict[str, ProviderResponse] = {}
        errors = {}

        tasks = [p.lookup_domain(domain) for p in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                logger.error(f"Provider {provider.provider_name} domain lookup failed: {result}")
                errors[provider.provider_name] = str(result)
                responses[provider.provider_name] = ProviderResponse(
                    provider_name=provider.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=str(result),
                    status="unavailable",
                    response_time_ms=0
                )
            else:
                responses[provider.provider_name] = result

        status = "success"
        if errors:
            status = "failed" if len(errors) == len(providers) else "partial_success"

        return ThreatEvidence(
            responses=responses,
            execution_status=status,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    async def lookup_ip(self, ip: str) -> ThreatEvidence:
        """
        Query all enabled registered providers to check the status of an IP.
        """
        providers = self.get_enabled_providers()
        if not providers:
            return ThreatEvidence(
                responses={},
                execution_status="no_providers_enabled",
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        responses: Dict[str, ProviderResponse] = {}
        errors = {}

        tasks = [p.lookup_ip(ip) for p in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                logger.error(f"Provider {provider.provider_name} IP lookup failed: {result}")
                errors[provider.provider_name] = str(result)
                responses[provider.provider_name] = ProviderResponse(
                    provider_name=provider.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=str(result),
                    status="unavailable",
                    response_time_ms=0
                )
            else:
                responses[provider.provider_name] = result

        status = "success"
        if errors:
            status = "failed" if len(errors) == len(providers) else "partial_success"

        return ThreatEvidence(
            responses=responses,
            execution_status=status,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    async def aggregate_lookup(
        self, indicator: str, indicator_type: Optional[str] = None, timeout: float = 5.0
    ) -> AggregatedThreatEvidence:
        """
        Synthesize concurrent lookups across all enabled/registered threat feeds.
        """
        from app.services.threat_intel.aggregator import ThreatIntelAggregator
        aggregator = ThreatIntelAggregator(self)
        return await aggregator.aggregate_lookup(indicator, indicator_type, timeout)

