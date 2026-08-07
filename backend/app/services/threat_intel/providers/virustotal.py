import base64
from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

class VirusTotalProvider(BaseThreatIntelProvider):
    def __init__(self, api_key: Optional[str]) -> None:
        self._api_key = api_key
        self._enabled = bool(api_key and api_key.strip())

    @property
    def provider_name(self) -> str:
        return "VirusTotal"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-apikey": self._api_key or "",
            "Accept": "application/json"
        }

    def _map_stats_to_verdict(self, stats: Dict[str, int]) -> ThreatVerdict:
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        harmless = stats.get("harmless", 0)
        undetected = stats.get("undetected", 0)

        if malicious > 0:
            return ThreatVerdict.MALICIOUS
        if suspicious > 0:
            return ThreatVerdict.SUSPICIOUS
        if harmless > 0 or undetected > 0:
            return ThreatVerdict.CLEAN
        
        return ThreatVerdict.UNKNOWN

    def _extract_matches(self, attributes: Dict[str, Any]) -> List[ThreatMatch]:
        matches = []
        results = attributes.get("last_analysis_results", {})
        for engine, res_val in results.items():
            category = res_val.get("category")
            if category in ["malicious", "suspicious"]:
                result = res_val.get("result") or "detected"
                matches.append(
                    ThreatMatch(
                        matched_name=engine,
                        category=category,
                        confidence=1.0,
                        raw_tags=[result]
                    )
                )
        return matches

    async def lookup_url(self, url: str) -> ProviderResponse:
        async def _run():
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(api_url, headers=self._get_headers())
                
                if response.status_code == 200:
                    raw_data = response.json()
                    attributes = raw_data.get("data", {}).get("attributes", {})
                    stats = attributes.get("last_analysis_stats", {})
                    verdict = self._map_stats_to_verdict(stats)
                    matches = self._extract_matches(attributes)
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=verdict,
                        matches=matches,
                        raw_response=raw_data,
                        status="success",
                        response_time_ms=0
                    )
                elif response.status_code == 401:
                    error_msg = "Invalid API key (401)"
                    status_code = "unavailable"
                elif response.status_code == 404:
                    error_msg = "Resource not found (404)"
                    status_code = "no_result"
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded (429)"
                    status_code = "rate_limited"
                else:
                    error_msg = f"VirusTotal API returned HTTP {response.status_code}"
                    status_code = "unavailable"

                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=error_msg,
                    status=status_code,
                    response_time_ms=0
                )

        return await self._safe_lookup(url, "url", _run())

    async def lookup_domain(self, domain: str) -> ProviderResponse:
        async def _run():
            api_url = f"https://www.virustotal.com/api/v3/domains/{domain}"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(api_url, headers=self._get_headers())
                
                if response.status_code == 200:
                    raw_data = response.json()
                    attributes = raw_data.get("data", {}).get("attributes", {})
                    stats = attributes.get("last_analysis_stats", {})
                    verdict = self._map_stats_to_verdict(stats)
                    matches = self._extract_matches(attributes)
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=verdict,
                        matches=matches,
                        raw_response=raw_data,
                        status="success",
                        response_time_ms=0
                    )
                elif response.status_code == 401:
                    error_msg = "Invalid API key (401)"
                    status_code = "unavailable"
                elif response.status_code == 404:
                    error_msg = "Resource not found (404)"
                    status_code = "no_result"
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded (429)"
                    status_code = "rate_limited"
                else:
                    error_msg = f"VirusTotal API returned HTTP {response.status_code}"
                    status_code = "unavailable"

                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=error_msg,
                    status=status_code,
                    response_time_ms=0
                )

        return await self._safe_lookup(domain, "domain", _run())

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        return self._unsupported_indicator("ip")
