import json
from datetime import datetime, timezone
from app.services.campaign_engine.models import (
    Campaign,
    CampaignMember,
    CampaignSeverity,
    CampaignStatus,
    CampaignSummary,
    CorrelationEvidence,
)
from app.services.campaign_engine.service import CampaignCorrelationService

def test_campaign_models():
    print('=== TESTING CAMPAIGN ENGINE FOUNDATION ===')
    
    try:
        # 1. Test Model Serialization
        print('\n--- 1. Testing Pydantic Models & Enums ---')
        
        evidence = CorrelationEvidence(
            type="shared_ip",
            value="192.168.1.50",
            description="Both indicators resolve to the same hosting IP address",
            confidence="high"
        )
        
        member = CampaignMember(
            indicator="https://fake-login-campaign.com",
            indicator_type="url",
            added_at=datetime.now(timezone.utc),
            added_reason="Correlated via shared IP address"
        )
        
        summary = CampaignSummary(
            total_indicators=1,
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc)
        )
        
        campaign = Campaign(
            campaign_id="CAMP-20260807-001",
            name="Automated Infrastructure Test Campaign",
            status=CampaignStatus.ACTIVE,
            severity=CampaignSeverity.HIGH,
            members=[member],
            summary=summary,
            shared_infrastructure=[evidence]
        )
        
        campaign_json = json.dumps(campaign.model_dump(mode='json'), indent=2)
        print("✅ Models serialized successfully!")
        print(f"Serialized Campaign Snippet:\n{campaign_json[:350]}...")

        # 2. Test Interfaces & Services
        print('\n--- 2. Testing Service Imports ---')
        service = CampaignCorrelationService()
        
        print("✅ CampaignCorrelationService instantiated successfully.")
        
    except Exception as e:
        print(f"❌ Foundation test failed: {e}")

if __name__ == '__main__':
    test_campaign_models()
