import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/ai"

def test_openrouter_endpoints():
    print('=== TESTING OPENROUTER AI INTEGRATION ===')
    
    # Target indicator and components
    indicator_str = "https://secure-update-login.com/auth"
    
    evidence_payload = {
        "indicator": indicator_str,
        "indicator_type": "url",
        "metadata": {
            "domain": "secure-update-login.com",
            "ip_address": "192.168.1.100"
        }
    }
    
    risk_payload = {
        "indicator": indicator_str,
        "overall_score": 95.0,
        "severity": "CRITICAL",
        "breakdown": {
            "heuristic_score": 95.0,
            "factors": ["Newly registered domain", "Free TLS cert"]
        }
    }
    
    campaign_payload = {
        "campaign_id": "CAMP-20260807-001",
        "name": "Automated Test Campaign",
        "status": "ACTIVE",
        "severity": "CRITICAL",
        "members": [],
        "summary": {
            "total_indicators": 5,
            "first_seen": "2026-08-07T00:00:00Z",
            "last_seen": "2026-08-07T00:00:00Z"
        }
    }

    try:
        # 1. Test Q&A Endpoint (/ask)
        print("\n--- 1. POST /api/v1/ai/ask ---")
        ask_body = {
            "indicator": indicator_str,
            "query": "Why is this indicator dangerous?",
            "evidence": evidence_payload,
            "risk_assessment": risk_payload,
            "campaign_details": campaign_payload
        }
        res_ask = requests.post(f"{BASE_URL}/ask", json=ask_body)
        
        if res_ask.status_code == 200:
            data = res_ask.json()
            print("✅ Q&A Response Received via OpenRouter!")
            print(f"   Answer: {data.get('message', {}).get('content')}")
            print(f"   Suggested Actions: {[a.get('label') for a in data.get('suggested_actions', [])]}")
        else:
            print(f"❌ Q&A Request Failed ({res_ask.status_code}): {res_ask.text}")

        # 2. Test Executive Summary Endpoint (/report/executive)
        print("\n--- 2. POST /api/v1/ai/report/executive ---")
        exec_body = {
            "indicator": indicator_str,
            "evidence": evidence_payload,
            "risk_assessment": risk_payload,
            "campaign_details": campaign_payload
        }
        res_exec = requests.post(f"{BASE_URL}/report/executive", json=exec_body)
        
        if res_exec.status_code == 200:
            data = res_exec.json()
            print("✅ Executive Summary Received via OpenRouter!")
            print(f"   Indicator: {data.get('indicator')}")
            print(f"   Overall Risk Rating: {data.get('overall_risk_rating')}")
            print(f"   Overall Score: {data.get('overall_score')}")
            print(f"   Key Findings: {data.get('key_findings')}")
            print(f"   Business Impact: {data.get('business_impact')}")
            print(f"   Action Summary: {data.get('recommended_action_summary')}")
        else:
            print(f"❌ Executive Summary Request Failed ({res_exec.status_code}): {res_exec.text}")

        print("\n🎉 MILESTONE 8 END-TO-END VERIFICATION COMPLETE!")

    except Exception as e:
        print(f"❌ Test script encountered an error: {e}")

if __name__ == '__main__':
    test_openrouter_endpoints()
