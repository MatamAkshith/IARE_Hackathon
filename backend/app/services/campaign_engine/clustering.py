"""
CampaignClusterer — Stage 7.3

Groups related investigations into phishing campaigns using similarity scores.
Automatically handles joining campaigns, creating new ones, merging overlapping
campaigns, and checking for similarity drift (splitting).
"""

import logging
import random
import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

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

logger = logging.getLogger("app.services.campaign_engine.clustering")


def _generate_campaign_id() -> str:
    """Generates a campaign ID matching the format: CAMP-YYYYMMDD-XXXX"""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    rand_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CAMP-{date_str}-{rand_str}"


class CampaignClusterer:
    """
    Evaluates new evidence against active campaigns and clusters them.
    Supports joining, creating, merging, and splitting operations.
    """

    def __init__(self, similarity_threshold: float = 0.40) -> None:
        self.similarity_engine = SimilarityEngine(threshold=similarity_threshold)
        logger.info(
            f"[CampaignClusterer] Initialized with similarity_threshold={similarity_threshold:.2f}"
        )

    def cluster_indicator(
        self,
        new_evidence: Dict[str, Any],
        active_campaigns: List[Campaign],
    ) -> Tuple[Campaign, str]:
        """
        Evaluates new evidence against all active campaigns.

        Rules:
        1. CREATE: If no active campaign correlates (max similarity < threshold),
           create a new campaign.
        2. JOIN: If exactly one active campaign correlates, add the indicator as
           a member of that campaign.
        3. MERGE: If the indicator correlates with multiple active campaigns,
           merge them all into a single unified campaign and add the indicator.

        Parameters
        ----------
        new_evidence     : Flat dictionary representing the new indicator features.
        active_campaigns : List of currently tracked active campaigns.

        Returns
        -------
        Tuple of (Target/Resulting Campaign, Action string ['created' | 'joined' | 'merged']).
        """
        indicator = new_evidence.get("indicator", "unknown")
        indicator_type = new_evidence.get("indicator_type", "url")
        logger.info(f"[cluster_indicator] Evaluating clustering for '{indicator}' against {len(active_campaigns)} active campaign(s)")

        # List of tuples: (Campaign, max_score, list of matched CorrelationEvidence)
        matched_campaigns: List[Tuple[Campaign, float, List[CorrelationEvidence]]] = []

        for campaign in active_campaigns:
            max_score = 0.0
            best_evidence: List[CorrelationEvidence] = []

            for member in campaign.members:
                res: CorrelationResult = self.similarity_engine.compare_evidence(
                    new_evidence, member.resolved_observations
                )
                if res.is_correlated and res.match_score > max_score:
                    max_score = res.match_score
                    best_evidence = res.evidence

            if max_score >= self.similarity_engine.threshold:
                matched_campaigns.append((campaign, max_score, best_evidence))

        # Sort matches by score descending
        matched_campaigns.sort(key=lambda x: x[1], reverse=True)

        now = datetime.now(timezone.utc)

        # ── Case 1: CREATE ────────────────────────────────────────────────── #
        if not matched_campaigns:
            logger.info(f"[cluster_indicator] No correlation found for '{indicator}'. Creating new campaign.")
            campaign_id = _generate_campaign_id()
            
            member = CampaignMember(
                indicator=indicator,
                indicator_type=indicator_type,
                added_at=now,
                added_reason="Initial seeding indicator.",
                resolved_observations=new_evidence,
            )
            
            summary = CampaignSummary(
                total_indicators=1,
                first_seen=now,
                last_seen=now,
                primary_ttp_tags=self._extract_ttp_tags(new_evidence),
            )

            new_camp = Campaign(
                campaign_id=campaign_id,
                name=f"Campaign {campaign_id}",
                status=CampaignStatus.ACTIVE,
                severity=self._deduce_severity(new_evidence),
                members=[member],
                summary=summary,
                shared_infrastructure=self._extract_infrastructure_evidence(new_evidence),
                created_at=now,
                updated_at=now,
            )
            return new_camp, "created"

        # ── Case 2: JOIN ──────────────────────────────────────────────────── #
        if len(matched_campaigns) == 1:
            target_campaign, score, evidence_hits = matched_campaigns[0]
            logger.info(
                f"[cluster_indicator] Strong correlation ({score * 100:.0f}%) found with "
                f"campaign '{target_campaign.campaign_id}' ('{target_campaign.name}'). Joining."
            )

            # Build attribution reason
            types = ", ".join(sorted({h.type for h in evidence_hits}))
            reason = f"Correlated with campaign members via shared {types} (match score: {score * 100:.0f}%)."

            new_member = CampaignMember(
                indicator=indicator,
                indicator_type=indicator_type,
                added_at=now,
                added_reason=reason,
                resolved_observations=new_evidence,
            )
            target_campaign.members.append(new_member)

            # Update Campaign Summary
            all_dates = [m.added_at for m in target_campaign.members]
            target_campaign.summary.total_indicators = len(target_campaign.members)
            target_campaign.summary.first_seen = min(all_dates)
            target_campaign.summary.last_seen = max(all_dates)
            
            new_tags = self._extract_ttp_tags(new_evidence)
            union_tags = list(set(target_campaign.summary.primary_ttp_tags + new_tags))
            target_campaign.summary.primary_ttp_tags = union_tags

            # Merge shared infrastructure evidence (avoid duplicates)
            seen_infra = {(ev.type, ev.value) for ev in target_campaign.shared_infrastructure}
            for hit in evidence_hits:
                if (hit.type, hit.value) not in seen_infra:
                    target_campaign.shared_infrastructure.append(hit)

            # Also add this indicator's own standalone infrastructure evidence
            own_infra = self._extract_infrastructure_evidence(new_evidence)
            for hit in own_infra:
                if (hit.type, hit.value) not in seen_infra:
                    target_campaign.shared_infrastructure.append(hit)

            target_campaign.updated_at = now
            return target_campaign, "joined"

        # ── Case 3: MERGE ─────────────────────────────────────────────────── #
        logger.info(
            f"[cluster_indicator] Overlapping correlation found with {len(matched_campaigns)} campaigns. "
            f"Merging all into primary campaign '{matched_campaigns[0][0].campaign_id}'."
        )
        
        # Primary is the one with the highest similarity match score
        primary_campaign = matched_campaigns[0][0]
        primary_evidence = matched_campaigns[0][2]
        
        # Merge all members and infrastructure from secondary campaigns
        merged_ids = []
        for sec_campaign, _, sec_evidence in matched_campaigns[1:]:
            merged_ids.append(sec_campaign.campaign_id)
            
            # Re-home members with merge annotations
            for member in sec_campaign.members:
                if member.indicator not in {m.indicator for m in primary_campaign.members}:
                    member.added_reason += f" (Merged from campaign: {sec_campaign.campaign_id})"
                    primary_campaign.members.append(member)
            
            # Re-home shared infrastructure
            seen_infra = {(ev.type, ev.value) for ev in primary_campaign.shared_infrastructure}
            for ev in sec_campaign.shared_infrastructure + sec_evidence:
                if (ev.type, ev.value) not in seen_infra:
                    primary_campaign.shared_infrastructure.append(ev)

        # Re-home matches from primary comparison too
        seen_infra = {(ev.type, ev.value) for ev in primary_campaign.shared_infrastructure}
        for ev in primary_evidence:
            if (ev.type, ev.value) not in seen_infra:
                primary_campaign.shared_infrastructure.append(ev)

        # Add the new indicator itself
        reason = f"Correlated with and triggered merge of campaigns: {', '.join(merged_ids)}"
        new_member = CampaignMember(
            indicator=indicator,
            indicator_type=indicator_type,
            added_at=now,
            added_reason=reason,
            resolved_observations=new_evidence,
        )
        primary_campaign.members.append(new_member)

        # Recalculate summary metrics
        all_dates = [m.added_at for m in primary_campaign.members]
        primary_campaign.summary.total_indicators = len(primary_campaign.members)
        primary_campaign.summary.first_seen = min(all_dates)
        primary_campaign.summary.last_seen = max(all_dates)

        # Merge TTP tags
        merged_tags: Set[str] = set(primary_campaign.summary.primary_ttp_tags)
        for sec_campaign, _, _ in matched_campaigns[1:]:
            merged_tags.update(sec_campaign.summary.primary_ttp_tags)
        merged_tags.update(self._extract_ttp_tags(new_evidence))
        primary_campaign.summary.primary_ttp_tags = list(merged_tags)

        # Upgrade severity if any merged campaign had higher severity
        severities = [primary_campaign.severity] + [c.severity for c, _, _ in matched_campaigns[1:]]
        primary_campaign.severity = self._max_severity(severities)
        
        primary_campaign.updated_at = now
        return primary_campaign, "merged"

    # ── Split (Heuristic Evaluation & Stub) ────────────────────────────────── #

    def check_for_split(self, campaign: Campaign) -> List[Campaign]:
        """
        Evaluates similarity metrics among all members inside a campaign.
        If a subset of members drifts away (no correlation links to others),
        it splits them off into a new separate campaign.

        Heuristic:
        Builds an undirected correlation graph of all members. If the graph
        is disconnected (contains multiple components), split the campaign
        along those components.
        """
        if len(campaign.members) <= 1:
            return [campaign]

        logger.info(f"[check_for_split] Checking campaign '{campaign.campaign_id}' for similarity drift.")

        # Build adjacency list: member index -> set of connected member indexes
        adj: Dict[int, Set[int]] = {i: set() for i in range(len(campaign.members))}

        for i in range(len(campaign.members)):
            for j in range(i + 1, len(campaign.members)):
                res = self.similarity_engine.compare_evidence(
                    campaign.members[i].resolved_observations,
                    campaign.members[j].resolved_observations,
                )
                if res.is_correlated:
                    adj[i].add(j)
                    adj[j].add(i)

        # Find connected components (BFS/DFS)
        visited = set()
        components: List[List[int]] = []

        for i in range(len(campaign.members)):
            if i not in visited:
                comp = []
                queue = [i]
                visited.add(i)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)

        # If there's only one connected component, no split is needed
        if len(components) <= 1:
            logger.debug(f"[check_for_split] Campaign '{campaign.campaign_id}' remains cohesive.")
            return [campaign]

        logger.info(
            f"[check_for_split] Similarity drift detected! Splitting campaign "
            f"'{campaign.campaign_id}' into {len(components)} separate campaigns."
        )

        split_campaigns: List[Campaign] = []
        now = datetime.now(timezone.utc)

        # Collect component members first to avoid mutating campaign.members during iteration
        components_members = []
        for comp_indices in components:
            components_members.append([campaign.members[i] for i in comp_indices])

        for idx, comp_members in enumerate(components_members):
            # Keep primary properties for the first component
            if idx == 0:
                campaign.members = comp_members
                # Recalculate summary
                all_dates = [m.added_at for m in comp_members]
                campaign.summary.total_indicators = len(comp_members)
                campaign.summary.first_seen = min(all_dates)
                campaign.summary.last_seen = max(all_dates)
                campaign.updated_at = now
                split_campaigns.append(campaign)
            else:
                # Spawn a new campaign for secondary components
                new_id = _generate_campaign_id()
                all_dates = [m.added_at for m in comp_members]
                
                summary = CampaignSummary(
                    total_indicators=len(comp_members),
                    first_seen=min(all_dates),
                    last_seen=max(all_dates),
                    primary_ttp_tags=list({t for m in comp_members for t in m.resolved_observations.get("ttp_tags", [])}),
                )
                
                # Re-extract shared infrastructure for this component
                infra = []
                for i in range(len(comp_members)):
                    for j in range(i + 1, len(comp_members)):
                        res = self.similarity_engine.compare_evidence(
                            comp_members[i].resolved_observations,
                            comp_members[j].resolved_observations
                        )
                        for hit in res.evidence:
                            if hit not in infra:
                                infra.append(hit)

                new_camp = Campaign(
                    campaign_id=new_id,
                    name=f"Campaign {new_id} (Split from {campaign.campaign_id})",
                    status=CampaignStatus.ACTIVE,
                    severity=campaign.severity,
                    members=comp_members,
                    summary=summary,
                    shared_infrastructure=infra,
                    created_at=now,
                    updated_at=now,
                )
                split_campaigns.append(new_camp)

        return split_campaigns

    # ── Heuristic helpers ──────────────────────────────────────────────────── #

    @staticmethod
    def _extract_ttp_tags(evidence: Dict[str, Any]) -> List[str]:
        """Heuristically extracts TTP tags based on evidence attributes."""
        tags = []
        if evidence.get("virustotal_verdict") == "malicious":
            tags.append("vt-flagged")
        if evidence.get("has_login_form"):
            tags.append("credential-harvesting")
        if not evidence.get("ssl_valid", True):
            tags.append("invalid-tls")
        # Young domain
        age = evidence.get("domain_age_days")
        if age is not None:
            try:
                if int(age) < 30:
                    tags.append("young-domain")
            except (ValueError, TypeError):
                pass
        return tags

    @staticmethod
    def _extract_infrastructure_evidence(evidence: Dict[str, Any]) -> List[CorrelationEvidence]:
        """Extracts standalone infrastructure evidence for campaign summary records."""
        infra = []
        ip = evidence.get("ip_address") or evidence.get("ip")
        if ip:
            infra.append(CorrelationEvidence(
                type="ip_address",
                value=str(ip),
                confidence="high",
                description=f"Resolving IP: {ip}"
            ))
        asn = evidence.get("asn") or evidence.get("autonomous_system_number")
        if asn:
            infra.append(CorrelationEvidence(
                type="asn",
                value=str(asn),
                confidence="low",
                description=f"Host ASN: {asn}"
            ))
        return infra

    @staticmethod
    def _deduce_severity(evidence: Dict[str, Any]) -> CampaignSeverity:
        """Deduces initial campaign severity from evidence risk markers."""
        if evidence.get("virustotal_verdict") == "malicious" or evidence.get("urlhaus_verdict") == "malicious":
            return CampaignSeverity.CRITICAL
        if evidence.get("has_login_form") and not evidence.get("ssl_valid", True):
            return CampaignSeverity.HIGH
        if evidence.get("has_login_form") or not evidence.get("ssl_valid", True):
            return CampaignSeverity.MEDIUM
        return CampaignSeverity.LOW

    @staticmethod
    def _max_severity(severities: List[CampaignSeverity]) -> CampaignSeverity:
        """Finds the maximum severity in a list."""
        order = {
            CampaignSeverity.LOW: 0,
            CampaignSeverity.MEDIUM: 1,
            CampaignSeverity.HIGH: 2,
            CampaignSeverity.CRITICAL: 3,
        }
        max_sev = CampaignSeverity.LOW
        for sev in severities:
            if order[sev] > order[max_sev]:
                max_sev = sev
        return max_sev
