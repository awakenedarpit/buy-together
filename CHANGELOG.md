# Changelog

All notable changes to the **Buy Together** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Git repository initialization and `.gitignore` targeting Python, Node, and model weight assets.
- `.env.example` defining explicit configuration contracts for API, database, auth, and AI providers.
- `AGENTS.md` operating manual for AI coding agents with zero-trust AI rules and memory handoff protocols.
- `MEMORY.md` dynamic state ledger for continuity between model switches and sessions.
- `TASKS.md` 18-phase implementation roadmap.
- Complete documentation suite under `docs/`: PRD, TRD, ARCHITECTURE, API, DATABASE, AI, SECURITY, TESTING, DEPLOYMENT, DEVELOPMENT, AI_AGENT_HANDOFF, and ADR-001 through ADR-004.
- Foundational `README.md`.
- Backend modular architecture scaffold:
  - `backend/app/core/config.py` using `pydantic-settings` BaseSettings.
  - `backend/app/core/logging.py` structured application logging.
  - `backend/app/api/v1/health.py` health check endpoint.
  - `backend/app/main.py` FastAPI app with lifespan handler and CORS middleware.
  - `backend/requirements.txt` with FastAPI, Uvicorn, SQLAlchemy, Pydantic, Alembic, psycopg, PyJWT, bcrypt, pytest.
  - `pytest.ini` with test runner options.
  - `backend/tests/test_health.py` verifying `/api/v1/health` (100% passing).
- Frontend application scaffold:
  - React 18 + Vite 6 + Tailwind CSS v4 in `frontend/`.
  - Configured `@tailwindcss/vite` plugin and `frontend/src/index.css`.
  - Initial `App.jsx` status dashboard connecting to healthcheck API.
  - Verified clean production build (`npm run build`).

### Security
- Mandated zero-trust pipeline for AI model outputs: strict validation through Pydantic before database writes.
- Established strict Role-Based Access Control (RBAC) separating `MEMBER` and `MANAGER` capabilities.
- Prohibited committing raw `.env` files or credentials.
