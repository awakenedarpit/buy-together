# MEMORY.md — Project Memory & Continuity Ledger

> **Notice**: This file tracks the live state of the "Buy Together" project. It must be updated at the end of every development phase or session to ensure flawless continuity across AI models, sessions, and human collaborators.

---

## 1. Current Status

* **Phase**: PHASE 0 Completed -> Ready for PHASE 1 (Repository & Dev Environment)
* **Overall Completion**: 10%
* **Current Task**: Completed Phase 0 documentation & architecture review; ready to scaffold backend and frontend
* **Last Completed Task**: Created full documentation suite (PRD, TRD, ARCHITECTURE, API, DATABASE, AI, SECURITY, TESTING, DEPLOYMENT, DEVELOPMENT, AI_AGENT_HANDOFF, ADR-001 through ADR-004, README, TASKS, CHANGELOG)
* **Next Task**: PHASE 1 — Scaffold backend directory structure, requirements.txt, environment settings, and basic FastAPI application

---

## 2. Completed Work

* Initialized Git repository in `/Users/user/PYDATA`.
* Inspected host system: macOS Darwin, Python 3.14.7, Node.js v26.8.1, npm 11.19.0.
* Verified absence of local Docker and PostgreSQL daemons; confirmed SQLite test fallback strategy.
* Created comprehensive `.gitignore` targeting Python, Node, OS artifacts, and large AI model weight files.
* Created `.env.example` defining configuration contracts for Backend, Database, Auth, and AI providers.
* Created `AGENTS.md` operating manual establishing coding rules, zero-trust AI policies, and handoff protocols.
* Created `MEMORY.md` live state ledger.
* Created `TASKS.md` with granular checklists across all phases.
* Created `CHANGELOG.md` following Keep a Changelog standards.
* Authored `docs/PRD.md` with problem statement, personas, stories, requirements, and flows.
* Authored `docs/TRD.md` detailing technical stack, schemas, and pipeline.
* Authored `docs/ARCHITECTURE.md` with Mermaid layer diagrams and sequence workflows.
* Authored `docs/API.md` with exhaustive REST endpoints and JSON contracts.
* Authored `docs/DATABASE.md` with ERD, indexing, and dynamic aggregation queries.
* Authored `docs/AI.md` detailing Gemma 4 12B extraction, schema contracts, and provider abstraction.
* Authored `docs/SECURITY.md` covering threat model, bcrypt hashing, JWT, RBAC, and IDOR prevention.
* Authored `docs/TESTING.md` defining unit/integration test strategies, fixtures, and execution scripts.
* Authored `docs/DEPLOYMENT.md` defining cloud topology and low-cost deployment runbooks.
* Authored `docs/DEVELOPMENT.md` guiding local setup, virtual environments, and dev servers.
* Authored `docs/AI_AGENT_HANDOFF.md` establishing model-switch continuity protocols.
* Authored Architecture Decision Records:
  - `ADR-001-postgresql.md` (PostgreSQL as primary engine)
  - `ADR-002-ai-provider-abstraction.md` (Decoupled BaseAIProvider interface)
  - `ADR-003-polling.md` (Client-side HTTP polling for MVP)
  - `ADR-004-dynamic-aggregation.md` (Dynamic query-time grouping vs persistent table)
* Authored root `README.md` with project overview, architecture diagram, and quickstart instructions.
* Audited all documents to ensure complete conceptual consistency and absence of contradictions.

---

## 3. Current Work

* Ready to begin PHASE 1: Repository structure setup, Python virtual environment & dependencies, FastAPI healthcheck endpoint.

---

## 4. Next Actions

1. Complete and review all Phase 0 documentation for consistency and absence of contradictions.
2. Provide Phase 0 report to the user and request review/decisions.
3. Transition to PHASE 1: Scaffold repository directory structure, Python virtual environment, dependencies (`requirements.txt`), and initial FastAPI app skeleton.

---

## 5. Important Decisions

* **ADR-001**: PostgreSQL as the production database engine (with SQLite compatibility for fast local automated tests).
* **ADR-002**: Pluggable AI Provider Abstraction (`BaseAIProvider` interface with `LocalGemmaProvider`, `HostedInferenceProvider`, and `MockAIProvider`).
* **ADR-003**: HTTP Polling (3–5s interval) for real-time frontend updates in MVP rather than premature WebSockets complexity.
* **ADR-004**: Dynamic query-time aggregation (`GROUP BY name, variant, unit`) rather than a persistent mutable aggregate table, preventing synchronization drift.

---

## 6. Known Problems & Limitations

* **Local Machine Resources**: Docker and `psql` are not installed locally. Local development without Docker will either use a remote cloud PostgreSQL (e.g. Supabase or Neon) or SQLite fallback for initial local development/testing.
* **PyTorch / Gemma 12B Footprint**: Gemma 4 12B requires significant RAM/VRAM. A `MockAIProvider` is critical for immediate local functional development and test suites, while supporting local/hosted Gemma options.

---

## 7. Environment

* **OS**: macOS (Darwin 24.6.0)
* **Python**: 3.14.7
* **Node.js**: v26.8.1
* **npm**: 11.19.0
* **Git**: Initialized at `/Users/user/PYDATA/.git`
* **Secrets Policy**: Zero secrets committed. Use `.env.example` as a template.

---

## 8. Model/Agent Handoff Notes

* If switching models: Read `AGENTS.md` -> `MEMORY.md` -> `TASKS.md` -> `docs/ARCHITECTURE.md`.
* Check `git status` before beginning work.
* Maintain clean commits with conventional commit syntax (`feat:`, `fix:`, `docs:`, etc.).
* Never bypass Pydantic validation when ingesting AI model outputs.

---

## 9. Files Created / Modified

* `.gitignore` (Created)
* `.env.example` (Created)
* `AGENTS.md` (Created)
* `MEMORY.md` (Created - this file)

---

## 10. Database Status

* **Engine**: PostgreSQL (Planned / Target), SQLite (Test fallback)
* **ORM**: SQLAlchemy 2.0+
* **Migrations**: Alembic (Planned for Phase 2)
* **Tables**: `users`, `messages`, `request_items` (Planned)

---

## 11. AI Integration Status

* **Target Model**: Gemma 4 12B
* **Active Default Provider**: `MockAIProvider` (Phase 0/1 setup)
* **Prompt Version**: `v1` (Documented in `docs/AI.md`)
* **Structured Output Schema**: Validated via Pydantic (`RequestItemExtract`)
* **Status**: Specification and interface stage

---

## 12. Deployment Status

* **Frontend**: PLANNED (Vercel / Cloudflare Pages / Static Hosting)
* **Backend**: PLANNED (Render / Railway / Fly.io / Docker)
* **Database**: PLANNED (Supabase / Neon managed PostgreSQL)
* **AI Inference**: PLANNED (Local Gemma / HuggingFace Inference API)
