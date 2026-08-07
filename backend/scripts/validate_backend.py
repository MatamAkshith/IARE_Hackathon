#!/usr/bin/env python3
"""
Backend Validation Script — Phase B (Stage B.2)

Pings the running local FastAPI backend and validates endpoint health,
campaign graphs, scans lists, and AI reports responses. Asserts that data
integrity is maintained and structures align with Pydantic schemas.
"""

import sys
import os

# Adjust python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import httpx
except ImportError:
    print("[!] Error: 'httpx' is not installed in the python path. Please use virtualenv.")
    sys.exit(1)

BASE_URL = "http://localhost:8000/api/v1"


def run_validation():
    print(f"[*] Starting system validation against backend: {BASE_URL}")

    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        # 1. Health readiness checks
        print("[*] 1. Checking API Readiness endpoint `/health/ready`...")
        res = client.get(f"{BASE_URL}/health/ready")
        assert res.status_code == 200, f"Readiness check failed with {res.status_code}"
        health = res.json()
        assert health["status"] == "ok" or health["status"] == "ready", "Status not OK"
        assert health["checks"]["database"] == "ok", "Database connection not healthy"
        print("[+] Health Readiness Check: PASS")

        # 2. Scans queue list
        print("[*] 2. Checking Scans List endpoint `/scans`...")
        res = client.get(f"{BASE_URL}/scans/")
        assert res.status_code == 200, f"Scans list query failed: {res.status_code}"
        scans = res.json()
        assert len(scans) >= 15, f"Expected at least 15 seeded scan records, found: {len(scans)}"
        print(f"[+] Scans List: PASS (Found {len(scans)} records)")

        # Get first completed scan for detail checks
        completed_scan = next((s for s in scans if s["status"] == "completed"), None)
        assert completed_scan is not None, "No completed scan found to validate details"
        scan_id = completed_scan["id"]

        # Get corresponding domain
        res = client.get(f"{BASE_URL}/domains/{completed_scan['domain_id']}")
        assert res.status_code == 200
        domain_url = res.json()["url"]

        # 3. Unified Evidence records
        print(f"[*] 3. Checking Unified Evidence query for indicator `{domain_url}`...")
        res = client.get(f"{BASE_URL}/unified-evidence/{domain_url}")
        assert res.status_code == 200, f"Unified evidence fetch failed: {res.status_code}"
        evidence_list = res.json()
        assert len(evidence_list) > 0, "No evidence records returned"
        assert "resolved_observations" in evidence_list[0], "resolved_observations field missing"
        print("[+] Unified Evidence Fetch: PASS")

        # 4. Risk assessment history
        print(f"[*] 4. Checking Risk Assessment history for indicator `{domain_url}`...")
        res = client.get(f"{BASE_URL}/risk/{domain_url}")
        assert res.status_code == 200, f"Risk assessment query failed: {res.status_code}"
        risk_list = res.json()
        assert len(risk_list) > 0, "No risk records returned"
        assert "overall_score" in risk_list[0], "overall_score field missing"
        print("[+] Risk Assessment History: PASS")

        # 5. Campaigns overview list
        print("[*] 5. Checking Campaigns list `/campaigns`...")
        res = client.get(f"{BASE_URL}/campaigns/")
        assert res.status_code == 200, f"Campaigns query failed: {res.status_code}"
        campaigns = res.json()
        assert len(campaigns) >= 2, f"Expected at least 2 seeded campaigns, found: {len(campaigns)}"
        print("[+] Campaigns List Query: PASS")

        # Check graph for the first campaign
        campaign_id = campaigns[0]["campaign_id"]
        print(f"[*] 6. Checking Campaigns Relationship Graph `/campaigns/{campaign_id}/graph`...")
        res = client.get(f"{BASE_URL}/campaigns/{campaign_id}/graph")
        assert res.status_code == 200, f"Campaign graph query failed: {res.status_code}"
        graph = res.json()
        assert "nodes" in graph and "edges" in graph, "Malformed campaign graph model"
        print(f"[+] Campaigns Graph Topology: PASS (Found {len(graph['nodes'])} nodes, {len(graph['edges'])} edges)")

        # 6. AI Technical Analyst Report
        print(f"[*] 7. Checking AI Analyst Report generation `/ai/report/analyst` for `{domain_url}`...")
        report_req = {
            "indicator": domain_url,
            "evidence": evidence_list[0],
            "risk_assessment": risk_list[0],
            "campaign_details": None
        }
        res = client.post(f"{BASE_URL}/ai/report/analyst", json=report_req)
        assert res.status_code == 200, f"AI Analyst Report generation failed: {res.status_code}"
        report = res.json()
        assert "conclusion" in report, "Analyst report conclusion missing"
        assert "recommendations" in report, "Analyst report recommendations missing"
        print("[+] AI Analyst Technical Report: PASS")

        # 7. AI Executive Summary
        print(f"[*] 8. Checking AI Executive Summary generation `/ai/report/executive` for `{domain_url}`...")
        res = client.post(f"{BASE_URL}/ai/report/executive", json=report_req)
        assert res.status_code == 200, f"AI Executive Summary generation failed: {res.status_code}"
        exec_summary = res.json()
        assert "business_impact" in exec_summary, "Executive summary business impact description missing"
        assert "overall_risk_rating" in exec_summary, "Executive summary risk rating missing"
        print("[+] AI Executive Business Summary: PASS")

    print("[+] ALL SYSTEM INTEGRATION VALIDATION TESTS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as ae:
        print(f"[!] Validation Failure Assertion: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Validation Error: {e}")
        sys.exit(1)
