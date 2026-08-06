import time
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

logger = logging.getLogger("app.services.threat_intel.providers.alienvault")

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

    def _normalize_response(self, raw_data: Dict[str, Any], response_time_ms: int) -> ProviderResponse:
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
            response_time_ms=response_time_ms
        )

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        return await self._query_indicator("IPv4", ip)

    async def lookup_domain(self, domain: str) -> ProviderResponse:
        return await self._query_indicator("domain", domain)

    async def lookup_url(self, url: str) -> ProviderResponse:
        return await self._query_indicator("url", url)

    async def _query_indicator(self, type_str: str, indicator: str) -> ProviderResponse:
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

        api_url = f"https://otx.alienvault.com/api/v1/indicators/{type_str}/{indicator}/general"

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(api_url, headers=self._get_headers())
                response_time_ms = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    raw_data = response.json()
                    return self._normalize_response(raw_data, response_time_ms)
                else:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=f"AlienVault OTX API returned HTTP {response.status_code}",
                        response_time_ms=response_time_ms
                    )
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.warning(f"AlienVault OTX {type_str} lookup exception: {e}")
                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=f"Connection/Timeout exception: {str(e)}",
                    response_time_ms=response_time_ms
                )
