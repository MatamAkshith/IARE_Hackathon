#!/usr/bin/env python3
"""
Seed Demo Data Script — Phase B (Stage B.1)

Generates 15–20 realistic mock investigation scenarios in the database.
Covers Google, Microsoft, Amazon, PayPal, SBI, and HDFC brand impersonations,
across various threat categories (phishing, typosquatting, expired SSL, redirects).
Links 2 distinct campaigns using both legacy Campaign and new CampaignRecord tables.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Adjust python path to import app package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.domain import Domain
from app.models.campaign import Campaign
from app.models.scan import Scan
from app.models.feature import Feature
from app.models.risk_score import RiskScore
from app.db.models.unified_evidence import UnifiedEvidenceRecord
from app.db.models.risk_assessment import RiskAssessmentRecord
from app.db.models.campaign import CampaignRecord, CampaignMemberRecord


def seed_data():
    db = SessionLocal()
    try:
        print("[*] Purging existing database tables...")
        db.query(CampaignMemberRecord).delete()
        db.query(CampaignRecord).delete()
        db.query(RiskAssessmentRecord).delete()
        db.query(UnifiedEvidenceRecord).delete()
        db.query(RiskScore).delete()
        db.query(Feature).delete()
        db.query(Scan).delete()
        db.query(Campaign).delete()
        db.query(Domain).delete()
        db.commit()
        print("[+] DB Purge Complete.")

        # ──────────────────────────────────────────────────────────────────────
        # 1. Create Campaigns
        # ──────────────────────────────────────────────────────────────────────
        print("[*] Creating campaigns...")
        
        # Legacy Campaign entities
        c1_legacy = Campaign(
            name="CozyBear Impersonation Wave",
            description="Active phishing campaign mimicking Microsoft corporate authentication portals.",
            status="active"
        )
        c2_legacy = Campaign(
            name="Fintech Harvester Syndicate",
            description="Phishing syndicate targeting digital payment wallets (PayPal, Amazon Pay).",
            status="active"
        )
        db.add(c1_legacy)
        db.add(c2_legacy)
        db.commit()

        # New CampaignRecord entities (Stage 7.5)
        c1_record = CampaignRecord(
            campaign_id="CAMP-2026-004",
            name="CozyBear Impersonation Wave",
            status="active",
            severity="critical",
            summary_json={
                "campaignName": "CozyBear Impersonation Wave",
                "campaignId": "CAMP-2026-004",
                "status": "Active",
                "riskLevel": "Critical",
                "confidence": "97%"
            },
            shared_infrastructure_json=[
                {"type": "ssl_cert_serial", "value": "03A1B2C3D4E5F67890", "added_reason": "Identical fake SSL serial deployed."}
            ]
        )
        c2_record = CampaignRecord(
            campaign_id="CAMP-2026-008",
            name="Fintech Harvester Syndicate",
            status="active",
            severity="high",
            summary_json={
                "campaignName": "Fintech Harvester Syndicate",
                "campaignId": "CAMP-2026-008",
                "status": "Active",
                "riskLevel": "High",
                "confidence": "92%"
            },
            shared_infrastructure_json=[
                {"type": "ip_address", "value": "185.230.125.44", "added_reason": "All domains host on same C-class range IP."}
            ]
        )
        db.add(c1_record)
        db.add(c2_record)
        db.commit()

        # ──────────────────────────────────────────────────────────────────────
        # 2. Setup Scenarios
        # ──────────────────────────────────────────────────────────────────────
        scenarios = [
            # CozyBear Campaign (Microsoft lookalikes)
            {
                "url": "secure-microsoft-login-verification.com",
                "brand": "Microsoft",
                "type": "phishing",
                "severity": "critical",
                "score": 92.0,
                "legacy_campaign": c1_legacy,
                "new_campaign_id": "CAMP-2026-004",
                "ip": "185.230.125.44",
                "asn": "AS41235 (FakeNetwork Inc.)",
                "isp": "GlobalHost Corp",
                "registrar": "NameCheap, Inc.",
                "creation_date": "2026-08-03T14:22:00Z",
                "ssl_issuer": "Self Signed (Fake Microsoft CA)",
                "page_title": "Microsoft Secure Login",
                "has_pwd": True,
                "findings": ["Lookalike domain targeting Microsoft.", "Self-signed certificate.", "Active credential form detected."]
            },
            {
                "url": "office365-security-check.net",
                "brand": "Microsoft",
                "type": "phishing",
                "severity": "critical",
                "score": 88.0,
                "legacy_campaign": c1_legacy,
                "new_campaign_id": "CAMP-2026-004",
                "ip": "185.230.125.45",
                "asn": "AS41235 (FakeNetwork Inc.)",
                "isp": "GlobalHost Corp",
                "registrar": "NameCheap, Inc.",
                "creation_date": "2026-08-01T08:15:00Z",
                "ssl_issuer": "Self Signed (Fake Microsoft CA)",
                "page_title": "Office 365 Verification Portal",
                "has_pwd": True,
                "findings": ["Microsoft credential harvesting template.", "Shared nameserver delegation with campaign.", "Self-signed SSL."]
            },
            {
                "url": "microsoft-login-auth.live",
                "brand": "Microsoft",
                "type": "phishing",
                "severity": "critical",
                "score": 84.0,
                "legacy_campaign": c1_legacy,
                "new_campaign_id": "CAMP-2026-004",
                "ip": "185.230.125.46",
                "asn": "AS41235 (FakeNetwork Inc.)",
                "isp": "GlobalHost Corp",
                "registrar": "NameCheap, Inc.",
                "creation_date": "2026-08-04T10:05:00Z",
                "ssl_issuer": "Self Signed (Fake Microsoft CA)",
                "page_title": "Microsoft Account Log In",
                "has_pwd": True,
                "findings": ["Microsoft lookalike keywords.", "Active input forms count: 2.", "Recently registered domain."]
            },

            # Fintech Harvester Syndicate (PayPal / Amazon Pay lookalikes)
            {
                "url": "paypa1-update.com",
                "brand": "PayPal",
                "type": "typosquatting",
                "severity": "high",
                "score": 78.0,
                "legacy_campaign": c2_legacy,
                "new_campaign_id": "CAMP-2026-008",
                "ip": "185.230.125.44",
                "asn": "AS41235 (FakeNetwork Inc.)",
                "isp": "GlobalHost Corp",
                "registrar": "NameCheap, Inc.",
                "creation_date": "2026-08-05T11:30:00Z",
                "ssl_issuer": "Let's Encrypt",
                "page_title": "PayPal Security Update",
                "has_pwd": True,
                "findings": ["Typosquatting targeting PayPal.", "Credential harvesting forms.", "Shared campaign IP."]
            },
            {
                "url": "amazon-verify-checkout.net",
                "brand": "Amazon",
                "type": "phishing",
                "severity": "high",
                "score": 80.0,
                "legacy_campaign": c2_legacy,
                "new_campaign_id": "CAMP-2026-008",
                "ip": "185.230.125.44",
                "asn": "AS41235 (FakeNetwork Inc.)",
                "isp": "GlobalHost Corp",
                "registrar": "NameCheap, Inc.",
                "creation_date": "2026-08-04T09:12:00Z",
                "ssl_issuer": "Let's Encrypt",
                "page_title": "Amazon Pay Portal",
                "has_pwd": True,
                "findings": ["Amazon branding elements lookalike.", "Password field detected.", "Shared campaign IP address."]
            },

            # Financial Institutions (SBI, HDFC bank mimics)
            {
                "url": "sbi-netbanking-verify.in",
                "brand": "SBI",
                "type": "phishing",
                "severity": "critical",
                "score": 95.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "193.109.112.5",
                "asn": "AS55421 (IndiaNet)",
                "isp": "Indian Telecom Corp",
                "registrar": "PublicDomainRegistry",
                "creation_date": "2026-08-06T04:12:00Z",
                "ssl_issuer": "Let's Encrypt",
                "page_title": "State Bank of India Online NetBanking",
                "has_pwd": True,
                "findings": ["Targeting SBI corporate netbanking.", "Credential forms.", "Invalid WHOIS registrar contact info."]
            },
            {
                "url": "hdfcbank-login-secure.co",
                "brand": "HDFC",
                "type": "phishing",
                "severity": "critical",
                "score": 90.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "193.109.112.6",
                "asn": "AS55421 (IndiaNet)",
                "isp": "Indian Telecom Corp",
                "registrar": "PublicDomainRegistry",
                "creation_date": "2026-08-06T05:33:00Z",
                "ssl_issuer": "Let's Encrypt",
                "page_title": "HDFC Bank Login portal",
                "has_pwd": True,
                "findings": ["HDFC brand impersonation wave.", "Active credential input form.", "Recently registered domain (less than 24h)."]
            },

            # Google mimics & redirect threats
            {
                "url": "accounts-google-verify.com",
                "brand": "Google",
                "type": "phishing",
                "severity": "high",
                "score": 75.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "104.244.42.1",
                "asn": "AS13412 (US-Hosts)",
                "isp": "US Hostings",
                "registrar": "GoDaddy",
                "creation_date": "2026-07-22T08:14:00Z",
                "ssl_issuer": "Sectigo",
                "page_title": "Google Accounts Login",
                "has_pwd": True,
                "findings": ["Targeting Google SSO authorization credentials.", "Hosting on suspicious bulk VPS subnet."]
            },
            {
                "url": "gmail-upgrade-verification.net",
                "brand": "Google",
                "type": "phishing",
                "severity": "high",
                "score": 70.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "104.244.42.2",
                "asn": "AS13412 (US-Hosts)",
                "isp": "US Hostings",
                "registrar": "GoDaddy",
                "creation_date": "2026-07-25T11:20:00Z",
                "ssl_issuer": "Sectigo",
                "page_title": "Gmail Portal upgrade",
                "has_pwd": True,
                "findings": ["Obfuscated external JS script included.", "Verification form present."]
            },

            # GitHub Lookalikes & Expired SSL threat indicators
            {
                "url": "github-auth-verify.com",
                "brand": "GitHub",
                "type": "expired_ssl",
                "severity": "medium",
                "score": 58.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "142.250.74.46",
                "asn": "AS15169 (Google)",
                "isp": "Google Cloud",
                "registrar": "GoDaddy",
                "creation_date": "2025-08-01T14:22:00Z",
                "ssl_issuer": "Expired Cert (Expired 2026-08-01)",
                "page_title": "GitHub login authentication redirection",
                "has_pwd": True,
                "findings": ["Expired TLS certificate.", "Credential fields on insecure connection."]
            },
            {
                "url": "git-update-portal.org",
                "brand": "GitHub",
                "type": "redirect",
                "severity": "medium",
                "score": 45.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "142.250.74.47",
                "asn": "AS15169 (Google)",
                "isp": "Google Cloud",
                "registrar": "GoDaddy",
                "creation_date": "2026-01-01T14:22:00Z",
                "ssl_issuer": "Let's Encrypt",
                "page_title": "Git Update Redirection",
                "has_pwd": False,
                "findings": ["Redirect chain: 2 hops to external server.", "No active password inputs."]
            },

            # Clean/Legitimate Scenarios for baseline contrast
            {
                "url": "google.com",
                "brand": "Google",
                "type": "safe",
                "severity": "safe",
                "score": 12.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "142.250.74.46",
                "asn": "AS15169 (Google)",
                "isp": "Google LLC",
                "registrar": "MarkMonitor Inc.",
                "creation_date": "1997-09-15T00:00:00Z",
                "ssl_issuer": "Google Trust Services",
                "page_title": "Google",
                "has_pwd": False,
                "findings": ["Established baseline domain.", "Legitimate registrar history.", "No threats indicators mapped."]
            },
            {
                "url": "microsoft.com",
                "brand": "Microsoft",
                "type": "safe",
                "severity": "safe",
                "score": 15.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "20.112.52.29",
                "asn": "AS8075 (Microsoft)",
                "isp": "Microsoft Corporation",
                "registrar": "MarkMonitor Inc.",
                "creation_date": "1991-05-02T00:00:00Z",
                "ssl_issuer": "Microsoft ECC CA",
                "page_title": "Microsoft - Cloud, Computers, Apps & Gaming",
                "has_pwd": False,
                "findings": ["Established brand portal.", "Highly trusted SSL chain.", "No anomalies found."]
            },
            {
                "url": "paypal.com",
                "brand": "PayPal",
                "type": "safe",
                "severity": "safe",
                "score": 14.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "64.4.250.36",
                "asn": "AS11643 (PayPal)",
                "isp": "PayPal Inc.",
                "registrar": "MarkMonitor Inc.",
                "creation_date": "1999-07-15T00:00:00Z",
                "ssl_issuer": "DigiCert SHA2 Extended Validation CA",
                "page_title": "Send Money, Pay Online or Set Up a Merchant Account - PayPal",
                "has_pwd": False,
                "findings": ["Legitimate payment portal.", "EV SSL verified.", "Zero threat alerts."]
            },
            {
                "url": "statebankofindia.com",
                "brand": "SBI",
                "type": "safe",
                "severity": "safe",
                "score": 18.0,
                "legacy_campaign": None,
                "new_campaign_id": None,
                "ip": "104.211.213.11",
                "asn": "AS55421 (IndiaNet)",
                "isp": "Indian Telecom",
                "registrar": "MarkMonitor Inc.",
                "creation_date": "2000-02-12T00:00:00Z",
                "ssl_issuer": "VeriSign Trust Network",
                "page_title": "State Bank of India",
                "has_pwd": False,
                "findings": ["Legitimate institutional domain.", "No phishing indicators flagged."]
            }
        ]

        # ──────────────────────────────────────────────────────────────────────
        # 3. Seed Domain, Scan, Feature, Risk, Evidence, and Member records
        # ──────────────────────────────────────────────────────────────────────
        print(f"[*] Seeding {len(scenarios)} investigation scenarios...")
        for sc in scenarios:
            # 1. Domain
            domain = Domain(
                url=sc["url"],
                is_legitimate=(sc["type"] == "safe")
            )
            db.add(domain)
            db.commit()

            # 2. Scan (Completed)
            scan = Scan(
                domain_id=domain.id,
                campaign_id=sc["legacy_campaign"].id if sc["legacy_campaign"] else None,
                status="completed"
            )
            db.add(scan)
            db.commit()

            # 3. Feature: domain_intel (Aggregated observations)
            observations = {
                "indicator": sc["url"],
                "domain_name": sc["url"],
                "tld": sc["url"].split(".")[-1],
                "ip_address": sc["ip"],
                "reverse_dns": f"ptr-{sc['ip'].replace('.', '-')}.fakehost.com",
                "hosting_provider": sc["isp"],
                "whois_registrar": sc["registrar"],
                "whois_creation_date": sc["creation_date"],
                "ssl_issuer": sc["ssl_issuer"],
                "ssl_common_name": sc["url"],
                "ssl_days_remaining": -5 if "Expired" in sc["ssl_issuer"] else 250,
                "page_title": sc["page_title"],
                "forms_count": 2 if sc["has_pwd"] else 0,
                "password_fields_count": 1 if sc["has_pwd"] else 0,
                "suspicious_keywords_found": (sc["type"] != "safe"),
                "virustotal_positives": 5 if sc["severity"] in ["critical", "high"] else 0,
                "virustotal_total": 90,
                "urlhaus_match": (sc["severity"] == "critical")
            }
            feature = Feature(
                scan_id=scan.id,
                key="domain_intel",
                value=observations
            )
            db.add(feature)

            # 4. RiskScore (Legacy)
            risk_score = RiskScore(
                scan_id=scan.id,
                score=int(sc["score"]),
                explanation="\n".join(sc["findings"])
            )
            db.add(risk_score)

            # 5. UnifiedEvidenceRecord (Stage 5.4)
            evidence_record = UnifiedEvidenceRecord(
                indicator=sc["url"],
                indicator_type="url",
                resolved_observations=observations,
                sources=[{"source": "internal_extraction", "confidence": "high"}],
                overall_confidence="high",
                metadata_json={
                    "audit_trail": {
                        "investigation_start": datetime.now(timezone.utc).isoformat(),
                        "events": [
                            {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "internal", "event_type": "extraction", "description": "Successfully completed WHOIS, DNS & TLS queries."}
                        ]
                    }
                }
            )
            db.add(evidence_record)

            # 6. RiskAssessmentRecord (Stage 6.4)
            risk_assessment = RiskAssessmentRecord(
                indicator=sc["url"],
                indicator_type="url",
                overall_score=sc["score"],
                severity=sc["severity"],
                breakdown={
                    "brand_impersonation": (sc["type"] != "safe"),
                    "credential_harvesting": sc["has_pwd"],
                    "new_domain": ("2026" in sc["creation_date"]),
                    "ssl_issues": ("Expired" in sc["ssl_issuer"] or "Self" in sc["ssl_issuer"])
                },
                recommendations=[
                    {"priority": "immediate", "description": "Block domain at external DNS firewalls."} if sc["severity"] in ["critical", "high"]
                    else {"priority": "medium", "description": "Monitor DNS resolution trails."}
                ],
                explanation="\n".join(sc["findings"]),
                unified_evidence_indicator=sc["url"]
            )
            db.add(risk_assessment)
            db.commit()

            # 7. CampaignMemberRecord (Stage 7.5) if associated
            if sc["new_campaign_id"]:
                member = CampaignMemberRecord(
                    campaign_id=sc["new_campaign_id"],
                    indicator=sc["url"],
                    indicator_type="url",
                    added_reason=f"Infrastructure overlap: hosting range IP matches campaign.",
                    resolved_observations_json=observations
                )
                db.add(member)
                db.commit()

        # Update CampaignRecord member lists summaries in DB
        c1_members = db.query(CampaignMemberRecord).filter(CampaignMemberRecord.campaign_id == "CAMP-2026-004").all()
        c1_record.summary_json = {
            "campaignName": "CozyBear Impersonation Wave",
            "campaignId": "CAMP-2026-004",
            "status": "Active",
            "riskLevel": "Critical",
            "confidence": "97%",
            "total_indicators": len(c1_members),
            "first_seen": "2026-08-01T08:15:00Z",
            "last_seen": "2026-08-06T22:15:00Z",
            "primary_ttp_tags": ["cozybear", "phishing", "microsoft"]
        }
        
        c2_members = db.query(CampaignMemberRecord).filter(CampaignMemberRecord.campaign_id == "CAMP-2026-008").all()
        c2_record.summary_json = {
            "campaignName": "Fintech Harvester Syndicate",
            "campaignId": "CAMP-2026-008",
            "status": "Active",
            "riskLevel": "High",
            "confidence": "92%",
            "total_indicators": len(c2_members),
            "first_seen": "2026-08-04T09:12:00Z",
            "last_seen": "2026-08-06T15:50:00Z",
            "primary_ttp_tags": ["fintech", "harvester", "paypal"]
        }

        db.commit()
        print(f"[+] Successfully seeded {len(scenarios)} records and 2 campaigns.")
    except Exception as err:
        db.rollback()
        print(f"[!] Error seeding database: {err}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
