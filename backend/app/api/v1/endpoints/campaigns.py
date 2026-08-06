from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, campaign_repo
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse

router = APIRouter()

@router.get("", response_model=List[CampaignResponse])
def read_campaigns(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    campaigns = campaign_repo.get_multi(db, skip=skip, limit=limit)
    return campaigns

@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    *,
    db: Session = Depends(get_db),
    campaign_in: CampaignCreate
) -> Any:
    db_obj = campaign_repo.create(db, obj_in=campaign_in)
    return db_obj

@router.get("/{id}", response_model=CampaignResponse)
def read_campaign(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    campaign = campaign_repo.get(db, id=id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign

@router.put("/{id}", response_model=CampaignResponse)
def update_campaign(
    *,
    id: int,
    db: Session = Depends(get_db),
    campaign_in: CampaignUpdate
) -> Any:
    campaign = campaign_repo.get(db, id=id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    campaign = campaign_repo.update(db, db_obj=campaign, obj_in=campaign_in)
    return campaign

@router.delete("/{id}", response_model=CampaignResponse)
def delete_campaign(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    campaign = campaign_repo.get(db, id=id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    campaign = campaign_repo.remove(db, id=id)
    return campaign
