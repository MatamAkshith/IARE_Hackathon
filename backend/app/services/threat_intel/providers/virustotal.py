import base64
import time
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

logger = logging.getLogger("app.services.threat_intel.providers.virustotal")

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
        """
        Map VT last_analysis_stats to ThreatVerdict.
        """
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
        """
        Extract engine detections as ThreatMatch entries.
        """
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

        # Base64 encode the URL (URL-safe, no padding)
        try:
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        except Exception as e:
            return ProviderResponse(
                provider_name=self.provider_name,
                verdict=ThreatVerdict.UNKNOWN,
                matches=[],
                raw_response={},
                error=f"Base64 encoding URL failed: {str(e)}",
                response_time_ms=int((time.time() - start_time) * 1000)
            )

        api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(api_url, headers=self._get_headers())
                response_time_ms = int((time.time() - start_time) * 1000)

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
                        response_time_ms=response_time_ms
                    )
                elif response.status_code == 401:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error="Invalid API key (401)",
                        response_time_ms=response_time_ms
                    )
                elif response.status_code == 404:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error="Resource not found (404)",
                        response_time_ms=response_time_ms
                    )
                elif response.status_code == 429:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error="Rate limit exceeded (429)",
                        response_time_ms=response_time_ms
                    )
                else:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=f"VirusTotal API returned HTTP {response.status_code}",
                        response_time_ms=response_time_ms
                    )
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.warning(f"VirusTotal URL lookup exception: {e}")
                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=f"Connection/Timeout exception: {str(e)}",
                    response_time_ms=response_time_ms
                )

    async def lookup_domain(self, domain: str) -> ProviderResponse:
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

        api_url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(api_url, headers=self._get_headers())
                response_time_ms = int((time.time() - start_time) * 1000)

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
                        response_time_ms=response_time_ms
                    )
                elif response.status_code == 401:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error="Invalid API key (401)",
                        response_time_ms=response_time_ms
                    )
                elif response.status_code == 404:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error="Resource not found (404)",
                        response_time_ms=response_time_ms
                    )
                elif response.status_code == 429:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error="Rate limit exceeded (429)",
                        response_time_ms=response_time_ms
                    )
                else:
                    return ProviderResponse(
                        provider_name=self.provider_name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=f"VirusTotal API returned HTTP {response.status_code}",
                        response_time_ms=response_time_ms
                    )
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.warning(f"VirusTotal Domain lookup exception: {e}")
                return ProviderResponse(
                    provider_name=self.provider_name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=f"Connection/Timeout exception: {str(e)}",
                    response_time_ms=response_time_ms
                )

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        """
        IP lookup is currently unsupported in this stage.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error="IP reputation lookups are unsupported in this stage.",
            response_time_ms=0
        )
