# Deployment Guide & Production Topology

## Project: Buy Together
**Architecture**: Decoupled Cloud Native / Serverless & Containerized  

---

## Live Hackathon MVP Deployment (Verified)

| Component | Status | Live Public URL |
| :--- | :--- | :--- |
| **Frontend SPA** | **LIVE** | `https://ascii-andrea-technological-optimum.trycloudflare.com` |
| **FastAPI Backend** | **LIVE** | `https://knee-mountain-butler-intellectual.trycloudflare.com` |
| **Health Check** | **PASS** | `https://knee-mountain-butler-intellectual.trycloudflare.com/api/v1/health` |
| **Database** | **PASS** | SQLite local engine with full Alembic migrations (`1ea134d4c373`) |
| **AI Provider** | **MOCK** | Deterministic MockAIProvider with Hinglish extraction support |

---

## 1. Production Topology Overview

```
                                  ┌──────────────────────────────┐
                                  │      Vercel / Cloudflare     │
                                  │   (Static React + Vite SPA)  │
                                  └──────────────┬───────────────┘
                                                 │ HTTPS
                                                 ▼
┌──────────────────────────────┐  HTTPS   ┌──────────────────────────────┐
│  HuggingFace Inference API   │◄─────────┤       Render / Railway       │
│   (Gemma 4 12B Serverless)   │          │   (FastAPI Backend Container)│
└──────────────────────────────┘          └──────────────┬───────────────┘
                                                         │ PostgreSQL Wire
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │      Supabase / Neon DB      │
                                          │     (Managed PostgreSQL)     │
                                          └──────────────────────────────┘
```

---

## 2. Infrastructure Tiers & Cost Optimization

| Component | Target Service | Free / Low-Cost Tier Capability | Production Recommendation |
| :--- | :--- | :--- | :--- |
| **Frontend** | Vercel / Cloudflare Pages | Free tier includes global edge CDN and automatic SSL. | Vercel / Cloudflare |
| **Backend** | Render / Railway / Fly.io | 512MB RAM container tier (sufficient for FastAPI). | Render / Railway |
| **Database** | Neon / Supabase | Free tier PostgreSQL (500MB storage, pooled connections). | Managed PostgreSQL |
| **AI Inference** | HuggingFace Inference API | Serverless token-based inference or local Ollama. | HF Inference / Dedicated endpoint |

> **Important Design Note**: Running a 12B parameter model (Gemma 4 12B) in full 16-bit precision requires ~24GB VRAM, which is expensive on cloud GPU instances. The architecture is explicitly designed so production can run on serverless inference APIs without paying for an idle dedicated GPU, while local workstations can run lightweight quantized local models or `MockAIProvider`.

---

## 3. Environment Variables Reference

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `ENVIRONMENT` | Yes | `production` | Deployment mode (`development`, `production`). |
| `DATABASE_URL` | Yes | None | Full PostgreSQL connection string with SSL mode. |
| `JWT_SECRET` | Yes | None | 64+ char random hex string for JWT signing. |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token TTL in minutes (24h). |
| `CORS_ORIGINS` | Yes | None | Comma-separated list of allowed frontend domains. |
| `AI_PROVIDER` | Yes | `hosted` | AI engine: `mock`, `local_gemma`, `hosted`. |
| `HOSTED_INFERENCE_URL` | Conditional | None | Required if `AI_PROVIDER=hosted`. |
| `HF_TOKEN` | Conditional | None | HuggingFace API key if using HF Inference API. |

---

## 4. Step-by-Step Deployment Runbook

### 4.1 Step 1: Database Setup (Supabase / Neon)
1. Create a free PostgreSQL instance on Supabase or Neon.
2. Obtain the connection string formatted for SQLAlchemy with the `psycopg` driver:
   `postgresql+psycopg://user:password@host:5432/dbname?sslmode=require`
3. Test connectivity.

### 4.2 Step 2: Backend Deployment (Render / Docker)
1. Push code to GitHub repository.
2. Connect repository to Render as a Web Service.
3. Configure build command:
   ```bash
   pip install -r backend/requirements.txt && alembic -c backend/alembic.ini upgrade head
   ```
4. Configure start command:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Set environment variables from Step 1 and generate `JWT_SECRET`.

### 4.3 Step 3: Frontend Deployment (Vercel)
1. Connect frontend folder (`frontend/`) to Vercel.
2. Build command: `npm run build`
3. Output directory: `dist`
4. Set environment variable: `VITE_API_URL=https://your-backend.onrender.com`
5. Deploy and verify HTTPS endpoint.

---

## 5. Troubleshooting & Health Checks

- **Healthcheck**: `GET /api/v1/health` returns `{"status": "ok", "database": "connected"}`.
- **Database Connection Pool Exhaustion**: In serverless deployments, use connection pooling (e.g. Supabase PgBouncer on port 6543) or configure SQLAlchemy `pool_size=5, max_overflow=2`.
- **Inference Timeout**: If the hosted model experiences cold starts, the backend gracefully catches timeout exceptions (10s threshold) and returns an informative HTTP 504 status.
