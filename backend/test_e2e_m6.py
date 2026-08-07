import requests
import json

def run_e2e_m6_verification():
    print('=== THREATLENS MILESTONE 6 E2E HEALTH CHECK ===')
    indicator = "https://m6-final-e2e-test.com"
    
    # 1. POST: Evaluate Risk & Persist
    print('\n--- 1. Testing Core Risk Pipeline (Evaluate, Score, Explain, Persist) ---')
    payload = {
        "indicator": indicator,
        "indicator_type": "url",
        "resolved_observations": {
            "domain_age_days": 5,
            "ssl_valid": False,
            "virustotal_verdict": "malicious",
            "has_login_form": True
        },
        "overall_confidence": "high",
        "metadata_json": {}
    }
    
    post_res = requests.post('http://127.0.0.1:8000/api/v1/risk/evaluate', json=payload)
    if post_res.status_code == 200:
        data = post_res.json()
        print('✅ Pipeline executed successfully!')
        print(f"   Final Score: {data.get('overall_score')}/100 | Severity: {data.get('severity')}")
        print(f"   Total Recommendations: {len(data.get('recommendations', []))}")
    else:
        print('❌ Pipeline failed:', post_res.text)
        return

    # 2. GET: Retrieve Persisted Risk Assessment
    print(f'\n--- 2. Testing DB Persistence (GET /api/v1/risk/{indicator}) ---')
    encoded_indicator = requests.utils.quote(indicator, safe='')
    get_res = requests.get(f'http://127.0.0.1:8000/api/v1/risk/{encoded_indicator}')
    
    if get_res.status_code == 200 and len(get_res.json()) > 0:
        record = get_res.json()[0]
        print(f"✅ Record successfully retrieved from PostgreSQL!")
        print(f"   Database ID: {record.get('id')}")
        print(f"   Stored Explanation Snippet: {record.get('explanation')[:60]}...")
    else:
        print('❌ Retrieval failed:', get_res.text)

if __name__ == '__main__':
    run_e2e_m6_verification()
