# Project Notes

> *NOTE TO AGENT: You must read and review `PROJECT_NOTES.md` at the start of every task/prompt to maintain full context of project progress, design decisions, and active changes.*

---

## 1. Project Vision & Problem Statement

### Project Vision
ThreatLens aims to be the definitive open-source enterprise brand protection platform. By combining real-time OSINT scraping, machine learning heuristic classifiers, computer vision page structural similarity, and natural language sentiment analysis, ThreatLens democratizes threat detection. We empower security groups of all sizes to preemptively secure their online presence and neutralize attacks before they cause financial or reputational damage.

### Problem Statement
Corporate brand impersonation and high-fidelity phishing websites have become increasingly cheap and trivial to launch. Attackers rapidly deploy lookalike domains, scrape official corporate assets, and trick employees or clients. Existing security solutions are often reactive, opaque, or slow to flag new threats. SOC analysts are overwhelmed with raw logs and lack actionable evidence (e.g. OCR transcripts, brand asset matching details, structural comparison scores) required to justify rapid domain takedown requests.

### Target Users
- **SOC Analysts**: Need a unified portal to review visual similarity scores, OCR extractions, and launch automated DNS/WHOIS lookups.
- **Threat Intelligence Leads**: Need to cluster brand abuse incidents into logical "campaigns" and track threat group behavior over time.
- **CISO / Security Managers**: Need high-level dashboards of active risks, metrics on takedown durations, and exportable executive reports.

---

## 2. Scope & Boundaries

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

## 3. System Architecture & Design Segregation

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

## 4. Decision Log

| Date | Decision | Rationale | Alternatives Considered | Status |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-06 | Choose FastAPI over Django | Lighter footprint, native async support for network requests, autogenerated OpenAPI docs. | Django REST Framework | Approved |
| 2026-08-06 | PostgreSQL + SQLAlchemy | Need robust relational integrity for campaign grouping and cross-evidence linking. | MongoDB | Approved |

---

## 5. Risk Register

| Risk ID | Risk Description | Likelihood | Impact | Mitigation Plan |
| :--- | :--- | :--- | :--- | :--- |
| R-001 | Scanning engines get blocked by Cloudflare/Cloudfront on targets | High | High | Rotate scrape proxies and user-agent strings. Fallback to headless browser capture engines. |
| R-002 | AI models take too long to run synchronously | Medium | High | Decouple scanning from response via FastAPI background tasks or a task queue. |

---

## 6. Completed Progress Tracker & Revision History

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

---

## 7. Verification Checklist for Manual Testing

Ensure the local PostgreSQL database is running, then run the following checks:
1. **Server Startup**: Run `uvicorn app.main:app --reload` and check that database tables initialization triggers successfully.
2. **Readiness Check**: Hit `GET /api/v1/health/ready` and confirm `{"status":"ready","checks":{"app":"ok","database":"ok"}}` is returned with `200 OK`.
3. **Interactive OpenAPI Docs**: Navigate to `http://127.0.0.1:8000/docs` and confirm the 6 core resource groups (`Domains`, `Scans`, `Campaigns`, `Features`, `Risk Scores`, `Feature Extraction`) show the endpoint actions.
4. **Validation Test**: Try sending a `POST /api/v1/domains` request with a missing required parameter (e.g. omitting `url`) and verify that FastAPI throws a `422 Unprocessable Entity` validation error response.
5. **Operational Verification**: Try a `GET /api/v1/domains/999` and verify that the system correctly catches the null response and raises a `404 Not Found` response code.
6. **Feature Extraction Verification**: Submit a `POST /api/v1/extract/domain` with payload `{"url": "https://google.com", "scan_id": 1}` and verify it extracts domain metadata.
7. **Network Extraction Verification**: Submit a `POST /api/v1/extract/network` with payload `{"url": "https://google.com", "scan_id": 1}` and verify it resolves IP, extracts SSL details (availability, days until expiry, issuer), redirect history, and returns HTTP 201 status with the structured JSON payload.
