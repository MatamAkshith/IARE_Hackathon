# ThreatLens

ThreatLens is an AI-powered Enterprise Phishing & Brand Impersonation Detection platform.

## Project Overview

ThreatLens is designed to proactively protect brand assets and detect corporate brand impersonations, high-fidelity phishing campaigns, and rogue digital presences. By automating comparison between suspicious targets and official company websites, analyzing lookalike domains, correlating visual indicators, and extracting explainable risk signals, ThreatLens enables security operations centers (SOC) to identify and mitigate risks rapidly.

## Objectives

- **Brand Protection**: Identify impersonation websites, lookalike domains, and social profiles.
- **Explainable Security Features**: Extract deep heuristic, textual, and visual indicators.
- **Multimodal Evidence Correlation**: Correlate signals across multiple feeds and threat intelligence sources.
- **Explainable Risk Scoring**: Compute a transparent threat index with visual proof and rationale.
- **Analyst Reporting**: Generate comprehensive, shareable threat intelligence reports.

## Tech Stack

- **Frontend**: React, Vite, TailwindCSS, React Router, Axios
- **Backend**: Python, FastAPI
- **Database**: PostgreSQL, SQLAlchemy ORM
- **AI/ML**: HuggingFace (transformer-based NLP models), OpenCV (computer vision matching), Scikit-learn (heuristic modeling)
- **Deployment**: Docker, Docker Compose

## Folder Structure

```text
├── assets/             # Shared static visual/brand assets
├── backend/            # Python FastAPI backend service
│   └── app/            # Main application logic
├── config/             # Environment, server, and system configuration files
├── datasets/           # Phishing signatures and training/validation datasets
├── docker/             # Dockerfiles and environment-specific compose components
├── docs/               # Architecture, workflow, and design documentation
├── frontend/           # Vite + React frontend web application
│   └── src/            # React source code (components, pages, services)
├── logs/               # Application log output directories
├── scripts/            # Database initialization, migration, and automation scripts
├── tests/              # Test suites for backend, frontend, and integration tests
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusion specifications
├── docker-compose.yml  # Multi-container service orchestrator configuration
└── README.md           # Project configuration and entry documentation
```

## Setup

Refer to the development guidelines for deployment:
1. Copy `.env.example` to `.env` and fill in necessary parameters.
2. Run `docker-compose up --build` from the root directory.

## Architecture Overview

ThreatLens uses a decoupled microservices architecture:
- **Client Tier**: A responsive React SPA for analysts to view detections, submit analyses, and export reports.
- **Application Tier**: A FastAPI web server handling domain queuing, ingestion pipelines, external API lookups, and routing jobs to the AI processing layer.
- **Storage Tier**: PostgreSQL database utilizing SQLAlchemy for structured threat tables, campaign entities, and historical scan results.
- **AI Processing Pipeline**: Specialized pipeline executing OCR/screenshot analysis with OpenCV, classification of page structures with Scikit-learn, and sentiment/brand extraction via HuggingFace models.

## Development Workflow

1. Setup environment variables.
2. Initialize database schemas.
3. Start development servers or Docker containers.
4. Run testing pipelines before committing changes.

## Contributors

- [Contributor Name / Placeholder]

## License

This project is licensed under the MIT License.

## Future Scope

- Integration with active takedown APIs and registrar hooks.
- Real-time browser extension for proactive end-user warning.
- Domain monitoring feed integrations.