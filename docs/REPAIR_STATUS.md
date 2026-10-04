# Master Repository Repair Ledger

This document tracks all defects, inconsistencies, type safety gaps, and runtime discrepancies discovered during the comprehensive repository audit.

---

## Repair Summary

- **Total Problems Identified**: 15
  - **CRITICAL**: 0
  - **HIGH**: 3 (BUG-001, BUG-002, BUG-015)
  - **MEDIUM**: 9 (BUG-003, BUG-004, BUG-005, BUG-006, BUG-007, BUG-010, BUG-011, BUG-012, BUG-013)
  - **LOW**: 3 (BUG-008, BUG-009, BUG-014)
- **Fixed & Verified**: 15
- **Remaining / Unresolved**: 0
- **Blocked**: 0

---

## Detailed Bug Inventory

### BUG-001
- **Severity**: HIGH
- **File**: `docs/DEVELOPMENT.md`
- **Problem**: Running the documented migration command `alembic -c backend/alembic.ini upgrade head` fails with exit code 255 (`No 'script_location' key found in configuration`).
- **Root Cause**: `alembic.ini` is located at repository root (`/Users/user/PYDATA/alembic.ini`), not inside `backend/`.
- **Required Fix**: Update documentation to `alembic upgrade head`.
- **Status**: CLOSED
- **Verification**: `alembic upgrade head` executed cleanly with exit code 0 (`1ea134d4c373 (head)`).

---

### BUG-002
- **Severity**: HIGH
- **File**: `backend/app/models/message.py`
- **Problem**: SQLAlchemy relationship on `Message.request_items` specified `cascade="all, delete-orphan"`, conflicting with `RequestItem.message_id` definition (`ForeignKey("messages.id", ondelete="SET NULL")`, `nullable=True`).
- **Root Cause**: Database design dictates that user purchase request items are preserved even if raw chat messages are cleared. `cascade="all, delete-orphan"` would mistakenly delete user purchase requests when a chat message was removed.
- **Required Fix**: Removed `delete-orphan` cascade from `Message.request_items`.
- **Status**: CLOSED
- **Verification**: Verified via newly added unit test `test_message_deletion_preserves_request_items` in `backend/tests/test_database.py`. Deleting a message preserves the request item.

---

### BUG-003
- **Severity**: MEDIUM
- **File**: `backend/app/schemas/__init__.py`
- **Problem**: Schemas for AI extraction and messages (`ExtractedItem`, `ExtractionResult`, `MessageCreate`, `MessageOut`, `RequestItemOut`, `MessageResponse`) were not re-exported.
- **Root Cause**: Incomplete `__all__` list in package `__init__.py`.
- **Required Fix**: Exported all extraction and message schemas in `backend/app/schemas/__init__.py`.
- **Status**: CLOSED
- **Verification**: `from backend.app.schemas import MessageCreate, ExtractedItem, ItemExtraction` verified successfully.

---

### BUG-004
- **Severity**: MEDIUM
- **File**: `backend/app/ai/`, `backend/app/services/`
- **Problem**: Missing `__init__.py` files in `backend/app/ai/` and `backend/app/services/`.
- **Root Cause**: Folders were created without Python package marker files.
- **Required Fix**: Added `__init__.py` to `backend/app/ai/` and `backend/app/services/` with explicit `__all__` exports.
- **Status**: CLOSED
- **Verification**: `python -c "import backend.app.ai, backend.app.services"` verified without error.

---

### BUG-005
- **Severity**: MEDIUM
- **File**: `backend/app/schemas/ai.py`, `docs/TRD.md`, `docs/ARCHITECTURE.md`
- **Problem**: Discrepancy in item schema naming: `ExtractedItem` in code vs `ItemExtraction` in architecture docs.
- **Root Cause**: Naming divergence during Phase 0 documentation vs Phase 3 implementation.
- **Required Fix**: Exported `ItemExtraction = ExtractedItem` alias in `backend/app/schemas/ai.py` and synced documentation references.
- **Status**: CLOSED
- **Verification**: Verified importing both `ItemExtraction` and `ExtractedItem` successfully.

---

### BUG-006
- **Severity**: MEDIUM
- **File**: `backend/app/ai/hosted_gemma_provider.py`, `README.md`, `ADR-002`
- **Problem**: Provider class naming divergence: `HostedGemmaProvider` in code vs `HostedInferenceProvider` in `README.md` and `ADR-002`.
- **Root Cause**: Naming divergence during provider design.
- **Required Fix**: Added `HostedInferenceProvider = HostedGemmaProvider` alias in `backend/app/ai/hosted_gemma_provider.py`.
- **Status**: CLOSED
- **Verification**: Verified `from backend.app.ai import HostedInferenceProvider` works cleanly.

---

### BUG-007
- **Severity**: MEDIUM
- **File**: `frontend/src/App.jsx`, `frontend/`
- **Problem**: Backend API URL was hardcoded as `'http://localhost:8000/api/v1/health'`, breaking deployment flexibility and missing environment variable fallback.
- **Root Cause**: Scaffolded with static URL without `import.meta.env.VITE_API_URL`.
- **Required Fix**: Updated `App.jsx` to use `import.meta.env.VITE_API_URL || 'http://localhost:8000'` and created `frontend/.env.example`.
- **Status**: CLOSED
- **Verification**: `npm run build` and `npm run lint` succeeded cleanly in `frontend/`.

---

### BUG-008
- **Severity**: LOW
- **File**: `frontend/src/App.css`
- **Problem**: Contained 185 lines of dead Vite starter CSS that was never imported or used.
- **Root Cause**: Leftover boilerplate from `npm create vite`.
- **Required Fix**: Cleaned `App.css` to remove unused boilerplate styles.
- **Status**: CLOSED
- **Verification**: `npm run build` executed cleanly in 122ms.

---

### BUG-009
- **Severity**: LOW
- **File**: `README.md`
- **Problem**: Project status section in `README.md` listed Backend, Frontend, AI Engine, and Database as "PLANNED (Phase 0)", which was stale.
- **Root Cause**: `README.md` was authored during Phase 0 and not updated after Phase 1–3 completion.
- **Required Fix**: Updated `README.md` status badges and descriptions to reflect verified Phase 1–3 deliverables.
- **Status**: CLOSED
- **Verification**: Verified accurate status descriptions in `README.md`.

---

### BUG-010
- **Severity**: MEDIUM
- **File**: `backend/app/api/deps.py`
- **Problem**: `require_role` performed direct comparison `current_user.role != required_role`.
- **Root Cause**: Depending on SQLAlchemy driver or SQLite storage, `current_user.role` could be evaluated as an enum instance or string value.
- **Required Fix**: Normalized comparison using `.value if hasattr(x, "value") else str(x)`.
- **Status**: CLOSED
- **Verification**: `test_role_based_access_control` passed in test suite.

---

### BUG-011
- **Severity**: MEDIUM
- **File**: `backend/app/api/v1/auth.py`
- **Problem**: `register_user` and `read_current_user` returned ORM `User` instances directly while type hints specified `-> UserOut:`.
- **Root Cause**: Relying implicitly on FastAPI response_model conversion rather than explicit typing.
- **Required Fix**: Explicitly return `UserOut.model_validate(user)` and `UserOut.model_validate(current_user)`.
- **Status**: CLOSED
- **Verification**: Verified typing and API response contracts.

---

### BUG-012
- **Severity**: MEDIUM
- **File**: `backend/app/services/extraction_service.py`
- **Problem**: `ExtractionService.provider` property cached `self._provider` on first call, preventing dynamic provider updates or test resets.
- **Root Cause**: Over-aggressive caching on instance attribute without distinguishing explicit override from default factory lookup.
- **Required Fix**: Track `self._explicit_provider`. If None, always fetch current provider from `get_ai_provider()`.
- **Status**: CLOSED
- **Verification**: Verified provider reset in tests takes effect immediately.

---

### BUG-013
- **Severity**: MEDIUM
- **File**: `backend/tests/conftest.py`
- **Problem**: `member_token` and `manager_token` fixtures called `db_session.commit()`, which persisted to SQLite in-memory table and risked cross-test leakage.
- **Root Cause**: Committing fixture seed data persists to SQLite in-memory table.
- **Required Fix**: Added post-test table truncation in `db_session` fixture and reuse-or-create logic in token fixtures.
- **Status**: CLOSED
- **Verification**: All 32 tests passed cleanly and independently.

---

### BUG-014
- **Severity**: LOW
- **File**: `pytest.ini`
- **Problem**: Starlette deprecation warning during test runs: `StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead`.
- **Root Cause**: Deprecation notice emitted by Starlette TestClient wrapper.
- **Required Fix**: Added filterwarnings in `pytest.ini` to cleanly filter this third-party deprecation warning.
- **Status**: CLOSED
- **Verification**: `pytest` runs 32 tests with 0 warnings.

---

### BUG-015
- **Severity**: HIGH
- **File**: `pyrightconfig.json`, `.vscode/settings.json`
- **Problem**: IDE diagnostics reported `Cannot find module 'fastapi'`, `Cannot find module 'sqlalchemy'`, `Cannot find module 'pytest'` across multiple backend files.
- **Root Cause**: The IDE's language server / Pyright was querying the global system Python (`/Library/Frameworks/Python.framework/Versions/3.14/lib/python3.14/site-packages`) instead of the project's local virtual environment (`.venv`).
- **Required Fix**: Created `pyrightconfig.json` with `"venvPath": "."`, `"venv": ".venv"`, `"extraPaths": ["."]`, and created `.vscode/settings.json` configuring `python.defaultInterpreterPath`.
- **Status**: CLOSED
- **Verification**: Verified that `.venv` packages (`fastapi`, `sqlalchemy`, `pytest`, `pydantic`, `pyjwt`, `bcrypt`) resolve correctly via project interpreter configuration.

