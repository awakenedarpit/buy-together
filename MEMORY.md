# MEMORY.md — Project Memory & Continuity Ledger

> **Notice**: This file tracks the live state of the "Buy Together" project. It must be updated at the end of every development phase or session to ensure flawless continuity across AI models, sessions, and human collaborators.

---

## 1. Current Status

* **Phase**: PHASE 1 Completed -> Ready for PHASE 2 (Database, SQLAlchemy Models & Migrations)
* **Overall Completion**: 20%
* **Current Task**: Completed Phase 1 backend & frontend scaffolds, automated healthcheck test, and frontend build; establishing GitHub remote
* **Last Completed Task**: Created FastAPI backend with Pydantic settings & CORS, React + Vite + Tailwind frontend, Pytest suite
* **Next Task**: PHASE 2 — Database setup, SQLAlchemy 2.0 models (`User`, `Message`, `RequestItem`), Alembic migrations

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
* Authored complete technical documentation suite in `docs/` (`PRD.md`, `TRD.md`, `ARCHITECTURE.md`, `API.md`, `DATABASE.md`, `AI.md`, `SECURITY.md`, `TESTING.md`, `DEPLOYMENT.md`, `DEVELOPMENT.md`, `AI_AGENT_HANDOFF.md`, `ADR-001` through `ADR-004`).
* Authored root `README.md`.
* Installed GitHub CLI (`gh 2.102.0`) via Homebrew and verified active authentication (`awakenedarpit`).
* Established Python virtual environment `.venv` and installed all backend production & test dependencies.
* Implemented modular backend scaffold:
  - `backend/app/core/config.py` with typed Pydantic `BaseSettings`.
  - `backend/app/core/logging.py` with formatted application logging.
  - `backend/app/api/v1/health.py` healthcheck route.
  - `backend/app/main.py` FastAPI app with lifespan handler and CORS middleware.
  - `pytest.ini` and `backend/tests/test_health.py`.
* Verified backend test suite with Pytest (1 passed in 0.01s).
* Established React + Vite + Tailwind CSS frontend scaffold in `frontend/`.
* Verified frontend build via `npm run build` (built cleanly in 439ms).

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
