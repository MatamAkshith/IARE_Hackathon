import requests
import json

def run_calibration_tests():
    print('=== TESTING RISK ENGINE CALIBRATION & EDGE CASES ===')
    
    # Test Case 1: Low Confidence Penalty
    print('\n--- Test 1: Low Confidence Adjustment ---')
    payload_low_conf = {
        "indicator": "https://low-confidence-test.com",
        "resolved_observations": {
            "domain_age_days": 1,
            "virustotal_verdict": "malicious"
        },
        "overall_confidence": "low"
    }
    res1 = requests.post('http://127.0.0.1:8000/api/v1/risk/evaluate', json=payload_low_conf)
    if res1.status_code == 200:
        data = res1.json()
        print(f"✅ Evaluated successfully! Score: {data.get('overall_score')}/100 (Severity: {data.get('severity')})")
        print(f"   Note: Score should be penalized/reduced due to 'low' confidence.")
    else:
        print('❌ Test 1 failed:', res1.text)

    # Test Case 2: Empty/Missing Evidence (Graceful Degradation)
    print('\n--- Test 2: Empty Evidence ---')
    payload_empty = {
        "indicator": "https://empty-evidence-test.com",
        "resolved_observations": {},
        "overall_confidence": "high"
    }
    res2 = requests.post('http://127.0.0.1:8000/api/v1/risk/evaluate', json=payload_empty)
    if res2.status_code == 200:
        data = res2.json()
        print(f"✅ Handled gracefully! Score: {data.get('overall_score')}/100 (Severity: {data.get('severity')})")
        if data.get('overall_score') == 0.0:
            print("   Correctly prevented division-by-zero and returned SAFE default.")
    else:
        print('❌ Test 2 failed:', res2.text)

    # Test Case 3: Extreme Evidence (Boundary Enforcement)
    print('\n--- Test 3: Extreme Evidence Boundary Check ---')
    payload_extreme = {
        "indicator": "https://extreme-test.com",
        "resolved_observations": {
            "domain_age_days": 0,
            "ssl_valid": False,
            "virustotal_verdict": "malicious",
            "has_login_form": True,
            "abuseipdb_score": 100
        },
        "overall_confidence": "high"
    }
    res3 = requests.post('http://127.0.0.1:8000/api/v1/risk/evaluate', json=payload_extreme)
    if res3.status_code == 200:
        data = res3.json()
        score = data.get('overall_score')
        print(f"✅ Evaluated successfully! Score: {score}/100 (Severity: {data.get('severity')})")
        if score <= 100.0:
            print("   Score correctly clamped at or below 100.0 (No overflow).")
    else:
        print('❌ Test 3 failed:', res3.text)

if __name__ == '__main__':
    run_calibration_tests()
