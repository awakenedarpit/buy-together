# Product Requirements Document (PRD)

## Project Name: Buy Together
**Status**: Approved (MVP Specification)  
**Version**: 1.0.0  
**Target Release**: MVP  

---

## 1. Executive Summary & Problem Statement

### 1.1 Problem Statement
In communities, university dorms, shared apartments, office departments, and collaborative groups, purchasing common supplies (groceries, stationery, hardware, electronics) is unorganized, error-prone, and tedious. Individuals frequently send unstructured chat messages in messaging apps (e.g., WhatsApp, Slack) using mixed language or Hinglish:
> *"bhai 2 notebook aur ek blue pen mangwa dena"*  
> *"mere liye 1 packet A4 paper and 3 gel pens"*

Organizers or project managers must manually read through disjointed chat threads, write down each person's requested items in spreadsheets, deduplicate and combine items to achieve bulk discounts, assign prices, calculate individual and overall expenses, and coordinate purchasing. This leads to missed orders, incorrect quantities, redundant shipping costs, and friction between group members.

### 1.2 Proposed Solution
**Buy Together** is an AI-powered group purchasing and request aggregation application. Members can type or paste natural-language or Hinglish requests into a single interface. An underlying AI model (Gemma 4 12B) parses and structures the request into discrete items with quantities, units, and variants. A strict backend validation pipeline ensures data integrity before saving. The Project Manager has an executive dashboard with dynamic group aggregation, unit pricing tools, and financial totals, eliminating manual spreadsheet consolidation.

---

## 2. Target Users & User Personas

### 2.1 Personas

#### Persona 1: Aryan (The Community Member)
- **Role**: College student / team member.
- **Context**: Needs stationery or shared groceries every week. Doesn't want to fill out complex 10-field forms.
- **Goal**: Quickly type what he wants in natural conversational language (*"2 spiral notebooks and 1 cello butterflow blue"*), review what was extracted, and track whether it's approved and purchased.
- **Pain Point**: Forgetting to message the group manager, items being missed, or having no visibility into their personal order history.

#### Persona 2: Sneha (The Project / Community Manager)
- **Role**: Dorm representative / office procurement lead.
- **Context**: In charge of placing the bulk order from wholesale vendors or online stores.
- **Goal**: See a unified list of who requested what, view a combined purchasing list (e.g., total 15 notebooks across 6 members), input wholesale unit prices, view total calculated costs, and mark items as purchased.
- **Pain Point**: Manually maintaining spreadsheets, dealing with ambiguous chat requests, and error-prone price calculations.

---

## 3. User Roles & Permissions Matrix

| Feature / Action | Member Role | Project Manager Role |
| :--- | :---: | :---: |
| Self-registration & Authentication | Yes | Yes |
| Submit Natural Language Chat Messages | Yes | Yes |
| View Own Extracted Request Items | Yes | Yes |
| Edit / Delete Own Request Items | Yes | Yes |
| View Other Members' Individual Requests | **No (Forbidden)** | **Yes** |
| Edit Other Members' Request Items | **No (Forbidden)** | **Yes** (Manager override) |
| View Dynamic Combined Requirements Table | No | **Yes** |
| Enter & Modify Unit Prices | **No (Forbidden)** | **Yes** |
| Update Item Status (Pending, Approved, Purchased, Rejected) | **No (Forbidden)** | **Yes** |
| View Total Financial Expenditures & Grand Totals | No | **Yes** |

---

## 4. User Stories

### Member Stories
- **US-M1**: As a Member, I want to sign up and log in securely so that my requests are tied to my identity.
- **US-M2**: As a Member, I want to type natural-language or Hinglish text describing what I need, so I don't have to fill out repetitive form fields.
- **US-M3**: As a Member, I want to see the structured items extracted by the AI immediately, so I can verify that my intent was parsed accurately.
- **US-M4**: As a Member, I want to view only my own past and pending requests, so my list remains clutter-free and private from other members.
- **US-M5**: As a Member, I want to edit or delete any pending request I submitted, in case my plans change or the AI extracted a wrong quantity.

### Manager Stories
- **US-PM1**: As a Project Manager, I want to view a member-by-member breakdown of requests, so I know who asked for what.
- **US-PM2**: As a Project Manager, I want a combined requirements view that automatically sums up quantities for identical items (matching name, variant, and unit), so I know the bulk quantity to purchase.
- **US-PM3**: As a Project Manager, I want to enter or update the unit price for an item, so the application calculates total line costs and the grand bulk order total automatically.
- **US-PM4**: As a Project Manager, I want to update the status of items (Pending -> Approved -> Purchased or Rejected), so members are informed of the procurement progress.

---

## 5. Functional Requirements

### 5.1 Authentication & Authorization
- **FR-AUTH-1**: User registration with Name, Email, Password, and Role (`MEMBER` default, `MANAGER` configurable).
- **FR-AUTH-2**: Password hashing using bcrypt. Plaintext passwords must never be stored or logged.
- **FR-AUTH-3**: Stateless JWT authentication with token expiration.
- **FR-AUTH-4**: Role-Based Access Control (RBAC) enforced via FastAPI route dependencies.

### 5.2 Natural Language Ingestion & AI Extraction
- **FR-AI-1**: The system must accept freeform text in English, Hindi, or Hinglish (e.g., *"bhai 2 notebook aur ek blue pen"*).
- **FR-AI-2**: The original raw message must be stored in the `messages` table before AI processing.
- **FR-AI-3**: Gemma 4 12B (or configured AI provider) must extract items conforming strictly to the JSON schema:
  ```json
  {
    "items": [
      {
        "name": "string",
        "variant": "string | null",
        "quantity": "integer (>= 1)",
        "unit": "string"
      }
    ]
  }
  ```
- **FR-AI-4**: The backend must validate the AI output through Pydantic. If validation fails or JSON is malformed, safe fallback handling must be triggered without crashing the service.
- **FR-AI-5**: Extracted and validated items are saved to the `request_items` table linked to the user and original message.

### 5.3 Member Request Management
- **FR-REQ-1**: Members can query `GET /api/v1/requests/my` to list their own requests.
- **FR-REQ-2**: Members can update (`PUT`) or delete (`DELETE`) their own requests.
- **FR-REQ-3**: The system must enforce ownership checks; returning `403 Forbidden` if a member attempts to touch another member's item.

### 5.4 Dynamic Aggregation & Manager Purchasing View
- **FR-AGG-1**: The manager view must dynamically group all active requests by `(normalized_name, normalized_variant, normalized_unit)`.
- **FR-AGG-2**: The aggregate must sum quantities and list the contributing members.
- **FR-AGG-3**: The manager can assign a `unit_price` to individual items or batch-assign a unit price across all matching items.
- **FR-AGG-4**: The system must calculate:
  - `item_total = quantity * unit_price`
  - `grand_total = sum(all line item totals)`
- **FR-AGG-5**: The manager can transition item statuses: `PENDING` -> `APPROVED` -> `PURCHASED` (or `REJECTED`).

---

## 6. Non-Functional Requirements (NFRs)

- **NFR-PERF-1**: Extraction API response time under 1.5 seconds when using hosted inference or mock provider.
- **NFR-SEC-1**: OWASP Top 10 compliance: zero SQL injection (via SQLAlchemy ORM parameterized queries), XSS sanitization, and strict IDOR prevention.
- **NFR-REL-1**: Graceful degradation: If the AI model is temporarily unreachable, the user is alerted with an informative error while their original message remains safely saved.
- **NFR-MOD-1**: Decoupled AI provider interface allowing hot-swapping between `mock`, `local_gemma`, and `hosted` inference via a single environment variable change (`AI_PROVIDER`).
- **NFR-TEST-1**: Automated test suite achieving high unit and API test coverage for auth, CRUD, ownership, aggregation, and financial calculations.

---

## 7. User Flows

### 7.1 Member Submission Flow
```
Member Logs In
  └─► Navigates to Member Chat Dashboard
        └─► Types: "bhai 2 notebook aur ek blue pen"
              └─► Submits to Backend
                    ├─► Message saved to `messages`
                    ├─► AI Provider extracts items
                    ├─► Pydantic validates items
                    ├─► Items saved to `request_items`
                    └─► Frontend receives items & refreshes list
```

### 7.2 Manager Procurement Flow
```
Manager Logs In
  └─► Navigates to Manager Dashboard
        ├─► Tab 1: Inspects per-member breakdown
        └─► Tab 2: Inspects Combined Purchasing List
              ├─► Sees: Notebook (qty: 6), Blue Pen (qty: 5), Black Pen (qty: 3)
              ├─► Enters Unit Price: Notebook = ₹40, Blue Pen = ₹10
              ├─► Backend calculates:
              │     Notebook Total: 6 * ₹40 = ₹240
              │     Blue Pen Total: 5 * ₹10 = ₹50
              │     Grand Total: ₹290
              └─► Manager updates status to 'APPROVED' or 'PURCHASED'
```

---

## 8. MVP Scope vs. Future Scope

### MVP Scope (Current)
- Member & Manager Authentication (JWT, bcrypt).
- Natural language / Hinglish message input.
- Gemma 4 12B extraction pipeline with Pydantic validation & MockAI provider.
- Relational schema in PostgreSQL (or SQLite test fallback).
- Member self-service request CRUD with strict ownership verification.
- Dynamic group aggregation (`GROUP BY name, variant, unit`).
- Manager pricing input and total financial calculations.
- Clean, modern responsive web UI with polling updates (3–5s).

### Future Scope (Post-MVP)
- Realtime WebSockets / SSE push updates.
- WhatsApp / Telegram bot integration for direct message ingestion.
- Receipt image OCR scanning for manager purchase verification.
- Automated payment split links (UPI / Stripe / Razorpay).
- Multi-group / multi-project tenancy.

---

## 9. Assumptions & Constraints

1. **AI Role Limitation**: Gemma 4 12B is strictly an extraction and normalization agent. It has zero authority over pricing, role authorization, or database transactions.
2. **Pricing Authority**: Unit prices are strictly provided or confirmed by the Project Manager.
3. **Hardware Constraints**: Running a 12B model locally requires substantial RAM/VRAM. For development and environments lacking high-end GPUs, the `MockAIProvider` or hosted inference endpoints are used.

---

## 10. Success Metrics
1. **Extraction Accuracy**: > 90% accurate extraction on standard Hinglish / conversational grocery and stationery requests.
2. **Data Consistency**: 0% data corruption or inventory leakage across members.
3. **Procurement Time Reduction**: > 75% reduction in manual effort required for group order consolidation compared to spreadsheets.
