"""
Campaign Persistence Repository — Stage 7.5

Implements database read/write queries for Campaign and CampaignMember records
mapping to/from Pydantic domain models.
"""

from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.campaign import CampaignRecord, CampaignMemberRecord
from app.services.campaign_engine.models import (
    Campaign,
    CampaignMember,
    CampaignSummary,
    CampaignSeverity,
    CampaignStatus,
    CorrelationEvidence,
)

logger = logging.getLogger("app.services.campaign_engine.repository")


class CampaignRepository:
    """
    Handles persistence logic for the Campaign Correlation Engine.
    Transforms ORM records to domain Pydantic objects and vice versa.
    """

    @staticmethod
    def record_to_domain(record: CampaignRecord) -> Campaign:
        """Helper to transform a CampaignRecord database model to a Pydantic Campaign model."""
        members = []
        for m_rec in record.members:
            members.append(CampaignMember(
                indicator=m_rec.indicator,
                indicator_type=m_rec.indicator_type,
                added_at=m_rec.added_at,
                added_reason=m_rec.added_reason,
                resolved_observations=m_rec.resolved_observations_json or {}
            ))

        summary_data = record.summary_json or {}
        # Parse timestamps in summary safely
        first_seen = summary_data.get("first_seen")
        last_seen = summary_data.get("last_seen")
        
        summary = CampaignSummary(
            total_indicators=summary_data.get("total_indicators", len(members)),
            first_seen=first_seen,
            last_seen=last_seen,
            primary_ttp_tags=summary_data.get("primary_ttp_tags") or []
        )

        shared_infra = []
        infra_data = record.shared_infrastructure_json or []
        for infra in infra_data:
            shared_infra.append(CorrelationEvidence(
                type=infra.get("type", "unknown"),
                value=infra.get("value", ""),
                confidence=infra.get("confidence", "unknown"),
                description=infra.get("description", "")
            ))

        return Campaign(
            campaign_id=record.campaign_id,
            name=record.name,
            status=CampaignStatus(record.status),
            severity=CampaignSeverity(record.severity),
            members=members,
            summary=summary,
            shared_infrastructure=shared_infra,
            created_at=record.created_at,
            updated_at=record.updated_at
        )

    def save_campaign(self, campaign: Campaign, db: Session) -> CampaignRecord:
        """
        Persists a Pydantic Campaign model to the database.
        Handles both creating new campaigns and updating existing ones.
        """
        logger.info(f"[save_campaign] Saving campaign '{campaign.campaign_id}' (members: {len(campaign.members)})")

        record = db.query(CampaignRecord).filter(
            CampaignRecord.campaign_id == campaign.campaign_id
        ).first()

        summary_dict = campaign.summary.model_dump(mode='json')
        infra_list = [infra.model_dump(mode='json') for infra in campaign.shared_infrastructure]

        if not record:
            logger.info(f"[save_campaign] Campaign '{campaign.campaign_id}' not found. Creating new record.")
            record = CampaignRecord(
                campaign_id=campaign.campaign_id,
                name=campaign.name,
                status=campaign.status.value,
                severity=campaign.severity.value,
                summary_json=summary_dict,
                shared_infrastructure_json=infra_list
            )
            db.add(record)
        else:
            logger.info(f"[save_campaign] Campaign '{campaign.campaign_id}' exists. Updating fields.")
            record.name = campaign.name
            record.status = campaign.status.value
            record.severity = campaign.severity.value
            record.summary_json = summary_dict
            record.shared_infrastructure_json = infra_list

        # Reconcile members
        db_members = db.query(CampaignMemberRecord).filter(
            CampaignMemberRecord.campaign_id == campaign.campaign_id
        ).all()
        existing_indicators = {m.indicator: m for m in db_members}

        # Track Pydantic members to keep
        processed_indicators = set()

        for member in campaign.members:
            processed_indicators.add(member.indicator)
            if member.indicator in existing_indicators:
                # Update existing member (e.g. if merge updated added_reason)
                m_rec = existing_indicators[member.indicator]
                m_rec.added_reason = member.added_reason
                m_rec.resolved_observations_json = member.resolved_observations
            else:
                # Add new member
                m_rec = CampaignMemberRecord(
                    campaign_id=campaign.campaign_id,
                    indicator=member.indicator,
                    indicator_type=member.indicator_type,
                    added_at=member.added_at,
                    added_reason=member.added_reason,
                    resolved_observations_json=member.resolved_observations
                )
                db.add(m_rec)

        # Delete any database members that are no longer in the Pydantic campaign (e.g. from drift splitting)
        for ind, m_rec in existing_indicators.items():
            if ind not in processed_indicators:
                logger.info(f"[save_campaign] Removing member '{ind}' from campaign '{campaign.campaign_id}' due to drift split.")
                db.delete(m_rec)

        try:
            db.commit()
            db.refresh(record)
            logger.info(f"[save_campaign] Successfully persisted campaign '{campaign.campaign_id}'")
        except Exception as exc:
            db.rollback()
            logger.error(f"[save_campaign] Failed to save campaign '{campaign.campaign_id}': {exc}", exc_info=True)
            raise exc

        return record

    def get_active_campaigns(self, db: Session) -> List[Campaign]:
        """Retrieves all campaigns with status='active'."""
        records = db.query(CampaignRecord).filter(
            CampaignRecord.status == CampaignStatus.ACTIVE.value
        ).all()
        return [self.record_to_domain(r) for r in records]

    def get_campaign_by_id(self, campaign_id: str, db: Session) -> Optional[Campaign]:
        """Retrieves a campaign by its unique campaign_id."""
        record = db.query(CampaignRecord).filter(
            CampaignRecord.campaign_id == campaign_id
        ).first()
        if not record:
            return None
        return self.record_to_domain(record)

    def list_campaigns(self, db: Session, skip: int = 0, limit: int = 50) -> List[Campaign]:
        """Lists campaigns with pagination, ordered by latest update first."""
        records = db.query(CampaignRecord).order_by(
            desc(CampaignRecord.updated_at)
        ).offset(skip).limit(limit).all()
        return [self.record_to_domain(r) for r in records]
