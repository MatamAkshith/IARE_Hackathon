# Hackathon Checklist

## Core Infrastructure
- [x] Configure backend project skeleton & directory layouts.
- [x] Configure frontend project skeleton, Tailwind, PostCSS, and Vite configs.
- [x] Create multi-container docker-compose setup for local development.
- [ ] Initialize PostgreSQL database configurations and database pool connector.

## Extraction Pipelines
- [ ] Develop async Target URL ingestion scraping logic (HTTP responses, DOM text).
- [ ] Configure headless browser screenshot generator utilizing target rendering.
- [ ] Configure WHOIS parser to capture domains age, registrar name, and registry logs.
- [ ] Integrate real-time DNS queries (A, MX, NS records checks).

## AI Detection Engines
- [ ] Build OpenCV logo matcher utilizing template-matching functions on screenshots.
- [ ] Build Scikit-learn structural distance classifier evaluating tag counts.
- [ ] Add HuggingFace pipeline for brand-name extraction and sentiment matching.
- [ ] Formulate weighted explainable risk score calculation logic.

## Analyst Frontend
- [ ] Build responsive dashboard showing scan queue entries.
- [ ] Build scanning jobs status monitoring panel.
- [ ] Build details view including side-by-side screenshot comparisons and logo highlight boundaries.
- [ ] Build campaign groupings viewer to show associated domains.
- [ ] Integrate one-click Takedown Report downloads.
