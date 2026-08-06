from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.services.threat_intel.service import ThreatIntelService
from app.services.threat_intel.models import AggregatedThreatEvidence
from pydantic import BaseModel

router = APIRouter()

class ThreatLookupRequest(BaseModel):
    indicator: str
    indicator_type: Optional[str] = None

# Global service instance
threat_intel_service = ThreatIntelService()

@router.post("/lookup", response_model=AggregatedThreatEvidence, status_code=status.HTTP_200_OK)
async def lookup_indicator_post(
    request: ThreatLookupRequest
) -> Any:
    """
    Perform a concurrent reputation lookup for the given indicator (URL, Domain, or IP)
    and synthesize an overall threat verdict.
    """
    if not request.indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator cannot be empty"
        )
    try:
        result = await threat_intel_service.aggregate_lookup(
            indicator=request.indicator,
            indicator_type=request.indicator_type
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat intelligence aggregation error: {str(e)}"
        )

@router.get("/lookup", response_model=AggregatedThreatEvidence, status_code=status.HTTP_200_OK)
async def lookup_indicator_get(
    indicator: str = Query(..., description="The URL, Domain, or IP address to lookup"),
    indicator_type: Optional[str] = Query(None, description="Optional type override: 'url', 'domain', 'ip'")
) -> Any:
    """
    Perform a concurrent reputation lookup for the given indicator (URL, Domain, or IP)
    and synthesize an overall threat verdict.
    """
    if not indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator query parameter cannot be empty"
        )
    try:
        result = await threat_intel_service.aggregate_lookup(
            indicator=indicator,
            indicator_type=indicator_type
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat intelligence aggregation error: {str(e)}"
        )

@router.post("/lookup/url", response_model=AggregatedThreatEvidence, status_code=status.HTTP_200_OK)
async def lookup_url(
    request: ThreatLookupRequest
) -> Any:
    """
    Specific helper endpoint to perform lookups for URLs.
    """
    if not request.indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator cannot be empty"
        )
    try:
        result = await threat_intel_service.aggregate_lookup(
            indicator=request.indicator,
            indicator_type="url"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat intelligence URL aggregation error: {str(e)}"
        )

@router.post("/lookup/domain", response_model=AggregatedThreatEvidence, status_code=status.HTTP_200_OK)
async def lookup_domain(
    request: ThreatLookupRequest
) -> Any:
    """
    Specific helper endpoint to perform lookups for Domains.
    """
    if not request.indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator cannot be empty"
        )
    try:
        result = await threat_intel_service.aggregate_lookup(
            indicator=request.indicator,
            indicator_type="domain"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat intelligence Domain aggregation error: {str(e)}"
        )

@router.post("/lookup/ip", response_model=AggregatedThreatEvidence, status_code=status.HTTP_200_OK)
async def lookup_ip(
    request: ThreatLookupRequest
) -> Any:
    """
    Specific helper endpoint to perform lookups for IP addresses.
    """
    if not request.indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator cannot be empty"
        )
    try:
        result = await threat_intel_service.aggregate_lookup(
            indicator=request.indicator,
            indicator_type="ip"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat intelligence IP aggregation error: {str(e)}"
        )
