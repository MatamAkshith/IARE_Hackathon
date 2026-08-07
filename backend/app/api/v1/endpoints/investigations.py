from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, scan_repo, get_current_user, log_activity
from app.db.models.employee import EmployeeRecord
from app.db.models.risk_assessment import RiskAssessmentRecord
from app.models.domain import Domain

logger = logging.getLogger("app.api.v1.endpoints.investigations")
router = APIRouter()


class InvestigationResponse(BaseModel):
    id: int
    indicator: str
    indicator_type: str
    status: str
    overall_score: float
    severity: str
    breakdown: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/{id}", response_model=InvestigationResponse)
def read_investigation(
    id: int,
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    """
    Retrieves the unified investigation status and deterministic risk assessment fields
    for a completed or running scan by its unique ID.
    """
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation scan record not found"
        )
        
    domain = db.query(Domain).filter(Domain.id == scan.domain_id).first()
    indicator = domain.url if domain else f"Scan #{id}"
    
    # Query latest risk assessment
    latest_risk = db.query(RiskAssessmentRecord).filter(
        RiskAssessmentRecord.indicator == indicator
    ).order_by(RiskAssessmentRecord.timestamp.desc()).first()
    
    log_activity(db, current_user.user_id, "scan_view", req_obj, indicator)

    return InvestigationResponse(
        id=scan.id,
        indicator=indicator,
        indicator_type=latest_risk.indicator_type if latest_risk else "url",
        status=scan.status,
        overall_score=latest_risk.overall_score if latest_risk else 0.0,
        severity=latest_risk.severity if latest_risk else "safe",
        breakdown=latest_risk.breakdown if latest_risk else {},
        recommendations=latest_risk.recommendations if latest_risk else [],
        explanation=latest_risk.explanation if latest_risk else "No evaluation completed yet.",
        timestamp=latest_risk.timestamp if latest_risk else scan.updated_at,
        created_at=scan.created_at,
        updated_at=scan.updated_at
    )
