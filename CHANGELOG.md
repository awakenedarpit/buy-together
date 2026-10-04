# Changelog

All notable changes to the **Buy Together** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - Hackathon MVP Release (Live Demo)

### Added
- Member Request Items CRUD API (`/api/v1/requests`, `/api/v1/requests/my`, `PATCH /api/v1/requests/{id}`, `DELETE /api/v1/requests/{id}`) with strict ownership enforcement (IDOR protection).
- Manager Procurement & Dynamic Aggregation API:
  - `GET /api/v1/manager/requests`: Complete member breakdown view with user profile information.
  - `GET /api/v1/manager/combined`: Dynamic SQL aggregation grouped by `(name, variant, unit)` with financial summaries.
  - `PATCH /api/v1/manager/requests/{id}/price`: Wholesale/retail unit pricing.
  - `PATCH /api/v1/manager/requests/{id}/status`: Procurement lifecycle state updates.
- Full React 19 + Vite 8 Single Page Application (`frontend/src/App.jsx`):
  - 1-click Quick Demo account fill for Member and Manager personas.
  - Natural-language request input box supporting Hinglish (*"bhai 2 notebook aur ek blue pen"*).
  - Real-time AI extraction result feedback cards.
  - Member active requests list with inline edit modal and instant deletion.
  - Manager Procurement Dashboard with KPI metrics, dynamic consolidated table, and member breakdown.
- Cloudflare Tunnel integration for zero-friction public HTTPS endpoints for frontend and backend.
- Automated end-to-end verification script testing all 10 user flow steps against live servers.

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
- Database & Authentication (Phase 2):
  - SQLAlchemy 2.0 ORM models: `User`, `Message`, `RequestItem`.
  - Alembic migration environment and initial migration `1ea134d4c373`.
  - Secure bcrypt password hashing via `pwdlib`.
  - JWT token generation and verification (`create_access_token`, `verify_token`).
  - Auth endpoints: `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`.
  - Role-based authorization dependency `require_role(role)`.
  - Isolated test fixtures with in-memory SQLite rollback sessions.
- AI Provider & Extraction Pipeline (Phase 3):
  - Provider abstraction interface `BaseAIProvider` decoupling application code from AI runtimes.
  - Deterministic `MockAIProvider` with Hinglish, English grocery, greeting, and error simulation fixtures.
  - `LocalGemmaProvider` with lazy loading, precision mapping, and missing-weight safety guards.
  - `HostedGemmaProvider` stub for remote inference endpoints.
  - Provider factory `get_ai_provider` resolving provider via `AI_PROVIDER` configuration setting.
  - Zero-trust `ExtractionService` validating and canonicalizing item names, quantities, and units.
  - `MessageService` coordinating atomic message and request-item persistence.
  - Endpoints: `POST /api/v1/messages` and `GET /api/v1/messages` with member ownership isolation.
  - Comprehensive unit and integration test suite (31 tests passing).

### Security
- Mandated zero-trust pipeline for AI model outputs: strict validation through Pydantic before database writes.
- Established strict Role-Based Access Control (RBAC) separating `MEMBER` and `MANAGER` capabilities.
- Prohibited committing raw `.env` files, API tokens, or model weights.
- Enforced strict member ownership verification on message history endpoints.
