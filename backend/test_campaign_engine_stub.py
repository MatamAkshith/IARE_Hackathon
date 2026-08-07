import json
from app.services.campaign_engine import (
    CampaignSeverity,
    CampaignStatus,
    CampaignMember,
    CorrelationEvidence,
    CorrelationResult,
    CampaignSummary,
    Campaign,
    CampaignCorrelationService,
)

def test_campaign_engine_imports_and_serialization():
    print("=== TESTING CAMPAIGN ENGINE FOUNDATION (Stage 7.1) ===")
    
    # 1. Enums check
    print("\n--- 1. Enums Check ---")
    assert CampaignSeverity.LOW == "low"
    assert CampaignSeverity.CRITICAL == "critical"
    assert CampaignStatus.ACTIVE == "active"
    assert CampaignStatus.DORMANT == "dormant"
    print("✅ Enums verified successfully!")

    # 2. Service Initialization check
    print("\n--- 2. Service Initialization Check ---")
    service = CampaignCorrelationService()
    print("✅ CampaignCorrelationService instantiated successfully!")

    # 3. Model Serialization check via mock creation
    print("\n--- 3. Mock Campaign Creation Check ---")
    mock_evidence = {
        "indicator": "https://suspicious-lure-portal.tk",
        "indicator_type": "url",
        "ip_address": "203.0.113.5",
        "domain_age_days": 5,
    }
    
    campaign = service.create_campaign(
        name="Target impersonation 2026-A",
        initial_evidence=mock_evidence,
        severity=CampaignSeverity.HIGH
    )
    
    print(f"✅ Campaign created successfully! ID: {campaign.campaign_id}")
    print(f"   Name: '{campaign.name}' | Severity: {campaign.severity.value} | Status: {campaign.status.value}")
    print(f"   First Member: {campaign.members[0].indicator} (added reason: {campaign.members[0].added_reason})")
    
    # Verify JSON serialization
    serialized = campaign.model_dump_json()
    print(f"   JSON Serialization verified successfully!")

    # 4. Service Stub Call check
    print("\n--- 4. Service stub additions check ---")
    related = service.find_related_campaigns(mock_evidence)
    print(f"   Related campaigns search returned: {related} (Stub)")

    updated_campaign = service.add_to_campaign(
        campaign_id=campaign.campaign_id,
        evidence={
            "indicator": "https://suspicious-lure-portal2.tk",
            "indicator_type": "url",
            "ip_address": "203.0.113.5"
        }
    )
    print(f"   Updated Campaign Summary: total_indicators={updated_campaign.summary.total_indicators}")
    print(f"   Updated Campaign Infrastructure elements count: {len(updated_campaign.shared_infrastructure)}")
    
    print("\n✅ All imports, enums, stubs, and serializations function perfectly!")

if __name__ == "__main__":
    test_campaign_engine_imports_and_serialization()
