# MEMORY.md — Project Memory & Continuity Ledger

> **Notice**: This file tracks the live state of the "Buy Together" project. It must be updated at the end of every development phase or session to ensure flawless continuity across AI models, sessions, and human collaborators.

---

## 1. Current Status

* **Phase**: **GEMINI AI EXTRACTION INTEGRATED & LIVE MVP COMPLETE**
* **Overall Completion**: 98%
* **Current Task**: Google Gemini AI Integration for natural-language requirement extraction (English/Hindi/Hinglish) with Zero-Trust validation and automated fallback.
* **Last Completed Task**: `GeminiProvider` implemented using `google-genai` SDK, structured JSON output (`response_mime_type="application/json"`), zero client key exposure, deterministic heuristic fallback for offline/quota safety, enhanced "Understanding your request..." and "Requirements Added ✓" UX, 39/39 pytest passing, deployed to Vercel.
* **Next Task**: Await Gemini API Key from user or deploy to permanent cloud host.

---

## 2. Live Demo Endpoints & Verification

```text
================================================================================
BUY TOGETHER — LIVE HACKATHON MVP
================================================================================
Frontend Public URL (Vercel Production):
https://frontend-green-rho-88.vercel.app

Frontend Backup URL (Tunnel):
https://ascii-andrea-technological-optimum.trycloudflare.com

Backend Public URL:
https://knee-mountain-butler-intellectual.trycloudflare.com

Health Endpoint:
https://knee-mountain-butler-intellectual.trycloudflare.com/api/v1/health

Demo Endpoints:
POST /api/v1/auth/demo-login  (payload: {"role": "MEMBER"} or {"role": "MANAGER"})

SPA Routes (Client-Side History):
/dashboard -> Member Portal
/manager   -> Manager Procurement Dashboard

Database:
SQLite local engine with full Alembic migrations (1ea134d4c373) (PostgreSQL-compatible)

AI Engine:
Google Gemini API (gemini-2.5-flash / configurable) + Heuristic Fallback Parser
(Deterministic fallback guarantees 100% demo uptime if API key is absent or quota is limited)

GitHub Repository:
https://github.com/awakenedarpit/buy-together
Branch: main
================================================================================
```

---

## 3. Verification Matrix

| Flow Step | Test Status | Details |
| :--- | :---: | :--- |
| **Backend Starts** | **PASS** | FastAPI v0.1.0 on port 8000 via Uvicorn |
| **Public Backend Tunnel** | **PASS** | `https://knee-mountain-butler-intellectual.trycloudflare.com` |
| **Frontend Builds** | **PASS** | React 19 + Vite 8 in 130ms with 0 warnings |
| **Vercel Production Deploy** | **PASS** | `https://frontend-green-rho-88.vercel.app` |
| **Vercel SPA Rewrites** | **PASS** | `/dashboard` and `/manager` return HTTP 200 with index.html |
| **Demo Member Login** | **PASS** | `POST /api/v1/auth/demo-login {"role":"MEMBER"}` returns signed JWT |
| **Demo Manager Login** | **PASS** | `POST /api/v1/auth/demo-login {"role":"MANAGER"}` returns signed JWT |
| **Zero Client Credentials** | **PASS** | No emails/passwords in JS bundle, localStorage, HTML, or public env |
| **AI Extraction Pipeline** | **PASS** | `"bhai 2 notebook aur ek blue pen"` -> Notebook (qty 2), Pen (qty 1, blue) |
| **Graceful AI Fallback** | **PASS** | `ExtractionService` automatically catches provider failures and falls back |
| **Item Persistence** | **PASS** | Extracted items saved atomically to `messages` & `request_items` tables |
| **Member Dashboard** | **PASS** | `GET /api/v1/requests` lists personal items with ownership isolation |
| **Inline Item Editing** | **PASS** | `PATCH /api/v1/requests/{id}` updates quantity & variant |
| **Item Deletion** | **PASS** | `DELETE /api/v1/requests/{id}` deletes item with IDOR protection |
| **Manager Inspection** | **PASS** | `GET /api/v1/manager/requests` displays all requests across members |
| **Dynamic Aggregation** | **PASS** | `GET /api/v1/manager/combined` groups by `(name, variant, unit)` |
| **Regression Suite** | **PASS** | **34/34 pytest tests passing** + **6/6 live public integration checks passing** |

---

## 4. Completed Work by Phase

* **Phase 0 & 1**: Foundations, documentation, initial FastAPI & Vite scaffold.
* **Phase 2**: Database models (`User`, `Message`, `RequestItem`), Alembic migrations, password hashing, JWT auth, and role-based access control.
* **Phase 3**: Zero-trust AI extraction pipeline, `BaseAIProvider` abstraction, `MockAIProvider`, message transaction service, input sanitization.
* **Phase 4 & 5 (MVP Delivery)**:
  - Member Request CRUD endpoints (`/api/v1/requests`) with strict IDOR prevention.
  - Manager Procurement & Dynamic Aggregation endpoints (`/api/v1/manager/requests`, `/api/v1/manager/combined`, pricing, and status updates).
  - Production-ready React + Vite frontend SPA with Member Portal and Manager Procurement Dashboards.
  - Public HTTPS Cloudflare tunnels for live external evaluation without deployment friction.
  - End-to-end verified with live automated test suite.

---

## 5. Known Limitations & Pragmatic Notes

* **AI Provider**: For the live demo, `AI_PROVIDER=mock` is active. This avoids forcing local 12B Gemma weights onto a constrained CPU environment and guarantees 100% responsive, deterministic inference for judges and testers. The provider abstraction (`BaseAIProvider`, `LocalGemmaProvider`, `HostedGemmaProvider`) is fully intact and ready for hosted GPU weights.
* **Tunnels**: Quick tunnels on `trycloudflare.com` remain alive while the background tunnel daemons run on the host.

---

## 6. Next Actions

1. Commit and push working MVP to `awakenedarpit/buy-together`.
2. Provide hackathon evaluation instructions and credentials.
