import requests
import json

def run_e2e_verification():
    print('=== THREATLENS MILESTONE 5 E2E HEALTH CHECK ===')
    indicator = 'https://e2e-final-test.com'
    
    # 1. POST: Process and Merge Evidence
    print('\n--- 1. Testing Core Pipeline (Merge, Normalize, Score, Timeline, DB Save) ---')
    payload = {
        'indicator': indicator,
        'internal_data': {'has_login_form': True, 'domain_age_days': 2, 'ssl_valid': False},
        'external_data': {'virustotal_verdict': 'malicious', 'domain_age_days': 1000, 'abuseipdb_score': 85}
    }
    
    post_res = requests.post('http://127.0.0.1:8000/api/v1/unified-evidence/process', json=payload)
    if post_res.status_code == 200:
        print('✅ Pipeline executed successfully!')
    else:
        print('❌ Pipeline failed:', post_res.text)
        return

    # 2. GET: Retrieve Persisted Evidence
    print(f'\n--- 2. Testing DB Persistence (GET /api/v1/unified-evidence/{indicator}) ---')
    get_res = requests.get(f'http://127.0.0.1:8000/api/v1/unified-evidence/{indicator}')
    if get_res.status_code == 200 and len(get_res.json()) > 0:
        record = get_res.json()[0]
        print(f"✅ Record retrieved! Overall Confidence: {record.get('overall_confidence')}")
        print(f"✅ Resolved Keys: {list(record.get('resolved_observations', {}).keys())}")
    else:
        print('❌ Retrieval failed:', get_res.text)
        return

    # 3. GET: Retrieve Timeline/Audit Trail
    print(f'\n--- 3. Testing Traceability (GET /api/v1/unified-evidence/timeline?indicator={indicator}) ---')
    timeline_res = requests.get('http://127.0.0.1:8000/api/v1/unified-evidence/timeline', params={'indicator': indicator})
    if timeline_res.status_code == 200:
        events = timeline_res.json().get('events', [])
        print(f'✅ Timeline retrieved! Total Events Tracked: {len(events)}')
        if events:
            print(f"   Last Event: {events[-1].get('event_type')} - {events[-1].get('description')}")
    else:
        print('❌ Timeline failed:', timeline_res.text)

if __name__ == '__main__':
    run_e2e_verification()
