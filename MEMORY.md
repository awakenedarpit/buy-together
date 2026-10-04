# MEMORY.md — Project Memory & Continuity Ledger

> **Notice**: This file tracks the live state of the "Buy Together" project. It must be updated at the end of every development phase or session to ensure flawless continuity across AI models, sessions, and human collaborators.

---

## 1. Current Status

* **Phase**: PHASE 3 Completed & Verified -> Ready for PHASE 4 (Member Request Workflow + CRUD)
* **Overall Completion**: 45%
* **Current Task**: Completed Phase 2 (Database & Auth) and Phase 3 (AI Provider Abstraction, Extraction Pipeline, Message Persistence)
* **Last Completed Task**: Phase 3 full regression check (31/31 tests passing) and documentation updates
* **Next Task**: PHASE 4 — Member Request Workflow + CRUD (`GET /api/v1/requests`, `PATCH /api/v1/requests/{id}`, `DELETE /api/v1/requests/{id}`)

---

## 2. Verification Status Summary

```text
Phase 2: VERIFIED
Phase 3: VERIFIED

AI provider:
Mock: VERIFIED (Deterministic fixtures for Hinglish & English)
Local Gemma: VERIFIED (Architecture, lazy loading, and error handling verified)
Hosted: NOT IMPLEMENTED / PLANNED (Extension stub in place)

Message ingestion:
VERIFIED (POST /api/v1/messages and GET /api/v1/messages)

Request extraction:
VERIFIED (Zero-trust Pydantic and business validation pipeline)

Known environment limitations:
Local Gemma 4 12B inference: NOT VERIFIED — ENVIRONMENT BLOCKED (macOS CPU; no local model weights)

GitHub state:
Remote: https://github.com/awakenedarpit/buy-together.git
Account: awakenedarpit
Branch: main

Next phase:
Phase 4 — Member Request Workflow + CRUD
```

---

## 3. Completed Work

* **Phase 0**:
  - Initialized Git repository in `/Users/user/PYDATA`.
  - Comprehensive documentation (`PRD.md`, `TRD.md`, `ARCHITECTURE.md`, `API.md`, `DATABASE.md`, `AI.md`, `SECURITY.md`, `TESTING.md`, `DEPLOYMENT.md`, `DEVELOPMENT.md`, `AI_AGENT_HANDOFF.md`, ADRs 001–004).
  - Continuity ledger (`AGENTS.md`, `MEMORY.md`, `TASKS.md`, `CHANGELOG.md`).
* **Phase 1**:
  - Python virtual environment `.venv` with FastAPI, SQLAlchemy, Pydantic, Alembic, pytest.
  - React + Vite + Tailwind CSS frontend scaffold with verified build.
  - Healthcheck endpoint `/api/v1/health`.
* **Phase 2** (`commit 0bf88e5`):
  - SQLAlchemy 2.0 ORM models: `User`, `Message`, `RequestItem`.
  - Alembic migration environment and initial migration `1ea134d4c373`.
  - Password hashing via `pwdlib` (`bcrypt`).
  - JWT token generation & verification (`create_access_token`, `verify_token`).
  - Auth endpoints: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`.
  - Role-based authorization dependency `require_role(role)`.
  - 13/13 unit and integration tests passing.
* **Phase 3**:
  - Abstract AI provider contract `BaseAIProvider` in `backend/app/ai/base.py`.
  - Pydantic extraction schemas `ExtractedItem` and `ExtractionResult` in `backend/app/schemas/ai.py`.
  - Prompt template `v1_extract.txt` with few-shot Hinglish examples.
  - Deterministic `MockAIProvider` with Hinglish, English grocery, greeting, and error simulation support.
  - `LocalGemmaProvider` with lazy loading and environment failure protection.
  - `HostedGemmaProvider` stub for future cloud inference.
  - Central provider factory `get_ai_provider` with `AI_PROVIDER` configuration setting.
  - `ExtractionService` zero-trust validation & unit canonicalization pipeline.
  - `MessageService` atomic transaction orchestrator.
  - Message endpoints: `POST /api/v1/messages` and `GET /api/v1/messages` with member ownership isolation.
  - 31/31 unit, integration, and security tests passing.

---

## 4. Test Results

* Total Tests: **31 passed** in 5.62s
  - `backend/tests/test_ai_provider.py`: 12 passed
  - `backend/tests/test_auth.py`: 10 passed
  - `backend/tests/test_database.py`: 2 passed
  - `backend/tests/test_health.py`: 1 passed
  - `backend/tests/test_messages.py`: 6 passed
* Frontend Build: **Passed** (`vite build` in 148ms)

---

## 5. Known Limitations & Environment Details

* **Inference Runtime**: The development machine is macOS on CPU. Live execution of `google/gemma-4-12b-it` is marked `NOT VERIFIED — ENVIRONMENT BLOCKED`. Local unit and integration testing relies strictly on `MockAIProvider`.
* **Database**: Local development and CI run against in-memory SQLite with full schema compatibility; production targets managed PostgreSQL.
* **Secrets Policy**: Zero secrets committed; all configurations driven via environment variables and `.env.example`.

---

## 6. Next Actions

1. Review and commit Phase 3 implementation (`feat(ai): add provider abstraction and request extraction pipeline`).
2. Push Phase 3 to GitHub `origin/main` (`awakenedarpit/buy-together`).
3. Verify remote push on GitHub.
4. Begin **Phase 4**: Member Request Workflow + CRUD (`GET /api/v1/requests`, `PATCH /api/v1/requests/{id}`, `DELETE /api/v1/requests/{id}`).
