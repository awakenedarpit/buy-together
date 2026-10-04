# Technical Requirements Document (TRD)

## Project Name: Buy Together
**Status**: Approved  
**Version**: 1.0.0  

---

## 1. System Overview & Technology Stack

The **Buy Together** application is architected as a modular monolith with clear domain boundaries between presentation, application services, domain models, persistence, and external AI providers.

```
┌─────────────────────────────────────────────────────────────┐
│                 React + Vite Web Frontend                   │
│   (Modular Component UI, Responsive Design, State Store)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / REST / JSON Polling (3-5s)
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend Core                     │
│  ├── CORS & Security Middleware                             │
│  ├── Authentication / RBAC (PyJWT, bcrypt, OAuth2Bearer)    │
│  ├── API Routers (/auth, /messages, /requests, /manager)    │
│  ├── Application Service Layer (Business Logic & Ownership) │
│  ├── Pydantic V2 Domain Validation Engine                   │
│  └── AI Provider Abstraction Interface                     │
│         ├── LocalGemmaProvider (Transformers / PyTorch)     │
│         ├── HostedInferenceProvider (HuggingFace / Remote)  │
│         └── MockAIProvider (Deterministic Unit Tests)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy 2.0 ORM
┌──────────────────────────────▼──────────────────────────────┐
│             PostgreSQL Database (Target/Production)         │
│          (SQLite with in-memory mode for rapid tests)       │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 Technology Stack Details

| Layer | Component | Version / Tool | Rationale |
| :--- | :--- | :--- | :--- |
| **Frontend** | Framework | React 18+ | Component-driven UI, fast ecosystem. |
| | Tooling | Vite 6+ | Rapid HMR, minimal bundling overhead. |
| | Styling | Vanilla CSS / CSS Modules | Flexible, lightweight, zero runtime framework debt. |
| **Backend** | Runtime | Python 3.12+ / 3.14 | Modern typing, high performance, AI integration. |
| | Framework | FastAPI 0.115+ | Asynchronous, auto-generates OpenAPI docs, fast. |
| | Server | Uvicorn | High-performance ASGI web server. |
| | Validation | Pydantic V2 | High-throughput data parsing and schema validation. |
| | ORM | SQLAlchemy 2.0+ | Modern type-safe SQL toolkit and session manager. |
| | Migrations | Alembic | Version-controlled schema evolutions. |
| | Auth | PyJWT + bcrypt | Stateless authentication and secure password hashing. |
| **AI Layer** | Primary Model | Gemma 4 12B | State-of-the-art multilingual & Hinglish reasoning. |
| | Abstraction | Custom `BaseAIProvider` | Completely decouples inference from business logic. |
| | Local Engine | Transformers + PyTorch | Direct local execution for demo/workstations. |
| | Hosted Engine | HuggingFace Inference API | Serverless GPU execution for cloud deployment. |
| | Testing Engine| `MockAIProvider` | Zero-dependency, deterministic test fixtures. |
| **Database** | Production | PostgreSQL 15+ | ACID-compliant relational engine with JSONB and indexing. |
| | Testing | SQLite | Zero-configuration local automated unit test runner. |

---

## 2. API Architecture & Standards

- **Protocol**: HTTP/1.1 over TLS (HTTPS in production).
- **Format**: JSON (`Content-Type: application/json`).
- **Status Codes**: Strict adherence to RFC 9110 HTTP semantics:
  - `200 OK`: Successful read/update.
  - `201 Created`: Resource successfully created.
  - `204 No Content`: Successful deletion.
  - `400 Bad Request`: Validation failure or malformed payload.
  - `401 Unauthorized`: Missing or invalid JWT token.
  - `403 Forbidden`: Authenticated user lacks permission / does not own the resource.
  - `404 Not Found`: Target resource does not exist.
  - `422 Unprocessable Entity`: Pydantic validation failure.
  - `500 Internal Server Error`: Unexpected server exception.
- **Documentation**: Automatically served at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## 3. Authentication & Authorization (RBAC)

### 3.1 Authentication Workflow
1. User provides credentials to `POST /api/v1/auth/login`.
2. Password checked against stored hash using `bcrypt.checkpw()`.
3. If valid, server generates a signed JWT access token containing:
   ```json
   {
     "sub": "user_id_string",
     "email": "user@example.com",
     "role": "MEMBER",
     "exp": 1740000000
   }
   ```
4. Client stores the token securely in memory/localStorage and passes it in the `Authorization: Bearer <token>` header for subsequent requests.

### 3.2 Authorization Enforcement
- Route-level access controlled via FastAPI dependency injection:
  - `get_current_active_user`: Enforces valid JWT token and active account.
  - `require_manager`: Enforces `user.role == UserRole.MANAGER`.
- Resource-level access controlled in Service layer:
  - Checks `request_item.user_id == current_user.id`.

---

## 4. AI Architecture & Pipeline

### 4.1 Zero-Trust Processing Pipeline
```
[User Message: "bhai 2 notebook aur ek blue pen"]
                       │
                       ▼
           [Step 1: Save Raw Message]
           (Persist to `messages` table)
                       │
                       ▼
         [Step 2: AI Provider Extraction]
         (Gemma 4 12B formats output as JSON)
                       │
                       ▼
       [Step 3: Pydantic Schema Validation]
       (Validate ExtractedItem (ItemExtraction) schema, types, >0 quantities)
                       │
                       ▼
       [Step 4: Business Rules Validation]
       (Deduplicate names, apply standard units, sanitize)
                       │
                       ▼
       [Step 5: Database Persistence]
       (Insert rows into `request_items` table)
```

### 4.2 AI Provider Interface Contract
```python
from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

class ExtractedItem(BaseModel):
    name: str
    variant: str | None = None
    quantity: int
    unit: str

class ExtractionResult(BaseModel):
    items: List[ExtractedItem]
    raw_response: str | None = None

class BaseAIProvider(ABC):
    @abstractmethod
    async def extract_items(self, text: str) -> ExtractionResult:
        """Extract structured purchase requirements from natural language text."""
        pass
```

---

## 5. Database Architecture

### 5.1 Tables & Entity Relationships
1. **`users`**:
   - `id` (UUID or Integer PK)
   - `name` (VARCHAR)
   - `email` (VARCHAR, UNIQUE, INDEXED)
   - `password_hash` (VARCHAR)
   - `role` (ENUM: `MEMBER`, `MANAGER`)
   - `created_at`, `updated_at` (TIMESTAMP)

2. **`messages`**:
   - `id` (UUID or Integer PK)
   - `user_id` (FK -> `users.id`, INDEXED)
   - `text` (TEXT)
   - `created_at` (TIMESTAMP)

3. **`request_items`**:
   - `id` (UUID or Integer PK)
   - `message_id` (FK -> `messages.id`, NULLABLE, INDEXED)
   - `user_id` (FK -> `users.id`, INDEXED)
   - `name` (VARCHAR, INDEXED)
   - `variant` (VARCHAR, NULLABLE)
   - `quantity` (INTEGER, CHECK > 0)
   - `unit` (VARCHAR, DEFAULT 'piece')
   - `unit_price` (NUMERIC(10, 2), NULLABLE, DEFAULT NULL)
   - `status` (ENUM: `PENDING`, `APPROVED`, `PURCHASED`, `REJECTED`)
   - `created_at`, `updated_at` (TIMESTAMP)

### 5.2 Dynamic Group Aggregation (No Redundant Table)
Combined requirements are calculated at query time to avoid cache invalidation bugs and desynchronization:
```sql
SELECT 
    LOWER(name) AS normalized_name,
    COALESCE(LOWER(variant), '') AS normalized_variant,
    LOWER(unit) AS normalized_unit,
    SUM(quantity) AS total_quantity,
    AVG(unit_price) AS unit_price,
    SUM(quantity * COALESCE(unit_price, 0)) AS total_cost,
    COUNT(DISTINCT user_id) AS requesting_member_count
FROM request_items
WHERE status != 'REJECTED'
GROUP BY LOWER(name), COALESCE(LOWER(variant), ''), LOWER(unit);
```

---

## 6. Frontend Architecture

- **State Management**: React state hooks (`useState`, `useEffect`, `useCallback`) and custom context (`AuthContext`) for user session and polling data.
- **Polling Strategy**: Resilient client-side polling every 3,000–5,000 ms. Automatically stops when browser tab loses visibility to conserve system resources.
- **Error Boundaries & Feedback**: Inline error toasts and form-level feedback for failed actions.

---

## 7. Error Handling & Structured Logging

- **Logging**: Python `logging` module configured with JSON/structured output format. All log entries include `timestamp`, `level`, `module`, and `event`.
- **Secret Scrubbing**: Passwords, auth tokens, and raw keys are strictly prohibited from logs.
- **Exception Interceptor**: Global exception handler catches unhandled errors and returns a generic `{ "detail": "An internal server error occurred." }` response without exposing stack traces.

---

## 8. Testing Strategy

1. **Unit Testing**:
   - Pydantic schema validation tests (valid/invalid quantities, empty strings, missing fields).
   - Dynamic aggregation calculation tests.
   - Auth password hashing and JWT encoding/decoding.
2. **Integration Testing**:
   - FastAPI `TestClient` invoking full route pipelines against a test SQLite/Postgres database.
   - End-to-end request submission using `MockAIProvider`.
   - Security tests verifying that a `MEMBER` cannot update prices or access other users' items.

---

## 9. Deployment Architecture

- **Target Architecture**:
  - Frontend: Deployed as static SPA to Vercel, Cloudflare Pages, or Netlify.
  - Backend: Dockerized FastAPI application running on Render, Railway, or Fly.io.
  - Database: Managed PostgreSQL instance on Supabase, Neon, or Railway.
  - AI Engine: Hosted Inference API (e.g. HuggingFace) in production; Local Gemma or Mock provider in local development.
