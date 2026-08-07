from typing import Any, List, Dict
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.scan import Scan
from app.models.domain import Domain
from app.db.models.risk_assessment import RiskAssessmentRecord
from app.db.models.campaign import CampaignRecord, CampaignMemberRecord
from app.models.campaign import Campaign as LegacyCampaign

from app.core.config import settings

logger = logging.getLogger("app.services.dashboard_service")


class DashboardService:
    """
    Dashboard Service — ThreatLens Backend
    Runs dynamic SQL queries to aggregate real-time metrics and compile recent threat monitoring feeds.
    """

    def get_stats(self, db: Session) -> Dict[str, Any]:
        # 1. Get total_scans
        total_scans = db.query(Scan).count()

        # 2. Get latest score for each scan record
        scan_scores = []
        scans_with_domains = db.query(Scan, Domain).join(Domain, Scan.domain_id == Domain.id).all()
        for scan, domain in scans_with_domains:
            latest_risk = db.query(RiskAssessmentRecord).filter(
                RiskAssessmentRecord.indicator == domain.url
            ).order_by(RiskAssessmentRecord.timestamp.desc()).first()
            score = latest_risk.overall_score if latest_risk else 0.0
            scan_scores.append(score)

        # 3. Calculate high_risk_domains (overall_score >= 71)
        high_risk_domains = sum(1 for s in scan_scores if s >= 71)

        # 4. Calculate active_campaigns
        active_campaigns = db.query(CampaignRecord).filter(
            func.lower(CampaignRecord.status) == "active"
        ).count()

        # 5. Calculate avg_risk_score
        avg_risk_score = round(sum(scan_scores) / len(scan_scores), 1) if scan_scores else 0.0

        # 6. Calculate risk_distribution (SAFE: 0-20, MEDIUM: 21-70, HIGH: 71-90, CRITICAL: 91-100)
        safe_count = 0
        medium_count = 0
        high_count = 0
        critical_count = 0

        for score in scan_scores:
            if score <= 20:
                safe_count += 1
            elif score <= 70:
                medium_count += 1
            elif score <= 90:
                high_count += 1
            else:
                critical_count += 1

        def get_pct(count: int) -> float:
            if total_scans == 0:
                return 0.0
            return round((count / total_scans) * 100, 1)

        # 7. Calculate recent_activity_count: scans created in last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_activity_count = db.query(Scan).filter(
            Scan.created_at >= cutoff
        ).count()

        # 8. Calculate operational threat feeds (out of 5 possible feeds)
        total_feeds = 5
        active_feeds = 1  # Local Heuristics is always operational
        if settings.VIRUSTOTAL_API_KEY and settings.VIRUSTOTAL_API_KEY.strip():
            active_feeds += 1
        if settings.PHISHTANK_API_KEY and settings.PHISHTANK_API_KEY.strip():
            active_feeds += 1
        if settings.URLHAUS_API_KEY and settings.URLHAUS_API_KEY.strip():
            active_feeds += 1
        if settings.ABUSEIPDB_API_KEY and settings.ABUSEIPDB_API_KEY.strip():
            active_feeds += 1

        return {
            "total_scans": total_scans,
            "high_risk_domains": high_risk_domains,
            "active_campaigns": active_campaigns,
            "avg_risk_score": avg_risk_score,
            "recent_activity_count": recent_activity_count,
            "total_feeds": total_feeds,
            "active_feeds": active_feeds,
            "risk_distribution": [
                {
                    "label": "Safe (0-20)",
                    "count": safe_count,
                    "percentage": get_pct(safe_count),
                    "color": "bg-emerald-500"
                },
                {
                    "label": "Medium (21-70)",
                    "count": medium_count,
                    "percentage": get_pct(medium_count),
                    "color": "bg-amber-500"
                },
                {
                    "label": "High (71-90)",
                    "count": high_count,
                    "percentage": get_pct(high_count),
                    "color": "bg-orange-500"
                },
                {
                    "label": "Critical (91-100)",
                    "count": critical_count,
                    "percentage": get_pct(critical_count),
                    "color": "bg-rose-500"
                }
            ]
        }


    def get_recent_feed(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        # Fetch scans ordered by created_at desc
        scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(limit).all()
        feed = []

        for scan in scans:
            domain = db.query(Domain).filter(Domain.id == scan.domain_id).first()
            target_domain = domain.url if domain else f"Scan #{scan.id}"

            # Campaign attribution
            campaign_attribution = "Unattributed"
            if scan.campaign_id:
                leg_camp = db.query(LegacyCampaign).filter(LegacyCampaign.id == scan.campaign_id).first()
                if leg_camp:
                    campaign_attribution = leg_camp.name
            else:
                member = db.query(CampaignMemberRecord).filter(
                    CampaignMemberRecord.indicator == target_domain
                ).first()
                if member:
                    camp_rec = db.query(CampaignRecord).filter(
                        CampaignRecord.campaign_id == member.campaign_id
                    ).first()
                    if camp_rec:
                        campaign_attribution = camp_rec.name

            # Latest Risk Assessment
            latest_risk = db.query(RiskAssessmentRecord).filter(
                RiskAssessmentRecord.indicator == target_domain
            ).order_by(RiskAssessmentRecord.timestamp.desc()).first()

            if latest_risk:
                risk_score = latest_risk.overall_score
                # Standardize severity bands
                if risk_score <= 20:
                    risk_rating = "SAFE"
                elif risk_score <= 70:
                    risk_rating = "MEDIUM"
                elif risk_score <= 90:
                    risk_rating = "HIGH"
                else:
                    risk_rating = "CRITICAL"
            else:
                risk_score = 0.0
                risk_rating = "SAFE"

            feed.append({
                "id": scan.id,
                "target_domain": target_domain,
                "risk_score": risk_score,
                "risk_rating": risk_rating,
                "pipeline_status": scan.status.upper(),
                "campaign_attribution": campaign_attribution,
                "date_time": scan.created_at.isoformat()
            })

        return feed
