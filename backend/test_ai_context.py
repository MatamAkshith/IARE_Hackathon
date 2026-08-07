import json
from datetime import datetime, timezone
from app.services.ai_assistant.schemas import AssistantMessage, SuggestedAction, ResponseType
from app.services.ai_assistant.context_builder import InvestigationContextBuilder

def test_ai_context_builder():
    print('=== TESTING AI INVESTIGATION CONTEXT BUILDER ===')
    
    # 1. Test Schema Instantiation
    try:
        print("\n--- 1. Testing Schemas & Models ---")
        msg = AssistantMessage(role="assistant", content="Testing schemas.", timestamp=datetime.now(timezone.utc))
        action = SuggestedAction(label="Block IP", action_type="block", payload={"ip": "1.1.1.1"})
        print(f"✅ Schemas instantiated successfully! Action Label: {action.label}")
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return

    # 2. Test Context Builder with Mock Data
    print("\n--- 2. Testing Context Aggregation ---")
    builder = InvestigationContextBuilder()
    
    mock_evidence = {
        "url": "https://secure-update-login.com/auth",
        "ip_address": "192.168.1.100",
        "domain": "secure-update-login.com",
        "domain_age_days": 2,
        "cert_issuer": "Let's Encrypt"
    }
    
    mock_risk = {
        "risk_score": 95,
        "risk_level": "CRITICAL",
        "explanation": "Newly registered domain using free TLS certificate to host a login page."
    }
    
    mock_campaign = {
        "campaign_id": "CAMP-TEST-001",
        "related_indicators": 5
    }

    try:
        context = builder.build_context(
            indicator="https://secure-update-login.com/auth",
            evidence=mock_evidence,
            risk_assessment=mock_risk,
            campaign_details=mock_campaign
        )
        print("✅ InvestigationContext object generated successfully!")
        
        print("\n--- 3. Testing Prompt Generation ---")
        prompt = builder.generate_system_prompt(context)
        print("✅ System Prompt Generated!")
        print("-" * 50)
        print(prompt[:400] + "\n...[TRUNCATED]...")
        print("-" * 50)
        print(f"Prompt Length: {len(prompt)} characters")
        
    except Exception as e:
        print(f"❌ Context Builder test failed: {e}")

if __name__ == '__main__':
    test_ai_context_builder()
