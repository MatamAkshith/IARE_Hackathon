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
            "domain_age_days": 2,          # < 30 days -> +20 points
            "ssl_valid": False,            # Invalid TLS -> +30 points
            "mx_records": [],              # Missing MX + sensitive keywords -> +30 points
            "virustotal_verdict": "malicious" # VT malicious -> +50 points
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
        assert risk_score.overall_score >= 91.0, "Should be CRITICAL"

    except Exception as e:
        print(f"❌ Engine crashed during calculation: {e}")
        raise e

def test_dynamic_telemetry_baseline():
    print('\n--- Testing Dynamic Telemetry Baseline (SAFE Score Default) ---')
    
    # Test case 1: Healthy legitimate domain should score SAFE (0 - 15)
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
        print(f"[+] Final Risk Score: {score_healthy.overall_score:.1f}/100 (Expected: 0.0 - 15.0)")
        print(f"[+] Assigned Severity: {score_healthy.severity.value.upper()}")
        
        assert 0.0 <= score_healthy.overall_score <= 15.0, "Healthy domain should score SAFE (0-15)"
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
            "domain_age_days": 15,         # < 30 days -> +20 points
            "ssl_valid": False,            # Invalid TLS -> +30 points
            "mx_records": [],              # Missing MX + sensitive keywords -> +30 points
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
    # Combination of Brand Impersonation (+40), Invalid/Missing TLS (+30), and Missing MX (+30) -> 100
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
        
        # Verify the presence of expected factors
        all_factors = score.breakdown.all_factors()
        for factor in all_factors:
            print(f"  - {factor.name} (+{factor.score_contribution} pts)")
            
        assert score.overall_score >= 85.0, "Microsoft spoof target must score >= 85.0"
        assert any(f.name == "Target Brand Impersonation Detected" for f in all_factors), "Missing Target Brand Impersonation factor"
        assert any(f.name == "Invalid or Missing TLS Certificate" for f in all_factors), "Missing TLS Certificate factor"
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

if __name__ == '__main__':
    test_weighted_risk_calculation()
    test_dynamic_telemetry_baseline()
    test_microsoft_brand_impersonation()
    test_college_whitelisting()
