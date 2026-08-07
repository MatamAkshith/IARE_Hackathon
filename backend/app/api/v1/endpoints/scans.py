from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, scan_repo, get_current_user
from app.schemas.scan import ScanCreate, ScanUpdate, ScanResponse
from app.db.models.employee import EmployeeRecord

router = APIRouter()

def _populate_scan_campaign(db: Session, scan: Any) -> Any:
    if not scan:
        return scan
    from app.models.domain import Domain
    from app.models.campaign import Campaign as LegacyCampaign
    from app.db.models.campaign import CampaignRecord, CampaignMemberRecord

    domain = db.query(Domain).filter(Domain.id == scan.domain_id).first()
    target_domain = domain.url if domain else ""

    scan.campaign_name = None
    scan.campaign_uid = None

    if scan.campaign_id:
        leg_camp = db.query(LegacyCampaign).filter(LegacyCampaign.id == scan.campaign_id).first()
        if leg_camp:
            scan.campaign_name = leg_camp.name
            camp_rec = db.query(CampaignRecord).filter(CampaignRecord.name == leg_camp.name).first()
            if camp_rec:
                scan.campaign_uid = camp_rec.campaign_id
    else:
        member = db.query(CampaignMemberRecord).filter(
            CampaignMemberRecord.indicator == target_domain
        ).first()
        if member:
            camp_rec = db.query(CampaignRecord).filter(
                CampaignRecord.campaign_id == member.campaign_id
            ).first()
            if camp_rec:
                scan.campaign_name = camp_rec.name
                scan.campaign_uid = camp_rec.campaign_id

    # 3. Query latest risk assessment score
    from app.db.models.risk_assessment import RiskAssessmentRecord
    latest_risk = db.query(RiskAssessmentRecord).filter(
        RiskAssessmentRecord.indicator == target_domain
    ).order_by(RiskAssessmentRecord.timestamp.desc()).first()
    scan.overall_score = latest_risk.overall_score if latest_risk else None

    return scan


@router.get("", response_model=List[ScanResponse])
def read_scans(
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    scans = scan_repo.get_multi(db, skip=skip, limit=limit)
    for scan in scans:
        _populate_scan_campaign(db, scan)
    return scans


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def create_scan(
    *,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user),
    scan_in: ScanCreate
) -> Any:
    scan_in.initiated_by = current_user.user_id
    db_obj = scan_repo.create(db, obj_in=scan_in)
    return _populate_scan_campaign(db, db_obj)


@router.get("/{id}", response_model=ScanResponse)
def read_scan(
    id: int,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    return _populate_scan_campaign(db, scan)


@router.put("/{id}", response_model=ScanResponse)
def update_scan(
    *,
    id: int,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user),
    scan_in: ScanUpdate
) -> Any:
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    scan = scan_repo.update(db, db_obj=scan, obj_in=scan_in)
    return _populate_scan_campaign(db, scan)

@router.delete("/{id}", response_model=ScanResponse)
def delete_scan(
    id: int,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    scan = scan_repo.remove(db, id=id)
    return scan
