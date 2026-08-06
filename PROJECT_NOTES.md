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
The data layer is decoupled using three core patterns:
1. **Model Representation (SQLAlchemy ORM)**: Relational models (`Domain`, `Campaign`, `Scan`, `Feature`, `RiskScore`) inheriting from a shared declarative `Base` with automated table name lowercase formatting and common audit tracking fields (`id`, `created_at`, `updated_at`).
2. **Data Validation (Pydantic V2 Schemas)**: Segregates request parameters from response serializers to prevent data exposure and enforce strict type contracts:
   - `[Entity]Base`: Shared properties between create/update/response schemas.
   - `[Entity]Create`: Data required during model creation.
   - `[Entity]Update`: Fields allowed for patching existing records (all fields optional).
   - `[Entity]Response`: Final response schema serialized back to the client, adding database-specific fields (`id`, `created_at`, `updated_at`). Employs `model_config = ConfigDict(from_attributes=True)` for seamless SQLAlchemy serialization.
3. **Data Access (Repository Pattern)**: Implements `CRUDBase` as a generic helper module mapping standard ORM methods (`get`, `get_multi`, `create`, `update`, `remove`) using TypeVars. Specific CRUD repositories subclass `CRUDBase` and expose global singleton instances.

### Directory / Folder Structure Changes
```text
backend/app/
├── api/
│   ├── endpoints/
│   │   └── root.py
│   ├── deps.py             # Injects get_db and repository singletons
│   └── router.py
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
