import json
from datetime import datetime, timezone, timedelta
from app.services.campaign_engine.models import Campaign, CampaignMember, CampaignSummary, CampaignStatus, CampaignSeverity
from app.services.campaign_engine.service import CampaignCorrelationService
from app.services.campaign_engine.graph_models import CampaignGraph, CampaignTimeline

def test_graph_and_timeline():
    print('=== TESTING CAMPAIGN TIMELINE & GRAPH ENGINE ===')
    
    # 1. Setup a Mock Campaign with Members & Infrastructure
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    
    member1 = CampaignMember(
        indicator="https://secure-update-login.com",
        indicator_type="url",
        added_at=yesterday,
        added_reason="Initial indicator",
        resolved_observations={"ip_address": "192.168.1.100", "cert_issuer": "Let's Encrypt"}
    )
    
    member2 = CampaignMember(
        indicator="https://verify-account-now.net",
        indicator_type="url",
        added_at=now,
        added_reason="Joined via shared IP",
        resolved_observations={"ip_address": "192.168.1.100", "cert_issuer": "Let's Encrypt"}
    )

    campaign = Campaign(
        campaign_id="CAMP-TEST-001",
        name="Test Campaign Graph",
        status=CampaignStatus.ACTIVE,
        severity=CampaignSeverity.HIGH,
        members=[member1, member2],
        summary=CampaignSummary(total_indicators=2, first_seen=yesterday, last_seen=now),
        shared_infrastructure=[], # Graph builder should infer from member resolved_observations or explicitly listed evidence
        created_at=yesterday,
        updated_at=now
    )

    service = CampaignCorrelationService()

    try:
        # 2. Test Graph Generation
        print("\n--- Generating Relationship Graph ---")
        graph = service.get_campaign_graph(campaign)
        print(f"✅ Graph Generated Successfully!")
        print(f"   Total Nodes: {len(graph.nodes)}")
        print(f"   Total Edges: {len(graph.edges)}")
        
        print("\n   Nodes List:")
        for node in graph.nodes:
            print(f"    - [{node.type}] {node.id}")
            
        print("\n   Edges List:")
        for edge in graph.edges:
            print(f"    - {edge.source} --({edge.relationship})--> {edge.target}")

        # 3. Test Timeline Generation
        print("\n--- Generating Campaign Timeline ---")
        timeline = service.get_campaign_timeline(campaign)
        print(f"✅ Timeline Generated Successfully!")
        print(f"   Total Events: {len(timeline.events)}")
        
        print("\n   Chronological Events:")
        for event in timeline.events:
            print(f"    - [{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {event.event_type}: {event.description}")

    except Exception as e:
        print(f"❌ Graph/Timeline test failed: {e}")

if __name__ == '__main__':
    test_graph_and_timeline()
