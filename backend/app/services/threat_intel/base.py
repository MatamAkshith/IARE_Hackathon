from abc import ABC, abstractmethod
from app.services.threat_intel.models import ProviderResponse

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
