from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

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
        async def _run():
            api_url = "https://api.abuseipdb.com/api/v2/check"
            params = {"ipAddress": ip}
            headers = {
                "Key": self._api_key or "",
                "Accept": "application/json"
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(api_url, headers=headers, params=params)

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
                        response_time_ms=0
                    )
                else:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=f"AbuseIPDB API returned HTTP {response.status_code}",
                        response_time_ms=0
                    )

        return await self._safe_lookup(ip, "ip", _run())

    async def lookup_url(self, url: str) -> ProviderResponse:
        return self._unsupported_indicator("url")

    async def lookup_domain(self, domain: str) -> ProviderResponse:
        return self._unsupported_indicator("domain")
