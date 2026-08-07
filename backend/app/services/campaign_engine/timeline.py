"""
Timeline Generation Service — Stage 7.4

Constructs a chronologically ordered sequence of milestones representing the
creation, registration, and correlation history of indicators grouped in a Campaign.
"""

import logging
from datetime import datetime, timezone
from typing import Any, List, Optional
from dateutil import parser

from app.services.campaign_engine.models import Campaign
from app.services.campaign_engine.graph_models import CampaignTimeline, TimelineEvent

logger = logging.getLogger("app.services.campaign_engine.timeline")


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Helper to safely parse diverse datetime shapes (ISO, YYYY-MM-DD, etc.) into timezone-aware datetimes."""
    if not value:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    
    val_str = str(value).strip()
    try:
        # Standard ISO-8601 parsing
        dt = datetime.fromisoformat(val_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        try:
            # Fallback parsing via dateutil
            dt = parser.parse(val_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            logger.debug(f"Failed to parse datetime value: '{value}'")
            return None


class CampaignTimelineService:
    """
    Generates a consolidated, chronologically sorted timeline of events
    associated with a phishing campaign.
    """

    def generate_timeline(self, campaign: Campaign) -> CampaignTimeline:
        """
        Extracts milestones from campaign logs and member metadata to build a chronological timeline.
        """
        logger.info(f"[generate_timeline] Compiling timeline for campaign '{campaign.campaign_id}'")

        events: List[TimelineEvent] = []

        # 1. Add Campaign Creation Event
        if campaign.created_at:
            created_dt = _parse_datetime(campaign.created_at)
            if created_dt:
                events.append(TimelineEvent(
                    timestamp=created_dt,
                    event_type="campaign_creation",
                    description=f"Campaign '{campaign.name}' (ID: {campaign.campaign_id}) was initialized.",
                    indicator=campaign.members[0].indicator if campaign.members else "system"
                ))

        # 2. Extract Member-Specific Events
        for member in campaign.members:
            indicator = member.indicator
            obs = member.resolved_observations or {}

            # A. Domain Creation Date (WHOIS)
            creation_val = obs.get("domain_creation_date") or obs.get("creation_date") or obs.get("created_at")
            if creation_val:
                creation_dt = _parse_datetime(creation_val)
                if creation_dt:
                    events.append(TimelineEvent(
                        timestamp=creation_dt,
                        event_type="domain_registration",
                        description=f"Domain '{indicator}' was registered (extracted from WHOIS data).",
                        indicator=indicator
                    ))

            # B. Association to Campaign (added_at)
            if member.added_at:
                added_dt = _parse_datetime(member.added_at)
                if added_dt:
                    events.append(TimelineEvent(
                        timestamp=added_dt,
                        event_type="indicator_association",
                        description=f"Indicator '{indicator}' associated with campaign. Reason: {member.added_reason}",
                        indicator=indicator
                    ))

        # Sort events chronologically (ascending: oldest first)
        events.sort(key=lambda ev: ev.timestamp)

        logger.info(f"[generate_timeline] Timeline generated successfully with {len(events)} events.")
        return CampaignTimeline(events=events)
