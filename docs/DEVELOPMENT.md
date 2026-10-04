# Local Development Guide

## Project: Buy Together
**Audience**: Software Engineers, AI Agents, Contributors  

---

## 1. Prerequisites

Ensure your development machine has the following tools installed:
- **Python**: 3.12 or higher (Python 3.14 verified)
- **Node.js**: 20+ (Node v26 verified) & npm
- **Git**: 2.30+
- **PostgreSQL** (optional for local; SQLite in-memory mode supported for immediate local dev and automated tests)

---

## 2. Quickstart Step-by-Step

### 2.1 Clone & Repository Inspection
```bash
cd /Users/user/PYDATA
git status
```

### 2.2 Environment Configuration
Copy the template configuration into `.env`:
```bash
cp .env.example .env
```
For initial local development, you can leave `AI_PROVIDER=mock` to test the full pipeline immediately without waiting for model downloads or GPU setup.

### 2.3 Backend Setup (Python & FastAPI)
1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
   Interactive Swagger documentation will be available at:  
   `http://localhost:8000/docs`

### 2.4 Frontend Setup (React & Vite)
1. In a separate terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The web application will be accessible at:  
   `http://localhost:5173`

---

## 3. Running Automated Tests

Run the full backend test suite:
```bash
pytest backend/tests/ -v
```

Run test suite with code coverage:
```bash
pytest --cov=backend/app --cov-report=term-missing
```

---

## 4. Coding Conventions & Best Practices

1. **Type Hints**: All Python functions must include parameter and return type hints.
2. **Layer Separation**:
   - Routers only parse HTTP requests and pass validated schemas to Services.
   - Services handle transactions, authorization checks, and orchestrate calls.
   - Repositories/Models handle database mappings.
3. **No Hardcoded Values**:
   - Never commit API keys, connection strings, or JWT secrets.
   - Use `Settings` loaded via `pydantic-settings`.
4. **Clean Commits**:
   - Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.
