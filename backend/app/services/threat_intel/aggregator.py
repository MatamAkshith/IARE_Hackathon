import asyncio
import logging
import ipaddress
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.services.threat_intel.models import ThreatVerdict, ProviderResponse, AggregatedThreatEvidence

logger = logging.getLogger("app.services.threat_intel.aggregator")

def detect_indicator_type(indicator: str) -> str:
    indicator = indicator.strip()
    
    # 1. Test for IP address
    try:
        ipaddress.ip_address(indicator)
        return "ip"
    except ValueError:
        pass
        
    # 2. Test for URL (starts with protocol or has path/query indicator characters)
    if re.match(r'^https?://', indicator, re.IGNORECASE) or "/" in indicator or "?" in indicator:
        return "url"
        
    # 3. Default to domain
    return "domain"

class ThreatIntelAggregator:
    def __init__(self, service) -> None:
        self.service = service

    async def aggregate_lookup(
        self, indicator: str, indicator_type: Optional[str] = None, timeout: float = 5.0
    ) -> AggregatedThreatEvidence:
        start_time = time.time()
        
        if not indicator_type:
            indicator_type = detect_indicator_type(indicator)

        # Get all registered and enabled providers
        providers = self.service.get_enabled_providers()
        
        if not providers:
            return AggregatedThreatEvidence(
                indicator=indicator,
                indicator_type=indicator_type,
                overall_verdict=ThreatVerdict.UNKNOWN,
                total_providers=0,
                successful_providers=0,
                failed_providers=0,
                malicious_count=0,
                suspicious_count=0,
                clean_count=0,
                provider_responses={},
                timestamp=datetime.now(timezone.utc)
            )

        tasks = []
        provider_names = []

        for provider in providers:
            provider_names.append(provider.provider_name)
            
            # Select target method
            if indicator_type == "url":
                coro = provider.lookup_url(indicator)
            elif indicator_type == "domain":
                coro = provider.lookup_domain(indicator)
            else:
                coro = provider.lookup_ip(indicator)

            # Wrap coroutine with timeout
            async def wrapped_lookup(name=provider.provider_name, c=coro):
                try:
                    return await asyncio.wait_for(c, timeout=timeout)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout of {timeout}s exceeded for provider: {name}")
                    return ProviderResponse(
                        provider_name=name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error="Request timed out",
                        status="unavailable",
                        response_time_ms=int(timeout * 1000)
                    )
                except Exception as ex:
                    logger.error(f"Error during lookup for provider {name}: {ex}")
                    return ProviderResponse(
                        provider_name=name,
                        verdict=ThreatVerdict.UNKNOWN,
                        matches=[],
                        raw_response={},
                        error=str(ex),
                        status="unavailable",
                        response_time_ms=0
                    )

            tasks.append(wrapped_lookup())

        # Execute concurrent lookups
        results = await asyncio.gather(*tasks, return_exceptions=True)

        provider_responses = {}
        successful = 0
        failed = 0
        malicious = 0
        suspicious = 0
        clean = 0

        for name, result in zip(provider_names, results):
            if isinstance(result, Exception):
                failed += 1
                response_obj = ProviderResponse(
                    provider_name=name,
                    verdict=ThreatVerdict.UNKNOWN,
                    matches=[],
                    raw_response={},
                    error=f"Internal aggregation exception: {str(result)}",
                    status="unavailable",
                    response_time_ms=0
                )
            else:
                response_obj = result
                # Check for verdict and status
                if response_obj.verdict == ThreatVerdict.UNKNOWN or response_obj.error:
                    failed += 1
                else:
                    successful += 1

                if response_obj.verdict == ThreatVerdict.MALICIOUS:
                    malicious += 1
                elif response_obj.verdict == ThreatVerdict.SUSPICIOUS:
                    suspicious += 1
                elif response_obj.verdict == ThreatVerdict.CLEAN:
                    clean += 1

            provider_responses[name] = response_obj

        # Consensus rules:
        # MALICIOUS if any provider returns MALICIOUS
        # SUSPICIOUS if any returns SUSPICIOUS and none MALICIOUS
        # CLEAN if all successful providers return CLEAN
        # UNKNOWN if all fail
        if malicious > 0:
            overall_verdict = ThreatVerdict.MALICIOUS
        elif suspicious > 0:
            overall_verdict = ThreatVerdict.SUSPICIOUS
        elif clean > 0:
            overall_verdict = ThreatVerdict.CLEAN
        else:
            overall_verdict = ThreatVerdict.UNKNOWN

        return AggregatedThreatEvidence(
            indicator=indicator,
            indicator_type=indicator_type,
            overall_verdict=overall_verdict,
            total_providers=len(provider_names),
            successful_providers=successful,
            failed_providers=failed,
            malicious_count=malicious,
            suspicious_count=suspicious,
            clean_count=clean,
            provider_responses=provider_responses,
            timestamp=datetime.now(timezone.utc)
        )
