# Project Notes

> *NOTE TO AGENT: You must read and review `PROJECT_NOTES.md` at the start of every task/prompt to maintain full context of project progress, design decisions, and active changes.*

---

## Development Rule
Before implementing any feature, always review:
1. **Current Development Status**
2. **System Architecture**
3. **Decision Log**
4. **Completed Progress Tracker**

Every implementation must remain consistent with these sections. Every completed task must update:
- **Progress Tracker**
- **Documentation**
- **Architecture** (if changed)
- **Decision Log** (if applicable)
- **Verification Checklist** (if required)

---

## 1. Current Development Status

| Status | Component / Feature Group | Details |
| :--- | :--- | :--- |
| **Completed** | Project Boilerplate | Folder structure setup, configs, entry points. |
| **Completed** | Backend Foundation | FastAPI entry, CORS middleware, UUID RequestID tracing. |
| **Completed** | Configuration Layer | Pydantic Settings env validation. |
| **Completed** | Middleware | Request timing and CORSMiddleware. |
| **Completed** | Health & Lifecycle | Readiness check (`/ready`) querying PostgreSQL. |
| **Completed** | Database Engine | Core SQLAlchemy engine with production connection pool settings. |
| **Completed** | ORM Models | Declarative mapped entities (`Domain`, `Campaign`, `Scan`, `Feature`, `RiskScore`). |
| **Completed** | Repository Pattern | Generic CRUDBase class & repository singletons injected in FastAPI deps. |
| **Completed** | REST APIs | CRUD endpoints for all mapped entities. |
| **Completed** | Feature Extraction Engine | URL Normalization, TLD parsing, WHOIS querying, DNS querying (A/MX/NS). |
| **Completed** | Network & TLS Intel | IP PTR reverse DNS, non-verifying TLS cert parse (CN, SANs, Issuer, Expiry). |
| **Completed** | Webpage HTML Intel | BeautifulSoup metadata, forms count, password detection, resource counters. |
| **Completed** | Aggregation Pipeline | Unified feature extraction scheduler, failing gracefully, storing JSON. |
| **Completed** | Threat Intelligence Integration | Integrations with VirusTotal, PhishTank, URLHaus, AbuseIPDB, and AlienVault OTX feeds with concurrent aggregation engine and lookups REST APIs. |
| **Completed** | Unified Evidence Engine | Merge, normalization, confidence scoring, DB persistence, REST API, audit trail, traceability & final refactor — Milestone 5 100% Complete (Stage 5.6). |
| **Completed** | Risk Scoring Engine | Explainable rules, recommendations, validation & calibration, DB persistence, REST API & final refactor — Milestone 6 100% Complete (Stage 6.6). |
| **Completed** | Campaign Correlation | Attacker attribution and clustering based on shared infrastructure footprints — Milestone 7 100% Complete (Stage 7.6). |
| **Completed** | AI Investigation Assistant | OpenRouter provider-agnostic HTTP gateway integration, model configurations (default vs fallback), REST API endpoints (ask, report), and local engine fallback — Milestone 8 (Stages 8.1 - 8.6) 100% COMPLETE. |
| **Remaining** | Brand Intelligence | Favicon hash, page template text similarity, visual logo detection. |
| **Remaining** | Explainable AI | Heuristics extraction summaries for SOC analysts. |
| **Completed** | Dashboard UI | Analyst control panel and queue dashboard. |
| **Completed** | Reporting | Exportable Markdown/PDF reports detailing threats evidence. |
| **Remaining** | Deployment | Final packaging and cloud/docker deployment patterns. |


---

## 2. Complete Technology Stack

### Frontend
- **React**: Single page application framework.
- **Vite**: Rapid frontend builder and server.
- **TailwindCSS**: CSS framework for modern design aesthetics.

### Backend
- **FastAPI**: Main high-performance RESTful API router framework.
- **Python**: Core programming language.

### Database & Persistence
- **PostgreSQL**: Primary transactional database.
- **SQLAlchemy**: Relational mapper (ORM) for schema interactions.
- **Pydantic V2**: Request validation and response serialization.

### Extraction Libraries
- **requests**: Standard HTTP GET client with redirect tracking.
- **BeautifulSoup**: HTML webpage element parsing.
- **dnspython**: Active DNS querying.
- **python-whois**: Registrar and age tracking.
- **socket & ssl**: Port 443 socket wrapping and certificate parsing.

### Future Integrations
- **Threat Feeds**: VirusTotal, PhishTank, URLHaus, AbuseIPDB.
- **Brand Matching**: OpenCV, imagehash, RapidFuzz.

---

## 3. End-to-End System Workflow

Runtime execution flow of URL submissions:

```text
User Submits URL (Dashboard)
      ↓
Create Scan Entity (DB Registry)
      ↓
Feature Extraction Pipeline
  ├─ DomainIntelService (DNS, WHOIS)
  ├─ NetworkIntelService (IP PTR, SSL/TLS cert)
  └─ WebpageIntelService (BeautifulSoup HTML parsing)
      ↓
Threat Intelligence Feeds (VirusTotal, PhishTank, URLHaus, AbuseIPDB)
      ↓
Brand Intelligence (OpenCV matching, Favicon hashes, text similarity)
      ↓
Campaign Correlation Engine (group assets by footprint attributes)
      ↓
Risk Scoring Engine (0-100 explainable score computed)
      ↓
LLM Explanation (SOC analyst summary narrative)
      ↓
Dashboard Refresh (Analyst updates)
      ↓
Incident Report Generation (Markdown / PDF export)
```

1. **User Submits URL**: Analyst inputs target url through the React UI queue.
2. **Create Scan**: System creates a Scan database record and links it to a Domain entity.
3. **Feature Extraction**: Aggregation Pipeline queries DNS, WHOIS registry, wrapper port 443 SSL certificate, and webpage HTML.
4. **Threat Intelligence Collection**: Feeds query reputation databases for quick matches.
5. **Brand Intelligence**: OpenCV template and image hashing evaluates lookalike assets.
6. **Campaign Correlation**: Attacker attribute matches identify campaign groups.
7. **Risk Scoring**: Risk engine translates signals to a transparent score.
8. **LLM Explanation**: Translates evidence logs to human narrative.
9. **Dashboard / Report**: Exports evidence package to SOC dashboard or PDF.

---

## 4. Database Relationship Overview

Entities in the ThreatLens database layer are mapped as follows:

```text
  ┌───────────────────┐
  │     Campaign      │
  └─────────┬─────────┘
            │ 1
            │
            │ *
  ┌─────────▼─────────┐
  │      Domain       │
  └─────────┬─────────┘
            │ 1
            │
            │ *
  ┌─────────▼─────────┐
  │       Scan        │
  └────┬──────────┬───┘
       │ 1        │ 1
       │          │
       │ *        │ *
┌──────▼──────┐ ┌─▼───────────┐
│   Feature   │ │  RiskScore  │
└─────────────┘ └─────────────┘
```

- **Campaign**: Groups multiple Domains under an identified adversary campaign.
- **Domain**: Represents the unique hostname target submitted for analysis.
- **Scan**: Represents an individual execution run on a Domain URL.
- **Feature**: Holds structured json evidence results (e.g. domain age, TLS, HTML attributes) extracted during the Scan.
- **RiskScore**: Holds the final explainable calculated score and contributing weights.

---

## 5. Development Roadmap

- **Milestone 4 (Threat Intelligence Integration)**: Hook API client calls to check domain reputation on VirusTotal, PhishTank, URLHaus, and AbuseIPDB.
- **Milestone 5 (Brand Intelligence)**: Deploy visual logo matches via OpenCV, favicon hashes (`imagehash`), and page text structure matching (`RapidFuzz`).
- **Milestone 6 (Risk Scoring Engine)**: Establish the explainable weighted engine combining parameters.
- **Milestone 7 (Campaign Correlation Engine)**: Deploy footprint mapping heuristics to group domain groups.
- **Milestone 8 (Explainable AI)**: Narrative summary generation.
- **Milestone 9 (Dashboard)**: Build React dashboard and queue tables.
- **Milestone 10 (Reporting)**: Implement PDF/Markdown incident report generators.
- **Milestone 11 (Integration)**: Final verification and cross-service tuning.
- **Milestone 12 (Deployment)**: Dockerized deployment manifests.

---

## 6. Planned Risk Scoring Design

> [!NOTE]
> *This outlines the planned Risk Engine design. It is not yet implemented.*

The ThreatLens Risk Engine calculates a transparent score from `0` (clean) to `100` (critical) using the following weighted signals:
- **Domain Age**: Younger domains trigger higher risk weights (critical when <30 days).
- **Registrar Reputation**: Flags known high-abuse registrars.
- **SSL Certificate Validity**: Flags lack of SSL, short lifespans, or mismatching Common Names.
- **Threat Intelligence**: Scoring modifiers based on VT detections or blacklist matches.
- **Brand Similarity**: Flags visual logo or textual matches referencing protected enterprise assets.
- **HTML structure**: Matches form input elements (password inputs) hosted on untrusted domains.
- **Infrastructure Similarity**: Flags shared malicious IPs or nameservers.
- **Campaign Confidence**: Scoring adjustments if linked to an active Campaign group.

The risk report will detail the exact weights that contributed to the score, allowing analysts to justify domain takedown requests.

---

## 7. Campaign Correlation Design & Architecture

> [!NOTE]
> *Stage 7.3 (Campaign Clustering & Attribution Engine) is implemented. Campaign persistence, REST APIs, and database migrations will be implemented in subsequent stages.*

Rather than treating target URLs as isolated events, ThreatLens groups assets into unified Campaign clusters based on shared infrastructure attributes. By matching footprints, analysts can identify the scope of target brand impersonation campaigns.

### Campaign Engine Abstractions (Stage 7.1)
The module is divided into a decoupling design:
1. **Core Domain Models (`models.py`)**:
   - `Campaign`: Holds campaign properties, tracked status, severity, list of associated member assets, summary metrics, and list of shared evidence.
   - `CampaignMember`: Represents an indicator URL/IP linked to a campaign with timestamps and observations snapshot.
   - `CorrelationEvidence`: Represents specific indicators matched (e.g. `shared_ip`, `favicon_hash`, `html_similarity`).
   - `CorrelationResult`: Scoring output of matcher checking correlation.
   - `CampaignSummary`: Overview statistics of indicators volume and tracking dates.
   - `CampaignSeverity` & `CampaignStatus` Enums.
2. **REST API validation Schemas (`schemas.py`)**:
   - Defines API shapes for creating campaigns (`CampaignCreate`), updating metadata (`CampaignUpdate`), adding members (`AddCampaignMemberRequest`), and returning payloads (`CampaignResponse`).
3. **Correlation Interface (`base.py`)**:
   - `BaseCorrelationStrategy`: Declares abstract correlation signature: `correlate(current_evidence, historical_evidence_list) -> CorrelationResult`. Diverse matches can inherit from this strategy.
4. **Campaign Service Orchestrator (`service.py`)**:
   - `CampaignCorrelationService`: Entry service coordinating searches, campaign registration, and member allocations.

### Similarity & Matching Algorithms (Stage 7.2)
We evaluate correlations using a 100-point weight budget scaled to a `[0.0, 1.0]` `match_score` range. A link is flagged as correlated if `match_score >= 0.40` (40% similarity match).

| Correlator | Match Type | Weight | Description |
|---|---|---|---|
| **Infrastructure** (40 pts) | `shared_ip` | 25 pts | Both domains resolve to the identical IPv4/IPv6 address. |
| | `shared_dns_records` | 10 pts | Indicators share DNS resolving A/AAAA records. |
| | `shared_asn` | 5 pts | Both host IPs resolve to the identical Autonomous System Network. |
| **TLS Certificate** (30 pts) | `shared_tls_serial` | 20 pts | Both endpoints utilize the identical certificate serial number. |
| | `shared_tls_subject` | 5 pts | Both share the TLS Subject Common Name (CN) or Org. |
| | `shared_tls_issuer` | 5 pts | Both certificates were generated by the identical CA. |
| **WHOIS Registry** (15 pts) | `shared_registrant_org` | 8 pts | Registrant organization match (filtering out privacy proxies). |
| | `shared_registrar` | 4 pts | Domain registrations routed via the identical registrar. |
| | `shared_domain_creation_date` | 3 pts | Domains registered on the exact same date (YYYY-MM-DD). |
| **HTML Content** (15 pts) | `shared_page_title` | 8 pts | Identical HTML page titles (skipping generic values like "index"). |
| | `shared_html_structure_hash` | 5 pts | Identical page structural DOM/template signature hashes. |
| | `shared_forms_count` | 2 pts | Both render the identical count of active forms (>0). |

### Campaign Clustering & Attribution Workflow (Stage 7.3)
The `CampaignClusterer` (`clustering.py`) orchestrates indicator rehoming, campaign merging, and similarity drift-splitting.

```
       New Investigation Resolved Observations
                       │
                       ▼
       ┌───────────────────────────────┐
       │   SimilarityEngine Evaluator  │  (Pairwise match against all active members)
       └───────────────────────────────┘
                       │
                       ├─> Max Score < 0.40  ───> [CREATE] New Campaign (CAMP-YYYYMMDD-XXXX)
                       │
                       ├─> Exactly 1 Match   ───> [JOIN]  Add as Member, merge TTPs/infra
                       │
                       └─> Multiple Matches  ───> [MERGE] Re-home all members to primary
                                                          campaign (highest score), merge TTPs,
                                                          upgrade severity.
```

- **Attribution Methodology**: Matches are tracked via detailed `CorrelationEvidence` lists stored in `shared_infrastructure`. Individual members record their specific match justification in `added_reason`.
- **Heuristic Drift Splits**: Periodically/post-eval, `check_for_split()` builds an undirected graph of campaign members using pairwise similarity. If the graph drifts into disconnected components, the campaign splits, spawning new campaigns with recalculated first/last seen metadata and re-extracted infrastructure arrays.

### Campaign Timeline & Relationship Graph (Stage 7.4)
To assist analysts in pivot investigations, Stage 7.4 constructs chronological timelines and node-link relationship graphs mapping the campaign topology.

1. **Relationship Graph Model (`graph_models.py` & `graph_builder.py`)**:
   - `GraphNode` models nodes for indicators (e.g. domains/URLs), resolving IP addresses, TLS Certificates, WHOIS details (Owner Org, Registrar), and HTML artifacts (Page Titles, DOM hashes).
   - `GraphEdge` links nodes with directional relationships (`resolves_to`, `hosted_on`, `presents_cert`, `registered_with`, `shares_layout_hash`).
   - Deduplicates matching vertices, allowing analysts to visualize shared infrastructure footprints instantly.
2. **Chronological Timeline Model (`timeline.py`)**:
   - Compiles point-in-time milestones from the campaign's lifecycle:
     * `campaign_creation`: Timestamp when the campaign was seeded.
     * `domain_registration`: Parsed WHOIS registration timestamps of associated indicator domains.
     * `indicator_association`: Log events marking when indicators were matched and joined to the campaign (with attribution reasoning).
   - Orders all milestones chronologically (oldest first) to map attacker setup patterns.

---

## 8. Project Vision & Problem Statement

### Project Vision
ThreatLens aims to be the definitive open-source enterprise brand protection platform, specializing in **AI-assisted phishing investigation, explainable risk analysis, and campaign attribution**. By coordinating network/webpage intelligence features, calculating explainable risk scores, and correlating shared infrastructure footprints, ThreatLens equips SOC analysts with the concrete evidence needed to attribution threat campaigns and expedite domain takedowns.

### Problem Statement
Corporate brand impersonation and high-fidelity phishing websites have become increasingly cheap and trivial to launch. Attackers rapidly deploy lookalike domains, scrape official corporate assets, and trick employees or clients. Existing security solutions are often reactive, opaque, or slow to flag new threats. SOC analysts are overwhelmed with raw logs and lack actionable evidence (e.g. OCR transcripts, brand asset matching details, structural comparison scores) required to justify rapid domain takedown requests.

### Target Users
- **SOC Analysts**: Need a unified portal to review visual similarity scores, OCR extractions, and launch automated DNS/WHOIS lookups.
- **Threat Intelligence Leads**: Need to cluster brand abuse incidents into logical "campaigns" and track threat group behavior over time.
- **CISO / Security Managers**: Need high-level dashboards of active risks, metrics on takedown durations, and exportable executive reports.

---

## 9. Scope & Boundaries

### MVP Scope
- **Domain Scan Queue**: An analyst-facing dashboard to submit suspicious URLs.
- **Evidence Extraction**: Automated pipeline extracting DNS records, WHOIS details, screenshot artifacts, and page HTML content.
- **AI-Powered Visual & Structural Matching**:
  - Image hashing and OpenCV match templates to evaluate logo usage.
  - TF-IDF and bag-of-words text extraction comparison against company templates.
- **Risk Score Engine**: A rule-based calculator combining heuristics (SSL lifetime, registrar, brand keywords) and AI signals into an explainable score (0-100).
- **Analyst Reporting**: Exportable Markdown/PDF reports outlining malicious indicators.

### Out-of-Scope Features
- **Automated Registrar Takedown Submissions**: Auto-submitting to registrars (MVP will provide the draft email template only).
- **Real-time SMS Alerting**: Integrations with cellular providers (MVP will use Slack/Webhook notifications only).
- **Deep Web / Dark Web Monitoring**: Searching Tor nodes (MVP focuses entirely on clear-web DNS/HTTPS protocols).

---

## 10. System Architecture & Design Segregation

### Architectural Design
The data layer and RESTful API layer are decoupled using four core patterns:
1. **Model Representation (SQLAlchemy ORM)**: Relational models (`Domain`, `Campaign`, `Scan`, `Feature`, `RiskScore`) inheriting from a shared declarative `Base` with automated table name lowercase formatting and common audit tracking fields (`id`, `created_at`, `updated_at`).
2. **Data Validation (Pydantic V2 Schemas)**: Segregates request parameters from response serializers to prevent data exposure and enforce strict type contracts:
   - `[Entity]Base`: Shared properties between create/update/response schemas.
   - `[Entity]Create`: Data required during model creation.
   - `[Entity]Update`: Fields allowed for patching existing records (all fields optional).
   - `[Entity]Response`: Final response schema serialized back to the client, adding database-specific fields (`id`, `created_at`, `updated_at`). Employs `model_config = ConfigDict(from_attributes=True)` for seamless SQLAlchemy serialization.
3. **Data Access (Repository Pattern)**: Implements `CRUDBase` as a generic helper module mapping standard ORM methods (`get`, `get_multi`, `create`, `update`, `remove`) using TypeVars. Specific CRUD repositories subclass `CRUDBase` and expose global singleton instances.
4. **API Routing (FastAPI REST Endpoints)**: Clean separation of resource route files under `backend/app/api/v1/endpoints/` exposing pluralized routing mounts.
5. **Feature Extraction Engine (URL Domain Intelligence)**: Standardized service layer (`DomainIntelService`) responsible for normalizing URLs, parsing domain hierarchies via `tldextract`, resolving A/MX/NS records via `dnspython`, querying registry creation dates via `python-whois`, and generating domain age values. Structured JSON datasets are saved in the database under `domain_intel` feature attributes.
6. **Feature Extraction Engine (Network & Certificate Intelligence)**: Standardized service layer (`NetworkIntelService`) responsible for resolving host IP routing and reverse DNS (socket PTR queries), extracting peer SSL/TLS certificate metadata (availability, issuer, common name, Subject Alternative Names, validity timestamps, days until expiry, signature algorithm, TLS protocol version, cipher suite) via non-verifying connections to port 443, and capturing HTTP GET connections response properties (status code, redirect chain history, final destination URL). Records are stored in the database features list under `network_intel`.
7. **Feature Extraction Engine (Webpage HTML Intelligence)**: Standardized service layer (`WebpageIntelService`) fetching HTML content safely and parsing metadata tags (title, description, keywords, language, favicon, canonical, Open Graph properties), form structures (total forms, password inputs, login forms detection via name/id/class keywords), resource references (js count, css count, image count, internal/external resource counts), and links mapping (internal/external href tags) using BeautifulSoup.
8. **Feature Extraction Engine (Feature Aggregation Pipeline)**: Orchestration layer (`FeatureAggregationService`) that executes all extraction services (Domain, Network, Webpage) concurrently/sequentially, handles timeouts or host failures gracefully by returning partial results, and combines outputs into a single normalized evidence dictionary containing metadata, status indicators, and errors.
9. **Threat Intelligence Foundation (Stage 4.1 & Refactoring 4.6)**: Structured modular framework (`app/services/threat_intel/`) containing Pydantic schemas (`models.py`) mapping verdicts and matches, and an abstract base provider (`base.py:BaseThreatIntelProvider`) implementing shared helpers (`_safe_lookup` for standardized logging/timing/exceptions, `_unsupported_indicator` for routing type exceptions, and `_disabled_response` for missing key validations).
10. **VirusTotal Integration (Stage 4.2 & Refactored)**: Threat provider integration (`app/services/threat_intel/providers/virustotal.py`) implementing v3 API URLs and Domains endpoints. Encodes URLs using URL-safe base64 parameter hashing, parses analysis engine indicators, normalizes responses into standardized schemas.
11. **PhishTank & URLHaus Integration (Stage 4.3 & Refactored)**: Threat provider integrations (`app/services/threat_intel/providers/phishtank.py` and `app/services/threat_intel/providers/urlhaus.py`) implementing URL reputation checks. PhishTank utilizes the custom `User-Agent` to prevent Cloudflare/403 blocks, while URLHaus passes authenticated `Auth-Key` queries or bypasses lookups gracefully.
12. **AbuseIPDB & AlienVault OTX Integration (Stage 4.4 & Refactored)**: Threat provider integrations (`app/services/threat_intel/providers/abuseipdb.py` and `app/services/threat_intel/providers/alienvault.py`) completing external feeds. AbuseIPDB maps confidence scores for IP checks, and AlienVault OTX queries domains, URLs, and IPs to count active pulse alerts.
13. **Threat Evidence Aggregation Engine (Stage 4.5)**: Orchestration layer (`app/services/threat_intel/aggregator.py`) and API router (`app/api/v1/endpoints/threat_intel.py`) executing concurrent indicators checks, enforcing timeout limits (5s max), and synthesizing verdicts on a priority scale (`malicious` > `suspicious` > `clean` > `unknown`).
14. **Unified Evidence Engine (Stage 5.1 & 5.2)**: Structured modular framework (`app/services/unified_evidence/`) mapping standardized evidence schemas (`models.py`) and interfaces (`service.py:UnifiedEvidenceService`) to combine internal extraction scans evidence (WHOIS, DNS, TLS, HTML BeautifulSoup) and external threat intelligence reputation lookups (VirusTotal, PhishTank, URLHaus, AbuseIPDB, AlienVault OTX) into a single normal model containing overall category and confidence levels.
15. **Evidence Merging Strategy (Stage 5.2)**: Implements `DefaultMergeStrategy` (`strategy.py`) inheriting from `BaseMergeStrategy` to handle conflict resolution and deduplication. Overlapping keys (such as `domain_age` or `ip_address`) are reconciled by prioritizing external threat intelligence over internal scans, recording overrides in `conflict_resolutions` for full traceability.
16. **Evidence Normalization Pipeline (Stage 5.3)**: Standardizes type representations via `EvidenceNormalizer` (`normalizer.py`), casting form flags to booleans, extracting digits from age spans to integers, strip-cleaning schemes/netloc values from URL indicators, and standardizing empty fields to `None`, writing detailed normalization log summaries.
17. **Confidence Scoring Engine (Stage 5.3)**: Computes reliability levels via `EvidenceConfidenceEngine` (`confidence.py`). Evaluates individual fields mapping indicators (`virustotal_verdict`, `provider_responses`, etc.) to `HIGH` confidence, heuristics inputs (`has_login_form`, `ssl_valid`, etc.) to `MEDIUM` confidence, and missing/corrupted tags to `UNKNOWN`/`LOW`. Overall consensus registers as `HIGH` if any critical indicator matches `HIGH` or averages score values.
18. **Unified Evidence Persistence & API (Stage 5.4)**: Persists processed evidence via `UnifiedEvidenceRecord` SQLAlchemy ORM model (`app/db/models/unified_evidence.py`) with indexed `indicator` and composite `indicator+timestamp` columns for fast history queries. Service methods `save_evidence(db, evidence)` and `get_evidence_by_indicator(db, indicator)` manage storage. REST endpoints `POST /api/v1/unified-evidence/process` (merge+normalize+save) and `GET /api/v1/unified-evidence/{indicator}` (history retrieval) complete the public interface.
19. **Evidence Timeline & Traceability (Stage 5.5)**: `EvidenceTimelineBuilder` (`timeline.py`) synthesizes a four-phase `AuditTrail` during `process_evidence`: (1) **Collection** — one event per internal key and one per external provider/key ingested; (2) **Conflict Resolution** — one event per merge override with key attribution; (3) **Normalization** — one event per type-cast applied; (4) **Confidence Scoring** — summary event. All events are sorted chronologically by microsecond-precision timestamps and stored inside `metadata_json["audit_trail"]` in `UnifiedEvidenceRecord`. The `GET /api/v1/unified-evidence/timeline?indicator=<…>` endpoint reconstructs and returns the `AuditTrail` from the most recent persisted record.
20. **Unified Evidence Engine Refactoring & Finalization (Stage 5.6)**: Final clean-up pass across all 5 module files:
    - **`strategy.py`**: Added module logger; removed dead `pass` branch; added INFO log on merge completion.
    - **`normalizer.py`**: Added module logger; refactored flat method into `_normalize_value` dispatcher + three private helpers (`_cast_bool`, `_cast_int`, `_standardize_url`); added per-key `try/except` fallback; replaced Python lists with `frozenset` key sets for O(1) lookups; added INFO log on normalize completion.
    - **`confidence.py`**: Added module logger; promoted key sets and weight map to module-level `frozenset`/`dict`; added DEBUG per-item log and INFO overall consensus log with score.
    - **`timeline.py`**: Fixed `datetime | None` union syntax to `Optional[datetime]` for Python <3.10 compatibility; extracted `_extract_key_from_message()` helper to eliminate duplicated key-parsing logic in Phase 2 and Phase 3; removed unused `payload` variable from provider loop; replaced `set` with ordered `list` for provider iteration.
    - **`service.py`**: Removed unused `TYPE_CHECKING` import; added outer `try/except` around the 5-step pipeline raising `RuntimeError` with full context; extracted `_detect_indicator_type()` and `_build_sources()` as module/static helpers; standardized all log messages with `[process_evidence]` prefix.

21. **Risk Engine Foundation (Stage 6.1)**: Created `app/services/risk_engine/` package with clean public `__init__.py` exports. Defined four Pydantic models in `models.py`:
    - `RiskSeverity` enum: SAFE / LOW / MEDIUM / HIGH / CRITICAL.
    - `RiskFactor`: individual explainable contributor with `name`, `score_contribution`, `description`, `weight`, `evidence_key`.
    - `RiskBreakdown`: five category lists with `all_factors()` and `total_contribution()` helpers.
    - `RiskScore`: complete result with `indicator`, `overall_score`, `severity`, `breakdown`, `factor_count`, `timestamp`, `explanation`.
    - `BaseRiskEvaluator` ABC in `base.py` with `evaluate()` abstract method and `safe_evaluate()` defensive wrapper that never propagates exceptions.

22. **Risk Engine Weighted Scoring Rules (Stage 6.2)**: Implemented five concrete evaluators in `rules.py`:

    | Evaluator | Max Score | Key Rules |
    |---|---|---|
    | `DomainIntelEvaluator` | 25 pts | Very young domain (<30d: 12pts), Young domain (<180d: 8pts), Suspicious TLD (7pts), IP-based URL (6pts) |
    | `DnsWhoisEvaluator` | 15 pts | No MX records (6pts), No NS records (5pts), WHOIS privacy (4pts) |
    | `TlsCertificateEvaluator` | 15 pts | Invalid/expired TLS (10pts), Free CA certificate (3pts), Near-expiry cert (2pts) |
    | `HtmlContentEvaluator` | 20 pts | Login form (10pts), Password inputs (5pts), High form count (3pts), Suspicious title (2pts) |
    | `ThreatIntelEvaluator` | 25 pts | VT Malicious (15pts), PhishTank confirmed (10pts), URLHaus active (10pts), AbuseIPDB high (8pts), OTX pulses (5pts) |

23. **Risk Scoring Normalization & Severity Mapping (Stage 6.2)**:
    - **Dynamic denominator**: If an entire evidence category has no relevant keys, its max_contribution is excluded from the denominator so the score remains correctly scaled to 0-100.
    - **Severity tiers**: SAFE (0-20) → LOW (21-40) → MEDIUM (41-70) → HIGH (71-89) → CRITICAL (90-100).
    - **Explainability**: Top-3 contributing factor names appear in the human-readable `explanation` field of every `RiskScore`.
    - **Input flexibility**: `RiskScoringService.calculate_risk()` accepts both a `UnifiedEvidence` Pydantic model and a plain dict.

24. **Risk Engine Data Flow (Stage 6.2)**:
    ```
    UnifiedEvidence / dict
           │
           ▼
    _extract_evidence()          ← flatten to resolved_observations + indicator
           │
           ▼
    [5 × safe_evaluate()]        ← DomainIntel, DNS/WHOIS, TLS, HTML, ThreatIntel
           │
           ▼
    RiskBreakdown.total_contribution()
           │
    ÷ dynamic_denominator × 100  ← excludes absent categories
           │
           ▼
    _map_severity()              ← SAFE / LOW / MEDIUM / HIGH / CRITICAL
           │
           ▼
    RiskScore(indicator, score, severity, breakdown, explanation)
    ```

25. **Recommendation Engine (Stage 6.3)**: `RecommendationEngine` (`recommendations.py`) maps triggered `RiskFactor` names to 20 deterministic, human-readable analyst recommendations ranked by priority. Design:
    - **Factor-level rules**: Each `RiskFactor.name` maps to `(action, priority, description)` tuple. Examples: `"VirusTotal: Malicious Verdict"` → `"Block indicator at perimeter"` (immediate); `"Login / Credential Form Detected"` → `"Test for credential harvesting"` (high).
    - **Severity catch-all**: A baseline `Recommendation` is always appended for the overall severity tier (CRITICAL→immediate incident response, HIGH→escalate, MEDIUM→triage queue, LOW→log+monitor, SAFE→no action).
    - **Deduplication**: Same `action` string is never added twice across factors.
    - **Priority sorting**: Output is sorted `immediate → high → medium → low` before returning.
    - **Integration**: `RecommendationEngine.generate(factors, severity)` called as Step 6 in `RiskScoringService.calculate_risk()`; results stored in `RiskScore.recommendations`.

26. **Risk Assessment Persistence (Stage 6.4)**: `RiskAssessmentRecord` SQLAlchemy ORM model (`app/db/models/risk_assessment.py`) columns:
    - `indicator` (String/2048, indexed), `indicator_type` (String), `overall_score` (Float), `severity` (String).
    - `breakdown` (JSON) — full `RiskBreakdown.model_dump()` for audit.
    - `recommendations` (JSON) — `List[Recommendation.model_dump()]`.
    - `explanation` (Text), `unified_evidence_indicator` (String, indexed), `timestamp` (DateTime with tz).
    - Composite index `(indicator, timestamp)` for fast history queries.

27. **Risk Engine REST API (Stage 6.4)**:
    - `POST /api/v1/risk/evaluate` — Accepts `EvaluateRiskRequest` (indicator + optional evidence dicts). Runs full pipeline, saves `RiskAssessmentRecord` to DB (if `save_to_db=True`), returns `RiskScore`.
    - `GET /api/v1/risk/{indicator:path}` — Returns `List[RiskAssessmentResponse]` for history retrieval, ordered by timestamp desc. Returns 404 if no records found.
    - Router registered under prefix `/risk` with tag `"Risk Engine"` in `v1_router`.

28. **Risk Engine Validation & Calibration (Stage 6.5)**:
    - **Centralized Config** (`config.py`): Extracted all category weights (`RISK_WEIGHTS`), confidence multipliers (`CONFIDENCE_MULTIPLIERS`), severity thresholds (`SEVERITY_THRESHOLDS`), and category key maps (`CATEGORY_EVIDENCE_KEYS`) into a single calibration file. Adjusting `RISK_WEIGHTS` automatically re-scales all evaluators.
    - **RiskValidator** (`validator.py`): Three safety gates integrated into the pipeline:
        1. `validate_evidence(evidence)` — Rejects empty, None, non-dict, indicator-only, or all-null evidence. Returns `False` to trigger an immediate SAFE/0.0 short-circuit.
        2. `calibrate_score(raw_score, confidence)` — Applies confidence multiplier: HIGH=1.0×, MEDIUM=0.85×, LOW=0.60×, UNKNOWN=0.50×. Default fallback=0.75×.
        3. `enforce_boundaries(score)` — Clamps to `[0.0, 100.0]`, handles NaN/infinity → 0.0.
    - **Pipeline Integration** (`service.py`): Steps renumbered 0–9. Step 0 = validation gate, Step 4 = confidence calibration, Step 5 = boundary enforcement. Explanation notes when calibration was applied.
    - **Weight Sourcing** (`rules.py`): All 5 evaluator `max_contribution` values now read from `config.RISK_WEIGHTS[category]` instead of hardcoded floats. `TOTAL_MAX_CONTRIBUTION` sourced from `config.TOTAL_WEIGHT`.

29. **Confidence Calibration Methodology**:
    | Confidence Level | Multiplier | Effect on Score | Rationale |
    |---|---|---|---|
    | HIGH | 1.00× | Unchanged | Full trust — external TI confirmed, multiple sources agree |
    | MEDIUM | 0.85× | −15% | Moderate trust — heuristic signals without external validation |
    | LOW | 0.60× | −40% | Low trust — incomplete data, prevents false alarm escalation |
    | UNKNOWN | 0.50× | −50% | No confidence signal — aggressive dampening |
    | (fallback) | 0.75× | −25% | Unrecognized confidence string |

30. **Risk Engine Architecture Flow**:
    ```
    ┌─────────────────┐      ┌───────────────┐      ┌─────────────────┐
    │ UnifiedEvidence │ ───> │  Validation   │ ───> │ Rule Evaluation │
    └─────────────────┘      └───────────────┘      └─────────────────┘
                                                             │
                                                             ▼
    ┌─────────────────┐      ┌───────────────┐      ┌─────────────────┐
    │ DB Persistence  │ <─── │Explainability │ <─── │   Confidence    │
    │  & REST APIs    │      │Recommendations│      │   Calibration   │
    └─────────────────┘      └───────────────┘      └─────────────────┘
    ```
    - **Step 0: Validation** (`validator.py`): Short-circuits empty/malformed evidence to SAFE/0.0 immediately.
    - **Step 1: Rule Evaluation** (`rules.py`): Fires category-level evaluators concurrently.
    - **Step 2: Normalization**: Computes 0–100 score relative to active categories (dynamic denominator).
    - **Step 3: Confidence Calibration**: Applies penalty multiplier matching the evidence's trust rating.
    - **Step 4: Boundary Clamping**: Clamps final score to `[0.0, 100.0]`, guards against NaN/infinity.
    - **Step 5: Recommendations & Explainability** (`recommendations.py`): Generates priority-sorted actions.
    - **Step 6: DB Persistence & API** (`endpoints/risk.py`): Saves score with full JSON breakdown, returns payload.

31. **Risk Engine Refactoring & Finalization (Stage 6.6)**:
    - **Dead Code Cleanup**: Removed unused `_SEVERITY_MAP` definition from `service.py`. Deleted unused `_CATEGORY_CAP` attribute from `ThreatIntelEvaluator` class in `rules.py`. Removed unused `Recommendation` class import in `service.py`.
    - **Standardized Logging**: Enforced uniform `logger.info()` lifecycle logs for start/completion of calculations in `service.py`, start/completion of endpoint requests in `risk.py`, and database persistence confirmations. Enforced `logger.debug()` for granular rule matching checks in `rules.py` and recommendations building in `recommendations.py`.
    - **Robust DB Commit Wrapper**: Enhanced the DB helper `_save_risk_score` in the API router to handle commit execution within a try/except block. On commit errors, it rolls back the transaction, logs the exception stack trace at ERROR level, and raises an explicit `HTTPException(status_code=500)` ensuring clean client responses.

32. **Campaign Engine Foundation (Stage 7.1)**:
    - **Package Directory** (`app/services/campaign_engine/`): Created the modular package skeleton with abstract strategy interface and typed domain models.
    - **Enums & Models** (`models.py`): Defined `CampaignSeverity` and `CampaignStatus` enums. Established core domain Pydantic entities (`Campaign`, `CampaignMember`, `CorrelationEvidence`, `CorrelationResult`, `CampaignSummary`).
    - **API Schemas** (`schemas.py`): Created structured validation schemas: `CampaignCreate` (seeding), `CampaignUpdate` (metadata), `AddCampaignMemberRequest` (member injection), and `CampaignResponse` (serialization).
    - **Strategy Interface** (`base.py`): Defined `BaseCorrelationStrategy` declaring correlation logic contract signature: `correlate(current_evidence, historical_evidence_list) -> CorrelationResult`.
    - **Orchestration Service** (`service.py`): Built `CampaignCorrelationService` managing stubs for `find_related_campaigns()`, `create_campaign()` (with UUID assignments and seeding), and `add_to_campaign()`.

33. **Campaign Core Similarity Matchers (Stage 7.2)**:
    - **Pairwise Correlators** (`correlators.py`): Implemented 4 concrete correlators comparing attributes of two investigations (Infrastructure, TLS, WHOIS, and HTML content features).
    - **Similarity Scorer** (`similarity.py`): Created `SimilarityEngine` combining matching weights (cumulative budget = 100 raw points). Bounded `match_score` to Pydantic constraint `[0.0, 1.0]` by dividing raw points by 100.
    - **Score Classification**: Flagged investigations as correlated (`is_correlated=True`) if `match_score` is greater than or equal to `0.40` (40% match threshold).
    - **Service Wrapper**: Exposed similarity evaluations via `CampaignCorrelationService.evaluate_link()`.

34. **Campaign Clustering & Drift Splits (Stage 7.3)**:
    - **Indicator Re-homing & Clustering** (`clustering.py`): Implemented `CampaignClusterer` orchestrating clustering operations.
    - **Clustering Rules**:
        1. *CREATE*: Max similarity score < 0.40 threshold. Creates new `Campaign` with ID `CAMP-YYYYMMDD-XXXX`.
        2. *JOIN*: Exactly one correlated campaign. Appends member, increments counts, updates timeline seen bounds, appends fresh infrastructure trace evidence, and extracts TTP tags (`vt-flagged`, `credential-harvesting`, etc.).
        3. *MERGE*: Multiple correlated campaigns. Re-homes all members, merges historical infrastructure traces/TTP tags, upgrades severity, and archives duplicate entities.
    - **Similarity Drift Splitting**: Heuristic BFS component checking in `check_for_split()` evaluates members cohesiveness. Disconnected components are split off, updating original campaign bounds and spawning fresh campaign clusters safely without mutation list index out of range bugs.
    - **Service Integration** (`service.py`): Exposed lifecycle actions through `CampaignCorrelationService.process_investigation(...)` and `check_campaign_drift(...)`.

35. **Campaign Timeline & Relationship Graph (Stage 7.4)**:
    - **Relationship Graph Representation** (`graph_models.py` & `graph_builder.py`): Declared Pydantic models for graph mapping (`GraphNode`, `GraphEdge`, `CampaignGraph`). Created `CampaignGraphBuilder` that traverses campaign members and builds indicator-to-attribute nodes and relationship edges.
    - **Chronological Timeline Generation** (`timeline.py`): Designed `CampaignTimelineService` extracting registration, creation, and association timestamps from campaign metadata, sorting them oldest-to-newest.
    - **Service Integration** (`service.py`): Exposed `get_campaign_graph()` and `get_campaign_timeline()`.

36. **Campaign Database Persistence (Stage 7.5)**:
    - **SQLAlchemy Models** (`db/models/campaign.py`): Created `CampaignRecord` (`campaigns` table) and `CampaignMemberRecord` (`campaign_members` table) ORM models linked with index fields and foreign key cascade rules. Registered tables inside `db/base.py` for automated creation.
    - **Persistence Repository** (`repository.py`): Implemented `CampaignRepository` managing transactional reads and writes: `save_campaign()`, `get_active_campaigns()`, `get_campaign_by_id()`, and `list_campaigns()`. Reconstructs Pydantic domain models dynamically.
    - **Service Integration** (`service.py`): Integrated repository inside `CampaignCorrelationService`. Wired `process_investigation()` and `check_campaign_drift()` to read active records, run clustering and splitting graphs, deactivate merged assets, and persist results.

37. **Campaign REST APIs & E2E Validation (Stage 7.6)**:
    - **FastAPI Endpoints** (`endpoints/campaigns.py`): Created routes for indicator correlation clustering (`POST /api/v1/campaigns/correlate`), listing paginated campaigns (`GET /api/v1/campaigns`), fetching campaign details (`GET /api/v1/campaigns/{campaign_id}`), fetching chronological timeline (`GET /api/v1/campaigns/{campaign_id}/timeline`), and fetching relationship node-link graphs (`GET /api/v1/campaigns/{campaign_id}/graph`). Mounted under versioned router.
    - **E2E Integration Testing** (`test_campaign_e2e.py`): Verified E2E REST API endpoints using FastAPI TestClient; validated A (CREATE) -> B (JOIN) -> list → details → timeline → graph E2E lifecycle runs successfully.







| Provider | URL Lookup | Domain Lookup | IP Lookup | Normalization Logic |
| :--- | :--- | :--- | :--- | :--- |
| **VirusTotal** | Supported | Supported | Unsupported | `malicious` > 0 -> Malicious; `suspicious` > 0 -> Suspicious; `harmless`/`undetected` -> Clean |
| **PhishTank** | Supported | Unsupported | Unsupported | `in_database` and `valid` is True -> Malicious; else -> Clean |
| **URLHaus** | Supported | Unsupported | Unsupported | `query_status == "ok"` -> Malicious; `query_status == "no_results"` -> Clean |
| **AbuseIPDB** | Unsupported | Unsupported | Supported | `abuseConfidenceScore` > 50 -> Malicious; score > 0 -> Suspicious; score == 0 -> Clean |
| **AlienVault OTX** | Supported | Supported | Supported | `pulse_info.count` > 2 -> Malicious; count > 0 -> Suspicious; count == 0 -> Clean |







### Integration Workflow
```
Client Request -> FastAPI Router -> Pydantic Schema Validation -> CRUD Repository Singleton -> SQLAlchemy Session (get_db) -> PostgreSQL Database
```


### Standard HTTP Response Codes
- **`200 OK`**: Successfully retrieved a resource (GET) or updated a resource (PUT).
- **`201 Created`**: Successfully created a resource (POST).
- **`400 Bad Request`**: Malformed request payload or validation errors.
- **`404 Not Found`**: Target resource identifier does not exist.
- **`503 Service Unavailable`**: Backing services (e.g. Postgres DB connection query failures) are unreachable.

### Directory / Folder Structure
```text
backend/app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── ai_assistant.py# AI Assistant API
│   │   │   ├── campaigns.py   # Campaigns API
│   │   │   ├── domains.py     # Domains API
│   │   │   ├── features.py    # Features API
│   │   │   ├── health.py      # Health/Ready Checks
│   │   │   ├── risk_scores.py # Risk Scores API
│   │   │   └── scans.py       # Scans API
│   │   └── router.py          # Assembles all v1 routers
│   ├── deps.py                # Injects get_db and repositories
│   └── router.py              # Root router mounting v1
├── core/
│   ├── config.py
│   └── logging.py
├── db/
│   ├── base_class.py       # Declarative base class Base
│   ├── base.py             # Migration registry index
│   ├── engine.py           # Core engine setup
│   ├── init_db.py          # Table initialization logic
│   ├── models/             # Database ORM models
│   │   ├── __init__.py     # Exports model records
│   │   ├── campaign.py     # Stage 7.5 CampaignRecord and CampaignMemberRecord
│   │   ├── risk_assessment.py # Stage 6.4 RiskScore ORM Persistence
│   │   └── unified_evidence.py# Stage 5.4 UnifiedEvidence ORM Persistence
│   └── session.py          # SessionLocal database sessionmaker factory
├── middleware/
│   ├── logging_middleware.py
│   └── request_id.py
├── integrations/           # Third-party integrations gateway clients
│   └── openrouter/         # OpenRouter provider-agnostic LLM client
│       ├── client.py       # Async HTTP completions client with retries and fallbacks
│       └── provider.py     # Prompt serialization and Pydantic validators
├── models/                 # Database ORM models
│   ├── __init__.py
│   ├── campaign.py
│   ├── domain.py
│   ├── feature.py
│   ├── risk_score.py
│   └── scan.py
├── repositories/           # CRUD data access layers
│   ├── __init__.py         # Exposes repository singletons
│   ├── base.py             # CRUDBase generic base class
│   ├── campaign.py
│   ├── domain.py
│   ├── feature.py
│   ├── risk_score.py
│   └── scan.py
├── schemas/                # Pydantic validation schemas
│   ├── __init__.py
│   ├── campaign.py
│   ├── domain.py
│   ├── feature.py
│   ├── risk_score.py
│   └── scan.py
├── services/               # Modular business logic services
│   ├── ai_assistant/       # AI Investigation Assistant (Stage 8.1 - 8.6)
│   │   ├── __init__.py     # Package exports
│   │   ├── base.py         # BaseAIAssistantService interface
│   │   ├── context_builder.py # InvestigationContextBuilder
│   │   ├── models.py       # Assistant ResponseType and ConversationStatus enums
│   │   ├── reasoning.py    # Stage 8.3 InvestigationReasoningService
│   │   ├── report_generator.py # Stage 8.4 ReportGeneratorService
│   │   ├── reporting_models.py # Stage 8.4 Report validation Pydantic models
│   │   ├── schemas.py      # SuggestedAction, AssistantMessage, InvestigationContext
│   │   └── service.py      # AIAssistantService class orchestrator
│   ├── campaign_engine/    # Campaign Correlation Engine (Stage 7.5/7.6)
│   │   ├── __init__.py     # Exports models, schemas, strategies, service
│   │   ├── base.py         # BaseCorrelationStrategy interface class
│   │   ├── clustering.py   # Stage 7.3 CampaignClusterer engine
│   │   ├── correlators.py  # Stage 7.2 concrete correlator strategies
│   │   ├── graph_builder.py# Stage 7.4 Relationship Graph Builder
│   │   ├── graph_models.py # Stage 7.4 Graph & Timeline schemas
│   │   ├── models.py       # Domain enums & Pydantic models
│   │   ├── repository.py   # Stage 7.5 Campaign SQL Database Repository
│   │   ├── schemas.py      # Ingress validation schemas
│   │   ├── service.py      # CampaignCorrelationService orchestrator
│   │   ├── similarity.py   # Stage 7.2 SimilarityEngine scorer
│   │   └── timeline.py     # Stage 7.4 Timeline Generation Service
│   ├── risk_engine/        # Explainable Risk Engine
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── recommendations.py
│   │   ├── rules.py
│   │   ├── service.py
│   │   └── validator.py
│   ├── threat_intel/       # External Threat Intel feeds
│   │   ├── providers/
│   │   ├── __init__.py
│   │   ├── aggregator.py
│   │   ├── models.py
│   │   └── service.py
│   ├── unified_evidence/   # Evidence Merging, Normalization & Confidence
│   │   ├── __init__.py
│   │   ├── confidence.py
│   │   ├── models.py
│   │   ├── normalizer.py
│   │   ├── service.py
│   │   └── strategy.py
│   ├── domain_intel.py
│   ├── webpage_intel.py
└── main.py

frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css
    ├── adapters/         # Normalizes response models
    ├── components/       # UI Components (Sidebar, Topbar, dashboard, campaign, reports, investigation)
    ├── data/             # Static telemetry datasets
    ├── hooks/            # useDashboard, useScans, useCampaigns, useReports hooks
    ├── layouts/          # Layout wrappers
    ├── providers/        # Context <DataProvider />
    ├── routes/           # Routing configuration
    └── services/         # Asynchronous mock API services
```

38. **AI Assistant Foundation & Models (Stage 8.1)**:
    - **Models and Enums** (`models.py`): Defined `ResponseType` (chat, summary, recommendation) and `ConversationStatus` (active, closed) enums mapping LLM interaction lifecycle details.
    - **Validation Schemas** (`schemas.py`): Created SuggestedAction, AssistantMessage, InvestigationContext, and AssistantResponse validation schemas.
    - **Service Contract Interface** (`base.py`): Declared `BaseAIAssistantService` requiring implementations of `generate_summary(context)` and `chat(context, history, message)`.

39. **Context Builder & Service Stub (Stage 8.2)**:
    - **InvestigationContextBuilder** (`context_builder.py`): Implemented the context aggregator. Resolves input entities (accepting dicts, Pydantic models, or SQL entities) and validates them.
    - **Graceful Error Recovery**: Prevents pipeline crashes on missing datasets (such as WHOIS DNS logs or risk calculations) by serializing them to `"Not Available"` string fallbacks rather than throwing errors.
    - **Dynamic Prompt Assembly Strategy**: The `generate_system_prompt(context)` method translates the structured `InvestigationContext` into a comprehensive system prompt injected with target indicators metadata, risk scoring factors, and coordinated campaign shared infrastructure overlaps.
    - **Service Implementation Stub** (`service.py`): Coded the concrete `AIAssistantService(BaseAIAssistantService)` class. Instantiates the `InvestigationContextBuilder` and returns structured stub answers containing the built prompt length details, ready for actual LLM API integrations.

40. **AI Reasoning Engine (Stage 8.3)**:
    - **Reasoning Service** (`reasoning.py`): Implemented the `InvestigationReasoningService` providing deterministic local context analysis.
    - **Deduplicated Suggested Actions**: Evaluates risk assessments, domain registration age limits (e.g. <=30 days), login form indicators, and campaign footprints to recommend specific mitigation blocks and registry alerts.
    - **Intent-Based Question Routing**: The `answer_question(query, context)` method routes query strings via keyword patterns to resolve explanations for: (1) **Risk & Severity Rationale** (score metrics and fired rule list), (2) **Coordinated Campaigns** (linked members and infrastructure overlaps), (3) **SOC Mitigation Guidelines** (priority action steps), and (4) **General Fallback Summaries**.
    - **Confidence Estimations**: Dynamically computes confidence levels (High/Medium/Low) matching data availability and encloses them directly inside the analyst conversational response blocks.

41. **Report Generator Architecture (Stage 8.4)**:
    - **Reporting Models** (`reporting_models.py`): Defined Pydantic models for report schemas: `EvidenceSummary`, `RecommendationSummary`, `ExecutiveSummary`, and `AnalystReport`.
    - **Report Generator Service** (`report_generator.py`): Implemented the `ReportGeneratorService`.
        - `generate_analyst_report(context)`: Renders full technical reports serializing age metadata, cert validity details, forms metrics, VT verdicts, related campaigns members, action recommendations, and audit timeline event logs.
        - `generate_executive_summary(context)`: Renders corporate-level overviews mapping severity ratings, threat classifications, corporate business impacts, and high-level containment plans.
        - **Graceful Null Traversal**: Leverages defensive coding patterns to fallback to empty values or descriptive strings (e.g. "Isolated outlier") if campaigns, risk details, or timelines are absent.

42. **OpenRouter LLM Integration Architecture (Stage 8.5)**:
    - **OpenRouter Configuration** (`openrouter/config.py`): Maps completions HTTP POST URL (`https://openrouter.ai/api/v1/chat/completions`) and configures request headers containing authorization, referer links, and site titles.
    - **Async httpx Client** (`openrouter/client.py`): Implements `OpenRouterClient` wrapping raw asynchronous HTTP requests. Integrates a 30-second timeout, rate-limit retry loop with backoff, and automatic fallback routing to the fallback model if primary requests fail.
    - **OpenRouter Provider** (`openrouter/provider.py`): Implements `OpenRouterProvider` managing system prompt wrapping and parsing LLM markdown JSON outputs into Pydantic models.
    - **Local Resilience Fallback** (`service.py`): Integrates safety fallbacks inside `AIAssistantService` routing questions and reports to local engines (`InvestigationReasoningService`, `ReportGeneratorService`) if `OPENROUTER_API_KEY` is not set or network errors occur.

43. **AI Assistant REST APIs (Stage 8.6)**:
    - **REST Endpoints** (`endpoints/ai_assistant.py`): Implements three versioned routes:
        - `POST /api/v1/ai/ask` invoking `ask_question`.
        - `POST /api/v1/ai/report/analyst` invoking `get_analyst_report`.
        - `POST /api/v1/ai/report/executive` invoking `get_executive_summary`.
    - **Router Mount** (`router.py`): Registers the AI assistant prefix router in the version 1 core container.

---

## 11. Decision Log

| Date | Decision | Rationale | Alternatives Considered | Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-06 | Choose FastAPI over Django | Lighter footprint, native async support for network requests, autogenerated OpenAPI docs. | Django REST Framework | Approved |
| 2026-08-06 | PostgreSQL + SQLAlchemy | Need robust relational integrity for campaign grouping and cross-evidence linking. | MongoDB | Approved |
| 2026-08-07 | Campaign Correlation Engine Abstractions | Choose strategy pattern interface and decoupled schema/model boundary to allow plugging in diverse similarity matchers (IP, SSL, HTML similarity) in stages without refactoring the core. | Hardcoded monolithic correlation service | Approved |
| 2026-08-07 | Merge Frontend Branch (Task 0) | Establishes a unified monorepo structure to streamline local development, backend/frontend coordination, and end-to-end integration. | Separate repositories with submodule links | Approved |


---

## 12. Risk Register

| Risk ID | Risk Description | Likelihood | Impact | Mitigation Plan |
| :--- | :--- | :--- | :--- | :--- |
| R-001 | Scanning engines get blocked by Cloudflare/Cloudfront on targets | High | High | Rotate scrape proxies and user-agent strings. Fallback to headless browser capture engines. |
| R-002 | AI models take too long to run synchronously | Medium | High | Decouple scanning from response via FastAPI background tasks or a task queue. |

---

## 13. Completed Progress Tracker & Revision History

### Sprint 1
- **2026-08-06 (Sprint 1 - Task 1 - 09:25):** **Task 1 (Boilerplate Structure Setup):** Generated complete project boilerplate and folder structures (`backend/app`, `frontend/src`, `docs`, `config`, `docker`, `tests`, `scripts`), creating the main root setup files (`README.md`, `.gitignore`, `.env.example`, `docker-compose.yml`) and starting documentations template.
- **2026-08-06 (Sprint 1 - Task 2 - 09:41):** **Task 2 (Backend Core Entry Setup):** Set up backend entry points `backend/app/main.py`, the core router `backend/app/api/router.py`, the root endpoint `backend/app/api/endpoints/root.py` and basic `Dockerfile` and `docker-compose.yml` local configs in `backend/` utilizing FastAPI and Uvicorn.
- **2026-08-06 (Sprint 1 - Task 3 - 09:43):** **Task 3 (Centralized Configuration Layer):** Implemented Settings class using Pydantic Settings base validation (`BaseSettings`, `SettingsConfigDict`) to load variables from `.env` dynamically with fallback settings default values.
- **2026-08-06 (Sprint 1 - Task 4 - 09:47):** **Task 4 (Request-Processing Middleware):** Integrated CORSMiddleware, custom `RequestIDMiddleware` (UUID tracking header injection as `X-Request-ID`), and custom timing/response `LoggingMiddleware`.
- **2026-08-06 (Sprint 1 - Task 5 - 09:54):** **Task 5 (Lifespan & Health Check Routers):** Added FastAPI lifespan lifecycle hooks (`Starting/Shutting down ThreatLens API framework...`) and structured versioned health checks endpoints `/health`, `/ready`, `/live` under the `/api/v1` router prefix.
- **2026-08-06 (Sprint 1 - Task 6 - 10:07):** **Task 6 (Database Engine Setup):** Configured core database engine connection pool specifications (`pool_pre_ping=True`, `pool_size`, `max_overflow`), integrating PostgreSQL driver requirements (using psycopg3 adapter).
- **2026-08-06 (Sprint 1 - Task 7 - 10:19):** **Task 7 (ORM Base & Dependencies Setup):** Created SQLAlchemy ORM foundation by designing declarative Base class using `@as_declarative()` with automated table name conversions, audit columns (`id`, `created_at`, `updated_at`), and `get_db()` request-scoped connection generator dependency.
- **2026-08-06 (Sprint 1 - Task 8 - 13:58):** **Task 8 (Feature Progress Documentation Update):** Populated project notes documentation index to track completed backend configuration milestones and implementation changes.
- **2026-08-06 (Sprint 1 - Task 9 - 19:30):** **Task 9 (Database Persistence Layer, ORM Models & Health Check):** Deployed core database relational entities (Domain, Campaign, Scan, Feature, RiskScore ORM models) with cascade rules. Integrated automatic table generation `init_models()` within FastAPI lifespan hooks. Upgraded the `/ready` API health check to dynamically query `SELECT 1` on the session dependency, returning a clean 503 status code on operational db connection exceptions.
- **2026-08-06 (Sprint 1 - Task 10 - 19:42):** **Task 10 (Pydantic Schema Validation & Repository Layer):** Implemented validation layer schemas and data access CRUD repository singletons (inheriting from a generic `CRUDBase` class). Injected repository singletons into the FastAPI dependencies container `deps.py`, ready for endpoints routing. Fully compiled documentation structures and changes.
- **2026-08-06 (Sprint 1 - Task 11 - 19:50):** **Task 11 (Foundational CRUD RESTful API Layer):** Implemented standard RESTful routers mapping GET (lists & detail), POST (201 status), PUT, and DELETE handlers for domains, scans, campaigns, features, and risk scores. Mounted all routers under versioned api tags. Verified the entire compilation and endpoints layout in Swagger Docs.
- **2026-08-06 (Sprint 1 - Task 12 - 20:00):** **Task 12 (Domain Intelligence Extraction Engine - Stage 3.1):** Deployed the domain parser and resolver service (`DomainIntelService`) handling URL normalizations, TLD suffixes parsing via `tldextract`, active A/MX/NS queries via `dnspython`, and creation/expiration tracking via `python-whois`. Exposed the `POST /api/v1/extract/domain` endpoint resolving scan requirements and persisting extracted attributes to database feature records.
- **2026-08-06 (Sprint 1 - Task 13 - 20:10):** **Task 13 (Network & Certificate Intelligence - Stage 3.2):** Implemented `NetworkIntelService` extracting host IP, reverse DNS (PTR pointer lookup), peer SSL/TLS certificate details (issuer, subject, validity timelines, expiry delta, signature algorithms, TLS version, cipher suite) via socket wrapping, and GET connection metadata (status codes, redirects history, final destination URL). Exposed `POST /api/v1/extract/network` saving data to database feature records.
- **2026-08-06 (Sprint 1 - Task 14 - 20:15):** **Task 14 (Webpage Feature Extraction & Aggregation Pipeline - Stage 3.3 & 3.4):** Deployed the webpage structure and element counter (`WebpageIntelService`) pulling page html metadata, form controls, resources, and link metrics using BeautifulSoup. Created orchestration pipeline (`FeatureAggregationService`) that aggregates domain, network, and webpage services safely into a single unified JSON evidence record. Updated `POST /api/v1/extract/domain` endpoint to store the complete aggregated object in the database features registry under key `domain_intel`.
- **2026-08-06 (Sprint 1 - Task 15 - 20:22):** **Task 15 (Feature Extraction API & Finalization - Stage 3.5 & 3.6):** Exposed the complete Feature Extraction engine endpoints: `POST /api/v1/extract/` submitting a URL for full orchestration extraction and saving results; `GET /api/v1/extract/{id}` retrieving extraction evidence by database ID; `GET /api/v1/extract/history/{scan_id}` listing scan history features. Executed final stabilization passes.
- **2026-08-06 (Sprint 1 - Task 16 - 20:50):** **Task 16 (Documentation Enhancement):** Added development rule standards, technology stack classifications, workflow layouts, relationship diagrams, roadmaps, risk-scoring heuristics schemas, and campaign attribution footprints. Synchronized notes index copies.
- **2026-08-06 (Sprint 1 - Task 17 - 21:30):** **Task 17 (Threat Intelligence Foundation - Stage 4.1):** Set up external threat intelligence placeholder keys in configuration. Created `BaseThreatIntelProvider` abstract interfaces using `abc`, common Pydantic response models (`models.py`), and the service registry orchestration pattern (`service.py:ThreatIntelService`) to execute enabled providers concurrently.
- **2026-08-06 (Sprint 1 - Task 18 - 21:40):** **Task 18 (VirusTotal Integration - Stage 4.2):** Implemented `VirusTotalProvider` invoking URL (URL-safe base64 parameters) and Domain lookup endpoints. Mapped analysis category statistics results to common verdicts, extracted engine records details to standard matches, and captured HTTP status exceptions. Updated registry constructor mappings.
- **2026-08-06 (Sprint 1 - Task 19 - 22:00):** **Task 19 (PhishTank & URLHaus Integration - Stage 4.3):** Implemented `PhishTankProvider` and `URLHausProvider` executing POST reputation queries. Mapped database flag rules and query statuses to verdicts, extracted threat names and tags to standardized matches, and handled exceptions.
- **2026-08-06 (Sprint 1 - Task 20 - 22:15):** **Task 20 (AbuseIPDB & AlienVault OTX Integration - Stage 4.4):** Implemented `AbuseIPDBProvider` (IP check API) and `AlienVaultProvider` (Pulse general IP, domain, and URL indicator queries). Integrated both with settings keys and auto-registered inside `ThreatIntelService`. Documented complete Milestone 4 threat intelligence layer.
- **2026-08-06 (Sprint 1 - Task 21 - 22:20):** **Task 21 (PhishTank & URLHaus Header Fixes):** Added descriptive User-Agent string to PhishTank POST requests, and integrated `Auth-Key` parameter for URLHaus. Added safe key checks bypassing queries gracefully when keys are missing.
- **2026-08-06 (Sprint 1 - Task 22 - 22:30):** **Task 22 (Aggregated Threat Evidence Engine & Endpoints - Stage 4.5):** Developed the concurrent multi-threaded lookups aggregator class (`ThreatIntelAggregator`), mapped type auto-detection algorithms, configured overall verdicts consensus rules, exposed lookup REST endpoints (GET/POST mount paths), and integrated the router prefix within FastAPI v1 routes.
- **2026-08-06 (Sprint 1 - Task 23 - 22:45):** **Task 23 (Provider Logic Refactoring - Stage 4.6):** Refactored duplicated lookups scaffolding into standard helper wrappers on `BaseThreatIntelProvider` (safely handling timing, logger scopes, configurations checks, and timing durations logs). Updated all 5 subclasses to leverage base hooks, cleaned registry imports, and added architecture roadmap for Milestone 5.
- **2026-08-06 (Sprint 1 - Task 24 - 23:30):** **Task 24 (Unified Evidence Models & Foundation - Stage 5.1):** Created foundational packages, schemas (`EvidenceCategory`, `EvidenceConfidence`, `EvidenceSource`, `EvidenceMetadata`, `UnifiedEvidence` structures) and interfaces for Unified Evidence module. Configured metadata indicators parameters and placeholder orchestrator service.
- **2026-08-06 (Sprint 1 - Task 25 - 23:45):** **Task 25 (Internal & External Evidence Merge - Stage 5.2):** Implemented `DefaultMergeStrategy` resolving conflicts by prioritizing external threat intel over internal extraction, and deduplicating identical fields. Updated service class to map sources and provider logs dynamically and populate conflict overrides.
- **2026-08-06 (Sprint 1 - Task 26 - 23:55):** **Task 26 (Evidence Normalization & Confidence Engine - Stage 5.3):** Built standard data type standardizer class (`EvidenceNormalizer`) casting boolean states and parsing integers age spans. Developed confidence scoring rules selector (`EvidenceConfidenceEngine`) assigning items confidence levels and overall investigation consensus values.
- **2026-08-06 (Sprint 1 - Task 27 - 00:10):** **Task 27 (Unified Evidence API & Persistence - Stage 5.4 | Milestone 5 COMPLETE):** Created `UnifiedEvidenceRecord` SQLAlchemy ORM model with composite index. Implemented `save_evidence` and `get_evidence_by_indicator` service methods. Exposed `POST /api/v1/unified-evidence/process` and `GET /api/v1/unified-evidence/{indicator}` REST endpoints. Registered router in v1. Milestone 5 (Unified Evidence Engine) fully complete.
- **2026-08-07 (Sprint 1 - Task 28 - 00:25):** **Task 28 (Evidence Timeline & Traceability - Stage 5.5):** Created `EvidenceTimelineBuilder` (`timeline.py`) generating four-phase audit trails (collection → conflict resolution → normalization → confidence scoring). Added `EvidenceEvent` and `AuditTrail` Pydantic models. Integrated timeline builder into `UnifiedEvidenceService.process_evidence` as Step 5; serialized `audit_trail` into `metadata_json` on DB persist. Exposed `GET /api/v1/unified-evidence/timeline?indicator=<…>` endpoint for audit trail retrieval. Stage 5.5 100% complete.
- **2026-08-07 (Sprint 1 - Task 29 - 00:35):** **Task 29 (Unified Evidence Engine Finalization & Refactoring - Stage 5.6 | Milestone 5 FINAL):** Performed end-to-end refactoring of all 5 module files. Standardized logging (INFO for lifecycle events, DEBUG for granular detail) across `strategy.py`, `normalizer.py`, `confidence.py`, `timeline.py`, and `service.py`. Added outer try/except pipeline guard in `service.py`. Fixed Python <3.10 type union syntax in `timeline.py`. Extracted private helpers to eliminate code duplication. Replaced list-based key lookups with frozensets. Stage 5.6 and Milestone 5 (Unified Evidence Engine) 100% FINAL.
- **2026-08-07 (Sprint 1 - Task 30 - 05:30):** **Task 30 (Risk Scoring Engine Foundation + Core Logic - Stages 6.1 & 6.2):** Created `app/services/risk_engine/` package. Defined `RiskSeverity`, `RiskFactor`, `RiskBreakdown`, `RiskScore` Pydantic models. Built `BaseRiskEvaluator` ABC with `safe_evaluate()` wrapper. Implemented 5 weighted evaluators (`DomainIntelEvaluator`, `DnsWhoisEvaluator`, `TlsCertificateEvaluator`, `HtmlContentEvaluator`, `ThreatIntelEvaluator`) with total 100-pt weight budget. Built `RiskScoringService` with dynamic denominator, 0-100 normalization, severity mapping, and explainability. Verified 3 test scenarios: HIGH (75/100), SAFE (0/100), MEDIUM (45/100). Stages 6.1 & 6.2 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 31 - 05:40):** **Task 31 (Risk Engine Recommendations, Persistence & API - Stages 6.3 & 6.4 | Milestone 6 FINAL):** Added `Recommendation` Pydantic model to `models.py`; extended `RiskScore.recommendations` field. Created `RecommendationEngine` (`recommendations.py`) with 20 factor-level rules + severity catch-alls, deduplication, and priority sorting. Integrated as Step 6 in `RiskScoringService.calculate_risk()`. Created `RiskAssessmentRecord` SQLAlchemy ORM model with JSON breakdown/recommendations columns and composite index. Registered in `db/base.py`. Exposed `POST /api/v1/risk/evaluate` and `GET /api/v1/risk/{indicator:path}` endpoints; registered router in v1. Verified pipeline end-to-end: 4 factors fired, 5 recommendations generated (1×immediate, 3×high, 1×medium). Stages 6.3 & 6.4 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 32 - 05:45):** **Task 32 (Risk Engine Validation & Calibration - Stage 6.5):** Created `config.py` extracting all weights, confidence multipliers, severity thresholds, and category key maps into centralized config. Created `RiskValidator` (`validator.py`) with `validate_evidence()` (empty/null guard), `calibrate_score()` (confidence multiplier), and `enforce_boundaries()` (NaN/clamp). Updated `rules.py` to import weights from `config.RISK_WEIGHTS`. Updated `service.py` with 10-step pipeline (Steps 0/4/5 = validation/calibration/boundaries). Verified 5 edge-case scenarios: HIGH→63.5, LOW→38.1 (calibrated), empty→0.0, all-null→0.0, MEDIUM→51.0 (calibrated). Stage 6.5 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 33 - 05:55):** **Task 33 (Risk Engine Refactoring, Logging & Finalization - Stage 6.6 | Milestone 6 FINAL):** Refactored codebase for Milestone 6 completion. Removed unused variables and dead parameters (`_SEVERITY_MAP` in `service.py`, `_CATEGORY_CAP` in `rules.py`). Standardized lifecycle logs at `INFO` and engine rule evaluations at `DEBUG`. Wrapped the database transaction logic in `risk.py` with explicit try/except/rollback controls raising standard `HTTPException(500)`. Stages 6.1–6.6 and Milestone 6 (Risk Scoring Engine) 100% FINAL.
- **2026-08-07 (Sprint 1 - Task 34 - 06:10):** **Task 34 (Campaign Correlation Foundation - Stage 7.1):** Created modular campaign engine directory structure under `services/campaign_engine/`. Defined core Pydantic domain models (`Campaign`, `CampaignMember`, `CorrelationEvidence`, `CorrelationResult`, `CampaignSummary`) and severity/status enums. Formulated Pydantic ingress/egress validation schemas. Drafted strategy pattern interface (`BaseCorrelationStrategy`). Coded `CampaignCorrelationService` orchestrating stubs for campaign resolution, creation, and indicator allocation. Verification test script validated all structures import, load, and serialize cleanly. Stage 7.1 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 35 - 06:15):** **Task 35 (Core Campaign Similarity Matcher - Stage 7.2):** Implemented core pairwise correlators (`InfrastructureCorrelator`, `TlsCorrelator`, `WhoisCorrelator`, and `HtmlCorrelator`) in `correlators.py`. Created `SimilarityEngine` (`similarity.py`) registering all strategies, executing pairwise scans, summing weights (IP=25, DNS=10, ASN=5, TLS Serial=20, TLS Subject=5, TLS Issuer=5, Registrant Org=8, Registrar=4, Creation Date=3, Page Title=8, HTML Hash=5, Forms Count=2), and classifying correlation if match_score >= 0.40. Integrated similarity scoring inside `CampaignCorrelationService.evaluate_link()`. Verification test script validated all pairwise matches and scoring calculations correctly. Stage 7.2 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 36 - 06:20):** **Task 36 (Campaign Clustering & Attribution - Stage 7.3):** Coded `CampaignClusterer` (`clustering.py`) with `cluster_indicator()` evaluating incoming observations against active campaigns. Programmed actions logic (CREATE for unmatched, JOIN for single match, MERGE for multi-matches), tracking attribution and re-homing indicators, summaries, and tags. Implemented BFS component graph partitioning inside `check_for_split()` resolving similarity drift/splitting. Integrated methods inside `service.py`. Stage 7.3 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 37 - 06:25):** **Task 37 (Campaign Timeline & Graph Engines - Stage 7.4):** Created `graph_models.py` (declaring `GraphNode`, `GraphEdge`, `CampaignGraph`, `TimelineEvent`, `CampaignTimeline`), `graph_builder.py` (`CampaignGraphBuilder` generating bipartite node-edge mapping indicators to IPs/certificates/registrars/layout hashes), and `timeline.py` (`CampaignTimelineService` extracting WHOIS, association, and campaign start datetimes and sorting them oldest-to-newest). Mounted methods on `CampaignCorrelationService`. Stage 7.4 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 38 - 06:30):** **Task 38 (Campaign Persistence Schema & Repository - Stage 7.5):** Created ORM tables `campaigns` and `campaign_members` (`db/models/campaign.py`) linked with cascades. Registered in `db/base.py`. Created `CampaignRepository` (`repository.py`) managing transactional CRUD operations (`save_campaign`, `get_active_campaigns`, `get_campaign_by_id`, `list_campaigns`) converting SQLAlchemy records to Pydantic objects. Integrated repository into `CampaignCorrelationService.process_investigation()` and `check_campaign_drift()`. Stage 7.5 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 39 - 06:35):** **Task 39 (Campaign REST APIs & E2E Validation - Stage 7.6 | Milestone 7 COMPLETE):** Created REST API endpoints in `endpoints/campaigns.py` mounting POST `/correlate` and GET listing, detail, timeline, and graph routes. Registered router in v1 router. E2E integration test script verified full correlate CREATE/JOIN flow and retrieve list/detail/graph/timeline responses successfully via TestClient. Milestone 7 fully COMPLETE.
- **2026-08-07 (Sprint 1 - Task 40 - 06:45):** **Task 40 (AI Assistant Foundation & Models - Stage 8.1):** Set up `ai_assistant/` directory. Defined ResponseType/ConversationStatus enums in `models.py` and SuggestedAction/AssistantMessage/InvestigationContext/AssistantResponse validation schemas in `schemas.py`. Created abstract interface `BaseAIAssistantService` in `base.py`. Stage 8.1 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 41 - 07:00):** **Task 41 (Context Builder & Service Stub - Stage 8.2):** Implemented `InvestigationContextBuilder` in `context_builder.py` aggregating and serializing evidence/risk/campaign details into a structured system prompt, defaulting missing fields to "Not Available" gracefully. Coded concrete `AIAssistantService` stub in `service.py` verifying context and prompt lengths. Package exports declared in `__init__.py`. Tested verification script cleanly. Stage 8.2 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 42 - 07:15):** **Task 42 (AI Reasoning Engine - Stage 8.3):** Implemented `InvestigationReasoningService` providing keyword routing for SOC questions ("Why is this URL risky?", "What infrastructure is shared?", "What should an analyst investigate next?") with confidence estimations, and SuggestedAction mapping logic. Stage 8.3 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 43 - 07:30):** **Task 43 (Report Generator - Stage 8.4):** Created `reporting_models.py` defining Pydantic report schemas and `ReportGeneratorService` generating ExecutiveSummary and AnalystReport payloads with defensive code for handling missing context properties gracefully. Stage 8.4 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 44 - 07:45):** **Task 44 (OpenRouter Client & Provider Integration - Stage 8.5):** Implemented `OpenRouterClient` (`client.py`) executing async HTTP completions via `httpx` with timeout parameters, rate-limit retry logic, and fallback model capabilities. Programmed `OpenRouterProvider` (`provider.py`) compiling prompt parameters and parsing LLM outputs into Pydantic report schemas. Refactored `AIAssistantService` to direct reasoning and reports dynamically, falling back to local deterministic engines on OpenRouter errors or when credentials are not configured. Stage 8.5 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 46 - 08:10):** **Task 46 (Dashboard Stage 1 - Frontend Shell - Task 20):** Built the complete, responsive SOC-themed React frontend shell. Wired up index.html, index.css, main.jsx, and App.jsx. Centralized routes utilizing React Router v6 mapping to coming-soon placeholders for Dashboard, Scans, Campaigns, Reports, and Settings. Created AppLayout with Sidebar navigation highlights, brand sky-blue theme configs, and Topbar featuring responsive mobile drawer toggle controls.
- **2026-08-07 (Sprint 1 - Task 47 - 08:15):** **Task 47 (Dashboard Stage 2 - Static Dashboard - Task 21):** Implemented complete static SOC analytics dashboard. Set up static telemetry datasets in `src/data/dashboardData.js` representing KPI cards, domain scan logs, risk bands, campaign distributions, timeline events, threat highlights, and offline readiness panels. Built modular components (KPICard, RiskChart, RecentScansTable, CampaignOverview, ThreatTimeline, ThreatSummary, StatusPanel) inside `src/components/dashboard/` and integrated them into `Dashboard.jsx`. Wrote reusable RiskScoreBadge and StatusPill components to color-code risk elements. Verified production-ready compilation.
- **2026-08-07 (Sprint 1 - Task 48 - 08:20):** **Task 48 (Dashboard Stage 3 - Investigation Workspace - Task 22):** Created the static analyst URL investigation workspace. Added a static telemetry dataset in `src/data/investigationData.js` representing registrar details, A/MX DNS records, WHOIS timestamps, SSL certificate handshakes, HTML tag attributes, response metadata, and threat badges flags. Built modular UI components (URLInputCard, ScanStatus, RiskSummary, ExplanationPanel, EvidenceAccordion, BadgeGroup) inside `src/components/investigation/` and integrated them into the new `Investigation.jsx` workspace page, which uses a 1-second state transition delay to simulate pre-flight loading animations. Re-mapped the `/scans` route to the new workspace.
- **2026-08-07 (Sprint 1 - Task 49 - 08:25):** **Task 49 (Dashboard Stage 4 - Campaigns Workspace - Task 23):** Created the static campaigns attribution workspace. Configured the static data file `src/data/campaignData.js` representing campaigns, connected domains lists, shared IP structures, DNS parameters, nameservers, SSL fingerprints, WHOIS similarity matrices, and attacker setups history timeline. Built modular components (CampaignSummaryCard, RelationshipGraph, ConnectedDomainsTable, InfrastructureCard, EvidenceTable, ConfidenceCard, CampaignTimeline) inside `src/components/campaign/` and integrated them into the dashboard layout inside `Campaigns.jsx`. Wrote a custom SVG threat topology graph to link nodes. Marked Campaign Correlation status as Completed.
- **2026-08-07 (Sprint 1 - Task 50 - 08:30):** **Task 50 (Dashboard Stage 5 - Reports Workspace - Task 24):** Created the static reports and external threat intelligence preview dashboard. Configured the static data file `src/data/threatIntelligenceData.js` representing VirusTotal community metrics, PhishTank indicators, URLHaus categories, AbuseIPDB reports, campaign IOC lists, overall reputation score gauges, SIEM action checklists, and mock Incident Reports previews. Built modular components (ThreatFeedPanel, IOCTable, ReputationCard, RecommendationsPanel, IncidentReportPreview, ExportPreview) inside `src/components/reports/` and integrated them into the dashboard layout inside `Reports.jsx`. Marked Reporting status as Completed.
- **2026-08-07 (Sprint 1 - Task 51 - 08:35):** **Task 51 (Dashboard Stage 6 - Data Layer - Task 25):** Refactored the frontend architecture to introduce a centralized data layer. Created asynchronous mock API services in `src/services/` (dashboardService, scanService, campaignService, reportService, mockApi) resolving after 300-1200ms latency. Introduced data adapters in `src/adapters/` (dashboardAdapter, scanAdapter, campaignAdapter, reportAdapter) to normalize response models. Defined core JSDoc model contracts in `src/interfaces/index.js`. Created centralized context `<DataProvider />` in `src/providers/` and custom hooks `useDashboard`, `useScans`, `useCampaigns`, and `useReports` in `src/hooks/` to eliminate direct JSON imports. Added `<SkeletonLoader />` pulsing placeholders and `<ErrorFallback />` retry components.
- **2026-08-07 (Sprint 1 - Task 52 - 08:40):** **Task 52 (SVG Runtime Error Fix - Task 26):** Fixed the persistent browser console warning `Error: <path> attribute d: Expected number`. Traced the root cause to malformed SVG path arc data inside `RiskChart.jsx` (threat risk pie slices), `Dashboard.jsx` (active-campaigns and threat-sources icons), and `ThreatFeedPanel.jsx` (external feeds icon) where the large-arc-flag and sweep-flag properties were not spaced correctly relative to the coordinates parameters. Resolved the layout issue by introducing spacing. Verified production-ready compile and verified console is error-free.
- **2026-08-07 (Sprint 1 - Task 53 - 08:45):** **Task 53 (SVG Document Icon Fix - Task 27):** Completely eliminated the persistent browser console warning `Error: <path> attribute d: Expected number` in document-style icons. Traced the root cause to two malformed paths: (1) a missing `h` command in the standard document icon inside `RecentScansTable.jsx`, `IOCTable.jsx`, and `RecommendationsPanel.jsx`; and (2) unspaced arc parameters inside `Sidebar.jsx`, `RecommendationsPanel.jsx`, and `ExplanationPanel.jsx`. Corrected all paths to fully space all arguments and restore the missing `h` character. Verified compilation succeeds cleanly and the console has zero remaining warnings.
- **2026-08-07 (Sprint 1 - Task 54 - 08:50):** **Task 54 (Monorepo Integration - Task 0):** Merged remote branch `origin/frontend` into `main`, resolving documentation and progress tracker conflicts. Validated backend startup and verified frontend dependencies installation. Established a unified monorepo structure. Task 0 100% COMPLETE.










---

## 14. Verification Checklist for Manual Testing

Ensure the local PostgreSQL database is running, then run the following checks:
1. **Server Startup**: Run `uvicorn app.main:app --reload` and check that database tables initialization triggers successfully.
2. **Readiness Check**: Hit `GET /api/v1/health/ready` and confirm `{"status":"ready","checks":{"app":"ok","database":"ok"}}` is returned with `200 OK`.
3. **Interactive OpenAPI Docs**: Navigate to `http://127.0.0.1:8000/docs` and confirm the 6 core resource groups (`Domains`, `Scans`, `Campaigns`, `Features`, `Risk Scores`, `Feature Extraction`) show the endpoint actions.
4. **Validation Test**: Try sending a `POST /api/v1/domains` request with a missing required parameter (e.g. omitting `url`) and verify that FastAPI throws a `422 Unprocessable Entity` validation error response.
5. **Operational Verification**: Try a `GET /api/v1/domains/999` and verify that the system correctly catches the null response and raises a `404 Not Found` response code.
6. **Feature Extraction Verification**: Submit a `POST /api/v1/extract/` with payload `{"url": "https://google.com", "scan_id": 1}` and verify it triggers the full aggregation pipeline (returning domain_intelligence, network_intelligence, webpage_intelligence, and metadata schemas) and returns a HTTP 201 status code with the complete JSON dataset.
7. **Evidence Retrival Verification**: Query `GET /api/v1/extract/{feature_id}` (e.g., ID 1) and confirm it returns the saved `FeatureResponse` details.
8. **Extraction History Verification**: Query `GET /api/v1/extract/history/{scan_id}` (e.g., Scan ID 1) and confirm it returns the list of all extraction records associated with that scan.

