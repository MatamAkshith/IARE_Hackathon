import uuid
from typing import Any, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.scan import Scan
from app.models.domain import Domain
from app.models.campaign import Campaign as LegacyCampaign
from app.db.models.campaign import CampaignRecord, CampaignMemberRecord


def attribute_scan_to_campaign(
    db: Session,
    scan_id: int,
    telemetry_data: Dict[str, Any],
    overall_score: float
) -> None:
    """
    Correlates high-risk manual investigations to campaigns based on brand name or
    shared infrastructure (IP/ASN), updating both the Scan record and the clustering engine tables.
    """
    # Rule 1: If Risk Score < 71 (SAFE/MEDIUM): Leave campaign_id as NULL (Unattributed)
    if overall_score < 71:
        return

    # Find the scan record
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return

    domain = db.query(Domain).filter(Domain.id == scan.domain_id).first()
    if not domain:
        return
    url = domain.url

    # Extract indicators from telemetry_data
    ip_address = telemetry_data.get("ip_address")
    asn = telemetry_data.get("asn")

    # Extract brand from url/domain
    brand = None
    url_lower = url.lower()
    brands = [
        "microsoft", "google", "amazon", "paypal", "github", "apple", "netflix",
        "infosys", "tcs", "wipro", "hcl", "techmahindra", "cognizant", "accenture",
        "icici", "hdfc", "sbi", "axis", "paytm", "phonepe", "vardhaman", "vmeg"
    ]
    for b in brands:
        if b in url_lower:
            if b == "vmeg":
                brand = "VMEG"
            elif b == "tcs":
                brand = "TCS"
            elif b == "hcl":
                brand = "HCL"
            elif b == "sbi":
                brand = "SBI"
            elif b == "hdfc":
                brand = "HDFC"
            elif b == "icici":
                brand = "ICICI"
            else:
                brand = b.capitalize()
            break

    # Look for matching active CampaignRecord
    matched_campaign = None
    active_campaigns = db.query(CampaignRecord).filter(
        func.lower(CampaignRecord.status) == "active"
    ).all()

    for camp in active_campaigns:
        # Check by brand name match
        if brand and brand.lower() in camp.name.lower():
            matched_campaign = camp
            break
        # Check by shared infrastructure (IP/ASN)
        for member in camp.members:
            obs = member.resolved_observations_json or {}
            if (ip_address and obs.get("ip_address") == ip_address) or (asn and obs.get("asn") == asn):
                matched_campaign = camp
                break
        if matched_campaign:
            break

    # If matching Campaign exists, update scan & members
    if matched_campaign:
        # Update Scan record campaign_id (legacy campaign lookup)
        legacy_camp = db.query(LegacyCampaign).filter(LegacyCampaign.name == matched_campaign.name).first()
        if not legacy_camp:
            legacy_camp = LegacyCampaign(name=matched_campaign.name, status="active")
            db.add(legacy_camp)
            db.commit()
            db.refresh(legacy_camp)

        scan.campaign_id = legacy_camp.id

        # Add a CampaignMemberRecord if it doesn't already exist
        existing_member = db.query(CampaignMemberRecord).filter(
            CampaignMemberRecord.campaign_id == matched_campaign.campaign_id,
            CampaignMemberRecord.indicator == url
        ).first()
        if not existing_member:
            new_member = CampaignMemberRecord(
                campaign_id=matched_campaign.campaign_id,
                indicator=url,
                indicator_type="url",
                added_reason="Coordinated infrastructure/behavior overlap",
                resolved_observations_json={**telemetry_data, "scan_id": scan.id}
            )
            db.add(new_member)
        db.commit()
    else:
        # If no matching campaign exists, create a new Campaign
        camp_name = f"Auto-Generated {brand or 'Generic'} Campaign"
        campaign_uid = f"CAMP-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"

        # Create Legacy Campaign
        legacy_camp = LegacyCampaign(name=camp_name, status="active")
        db.add(legacy_camp)
        db.commit()
        db.refresh(legacy_camp)

        scan.campaign_id = legacy_camp.id

        # Create CampaignRecord
        now = datetime.now(timezone.utc)
        new_camp_rec = CampaignRecord(
            campaign_id=campaign_uid,
            name=camp_name,
            status="active",
            severity="high" if overall_score < 86 else "critical",
            summary_json={
                "campaignName": camp_name,
                "campaignId": campaign_uid,
                "status": "Active",
                "riskLevel": "High" if overall_score < 86 else "Critical",
                "confidence": "90%",
                "totalIndicators": 1,
                "first_seen": now.isoformat(),
                "last_seen": now.isoformat(),
                "firstSeen": now.isoformat(),
                "lastSeen": now.isoformat(),
                "primary_ttp_tags": [brand.lower()] if brand else ["generic"],
                "primaryTtpTags": [brand.lower()] if brand else ["generic"]
            },
            shared_infrastructure_json=[
                {"type": "ip", "value": ip_address}
            ] if ip_address else []
        )
        db.add(new_camp_rec)
        db.commit()

        # Create CampaignMemberRecord
        new_member = CampaignMemberRecord(
            campaign_id=campaign_uid,
            indicator=url,
            indicator_type="url",
            added_reason="Initial high-risk indicator seeding campaign",
            resolved_observations_json={**telemetry_data, "scan_id": scan.id}
        )
        db.add(new_member)
        db.commit()
