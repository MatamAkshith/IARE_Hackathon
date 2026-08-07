"""
CampaignCorrelationService — Stage 7.2

Main orchestration service skeleton for finding, grouping, and managing
phishing assets within Campaign clusters. Includes the evaluate_link interface
wrapping the similarity engine.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.services.campaign_engine.models import (
    Campaign,
    CampaignMember,
    CampaignSeverity,
    CampaignStatus,
    CampaignSummary,
    CorrelationEvidence,
    CorrelationResult,
)
from app.services.campaign_engine.similarity import SimilarityEngine
from app.services.campaign_engine.clustering import CampaignClusterer
from app.services.campaign_engine.graph_models import CampaignGraph, CampaignTimeline
from app.services.campaign_engine.graph_builder import CampaignGraphBuilder
from app.services.campaign_engine.timeline import CampaignTimelineService
from app.services.campaign_engine.repository import CampaignRepository
from app.db.models.campaign import CampaignRecord

logger = logging.getLogger("app.services.campaign_engine.service")


class CampaignCorrelationService:
    """
    Main orchestration class for the Campaign Correlation Engine.
    Provides stub interfaces for campaign grouping and similarity evaluation.
    """

    def __init__(self) -> None:
        self._similarity_engine = SimilarityEngine()
        self._clusterer = CampaignClusterer(similarity_threshold=self._similarity_engine.threshold)
        self._graph_builder = CampaignGraphBuilder()
        self._timeline_service = CampaignTimelineService()
        self._repository = CampaignRepository()
        logger.info(
            "[CampaignCorrelationService] Initializing Campaign Correlation Service with SimilarityEngine, "
            "CampaignClusterer, CampaignGraphBuilder, CampaignTimelineService, and CampaignRepository."
        )

    def evaluate_link(
        self,
        source_evidence: Dict[str, Any],
        target_evidence: Dict[str, Any],
    ) -> CorrelationResult:
        """
        Runs the registered similarity engine correlators to evaluate relationships
        and calculate a similarity match score between two evidence packages.

        Parameters
        ----------
        source_evidence : Dictionary representing resolved features of Evidence A.
        target_evidence : Dictionary representing resolved features of Evidence B.

        Returns
        -------
        CorrelationResult detailing matched overlaps, is_correlated boolean, and score.
        """
        logger.info(
            f"[evaluate_link] Starting similarity match between "
            f"'{source_evidence.get('indicator', 'unknown')}' and '{target_evidence.get('indicator', 'unknown')}'"
        )
        return self._similarity_engine.compare_evidence(source_evidence, target_evidence)

    def find_related_campaigns(
        self,
        evidence: Dict[str, Any],
    ) -> List[Campaign]:
        """
        Stub interface to inspect current investigation evidence and query historical
        campaigns for infrastructure, content, or behavioral overlaps.

        Parameters
        ----------
        evidence : Flat dictionary representing resolved features (from UnifiedEvidence).

        Returns
        -------
        List of matching Campaign registries.
        """
        indicator = evidence.get("indicator", "unknown")
        logger.info(f"[find_related_campaigns] Searching for campaigns related to indicator: '{indicator}'")
        
        # Stub implementation returning empty list
        logger.debug(f"[find_related_campaigns] Completed query for '{indicator}'. No matches found (Stub).")
        return []

    def create_campaign(
        self,
        name: str,
        initial_evidence: Dict[str, Any],
        severity: CampaignSeverity = CampaignSeverity.LOW,
    ) -> Campaign:
        """
        Stub interface to register a new Campaign cluster seeded with a member.

        Parameters
        ----------
        name             : Human-readable name of the campaign.
        initial_evidence : Flat dictionary representing resolved features of the first member.
        severity         : Initial threat severity.

        Returns
        -------
        Newly created Campaign object.
        """
        indicator = initial_evidence.get("indicator", "unknown")
        indicator_type = initial_evidence.get("indicator_type", "url")
        logger.info(f"[create_campaign] Creating new campaign '{name}' seeded by: '{indicator}'")

        campaign_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        member = CampaignMember(
            indicator=indicator,
            indicator_type=indicator_type,
            added_at=now,
            added_reason="Initial indicator seeding the campaign.",
            resolved_observations=initial_evidence,
        )

        summary = CampaignSummary(
            total_indicators=1,
            first_seen=now,
            last_seen=now,
            primary_ttp_tags=[],
        )

        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            status=CampaignStatus.ACTIVE,
            severity=severity,
            members=[member],
            summary=summary,
            shared_infrastructure=[],
            created_at=now,
            updated_at=now,
        )

        logger.info(f"[create_campaign] Successfully created Campaign campaign_id='{campaign_id}' ('{name}').")
        return campaign

    def add_to_campaign(
        self,
        campaign_id: str,
        evidence: Dict[str, Any],
        added_reason: str = "Correlated infrastructure/behavior overlap",
    ) -> Campaign:
        """
        Stub interface to associate a newly detected indicator to an existing campaign,
        updating members tracking and summary metrics.

        Parameters
        ----------
        campaign_id  : Unique identifier of the target campaign.
        evidence     : Flat dictionary representing resolved features of the new member.
        added_reason : Analytical reason for matching.

        Returns
        -------
        Updated Campaign object.
        """
        indicator = evidence.get("indicator", "unknown")
        indicator_type = evidence.get("indicator_type", "url")
        logger.info(f"[add_to_campaign] Adding member '{indicator}' to campaign: '{campaign_id}'")

        # Stub implementation returning a dummy Campaign representation
        now = datetime.now(timezone.utc)
        member = CampaignMember(
            indicator=indicator,
            indicator_type=indicator_type,
            added_at=now,
            added_reason=added_reason,
            resolved_observations=evidence,
        )

        summary = CampaignSummary(
            total_indicators=2,
            first_seen=now,
            last_seen=now,
            primary_ttp_tags=["stub-ttp"],
        )

        dummy_campaign = Campaign(
            campaign_id=campaign_id,
            name="Mock Stub Campaign",
            status=CampaignStatus.ACTIVE,
            severity=CampaignSeverity.MEDIUM,
            members=[member],
            summary=summary,
            shared_infrastructure=[
                CorrelationEvidence(
                    type="shared_ip",
                    value=evidence.get("ip_address", "127.0.0.1"),
                    confidence="medium",
                    description="Associated via stub infrastructure matching.",
                )
            ],
            created_at=now,
            updated_at=now,
        )

        logger.info(f"[add_to_campaign] Successfully added member '{indicator}' to campaign: '{campaign_id}'.")
        return dummy_campaign

    def process_investigation(
        self,
        new_evidence: Dict[str, Any],
        active_campaigns: Optional[List[Campaign]] = None,
        db: Optional[Session] = None,
    ) -> Tuple[Campaign, str]:
        """
        Processes a newly generated investigation evidence block, grouping it
        into a campaign (created, joined, or merged) using the CampaignClusterer.
        If a DB session is provided, automatically fetches active campaigns from the DB,
        performs clustering, handles merge deactivations, and persists the result.
        """
        indicator = new_evidence.get("indicator", "unknown")
        logger.info(f"[process_investigation] Processing clustering for indicator: '{indicator}'")

        if active_campaigns is None:
            if db:
                active_campaigns = self._repository.get_active_campaigns(db)
                logger.info(f"[process_investigation] Fetched {len(active_campaigns)} active campaigns from database.")
            else:
                active_campaigns = []
                logger.info("[process_investigation] No active campaigns or DB session provided. Defaulting to empty list.")

        campaign, action = self._clusterer.cluster_indicator(new_evidence, active_campaigns)

        if db:
            if action == "merged":
                # Deactivate merged secondary campaigns
                primary_indicators = {m.indicator for m in campaign.members}
                db_active_records = db.query(CampaignRecord).filter(
                    CampaignRecord.status == "active",
                    CampaignRecord.campaign_id != campaign.campaign_id
                ).all()
                for r in db_active_records:
                    record_indicators = {m.indicator for m in r.members}
                    if record_indicators and record_indicators.issubset(primary_indicators):
                        logger.info(f"[process_investigation] Deactivating merged secondary campaign '{r.campaign_id}' (status='merged')")
                        r.status = "merged"
            
            # Persist resulting campaign (insert or update)
            self._repository.save_campaign(campaign, db)

        logger.info(
            f"[process_investigation] Finished processing indicator '{indicator}'. "
            f"Campaign ID: '{campaign.campaign_id}' | Action: '{action}'."
        )
        return campaign, action

    def check_campaign_drift(
        self,
        campaign: Campaign,
        db: Optional[Session] = None,
    ) -> List[Campaign]:
        """
        Checks a campaign for similarity drift among its members and splits it
        if required. If a DB session is provided, persists the split campaigns to the DB.
        """
        split_campaigns = self._clusterer.check_for_split(campaign)
        if db and len(split_campaigns) > 1:
            logger.info(f"[check_campaign_drift] Mutated campaign split. Persisting {len(split_campaigns)} campaigns to DB.")
            for camp in split_campaigns:
                self._repository.save_campaign(camp, db)
        return split_campaigns

    def get_campaign_graph(
        self,
        campaign: Campaign,
    ) -> CampaignGraph:
        """
        Generates the relationship graph connecting campaign members and shared infrastructure.
        """
        return self._graph_builder.build_graph(campaign)

    def get_campaign_timeline(
        self,
        campaign: Campaign,
    ) -> CampaignTimeline:
        """
        Generates the chronological timeline of events for a campaign.
        """
        return self._timeline_service.generate_timeline(campaign)
