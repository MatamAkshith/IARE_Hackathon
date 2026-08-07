from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch
from app.core.config import settings

class URLHausProvider(BaseThreatIntelProvider):
    def __init__(self) -> None:
        self._api_key = settings.URLHAUS_API_KEY
        self._enabled = True

    @property
    def provider_name(self) -> str:
        return "URLHaus"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def lookup_url(self, url: str) -> ProviderResponse:
        async def _run():
            if not self._api_key or not self._api_key.strip():
                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error="Bypassed URLHaus lookup: API key is missing or not configured",
                    status="unavailable",
                    response_time_ms=0
                )

            payload = {
                "url": url
            }
            api_url = "https://urlhaus-api.abuse.ch/v1/url/"
            headers = {
                "Auth-Key": self._api_key,
                "Accept": "application/json"
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(api_url, data=payload, headers=headers)

                if response.status_code == 200:
                    raw_data = response.json()
                    query_status = raw_data.get("query_status")

                    if query_status == "ok":
                        verdict = ThreatVerdict.MALICIOUS
                        threat = raw_data.get("threat") or "malware_distribution"
                        tags = raw_data.get("tags") or []
                        matches = [
                            ThreatMatch(
                                matched_name="URLHaus",
                                category=threat,
                                confidence=1.0,
                                raw_tags=tags
                            )
                        ]
                        status_str = "success"
                    elif query_status == "no_results":
                        verdict = ThreatVerdict.CLEAN
                        matches = []
                        status_str = "no_result"
                    else:
                        verdict = ThreatVerdict.UNKNOWN
                        matches = []
                        status_str = "no_result"

                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=verdict,
                        matches=matches,
                        raw_response=raw_data,
                        status=status_str,
                        response_time_ms=0
                    )
                else:
                    status_str = "rate_limited" if response.status_code == 429 else "unavailable"
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=f"URLHaus API returned HTTP {response.status_code}",
                        status=status_str,
                        response_time_ms=0
                    )

        return await self._safe_lookup(url, "url", _run())

    async def lookup_domain(self, domain: str) -> ProviderResponse:
        return self._unsupported_indicator("domain")

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        return self._unsupported_indicator("ip")
