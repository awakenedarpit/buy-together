# Changelog

All notable changes to the **Buy Together** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Git repository initialization and `.gitignore` targeting Python, Node, and model weight assets.
- `.env.example` defining explicit configuration contracts for API, database, auth, and AI providers.
- `AGENTS.md` operating manual for AI coding agents with zero-trust AI rules and memory handoff protocols.
- `MEMORY.md` dynamic state ledger for continuity between model switches and sessions.
- `TASKS.md` 18-phase implementation roadmap.
- Complete documentation suite under `docs/`:
  - `docs/PRD.md` (Product Requirements Document)
  - `docs/TRD.md` (Technical Requirements Document)
  - `docs/ARCHITECTURE.md` (System Architecture)
  - `docs/API.md` (REST API Specification)
  - `docs/DATABASE.md` (Relational Schema & Dynamic Aggregation)
  - `docs/AI.md` (AI Extraction & Gemma Integration)
  - `docs/SECURITY.md` (Security Policy & RBAC)
  - `docs/TESTING.md` (Testing Strategy)
  - `docs/DEPLOYMENT.md` (Deployment Runbook)
  - `docs/DEVELOPMENT.md` (Developer Setup Guide)
  - `docs/AI_AGENT_HANDOFF.md` (Model Switch Protocol)
  - Architecture Decision Records (`ADR-001` through `ADR-004`).
- Foundational `README.md`.

### Security
- Mandated zero-trust pipeline for AI model outputs: strict validation through Pydantic before database writes.
- Established strict Role-Based Access Control (RBAC) separating `MEMBER` and `MANAGER` capabilities.
- Prohibited committing raw `.env` files or credentials.
