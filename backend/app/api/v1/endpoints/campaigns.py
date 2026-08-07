"""
Campaign Correlation REST APIs — Stage 7.5

Exposes API endpoints to trigger evidence correlation clustering and retrieve
campaign details, relationship graphs, and event timelines.
"""

from typing import Any, Dict, List
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user, log_activity
from app.services.campaign_engine.service import CampaignCorrelationService
from app.services.campaign_engine.repository import CampaignRepository
from app.services.campaign_engine.schemas import CampaignResponse
from app.services.campaign_engine.graph_models import CampaignGraph, CampaignTimeline
from app.core.security import RoleChecker
from app.db.models.employee import EmployeeRecord

logger = logging.getLogger("app.api.v1.endpoints.campaigns")

router = APIRouter()
campaign_service = CampaignCorrelationService()
campaign_repo = CampaignRepository()

# Define checkers
allowed_write_roles = RoleChecker(["admin", "soc_lead", "threat_intel", "security_manager"])


class CorrelateResponse(BaseModel):
    """API payload response for correlation clustering action."""
    campaign: CampaignResponse = Field(description="The Campaign cluster result.")
    action: str = Field(description="Action executed: 'created' | 'joined' | 'merged'.")


@router.post("/correlate", response_model=CorrelateResponse, status_code=status.HTTP_200_OK)
def correlate_indicator(
    *,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(allowed_write_roles),
    evidence: Dict[str, Any] = Body(
        ...,
        example={
            "indicator": "https://secure-update-login.com",
            "indicator_type": "url",
            "ip_address": "192.168.1.100",
            "cert_serial": "03A1B2C3D4E5F67890",
            "page_title": "Secure Customer Portal Verification"
        }
    )
) -> Any:
    """
    Submits an indicator's resolved evidence observations to evaluate link correlation
    against active campaigns. Merges overlapping campaigns, creates new ones, or joins existing ones.
    """
    logger.info(
        f"[correlate_indicator] Correlation request received for indicator: "
        f"'{evidence.get('indicator', 'unknown')}'"
    )
    
    if not evidence.get("indicator"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Indicator field is required within resolved evidence observations."
        )

    try:
        # Runs the service which queries active, evaluates matching, merges or joins, and persists to DB.
        campaign, action = campaign_service.process_investigation(new_evidence=evidence, db=db)
        return CorrelateResponse(campaign=campaign, action=action)
    except Exception as exc:
        logger.error(f"[correlate_indicator] Core clustering processing failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while clustering this indicator: {str(exc)}"
        )


@router.get("", response_model=List[CampaignResponse])
def list_campaigns(
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
) -> Any:
    """
    Retrieves all campaigns, paginated, sorted by latest updates first.
    """
    logger.info(f"[list_campaigns] Listing campaigns with skip={skip}, limit={limit}")
    log_activity(db, current_user.user_id, "campaign_view", req_obj)
    try:
        campaigns = campaign_repo.list_campaigns(db, skip=skip, limit=limit)
        return campaigns
    except Exception as exc:
        logger.error(f"[list_campaigns] Database query failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve campaigns list."
        )


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: str,
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    """
    Retrieves a specific campaign configuration by its unique Campaign ID (e.g. CAMP-YYYYMMDD-XXXX).
    """
    logger.info(f"[get_campaign] Fetching campaign_id='{campaign_id}'")
    log_activity(db, current_user.user_id, "campaign_view", req_obj, campaign_id)
    campaign = campaign_repo.get_campaign_by_id(campaign_id=campaign_id, db=db)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID '{campaign_id}' not found."
        )
    return campaign


@router.get("/{campaign_id}/timeline", response_model=CampaignTimeline)
def get_campaign_timeline(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    """
    Constructs and returns the chronological timeline history of events for a specific campaign.
    """
    logger.info(f"[get_campaign_timeline] Building timeline for campaign_id='{campaign_id}'")
    campaign = campaign_repo.get_campaign_by_id(campaign_id=campaign_id, db=db)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID '{campaign_id}' not found."
        )
    try:
        timeline = campaign_service.get_campaign_timeline(campaign)
        return timeline
    except Exception as exc:
        logger.error(f"[get_campaign_timeline] Failed to build timeline: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate campaign timeline."
        )


@router.get("/{campaign_id}/graph", response_model=CampaignGraph)
def get_campaign_graph(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    """
    Constructs and returns the node-link relationship graph topology representing the campaign footprint.
    """
    logger.info(f"[get_campaign_graph] Building relationship graph for campaign_id='{campaign_id}'")
    campaign = campaign_repo.get_campaign_by_id(campaign_id=campaign_id, db=db)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with ID '{campaign_id}' not found."
        )
    try:
        graph = campaign_service.get_campaign_graph(campaign)
        return graph
    except Exception as exc:
        logger.error(f"[get_campaign_graph] Failed to build graph: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate campaign relationship graph."
        )
