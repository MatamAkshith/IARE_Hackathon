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
| **Current** | Threat Intelligence Integration | Preparing integrations with threat intel feeds. |
| **Remaining** | Brand Intelligence | Favicon hash, page template text similarity, visual logo detection. |
| **Remaining** | Risk Scoring Engine | Explainable rules-based risk assessment engine. |
| **Remaining** | Campaign Correlation | Attacker attribution and clustering based on shared footprints. |
| **Remaining** | Explainable AI | Heuristics extraction summaries for SOC analysts. |
| **Remaining** | Dashboard UI | Analyst control panel and queue dashboard. |
| **Remaining** | Reporting | Exportable Markdown/PDF reports detailing threats evidence. |
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

## 7. Campaign Correlation Design

> [!NOTE]
> *This outlines the planned Campaign Correlation design. It is not yet implemented.*

Rather than treating target URLs as isolated events, ThreatLens groups assets into unified Campaign clusters based on shared infrastructure attributes. By matching footprints, analysts can identify the scope of target brands impersonation campaigns.

Correlated evidence attributes include:
- **Registrar similarity**: Domains registered near-simultaneously through matching registrars.
- **Shared nameservers**: Matching DNS nameservers.
- **Infrastructure reuse**: Hosting domains on identical IP ranges.
- **SSL Cert properties**: Identical certificates signatures or issuers.
- **Favicon hashes**: Matching icon visual assets.
- **HTML structure similarity**: Matching templates structure.

The correlation engine produces a Campaign group detailing associated domains, shared evidence, a correlation confidence score, and a brief explanation.

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
9. **Threat Intelligence Foundation (Stage 4.1)**: Structured modular framework (`app/services/threat_intel/`) containing Pydantic schemas (`models.py`) mapping verdicts and matches, an abstract base provider (`base.py:BaseThreatIntelProvider`) using `abc` with mandatory async methods (`lookup_url`, `lookup_domain`, `lookup_ip`), and a registry-based orchestration service (`service.py:ThreatIntelService`) to register and execute all configured feeds concurrently.
10. **VirusTotal Integration (Stage 4.2)**: Specific threat provider integration (`app/services/threat_intel/providers/virustotal.py`) implementing v3 API URLs and Domains endpoints. Encodes URLs using URL-safe base64 parameter hashing, parses analysis engine indicators, normalizes responses into standardized schemas, and handles errors (401, 404, 429) gracefully.
11. **PhishTank & URLHaus Integration (Stage 4.3)**: Specific threat provider integrations (`app/services/threat_intel/providers/phishtank.py` and `app/services/threat_intel/providers/urlhaus.py`) implementing URL reputation checks via their respective POST endpoints. PhishTank parses `in_database` and `valid` flags to assess phishing threats, while URLHaus parses `query_status` malware indicators. Both normalize results to standard verdicts and handle errors gracefully.

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
│   └── session.py          # SessionLocal database sessionmaker factory
├── middleware/
│   ├── logging_middleware.py
│   └── request_id.py
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
└── main.py
```

---

## 11. Decision Log

| Date | Decision | Rationale | Alternatives Considered | Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-06 | Choose FastAPI over Django | Lighter footprint, native async support for network requests, autogenerated OpenAPI docs. | Django REST Framework | Approved |
| 2026-08-06 | PostgreSQL + SQLAlchemy | Need robust relational integrity for campaign grouping and cross-evidence linking. | MongoDB | Approved |

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
- - **2026-08-06 (Sprint 1 - Task 11 - 19:50):** **Task 11 (Foundational CRUD RESTful API Layer):** Implemented standard RESTful routers mapping GET (lists & detail), POST (201 status), PUT, and DELETE handlers for domains, scans, campaigns, features, and risk scores. Mounted all routers under versioned api tags. Verified the entire compilation and endpoints layout in Swagger Docs.
- - **2026-08-06 (Sprint 1 - Task 12 - 20:00):** **Task 12 (Domain Intelligence Extraction Engine - Stage 3.1):** Deployed the domain parser and resolver service (`DomainIntelService`) handling URL normalizations, TLD suffixes parsing via `tldextract`, active A/MX/NS queries via `dnspython`, and creation/expiration tracking via `python-whois`. Exposed the `POST /api/v1/extract/domain` endpoint resolving scan requirements and persisting extracted attributes to database feature records.
- - **2026-08-06 (Sprint 1 - Task 13 - 20:10):** **Task 13 (Network & Certificate Intelligence - Stage 3.2):** Implemented `NetworkIntelService` extracting host IP, reverse DNS (PTR pointer lookup), peer SSL/TLS certificate details (issuer, subject, validity timelines, expiry delta, signature algorithms, TLS version, cipher suite) via socket wrapping, and GET connection metadata (status codes, redirects history, final destination URL). Exposed `POST /api/v1/extract/network` saving data to database feature records.
- - **2026-08-06 (Sprint 1 - Task 14 - 20:15):** **Task 14 (Webpage Feature Extraction & Aggregation Pipeline - Stage 3.3 & 3.4):** Deployed the webpage structure and element counter (`WebpageIntelService`) pulling page html metadata, form controls, resources, and link metrics using BeautifulSoup. Created orchestration pipeline (`FeatureAggregationService`) that aggregates domain, network, and webpage services safely into a single unified JSON evidence record. Updated `POST /api/v1/extract/domain` endpoint to store the complete aggregated object in the database features registry under key `domain_intel`.
- - **2026-08-06 (Sprint 1 - Task 15 - 20:22):** **Task 15 (Feature Extraction API & Finalization - Stage 3.5 & 3.6):** Exposed the complete Feature Extraction engine endpoints: `POST /api/v1/extract/` submitting a URL for full orchestration extraction and saving results; `GET /api/v1/extract/{id}` retrieving extraction evidence by database ID; `GET /api/v1/extract/history/{scan_id}` listing scan history features. Executed final stabilization passes.
- **2026-08-06 (Sprint 1 - Task 16 - 20:50):** **Task 16 (Documentation Enhancement):** Added development rule standards, technology stack classifications, workflow layouts, relationship diagrams, roadmaps, risk-scoring heuristics schemas, and campaign attribution footprints. Synchronized notes index copies.
- **2026-08-06 (Sprint 1 - Task 17 - 21:30):** **Task 17 (Threat Intelligence Foundation - Stage 4.1):** Set up external threat intelligence placeholder keys in configuration. Created `BaseThreatIntelProvider` abstract interfaces using `abc`, common Pydantic response models (`models.py`), and the service registry orchestration pattern (`service.py:ThreatIntelService`) to execute enabled providers concurrently.
- **2026-08-06 (Sprint 1 - Task 18 - 21:40):** **Task 18 (VirusTotal Integration - Stage 4.2):** Implemented `VirusTotalProvider` invoking URL (URL-safe base64 parameters) and Domain lookup endpoints. Mapped analysis category statistics results to common verdicts, extracted engine records details to standard matches, and captured HTTP status exceptions. Updated registry constructor mappings.
- **2026-08-06 (Sprint 1 - Task 19 - 22:00):** **Task 19 (PhishTank & URLHaus Integration - Stage 4.3):** Implemented `PhishTankProvider` and `URLHausProvider` executing POST reputation queries. Mapped database flag rules and query statuses to verdicts, extracted threat names and tags to standardized matches, and handled exceptions.

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
