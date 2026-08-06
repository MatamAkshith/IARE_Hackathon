import time
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

logger = logging.getLogger("app.services.threat_intel.providers.abuseipdb")

class AbuseIPDBProvider(BaseThreatIntelProvider):
    def __init__(self, api_key: Optional[str]) -> None:
        self._api_key = api_key
        self._enabled = bool(api_key and api_key.strip())

    @property
    def provider_name(self) -> str:
        return "AbuseIPDB"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        start_time = time.time()
        
        if not self.is_enabled:
            return ProviderResponse(
                provider_name=self.provider_name,
                verdict=ThreatVerdict.UNKNOWN,
                matches=[],
                raw_response={},
                error="Provider is disabled or API key is missing",
                response_time_ms=0
            )

        api_url = "https://api.abuseipdb.com/api/v2/check"
        params = {"ipAddress": ip}
        headers = {
            "Key": self._api_key or "",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(api_url, headers=headers, params=params)
                response_time_ms = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    raw_data = response.json()
                    data = raw_data.get("data", {})
                    score = data.get("abuseConfidenceScore", 0)

                    if score > 50:
                        verdict = ThreatVerdict.MALICIOUS
                    elif score > 0:
                        verdict = ThreatVerdict.SUSPICIOUS
                    else:
                        verdict = ThreatVerdict.CLEAN

                    matches = []
                    if score > 0:
                        matches.append(
                            ThreatMatch(
                                matched_name="AbuseIPDB",
                                category="abuse_ip",
                                confidence=float(score) / 100.0,
                                raw_tags=[f"confidence_score_{score}"]
                            )
                        )

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
                        error=f"AbuseIPDB API returned HTTP {response.status_code}",
                        response_time_ms=response_time_ms
                    )
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.warning(f"AbuseIPDB IP lookup exception: {e}")
                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=f"Connection/Timeout exception: {str(e)}",
                    response_time_ms=response_time_ms
                )

    async def lookup_url(self, url: str) -> ProviderResponse:
        """
        AbuseIPDB only supports IP reputation queries.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error="URL reputation lookup is unsupported by AbuseIPDB",
            response_time_ms=0
        )

    async def lookup_domain(self, domain: str) -> ProviderResponse:
        """
        AbuseIPDB only supports IP reputation queries.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error="Domain reputation lookup is unsupported by AbuseIPDB",
            response_time_ms=0
        )
