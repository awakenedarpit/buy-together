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

- [ ] Create modular directory structure (`backend/app`, `backend/tests`, `frontend/src`)
- [ ] Setup Python environment and dependencies (`requirements.txt`, `pyproject.toml`)
- [ ] Setup Node/Vite/React frontend scaffold
- [ ] Configure environment variable loading with `pydantic-settings`
- [ ] Setup structured logging module with JSON/standard formatter
- [ ] Verify FastAPI healthcheck endpoint (`/api/v1/health`)

---

## Phase 2: Database, Models & Migrations

- [ ] Setup SQLAlchemy 2.0 database engine & session dependency
- [ ] Define database models:
  - [ ] `User` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`, `updated_at`)
  - [ ] `Message` (`id`, `user_id`, `text`, `created_at`)
  - [ ] `RequestItem` (`id`, `message_id`, `user_id`, `name`, `variant`, `quantity`, `unit`, `unit_price`, `status`, `created_at`, `updated_at`)
- [ ] Setup Alembic migration environment
- [ ] Generate initial database migration script
- [ ] Verify migration execution and schema validation

---

## Phase 3: Authentication, JWT & Role Authorization

- [ ] Implement secure password hashing with `bcrypt` / `pwdlib`
- [ ] Implement JWT token generation and validation utilities
- [ ] Create Pydantic auth schemas (`UserRegister`, `UserLogin`, `TokenResponse`, `UserOut`)
- [ ] Implement `/api/v1/auth/register` endpoint
- [ ] Implement `/api/v1/auth/login` endpoint
- [ ] Implement `/api/v1/auth/me` endpoint
- [ ] Create FastAPI authentication dependencies (`get_current_user`, `require_role(role)`)
- [ ] Write unit and integration tests for authentication and RBAC

---

## Phase 4: AI Provider Abstraction

- [ ] Define `BaseAIProvider` abstract interface class
- [ ] Define extraction input and output data contracts (`ItemExtraction`, `ExtractionResult`)
- [ ] Implement `MockAIProvider` with deterministic test fixtures and Hinglish examples
- [ ] Implement provider factory based on `AI_PROVIDER` configuration setting
- [ ] Write unit tests verifying provider interchangeability

---

## Phase 5: Local & Remote Gemma Integration

- [ ] Create versioned prompt template (`prompts/v1_extract.txt`) with few-shot Hinglish examples
- [ ] Implement `LocalGemmaProvider` using Transformers / PyTorch pipeline
- [ ] Implement `HostedInferenceProvider` for HuggingFace / OpenAI-compatible remote endpoints
- [ ] Add runtime error handling, model loading status, and graceful timeout fallback

---

## Phase 6: AI Extraction & Validation Pipeline

- [ ] Implement strict Pydantic validation on model output
- [ ] Implement normalization logic (trimming, lowercase names, singular units)
- [ ] Handle malformed AI outputs, missing attributes, and zero/negative quantities
- [ ] Write comprehensive validation test suite with edge cases

---

## Phase 7: Messages & Request Item Creation

- [ ] Create message ingestion service
- [ ] Connect ingestion pipeline: User Input -> Save Message -> AI Extract -> Validate -> Save Request Items
- [ ] Implement `POST /api/v1/messages/` endpoint
- [ ] Verify atomic transaction rollback if database write fails

---

## Phase 8: Member CRUD & Ownership Control

- [ ] Implement `GET /api/v1/requests/my` (member's personal requests)
- [ ] Implement `PUT /api/v1/requests/{id}` (edit personal request)
- [ ] Implement `DELETE /api/v1/requests/{id}` (delete personal request)
- [ ] Enforce ownership checks (prevent members from editing others' items)
- [ ] Write tests verifying IDOR protection and unauthorized access rejection

---

## Phase 9: Dynamic Aggregation Engine

- [ ] Design dynamic aggregation query grouped by `(name, variant, unit)`
- [ ] Calculate total consolidated quantities across all members
- [ ] Build breakdown of contributing members per aggregated item
- [ ] Ensure case-insensitive grouping (e.g., "notebook" vs "Notebook")
- [ ] Write unit tests for aggregation math and grouping edge cases

---

## Phase 10: Manager APIs & Financial Calculations

- [ ] Implement `GET /api/v1/manager/requests` (all requests by member)
- [ ] Implement `GET /api/v1/manager/combined` (aggregated items with totals)
- [ ] Implement `PATCH /api/v1/manager/requests/{id}/price` (set unit price)
- [ ] Implement `PATCH /api/v1/manager/items/batch-price` (set price across all matching items)
- [ ] Implement `PATCH /api/v1/manager/requests/{id}/status` (update item status)
- [ ] Calculate line totals and grand totals purely in backend
- [ ] Enforce manager-only route protection via RBAC

---

## Phase 11: React Frontend (Member Experience)

- [ ] Setup React + Vite frontend with modern aesthetic design system
- [ ] Build Authentication views (`/login`, `/register`) with token storage
- [ ] Build Member Dashboard (`/member`):
  - [ ] Natural language chat input bar (with example prompts)
  - [ ] Real-time item extraction feedback card
  - [ ] Personal request table/cards with edit and delete actions
  - [ ] Status indicators (Pending, Approved, Purchased, Rejected)

---

## Phase 12: React Frontend (Manager Experience)

- [ ] Build Manager Dashboard (`/manager`):
  - [ ] Tab 1: Member-by-member breakdown
  - [ ] Tab 2: Combined purchasing requirements table
  - [ ] Inline price editing inputs
  - [ ] Financial metrics bar (Grand total, total items, active members)
  - [ ] Status toggles and exportable purchase checklist

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
