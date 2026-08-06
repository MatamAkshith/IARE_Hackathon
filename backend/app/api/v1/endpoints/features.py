from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, feature_repo
from app.schemas.feature import FeatureCreate, FeatureUpdate, FeatureResponse

router = APIRouter()

@router.get("", response_model=List[FeatureResponse])
def read_features(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    features = feature_repo.get_multi(db, skip=skip, limit=limit)
    return features

@router.post("", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
def create_feature(
    *,
    db: Session = Depends(get_db),
    feature_in: FeatureCreate
) -> Any:
    db_obj = feature_repo.create(db, obj_in=feature_in)
    return db_obj

@router.get("/{id}", response_model=FeatureResponse)
def read_feature(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    feature = feature_repo.get(db, id=id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    return feature

@router.put("/{id}", response_model=FeatureResponse)
def update_feature(
    *,
    id: int,
    db: Session = Depends(get_db),
    feature_in: FeatureUpdate
) -> Any:
    feature = feature_repo.get(db, id=id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    feature = feature_repo.update(db, db_obj=feature, obj_in=feature_in)
    return feature

@router.delete("/{id}", response_model=FeatureResponse)
def delete_feature(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    feature = feature_repo.get(db, id=id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    feature = feature_repo.remove(db, id=id)
    return feature
