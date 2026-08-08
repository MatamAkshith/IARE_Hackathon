import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_full_secured_workflow():
    print("[*] 1. Authenticating to get token...")
    login_url = f"{BASE_URL}/auth/login"
    res = requests.post(login_url, json={"user_id": "admin", "passkey": "Admin@123"})
    if res.status_code != 200:
        print(f"[!] Authentication failed: {res.status_code}")
        sys.exit(1)
    
    token = res.json()["access_token"]
    print(f"[+] Authentication PASS. Token acquired.")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("[*] 2. Checking stats endpoint...")
    res = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    if res.status_code != 200:
        print(f"[!] Stats failed: {res.status_code}")
        sys.exit(1)
    print(f"[+] Stats PASS: {res.json()['total_scans']} total scans.")
    
    print("[*] 3. Creating domain record...")
    domain_res = requests.post(f"{BASE_URL}/domains/", headers=headers, json={"url": "validate-secured-domain.com"})
    if domain_res.status_code not in (200, 201):
        print(f"[!] Domain creation failed: {domain_res.status_code} {domain_res.text}")
        sys.exit(1)
    domain_id = domain_res.json()["id"]
    print(f"[+] Domain creation PASS. Domain ID: {domain_id}")

    print("[*] 4. Submitting new URL scan...")
    scan_url = f"{BASE_URL}/scans"
    res = requests.post(scan_url, headers=headers, json={"domain_id": domain_id, "status": "pending"})
    if res.status_code != 201:
        print(f"[!] Scan submission failed: {res.status_code} {res.text}")
        sys.exit(1)
    scan_data = res.json()
    print(f"[+] Scan submission PASS. Scan ID: {scan_data['id']}.")

    print("[*] 5. Getting scan details...")
    res = requests.get(f"{BASE_URL}/scans/{scan_data['id']}", headers=headers)
    if res.status_code != 200:
        print(f"[!] Fetch details failed: {res.status_code}")
        sys.exit(1)
    print(f"[+] Fetch details PASS.")
    
    print("[*] 6. Getting campaigns list...")
    res = requests.get(f"{BASE_URL}/campaigns", headers=headers)
    if res.status_code != 200:
        print(f"[!] Campaigns query failed: {res.status_code}")
        sys.exit(1)
    print(f"[+] Campaigns query PASS: {len(res.json())} campaigns.")
    
    print("[+] All secured endpoints respond correctly. Verification PASS.")

if __name__ == "__main__":
    test_full_secured_workflow()
