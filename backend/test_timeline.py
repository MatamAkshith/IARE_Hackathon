import requests
import json

def test_evidence_timeline():
    print('--- 1. Testing POST /api/v1/unified-evidence/process ---')
    payload = {
        'indicator': 'https://timeline-test.com',
        'internal_data': {'has_login_form': True, 'domain_age_days': 2},
        'external_data': {'virustotal_verdict': 'malicious', 'domain_age_days': 1000}
    }
    
    post_res = requests.post('http://127.0.0.1:8000/api/v1/unified-evidence/process', json=payload)
    if post_res.status_code == 200:
        print('✅ Evidence processed and audit trail generated!')
    else:
        print('❌ Failed to process:', post_res.text)
        return

    print('\n--- 2. Testing GET /api/v1/unified-evidence/timeline?indicator=https://timeline-test.com ---')
    get_res = requests.get('http://127.0.0.1:8000/api/v1/unified-evidence/timeline', params={'indicator': 'https://timeline-test.com'})
    print(f'Status: {get_res.status_code}')
    
    if get_res.status_code == 200:
        timeline_data = get_res.json()
        print('\nChronological Audit Trail Preview:')
        print(json.dumps(timeline_data, indent=2))
    else:
        print(get_res.text)

if __name__ == '__main__':
    test_evidence_timeline()
