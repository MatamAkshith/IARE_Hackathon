from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.unified_evidence.service import UnifiedEvidenceService
from app.services.unified_evidence.models import UnifiedEvidence, AuditTrail, EvidenceEvent

router = APIRouter()

# Service singleton
_unified_evidence_service = UnifiedEvidenceService()


class ProcessEvidenceRequest(BaseModel):
    indicator: str
    internal_data: Dict[str, Any] = {}
    external_data: Dict[str, Any] = {}
    save_to_db: bool = True


class EvidenceRecordResponse(BaseModel):
    id: int
    indicator: str
    indicator_type: str
    overall_confidence: str
    resolved_observations: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    timestamp: str

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
# POST /process                                                                #
# --------------------------------------------------------------------------- #
@router.post(
    "/process",
    response_model=UnifiedEvidence,
    status_code=status.HTTP_200_OK,
    summary="Process & Merge Evidence",
    description=(
        "Accepts raw internal feature extraction data and external threat intelligence data for an indicator. "
        "Merges, normalizes, scores confidence, builds audit trail, and optionally saves the result to the database."
    )
)
def process_evidence(
    request: ProcessEvidenceRequest,
    db: Session = Depends(get_db)
) -> Any:
    if not request.indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator cannot be empty."
        )
    try:
        evidence = _unified_evidence_service.process_evidence(
            indicator=request.indicator,
            internal_data=request.internal_data,
            external_data=request.external_data,
        )
        if request.save_to_db:
            _unified_evidence_service.save_evidence(db=db, evidence=evidence)

        return evidence
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence processing error: {str(e)}"
        )


# --------------------------------------------------------------------------- #
# GET /{indicator}/timeline                                                    #
# NOTE: This specific sub-path route MUST be declared before the catch-all    #
# /{indicator:path} route below, otherwise FastAPI will consume it first.     #
# We use a query-param approach to avoid path routing conflicts.               #
# --------------------------------------------------------------------------- #
@router.get(
    "/timeline",
    response_model=AuditTrail,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Evidence Timeline",
    description=(
        "Retrieves the stored audit trail (chronological list of evidence collection, "
        "conflict resolution, normalization, and scoring events) for the most recent "
        "evidence record of a given indicator. Pass the indicator as a query parameter."
    )
)
def get_evidence_timeline(
    indicator: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    GET /api/v1/unified-evidence/timeline?indicator=<url_or_domain_or_ip>

    Returns the AuditTrail from the most recent persisted evidence record for
    the given indicator. The audit trail is stored inside metadata_json.
    """
    if not indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator query parameter cannot be empty."
        )
    try:
        records = _unified_evidence_service.get_evidence_by_indicator(db=db, indicator=indicator)
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No evidence records found for indicator: '{indicator}'"
            )

        # Most recent record is first (ordered by timestamp DESC in service)
        latest = records[0]
        metadata = latest.metadata_json or {}
        audit_trail_raw = metadata.get("audit_trail")

        if not audit_trail_raw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"No audit trail found in the latest evidence record for indicator: '{indicator}'. "
                    "This record may have been created before Stage 5.5 was deployed."
                )
            )

        # Reconstruct Pydantic AuditTrail from stored JSON
        audit_trail = AuditTrail(
            investigation_start=audit_trail_raw["investigation_start"],
            events=[
                EvidenceEvent(
                    timestamp=e["timestamp"],
                    source=e["source"],
                    event_type=e["event_type"],
                    description=e["description"],
                    key_affected=e.get("key_affected"),
                )
                for e in audit_trail_raw.get("events", [])
            ]
        )

        return audit_trail

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Timeline retrieval error: {str(e)}"
        )


# --------------------------------------------------------------------------- #
# GET /{indicator} — catch-all (must remain LAST)                              #
# --------------------------------------------------------------------------- #
@router.get(
    "/{indicator:path}",
    response_model=List[EvidenceRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve Historical Evidence",
    description=(
        "Retrieves all persisted unified evidence records for a given indicator (URL, domain, or IP), "
        "ordered by most recent timestamp first."
    )
)
def get_evidence_history(
    indicator: str = Path(..., description="The indicator to retrieve evidence history for (URL, domain, or IP)"),
    db: Session = Depends(get_db)
) -> Any:
    if not indicator.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indicator path parameter cannot be empty."
        )
    try:
        records = _unified_evidence_service.get_evidence_by_indicator(db=db, indicator=indicator)
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No evidence records found for indicator: '{indicator}'"
            )
        return [
            EvidenceRecordResponse(
                id=r.id,
                indicator=r.indicator,
                indicator_type=r.indicator_type,
                overall_confidence=r.overall_confidence,
                resolved_observations=r.resolved_observations,
                sources=r.sources,
                metadata_json=r.metadata_json,
                timestamp=r.timestamp.isoformat() if r.timestamp else ""
            )
            for r in records
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence retrieval error: {str(e)}"
        )
