import time
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

logger = logging.getLogger("app.services.threat_intel.providers.phishtank")

class PhishTankProvider(BaseThreatIntelProvider):
    def __init__(self, api_key: Optional[str]) -> None:
        self._api_key = api_key
        # PhishTank can run without a key
        self._enabled = True

    @property
    def provider_name(self) -> str:
        return "PhishTank"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def lookup_url(self, url: str) -> ProviderResponse:
        start_time = time.time()
        
        payload: Dict[str, Any] = {
            "url": url,
            "format": "json"
        }
        if self._api_key and self._api_key.strip():
            payload["app_key"] = self._api_key

        api_url = "https://checkurl.phishtank.com/checkurl/"
        headers = {
            "User-Agent": "phishtank/threatlens",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                # PhishTank checkurl API expects application/x-www-form-urlencoded (data=payload)
                response = await client.post(api_url, data=payload, headers=headers)


                response_time_ms = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    raw_data = response.json()
                    results = raw_data.get("results", {})
                    
                    in_database = results.get("in_database") is True
                    valid = results.get("valid") is True
                    
                    if in_database and valid:
                        verdict = ThreatVerdict.MALICIOUS
                        matches = [
                            ThreatMatch(
                                matched_name="PhishTank",
                                category="phishing",
                                confidence=1.0,
                                raw_tags=["in_database", "valid_phish"]
                            )
                        ]
                    else:
                        verdict = ThreatVerdict.CLEAN
                        matches = []

                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=verdict,
                        matches=matches,
                        raw_response=raw_data,
                        response_time_ms=response_time_ms
                    )
                else:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=f"PhishTank API returned HTTP {response.status_code}",
                        response_time_ms=response_time_ms
                    )
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.warning(f"PhishTank URL lookup exception: {e}")
                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=f"Connection/Timeout exception: {str(e)}",
                    response_time_ms=response_time_ms
                )

    async def lookup_domain(self, domain: str) -> ProviderResponse:
        """
        PhishTank only supports URL-level checks.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error="Domain lookup is unsupported by PhishTank",
            response_time_ms=0
        )

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        """
        PhishTank only supports URL-level checks.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error="IP lookup is unsupported by PhishTank",
            response_time_ms=0
        )
