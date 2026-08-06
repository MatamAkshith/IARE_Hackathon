from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, risk_score_repo
from app.schemas.risk_score import RiskScoreCreate, RiskScoreUpdate, RiskScoreResponse

router = APIRouter()

@router.get("", response_model=List[RiskScoreResponse])
def read_risk_scores(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    risk_scores = risk_score_repo.get_multi(db, skip=skip, limit=limit)
    return risk_scores

@router.post("", response_model=RiskScoreResponse, status_code=status.HTTP_201_CREATED)
def create_risk_score(
    *,
    db: Session = Depends(get_db),
    risk_score_in: RiskScoreCreate
) -> Any:
    db_obj = risk_score_repo.create(db, obj_in=risk_score_in)
    return db_obj

@router.get("/{id}", response_model=RiskScoreResponse)
def read_risk_score(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    risk_score = risk_score_repo.get(db, id=id)
    if not risk_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk score not found"
        )
    return risk_score

@router.put("/{id}", response_model=RiskScoreResponse)
def update_risk_score(
    *,
    id: int,
    db: Session = Depends(get_db),
    risk_score_in: RiskScoreUpdate
) -> Any:
    risk_score = risk_score_repo.get(db, id=id)
    if not risk_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk score not found"
        )
    risk_score = risk_score_repo.update(db, db_obj=risk_score, obj_in=risk_score_in)
    return risk_score

@router.delete("/{id}", response_model=RiskScoreResponse)
def delete_risk_score(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    risk_score = risk_score_repo.get(db, id=id)
    if not risk_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk score not found"
        )
    risk_score = risk_score_repo.remove(db, id=id)
    return risk_score
