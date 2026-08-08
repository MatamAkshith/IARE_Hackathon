import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_auto_correlation():
    print("[*] 1. Authenticating as admin...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"user_id": "admin", "passkey": "Admin@123"})
    if login_res.status_code != 200:
        print(f"[!] Login failed: {login_res.text}")
        sys.exit(1)
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("[*] 2. Registering a test domain...")
    domain_res = requests.post(f"{BASE_URL}/domains/", headers=headers, json={"url": "automatic-correlation-engine-domain.com"})
    if domain_res.status_code not in (200, 201):
        print(f"[!] Domain registration failed: {domain_res.text}")
        sys.exit(1)
    domain_id = domain_res.json()["id"]
    
    print("[*] 3. Creating a new pending scan...")
    scan_res = requests.post(f"{BASE_URL}/scans", headers=headers, json={"domain_id": domain_id, "status": "pending"})
    if scan_res.status_code != 201:
        print(f"[!] Scan creation failed: {scan_res.text}")
        sys.exit(1)
    scan_id = scan_res.json()["id"]
    print(f"[+] Scan #{scan_id} created with pending status.")
    
    # Simulate processing by creating UnifiedEvidence
    print("[*] 4. Processing evidence...")
    evidence_res = requests.post(f"{BASE_URL}/unified-evidence/process", headers=headers, json={
        "indicator": "automatic-correlation-engine-domain.com",
        "internal_data": {
            "ip_address": "198.51.100.42",
            "ssl_cert_serial": "999888777666",
            "page_title": "Microsoft Login Authentication Portal"
        },
        "external_data": {},
        "save_to_db": True
    })
    if evidence_res.status_code != 200:
        print(f"[!] Evidence processing failed: {evidence_res.text}")
        sys.exit(1)
        
    # Simulate completion by setting status to completed
    print("[*] 5. Updating scan status to COMPLETED...")
    update_res = requests.put(f"{BASE_URL}/scans/{scan_id}", headers=headers, json={"status": "completed"})
    if update_res.status_code != 200:
        print(f"[!] Scan update failed: {update_res.text}")
        sys.exit(1)
        
    updated_scan = update_res.json()
    print(f"[+] Scan status update returned: {updated_scan}")
    
    # Assertions
    print("[*] 6. Verifying campaign attribution...")
    campaign_name = updated_scan.get("campaign_name")
    campaign_uid = updated_scan.get("campaign_uid")
    
    if not campaign_name:
        print("[!] Validation FAILURE: Campaign was not automatically attributed (campaign_name is None).")
        sys.exit(1)
        
    print(f"[+] SUCCESS! Auto-attributed to Campaign Name: '{campaign_name}' (UID: {campaign_uid})")
    
if __name__ == "__main__":
    test_auto_correlation()
