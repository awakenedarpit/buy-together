# Testing Strategy & Quality Assurance Plan

## Project: Buy Together
**Testing Framework**: `pytest` (Backend) & Component Tests (Frontend)  
**Execution Environment**: Local Developer Workstations & CI/CD Pipelines  

---

## 1. Testing Philosophy

1. **Fast, Deterministic Feedback**: CI unit and integration suites must complete in seconds, not minutes.
2. **Decoupled AI Testing**: Routine test runs must **never** download or execute the 12B parameter model weights. The `MockAIProvider` provides deterministic, repeatable linguistic fixtures.
3. **Dedicated Integration Suite**: A separate optional test suite (`pytest -m live_model`) runs against the real Gemma engine when hardware is available.

---

## 2. Test Pyramid & Scope

```
           / \
          /   \
         / E2E \       Playwright / Browser Verification
        /-------\
       / Integr. \     FastAPI TestClient + In-Memory SQLite DB
      /-----------\
     /    Unit     \   Pydantic Validators, Business Rules, Price Aggregations
    /---------------\
```

### 2.1 Backend Test Modules (`backend/tests/`)
- `test_auth.py`:
  - Password hashing and verification.
  - User registration (valid data, duplicate email, weak password).
  - User login (valid credentials, invalid password, nonexistent user).
  - JWT token generation, parsing, and expiration handling.
- `test_ai_validation.py`:
  - Pydantic schema validation for `ExtractedItem` and `ExtractionResult`.
  - Handling missing keys, invalid types, zero or negative quantities.
  - Recovery from malformed JSON strings.
- `test_requests.py`:
  - Member message submission (`POST /api/v1/messages/`).
  - Request creation, listing, updating, and deleting.
  - Strict ownership enforcement (IDOR rejection: User A cannot edit User B's item).
- `test_aggregation.py`:
  - Dynamic grouping logic (`name + variant + unit`).
  - Case-insensitivity verification ("Notebook" vs "notebook").
  - Summation of quantities and pricing calculations.
- `test_manager.py`:
  - Manager route protection (rejecting non-manager users with 403 Forbidden).
  - Unit price assignment and batch price updates.
  - Total calculation correctness (`line_total` and `grand_total`).
  - Status updates (`PENDING` -> `APPROVED` -> `PURCHASED`).

---

## 3. Test Fixtures (`conftest.py`)

Key shared fixtures:
- `db_session`: In-memory SQLite session with table creation and teardown.
- `client`: `TestClient(app)` configured with overridden dependencies.
- `member_user`: Standard user with role `MEMBER`.
- `manager_user`: Privileged user with role `MANAGER`.
- `member_token` & `manager_token`: Pre-generated valid JWT bearer tokens.
- `mock_ai_provider`: Injected `MockAIProvider` with predefined Hinglish test responses.

---

## 4. Running Tests

```bash
# Run all standard unit and integration tests (fast, no GPU required)
pytest -v

# Run with test coverage report
pytest --cov=backend/app --cov-report=term-missing

# Run only authentication tests
pytest backend/tests/test_auth.py -v

# Run optional live Gemma model integration tests (requires local GPU or API token)
pytest backend/tests/test_live_gemma.py -v -m live_model
```
