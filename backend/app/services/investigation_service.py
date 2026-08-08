"""
InvestigationService — Stage G.2

Handles timeouts and automatic recovery of stalled scans (pending/processing/scanning).
"""
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

logger = logging.getLogger("app.services.investigation_service")

STALE_THRESHOLD_MINUTES = 3

def recover_stale_scans(db: Session) -> int:
    """
    Finds scans stuck in 'pending', 'scanning', or 'processing' states
    that were created more than STALE_THRESHOLD_MINUTES ago, and marks them 'failed'.
    Returns the count of recovered scans.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=STALE_THRESHOLD_MINUTES)
    
    from app.models.scan import Scan
    
    stale_scans = db.query(Scan).filter(
        Scan.status.in_(["pending", "scanning", "processing"]),
        Scan.created_at < cutoff
    ).all()
    
    count = 0
    for scan in stale_scans:
        logger.warning(
            f"[recover_stale_scans] Scan #{scan.id} (status='{scan.status}') "
            f"created at {scan.created_at} exceeded timeout. Marking as 'failed'."
        )
        scan.status = "failed"
        db.add(scan)
        count += 1
        
    if count > 0:
        db.commit()
        
    return count
