import requests
import json

def test_risk_api_and_persistence():
    print('=== TESTING RISK ENGINE API & PERSISTENCE ===')
    
    # 1. POST: Evaluate Risk & Generate Recommendations
    print('\n--- 1. POST /api/v1/risk/evaluate ---')
    payload = {
        "indicator": "https://urgent-update-secure-auth.com",
        "indicator_type": "url",
        "resolved_observations": {
            "domain_age_days": 1,
            "ssl_valid": False,
            "virustotal_verdict": "malicious"
        },
        "overall_confidence": "high",
        "metadata_json": {}
    }
    
    post_res = requests.post('http://127.0.0.1:8000/api/v1/risk/evaluate', json=payload)
    if post_res.status_code == 200:
        data = post_res.json()
        print(f"✅ Risk Evaluated & Persisted!")
        print(f"   Score: {data.get('overall_score')}/100 | Severity: {data.get('severity')}")
        print("\n   Recommendations Generated:")
        for rec in data.get('recommendations', []):
            print(f"    - [{rec.get('priority').upper()}] {rec.get('action')}: {rec.get('description')}")
    else:
        print('❌ Evaluation failed:', post_res.text)
        return

    # 2. GET: Retrieve from Database
    print('\n--- 2. GET /api/v1/risk/{indicator} ---')
    encoded_indicator = requests.utils.quote("https://urgent-update-secure-auth.com", safe='')
    get_res = requests.get(f'http://127.0.0.1:8000/api/v1/risk/{encoded_indicator}')
    
    if get_res.status_code == 200 and len(get_res.json()) > 0:
        db_record = get_res.json()[0]
        print(f"✅ Record successfully fetched from PostgreSQL!")
        print(f"   Stored Explanation: {db_record.get('explanation')}")
    else:
        print('❌ Retrieval failed:', get_res.text)

if __name__ == '__main__':
    test_risk_api_and_persistence()
