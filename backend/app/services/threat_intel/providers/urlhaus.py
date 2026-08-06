import time
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.services.threat_intel.base import BaseThreatIntelProvider
from app.services.threat_intel.models import ProviderResponse, ThreatVerdict, ThreatMatch

logger = logging.getLogger("app.services.threat_intel.providers.urlhaus")

class URLHausProvider(BaseThreatIntelProvider):
    def __init__(self) -> None:
        self._enabled = True

    @property
    def provider_name(self) -> str:
        return "URLHaus"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def lookup_url(self, url: str) -> ProviderResponse:
        start_time = time.time()
        
        payload = {
            "url": url
        }
        api_url = "https://urlhaus-api.abuse.ch/v1/url/"

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                # URLHaus expects application/x-www-form-urlencoded
                response = await client.post(api_url, data=payload)
                response_time_ms = int((time.time() - start_time) * 1000)

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
                    elif query_status == "no_results":
                        verdict = ThreatVerdict.CLEAN
                        matches = []
                    else:
                        verdict = ThreatVerdict.UNKNOWN
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
                        error=f"URLHaus API returned HTTP {response.status_code}",
                        response_time_ms=response_time_ms
                    )
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                logger.warning(f"URLHaus URL lookup exception: {e}")
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
        URLHaus URL endpoint does not directly support clean Domain reputation queries in this structure.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error="Domain lookup is unsupported by URLHaus in this stage",
            response_time_ms=0
        )

    async def lookup_ip(self, ip: str) -> ProviderResponse:
        """
        URLHaus URL endpoint does not directly support clean IP reputation queries.
        """
        return ProviderResponse(
            provider_name=self.provider_name,
            verdict=ThreatVerdict.UNKNOWN,
            matches=[],
            raw_response={},
            error="IP lookup is unsupported by URLHaus in this stage",
            response_time_ms=0
        )
