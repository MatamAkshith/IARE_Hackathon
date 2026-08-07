"""
Risk Assessment REST API Endpoints — Stage 6.4 & 6.6

Endpoints:
  POST /api/v1/risk/evaluate
    Accepts a payload with indicator + evidence, runs the full risk scoring pipeline,
    persists the result, and returns the complete RiskScore.

  GET /api/v1/risk/{indicator:path}
    Retrieves historical risk assessment records for a specific indicator,
    ordered by most recent timestamp first.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.risk_engine.service import RiskScoringService
from app.services.risk_engine.models import RiskScore

logger = logging.getLogger("app.api.v1.endpoints.risk")
router = APIRouter()

# Service singleton
_risk_service = RiskScoringService()


# ─────────────────────────────────────────────────────────────────────────── #
# Request / Response schemas                                                   #
# ─────────────────────────────────────────────────────────────────────────── #

class EvaluateRiskRequest(BaseModel):
    """
    Payload for POST /risk/evaluate.

    Accepts either a full UnifiedEvidence-shaped payload or a flat evidence dict.
    The indicator field is mandatory; all other fields are optional and fall
    through to the evidence dict used by the rule evaluators.
    """
    indicator: str
    indicator_type: Optional[str] = "url"
    resolved_observations: Optional[Dict[str, Any]] = None
    internal_evidence: Optional[Dict[str, Any]] = None
    external_evidence: Optional[Dict[str, Any]] = None
    overall_confidence: Optional[str] = "unknown"
    save_to_db: bool = True


class RiskAssessmentResponse(BaseModel):
    """Serialized view of a persisted RiskAssessmentRecord."""
    id: int
    indicator: str
    indicator_type: str
    overall_score: float
    severity: str
    breakdown: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    timestamp: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────── #
# Helper — persist RiskScore → RiskAssessmentRecord                           #
# ─────────────────────────────────────────────────────────────────────────── #

def _save_risk_score(
    db: Session,
    score: RiskScore,
    indicator_type: str,
) -> None:
    """
    Serializes and persists a RiskScore to the database.
    Wraps db operations in a try/except block to handle errors gracefully.
    """
    from app.db.models.risk_assessment import RiskAssessmentRecord

    try:
        breakdown_json = score.breakdown.model_dump()
        recommendations_json = [r.model_dump() for r in score.recommendations]

        record = RiskAssessmentRecord(
            indicator=score.indicator,
            indicator_type=indicator_type,
            overall_score=score.overall_score,
            severity=score.severity.value,
            breakdown=breakdown_json,
            recommendations=recommendations_json,
            explanation=score.explanation,
            unified_evidence_indicator=score.indicator,
            timestamp=score.timestamp,
        )
        db.add(record)
        db.commit()
        logger.info(f"Successfully saved RiskAssessmentRecord for indicator: '{score.indicator}'")
    except Exception as exc:
        db.rollback()
        logger.error(
            f"Failed to persist RiskAssessmentRecord to DB for indicator '{score.indicator}': {exc}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database persistence failed: {str(exc)}",
        )


# ─────────────────────────────────────────────────────────────────────────── #
# POST /evaluate                                                               #
# ─────────────────────────────────────────────────────────────────────────── #

@router.post(
    "/evaluate",
    response_model=RiskScore,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Risk for an Indicator",
    description=(
        "Accepts a structured evidence payload, runs the full explainable risk scoring "
        "pipeline (evaluation → normalization → severity mapping → recommendations), "
        "optionally persists the result, and returns the complete RiskScore."
    ),
)
def evaluate_risk(
    request: EvaluateRiskRequest,
    db: Session = Depends(get_db),
) -> Any:
    if not request.indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator cannot be empty.",
        )

    logger.info(f"POST /api/v1/risk/evaluate called for indicator: '{request.indicator}'")

    try:
        # Build a flat evidence dict from the request fields
        evidence: Dict[str, Any] = {"indicator": request.indicator}
        if request.overall_confidence:
            evidence["overall_confidence"] = request.overall_confidence

        # Merge resolved_observations first
        if request.resolved_observations:
            evidence.update(request.resolved_observations)

        # Layer in internal evidence (non-destructive)
        if request.internal_evidence:
            for k, v in request.internal_evidence.items():
                evidence.setdefault(k, v)

        # Layer in external evidence (non-destructive — resolved_observations wins)
        if request.external_evidence:
            for k, v in request.external_evidence.items():
                evidence.setdefault(k, v)

        score = _risk_service.calculate_risk(evidence)

        if request.save_to_db:
            _save_risk_score(
                db=db,
                score=score,
                indicator_type=request.indicator_type or "url",
            )
            
            # Dynamic Campaign Correlation Step
            try:
                from app.models.domain import Domain
                from app.models.scan import Scan
                from app.services.campaign_service import attribute_scan_to_campaign

                domain = db.query(Domain).filter(Domain.url == request.indicator).first()
                if domain:
                    scan = db.query(Scan).filter(Scan.domain_id == domain.id).order_by(Scan.id.desc()).first()
                    if scan:
                        attribute_scan_to_campaign(
                            db=db,
                            scan_id=scan.id,
                            telemetry_data=evidence,
                            overall_score=score.overall_score
                        )
            except Exception as correlation_exc:
                logger.warning(
                    f"Failed to dynamically correlate scan to campaign for '{request.indicator}': {correlation_exc}",
                    exc_info=True
                )

        logger.info(f"POST /api/v1/risk/evaluate completed successfully for indicator: '{request.indicator}'")
        return score

    except HTTPException:
        # Re-raise HTTPExceptions raised from DB helper directly
        raise
    except Exception as exc:
        logger.error(f"Error during risk evaluation for indicator '{request.indicator}': {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk evaluation error: {str(exc)}",
        )


# ─────────────────────────────────────────────────────────────────────────── #
# GET /{indicator} — history retrieval (catch-all, must be last)              #
# ─────────────────────────────────────────────────────────────────────────── #

@router.get(
    "/{indicator:path}",
    response_model=List[RiskAssessmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve Risk Assessment History",
    description=(
        "Retrieves all persisted risk assessment records for a given indicator "
        "(URL, domain, or IP), ordered by most recent timestamp first."
    ),
)
def get_risk_history(
    indicator: str = Path(..., description="The indicator to retrieve risk history for"),
    db: Session = Depends(get_db),
) -> Any:
    if not indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator path parameter cannot be empty.",
        )

    logger.info(f"GET /api/v1/risk history called for indicator: '{indicator}'")

    try:
        from app.db.models.risk_assessment import RiskAssessmentRecord

        records = (
            db.query(RiskAssessmentRecord)
            .filter(RiskAssessmentRecord.indicator == indicator)
            .order_by(RiskAssessmentRecord.timestamp.desc())
            .all()
        )

        if not records:
            logger.info(f"No risk history records found in DB for indicator: '{indicator}'")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No risk assessments found for indicator: '{indicator}'",
            )

        logger.info(f"Successfully retrieved {len(records)} risk history record(s) for indicator: '{indicator}'")
        return [
            RiskAssessmentResponse(
                id=r.id,
                indicator=r.indicator,
                indicator_type=r.indicator_type,
                overall_score=r.overall_score,
                severity=r.severity,
                breakdown=r.breakdown,
                recommendations=r.recommendations,
                explanation=r.explanation,
                timestamp=r.timestamp.isoformat() if r.timestamp else "",
            )
            for r in records
        ]

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving risk history for indicator '{indicator}': {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk history retrieval error: {str(exc)}",
        )
