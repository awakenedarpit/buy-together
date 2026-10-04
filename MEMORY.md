# MEMORY.md — Project Memory & Continuity Ledger

> **Notice**: This file tracks the live state of the "Buy Together" project. It must be updated at the end of every development phase or session to ensure flawless continuity across AI models, sessions, and human collaborators.

---

## 1. Current Status

* **Phase**: **HACKATHON MVP COMPLETED & VERIFIED (LIVE PUBLIC DEMO URLS)**
* **Overall Completion**: 90%
* **Current Task**: Full Hackathon MVP delivery — Frontend, Backend, AI Extraction, Member Dashboard, Manager Dashboard, Public Tunnels, End-to-End Live Verification.
* **Last Completed Task**: Live end-to-end testing (10/10 checks passing), Public Cloudflare tunnels active, 34/34 backend tests passing, frontend production bundle built and serving.
* **Next Task**: Post-hackathon optimizations (Gemma 4 12B hosted GPU deployment, permanent domain mapping, advanced analytics).

---

## 2. Live Demo Endpoints & Verification

```text
================================================================================
BUY TOGETHER — LIVE HACKATHON MVP
================================================================================
Frontend Public URL:
https://ascii-andrea-technological-optimum.trycloudflare.com

Backend Public URL:
https://knee-mountain-butler-intellectual.trycloudflare.com

Health Endpoint:
https://knee-mountain-butler-intellectual.trycloudflare.com/api/v1/health

Database:
SQLite local engine with full Alembic migrations (1ea134d4c373) (PostgreSQL-compatible)

AI Engine:
MockAIProvider (Deterministic, zero-latency Hinglish extraction for demo reliability)

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
| **Frontend Builds** | **PASS** | React 19 + Vite 8 in 123ms with 0 warnings |
| **Public Frontend Tunnel** | **PASS** | `https://ascii-andrea-technological-optimum.trycloudflare.com` |
| **Health Check** | **PASS** | `GET /api/v1/health` returns status `ok`, provider `mock` |
| **Database Migrations** | **PASS** | Alembic migration head `1ea134d4c373` applied |
| **User Registration** | **PASS** | `POST /api/v1/auth/register` creates Member & Manager roles |
| **JWT Authentication** | **PASS** | `POST /api/v1/auth/login` issues bearer tokens |
| **AI Extraction Pipeline** | **PASS** | `"bhai 2 notebook aur ek blue pen"` extracts structured items |
| **Item Persistence** | **PASS** | Extracted items saved to `messages` & `request_items` tables |
| **Member Dashboard** | **PASS** | `GET /api/v1/requests` lists personal items with ownership isolation |
| **Inline Item Editing** | **PASS** | `PATCH /api/v1/requests/{id}` updates quantity & variant |
| **Item Deletion** | **PASS** | `DELETE /api/v1/requests/{id}` deletes item with IDOR protection |
| **Manager Inspection** | **PASS** | `GET /api/v1/manager/requests` displays all requests across members |
| **Manager Unit Pricing** | **PASS** | `PATCH /api/v1/manager/requests/{id}/price` updates unit & total cost |
| **Dynamic Aggregation** | **PASS** | `GET /api/v1/manager/combined` groups by `(name, variant, unit)` |
| **Regression Suite** | **PASS** | **34/34 pytest tests passing** (0 errors, 0 warnings) |

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
