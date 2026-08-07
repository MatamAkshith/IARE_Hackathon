import json
from app.services.campaign_engine.service import CampaignCorrelationService

def test_similarity_correlation():
    print('=== TESTING CAMPAIGN CORRELATION ENGINE ===')
    
    # Evidence A (Flat dictionary as expected by correlators)
    evidence_a = {
        "indicator": "https://secure-update-login.com",
        "ip_address": "192.168.1.100",
        "cert_issuer": "Let's Encrypt Authority X3",
        "cert_serial": "03A1B2C3D4E5F67890",
        "registrar": "NameCheap, Inc.",
        "page_title": "Secure Customer Portal Verification",
        "domain_creation_date": "2026-08-01"
    }

    # Evidence B (Historical Investigation with shared infrastructure/attributes)
    evidence_b = {
        "indicator": "https://verify-account-now.net",
        "ip_address": "192.168.1.100",           # MATCH: Shared IP (InfrastructureCorrelator)
        "cert_issuer": "Let's Encrypt Authority X3",   # MATCH: Shared Issuer (TlsCorrelator)
        "cert_serial": "03A1B2C3D4E5F67890",   # MATCH: Shared Serial (TlsCorrelator)
        "registrar": "GoDaddy.com, LLC",         # NO MATCH
        "page_title": "Secure Customer Portal Verification", # MATCH: Shared Title (HtmlCorrelator)
        "domain_creation_date": "2026-08-01"   # MATCH: Shared Registration Date (WhoisCorrelator)
    }

    service = CampaignCorrelationService()

    try:
        print("\n--- Evaluating Link Between Evidence A and Evidence B ---")
        result = service.evaluate_link(evidence_a, evidence_b)
        
        print(f"✅ Correlation Evaluated!")
        print(f"   Is Correlated: {result.is_correlated}")
        print(f"   Match Score: {result.match_score * 100:.1f}%")
        print(f"   Total Evidence Matches: {len(result.evidence)}")
        
        if result.evidence:
            print("\n--- Overlapping Evidence Detected ---")
            for ev in result.evidence:
                print(f"  - [{ev.type.upper()}] (Confidence: {ev.confidence}): {ev.description}")

    except Exception as e:
        print(f"❌ Correlation test failed: {e}")

if __name__ == '__main__':
    test_similarity_correlation()
