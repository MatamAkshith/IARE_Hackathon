from abc import ABC, abstractmethod
import time
import logging
from typing import Optional
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict

class BaseThreatIntelProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the unique identifier/name of the provider.
        """
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Return whether this provider is currently enabled (e.g., config is active).
        """
        pass

    @abstractmethod
    async def lookup_url(self, url: str) -> ProviderResponse:
        """
        Check the threat status of a URL.
        """
        pass

    @abstractmethod
    async def lookup_domain(self, domain: str) -> ProviderResponse:
        """
        Check the threat status of a domain.
        """
        pass

    @abstractmethod
    async def lookup_ip(self, ip: str) -> ProviderResponse:
        """
        Check the threat status of an IP address.
        """
        pass

    def _unsupported_indicator(self, indicator_type: str) -> ProviderResponse:
        """
        Helper method to generate an UNKNOWN response for unsupported indicators.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error=f"{indicator_type.upper()} lookup is unsupported by {self.provider_name}",
            response_time_ms=0
        )

    def _disabled_response(self) -> ProviderResponse:
        """
        Helper method to generate an UNKNOWN response when the provider is disabled.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error=f"Provider {self.provider_name} is disabled or API key is missing",
            response_time_ms=0
        )

    async def _safe_lookup(self, indicator: str, indicator_type: str, lookup_coro) -> ProviderResponse:
        """
        Helper wrapper to handle timing, logging, validation status checks, and exceptions consistently.
        """
        logger = logging.getLogger(f"app.services.threat_intel.providers.{self.provider_name.lower().replace(' ', '_')}")
        logger.info(f"Starting {indicator_type.upper()} lookup for '{indicator}' on {self.provider_name}")
        
        if not self.is_enabled:
            logger.warning(f"{self.provider_name} lookup requested but provider is disabled")
            return self._disabled_response()
            
        start_time = time.time()
        try:
            response = await lookup_coro
            response_time_ms = int((time.time() - start_time) * 1000)
            response.response_time_ms = response_time_ms
            
            if response.error:
                logger.warning(f"Completed lookup on {self.provider_name} with error: {response.error} (took {response_time_ms}ms)")
            else:
                logger.info(f"Completed lookup on {self.provider_name} successfully (took {response_time_ms}ms, verdict: {response.verdict})")
            
            return response
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Error during lookup on {self.provider_name} (took {response_time_ms}ms): {e}", exc_info=True)
            return ProviderResponse(
                provider_name=self.provider_name,
                verdict=ThreatVerdict.UNKNOWN,
                matches=[],
                raw_response={},
                error=f"Lookup failed: {str(e)}",
                response_time_ms=response_time_ms
            )
