import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import asyncio

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ThreatEvidence, ProviderResponse, ThreatVerdict

logger = logging.getLogger("app.services.threat_intel.service")

class ThreatIntelService:
    def __init__(self) -> None:
        self._providers: Dict[str, BaseThreatIntelProvider] = {}

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
