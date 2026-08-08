from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, scan_repo, get_current_user, log_activity
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
    # Stage G.2: Recover any hung scans first
    try:
        from app.services.investigation_service import recover_stale_scans
        recover_stale_scans(db)
    except Exception as e:
        logger.error(f"[read_scans] Error recovering stale scans: {e}")

    scans = scan_repo.get_multi(db, skip=skip, limit=limit)
    for scan in scans:
        _populate_scan_campaign(db, scan)
    return scans


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def create_scan(
    *,
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user),
    scan_in: ScanCreate
) -> Any:
    scan_in.initiated_by = current_user.user_id
    db_obj = scan_repo.create(db, obj_in=scan_in)
    
    # E.5: Log activity
    log_activity(db, current_user.user_id, "scan_create", req_obj, str(db_obj.domain_id))
    
    return _populate_scan_campaign(db, db_obj)


@router.get("/{id}", response_model=ScanResponse)
def read_scan(
    id: int,
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    scan = scan_repo.get(db, id=id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
        
    log_activity(db, current_user.user_id, "scan_view", req_obj, str(id))
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
    
    # Stage G.3: If scan has completed, trigger the attribution engine
    if scan.status == "completed":
        try:
            from app.services.campaign_service import run_campaign_correlation
            run_campaign_correlation(scan.id, db)
            db.refresh(scan)
        except Exception as exc:
            logger.error(f"[update_scan] Automatic campaign correlation failed: {exc}", exc_info=True)
            
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
