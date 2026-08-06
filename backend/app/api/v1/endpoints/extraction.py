from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, feature_repo, scan_repo
from app.models.feature import Feature
from app.schemas.feature import FeatureCreate, FeatureResponse
from app.services.feature_aggregator import FeatureAggregationService

router = APIRouter()

class ExtractionSubmitRequest(BaseModel):
    url: str
    scan_id: int

@router.post("/", response_model=Any, status_code=status.HTTP_201_CREATED)
def submit_extraction(
    *,
    db: Session = Depends(get_db),
    payload: ExtractionSubmitRequest
) -> Any:
    """
    Submits a URL for unified intelligence extraction.
    Runs the Domain, Network, and Webpage extractors, saving results to the DB.
    """
    # Verify target scan_id exists in the database first
    scan = scan_repo.get(db, id=payload.scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID {payload.scan_id} not found."
        )

    service = FeatureAggregationService()
    try:
        extracted_data = service.aggregate_features(payload.url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature extraction aggregation failed: {str(e)}"
        )

    # Save to features database registry under "domain_intel" as the aggregated evidence key
    feature_in = FeatureCreate(
        scan_id=payload.scan_id,
        key="domain_intel",
        value=extracted_data
    )
    feature_repo.create(db, obj_in=feature_in)

    return extracted_data

@router.get("/{id}", response_model=FeatureResponse)
def get_extraction_by_id(
    *,
    db: Session = Depends(get_db),
    id: int
) -> Any:
    """
    Retrieves a specific feature extraction record by its ID.
    """
    feature = feature_repo.get(db, id=id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature record with ID {id} not found."
        )
    return feature

@router.get("/history/{scan_id}", response_model=List[FeatureResponse])
def get_extraction_history(
    *,
    db: Session = Depends(get_db),
    scan_id: int
) -> Any:
    """
    Retrieves the basic extraction history (features list) for a specific scan ID.
    """
    # Verify scan ID exists first
    scan = scan_repo.get(db, id=scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID {scan_id} not found."
        )
    
    features = db.query(Feature).filter(Feature.scan_id == scan_id).all()
    return features
