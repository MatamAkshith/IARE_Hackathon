"""
Automatic Campaign Correlation Engine — Stage G.3

Orchestrates automated scan attribution and campaign clustering.
"""
import logging
from sqlalchemy.orm import Session
from app.models.scan import Scan
from app.models.domain import Domain
from app.db.models.unified_evidence import UnifiedEvidenceRecord
from app.models.campaign import Campaign as LegacyCampaign
from app.services.campaign_engine.service import CampaignCorrelationService

logger = logging.getLogger("app.services.campaign_service")
correlation_service = CampaignCorrelationService()

def run_campaign_correlation(investigation_id: int, db: Session) -> None:
    """
    Kicks off campaign correlation for the completed investigation.
    Extracts features from UnifiedEvidence, queries the clustering engine,
    associates the scan to the resulting campaign, and updates the DB.
    """
    logger.info(f"[run_campaign_correlation] Starting correlation for scan ID {investigation_id}")
    
    # 1. Fetch scan
    scan = db.query(Scan).filter(Scan.id == investigation_id).first()
    if not scan:
        logger.error(f"[run_campaign_correlation] Scan #{investigation_id} not found.")
        return
        
    # 2. Fetch domain
    domain = db.query(Domain).filter(Domain.id == scan.domain_id).first()
    if not domain:
        logger.error(f"[run_campaign_correlation] Domain for Scan #{investigation_id} not found.")
        return
        
    target_domain = domain.url
    
    # 3. Fetch latest unified evidence
    evidence_rec = db.query(UnifiedEvidenceRecord).filter(
        UnifiedEvidenceRecord.indicator == target_domain
    ).order_by(UnifiedEvidenceRecord.timestamp.desc()).first()
    
    # Build resolved observations payload
    if evidence_rec and evidence_rec.resolved_observations:
        evidence_payload = dict(evidence_rec.resolved_observations)
    else:
        # Fallback if no unified evidence record exists yet
        evidence_payload = {
            "indicator": target_domain,
            "indicator_type": "url",
            "ip_address": "",
            "cert_serial": "",
            "page_title": ""
        }
        
    # Standardize indicators
    evidence_payload["indicator"] = target_domain
    evidence_payload["indicator_type"] = "url"
    
    try:
        # 4. Trigger Campaign Clustering Engine
        campaign, action = correlation_service.process_investigation(new_evidence=evidence_payload, db=db)
        logger.info(
            f"[run_campaign_correlation] Scan #{investigation_id} clustered. "
            f"Campaign ID: '{campaign.campaign_id}' (name='{campaign.name}') | Action: '{action}'"
        )
        
        # 5. Link with LegacyCampaign model for full compatibility
        legacy_camp = db.query(LegacyCampaign).filter(LegacyCampaign.name == campaign.name).first()
        if not legacy_camp:
            legacy_camp = LegacyCampaign(
                name=campaign.name, 
                description=f"Automated Campaign Group ({campaign.campaign_id})"
            )
            db.add(legacy_camp)
            db.commit()
            db.refresh(legacy_camp)
            
        scan.campaign_id = legacy_camp.id
        db.add(scan)
        db.commit()
        
        logger.info(f"[run_campaign_correlation] Scan #{investigation_id} linked to Campaign ID {legacy_camp.id} (UUID: {campaign.campaign_id}).")
    except Exception as e:
        logger.error(f"[run_campaign_correlation] Error running correlation engine: {e}", exc_info=True)
