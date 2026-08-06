# Roadmap

## Phase 1: MVP Setup & Core Pipeline (Day 1)
- [x] Initial boilerplate setup, git branch conventions, and container setup.
- [ ] Implement Scraper engine utilizing headless browser libraries to fetch HTML/screenshot.
- [ ] Connect PostgreSQL schema, migrations, and model persistence via SQLAlchemy.
- [ ] Develop simple scoring engine using string matching rules (keyword checks, SSL existence, registration age).
- [ ] Build basic React client with target URL submission dashboard.

## Phase 2: AI Integration & Campaign Abstractions (Day 2)
- [ ] Implement OpenCV visual template matcher to extract structural match percentages.
- [ ] Deploy NLP classifiers using HuggingFace transformer pipelines to detect brand impersonation texts.
- [ ] Formulate multidimensional clustering of targets into logical Campaigns using DB queries on registrar networks.
- [ ] Design the analyst portal interactive details view showing logo highlights and visual comparisons.

## Phase 3: Reporting & Takedowns (Day 3)
- [ ] Compile automatically synthesized threat reports including visual side-by-side components.
- [ ] Automate WHOIS parsing to locate registrar abuse contact addresses.
- [ ] Generate downloadable markdown and PDF compliance packets.

## Future Scope / Enhancements
- **Active DNS Sinkholing Integration**: Auto-notify Cloudflare/Google DNS resolvers.
- **Deep fake identity checks**: Identify false brand profiles across major social networks.
- **Chrome/Firefox browser extensions**: Real-time evaluation of visited domains.
