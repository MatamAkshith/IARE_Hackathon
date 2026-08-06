from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, domain_repo
from app.schemas.domain import DomainCreate, DomainUpdate, DomainResponse

router = APIRouter()

@router.get("", response_model=List[DomainResponse])
def read_domains(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    domains = domain_repo.get_multi(db, skip=skip, limit=limit)
    return domains

@router.post("", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
def create_domain(
    *,
    db: Session = Depends(get_db),
    domain_in: DomainCreate
) -> Any:
    db_obj = domain_repo.create(db, obj_in=domain_in)
    return db_obj

@router.get("/{id}", response_model=DomainResponse)
def read_domain(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    domain = domain_repo.get(db, id=id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    return domain

@router.put("/{id}", response_model=DomainResponse)
def update_domain(
    *,
    id: int,
    db: Session = Depends(get_db),
    domain_in: DomainUpdate
) -> Any:
    domain = domain_repo.get(db, id=id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    domain = domain_repo.update(db, db_obj=domain, obj_in=domain_in)
    return domain

@router.delete("/{id}", response_model=DomainResponse)
def delete_domain(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    domain = domain_repo.get(db, id=id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    domain = domain_repo.remove(db, id=id)
    return domain
