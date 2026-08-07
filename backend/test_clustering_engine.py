import json
from app.services.campaign_engine.service import CampaignCorrelationService

def test_clustering_engine():
    print('=== TESTING CAMPAIGN CLUSTERING ENGINE ===')
    
    # Evidence A (First malicious site)
    evidence_a = {
        "indicator": "https://secure-update-login.com",
        "indicator_type": "url",
        "ip_address": "192.168.1.100",
        "cert_issuer": "Let's Encrypt Authority X3",
        "cert_serial": "03A1B2C3D4E5F67890",
        "domain_creation_date": "2026-08-01",
        "page_title": "Secure Customer Portal Verification"
    }

    # Evidence B (Related site sharing infrastructure & cert — SHOULD JOIN Evidence A's campaign)
    evidence_b = {
        "indicator": "https://verify-account-now.net",
        "indicator_type": "url",
        "ip_address": "192.168.1.100",
        "cert_issuer": "Let's Encrypt Authority X3",
        "cert_serial": "03A1B2C3D4E5F67890",
        "domain_creation_date": "2026-08-01",
        "page_title": "Secure Customer Portal Verification"
    }

    # Evidence C (Unrelated site — SHOULD CREATE A NEW campaign)
    evidence_c = {
        "indicator": "http://totally-different-phish.org",
        "indicator_type": "url",
        "ip_address": "10.0.0.55",
        "cert_issuer": "Sectigo RSA",
        "cert_serial": "99999999999999",
        "domain_creation_date": "2025-01-15",
        "page_title": "Update your banking details"
    }

    service = CampaignCorrelationService()
    active_campaigns = []

    try:
        print("\n--- 1. Processing Evidence A (Expected: New Campaign Created) ---")
        camp_a, action_a = service.process_investigation(evidence_a, active_campaigns)
        active_campaigns.append(camp_a)
        print(f"✅ Action: {action_a.upper()}")
        print(f"   Campaign ID: {camp_a.campaign_id}")
        print(f"   Members Count: {len(camp_a.members)}")

        print("\n--- 2. Processing Evidence B (Expected: Joined Existing Campaign) ---")
        camp_b, action_b = service.process_investigation(evidence_b, active_campaigns)
        # Update active_campaigns list in place
        active_campaigns = [c if c.campaign_id != camp_b.campaign_id else camp_b for c in active_campaigns]
        
        print(f"✅ Action: {action_b.upper()}")
        print(f"   Target Campaign ID: {camp_b.campaign_id}")
        print(f"   Members Count: {len(camp_b.members)}")
        print(f"   Attribution Reason: {camp_b.members[-1].added_reason}")

        print("\n--- 3. Processing Evidence C (Expected: New Unrelated Campaign Created) ---")
        camp_c, action_c = service.process_investigation(evidence_c, active_campaigns)
        if action_c == "created":
            active_campaigns.append(camp_c)
        
        print(f"✅ Action: {action_c.upper()}")
        print(f"   New Campaign ID: {camp_c.campaign_id}")
        print(f"   Total Active Campaigns in System: {len(active_campaigns)}")

    except Exception as e:
        print(f"❌ Clustering test failed: {e}")

if __name__ == '__main__':
    test_clustering_engine()
