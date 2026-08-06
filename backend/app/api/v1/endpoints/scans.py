from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, scan_repo
from app.schemas.scan import ScanCreate, ScanUpdate, ScanResponse

router = APIRouter()

@router.get("", response_model=List[ScanResponse])
def read_scans(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    scans = scan_repo.get_multi(db, skip=skip, limit=limit)
    return scans

@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def create_scan(
    *,
    db: Session = Depends(get_db),
    scan_in: ScanCreate
) -> Any:
    db_obj = scan_repo.create(db, obj_in=scan_in)
    return db_obj

@router.get("/{id}", response_model=ScanResponse)
def read_scan(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    return scan

@router.put("/{id}", response_model=ScanResponse)
def update_scan(
    *,
    id: int,
    db: Session = Depends(get_db),
    scan_in: ScanUpdate
) -> Any:
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    scan = scan_repo.update(db, db_obj=scan, obj_in=scan_in)
    return scan

@router.delete("/{id}", response_model=ScanResponse)
def delete_scan(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    scan = scan_repo.remove(db, id=id)
    return scan
