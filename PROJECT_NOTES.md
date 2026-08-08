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
| **Completed** | Dashboard UI | React SPA with all five pages (Dashboard, Investigation, Campaigns, Reports, Settings) fully built and rendering with live backend integration. |
| **Completed** | Reporting | Exportable Markdown/PDF reports detailing threat evidence. |
| **Completed** | Scans UI & Workflows | Submission form, progress polling indicator, and detailed Investigation Details views wired to live API endpoints. |
| **Completed** | Frontend API Integration | Replace all mock data services (Campaigns, Reports, Settings, Dashboard, Scans, Details) with real backend REST calls. Purged all static mock JSON structures from the repository. |
| **Completed** | E2E Validation | Verified complete end-to-end flows in a local running environment. |
| **Completed** | Demo Dataset Generation | Standalone SQLAlchemy script (`seed_demo_data.py`) generated 15 realistic investigation scenarios and 2 campaign clusters. |
| **Completed** | System Validation | Validation script (`validate_backend.py`) verifies readiness, scans, evidence, risk, campaigns, and AI report endpoints. |
| **Completed** | Frontend Audits & UX | Audit of all 5 SPA pages. Cleaned up error boundaries, empty states, and dynamic load spinners (Stage B.3). |
| **Completed** | E2E System Validation | Executed complete typosquatting and impersonation workflows from target submission to final reports (Stage B.4). |
| **Remaining** | Brand Intelligence | Favicon hash, page template text similarity, visual logo detection. |
| **Remaining** | Deployment | Final packaging and cloud/docker deployment patterns. |
| ✅ **LOCKED** | Backend Architecture | All 8 milestones complete. NO new backend endpoints or architectural changes will be introduced. |
| ✅ **LOCKED** | Frontend Integration | Phase A (Stages A.1 - A.6) fully complete and validated. |
| ✅ **LOCKED** | Demo Dataset & Validation | Phase B (Stages B.1 - B.4) fully seeded, validated, and demo-playbook compiled. Platform is 100% complete and demo-ready. |
| ✅ **LOCKED** | Auth & Audit Integration | Authentication login system, protected routing, and post-merge regression validation 100% completed. |
| ✅ **LOCKED** | Role-Based Access Control | Organziational RBAC controls, brute-force locking, account security, and token lifecycles fully implemented. |
| ✅ **LOCKED** | Session Mgmt & Activity Audit | Session management, automatic timeout redirections, and analyst activity database logging fully completed. |
| ✅ **LOCKED** | Navigation & Route Recovery | All protected routes restored, deep-links validated, and sidebar synchronization completed. |


---

## 2. Complete Technology Stack

### Frontend
- **React**: Single page application framework.
- **Vite**: Rapid frontend builder and server.
- **TailwindCSS**: CSS framework for modern design aesthetics.
- **Axios** (`^1.4.0`): HTTP client used for all backend API calls.

### Frontend API Networking Layer (`frontend/src/api/`)
| File | Purpose |
| :--- | :--- |
| `.env` | `VITE_API_BASE_URL` — single env variable pointing to `http://localhost:8000/api/v1` |
| `api/client.js` | Singleton Axios instance with `baseURL`, 30s timeout, JSON headers, request/response interceptors |
| `api/errorHandler.js` | `normalizeError()` — converts raw AxiosError into canonical `ApiError` object; handles FastAPI 422 arrays, network failures, and all 4xx/5xx codes |
| `api/types.js` | JSDoc type definitions: `ApiError`, `FastApiValidationError`, `PaginationParams`, `PaginatedResponse<T>` |
| `api/index.js` | Barrel file — re-exports `apiClient`, `normalizeError`, `isApiError` for convenient imports |

**Interceptor chain**:
```
Request ──► Log outgoing call (dev only) ──► Forward to backend
Response ──► Unwrap response.data ──► Return plain object to caller
         └─► On error: normalizeError() ──► re-throw ApiError
```

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
| 2026-08-07 | Use Axios as the frontend HTTP client (Stage A.1) | Axios was already present as a project dependency (`^1.4.0`). It provides interceptors for global request/response transformation, structured error objects, timeout support, and automatic JSON serialization — all required for the ThreatLens integration layer. The response interceptor unwraps `response.data` directly, so service files receive plain objects. All HTTP errors are normalized via `normalizeError()` into a canonical `ApiError` shape before reaching any React component. | fetch() with manual wrapper, SWR, React Query | Approved |
| 2026-08-07 | Dashboard uses `Promise.allSettled()` for parallel fetching (Stage A.2) | The dashboard requires data from three endpoints (scans, campaigns, risk-scores). Using `Promise.allSettled()` instead of `Promise.all()` ensures the dashboard remains partially functional if one endpoint returns an error (e.g., risk-scores table empty). Individual fetch failures return empty arrays; only a total backend outage surfaces a full ErrorFallback. The adapter layer (`adaptDashboardData`) is unchanged — only the data source changed. | Promise.all() with total failure, sequential fetching | Approved |
| 2026-08-07 | Orchestrated client-driven background analysis for scans (Stage A.3) | Since the backend FastAPI API handles all steps (extraction, merging, risk evaluation) synchronously and does not use a background worker queue, we kick off the orchestration pipeline sequentially from the client background using Axios, and update the scan record status (`pending` -> `scanning` -> `completed`/`failed`) in the database. This allows the frontend to poll `GET /scans/{id}` to track analysis progress without blocking. | Synchronous blocking client requests | Approved |
| 2026-08-07 | Pre-generate AI reports on completed scan loads (Stage A.4) | On loading the completed investigation details view, the page queries `/ai/report/analyst` and `/ai/report/executive` in parallel with the latest evidence and risk state. This ensures that pre-computed LLM verdicts are ready immediately when the analyst toggles between the Analyst and Executive views. | Generate AI report only on demand/button click | Approved |
| 2026-08-07 | Dynamic SVG node position calculator for graph (Stage A.5) | Calculating dynamic node coordinates based on the count of indicators (left side) and infrastructure properties (right side) returned by `GET /campaigns/{id}/graph` prevents visual overlaps and adjusts layouts dynamically when campaigns scale or merge. | Hardcoded node positions | Approved |
| 2026-08-07 | Tabbed Q&A Chat & Reports Layout (Stage A.6) | Placing both the live LLM Chat interface and the static pre-generated reports side-by-side inside the details panel allows analysts to easily toggle between reading high-level executive conclusions and doing active deep-dive Q&A forensics. | Separate page for AI Assistant chatbot | Approved |
| 2026-08-07 | Client-side Mock JWT Auth Flow | To secure operational screens, mock JWT tokens are generated, signed, and validated on the client side with role/permission attributes. Secure paths are guarded via a `<ProtectedRoute>` component intercepting unauthorized access attempts. | Session-based state, Server auth integration | Approved |
| 2026-08-07 | Campaign ID Persistence in Repository | Assigning `campaign.id = record.id` dynamically after PostgreSQL transaction commit ensures that returned campaign entities retain their primary key database ID, resolving downstream Pydantic `CorrelateResponse` validator requirements. | Cast type to dynamic dict, Remove id field | Approved |

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
- **2026-08-07 (Sprint 1 - Task 45 - 08:00):** **Task 45 (AI Assistant REST APIs - Stage 8.6):** Created versioned endpoint controllers (`endpoints/ai_assistant.py`) mounting `POST /ai/ask`, `POST /ai/report/analyst`, and `POST /ai/report/executive` routes. Registered routes in version 1 core router. Tested all API workflows via FastAPI TestClient validating fallback modes and schema validations. Stage 8.6 & Milestone 8 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 46 - 08:10):** **Task 46 (Dashboard Stage 1 - Frontend Shell - Task 20):** Built the complete, responsive SOC-themed React frontend shell. Wired up index.html, index.css, main.jsx, and App.jsx. Centralized routes utilizing React Router v6 mapping to coming-soon placeholders for Dashboard, Scans, Campaigns, Reports, and Settings. Created AppLayout with Sidebar navigation highlights, brand sky-blue theme configs, and Topbar featuring responsive mobile drawer toggle controls.
- **2026-08-07 (Sprint 1 - Task 47 - 08:15):** **Task 47 (Dashboard Stage 2 - Static Dashboard - Task 21):** Implemented complete static SOC analytics dashboard. Set up static telemetry datasets in `src/data/dashboardData.js` representing KPI cards, domain scan logs, risk bands, campaign distributions, timeline events, threat highlights, and offline readiness panels. Built modular components (KPICard, RiskChart, RecentScansTable, CampaignOverview, ThreatTimeline, ThreatSummary, StatusPanel) inside `src/components/dashboard/` and integrated them into `Dashboard.jsx`. Wrote reusable RiskScoreBadge and StatusPill components to color-code risk elements. Verified production-ready compilation.
- **2026-08-07 (Sprint 1 - Task 48 - 08:20):** **Task 48 (Dashboard Stage 3 - Investigation Workspace - Task 22):** Created the static analyst URL investigation workspace. Added a static telemetry dataset in `src/data/investigationData.js` representing registrar details, A/MX DNS records, WHOIS timestamps, SSL certificate handshakes, HTML tag attributes, response metadata, and threat badges flags. Built modular UI components (URLInputCard, ScanStatus, RiskSummary, ExplanationPanel, EvidenceAccordion, BadgeGroup) inside `src/components/investigation/` and integrated them into the new `Investigation.jsx` workspace page, which uses a 1-second state transition delay to simulate pre-flight loading animations. Re-mapped the `/scans` route to the new workspace.
- **2026-08-07 (Sprint 1 - Task 49 - 08:25):** **Task 49 (Dashboard Stage 4 - Campaigns Workspace - Task 23):** Created the static campaigns attribution workspace. Configured the static data file `src/data/campaignData.js` representing campaigns, connected domains lists, shared IP structures, DNS parameters, nameservers, SSL fingerprints, WHOIS similarity matrices, and attacker setups history timeline. Built modular components (CampaignSummaryCard, RelationshipGraph, ConnectedDomainsTable, InfrastructureCard, EvidenceTable, ConfidenceCard, CampaignTimeline) inside `src/components/campaign/` and integrated them into the dashboard layout inside `Campaigns.jsx`. Wrote a custom SVG threat topology graph to link nodes. Marked Campaign Correlation status as Completed.
- **2026-08-07 (Sprint 1 - Task 50 - 08:30):** **Task 50 (Dashboard Stage 5 - Reports Workspace - Task 24):** Created the static reports and external threat intelligence preview dashboard. Configured the static data file `src/data/threatIntelligenceData.js` representing VirusTotal community metrics, PhishTank indicators, URLHaus categories, AbuseIPDB reports, campaign IOC lists, overall reputation score gauges, SIEM action checklists, and mock Incident Reports previews. Built modular components (ThreatFeedPanel, IOCTable, ReputationCard, RecommendationsPanel, IncidentReportPreview, ExportPreview) inside `src/components/reports/` and integrated them into the dashboard layout inside `Reports.jsx`. Marked Reporting status as Completed.
- **2026-08-07 (Sprint 1 - Task 51 - 08:35):** **Task 51 (Dashboard Stage 6 - Data Layer - Task 25):** Refactored the frontend architecture to introduce a centralized data layer. Created asynchronous mock API services in `src/services/` (dashboardService, scanService, campaignService, reportService, mockApi) resolving after 300-1200ms latency. Introduced data adapters in `src/adapters/` (dashboardAdapter, scanAdapter, campaignAdapter, reportAdapter) to normalize response models. Defined core JSDoc model contracts in `src/interfaces/index.js`. Created centralized context `<DataProvider />` in `src/providers/` and custom hooks `useDashboard`, `useScans`, `useCampaigns`, and `useReports` in `src/hooks/` to eliminate direct JSON imports. Added `<SkeletonLoader />` pulsing placeholders and `<ErrorFallback />` retry components.
- **2026-08-07 (Sprint 1 - Task 52 - 08:40):** **Task 52 (SVG Runtime Error Fix - Task 26):** Fixed the persistent browser console warning `Error: <path> attribute d: Expected number`. Traced the root cause to malformed SVG path arc data inside `RiskChart.jsx` (threat risk pie slices), `Dashboard.jsx` (active-campaigns and threat-sources icons), and `ThreatFeedPanel.jsx` (external feeds icon) where the large-arc-flag and sweep-flag properties were not spaced correctly relative to the coordinates parameters. Resolved the layout issue by introducing spacing. Verified production-ready compile and verified console is error-free.
- **2026-08-07 (Sprint 1 - Task 53 - 08:45):** **Task 53 (SVG Document Icon Fix - Task 27):** Completely eliminated the persistent browser console warning `Error: <path> attribute d: Expected number` in document-style icons. Traced the root cause to two malformed paths: (1) a missing `h` command in the standard document icon inside `RecentScansTable.jsx`, `IOCTable.jsx`, and `RecommendationsPanel.jsx`; and (2) unspaced arc parameters inside `Sidebar.jsx`, `RecommendationsPanel.jsx`, and `ExplanationPanel.jsx`. Corrected all paths to fully space all arguments and restore the missing `h` character. Verified compilation succeeds cleanly and the console has zero remaining warnings.
- **2026-08-07 (Sprint 1 - Task 54 - 08:50):** **Task 54 (Monorepo Integration - Task 0):** Merged remote branch `origin/frontend` into `main`, resolving documentation and progress tracker conflicts. Validated backend startup and verified frontend dependencies installation. Established a unified monorepo structure. Task 0 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 55 - 09:00):** **Task 55 (Familiarization & Validation - Tasks 1, 2, 3):** Completed system architecture and monorepo codebase validation. Documented model persistence structure splits and compiled the frontend mock data endpoints mapping inside `PROJECT_NOTES.md`. Tasks 1, 2, and 3 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 56 - 09:10):** **Task 56 (Backend-Frontend API Mapping - Task 4):** Authored the comprehensive "Backend-Frontend API Mapping" section (Section 16) in `PROJECT_NOTES.md`. Defined endpoint contracts, request/response models, and all required UI states (loading, error, empty, highlight) for all 7 frontend surfaces: Dashboard, Investigation, Campaigns, AI Assistant, Reports, Risk Details Panel, and Evidence Viewer. Task 4 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 57 - 09:15):** **Task 57 (Development Rules & Focus Pivot - Tasks 5, 6, 7):** Authored the "Strict Development Rules" section (Section 17) in `PROJECT_NOTES.md` covering 12 binding rules across Architecture, Frontend Integration, and Documentation categories. Updated the "Current Development Status" table to mark Backend Architecture as LOCKED (all 8 milestones complete) and Frontend API Integration + E2E Validation as the active development focus. Tasks 5, 6, and 7 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 58 - 09:25):** **Task 58 (Frontend API Foundation - Stage A.1):** Established the centralized Axios HTTP client layer under `frontend/src/api/`. Created `frontend/.env` with `VITE_API_BASE_URL=http://localhost:8000/api/v1`. Created `api/client.js` — singleton Axios instance with `baseURL`, 30s timeout, JSON headers, dev-mode request logger, and response interceptor that unwraps `response.data` on success. Created `api/errorHandler.js` with `normalizeError()` converting raw AxiosErrors into structured `ApiError` objects (handles FastAPI 422 validation arrays, network errors, and all 4xx/5xx codes). Created `api/types.js` with JSDoc type contracts (`ApiError`, `FastApiValidationError`, `PaginationParams`, `PaginatedResponse<T>`). Created `api/index.js` barrel file. Verified `npm run build` compiles with zero errors. Documented API networking layer in tech stack and architecture sections. Stage A.1 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 59 - 09:35):** **Task 59 (Dashboard API Integration - Stage A.2):** Replaced all mock data in the Dashboard with live FastAPI backend calls. Created `api/dashboardApiService.js` — fetches `GET /api/v1/scans/`, `GET /api/v1/campaigns/`, `GET /api/v1/risk-scores/`, and `GET /api/v1/health/ready` in parallel using `Promise.allSettled()` (individual failures return empty arrays, not crashes). Assembles KPIs, scans table rows, risk distribution bands, campaign overview buckets, event timeline, threat summary highlights, and service status dots from raw backend responses. Updated `services/dashboardService.js` to call `getDashboardData()` instead of mock JSON. Updated `providers/DataProvider.jsx` to import `isApiError()` and extract structured `ApiError` messages. Adapter contract (`adaptDashboardData`) preserved intact. Verified `npm run build` passes cleanly (147 modules, 0 errors). Stage A.2 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 60 - 09:45):** **Task 60 (Scan Submission & Progress Polling - Stage A.3):** Built submission and history logs workspace. Mapped `/scans` route to the new `Scans.jsx` page. Implemented URL validation and client-side background scan task scheduling inside `api/investigationService.js`. When a URL is submitted, we create database entries, invoke `submitInvestigation(url)` (POST), and execute the sequential backend extraction + merging + scoring pipeline in the background. The component polls `getInvestigationStatus(id)` every 1 second, updating the steps tracker (`ScanStatus`), and routes the analyst to the details page `/scans/:id` on completion. Stage A.3 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 61 - 10:00):** **Task 61 (Detailed Investigation View & Evidence - Stage A.4):** Created `InvestigationDetails.jsx` details page. Fetches full scan payload via `getInvestigationDetails(id)` on mount. Maps backend `resolved_observations` into individual section tables (Domain, DNS, WHOIS, SSL, HTML, Metadata) rendered in the `EvidenceAccordion`. Populates risk dial scores, findings tags, campaign overlaps, and parallel pre-generated AI summaries (Analyst technical reports + Executive summaries). Handled loading skeletons, try-catch connection blocks, and clean fallback arrays. Verified `npm run build` passes cleanly with 0 errors. Stage A.4 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 62 - 10:15):** **Task 62 (Campaign Intelligence Integration - Stage A.5):** Created `api/campaignService.js` and updated `services/campaignService.js` to fetch live data from `/campaigns/` list and detailed `/campaigns/{id}/graph` & `/campaigns/{id}/timeline` endpoints. Refactored `RelationshipGraph.jsx` to dynamically assign node coordinates (indicators on left, infrastructure assets on right) and render SVG lines using live API responses. Handled empty-states, loaders, and error fallbacks. Stage A.5 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 63 - 10:30):** **Task 63 (AI Assistant & Reports Integration - Stage A.6):** Created `api/aiService.js` connecting to `/ai/ask`, `/ai/report/analyst`, and `/ai/report/executive`. Developed interactive `AiAssistantChat.jsx` conversational Q&A widget featuring preset query chips, markdown rendering, and structured containment checklists. Embedded chat alongside technical previews in `InvestigationDetails.jsx`. Deployed live `reportService.js` fetching real telemetry logs for the Reports workspace view. Performed a complete codebase sweep, purging all mock JSON files (`campaignData`, `dashboardData`, `investigationData`, `threatIntelligenceData`, and `mockApi.js`). Verified frontend builds cleanly. Phase A 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 64 - 10:45):** **Task 64 (Demo Dataset Generation - Stage B.1):** Created `backend/scripts/seed_demo_data.py` standalone database seeding script. The script purges existing records and seeds 15 distinct completed scans representing phishing campaigns, typosquatting (e.g. `paypa1-update.com`), expired SSL/TLS certificates, and malicious redirects targeting Google, Microsoft, PayPal, Amazon, SBI, and HDFC Bank. Configured 2 campaign correlation clusters ("CozyBear Impersonation Wave" and "Fintech Harvester Syndicate") using both legacy `Campaign` and new `CampaignRecord` tables, populated with member details, shared infrastructure overlays, and datetime properties. Stage B.1 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 65 - 11:00):** **Task 65 (System Validation - Stage B.2):** Created `backend/scripts/validate_backend.py` verification test script using HTTPX. Verified health checks, scans lists, unified evidence structures, risk assessment histories, campaigns overview, campaign topology graphs, and AI technical analyst / executive business summary report endpoints against the running Uvicorn local server, ensuring 100% API compatibility and data schema compliance. Stage B.2 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 66 - 11:15):** **Task 66 (Frontend UX Audit & State Handling - Stage B.3):** Conducted thorough audits of all 5 SPA pages. Verified loading skeletons pulse on page swaps, API exceptions fail gracefully into ErrorFallbacks, and empty tables show warning message panels. Purged all remaining development mocks. Stage B.3 100% COMPLETE.
- **2026-08-07 (Sprint 1 - Task 67 - 11:30):** **Task 67 (E2E Verification & Playbook - Stage B.4):** Verified end-to-end phishing and typosquatting scenarios against the running FastAPI backend and populated the SQLite database. Created section 21 in `PROJECT_NOTES.md` authoring the complete Step-by-Step Demo Playbook, presentation scenarios, and system completion checkmarks. Phase B 100% COMPLETE.











## 14. Familiarization & Validation Report

### Backend Discrepancies
- **Model Split Boundary**: Relational database ORM classes are split between `app/models/` (older models for Domain, Scan, Feature, RiskScore, etc.) and `app/db/models/` (newer models for CampaignRecord, CampaignMemberRecord, UnifiedEvidence, RiskAssessment).
- **Deprecated Model**: The `Campaign` model inside `app/models/campaign.py` is deprecated/unused, as all campaign functions are backed by `CampaignRecord` and `CampaignMemberRecord` in `app/db/models/campaign.py`.

### Frontend Mock Data API Integration Mapping
- **Dashboard Component** (`frontend/src/pages/Dashboard.jsx`):
  - *Current Status*: Uses mock `getDashboard()` retrieving hardcoded KPIs, telemetry data, recent scans table, and risk distributions.
  - *Target API Endpoint*: `GET /api/v1/scans/` (recent scans), `GET /api/v1/campaigns/` (attributed campaign lists & stats), and telemetry calculation routes.
- **Investigation Workspace** (`frontend/src/pages/Investigation.jsx`):
  - *Current Status*: Uses mock `getInvestigation(url)` simulating loading delay and parsing mock DNS, certificate, and HTML content tables.
  - *Target API Endpoint*: `POST /api/v1/unified-evidence/process` (to scan URL), `GET /api/v1/unified-evidence/{indicator}` (for detailed categories), `GET /api/v1/risk/{indicator}` (for explanation breakdowns), and `POST /api/v1/ai/ask` (for analyst Q&A).
- **Campaigns Workspace** (`frontend/src/pages/Campaigns.jsx`):
  - *Current Status*: Uses mock `getCampaigns()` rendering active domains, shared IP/SSL overlaps, and a hardcoded SVG topology relationship graph.
  - *Target API Endpoint*: `GET /api/v1/campaigns/{campaign_id}`, `GET /api/v1/campaigns/{campaign_id}/graph` (for SVG mapping), and `GET /api/v1/campaigns/{campaign_id}/timeline` (for timeline history).
- **Reports Workspace** (`frontend/src/pages/Reports.jsx`):
  - *Current Status*: Uses mock `getReports()` displaying community detections ratios, IOC checklist triggers, and Incident Report layout previews.
  - *Target API Endpoint*: `POST /api/v1/ai/report/analyst` and `POST /api/v1/ai/report/executive` to dynamic PDF/markdown summaries.

---

## 15. Verification Checklist for Manual Testing


Ensure the local PostgreSQL database is running, then run the following checks:
1. **Server Startup**: Run `uvicorn app.main:app --reload` and check that database tables initialization triggers successfully.
2. **Readiness Check**: Hit `GET /api/v1/health/ready` and confirm `{"status":"ready","checks":{"app":"ok","database":"ok"}}` is returned with `200 OK`.
3. **Interactive OpenAPI Docs**: Navigate to `http://127.0.0.1:8000/docs` and confirm the 6 core resource groups (`Domains`, `Scans`, `Campaigns`, `Features`, `Risk Scores`, `Feature Extraction`) show the endpoint actions.
4. **Validation Test**: Try sending a `POST /api/v1/domains` request with a missing required parameter (e.g. omitting `url`) and verify that FastAPI throws a `422 Unprocessable Entity` validation error response.
5. **Operational Verification**: Try a `GET /api/v1/domains/999` and verify that the system correctly catches the null response and raises a `404 Not Found` response code.
6. **Feature Extraction Verification**: Submit a `POST /api/v1/extract/` with payload `{"url": "https://google.com", "scan_id": 1}` and verify it triggers the full aggregation pipeline (returning domain_intelligence, network_intelligence, webpage_intelligence, and metadata schemas) and returns a HTTP 201 status code with the complete JSON dataset.
7. **Evidence Retrival Verification**: Query `GET /api/v1/extract/{feature_id}` (e.g., ID 1) and confirm it returns the saved `FeatureResponse` details.
8. **Extraction History Verification**: Query `GET /api/v1/extract/history/{scan_id}` (e.g., Scan ID 1) and confirm it returns the list of all extraction records associated with that scan.


---

## 16. Backend-Frontend API Mapping

> **Single Source of Truth**: This section is the canonical mapping reference. Every frontend service file must implement exactly these contracts.

---

### 16.1 Dashboard Page (`frontend/src/pages/Dashboard.jsx`)

**Purpose**: Aggregated SOC analytics — KPI stats, recent scans table, risk distribution chart, campaign overview, and threat timeline.

| # | Endpoint | Method | Purpose |
| :- | :--- | :--- | :--- |
| 1 | `/api/v1/scans/` | `GET` | Paginated list of recent scan records |
| 2 | `/api/v1/campaigns/` | `GET` | Active campaign list for the campaign overview panel |
| 3 | `/api/v1/risk/` | `GET` | Recent risk assessments for risk distribution chart |

**Request Payloads**:
```
GET /api/v1/scans/         ?skip=0&limit=10
GET /api/v1/campaigns/     ?skip=0&limit=5
GET /api/v1/risk/          ?skip=0&limit=50
```

**Response Models**:
- `GET /scans/` → `List[ScanResponse]` — fields: `id`, `url`, `status`, `created_at`, `campaign_id`
- `GET /campaigns/` → `List[CampaignOut]` — fields: `id`, `campaign_id`, `name`, `status`, `severity`, `member_count`
- `GET /risk/` → `List[RiskAssessmentOut]` — fields: `id`, `indicator`, `risk_score`, `severity`, `created_at`

**UI States to Handle**:
- **Loading**: Skeleton loader pulsing cards while all three fetches are in-flight.
- **Error**: `<ErrorFallback />` retry component if any fetch fails.
- **Empty**: Zero-state copy ("No scans yet — submit a URL to begin.") for the recent scans table.

---

### 16.2 Investigation Workspace (`frontend/src/pages/Investigation.jsx`)

**Purpose**: URL submission, full pipeline telemetry (WHOIS, DNS, TLS, HTML), AI analyst Q&A, and risk explanation.

| # | Endpoint | Method | Purpose |
| :- | :--- | :--- | :--- |
| 1 | `/api/v1/unified-evidence/process` | `POST` | Submit a URL to trigger the full extraction pipeline |
| 2 | `/api/v1/unified-evidence/{indicator}` | `GET` | Retrieve categorized evidence blocks |
| 3 | `/api/v1/risk/{indicator}` | `GET` | Retrieve risk score, severity, heuristics, and recommendations |
| 4 | `/api/v1/ai/ask` | `POST` | Send analyst question; receive AI-generated answer |

**Request Payloads**:
```json
// POST /api/v1/unified-evidence/process
{ "indicator": "https://evil-domain.com", "scan_id": 1 }

// POST /api/v1/ai/ask
{ "indicator": "https://evil-domain.com", "question": "Why is this URL risky?" }
```

**Response Models**:
- `POST /process` → `{ "status": "ok", "evidence_id": "...", "indicator": "..." }`
- `GET /unified-evidence/{indicator}` → `UnifiedEvidenceResponse` — contains categorized evidence blocks (domain, network, tls, webpage, threat_intel)
- `GET /risk/{indicator}` → `RiskAssessmentOut` — `risk_score`, `severity`, `explanation` (list of heuristic strings), `recommendations`
- `POST /ai/ask` → `AssistantResponse` — `message`, `suggested_actions`, `confidence`

**UI States to Handle**:
- **Idle**: URL input card rendered with submit button.
- **Loading**: `<ScanStatus />` progress indicator displayed while POST /process and subsequent GETs complete.
- **Success**: Evidence accordion, risk summary, and explanation panel populated.
- **Error**: Inline alert with retry option if pipeline fails.
- **Empty Evidence**: "No evidence gathered yet" placeholder inside each accordion section.

---

### 16.3 Campaigns Workspace (`frontend/src/pages/Campaigns.jsx`)

**Purpose**: Campaign attribution cluster view — summary card, connected domains table, infrastructure card, shared evidence, confidence card, graph topology, and timeline.

| # | Endpoint | Method | Purpose |
| :- | :--- | :--- | :--- |
| 1 | `/api/v1/campaigns/` | `GET` | List all active campaigns (to populate selector/list) |
| 2 | `/api/v1/campaigns/{campaign_id}` | `GET` | Single campaign detail — summary, domains, infrastructure, evidence |
| 3 | `/api/v1/campaigns/{campaign_id}/graph` | `GET` | Graph node/edge data for the SVG relationship topology |
| 4 | `/api/v1/campaigns/{campaign_id}/timeline` | `GET` | Chronological timeline events for `<CampaignTimeline />` |

**Request Payloads**:
```
GET /api/v1/campaigns/                     ?skip=0&limit=20
GET /api/v1/campaigns/{campaign_id}
GET /api/v1/campaigns/{campaign_id}/graph
GET /api/v1/campaigns/{campaign_id}/timeline
```

**Response Models**:
- `GET /campaigns/` → `List[CampaignOut]`
- `GET /campaigns/{id}` → `CampaignOut` with nested `members: List[CampaignMemberOut]`
- `GET /campaigns/{id}/graph` → `CampaignGraph` — `{ nodes: [GraphNode], edges: [GraphEdge] }` where `GraphNode = { id, label, type }` and `GraphEdge = { source, target, weight }`
- `GET /campaigns/{id}/timeline` → `CampaignTimeline` — `{ events: [{ time, title, desc }] }`

**UI States to Handle**:
- **Loading**: Skeleton on `CampaignSummaryCard`, `RelationshipGraph`, and `ConnectedDomainsTable`.
- **Error**: Full-page `<ErrorFallback />` with retry if campaign fetch fails.
- **Empty**: Zero-state copy ("No active campaigns correlated yet.") when campaigns list is empty.
- **No Graph**: Static "Insufficient data for topology graph" message when `nodes` array is empty.

---

### 16.4 AI Assistant Chat Interface (`frontend/src/pages/Investigation.jsx` — embedded)

**Purpose**: In-context AI analyst Q&A panel for a scanned indicator.

| # | Endpoint | Method | Purpose |
| :- | :--- | :--- | :--- |
| 1 | `/api/v1/ai/ask` | `POST` | Submit an analyst question for a given indicator |
| 2 | `/api/v1/ai/report/analyst` | `POST` | Generate a full analyst markdown report |
| 3 | `/api/v1/ai/report/executive` | `POST` | Generate a concise executive summary |

**Request Payloads**:
```json
// POST /api/v1/ai/ask
{ "indicator": "https://evil-domain.com", "question": "What infrastructure is shared?" }

// POST /api/v1/ai/report/analyst
{ "indicator": "https://evil-domain.com" }

// POST /api/v1/ai/report/executive
{ "indicator": "https://evil-domain.com" }
```

**Response Models**:
- `POST /ai/ask` → `AssistantResponse` — `{ message: str, suggested_actions: [SuggestedAction], confidence: str }`
- `POST /ai/report/analyst` → `AnalystReport` — `{ indicator, risk_score, severity, timeline_summary, ioc_list, conclusion, recommended_actions }`
- `POST /ai/report/executive` → `ExecutiveSummary` — `{ indicator, verdict, executive_summary, key_findings: [str], priority_actions: [str] }`

**UI States to Handle**:
- **Loading**: Spinner inside the ask button; disable repeat submission.
- **Streaming illusion**: Simulate typewriter-style rendering of AI answer.
- **Error**: Inline error copy ("AI service temporarily unavailable. Try again.").
- **Fallback Notice**: If OpenRouter fails and local engine answers, label response as "⚡ Local Reasoning Engine".

---

### 16.5 Reports Workspace (`frontend/src/pages/Reports.jsx`)

**Purpose**: External threat intelligence feeds, IOC table, reputation score, SIEM recommendations, and exportable incident report preview.

| # | Endpoint | Method | Purpose |
| :- | :--- | :--- | :--- |
| 1 | `/api/v1/ai/report/analyst` | `POST` | Analyst-level full Markdown incident report |
| 2 | `/api/v1/ai/report/executive` | `POST` | Executive-level summary |
| 3 | `/api/v1/unified-evidence/{indicator}` | `GET` | Threat feed data: VirusTotal, PhishTank, URLHaus, AbuseIPDB from evidence blocks |
| 4 | `/api/v1/risk/{indicator}` | `GET` | Reputation score, verdict, and recommendations |

**Request Payloads**: Same as Sections 16.2 and 16.4 above.

**Response Models**: `AnalystReport`, `ExecutiveSummary`, `UnifiedEvidenceResponse`, `RiskAssessmentOut` — all defined in Sections 16.2 and 16.4.

**UI States to Handle**:
- **Loading**: Skeleton on `ThreatFeedPanel`, `IOCTable`, and `ReputationCard`.
- **Error**: Feed-level error badges ("VirusTotal feed unavailable") rather than full-page failures.
- **Export**: On "Export" click — serialize `AnalystReport` or `ExecutiveSummary` response to a `.md` or `.json` file download.
- **Empty IOC List**: Show "No indicators of compromise identified." placeholder row.

---

### 16.6 Risk Details Panel (`frontend/src/components/investigation/RiskSummary.jsx`)

**Purpose**: Granular risk breakdown — score, severity badge, heuristics list, and recommendation.

| # | Endpoint | Method | Purpose |
| :- | :--- | :--- | :--- |
| 1 | `/api/v1/risk/{indicator}` | `GET` | Full risk assessment for a given URL/indicator |

**Request Payload**: `GET /api/v1/risk/{indicator}` (URL-encoded indicator)

**Response Model**: `RiskAssessmentOut`
```json
{
  "indicator": "https://evil-domain.com",
  "risk_score": 87.5,
  "max_score": 100,
  "severity": "critical",
  "confidence": "high",
  "explanation": ["Suspicious TLD registered 3 days ago", "No WHOIS privacy — known-bad registrar"],
  "recommendation": "Block immediately and escalate to Tier 2.",
  "created_at": "2026-08-07T03:15:00Z"
}
```

**UI States to Handle**:
- **Loading**: Pulsing skeleton ring around the risk score badge.
- **Error**: Grayed-out badge with "Risk data unavailable" message.
- **Low Score (< 30)**: Render green badge with "Low Risk" copy.
- **Critical Score (>= 80)**: Render red pulsing badge with "CRITICAL" label.

---

### 16.7 Evidence Viewer (`frontend/src/components/investigation/EvidenceAccordion.jsx`)

**Purpose**: Collapsed accordion sections for WHOIS, DNS, TLS, DOM/HTML, and threat intelligence evidence blocks.

| # | Endpoint | Method | Purpose |
| :- | :--- | :--- | :--- |
| 1 | `/api/v1/unified-evidence/{indicator}` | `GET` | All categorized evidence blocks for the indicator |

**Request Payload**: `GET /api/v1/unified-evidence/{indicator}` (URL-encoded indicator)

**Response Model**: `UnifiedEvidenceResponse` (nested categories)
```json
{
  "indicator": "https://evil-domain.com",
  "domain_intelligence": { "registrar": "...", "creation_date": "...", "expiry_date": "...", "name_servers": [...] },
  "network_intelligence": { "ip_address": "...", "asn": "...", "hosting_provider": "...", "dns_records": { "A": [...], "MX": [...], "NS": [...] } },
  "tls_intelligence": { "common_name": "...", "issuer": "...", "valid_from": "...", "valid_to": "...", "san_list": [...] },
  "webpage_intelligence": { "page_title": "...", "form_count": 2, "has_password_field": true, "external_links": 14 },
  "threat_intel": { "virustotal": {...}, "phishtank": {...}, "urlhaus": {...}, "abuseipdb": {...} }
}
```

**UI States to Handle**:
- **Loading**: Skeleton rows inside each accordion section.
- **Error**: Per-section error badge ("DNS data unavailable") rather than collapsing the section entirely.
- **Empty Category**: Render "No data gathered for this category" within the section body.
- **Highlight Anomalies**: Rows where `highlight: true` must render with an amber background tint.

---

## 17. Strict Development Rules

> `PROJECT_NOTES.md` is the **single source of truth** for this project. Every implementation decision must be consistent with this document. Every completed task must immediately update this document.

### 17.1 Architecture Rules
1. **Never Redesign Completed Architecture** — All 8 backend milestones are finalized. No new backend services, database tables, or architectural patterns will be introduced without explicit approval.
2. **Reuse Existing Services** — Before writing new logic, check `backend/app/services/` for an existing service. Frontend fetches must call live backend endpoints; no new mock responses may be introduced.
3. **Repository Pattern is Mandatory** — All database access in the backend must go through the repository layer (`app/db/repositories/`). Direct SQLAlchemy session queries in endpoint handlers are forbidden.
4. **API Versioning** — All backend routes must stay under `/api/v1/`. No routes outside this prefix will be accepted.
5. **No Duplicate Logic** — Similarity scoring, risk calculations, evidence normalization, and campaign clustering already exist in their respective engines. Never re-implement these in a new file.

### 17.2 Frontend Integration Rules
6. **Replace Mock Data Surgically** — Each frontend service file (`dashboardService.js`, `scanService.js`, etc.) must be updated to call the backend API instead of the local mock. The adapter files (`dashboardAdapter.js`, etc.) must continue to be used to normalize responses.
7. **Error Boundaries Are Mandatory** — Every page-level data fetch must be wrapped in a try/catch. All errors must render the existing `<ErrorFallback />` component.
8. **Loading States Are Non-Negotiable** — Every async operation must display `<SkeletonLoader />` until data resolves. No spinner-less blank states.
9. **Adapter Contract Must Be Preserved** — The existing adapter functions (`adaptDashboardData`, `adaptScanData`, `adaptCampaignData`, `adaptReportData`) define the normalized data shape consumed by React components. These shapes must not change during API integration; only the data *source* changes (from mock JSON to live API response).

### 17.3 Documentation Rules
10. **Update Immediately** — After every completed task, the Progress Tracker and Revision History in `PROJECT_NOTES.md` must be updated before moving to the next task.
11. **Decision Log First** — Any deviation from the architecture or a new design decision must be logged in the Decision Log before implementation begins.
12. **No Orphan Code** — If a file is created, its purpose must be documented. If a file is deleted, the deletion must be recorded in the Revision History.

---

## 18. Investigation Workflow & Details Architecture

### 18.1 API Interaction Flows (Stage A.3)
When a user submits a suspicious indicator (URL or domain) on the `Scans.jsx` submission view:
1. **URL Validation**: Basic validation ensures a valid domain format.
2. **Registration**:
   - `POST /api/v1/domains/` with `{ url }` registers the domain.
   - `POST /api/v1/scans/` with `{ domain_id }` registers the scan (default status: `pending`).
3. **Async Pipeline Triggering**: The client triggers a background task execution flow:
   - `PUT /api/v1/scans/{id}` updates status to `scanning`.
   - `POST /api/v1/extract/` executes DNS, WHOIS, TLS, and BeautifulSoup counter collections.
   - `POST /api/v1/unified-evidence/process` merges features and scores confidence.
   - `POST /api/v1/risk/evaluate` calculates the transparent 0-100 risk score.
   - `POST /api/v1/campaigns/correlate` matches shared infrastructure traits.
   - `PUT /api/v1/scans/{id}` updates status to `completed` (or `failed` if an error occurs).
4. **Polling & Redirect**: The submission panel polls `GET /api/v1/scans/{id}` once per second. Upon finding status `completed`, the router redirects to `/scans/{id}`.

### 18.2 Investigation Details Architecture (Stage A.4)
On loading `/scans/:id` (`InvestigationDetails.jsx`):
1. **API Telemetry Merging**:
   - `GET /api/v1/scans/{id}` retrieves base scan metadata.
   - `GET /api/v1/unified-evidence/{url}` loads merged observations.
   - `GET /api/v1/risk/{url}` retrieves score details and triggered heuristics.
   - `POST /api/v1/ai/report/analyst` and `POST /api/v1/ai/report/executive` fetch pre-generated LLM summaries.
   - `GET /api/v1/campaigns/` fetches campaign registry to find infrastructure overlap.
2. **UI Component Mappings**:
   - **EvidenceAccordion**: Maps observations from `resolved_observations` to Domain, DNS, WHOIS, SSL, HTML, and Metadata tables.
   - **RiskSummary**: Displays overall score, severity rating, confidence percentage, and Analyst Action recommendation.
   - **BadgeGroup**: Iterates over triggered heuristics indicators (e.g. "Impersonation", "New Domain").
   - **AI Reports Panel**: A tabbed card showing the Analyst technical report (conclusions, recommendations checklist) and the Executive leadership summary (impact summary, exposure rating).

---

## 19. Campaign Correlation & AI Assistant Frontend Architecture

### 19.1 Campaign Intelligence Integration (Stage A.5)
The campaigns workspace (`frontend/src/pages/Campaigns.jsx`) is wired to live backend endpoints:
- **Campaign Selection**: Automatically queries the active campaign list using `GET /api/v1/campaigns/`. It retrieves details for the most recent active correlation cluster (`GET /api/v1/campaigns/{campaign_id}`).
- **RelationshipGraph**: Renders an interactive network topology SVG. Queries `GET /api/v1/campaigns/{campaign_id}/graph` to retrieve nodes and edges.
  - Nodes classified as `indicator` are mapped to coordinates on the left side of the canvas.
  - Nodes containing shared infrastructure attributes (`ip`, `certificate`, `whois`, etc.) are mapped to coordinates on the right side.
  - Connections (`edges`) are drawn from the center campaign hub to all vertices, showing link weights.

### 19.2 Conversational AI Chat Integration (Stage A.6)
The AI Chat widget (`AiAssistantChat.jsx`) is embedded inside the details workspace panel:
- **Context Injection**: Every query sent to `POST /api/v1/ai/ask` includes the `indicator` string along with the current scan's telemetry context payload (evidence observations, risk score metrics, and campaign status).
- **Preset Chips**: Features preset inquiry buttons (e.g. "Why is this indicator rated risky?") to let analysts query threat summaries with a single click.
- **Markdown & Action Lists**: Renders structured markdown responses and suggested SIEM action items returned by the LLM reasoning engine.

### 19.3 Known Limitations
- **Graph Rendering Limits**: The dynamic coordinate mapper arranges up to 10 indicators (left side) and 10 infrastructure elements (right side) without layout overlapping. Large campaign clusters containing >25 indicators may degrade visual spacing.
- **AI Report Latency**: Requesting real-time report summaries from `/ai/report/analyst` or `/ai/report/executive` may require 1–3 seconds depending on the OpenRouter provider gateway response speed.

---

## 20. Demo Dataset & System Validation Documentation

### 20.1 Seeding Scenarios Overview (Stage B.1)
The script `backend/scripts/seed_demo_data.py` generates 15 target indicators with realistic telemetry parameters and completed status:
1. **secure-microsoft-login-verification.com**: Critical Microsoft phishing portal linked to CozyBear campaign. IP range: `185.230.125.44` (Shared).
2. **office365-security-check.net**: Critical Microsoft credential harvesting portal linked to CozyBear campaign. IP range: `185.230.125.45`.
3. **microsoft-login-auth.live**: Critical Microsoft credential harvesting portal linked to CozyBear campaign. IP range: `185.230.125.46`.
4. **paypa1-update.com**: High-risk PayPal typosquatting domain linked to Fintech Harvester campaign. IP range: `185.230.125.44` (Shared).
5. **amazon-verify-checkout.net**: High-risk Amazon Pay phishing portal linked to Fintech Harvester campaign. IP range: `185.230.125.44` (Shared).
6. **sbi-netbanking-verify.in**: Critical State Bank of India netbanking mimic (individual threat).
7. **hdfcbank-login-secure.co**: Critical HDFC Bank login portal mimic (individual threat).
8. **accounts-google-verify.com**: High-risk Google login credentials harvester (individual threat).
9. **gmail-upgrade-verification.net**: High-risk Gmail portal upgrade credential harvester (individual threat).
10. **github-auth-verify.com**: Medium-risk GitHub redirect containing an expired SSL/TLS certificate.
11. **git-update-portal.org**: Medium-risk GitHub redirection chain containing 2 hops.
12. **google.com**: Safe/Legitimate Google main brand portal (baseline contrast).
13. **microsoft.com**: Safe/Legitimate Microsoft main brand portal (baseline contrast).
14. **paypal.com**: Safe/Legitimate PayPal main brand portal (baseline contrast).
15. **statebankofindia.com**: Safe/Legitimate State Bank of India main portal (baseline contrast).

### 20.2 System Validation Tests (Stage B.2)
The verification script `backend/scripts/validate_backend.py` runs 8 consecutive endpoint checks against `http://localhost:8000/api/v1`:
* **Health Readiness `/health/ready`**: Verifies database connection and general server status.
* **Scans Log `/scans`**: Asserts that all 15 seeded scan records are successfully returned.
* **Unified Evidence `/unified-evidence/{indicator}`**: Validates the presence of WHOIS, DNS, and TLS observations.
* **Risk History `/risk/{indicator}`**: Validates that risk score metrics and triggered heuristics are present.
* **Campaigns Log `/campaigns`**: Asserts that the 2 custom campaign correlation clusters are successfully returned.
* **Campaign Topology `/campaigns/{id}/graph`**: Asserts that CozyBear graph relationships compile with nodes and edges.
* **AI Analyst Report `/ai/report/analyst`**: Verifies that technical markdown summary and mitigation actions checklist compile cleanly.
* **AI Executive Summary `/ai/report/executive`**: Verifies that C-level business impact narratives and risk rating categories compile cleanly.

---

## 21. Final System Validation & Demo Playbook

### 21.1 Presentation Workflow
To present the ThreatLens platform to stakeholders or clients, walk through the following 5-step operational flow:
1. **System Health Check (Dashboard)**: Point out the readiness state dots in the top bar. Note that telemetry sources (WHOIS, DNS, HTTP, SSL) and database instances are fully operational.
2. **Review Campaign Clusters (Campaigns)**: Navigate to the Campaigns workspace. Demonstrate the Threat Correlation Topology graph mapping lookalike Microsoft domains linked to the `CozyBear Impersonation Wave` campaign, highlighting the shared infrastructure footprint attributes.
3. **Queue Scans History (Scans Log)**: Navigate to the Domain Scanning Queue. Show the list of 15 pre-seeded threat scenarios.
4. **Trigger Active Scan (Submission)**: Type a new test URL (e.g. `office365-security-check.net`) into the input box and click "Start Scan". Highlight the real-time polling steps tracker (`ScanStatus`) changing states as the backend registers records, extracts attributes, and evaluates risk.
5. **Analyze Threats Telemetry (Details)**: Inspect the compiled details view. Demonstrate the explainable risk gauges, SSL issue warning tags, WHOIS registration age rows, and live markdown responses compiled by the OpenRouter AI Assistant Chat tab.

### 21.2 Primary Demonstration Scenarios
* **Scenario A (Critical Risk - Campaign Impersonation)**: Target indicator `office365-security-check.net`. Show overall risk score 88/100, active harvesting form indicators, self-signed TLS certificates common name matches, and connection to the CozyBear campaign cluster.
* **Scenario B (Medium Risk - Infrastructure Flaw)**: Target indicator `github-auth-verify.com`. Show risk score 58/100, expired SSL certificate warnings, and lack of active campaign correlation link (unattributed threat).
* **Scenario C (Safe Baseline)**: Target indicator `google.com`. Show overall risk score 12/100, Let's Encrypt / Google Trust Services SSL verified chain, MarkMonitor registrar age baseline, and zero heuristic triggers.

---

## 22. Telemetry Extractor Pipeline Error Handling & Lexical Brand Impersonation Rules (2026-08-07)

### 22.1 Error Handling in Telemetry Extractor Pipeline
* **Robust Exception Wrappers**: Modified all network socket, HTTP, SSL, and DNS lookups in `DomainIntelService`, `NetworkIntelService`, and `WebpageIntelService` to catch `(Exception, requests.RequestException, socket.error, ssl.SSLError)`.
* **DNS Resolver Timeouts**: Enhanced `resolve_dns` to configure a custom `dns.resolver.Resolver` instance with a strict `timeout = 3.0` and `lifetime = 3.0` seconds, preventing hangs on unresponsive nameservers.
* **WHOIS Socket Timeouts**: Configured a temporary default socket timeout of `5.0` seconds around `whois.whois(domain)` to prevent blocking the worker on slow WHOIS queries.
* **Structured Fallback Telemetry**: If an extraction fails or times out, the service returns a structured fallback dictionary containing `{"status": "unreachable", "error": str(e)}` alongside empty defaults instead of raising an HTTP 500, enabling the scan record status to transition to `COMPLETED` successfully with partial data.

### 22.2 Brand Impersonation & Lexical Risk Heuristics
* **Nested Evidence Mapping**: Enhanced `DefaultMergeStrategy` to flatten nested extraction results from the individual intel services (`domain_intelligence`, `network_intelligence`, `webpage_intelligence`) into top-level flat observations in the resolved observations dictionary. This bridges the gap between nested extraction payloads and flat evaluator rule schemas.
* **Lexical Risk Rules**: Implemented lexical brand impersonation checks in `DomainIntelEvaluator` looking for target enterprise brands (`microsoft`, `google`, `amazon`, `paypal`, `github`, `vardhaman`) combined with phishing-specific keywords (`login`, `verify`, `auth`, `secure`, `update`, `account`, `portal`) in the domain host part.
* **Minimum Base Score Enforcers**: Configured `RiskScoringService` to enforce a minimum base Risk Score of `85.0` (HIGH severity) whenever a brand impersonation lexical match is flagged, regardless of whether DNS/WHOIS telemetry is present or empty.

---

## 23. Stage D.1 (Risk Score Consistency Engine) & Stage D.2 (AI Context Synchronization) (2026-08-07)

### 23.1 Centralized Severity Mapping
* **Centralized Thresholds**: Updated `SEVERITY_THRESHOLDS` in `config.py` to:
  * `>= 91.0`: `critical`
  * `>= 71.0`: `high`
  * `>= 41.0`: `medium`
  * `>= 21.0`: `low`
  * `>= 0.0`: `safe`
* **Score Bounds Mapping**: Updated the `RiskSeverity` docstring comments in `models.py` to explicitly match these mapping bounds (e.g. 0-20=SAFE, 21-40=LOW, 41-70=MEDIUM, 71-90=HIGH, 91-100=CRITICAL).

### 23.2 Campaign Severity Aggregation
* **Dynamic Aggregate Severity**: Implemented `_aggregate_severity` in `CampaignRepository`. When loading or saving campaigns, the service dynamically resolves the latest `RiskAssessmentRecord` for all correlated member indicators and sets the campaign's overall threat severity to the maximum severity among them (defaulting `safe` member investigations to `LOW` campaign severity).
* **Identically Formatted Badges**: Mounted `/api/v1/investigations/{id}` endpoint matching the risk details layout. This guarantees that API responses for investigations and campaigns share identical severity badge strings ("safe", "low", "medium", "high", "critical"), eliminating contradictory dashboard displays.

### 23.3 AI Context Synchronization
* **Refactored Prompt Builder**: Refactored `generate_system_prompt` in `context_builder.py` to serialize and inject structured backend context parameters (`risk_score`, `severity`, `iocs`, `domain_metadata`, and `campaign_info`).
* **Anti-Hallucination Guardrails**: Embedded strict Tier-2 security instructions inside the LLM prompt forcing the assistant to base summaries and responses strictly on the provided `Risk Score` and `Severity`, preventing Q&A responses from stating a threat is negligible if severity is HIGH or CRITICAL, and forcing it to explicitly list the provided IOCs.
* **Forwarding Interface Compatibility**: Created `app/services/ai_service.py` and `app/services/campaign_engine.py` wrapper modules to ensure import forwarding compatibility.
* **Progress**: Stage D.1 and Stage D.2 are **100% COMPLETE**.

---

## 24. Stage D.3 (Threat Intelligence Feed Validation) & Stage D.4 (Campaign Correlation Validation) (2026-08-07)

### 24.1 Threat Intelligence Feed Status Mapping
* **Status Mapping Fields**: Standardized the `ProviderResponse` Pydantic model by adding an explicit `status` field mapping the status of external reputation feed lookup:
  * `success`: The API lookup completed successfully, returning matching hits or confirming the indicator is clean.
  * `no_result`: The API lookup returned a 404 resource not found or a lookup payload indicating the indicator does not exist in the threat feed database.
  * `rate_limited`: The API lookup returned HTTP 429 indicating client lookup thresholds were exceeded.
  * `unavailable`: The API lookup timed out, credentials were not configured, or a network exception occurred.
* **Graceful UI Fallbacks**: Updated `ThreatFeedPanel.jsx` and the adapter to render specific status cards for each of these states. Instead of empty sections, cards style themselves dynamically with clear warning alerts, timeout/rate-limit notice text, and fallback community scores and ingestion metrics.

### 24.2 Campaign Correlation Graphing Properties
* **Shared Infrastructure Mapping**: Populated properties inside `CampaignGraphBuilder` for relationship visualizations:
  * **IP Address Node**: ASN name, hosting ISP name, and connection weight.
  * **TLS Certificate Node**: Common SSL fingerprint serial, certificate subject/issuer fields.
  * **Registrar Authority Node**: Registrar name, delegated nameservers list, and string similarity matching metric.
  * **WHOIS Owner Node**: Registrant owner organization name, and relational similarity score (e.g. "94% Match").
* **Visual Graph Alignments**: Aligned `campaignService.js` and `connectedDomainsTable.js` frontend models to parse the correct backend types and properties, ensuring the graph visualization elements match correlated member evidence accurately.
* **Progress**: Stage D.3 and Stage D.4 are **100% COMPLETE**.

---

## 25. Domain Ingestion Get-or-Create Logic (2026-08-07)

### 25.1 CRUDDomain Get-or-Create Logic
* **Overridden Create**: Overrode the `create` method in `CRUDDomain` (`repositories/domain.py`) to perform a lookup query by URL prior to inserting new records. If an existing `Domain` record matches the target URL, it is returned immediately instead of attempting an INSERT, avoiding PostgreSQL unique constraint violations (`ix_domain_url`).

---

## 26. Stage D.5 (Report Consistency & Export Validation) & Stage D.6 (End-to-End Consistency Audit) (2026-08-07)

### 26.1 Report Consistency & Export Validation
* **Export Action Handlers**: Fully enabled download functionality in the frontend `ExportPreview.jsx` component. Clicking the export buttons now compiles and triggers direct client-side downloads for:
  * **Markdown (.md)**: A beautifully structured markdown report matching the Incident Report Preview layout exactly, containing headers, timestamp indicators, threat summaries, and analyst mitigation action checklists.
  * **JSON (.json)**: A clean JSON schema mapping all report preview sections to distinct properties.
* **Dynamic Generation Timestamp**: Made the generation timestamp inside `IncidentReportPreview.jsx` fully dynamic, capturing the live client-side date/time when the report was compiled rather than hardcoding static mock dates.

### 26.2 End-to-End Consistency Audit & Demo Readiness
* **Infrastructure Metric Parity**: Verified that all risk metrics, severities, and threat categorizations are strictly synchronized. Aligned `campaignService.js` to derive each domain's `riskScore` directly from their underlying telemetry `resolved_observations.risk_score` (falling back to campaign severity scoring defaults where appropriate), ensuring complete metric parity between campaign lists, topology graphs, and details panels.
* **Final Verification Checklist**:
  * [x] Database Get-or-Create behavior on duplicate URL scan submissions resolves without Postgres unique violations.
  * [x] External feeds status mappings (`success`, `no_result`, `rate_limited`, `unavailable`) correctly align with API responses and handle timeouts/limits gracefully.
  * [x] SVG Campaign topology nodes and edges accurately display Registrar and WHOIS relationships.
  * [x] Report downloads match UI preview details exactly.
  * [x] AI reasoning engine context synchronizes with calculated backend risk values without hallucinations.
* **Known Limitations**:
  * *OpenRouter Latency*: Async completions via API gateway may experience 1-3 seconds response latency. Falling back to local deterministic generation works instantly.
  * *Topology Spacing*: SVG graph coordinates support up to 10 indicators/infrastructure items before layout overlapping.
* **Demo-Ready Declaration**: The ThreatLens platform is officially **Demo-Ready**. All features, databases, REST endpoints, and UI views are fully synchronized, audited, and ready for deployment.
* **Progress**: Stage D.5 and Stage D.6 are **100% COMPLETE**.



---

## 27. Historical Scan Selector & Report Deep-Linking (2026-08-07)

### 27.1 Historical Scan Selector Dropdown (Reports Page)
* **Self-Contained Reports Page**: Refactored `Reports.jsx` to manage its own local state entirely (replacing the `useReports()` Context hook), enabling dynamic scan selection independent of the global data layer.
* **Scan History Dropdown**: Added a styled `<select>` dropdown at the top of the Reports page header. Fetches all completed investigations via `getInvestigationHistory()` on mount and renders them as options formatted as `#<ID> — <domain>`.
* **On-Demand Report Loading**: When an analyst selects a different scan, the page calls `getReportForScan(scanId)` to fetch that specific scan's threat feeds, IOCs, risk assessment, and incident report preview dynamically.
* **Loading & Error States**: Shows a spinner overlay when loading a new report, and surfaces an error banner with a Retry button if the report fetch fails.

### 27.2 URL Deep-Linking Support
* **`useSearchParams` Integration**: Reports page reads `?scanId=X` from the URL on mount. If present, initializes the dropdown selection and report payload to that specific scan without additional navigation.
* **URL Sync on Dropdown Change**: Each time the dropdown selection changes, the URL search parameter is updated automatically via `setSearchParams({ scanId })`, making every viewed report shareable and bookmarkable.
* **"View Report" Button on Scans Page**: Added a second action button in the Scans history table (alongside "Details") labeled **"Report"** that navigates directly to `/reports?scanId={id}` for any completed scan.

---

## 28. Complete Commit History Audit & Traceability Log (2026-08-07)

This section provides a full cross-referenced audit of every commit in the repository, mapping each to the corresponding PROJECT_NOTES section. Verified against `git log --oneline --all` on 2026-08-07.

---

### Phase 0 — Project Bootstrap (2026-08-06)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `bf85a91` | Initial commit | §1 |
| `9de08a2` | Initialize project structure and boilerplate | §1, §10 |
| `57e6cde` | Populate comprehensive system architecture and design documentation | §10 |

---

### Phase 1 — Backend Core & Database (2026-08-06)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `c869c90` | Initialize backend core structure and FastAPI entry point | §10, §13 |
| `c93678b` | Implement Pydantic Settings configuration layer | §10 |
| `caad690` | Implement request-processing pipeline with CORS, logging middleware, Request ID tracing | §10 |
| `a0c32a2` | Implement FastAPI lifespan handlers and structured versioned health endpoints | §10 |
| `d8eeca9` | Initialize database configurations and core SQLAlchemy engine with connection pooling | §10 |
| `a06c82a` | Implement declarative base, SessionLocal, and `get_db` dependency | §10 |
| `2492c18` | Update PROJECT_NOTES.md feature tracking log and sync config changes | §13 |
| `27a131c` | Restructure progress log in PROJECT_NOTES.md with sprint format | §13 |
| `b5996a2` | Implement database persistence layer with ORM models and startup schema generation | §4, §10, §13 |
| `034d501` | Implement Pydantic validation schemas, generic CRUD base, and specific repository layers | §10, §13 |
| `999a952` | Implement RESTful API endpoints for all core entities under `/api/v1` router | §16, §13 |

---

### Phase 2 — Feature Extraction Engine — Milestone 3 (2026-08-06)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `f1d4d62` | Implement DomainIntelService (DNS/WHOIS extraction) and first extraction endpoint | §3, §13 |
| `7f149ac` | Implement NetworkIntelService (IP/DNS/SSL/HTTP) and network extraction endpoints | §3, §13 |
| `c71fe6b` | Implement WebpageIntelService, FeatureAggregationService, and POST `/extract/domain` | §3, §13 |
| `3ed3e0e` | Expose unified Feature Extraction Engine REST API endpoints and final stabilization | §3, §16 |
| `c5d8df8` | Milestone 3: Feature Extraction Engine completed | §13 |

---

### Phase 3 — Threat Intelligence Engine — Milestone 4 (2026-08-06)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `2436d35` | Enhance PROJECT_NOTES.md with tech stack, workflows, diagrams, and roadmaps | §2–§9 |
| `7ee3c99` | Stage 4.1 — Threat Intelligence Foundation: base provider interfaces, service registry orchestrator | §3, §13 |
| `ac93fff` | Stage 4.2 — VirusTotal Integration (API v3) | §3, §16 |
| `3120a1a` | Update `.env.example` with `VIRUSTOTAL_API_KEY` placeholder | §17 |
| `87434a8` | Stage 4.3 — PhishTank & URLHaus Integration | §3, §16 |
| `b62c863` | Fix HTTP 403/401 errors for PhishTank and URLHaus providers (header fixes) | §13 |
| `763a554` | Stage 4.4 — AbuseIPDB & AlienVault OTX Integration (Milestone 4 complete) | §3, §16 |
| `efe14c0` | Stage 4.5 — Aggregated Threat Evidence Engine & Endpoints | §3, §16 |
| `5913732` | Refactor threat intel provider lookup logic & unify error handling | §3, §13 |

---

### Phase 4 — Unified Evidence Engine — Milestone 5 (2026-08-06)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `b35b60b` | Stage 5.1 — Unified Evidence Models & Foundation | §10, §13 |
| `d19ccc0` | Stage 5.2 — Internal & External Evidence Merge Strategy | §3, §10 |
| `f3c9463` | Stage 5.3 — Evidence Normalization & Confidence Calculation | §3, §10 |
| `6c8b0fd` | Stage 5.4 — Unified Evidence API & Persistence (Milestone 5 complete) | §16 |
| `303731f` | Stage 5.5 — Evidence Timeline & Traceability | §3 |
| `4ca4936` | Stage 5.6 — Unified Evidence Engine finalization & refactoring (Milestone 5 FINAL) | §13 |

---

### Phase 5 — Frontend Foundation (Static) (2026-08-06)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `b768d5d` | Bootstrap Vite React application entry points | §10 |
| `cf4a599` | Implement centralized router and placeholder pages | §10 |
| `1b01927` | Create responsive dashboard layout with drawer sidebar | §10 |
| `d2cc7a0` | Update PROJECT_NOTES for Stage 1 layout work | §1 |
| `14df9b6` | Add static dashboard analytics data model | §10 |
| `28f64cc` | Create modular dashboard components | §10 |
| `c4f0c66` | Integrate components into dashboard page view | §10 |
| `d6da628` | Add reusable RiskScoreBadge and StatusPill components | §10 |
| `c5a97d2` | Implement static SOC dashboard analytics | §10 |
| `76e6599` | Add static threat intelligence and reports dataset | §10 |
| `f7bb31d` | Build modular threat intelligence and reports components | §10 |
| `d336438` | Integrate components into reports page view | §10 |
| `af6fa2d` | Implement Threat Intelligence & Reports dashboard | §10 |
| `ae25c01` | Fix threat intelligence card alignment | §13 |
| `6506f39` | Refactor threat intelligence card presentation | §13 |
| `6d06dc3` | Implement Campaign Intelligence Dashboard | §10 |
| `0321081` | Add mock API services layer and schemas | §10 |
| `37495ac` | Add data normalisation adapters | §10 |
| `66f2677` | Implement DataProvider and custom hooks | §10 |
| `7124313` | Create skeleton loader and error fallback components | §10 |
| `868df77` | Rewire page components to consume centralized hooks | §10 |
| `17de189` | Introduce centralized mock service architecture | §10 |
| `39cfe19` | Fix invalid SVG path rendering | §13 |
| `901631b` | Fix invalid SVG path rendering | §13 |
| `6431d32` | Fix invalid document icon path | §13 |
| `17b629a` | Fix Threat Scoring Explanation header alignment | §13 |
| `04c133a` | Fix investigation workspace card overflow and alignment | §13 |
| `db2c2bf` | Fix scan pipeline within card bounds | §13 |
| `6c5719c` | Add static URL investigation telemetry dataset | §10 |
| `fc280c8` | Build reusable investigation components | §10 |
| `beb76a7` | Implement URL investigation workspace page and routing | §10 |
| `8abe60d` | Implement URL investigation workspace | §10 |

---

### Phase 6 — Risk Scoring Engine — Milestone 6 (2026-08-07)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `4f9b80b` | Stages 6.1 & 6.2 — Explainable Risk Scoring Engine foundation & core logic | §6, §13 |
| `26e6198` | Stages 6.3 & 6.4 — Recommendation Engine, DB Persistence & Risk API (Milestone 6 FINAL) | §6, §16 |
| `971b7cf` | Enhance Risk Engine API with `overall_confidence` and finalize Milestone 6 | §6, §16 |
| `a48d24c` | Stage 6.6 — Final refactoring, standardized logging, project documentation | §13 |

---

### Phase 7 — Campaign Correlation Engine — Milestone 7 (2026-08-07)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `db734de` | Stage 7.1 — Campaign Correlation Engine foundation, models, schemas, and service interfaces | §7, §13 |
| `add195d` | Stage 7.2 — Core correlation strategies, SimilarityEngine weights, and evaluate_link service | §7, §13 |
| `b367831` | Stage 7.3 — Campaign Clustering & Attribution Engine with join, merge, and split logic | §7, §13 |
| `a85dbbf` | Stage 7.4 — Campaign Timeline and Relationship Graph engines | §7, §13 |
| `451b305` | Stages 7.5 & 7.6 — DB persistence, repository mapping, FastAPI campaigns endpoint, E2E validation | §7, §16 |

---

### Phase 8 — AI Assistant Engine — Milestone 8 (2026-08-07)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `666ce1d` | Stages 8.1 & 8.2 — AI architectural foundation, context builder, and system prompt generator | §10, §13 |
| `ed99191` | Stages 8.3 & 8.4 — Reasoning engine, question router, and report generators | §10, §13 |
| `86a87ee` | Stages 8.5 & 8.6 — OpenRouter completions client and REST API endpoints | §16, §19.2 |

---

### Phase A — Frontend ↔ Backend Live Integration (2026-08-07)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `780b8bd` | Task 0 — Merge remote frontend branch into main (monorepo) | §14 |
| `ce5ba90` | Tasks 1–3 — Familiarization & validation report in project notes | §14, §15 |
| `039c766` | Tasks 4–7 — Backend-frontend API mapping, strict dev rules, and focus pivot | §16, §17 |
| `56066ff` | Stage A.1 — Frontend API networking layer: Axios client, interceptors, error handler | §16 |
| `2299d82` | Stage A.2 — Connect dashboard to live FastAPI backend, replace all mock data | §16 |
| `41d31a7` | Stages A.3 & A.4 — Submission workflow and detailed investigation views | §18 |
| `176c3ce` | Stages A.5 & A.6 — Campaign graphs, dynamic timelines, live reports, AI Q&A chat | §19 |
| `fdec3a9` | Phase A complete — Full frontend integration with backend APIs | §14–§19 |

---

### Phase B — Seeding, Validation & Demo Readiness (2026-08-07)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `e412b2f` | Stages B.1 & B.2 — 15 demo scenario DB records + end-to-end backend validation scripts | §20 |
| `c879f9a` | Stages B.3 & B.4 — Final system validation & demo playbook | §21 |

---

### Phase D — Consistency, Validation & Polish (2026-08-07)

| Commit | Subject | Notes Ref |
|--------|---------|-----------|
| `d805553` | Stages D.1 & D.2 — Risk score consistency engine & AI context synchronization | §22, §23 |
| *(inline)* | Stages D.3 & D.4 — Threat intel feed validation & campaign correlation validation | §24 |
| *(inline)* | Stage D.5 & D.6 — Report consistency, export validation & end-to-end audit | §26 |
| *(inline)* | Domain ingestion Get-or-Create logic (duplicate URL fix) | §25 |
| `9e74f3a` | Historical scan selector dropdown & deep-linking to Reports page | §27 |

---

### Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Commits** | 80+ |
| **First Commit Date** | 2026-08-06 |
| **Latest Commit Date** | 2026-08-07 |
| **Active Branch** | `main` |
| **Remote Tracking** | `origin/main` (https://github.com/MatamAkshith/IARE_Hackathon) |
| **Working Tree Status** | ✅ Clean — nothing to commit |
| **PROJECT_NOTES Coverage** | ✅ Sections 1–27 mapped to all major commits |
| **Open Issues** | None — platform is Demo-Ready |

---

## 29. Multi-Brand Campaign Selector, Deep-Linking & Report Drill-Down (2026-08-07)

### 29.1 Rich Multi-Brand Campaign Seeding (seed_demo_data.py)
* **4 Distinct Campaign Clusters**: Expanded seed script from 2 to **4 named campaign records**, each with 2-3 correlated member domains:
  * `CAMP-2026-004` — **CozyBear Impersonation Wave** (Critical): 3 Microsoft lookalike domains. Shared ASN `AS41235`, registrar `NameCheap`, and identical fake SSL serial `03A1B2C3D4E5F67890`.
  * `CAMP-2026-008` — **Fintech Harvester Syndicate** (High): 2 PayPal phishing domains. Shared IP `185.230.125.44` and nameserver delegation.
  * `CAMP-2026-011` — **Amazon Billing Smash & Grab** (High): 3 Amazon checkout lookalikes. Hosted on Linode VPS `45.33.32.156`, identical self-signed cert.
  * `CAMP-2026-015` — **Indian Banking Fraud Ring** (Critical): 3 SBI/HDFC impersonation domains. Shared C2 IP `193.109.112.5`, offshore registrar `PublicDomainRegistry`.
* **scan_id in resolved_observations**: Each `CampaignMemberRecord` now stores the seeded `scan_id` inside `resolved_observations_json` so the frontend can construct `/reports?scanId={id}` drill-down links.
* **Total scenarios**: Increased from 15 to **20 investigation records** (11 campaign-attributed + 4 unattributed threats + 5 safe baselines).

### 29.2 Campaign Selector Dropdown & URL State (Campaigns.jsx)
* **Self-Contained Page**: Refactored `Campaigns.jsx` to manage its own local state entirely, dropping the `useCampaigns()` Context hook dependency for full dynamic loading.
* **Campaign Selector Dropdown**: Added a styled `<select>` in the header listing all active campaigns as `{campaign_id} — {name}`. Severity badge and member count shown beneath the dropdown.
* **`useSearchParams` Deep-Linking**: Reads `?campaignId=X` from URL on mount. Updates the URL param on every dropdown change, making every selected campaign view bookmarkable and shareable.
* **On-Demand Loading**: Calls `getCampaignDetails(campaignId)` when the dropdown changes, re-rendering the topology graph, shared infrastructure, evidence table, and timeline for the selected campaign.
* **Loading & Error UX**: Shows a spinner overlay while loading and an error banner with Retry button on fetch failure.

### 29.3 Drill-Down to Individual Domain Reports (ConnectedDomainsTable.jsx)
* **"Report" Action Column**: Added an 8th column to the Correlated Campaign Domains table with a styled rose-colored "Report" button for each row.
* **`useNavigate` Integration**: Clicking the button navigates to `/reports?scanId={domain.scanId}`, allowing analysts to seamlessly pivot from the campaign macro-view to the individual domain's full threat intelligence report.
* **Graceful Fallback**: Rows where `scanId` is `null` (e.g. live-correlated domains not seeded) show a `—` placeholder instead.
* **`scanId` Propagation**: Updated `campaignService.js` to extract `resolved_observations.scan_id` from each campaign member's observations and expose it as `scanId` in the `connectedDomains` array.

---

## 30. Expanded Brand Dictionary & Lexical Impersonation Rules (2026-08-07)

### 30.1 Brand Dictionary Expansion
* **New Target Brands**: Updated both the `DomainIntelEvaluator` (`backend/app/services/risk_engine/rules.py`) and the `RiskScoringService` (`backend/app/services/risk_engine/service.py`) brand lists to include top Indian and global enterprise IT/financial/tech brands:
  * **Tech/IT Services**: `infosys`, `tcs`, `wipro`, `hcl`, `techmahindra`, `cognizant`, `accenture`
  * **Banking/Fintech**: `icici`, `hdfc`, `sbi`, `axis`, `paytm`, `phonepe`
  * **Global Tech**: `microsoft`, `google`, `amazon`, `paypal`, `github`, `apple`, `netflix`, `vardhaman`
* **Suspicious Keywords Expansion**: Added `employee`, `benefits`, `benefit`, `careers`, `support`, `hr`, and `jobs` to the suspicious lexical keywords lists, allowing lookup domains such as `infosys-employee-benefits.net` to properly match the lexical threat heuristics.

### 30.2 Evaluation & Verification
* **Minimum Base Score Trigger**: Confirmed that any domain match of target brand + suspicious keyword triggers the minimum base score of `85.0` (HIGH severity) regardless of the availability of other evidence.
* **Test Validation**: Added automated assertions verifying the updated logic in `backend/test_risk_engine.py` for both `login.microsoft-auth-verify.com` and `infosys-employee-benefits.net`. All tests pass successfully.

---

## 31. SOC Dashboard SQL Integration & Synchronization (2026-08-07)

### 31.1 Backend Dashboard Endpoints & Dynamic SQL Aggregation
* **`GET /api/v1/dashboard/stats`**: Implemented a dynamic SQL statistics aggregation endpoint. Queries `scan` table to get the total number of scans, joins `scan` and `domain` tables to fetch the latest `RiskAssessmentRecord` for each unique domain URL, and calculates:
  * `total_scans`: Exact count of scans.
  * `high_risk_domains`: Count of scans with an overall risk score of 71 or higher.
  * `active_campaigns`: Count of active campaign records in the `campaigns` table.
  * `avg_risk_score`: Mathematical average of all scan risk scores, rounded to 1 decimal place.
  * `risk_distribution`: Bucketed array containing exact scan counts and percentages for `Safe (0-20)`, `Medium (21-70)`, `High (71-90)`, and `Critical (91-100)` bands, ensuring the sum of all bucket counts is exactly equal to `total_scans`.
* **`GET /api/v1/dashboard/recent-feed`**: Implemented a dynamic threat monitoring feed query joining `scan`, `domain`, `campaign_members`, `campaigns`, and `risk_assessment_records`. Returns:
  * `target_domain`: The actual domain URL string instead of placeholder fallback strings.
  * `risk_score`: The latest calculated numerical score.
  * `risk_rating`: The mapped severity band string matching the Risk Engine.
  * `pipeline_status`: Ingestion pipeline status in upper case.
  * `campaign_attribution`: Campaign name or `"Unattributed"`.
  * `date_time`: Ingestion date and time in ISO format.

### 31.2 Frontend Integration & Drill-Down Navigation
* **`dashboardApiService.js` Refactoring**: Updated the API service layer to query `/api/v1/dashboard/stats` and `/api/v1/dashboard/recent-feed` instead of executing client-side stitching of multiple paginated lists.
* **Badges Alignment**: Updated the `RiskScoreBadge` component thresholds to match the unified Risk Engine bands:
  * `0-20`: Safe (Green/Emerald)
  * `21-70`: Medium (Yellow/Amber)
  * `71-90`: High (Orange/Orange)
  * `91-100`: Critical (Red/Rose)
* **Drill-Down Links**: Integrated `useNavigate` into the `RecentScansTable` component, making all rows in the threat monitoring feed clickable and deep-linking directly to `/scans/{id}` to view full telemetry details.
* Updated `Campaigns.jsx` (`frontend/src/pages/Campaigns.jsx`) search parameter mapping to parse both `campaignId` and `id` keys.
* Verified that backend test suites and frontend production builds pass cleanly.

---

## 43. Graded Risk Scoring & Enhanced Scans Table UI (2026-08-07)

### 43.1 Graded Scoring Logic (Backend)
* Adjusted the risk engine scoring mechanism in `service.py` (`backend/app/services/risk_engine/service.py`):
  * Set a base score of `10.0` for all domains to account for background internet noise.
  * Adjusted `Generalized Phishing Impersonation Penalty` weight to `+35`.
  * Adjusted `Missing MX Records on Sensitive Target` weight to `+20`.
  * Separated the combined TLS/Age anomaly into two granular checks:
    * `Invalid or Missing TLS Certificate`: `+20` points.
    * `Young Domain Age` (< 30 days): `+15` points.
  * Verified that single-anomaly domains resolve to low/medium scores (~25–35), producing a smooth risk gradient instead of binary 0 or 100 spikes.
* Adapted backend unit tests (`backend/test_risk_engine.py`) to conform to the new granular factor structures and names.

### 43.2 Interactive Column & Pending State Handling (Frontend)
* Exposed `overall_score` inside the `ScanResponse` schema and populated it in backend endpoints by retrieving the latest risk assessment record for the domain.
* Mapped `overall_score` in the frontend history mapper (`frontend/src/api/investigationService.js`).
* Added a new **RISK SCORE** column in `Scans.jsx` placed before the Attribution column.
  * Renders numeric scores using a color-coded severity badge (Safe, Medium, High, Critical).
  * Displays "Calculating..." for pending/scanning investigations.
* Replaced blank action slots for pending/scanning scans with a disabled, spinning **Analyzing** button.

---

## 44. Campaigns Dropdown Wiring & Pydantic Validation Correction (2026-08-07)

### 44.1 Safe Schema Parsing (Backend)
* Resolved a database validation crash in `/api/v1/campaigns` caused by missing or camelCase datetime variables (`first_seen`/`last_seen`) in the campaign summary JSON field.
* Configured `record_to_domain` (`backend/app/services/campaign_engine/repository.py`) to safely support camelCase and snake_case properties, adding robust fallbacks to `record.created_at`/`record.updated_at` (or current timezone-aware timestamp) to guarantee successful validation.
* Added `id: int` to both `Campaign` Pydantic model (`backend/app/services/campaign_engine/models.py`) and `CampaignResponse` (`backend/app/services/campaign_engine/schemas.py`) schemas, mapping it in repository queries.
* Enhanced `get_campaign_by_id` repository selector to support looking up campaigns by database primary key integer ID or campaign_id string identifier dynamically.

### 44.2 Campaigns Select Dropdown Selector (Frontend)
* Updated `Campaigns.jsx` (`frontend/src/pages/Campaigns.jsx`) to map the active campaign select dropdown values to `c.id` (database primary key ID) and displays `c.name` as display label.
* Fixed selection state matching to support mapping details dynamically using either `id` (integer) or `campaign_id` (UUID string), resolving the initial dropdown empty state stuck on mount.
* Verified that selecting other active campaign clusters dynamically triggers the fetch and clears selector placeholder views.

---

## 45. Authentication Module Foundation (Phase 1) (2026-08-07)

### 45.1 Authentication Module Initialized
* **Dedicated Authentication Directory**: Created a fully isolated structure at `frontend/src/auth/` containing core directories for `pages`, `components`, `context`, `hooks`, `services`, and `utils`.
* **Flow Architecture**: Implemented the foundation of the login workflow: `Login → JWT → Role → Permissions → Dashboard`.
* **State Context & Custom Hooks**: Created `AuthContext.jsx` and `useAuth.js` to manage, parse, and propagate authentication states, token data, permission validation functions, and user settings globally.

### 45.2 Components & Pages Created
* **AuthLayout.jsx**: Designed a premium SOC dashboard style split-layout with ambient cyber-themed background decorations, dynamic monitoring status panels, and a glassmorphism card container.
* **LoginForm.jsx**: Created the primary console form equipped with email validation, remember me toggles, loading animations, and error handling banners.
* **PasswordField.jsx**: Built a custom password entry field with toggleable show/hide behavior and focus highlights.
* **RememberMe.jsx**: Created a custom styled interactive checkbox.
* **ProtectedRoute.jsx**: Programmed a route guardian wrapping secure pages, performing permission/role clearance checks, and displaying a cryptographic session verification loader during initialization.
* **Login.jsx**: Form container rendering `LoginForm` and version confidentiality footer notices.
* **ForgotPassword.jsx**: Password reset request interface with mock API latency and transactional success state.
* **Unauthorized.jsx**: Security clearance error screen displaying active user credentials, permission mismatch details, and links to re-authenticate.

### 45.3 Mock Services & Utilities
* **authService.js**: Simulates backend database lookups with built-in network delays for simulated user validation (`admin@threatlens.io`, `analyst@threatlens.io`, `auditor@threatlens.io`).
* **jwt.js**: Provides functions to encode, decode, check expiration, and store simulated JSON Web Tokens in `localStorage`.
* **roles.js**: Defines standard roles (`admin`, `analyst`, `auditor`) and associated labels.
* **permissions.js**: Maps roles to security permissions (`view:dashboard`, `run:scans`, `manage:campaigns`, `export:reports`, `manage:settings`) and verifies operator clearance levels.

### 45.4 Integration and Routing
* **App.jsx**: Wrapped the root application tree in `AuthProvider` to enable global auth context availability.
* **routes/index.jsx**: Registered `/login`, `/forgot-password`, and `/unauthorized` as public routes and wrapped the existing dashboard layout route within `<ProtectedRoute>` to guard all dashboard pages from unauthenticated access.

### 45.5 Verification & Verification Results
* **Successful Build**: Verified that Vite executes build targets cleanly. Running `npm run build` succeeds with zero warnings/errors.
* **Browser Test Constraint**: Attempted automated browser execution verification, but encountered Playwright driver installation issues on the local runner environment due to non-200 CDN downloads. Local manual verification is recommended.

---

## 46. Login Interface Refinements (2026-08-07)

### 46.1 Interface Simplification
* **Login Identifier label change**: Replaced the input label from "Identity Email" to "ENTER ID" and updated its input type from `email` to a generic `text` input. Updated the placeholder text to `"Enter your ThreatLens ID"` to establish a generic user identifier input.
* **Removal of remember & recovery session controls**: Deleted the entire row containing the `Remember active session` checkbox and the `Recover Key` forgot-password redirection link. The submit button is now positioned directly beneath the credentials block, leaving no unused layout space.
* **Removal of the simulation widget**: Completely deleted the `Simulator Safe Credentials` footer container (including its title, `Mock Auth Enabled` status badge, and the three pre-filled credential role trigger buttons) to clean up the login card interface for production.
* **UI spacing adjustments**: Adjusted layout spacing and balanced margins within the card, ensuring a modern, distraction-free corporate login flow while preserving responsive CSS presentations.

---

## 47. Post-Merge Verification & E2E Regression Testing (2026-08-07)

### 47.1 Full monorepo merge & Dependency audits
* Verified the successful merge of the teammate's authentication module features into the `main` branch.
* Ran dependency sync checks (`npm install`) and verified frontend compiles successfully (`npm run build`).
* Resolved the campaign primary key schema validation crash in `/correlate` by dynamically mapping database IDs inside `save_campaign` repo helper.

### 47.2 End-to-End Regression Workflows
* Executed end-to-end integration tests (`test_campaign_api_e2e.py` and `test_e2e_m6.py`) confirming that user login simulations, scans submission, risk evaluations, and campaigns clustering attributes function perfectly.
* Confirmed that all backend APIs and frontend routes compile and load error-free.

---

## 48. Stage E.1 & E.2 Enterprise Authentication & Audit Logging Integration (2026-08-07)

### 48.1 Enterprise Authentication & Database Seeding (E.1)
* **Backend JWT Authentication**: Replaced mock authentication with a server-side JWT authentication pipeline. The backend issues signed tokens using `python-jose` (HS256) and stores them in client storage.
* **Pre-Provisioned Accounts Table**: Defined `EmployeeRecord` ORM representing pre-provisioned enterprise operator credentials.
* **lifespan Database Seeding**: Integrated automatic database seeding on startup, provisioning all 7 required credentials: `admin`, `soclead`, `analyst01`, `analyst02`, `threatintel`, `incident01`, `securitymgr` with bcrypt hashes.
* **Enterprise Restriction**: Disabled all public registration, self-service signups, and email recoveries.

### 48.2 Audit Logging & Authentication Guards (E.2)
* **AuditLogRecord ORM**: Created `auth_audit_logs` database table tracking all auth events: `login_success`, `login_failed`, `logout`, and `invalid_token` with IP addresses and User Agents.
* **JWT Guard Dependency**: Added `get_current_user` FastAPI dependency validating HTTP Bearer token signatures and logging invalid tokens.
* **Scan Attribution**: Added `initiated_by` to the `Scan` ORM and validated Pydantic schemas, tying manual URL submissions to the authenticated operator's User ID.
* **Frontend Headers & Session Display**: Refactored `apiClient` Axios interceptors to automatically attach the `Authorization` header, and wired the Topbar header to display the active operator's User ID, Role, and a fully functional logout modal.
* **Build Verification**: Run `npm run build` to confirm 100% clean frontend builds, and restarted backend verifying clean startup, model sync, and seeder execution. All systems ready for next phase.

---

## 49. Stage E.3 & E.4 Role-Based Access Control (RBAC) & Enterprise Security Hardening (2026-08-07)

### 49.1 Role-Based Access Control (E.3)
* **API Route Protection**: Implemented a reusable `RoleChecker` dependency class in `security.py` that checks the role embedded in the request's JWT payload and raises a 403 Forbidden on authorization mismatch.
* **Protected Write Access**: Restricted campaigns clustering `/correlate` and settings write routes to only high-clearance roles (`admin`, `soc_lead`, `threat_intel`, `security_manager`).
* **Frontend Role Guards**: Applied client-side authorization routing inside `routes/index.jsx` using the `allowedRoles` filter on protected routes.
* **Dynamic Navigation**: Configured `Sidebar.jsx` to filter navigation links and hide unauthorized pages (e.g. Campaigns or Settings) if the user's role lacks access.

### 49.2 Enterprise Hardening & Lockout (E.4)
* **Brute-Force Protection**: Added `failed_login_attempts` counter and `locked_until` datetime fields to `EmployeeRecord` ORM.
* **Temporary Lockout**: Automatically locks user accounts temporarily for 15 minutes after 5 consecutive failed login attempts, recording `account_locked` in the authentication audit log.
* **Session Lifecycle Redirects**: Handled 401 Unauthorized API failures (due to expired or modified tokens) in the Axios `apiClient` interceptor by wiping the token from `localStorage` and redirecting users to `/login?session=expired`.
* **Session Info UI**: Updated the header and sidebar components to output the active user ID and their role designation.

---

## 50. Stage E.5 & E.6 Session Management & Final Security Audit (2026-08-07)

### 50.1 Session Management & Activity Monitoring (E.5)
* **ActivityLogRecord ORM**: Created the `analyst_activity_logs` table to store detailed analyst actions (`dashboard_view`, `scan_create`, `scan_view`, `campaign_view`, `ai_assistant_query`, `report_export`) along with User ID, IP address, and User Agent.
* **Auto-Logout Expiry Check**: Added a periodic check loop inside `AuthContext.jsx` running every 10 seconds. It automatically flags token expiration, clears local session credentials, and redirects users to `/login?session=expired`.
* **Traceable API Access**: Injected `log_activity` calls in dashboard endpoints, scan creation/details, campaigns list/details, and AI Assistant conversational `/ask` and `/report` exports.

### 50.2 Authentication Validation & Final Security Audit (E.6)
* **Pre-defined Account Login**: Verified authenticating with predefined SOC Analyst accounts. Success writes `login_success` in audit logs and redirects to Dashboard.
* **Access Checks**: Verified that accessing `/stats` or `/recent-feed` without a valid token yields a 401 response and records `invalid_token` in the logs.
* **Scan Attribution**: Confirmed that manually running scans logs the `scan_create` action and maps `initiated_by` to the authenticated operator's user ID.
* **RBAC Enforcement**: Confirmed that when an account with the role `analyst` attempts to trigger correlation at `/correlate` or accessSettings, the backend returns a 403 Forbidden, and the frontend dynamically hides these links.
* **E2E Workflow Validation**: Successfully ran the complete SOC workflow from logging in, viewing stats, submitting indicators, obtaining AI breakdowns, exporting analyst reports, and logging out. All actions verified inside database activity tables.

---

## 51. Hotfix H.1 — Restore Campaigns & Settings Navigation (2026-08-08)

### 51.1 Restore Sidebar Links & Routing
* **Sidebar Link Restoration**: Restored the main sidebar menu items array to include Campaigns and Settings unconditionally. Links are rendered in the exact original order: Dashboard, Scans, Campaigns, Reports, Settings.
* **Frontend Routing Restoration**: Reconnected `Campaigns` and `Settings` page components under the main protected `/campaigns` and `/settings` routes, wrapped in standard authentication checks.
* **RBAC Preservation**: Kept all existing token parsing and JWT authentication logic fully intact on both the frontend and backend.

---

## 52. Stage F.1 & F.2 Navigation & Route Recovery, Module Synchronization & Navigation Validation (2026-08-08)

### 52.1 Navigation & Route Recovery (F.1)
* **Sidebar Links Restoration**: Restored sidebar menu items array to unconditionally include all 5 modules in the exact required layout and order: Dashboard, Scans, Campaigns, Reports, Settings.
* **Route Reconnection**: Reconnected Campaigns and Settings page routes under the protected workspace wrapper in `routes/index.jsx`, ensuring authentication state is preserved upon refreshing.

### 52.2 Module Synchronization & Validation (F.2)
* **Cross-Module Deep-Linking**: Verified all module pivot links:
  * Dashboard KPI cards deep-link correctly to `/scans`, `/campaigns`, and `/settings`.
  * Campaigns domain list table links to `/reports?scanId={id}` report previews.
  * Reports selector header pivot links to `/scans/{id}` scan details.
  * Settings view features a session termination logout command.
* **Dynamic Content Checking**: Confirmed that all views fetch live database entries without any fallback placeholder values.




