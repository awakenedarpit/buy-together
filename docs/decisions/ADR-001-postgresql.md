# ADR-001: Selection of PostgreSQL as Primary Database Engine

## Status
Accepted

## Context
Buy Together requires a robust, ACID-compliant relational data store capable of handling user authentication, message persistence, request items with relational foreign keys, cascade deletions, and grouping aggregations (`GROUP BY name, variant, unit`). In addition, the target deployment platforms (Supabase, Neon, Railway, Render) offer generous free and low-cost tiers for managed PostgreSQL instances.

## Decision
We select **PostgreSQL** (version 15+) as the primary production database engine, accessed via SQLAlchemy 2.0 ORM with the `psycopg` driver. For automated unit and integration tests running on developer machines or lightweight CI runners without a PostgreSQL daemon, SQLite (via `aiosqlite` or standard `sqlite3`) will be supported as a drop-in testing engine.

## Alternatives Considered
1. **MongoDB / NoSQL Document Store**:
   - *Pros*: Flexible document schema for AI extraction results.
   - *Cons*: Weak relational referential integrity, less mature SQL aggregation for dynamic financial reports, lack of strict schema enforcement without heavy application-layer scaffolding.
2. **SQLite Exclusively**:
   - *Pros*: Zero setup, embedded single file.
   - *Cons*: Concurrency bottlenecks in multi-user production environments, lack of managed cloud hosting tiers like Supabase.

## Consequences
- Production deployments require a PostgreSQL instance (or cloud connection string).
- Migrations will be tracked strictly using Alembic to support PostgreSQL DDL.
- Test suites must maintain ANSI SQL compatibility so tests run cleanly on SQLite.
