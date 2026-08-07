from typing import Any, List, Dict
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.dashboard_service import DashboardService

logger = logging.getLogger("app.api.v1.endpoints.dashboard")
router = APIRouter()
dashboard_service = DashboardService()


@router.get("/stats", response_model=Dict[str, Any])
def get_dashboard_stats(db: Session = Depends(get_db)) -> Any:
    """
    Retrieves live SQL aggregation statistics for the SOC Dashboard KPIs and Risk Distribution.
    """
    logger.info("[get_dashboard_stats] Fetching live dashboard stats")
    try:
        stats = dashboard_service.get_stats(db)
        return stats
    except Exception as exc:
        logger.error(f"[get_dashboard_stats] Failed to fetch stats: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics."
        )


@router.get("/recent-feed", response_model=List[Dict[str, Any]])
def get_recent_feed(
    db: Session = Depends(get_db),
    limit: int = 10
) -> Any:
    """
    Retrieves the recent threat monitoring feed with targets, scores, status, and campaign attribution.
    """
    logger.info(f"[get_recent_feed] Fetching recent feed with limit={limit}")
    try:
        feed = dashboard_service.get_recent_feed(db, limit=limit)
        return feed
    except Exception as exc:
        logger.error(f"[get_recent_feed] Failed to fetch feed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent scans feed."
        )
