import json
from app.services.risk_engine.service import RiskScoringService
from app.services.unified_evidence.models import UnifiedEvidence, EvidenceMetadata

def test_weighted_risk_calculation():
    print('--- Testing Risk Calculation Engine ---')
    
    # 1. Create a proper UnifiedEvidence Pydantic instance for a highly suspicious domain
    unified_evidence = UnifiedEvidence(
        indicator="https://secure-login-update-now.com",
        indicator_type="url",
        resolved_observations={
            "domain_age_days": 2,          # young age -> +25 (TLS or age anomaly)
            "ssl_valid": False,            # invalid TLS -> (covered by TLS/age OR check)
            "mx_records": [],              # Missing MX + intent keyword -> +25 points
            "virustotal_verdict": "malicious" # VT match -> +30 points
        },
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(
            item_confidences={
                "virustotal_verdict": "high",
                "domain_age_days": "medium"
            }
        )
    )

    service = RiskScoringService()
    
    try:
        risk_score = service.calculate_risk(unified_evidence)
        
        print(f"\n[+] Indicator: {risk_score.indicator}")
        print(f"[+] Final Risk Score: {risk_score.overall_score:.1f}/100")
        print(f"[+] Assigned Severity: {risk_score.severity.value.upper()}")
        print(f"[+] Factors Triggered: {risk_score.factor_count}")
        
        print("\n[+] Explainable Breakdown:")
        breakdown_dict = risk_score.breakdown.model_dump()
        for category, factors in breakdown_dict.items():
            if factors:
                print(f"\n  [{category.upper()}]")
                for factor in factors:
                    print(f"    - {factor['name']} (+{factor['score_contribution']} pts): {factor['description']}")
                    
        print(f"\n[+] Summary Explanation:\n    {risk_score.explanation}")
        assert risk_score.overall_score >= 89.0, "Should be CRITICAL"

    except Exception as e:
        print(f"❌ Engine crashed during calculation: {e}")
        raise e

def test_dynamic_telemetry_baseline():
    print('\n--- Testing Dynamic Telemetry Baseline (SAFE Score Default) ---')
    
    # Test case 1: Healthy legitimate domain should score SAFE (0 - 20)
    evidence_healthy = UnifiedEvidence(
        indicator="https://google.com",
        indicator_type="url",
        resolved_observations={
            "domain_age_days": 10000,
            "ssl_valid": True,
            "tls_issuer": "Google Trust Services",
            "mx_records": ["aspmx.l.google.com"],
            "ns_records": ["ns1.google.com"],
            "virustotal_verdict": "clean"
        },
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    
    service = RiskScoringService()
    try:
        score_healthy = service.calculate_risk(evidence_healthy)
        
        print(f"[+] Healthy Indicator: {score_healthy.indicator}")
        print(f"[+] Final Risk Score: {score_healthy.overall_score:.1f}/100 (Expected: 0.0 - 20.0)")
        print(f"[+] Assigned Severity: {score_healthy.severity.value.upper()}")
        
        assert 0.0 <= score_healthy.overall_score <= 20.0, "Healthy domain should score SAFE (0-20)"
        assert score_healthy.severity.value == "safe", "Should be SAFE severity"
        print("[+] Legitimate healthy domain baseline test passed successfully!")
    except Exception as e:
        print(f"❌ Legitimate healthy domain baseline test crashed: {e}")
        raise e

    # Test case 2: Spoofed domain with anomalies should accumulate points dynamically
    evidence_suspicious = UnifiedEvidence(
        indicator="https://vardhaman-erp-login.com",
        indicator_type="url",
        resolved_observations={
            "domain_age_days": 15,         # < 30 days -> +25 points (TLS/age anomaly)
            "ssl_valid": False,            # Invalid TLS -> (covered by TLS/age OR check)
            "mx_records": [],              # Missing MX + sensitive keywords -> +25 points
        },
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    try:
        score_susp = service.calculate_risk(evidence_suspicious)
        
        print(f"\n[+] Suspicious Indicator: {score_susp.indicator}")
        print(f"[+] Final Risk Score: {score_susp.overall_score:.1f}/100 (Expected: >= 71.0)")
        print(f"[+] Assigned Severity: {score_susp.severity.value.upper()}")
        for category, factors in score_susp.breakdown.model_dump().items():
            if factors:
                for factor in factors:
                    print(f"    - [{category.upper()}] {factor['name']}: {factor['description']}")
                    
        assert score_susp.overall_score >= 71.0, "Should score >= 71.0 (HIGH/CRITICAL)"
        print("[+] Spoofed domain dynamic accumulation test passed successfully!")
    except Exception as e:
        print(f"❌ Spoofed domain dynamic accumulation test crashed: {e}")
        raise e

def test_microsoft_brand_impersonation():
    print('\n--- Testing Microsoft Brand Impersonation (Strict Stopping Condition) ---')
    
    # Test case: login.microsoft-auth-verify.com
    # Combination of Brand Impersonation (+40), Missing MX on sensitive (+25), TLS/Age (+25), structure (+15) -> 100.0 (CRITICAL)
    evidence = UnifiedEvidence(
        indicator="https://login.microsoft-auth-verify.com/login.html",
        indicator_type="url",
        resolved_observations={}, # Empty telemetry implies Missing TLS and Missing MX
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    
    service = RiskScoringService()
    try:
        score = service.calculate_risk(evidence)
        print(f"[+] Indicator: {score.indicator}")
        print(f"[+] Final Risk Score: {score.overall_score:.1f}/100 (Expected: 100)")
        print(f"[+] Assigned Severity: {score.severity.value.upper()}")
        
        all_factors = score.breakdown.all_factors()
        for factor in all_factors:
            print(f"  - {factor.name} (+{factor.score_contribution} pts)")
            
        assert score.overall_score >= 71.0, "Microsoft spoof target must score >= 71.0 (HIGH/CRITICAL)"
        assert any(f.name == "Generalized Phishing Impersonation Penalty" for f in all_factors), "Missing brand+intent penalty"
        assert any(f.name == "TLS Anomaly or Young Domain Age" for f in all_factors), "Missing TLS/Age factor"
        assert any(f.name == "Missing MX Records on Sensitive Target" for f in all_factors), "Missing MX Records factor"
        print("[+] Microsoft Brand Impersonation check passed successfully!")
    except Exception as e:
        print(f"❌ Microsoft Brand Impersonation check crashed: {e}")
        raise e

def test_college_whitelisting():
    print('\n--- Testing Official Domain Whitelisting ---')
    service = RiskScoringService()
    evidence = UnifiedEvidence(
        indicator="https://vardhaman.org",
        indicator_type="url",
        resolved_observations={},
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    try:
        score = service.calculate_risk(evidence)
        print(f"[+] Indicator: {score.indicator}")
        print(f"[+] Final Risk Score: {score.overall_score:.1f}/100 (Expected: 0.0)")
        assert score.overall_score == 0.0
        print("[+] Official college whitelisting test passed successfully!")
    except Exception as e:
        print(f"❌ Official college whitelisting test crashed: {e}")
        raise e

def test_google_phishing_no_calibration():
    print('\n--- Testing Google Phishing (Without Confidence Calibration Penalty) ---')
    evidence = UnifiedEvidence(
        indicator="https://accounts-google-verify-secure.net",
        indicator_type="url",
        resolved_observations={}, # Empty telemetry
        sources=[],
        overall_confidence="unknown", # Confidence is unknown/low, previously halved the score!
        metadata=EvidenceMetadata(item_confidences={})
    )
    service = RiskScoringService()
    try:
        score = service.calculate_risk(evidence)
        print(f"[+] Indicator: {score.indicator}")
        print(f"[+] Final Risk Score: {score.overall_score:.1f}/100 (Expected: 90 - 100)")
        print(f"[+] Assigned Severity: {score.severity.value.upper()}")
        assert 90.0 <= score.overall_score <= 100.0, "Phishing domain must score 90-100 CRITICAL/HIGH even with unknown confidence"
        print("[+] Google Phishing without calibration test passed successfully!")
    except Exception as e:
        print(f"❌ Google Phishing without calibration test crashed: {e}")
        raise e

if __name__ == '__main__':
    test_weighted_risk_calculation()
    test_dynamic_telemetry_baseline()
    test_microsoft_brand_impersonation()
    test_college_whitelisting()
    test_google_phishing_no_calibration()
