import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/campaigns"

def run_e2e_campaign_test():
    print("=== TESTING E2E CAMPAIGN API & PERSISTENCE ===")

    # 1. Submit Evidence A (Should CREATE a campaign)
    evidence_a = {
        "indicator": "https://bank-secure-update.com",
        "indicator_type": "url",
        "ip_address": "203.0.113.50",
        "cert_issuer": "BadActor CA",
        "page_title": "Secure Bank Login"
    }
    
    print("\n--- 1. POST /correlate (Evidence A) ---")
    res_a = requests.post(f"{BASE_URL}/correlate", json=evidence_a)
    if res_a.status_code != 200:
        print(f"❌ Failed: {res_a.text}")
        return
        
    data_a = res_a.json()
    campaign_id = data_a["campaign"]["campaign_id"]
    print(f"✅ Action: {data_a['action'].upper()}")
    print(f"   Created Campaign ID: {campaign_id}")
    print(f"   Members: {len(data_a['campaign']['members'])}")

    time.sleep(1) # Small delay to ensure timestamp differences

    # 2. Submit Evidence B (Should JOIN Evidence A's campaign)
    evidence_b = {
        "indicator": "https://verify-bank-secure.net",
        "indicator_type": "url",
        "ip_address": "203.0.113.50", # Shared IP
        "cert_issuer": "BadActor CA", # Shared Cert
        "page_title": "Secure Bank Login" # Shared Title
    }

    print("\n--- 2. POST /correlate (Evidence B) ---")
    res_b = requests.post(f"{BASE_URL}/correlate", json=evidence_b)
    data_b = res_b.json()
    print(f"✅ Action: {data_b['action'].upper()}")
    print(f"   Target Campaign ID: {data_b['campaign']['campaign_id']}")
    print(f"   Members: {len(data_b['campaign']['members'])}")
    
    # 3. Get Campaign Timeline
    print(f"\n--- 3. GET /{campaign_id}/timeline ---")
    res_time = requests.get(f"{BASE_URL}/{campaign_id}/timeline")
    timeline = res_time.json()
    print(f"✅ Timeline retrieved! Total Events: {len(timeline.get('events', []))}")
    for ev in timeline.get('events', []):
        print(f"   - [{ev['timestamp']}] {ev['event_type']}")

    # 4. Get Campaign Graph
    print(f"\n--- 4. GET /{campaign_id}/graph ---")
    res_graph = requests.get(f"{BASE_URL}/{campaign_id}/graph")
    graph = res_graph.json()
    print(f"✅ Graph retrieved! Nodes: {len(graph.get('nodes', []))} | Edges: {len(graph.get('edges', []))}")
    
    print("\n🎉 MILESTONE 7 END-TO-END VERIFICATION COMPLETE!")

if __name__ == "__main__":
    run_e2e_campaign_test()
