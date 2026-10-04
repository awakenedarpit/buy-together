# AGENTS.md — AI Agent Operating Manual for "Buy Together"

Welcome, AI Agent. This document is your foundational operating manual for contributing to **Buy Together**. Read this file before performing any code generation, refactoring, or architectural modifications.

---

## 1. Project Overview

**Buy Together** is an AI-powered group purchasing and request aggregation application.
It allows community members (e.g., college dorms, office teams, neighborhood groups) to naturally express what items they need in chat (including Hinglish and natural language such as *"bhai 2 notebook aur ek blue pen"*).

The system uses **Gemma 4 12B** (or an interchangeable inference provider) to extract structured purchase items, validates every extracted item through strict **Pydantic schemas and business validation rules**, persists the requests in **PostgreSQL**, and provides:
1. **Members** with self-service views to track, edit, or delete their own pending requests.
2. **Project Managers** with aggregate views to inspect all member demands, view dynamically grouped and summed requirements, assign unit prices, compute financial totals, and export consolidated purchasing lists.

---

## 2. Core Architecture

The system is organized as a clean, decoupled modular monolith:

```
[React + Vite Frontend]
         │ (HTTP REST / Polling)
         ▼
[FastAPI Application Layer]
   ├── [Auth & RBAC Middleware] (PyJWT + bcrypt)
   ├── [Application Services]   (Business Logic & Ownership)
   ├── [AI Provider Abstraction] (BaseAIProvider Interface)
   │        ├── LocalGemmaProvider (Transformers / PyTorch)
   │        ├── HostedInferenceProvider (HuggingFace / Remote API)
   │        └── MockAIProvider (Deterministic Unit Tests)
   ├── [Pydantic Validation Layer] (Strict Data Contracts)
   └── [SQLAlchemy Persistence]
            │
            ▼
    [PostgreSQL Database]
```

### Critical Separation of Concerns
- **AI Layer Responsibility**: Linguistic extraction, normalization suggestions, unit parsing, and structured JSON output.
- **Python Backend Responsibility**: Authentication, role authorization, business constraint validation, unit price calculations, database persistence, and dynamic aggregation.

---

## 3. Mandatory Coding Rules

1. **Modular Code Structure**:
   - Never put everything into one or two giant files.
   - Separate routers, services, repositories, schemas, models, and AI providers into dedicated modules.
2. **Type Safety & Type Annotations**:
   - Use Python type hints (`typing`, Pydantic models) across all backend services and functions.
   - Use TypeScript or strict PropTypes in frontend components where applicable.
3. **Naming & Small Functions**:
   - Use descriptive, intention-revealing variable and function names.
   - Keep functions focused on a single responsibility; functions exceeding 50 lines should be inspected for extraction.
4. **Zero Hardcoded Secrets**:
   - Never hardcode secrets, passwords, JWT keys, or API tokens.
   - All secrets must be loaded via environment variables / configuration classes.
5. **No Duplicate Business Logic**:
   - Centralize calculation and validation logic in backend service modules, never duplicated in frontend or database triggers.

---

## 4. AI Interaction Rules (Zero Trust)

1. **Never Trust AI Output**:
   - All AI output must be treated as untrusted user input.
   - Run AI JSON through Pydantic validators (`RequestItemCreateList`) and Python business sanity checks.
2. **Strict Flow Enforcement**:
   ```
   User Input ──► Raw Message Saved ──► AI Extraction ──► Pydantic Validation ──► Business Validation ──► Database
   ```
   *NEVER:* `User Input ──► AI ──► Database` directly.
3. **No Direct Database Access for AI**:
   - The AI model or prompt has zero direct access to the database or SQL queries.
4. **AI Never Determines Permissions or Roles**:
   - Authorization is strictly enforced by FastAPI dependency injection (`get_current_user`, `require_role`).
5. **Preserve Raw User Input**:
   - Always persist the original user message text in the `messages` table before or alongside extracted items.

---

## 5. Database & Migration Rules

1. **Use Migrations**:
   - Always use Alembic for database schema changes. Do not execute manual ad-hoc DDL in production.
2. **Preserve Referential Integrity**:
   - Enforce foreign keys between `users`, `messages`, and `request_items` with appropriate cascade behaviors.
3. **Appropriate Indexing**:
   - Index lookup fields: `user_id`, `message_id`, `status`, and compound indexes for dynamic aggregation (`(name, variant, unit)`).
4. **Dynamic Aggregation over Persistent Redundant Tables**:
   - For MVP, do **not** create a permanent `combined_requirements` table. Aggregate dynamically using SQL `GROUP BY` or dedicated service queries to prevent synchronization anomalies.

---

## 6. Security Rules

1. **Password Hashing**: Always hash passwords with bcrypt with appropriate salt rounds. Never store plaintext.
2. **JWT Authentication**: Issue signed JWT tokens with standard claims (`sub`, `role`, `exp`). Validate tokens on every protected route.
3. **Role-Based Access Control (RBAC)**:
   - `MEMBER`: Allowed to submit messages, read/update/delete their own requests.
   - `MANAGER`: Allowed to inspect all requests, update unit prices, update status, and view combined totals.
4. **Ownership Verification (Prevent IDOR)**:
   - When a member attempts to edit or delete a request item, verify `item.user_id == current_user.id`. Return `403 Forbidden` or `404 Not Found` if ownership does not match.
5. **Safe Error Handling**:
   - Never leak internal stack traces, DB connection strings, or system paths to clients.

---

## 7. Testing Rules

1. **Comprehensive Coverage**:
   - Every major feature must have automated tests in `backend/tests/`.
   - Core test suites: Auth, Authorization/RBAC, AI Output Validation, Request Item CRUD & Ownership, Dynamic Aggregation, and Manager Pricing.
2. **Deterministic AI Testing**:
   - Never require downloading or running a 12B model inside CI or routine unit tests.
   - Use `MockAIProvider` with predefined fixtures for fast, deterministic unit test execution.
   - Separate live model tests into integration suites (`tests/integration/test_live_gemma.py`).

---

## 8. Documentation & Memory Maintenance Rules

After **every** meaningful development step or session:
1. Update [MEMORY.md](file:///Users/user/PYDATA/MEMORY.md) with exact current status, completed work, and next actions.
2. Update [TASKS.md](file:///Users/user/PYDATA/TASKS.md) to reflect completed items and active progress.
3. Update [CHANGELOG.md](file:///Users/user/PYDATA/CHANGELOG.md) under the appropriate category (`Added`, `Changed`, `Fixed`, `Security`, `Documentation`).
4. Record major architectural shifts as new Architecture Decision Records in `docs/decisions/`.
5. Update technical documentation if interfaces, schemas, or deployment instructions changed.

---

## 9. Handoff Protocol for Next AI Agents

If you are a new AI model taking over this session:
1. First, read [AGENTS.md](file:///Users/user/PYDATA/AGENTS.md) (this file).
2. Second, read [MEMORY.md](file:///Users/user/PYDATA/MEMORY.md) to see where the project currently stands.
3. Third, read [TASKS.md](file:///Users/user/PYDATA/TASKS.md) to identify the immediate next task.
4. Fourth, inspect `git status` and recent commits to verify the disk state matches `MEMORY.md`.
5. Do not re-implement completed tasks. Continue directly with the next uncompleted task.
