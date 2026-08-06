# Database Design

## Database Conventions

- **Naming Conventions**:
  - Tables and columns are named in `snake_case` pluralized (e.g. `companies`, `scan_jobs`).
  - Primary keys are named `id` (bigint or uuid).
  - Foreign keys are named `entity_id` (e.g. `company_id`).
- **ORM Style**: Standard declarative base mapping in SQLAlchemy. Relationships are loaded lazily by default unless query optimizations are explicitly required (e.g. `selectinload`).
- **Indexes**: Indices are declared for lookup columns like `status`, `target_url`, and `campaign_id` to boost query performance.

## Entity Relationship Overview

```text
+---------------+         +---------------+         +---------------+
|   companies   |1      * |   scan_jobs   |*      1 |   campaigns   |
|---------------|---------|---------------|---------|---------------|
| id            |         | id (UUID)     |         | id            |
| name          |         | target_url    |         | name          |
| logo_url      |         | company_id    |         | pattern_hash  |
| domains (JSON)|         | status        |         | status        |
+---------------+         | risk_score    |         +---------------+
                          | campaign_id   |
                          +---------------+
                                  | 1
                                  |
                                  | *
                          +---------------+
                          |   evidence    |
                          |---------------|
                          | id            |
                          | job_id        |
                          | type (Enum)   |
                          | details (JSON)|
                          +---------------+
```

## Tables Details

### `companies`
Stores the registered company identities and their baseline configurations.
- `id` (BIGINT, Primary Key)
- `name` (VARCHAR(255), Not Null)
- `legitimate_domains` (JSONB, Not Null)
- `logo_url` (VARCHAR(1024), Nullable)
- `created_at` (TIMESTAMP, default: now)

### `scan_jobs`
Tracks each URL analysis job request and final evaluation score.
- `id` (UUID, Primary Key)
- `target_url` (VARCHAR(2048), Not Null)
- `company_id` (BIGINT, Foreign Key referencing `companies.id`, Not Null)
- `status` (VARCHAR(50), default: 'PENDING')
- `risk_score` (INTEGER, Nullable)
- `campaign_id` (BIGINT, Foreign Key referencing `campaigns.id`, Nullable)
- `created_at` (TIMESTAMP, default: now)

### `evidence`
Stores visual, heuristic, and textual metadata artifacts extracted from target web properties.
- `id` (BIGINT, Primary Key)
- `job_id` (UUID, Foreign Key referencing `scan_jobs.id`, Not Null)
- `evidence_type` (VARCHAR(50)) -- e.g. 'SCREENSHOT', 'DOM_HTML', 'DNS', 'WHOIS'
- `details` (JSONB) -- e.g. `{"p_hash": "a1b2...", "registrar": "GoDaddy"}`
- `created_at` (TIMESTAMP, default: now)

### `campaigns`
Groups distinct detection instances that share standard patterns indicating they are run by the same threat actor.
- `id` (BIGINT, Primary Key)
- `name` (VARCHAR(255))
- `pattern_hash` (VARCHAR(64), Nullable) -- e.g., similar screenshot hash clusters
- `status` (VARCHAR(50), default: 'ACTIVE')
- `created_at` (TIMESTAMP, default: now)
