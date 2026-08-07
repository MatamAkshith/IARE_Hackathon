from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

class AlienVaultProvider(BaseThreatIntelProvider):
    def __init__(self, api_key: Optional[str]) -> None:
        self._api_key = api_key
        self._enabled = bool(api_key and api_key.strip())

    @property
    def provider_name(self) -> str:
        return "AlienVault OTX"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-OTX-API-KEY": self._api_key or "",
            "Accept": "application/json"
        }

    def _normalize_response(self, raw_data: Dict[str, Any]) -> ProviderResponse:
        pulse_info = raw_data.get("pulse_info", {})
        count = pulse_info.get("count", 0)

        if count > 2:
            verdict = ThreatVerdict.MALICIOUS
        elif count > 0:
            verdict = ThreatVerdict.SUSPICIOUS
        else:
            verdict = ThreatVerdict.CLEAN

        matches = []
        pulses = pulse_info.get("pulses", [])
        for p in pulses:
            matches.append(
                ThreatMatch(
                    matched_name=p.get("name") or "AlienVault Pulse",
                    category="threat_intel",
                    confidence=1.0,
                    raw_tags=p.get("tags") or []
                )
            )

        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=verdict,
            matches=matches,
            raw_response=raw_data,
            response_time_ms=0
        )

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        return await self._query_indicator("IPv4", ip, "ip")

    async def lookup_domain(self, domain: str) -> ProviderResponse:
        return await self._query_indicator("domain", domain, "domain")

    async def lookup_url(self, url: str) -> ProviderResponse:
        return await self._query_indicator("url", url, "url")

    async def _query_indicator(self, type_str: str, indicator: str, indicator_type: str) -> ProviderResponse:
        async def _run():
            api_url = f"https://otx.alienvault.com/api/v1/indicators/{type_str}/{indicator}/general"

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(api_url, headers=self._get_headers())

                if response.status_code == 200:
                    raw_data = response.json()
                    res = self._normalize_response(raw_data)
                    res.status = "success"
                    return res
                else:
                    status_str = "rate_limited" if response.status_code == 429 else "unavailable"
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=f"AlienVault OTX API returned HTTP {response.status_code}",
                        status=status_str,
                        response_time_ms=0
                    )

        return await self._safe_lookup(indicator, indicator_type, _run())
