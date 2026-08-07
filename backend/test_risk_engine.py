import json
from app.services.risk_engine.service import RiskScoringService
from app.services.unified_evidence.models import UnifiedEvidence, EvidenceMetadata

def test_weighted_risk_calculation():
    print('--- Testing Risk Calculation Engine ---')
    
    # 1. Create a proper UnifiedEvidence Pydantic instance
    unified_evidence = UnifiedEvidence(
        indicator="https://secure-login-update-now.com",
        indicator_type="url",
        resolved_observations={
            "domain_age_days": 2,
            "has_login_form": True,
            "ssl_valid": False,
            "virustotal_verdict": "malicious",
            "abuseipdb_score": 95
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

    except Exception as e:
        print(f"❌ Engine crashed during calculation: {e}")

def test_brand_impersonation_lexical_rule():
    print('\n--- Testing Brand Impersonation Lexical Heuristics ---')
    
    # Test case 1: Target brand + suspicious keyword in domain, empty telemetry
    evidence_empty = UnifiedEvidence(
        indicator="https://login.microsoft-auth-verify.com/login.html",
        indicator_type="url",
        resolved_observations={},
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    
    service = RiskScoringService()
    try:
        score_empty = service.calculate_risk(evidence_empty)
        
        print(f"[+] Indicator: {score_empty.indicator}")
        print(f"[+] Final Risk Score: {score_empty.overall_score:.1f}/100 (Expected: >= 85.0)")
        print(f"[+] Assigned Severity: {score_empty.severity.value.upper()}")
        print(f"[+] Factors Triggered: {score_empty.factor_count}")
        for category, factors in score_empty.breakdown.model_dump().items():
            if factors:
                for factor in factors:
                    print(f"    - [{category.upper()}] {factor['name']}: {factor['description']}")
                    
        assert score_empty.overall_score >= 85.0, "Score should be capped at minimum 85.0"
        assert any(f.name == "Target Brand Impersonation via Lexical Heuristics" for f in score_empty.breakdown.domain_intelligence), "Lexical impersonation factor missing"
        print("[+] Microsoft Brand Impersonation test case passed successfully!")
    except Exception as e:
        print(f"❌ Microsoft Brand Impersonation test crashed: {e}")
        raise e

    # Test case 2: Infosys brand + employee benefits keyword, empty telemetry
    evidence_infosys = UnifiedEvidence(
        indicator="https://infosys-employee-benefits.net",
        indicator_type="url",
        resolved_observations={},
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    
    try:
        score_infosys = service.calculate_risk(evidence_infosys)
        
        print(f"[+] Indicator: {score_infosys.indicator}")
        print(f"[+] Final Risk Score: {score_infosys.overall_score:.1f}/100 (Expected: >= 85.0)")
        print(f"[+] Assigned Severity: {score_infosys.severity.value.upper()}")
        print(f"[+] Factors Triggered: {score_infosys.factor_count}")
        for category, factors in score_infosys.breakdown.model_dump().items():
            if factors:
                for factor in factors:
                    print(f"    - [{category.upper()}] {factor['name']}: {factor['description']}")
                    
        assert score_infosys.overall_score >= 85.0, "Score should be capped at minimum 85.0"
        assert any(f.name == "Target Brand Impersonation via Lexical Heuristics" for f in score_infosys.breakdown.domain_intelligence), "Lexical impersonation factor missing"
        print("[+] Infosys Brand Impersonation test case passed successfully!")
    except Exception as e:
        print(f"❌ Infosys Brand Impersonation test crashed: {e}")
        raise e

    # Test case 3: Official whitelisted college domain
    evidence_whitelisted = UnifiedEvidence(
        indicator="https://vardhaman.org",
        indicator_type="url",
        resolved_observations={},
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    try:
        score_whitelisted = service.calculate_risk(evidence_whitelisted)
        print(f"[+] Indicator: {score_whitelisted.indicator}")
        print(f"[+] Final Risk Score: {score_whitelisted.overall_score:.1f}/100 (Expected: 0.0)")
        print(f"[+] Assigned Severity: {score_whitelisted.severity.value.upper()}")
        assert score_whitelisted.overall_score == 0.0, "Whitelisted domain must score 0.0"
        assert score_whitelisted.severity.value == "safe", "Whitelisted domain must be SAFE"
        print("[+] Whitelisting test case passed successfully!")
    except Exception as e:
        print(f"❌ Whitelisting test crashed: {e}")
        raise e

    # Test case 4: Spoofed college ERP target
    evidence_spoofed = UnifiedEvidence(
        indicator="https://vardhaman-erp-login.com",
        indicator_type="url",
        resolved_observations={},
        sources=[],
        overall_confidence="high",
        metadata=EvidenceMetadata(item_confidences={})
    )
    try:
        score_spoofed = service.calculate_risk(evidence_spoofed)
        print(f"[+] Indicator: {score_spoofed.indicator}")
        print(f"[+] Final Risk Score: {score_spoofed.overall_score:.1f}/100 (Expected: >= 85.0)")
        print(f"[+] Assigned Severity: {score_spoofed.severity.value.upper()}")
        assert score_spoofed.overall_score >= 85.0, "Spoofed ERP domain must score >= 85.0"
        assert score_spoofed.severity.value == "high", "Spoofed ERP domain must be HIGH"
        print("[+] Spoofed college ERP test case passed successfully!")
    except Exception as e:
        print(f"❌ Spoofed college ERP test crashed: {e}")
        raise e

if __name__ == '__main__':
    test_weighted_risk_calculation()
    test_brand_impersonation_lexical_rule()
