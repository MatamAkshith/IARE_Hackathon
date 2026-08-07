import json
from app.services.campaign_engine.service import CampaignCorrelationService
from app.services.campaign_engine.models import CampaignStatus, CampaignSeverity, CampaignMember

def test_campaign_clustering():
    print("=== TESTING CAMPAIGN CLUSTERING & DRIFT SPLIT ENGINE (Stage 7.3) ===")
    
    # Instantiate service
    service = CampaignCorrelationService()
    
    active_campaigns = []
    
    # ── Test 1: CREATE Campaign ──
    print("\n--- Test 1: Creating Campaign for Indicator A ---")
    evidence_a = {
        "indicator": "https://phishing-site-a.com",
        "indicator_type": "url",
        "ip_address": "203.0.113.5",
        "tls_serial": "11111",
        "page_title": "Credential Harvest Login A"
    }
    
    camp_a, action_a = service.process_investigation(evidence_a, active_campaigns)
    print(f"Action: {action_a} | Campaign ID: {camp_a.campaign_id} | Name: {camp_a.name}")
    assert action_a == "created"
    assert len(camp_a.members) == 1
    assert camp_a.members[0].indicator == "https://phishing-site-a.com"
    
    # Save active campaign
    active_campaigns.append(camp_a)
    
    # ── Test 2: JOIN Campaign ──
    print("\n--- Test 2: Joining Indicator B to Campaign A ---")
    evidence_b = {
        "indicator": "https://phishing-site-b.com",
        "indicator_type": "url",
        "ip_address": "203.0.113.5",     # Match shared IP (25 points)
        "tls_serial": "11111",            # Match shared TLS serial (20 points)
        "page_title": "Credential Harvest Login B"
    }
    # Match score: 25 (IP) + 20 (TLS Serial) = 45 points (0.45) >= 0.40 threshold.
    
    camp_b, action_b = service.process_investigation(evidence_b, active_campaigns)
    print(f"Action: {action_b} | Campaign ID: {camp_b.campaign_id} | Members count: {len(camp_b.members)}")
    assert action_b == "joined"
    assert camp_b.campaign_id == camp_a.campaign_id
    assert len(camp_b.members) == 2
    
    # ── Test 3: CREATE Campaign C (distinct) ──
    print("\n--- Test 3: Creating Campaign C for Distinct Indicator C ---")
    evidence_c = {
        "indicator": "https://phishing-site-c.com",
        "indicator_type": "url",
        "ip_address": "198.51.100.10",
        "tls_serial": "33333",
        "page_title": "Different Phishing Title C"
    }
    camp_c, action_c = service.process_investigation(evidence_c, active_campaigns)
    print(f"Action: {action_c} | Campaign ID: {camp_c.campaign_id} | Name: {camp_c.name}")
    assert action_c == "created"
    
    # Save active campaign
    active_campaigns.append(camp_c)
    
    # ── Test 4: MERGE Campaigns A and C ──
    print("\n--- Test 4: Merging Campaigns A and C via Intermediary Domain D ---")
    evidence_d = {
        "indicator": "https://phishing-site-d.com",
        "indicator_type": "url",
        # Shares IP and TLS Serial with Campaign A
        "ip_address": "203.0.113.5",
        "tls_serial": "11111",
        # Shares HTML structure hash with Campaign C
        "html_structure_hash": "ccccc_hash",
        "structural_hash": "ccccc_hash" # supporting fallback key name in HTML correlator
    }
    # Let's populate structural_hash in evidence_c to trigger match with evidence_d
    camp_c.members[0].resolved_observations["structural_hash"] = "ccccc_hash"
    camp_c.members[0].resolved_observations["html_structure_hash"] = "ccccc_hash"
    # Wait, does c share something else with d to cross threshold?
    # html_structure_hash = 5 points. shared registrant org = 8 points. registrant org match:
    camp_c.members[0].resolved_observations["org"] = "adversary_org"
    evidence_d["org"] = "adversary_org" # registrant org = 8 points
    camp_c.members[0].resolved_observations["registrar"] = "namecheap"
    evidence_d["registrar"] = "namecheap" # registrar = 4
    camp_c.members[0].resolved_observations["page_title"] = "Different Phishing Title C"
    evidence_d["page_title"] = "Different Phishing Title C" # page_title = 8
    camp_c.members[0].resolved_observations["forms_count"] = 3
    evidence_d["forms_count"] = 3 # forms_count = 2
    # Match score D vs C = 5 (html hash) + 8 (registrant org) + 4 (registrar) + 8 (page title) + 2 (forms count) = 27 raw points.
    # Wait, 27 / 100 = 0.27, which is < 0.40 threshold. Let's make it share more:
    # Let's share DNS A/AAAA records:
    camp_c.members[0].resolved_observations["a_records"] = ["198.51.100.10"]
    evidence_d["a_records"] = ["198.51.100.10"] # shared_dns_records = 10 pts
    # Now D vs C = 27 + 10 = 37 pts. Still below 40. Let's share ASN:
    camp_c.members[0].resolved_observations["asn"] = "AS54321"
    evidence_d["asn"] = "AS54321" # shared_asn = 5 pts
    # Now D vs C = 37 + 5 = 42 pts. 42 / 100 = 0.42 >= 0.40 threshold!
    # And D vs A = 25 (IP) + 20 (TLS Serial) = 45 pts >= 0.40 threshold.
    # Therefore, D will correlate with BOTH Campaign A (via members A/B) and Campaign C (via member C).
    
    camp_d, action_d = service.process_investigation(evidence_d, active_campaigns)
    print(f"Action: {action_d} | Re-homed Campaign ID: {camp_d.campaign_id} | Total Members: {len(camp_d.members)}")
    assert action_d == "merged"
    # Should contain members: A, B, C, D (Total: 4)
    assert len(camp_d.members) == 4
    
    # ── Test 5: SPLIT Campaign due to similarity drift ──
    print("\n--- Test 5: Simulating/Testing Campaign Split Checks ---")
    # Let's create a campaign with 3 members: member 1 and member 2 correlate, but member 3 has no correlation with either.
    m1 = CampaignMember(
        indicator="https://site-1.com",
        indicator_type="url",
        added_reason="Seeding",
        resolved_observations={"indicator": "https://site-1.com", "ip_address": "1.1.1.1", "cert_serial": "XYZ"}
    )
    m2 = CampaignMember(
        indicator="https://site-2.com",
        indicator_type="url",
        added_reason="Correlated with 1",
        resolved_observations={"indicator": "https://site-2.com", "ip_address": "1.1.1.1", "cert_serial": "XYZ"}
    )
    m3 = CampaignMember(
        indicator="https://site-3.com",
        indicator_type="url",
        added_reason="Redundant addition",
        resolved_observations={"indicator": "https://site-3.com", "ip_address": "9.9.9.9"}
    )
    
    from app.services.campaign_engine.models import CampaignSummary, Campaign
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    drift_campaign = Campaign(
        campaign_id="CAMP-DRIFT-TEST",
        name="Drift Test Campaign",
        members=[m1, m2, m3],
        summary=CampaignSummary(total_indicators=3, first_seen=now, last_seen=now),
        shared_infrastructure=[],
        created_at=now,
        updated_at=now
    )
    
    split_result = service.check_campaign_drift(drift_campaign)
    print(f"Split completed. Returned {len(split_result)} campaign(s).")
    assert len(split_result) == 2
    print(f"  - Campaign 1 ID: {split_result[0].campaign_id} | members count: {len(split_result[0].members)}")
    print(f"  - Campaign 2 ID: {split_result[1].campaign_id} | members count: {len(split_result[1].members)}")
    assert len(split_result[0].members) == 2
    assert len(split_result[1].members) == 1
    
    print("\n✅ Campaign clustering and drift split checks verified successfully!")

if __name__ == "__main__":
    test_campaign_clustering()
