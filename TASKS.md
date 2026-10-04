# TASKS.md — Project Task Management & Status Ledger

> **Status Legend**:
> - `[x]` Completed
> - `[/]` In Progress
> - `[ ]` Backlog
> - `[!]` Blocked

---

## Current Sprint Overview

- **Active Phase**: Phase 0 — Documentation and Continuity System
- **Next Phase**: Phase 1 — Repository & Development Environment Setup

---

## Phase 0: Project Documentation & Agent Continuity System

- [x] Inspect existing repository and system environment
- [x] Initialize Git repository
- [x] Create `.gitignore`
- [x] Create `.env.example`
- [x] Create `AGENTS.md`
- [x] Create `MEMORY.md`
- [x] Create `TASKS.md`
- [x] Create `CHANGELOG.md`
- [x] Create `docs/PRD.md` (Product Requirements Document)
- [x] Create `docs/TRD.md` (Technical Requirements Document)
- [x] Create `docs/ARCHITECTURE.md` (System Architecture)
- [x] Create `docs/API.md` (API Specification)
- [x] Create `docs/DATABASE.md` (Database Design & Aggregation)
- [x] Create `docs/AI.md` (Gemma 4 12B Integration & Prompting)
- [x] Create `docs/SECURITY.md` (Threat Model & Security Controls)
- [x] Create `docs/TESTING.md` (Testing Strategy & Fixtures)
- [x] Create `docs/DEPLOYMENT.md` (Deployment Strategy & Topology)
- [x] Create `docs/DEVELOPMENT.md` (Developer Onboarding & Workflow)
- [x] Create `docs/AI_AGENT_HANDOFF.md` (Model Switch Protocol)
- [x] Create Architecture Decision Records:
  - [x] `docs/decisions/ADR-001-postgresql.md`
  - [x] `docs/decisions/ADR-002-ai-provider-abstraction.md`
  - [x] `docs/decisions/ADR-003-polling.md`
  - [x] `docs/decisions/ADR-004-dynamic-aggregation.md`
- [x] Create foundational `README.md`
- [x] Review architecture documents for consistency and absence of contradictions

---

## Phase 1: Repository & Development Environment

- [x] Create modular directory structure (`backend/app`, `backend/tests`, `frontend/src`)
- [x] Setup Python environment and dependencies (`requirements.txt`, `pytest.ini`)
- [x] Setup Node/Vite/React frontend scaffold with Tailwind CSS
- [x] Configure environment variable loading with `pydantic-settings` (`backend/app/core/config.py`)
- [x] Setup structured logging module with standard formatter (`backend/app/core/logging.py`)
- [x] Implement FastAPI main entrypoint with CORS and lifespan handler (`backend/app/main.py`)
- [x] Verify FastAPI healthcheck endpoint (`/api/v1/health`) with automated tests
- [x] Verify React + Vite + Tailwind frontend build
- [x] Initialize GitHub remote repository and push Phase 0 and Phase 1 commits (`https://github.com/awakenedarpit/buy-together`)

---

## Phase 2: Database, Models & Migrations

- [x] Setup SQLAlchemy 2.0 database engine & session dependency
- [x] Define database models:
  - [x] `User` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`, `updated_at`)
  - [x] `Message` (`id`, `user_id`, `text`, `created_at`)
  - [x] `RequestItem` (`id`, `message_id`, `user_id`, `name`, `variant`, `quantity`, `unit`, `unit_price`, `status`, `created_at`, `updated_at`)
- [x] Setup Alembic migration environment
- [x] Generate initial database migration script
- [x] Verify migration execution and schema validation

---

## Phase 3: Authentication, JWT & Role Authorization

- [x] Implement secure password hashing with `bcrypt` / `pwdlib`
- [x] Implement JWT token generation and validation utilities
- [x] Create Pydantic auth schemas (`UserRegister`, `UserLogin`, `TokenResponse`, `UserOut`)
- [x] Implement `/api/v1/auth/register` endpoint
- [x] Implement `/api/v1/auth/login` endpoint
- [x] Implement `/api/v1/auth/me` endpoint
- [x] Create FastAPI authentication dependencies (`get_current_user`, `require_role(role)`)
- [x] Write unit and integration tests for authentication and RBAC

---

## Phase 4 (AI Abstraction & Extraction Pipeline)

- [x] Define `BaseAIProvider` abstract interface class
- [x] Define extraction input and output data contracts (`ExtractedItem`, `ExtractionResult`)
- [x] Implement `MockAIProvider` with deterministic test fixtures and Hinglish examples
- [x] Implement provider factory based on `AI_PROVIDER` configuration setting
- [x] Write unit tests verifying provider interchangeability
- [x] Create versioned prompt template (`prompts/v1_extract.txt`) with few-shot Hinglish examples
- [x] Implement `LocalGemmaProvider` using Transformers / PyTorch pipeline
- [x] Implement `HostedGemmaProvider` stub for remote inference endpoints
- [x] Add runtime error handling, model loading status, and graceful fallback
- [x] Implement strict Pydantic validation on model output (`ExtractedItem`)
- [x] Implement normalization logic (trimming, lowercase names, singular units)
- [x] Handle malformed AI outputs, missing attributes, and zero/negative quantities
- [x] Write comprehensive validation test suite with edge cases
- [x] Implement `GeminiProvider` using official `google-genai` SDK with strict JSON output
- [x] Integrate `GEMINI_API_KEY` and `GEMINI_MODEL` server-side settings
- [x] Implement automatic fallback to heuristic parser if Gemini API is unconfigured or times out
- [x] Enhanced UX in React frontend: "Understanding your request..." and "Requirements Added ✓"
- [x] Unit test suite covering all 5 prompt scenarios and zero-trust validation layers
- [x] Create message ingestion service (`MessageService`)
- [x] Connect ingestion pipeline: User Input -> Save Message -> AI Extract -> Validate -> Save Request Items
- [x] Implement `POST /api/v1/messages` and `GET /api/v1/messages` endpoints
- [x] Verify atomic transaction rollback if database write or AI provider fails

---

## Phase 8: Member CRUD & Ownership Control

- [x] Implement `GET /api/v1/requests` and `GET /api/v1/requests/my` (member's personal requests)
- [x] Implement `PATCH /api/v1/requests/{id}` (edit personal request)
- [x] Implement `DELETE /api/v1/requests/{id}` (delete personal request)
- [x] Enforce ownership checks (prevent members from editing others' items)
- [x] Write tests verifying IDOR protection and unauthorized access rejection

---

## Phase 9: Dynamic Aggregation Engine

- [x] Design dynamic aggregation query grouped by `(name, variant, unit)`
- [x] Calculate total consolidated quantities across all members
- [x] Build breakdown of contributing members per aggregated item
- [x] Ensure case-insensitive grouping (e.g., "notebook" vs "Notebook")
- [x] Write unit tests for aggregation math and grouping edge cases

---

## Phase 10: Manager APIs & Financial Calculations

- [x] Implement `GET /api/v1/manager/requests` (all requests by member)
- [x] Implement `GET /api/v1/manager/combined` (aggregated items with totals)
- [x] Implement `PATCH /api/v1/manager/requests/{id}/price` (set unit price)
- [x] Implement `PATCH /api/v1/manager/requests/{id}/status` (update item status)
- [x] Calculate line totals and grand totals purely in backend
- [x] Enforce manager-only route protection via RBAC

---

## Phase 11: React Frontend (Member Experience & 1-Click Demo)

- [x] Setup React + Vite frontend with modern dark aesthetic design system
- [x] Build Authentication views (`/login`, `/register`) with token storage
- [x] 1-Click Server-Side Demo Authentication (`POST /api/v1/auth/demo-login`):
  - [x] `🚀 Continue as Demo Member` prominent button
  - [x] `👑 Continue as Demo Manager` prominent button
  - [x] Zero client-side credentials (no emails/passwords in JS, localStorage, HTML, or public env)
  - [x] Idempotent server-side account provisioning & signed JWT issuance
- [x] Vercel SPA routing rewrites (`frontend/vercel.json`) for `/dashboard` and `/manager`
- [x] Build Member Dashboard:
  - [x] Natural language chat input bar (with quick sample prompts)
  - [x] Real-time item extraction feedback card
  - [x] Personal request table with inline edit and delete actions
  - [x] Status indicators (Pending, Approved, Purchased, Rejected)

---

## Phase 12: React Frontend (Manager Experience)

- [x] Build Manager Dashboard:
  - [x] Tab 1: Combined purchasing requirements table
  - [x] Tab 2: Member-by-member breakdown
  - [x] Inline price editing inputs
  - [x] Financial metrics bar (Grand total, total items, active members)
  - [x] Status selection per item

---

## Phase 13: Polling & Live Updates

- [ ] Configure resilient client-side polling (3–5s interval)
- [ ] Implement optimistic UI updates with error rollback
- [ ] Add background refresh pause when window is hidden/blurred
- [ ] Add network error banner and reconnection handling

---

## Phase 14: Automated Testing Suite

- [ ] Write backend unit tests (auth, services, models, validators)
- [ ] Write backend integration tests (FastAPI TestClient end-to-end flows)
- [ ] Write AI extraction test scenarios (English, Hindi, Hinglish inputs)
- [ ] Write frontend component and user flow tests

---

## Phase 15: Security Hardening

- [ ] Verify CORS origins, headers, and credentials policies
- [ ] Run security checks (SQL injection, XSS, rate limiting)
- [ ] Verify safe error handling with zero trace leakage
- [ ] Audit dependencies for known vulnerabilities

---

## Phase 16: Deployment & Infrastructure Setup

- [ ] Prepare Dockerfile and docker-compose for multi-container deployment
- [ ] Prepare Vercel / Netlify configuration for frontend
- [ ] Prepare Render / Railway deployment manifest for backend
- [ ] Test production build scripts (`npm run build`, Python production server)

---

## Phase 17: Documentation Cleanup & Demo Preparation

- [ ] Update `README.md` with complete architecture diagrams and demo credentials
- [ ] Update `CHANGELOG.md` with full version release notes
- [ ] Verify all documentation links and instructions
- [ ] Prepare end-to-end demo walkthrough video/script
