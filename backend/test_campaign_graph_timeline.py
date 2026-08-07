from datetime import datetime, timezone
from app.services.campaign_engine.models import (
    Campaign,
    CampaignMember,
    CampaignSummary,
    CampaignSeverity,
    CampaignStatus,
)
from app.services.campaign_engine.service import CampaignCorrelationService
from app.services.campaign_engine.graph_models import NodeType

def test_graph_and_timeline():
    print("=== TESTING CAMPAIGN RELATIONSHIP GRAPH & TIMELINE (Stage 7.4) ===")
    
    # 1. Setup a Mock Campaign with 2 members containing rich resolved observations
    now = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
    reg_date_a = "2026-08-01T00:00:00Z"
    reg_date_b = "2026-08-03"
    
    m1 = CampaignMember(
        indicator="https://site-a.com",
        indicator_type="url",
        added_at=datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc),
        added_reason="Initial seeding",
        resolved_observations={
            "indicator": "https://site-a.com",
            "ip_address": "192.168.10.20",
            "asn": "AS9999",
            "tls_serial": "ABC12345",
            "tls_issuer": "Let's Encrypt",
            "registrar": "Namecheap",
            "domain_creation_date": reg_date_a,
            "page_title": "Fake Banking Login Secure Portal"
        }
    )
    
    m2 = CampaignMember(
        indicator="https://site-b.com",
        indicator_type="url",
        added_at=datetime(2026, 8, 7, 11, 0, 0, tzinfo=timezone.utc),
        added_reason="Shared infrastructure match",
        resolved_observations={
            "indicator": "https://site-b.com",
            "ip_address": "192.168.10.20", # SHARED IP!
            "asn": "AS9999",               # SHARED ASN!
            "tls_serial": "XYZ99999",       # DIFFERENT Cert
            "tls_issuer": "DigiCert",
            "registrar": "GoDaddy",
            "domain_creation_date": reg_date_b,
            "page_title": "Fake Secure Portal Login Screen"
        }
    )
    
    campaign = Campaign(
        campaign_id="CAMP-20260807-RICH",
        name="Rich Graph & Timeline Test Campaign",
        status=CampaignStatus.ACTIVE,
        severity=CampaignSeverity.HIGH,
        members=[m1, m2],
        summary=CampaignSummary(total_indicators=2, first_seen=now, last_seen=now),
        shared_infrastructure=[],
        created_at=now,
        updated_at=now
    )
    
    service = CampaignCorrelationService()
    
    # 2. Test Graph Generation
    print("\n--- 1. Testing Relationship Graph Builder ---")
    graph = service.get_campaign_graph(campaign)
    print(f"Graph nodes count: {len(graph.nodes)}")
    print(f"Graph edges count: {len(graph.edges)}")
    
    # Verify indicator nodes
    indicators = [n for n in graph.nodes if n.type == NodeType.INDICATOR]
    assert len(indicators) == 2
    assert {i.id for i in indicators} == {"https://site-a.com", "https://site-b.com"}
    
    # Verify IP node is shared
    ip_nodes = [n for n in graph.nodes if n.type == NodeType.IP]
    assert len(ip_nodes) == 1
    assert ip_nodes[0].id == "192.168.10.20"
    
    # Verify ASN node is shared
    asn_nodes = [n for n in graph.nodes if n.type == NodeType.ASN]
    assert len(asn_nodes) == 1
    assert asn_nodes[0].id == "AS9999"
    
    # Verify edges
    resolves_edges = [e for e in graph.edges if e.relationship == "resolves_to"]
    assert len(resolves_edges) == 2
    assert {e.source for e in resolves_edges} == {"https://site-a.com", "https://site-b.com"}
    assert {e.target for e in resolves_edges} == {"192.168.10.20"}
    
    print("✅ CampaignGraph structure matches expectations!")

    # 3. Test Timeline Generation
    print("\n--- 2. Testing Campaign Timeline Service ---")
    timeline = service.get_campaign_timeline(campaign)
    print(f"Timeline events count: {len(timeline.events)}")
    
    # Expected chronological order:
    # 1. Registration A (2026-08-01)
    # 2. Registration B (2026-08-03)
    # 3. Association A  (2026-08-07 10:00:00)
    # 4. Association B  (2026-08-07 11:00:00)
    # 5. Campaign Creation (2026-08-07 12:00:00)
    
    assert len(timeline.events) == 5
    
    for idx, event in enumerate(timeline.events):
        print(f"  [{idx + 1}] {event.timestamp.isoformat()} | {event.event_type.upper()} | {event.description} ({event.indicator})")
        
    assert timeline.events[0].event_type == "domain_registration"
    assert timeline.events[0].indicator == "https://site-a.com"
    
    assert timeline.events[1].event_type == "domain_registration"
    assert timeline.events[1].indicator == "https://site-b.com"
    
    assert timeline.events[2].event_type == "indicator_association"
    assert timeline.events[2].indicator == "https://site-a.com"
    
    assert timeline.events[3].event_type == "indicator_association"
    assert timeline.events[3].indicator == "https://site-b.com"
    
    assert timeline.events[4].event_type == "campaign_creation"
    assert timeline.events[4].indicator == "https://site-a.com"

    print("✅ CampaignTimeline events chronological sort passes!")

if __name__ == "__main__":
    test_graph_and_timeline()
