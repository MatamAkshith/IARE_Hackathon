from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, feature_repo, scan_repo
from app.services.domain_intel import DomainIntelService
from app.schemas.feature import FeatureCreate

router = APIRouter()

class DomainExtractionRequest(BaseModel):
    url: str
    scan_id: int

class NetworkExtractionRequest(BaseModel):
    url: str
    scan_id: int

@router.post("/domain", response_model=Any, status_code=status.HTTP_201_CREATED)
def extract_domain_intelligence(
    *,
    db: Session = Depends(get_db),
    payload: DomainExtractionRequest
) -> Any:
    # Verify target scan_id exists in the database first
    scan = scan_repo.get(db, id=payload.scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID {payload.scan_id} not found."
        )

    service = DomainIntelService()
    try:
        extracted_data = service.extract_intelligence(payload.url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Domain intelligence extraction failed: {str(e)}"
        )

    # Save to features database registry
    feature_in = FeatureCreate(
        scan_id=payload.scan_id,
        key="domain_intel",
        value=extracted_data
    )
    feature_repo.create(db, obj_in=feature_in)

    return extracted_data


from app.services.network_intel import NetworkIntelService

@router.post("/network", response_model=Any, status_code=status.HTTP_201_CREATED)
def extract_network_intelligence(
    *,
    db: Session = Depends(get_db),
    payload: NetworkExtractionRequest
) -> Any:
    # Verify target scan_id exists in the database first
    scan = scan_repo.get(db, id=payload.scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID {payload.scan_id} not found."
        )

    service = NetworkIntelService()
    try:
        extracted_data = service.extract_network_intelligence(payload.url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Network intelligence extraction failed: {str(e)}"
        )

    # Save to features database registry
    feature_in = FeatureCreate(
        scan_id=payload.scan_id,
        key="network_intel",
        value=extracted_data
    )
    feature_repo.create(db, obj_in=feature_in)

    return extracted_data

