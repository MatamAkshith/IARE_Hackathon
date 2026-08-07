from fastapi.testclient import TestClient
from app.main import app

def test_campaigns_e2e_api():
    print("=== TESTING CAMPAIGN API ENDPOINTS E2E (Stage 7.5/7.6) ===")
    
    client = TestClient(app)
    
    # 1. Trigger correlation / correlate endpoint
    evidence_a = {
        "indicator": "https://threat-site-a.com",
        "indicator_type": "url",
        "ip_address": "192.0.2.1",
        "cert_serial": "AABBCCDD11",
        "page_title": "Fake Office Portal Login Page"
    }
    
    print("\n--- Sending Correlate Request for Indicator A ---")
    response = client.post("/api/v1/campaigns/correlate", json=evidence_a)
    assert response.status_code == 200
    data = response.json()
    print("Response JSON:")
    print(f"  Action: {data['action']}")
    print(f"  Campaign ID: {data['campaign']['campaign_id']}")
    print(f"  Members count: {len(data['campaign']['members'])}")
    
    assert data["action"] == "created"
    campaign_id = data["campaign"]["campaign_id"]
    
    # 2. Add another correlated indicator to join the campaign
    evidence_b = {
        "indicator": "https://threat-site-b.com",
        "indicator_type": "url",
        "ip_address": "192.0.2.1",       # Shared IP (25 points)
        "cert_serial": "AABBCCDD11",      # Shared Cert Serial (20 points)
        "page_title": "Fake Office Portal Login Page"
    }
    
    print("\n--- Sending Correlate Request for Indicator B (Correlated with A) ---")
    response_b = client.post("/api/v1/campaigns/correlate", json=evidence_b)
    assert response_b.status_code == 200
    data_b = response_b.json()
    print("Response JSON:")
    print(f"  Action: {data_b['action']}")
    print(f"  Target Campaign ID: {data_b['campaign']['campaign_id']}")
    print(f"  Members count: {len(data_b['campaign']['members'])}")
    
    assert data_b["action"] == "joined"
    assert data_b["campaign"]["campaign_id"] == campaign_id
    assert len(data_b["campaign"]["members"]) == 2

    # 3. Retrieve campaigns list
    print("\n--- GET /api/v1/campaigns (List Campaigns) ---")
    list_response = client.get("/api/v1/campaigns")
    assert list_response.status_code == 200
    campaigns = list_response.json()
    print(f"  Total Campaigns returned: {len(campaigns)}")
    assert len(campaigns) >= 1
    
    # 4. Retrieve campaign details
    print(f"\n--- GET /api/v1/campaigns/{{campaign_id}} (Campaign: {campaign_id}) ---")
    detail_response = client.get(f"/api/v1/campaigns/{campaign_id}")
    assert detail_response.status_code == 200
    details = detail_response.json()
    assert details["campaign_id"] == campaign_id
    print(f"  Name: {details['name']}")
    print(f"  Status: {details['status']}")
    print(f"  Severity: {details['severity']}")
    
    # 5. Retrieve graph
    print(f"\n--- GET /api/v1/campaigns/{{campaign_id}}/graph ---")
    graph_response = client.get(f"/api/v1/campaigns/{campaign_id}/graph")
    assert graph_response.status_code == 200
    graph = graph_response.json()
    print(f"  Nodes count: {len(graph['nodes'])}")
    print(f"  Edges count: {len(graph['edges'])}")
    assert len(graph["nodes"]) > 0
    
    # 6. Retrieve timeline
    print(f"\n--- GET /api/v1/campaigns/{{campaign_id}}/timeline ---")
    timeline_response = client.get(f"/api/v1/campaigns/{campaign_id}/timeline")
    assert timeline_response.status_code == 200
    timeline = timeline_response.json()
    print(f"  Events count: {len(timeline['events'])}")
    assert len(timeline["events"]) > 0

    print("\n✅ E2E Campaign Correlation persistence and REST API endpoints validated successfully!")

if __name__ == "__main__":
    test_campaigns_e2e_api()
