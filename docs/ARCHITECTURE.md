# Architecture Specification

## Project: Buy Together
**Status**: Active Architecture Guide  
**Version**: 1.0.0  

---

## 1. High-Level Architectural Diagram

```mermaid
graph TD
    subgraph Presentation Layer
        UI[React + Vite Single Page Application]
        MemberDash[Member Dashboard: Chat & Personal Requests]
        ManagerDash[Manager Dashboard: Breakdown & Combined Purchasing]
        UI --> MemberDash
        UI --> ManagerDash
    end

    subgraph API & Gateway Layer
        HTTP[FastAPI REST API Server]
        CORS[CORS & Security Middleware]
        AuthMW[JWT Auth & RBAC Dependencies]
        HTTP --> CORS
        HTTP --> AuthMW
    end

    subgraph Application Service Layer
        AuthService[Auth Service: Register, Login, Token Generation]
        MsgService[Message Ingestion & Extraction Coordinator]
        ReqService[Request Item Service: Member CRUD & Ownership]
        AggService[Aggregation & Pricing Financial Engine]
    end

    subgraph Domain & Validation Layer
        Schemas[Pydantic V2 Domain Schemas]
        BizRules[Business Validation & Sanitization Rules]
    end

    subgraph AI Integration Layer
        AIProviderFace[BaseAIProvider Abstract Interface]
        LocalGemma[LocalGemmaProvider: PyTorch / Transformers]
        HostedAI[HostedInferenceProvider: Remote API]
        MockAI[MockAIProvider: Deterministic Unit Tests]
        AIProviderFace --> LocalGemma
        AIProviderFace --> HostedAI
        AIProviderFace --> MockAI
    end

    subgraph Persistence Layer
        ORM[SQLAlchemy 2.0 ORM Engine]
        Postgres[(PostgreSQL Database)]
        SQLiteTest[(SQLite In-Memory Test DB)]
        ORM --> Postgres
        ORM --> SQLiteTest
    end

    UI -- HTTP/JSON (REST & Polling) --> HTTP
    AuthMW --> AuthService
    HTTP --> MsgService
    HTTP --> ReqService
    HTTP --> AggService

    MsgService --> Schemas
    MsgService --> BizRules
    MsgService --> AIProviderFace
    MsgService --> ORM

    ReqService --> Schemas
    ReqService --> BizRules
    ReqService --> ORM

    AggService --> ORM
    AuthService --> ORM
```

---

## 2. Layered Responsibilities & Boundaries

### 2.1 Presentation Layer (Frontend)
- **Role**: Render user interface, manage client-side state, capture user natural language inputs, and poll backend updates.
- **Boundaries**: Contains zero pricing logic, zero authorization bypasses, and zero database credentials. Totals displayed in UI are received directly from backend calculations or used purely for optimistic preview.

### 2.2 API & Gateway Layer
- **Role**: Route incoming HTTP requests, enforce CORS headers, validate bearer tokens, verify role permissions (`MEMBER` vs `MANAGER`), and serialize response payloads.
- **Boundaries**: Thin controllers; does not contain SQL queries or complex business algorithms.

### 2.3 Application Service Layer
- **Role**: Coordinate workflows across domain models, AI providers, and repositories.
  - `MessageService`: Saves the raw message, queries the AI provider, runs validation, and records extracted items in a transaction.
  - `RequestService`: Enforces resource ownership before updating or deleting items.
  - `AggregationService`: Performs grouping and financial math (e.g. `sum(quantity * unit_price)`).
- **Boundaries**: Independent of the web framework (FastAPI) and AI model vendor.

### 2.4 Domain & Validation Layer
- **Role**: Enforce data integrity invariants using Pydantic V2 schemas.
  - `ItemExtraction`: Ensures item names are non-empty, quantities are positive integers (`>= 1`), and units are standard strings.
  - `UserRole`: Restricts role assignment.
- **Boundaries**: Pure Python objects; zero external network dependencies.

### 2.5 AI Integration Layer
- **Role**: Encapsulate all linguistic extraction logic behind `BaseAIProvider`.
  - Prompts are kept in version-controlled templates (`prompts/v1_extract.txt`).
  - Swapping inference engines is controlled via `AI_PROVIDER` (`mock`, `local_gemma`, `hosted`) without changing a single line of business code.
- **Boundaries**: Zero database access. Output is treated as untrusted user input until validated.

### 2.6 Persistence Layer
- **Role**: Manage ACID transactions, relational foreign keys, cascade deletes, and dynamic SQL grouping via SQLAlchemy 2.0.
- **Boundaries**: Encapsulates all SQL dialect specifics.

---

## 3. Core Data Workflows

### 3.1 Member Message Submission & Extraction Workflow
```mermaid
sequenceDiagram
    autonumber
    actor Member
    participant Frontend
    participant FastAPI
    participant AuthMW
    participant MessageService
    participant AIProvider
    participant Pydantic
    participant Database

    Member->>Frontend: Types "bhai 2 notebook aur ek blue pen"
    Frontend->>FastAPI: POST /api/v1/messages/ (Bearer Token)
    FastAPI->>AuthMW: Validate JWT
    AuthMW-->>FastAPI: Current User (Member)
    FastAPI->>MessageService: ingest_message(user_id, text)
    MessageService->>Database: INSERT INTO messages (user_id, text)
    Database-->>MessageService: message_id
    MessageService->>AIProvider: extract_items(text)
    AIProvider-->>MessageService: Raw JSON Output
    MessageService->>Pydantic: Validate against ExtractionResult
    Pydantic-->>MessageService: Validated ExtractedItem list
    loop For each validated item
        MessageService->>Database: INSERT INTO request_items (user_id, message_id, name, variant, qty, unit, status)
    end
    Database-->>MessageService: Saved RequestItem list
    MessageService-->>FastAPI: Return Message + Extracted Items
    FastAPI-->>Frontend: 201 Created (JSON)
    Frontend-->>Member: Display Extracted Items & Success Confirmation
```

### 3.2 Dynamic Aggregation & Manager Pricing Workflow
```mermaid
sequenceDiagram
    autonumber
    actor Manager
    participant Frontend
    participant FastAPI
    participant AggregationService
    participant Database

    Manager->>Frontend: Opens "Combined Requirements" Tab
    Frontend->>FastAPI: GET /api/v1/manager/combined (Bearer Token)
    FastAPI->>AggregationService: get_combined_requirements()
    AggregationService->>Database: SELECT name, variant, unit, SUM(qty) GROUP BY name, variant, unit
    Database-->>AggregationService: Aggregated Rows
    AggregationService-->>FastAPI: Consolidated list + Grand Total
    FastAPI-->>Frontend: 200 OK (JSON)
    Frontend-->>Manager: Render Combined Purchasing List
    Manager->>Frontend: Enters Unit Price ₹40 for Notebook
    Frontend->>FastAPI: PATCH /api/v1/manager/items/batch-price (name, variant, unit, price=40)
    FastAPI->>AggregationService: update_batch_price(name, variant, unit, price)
    AggregationService->>Database: UPDATE request_items SET unit_price=40 WHERE name=...
    Database-->>AggregationService: Updated records
    AggregationService-->>FastAPI: Success confirmation & recalculated total
    FastAPI-->>Frontend: 200 OK
    Frontend-->>Manager: Update UI with new Totals
```

---

## 4. Architectural Invariants & Anti-Patterns Forbidden

1. **NO AI Direct Database Operations**: The AI provider must never execute SQL, open database connections, or modify records directly.
2. **NO Redundant Aggregate Tables**: The system must NOT maintain a permanent `combined_requirements` table in MVP. Dynamic aggregation prevents data drift when requests are edited or deleted.
3. **NO Monolithic Single File Code**: Code must be separated into explicit packages (`api/`, `core/`, `models/`, `schemas/`, `services/`, `providers/`).
4. **NO Client-Determined Authorization**: The client never passes user IDs for authentication; user identity is derived strictly from the verified JWT payload.
5. **NO Trust in Client Totals**: Financial calculations must execute server-side; the server will never accept total amounts sent from the frontend.
