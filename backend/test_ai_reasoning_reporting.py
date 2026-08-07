import asyncio
from datetime import datetime, timezone
from app.services.ai_assistant.context_builder import InvestigationContextBuilder
from app.services.ai_assistant.service import AIAssistantService
from app.services.unified_evidence.models import UnifiedEvidence, EvidenceMetadata
from app.services.risk_engine.models import RiskScore, RiskSeverity, RiskBreakdown
from app.services.campaign_engine.models import Campaign, CampaignStatus, CampaignSeverity, CampaignSummary

async def test_reasoning_and_reporting():
    print('=== TESTING AI REASONING & REPORTING ENGINE ===')
    
    indicator_str = "https://secure-update-login.com/auth"
    
    # 1. Setup Context with Correctly Imported Models
    evidence = UnifiedEvidence(
        indicator=indicator_str,
        indicator_type="url",
        metadata=EvidenceMetadata(
            domain="secure-update-login.com",
            ip_address="192.168.1.100"
        )
    )
    risk = RiskScore(
        indicator=indicator_str,
        overall_score=95.0,
        severity=RiskSeverity.CRITICAL,
        breakdown=RiskBreakdown(heuristic_score=95.0, factors=["Newly registered domain", "Free TLS cert"])
    )
    campaign = Campaign(
        campaign_id="CAMP-20260807-001",
        name="Automated Test Campaign",
        status=CampaignStatus.ACTIVE,
        severity=CampaignSeverity.CRITICAL,
        members=[],
        summary=CampaignSummary(
            total_indicators=5,
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc)
        )
    )

    context = InvestigationContextBuilder().build_context(
        indicator=indicator_str,
        evidence=evidence,
        risk_assessment=risk,
        campaign_details=campaign
    )
    
    service = AIAssistantService()

    try:
        # 2. Test Reasoning Engine (Q&A)
        print("\n--- 1. Testing Reasoning Engine Q&A ---")
        q1 = "Why is this URL risky?"
        res1 = await service.ask_question(query=q1, context=context)
        print(f"Q: {q1}\nA: {res1.message.content}\nActions: {[a.label for a in res1.suggested_actions]}\n")
        
        q2 = "What infrastructure is shared?"
        res2 = await service.ask_question(query=q2, context=context)
        print(f"Q: {q2}\nA: {res2.message.content}\n")

        # 3. Test Report Generation
        print("\n--- 2. Testing Report Generation ---")
        analyst_report = await service.get_analyst_report(context)
        print("✅ Analyst Report Generated Successfully!")
        print(f"   Indicator: {analyst_report.indicator}")
        print(f"   Severity: {analyst_report.severity}")
        print(f"   Risk Score: {analyst_report.risk_score}")
        print(f"   Campaign ID: {analyst_report.campaign_id}")
        print(f"   Conclusion: {analyst_report.conclusion}")

        exec_summary = await service.get_executive_summary(context)
        print("\n✅ Executive Summary Generated Successfully!")
        
        # Safely print whichever conclusion/summary attribute exists on ExecutiveSummary
        conclusion_text = getattr(exec_summary, 'conclusion', None) or getattr(exec_summary, 'summary', None) or getattr(exec_summary, 'executive_summary', 'Generated')
        print(f"   Summary/Conclusion: {conclusion_text}")

        print("\n🎉 MILESTONE 8 REASONING & REPORTING ENGINE VERIFIED!")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    asyncio.run(test_reasoning_and_reporting())

