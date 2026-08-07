import json
from app.services.campaign_engine.service import CampaignCorrelationService

def test_campaign_similarity_matching():
    print("=== TESTING CAMPAIGN SIMILARITY ENGINE (Stage 7.2) ===")
    
    # 1. Instantiate service
    service = CampaignCorrelationService()
    
    # 2. Setup mock evidence A (phishing site A)
    evidence_a = {
        "indicator": "https://paypal-update-login.com",
        "indicator_type": "url",
        "ip_address": "203.0.113.50",
        "autonomous_system_number": "AS12345",
        "a_records": ["203.0.113.50", "203.0.113.51"],
        "tls_serial": "999888777666",
        "tls_issuer": "Let's Encrypt",
        "tls_subject": "paypal-update-login.com",
        "registrar": "Namecheap Inc.",
        "org": "Redacted for privacy",
        "domain_creation_date": "2026-08-05T12:00:00Z",
        "page_title": "Confirm and verify your account",
        "structural_hash": "a1b2c3d4e5",
        "forms_count": 2
    }

    # 3. Setup mock evidence B (correlated phishing site B - sharing IP, ASN, Cert Serial, and structure hash)
    evidence_b = {
        "indicator": "https://paypal-security-check.com",
        "indicator_type": "url",
        "ip_address": "203.0.113.50",
        "autonomous_system_number": "AS12345",
        "a_records": ["203.0.113.50"],
        "tls_serial": "999888777666",
        "tls_issuer": "Let's Encrypt",
        "tls_subject": "paypal-security-check.com",
        "registrar": "GoDaddy.com LLC",
        "org": "Redacted for privacy",
        "domain_creation_date": "2026-08-06T12:00:00Z",
        "page_title": "Secure portal login",
        "structural_hash": "a1b2c3d4e5",
        "forms_count": 2
    }

    # 4. Setup mock evidence C (non-correlated benign domain)
    evidence_c = {
        "indicator": "https://legitimate-shop.com",
        "indicator_type": "url",
        "ip_address": "8.8.8.8",
        "autonomous_system_number": "AS15169",
        "tls_serial": "111222333",
        "tls_issuer": "DigiCert Inc",
        "tls_subject": "legitimate-shop.com",
        "registrar": "MarkMonitor",
        "org": "Legit Shop Corp",
        "domain_creation_date": "2020-01-01T00:00:00Z",
        "page_title": "Shop Online Today",
        "structural_hash": "zzzzzzzzzz",
        "forms_count": 0
    }

    print("\n--- Test 1: Correlated Sites (A vs B) ---")
    res_ab = service.evaluate_link(evidence_a, evidence_b)
    print(f"Is Correlated: {res_ab.is_correlated}")
    print(f"Match Score:   {res_ab.match_score:.2f} ({res_ab.match_score * 100:.0f}%)")
    print("Matched Evidence:")
    for hit in res_ab.evidence:
        print(f"  - [{hit.type.upper()}] (value='{hit.value}') -> {hit.description}")
        
    # Check that A and B are correlated
    assert res_ab.is_correlated is True
    # Expected points:
    # shared_ip: 25
    # shared_asn: 5
    # shared_dns_records: 10
    # shared_tls_serial: 20
    # shared_tls_issuer: 5
    # shared_html_structure_hash: 5
    # shared_forms_count: 2
    # Total = 72 points / 100 = 0.72 match_score
    assert abs(res_ab.match_score - 0.72) < 0.001

    print("\n--- Test 2: Non-Correlated Sites (A vs C) ---")
    res_ac = service.evaluate_link(evidence_a, evidence_c)
    print(f"Is Correlated: {res_ac.is_correlated}")
    print(f"Match Score:   {res_ac.match_score:.2f} ({res_ac.match_score * 100:.0f}%)")
    print("Matched Evidence:")
    for hit in res_ac.evidence:
        print(f"  - [{hit.type.upper()}] (value='{hit.value}') -> {hit.description}")
        
    assert res_ac.is_correlated is False
    assert res_ac.match_score == 0.0
    
    print("\n✅ Campaign similarity engine verification tests passed successfully!")

if __name__ == "__main__":
    test_campaign_similarity_matching()
