# ADR-004: Dynamic Aggregation Query Pattern vs. Persistent Aggregate Table

## Status
Accepted

## Context
In Buy Together, members independently request items (e.g. Member A requests 2 notebooks, Member B requests 3 notebooks). The manager needs to see the consolidated demand (Notebook: quantity 5). We evaluated whether to store aggregated totals in a dedicated database table (`combined_requirements`) or calculate them dynamically on demand.

## Decision
We decide **NOT** to create a persistent `combined_requirements` database table for the MVP. Instead, aggregation is computed dynamically via SQL queries (`GROUP BY LOWER(name), LOWER(COALESCE(variant, '')), LOWER(unit)`) or service-level aggregation.

## Alternatives Considered
1. **Persistent `combined_requirements` Table with Database Triggers or Sync Service**:
   - *Pros*: Faster reads if millions of requests exist.
   - *Cons*: High risk of data drift. If a member edits their quantity from 3 to 2, or deletes their item, or if the manager updates a price, complex cache invalidation and trigger logic is required. Race conditions easily lead to incorrect inventory totals.

## Consequences
- Guaranteed mathematical consistency: The aggregated purchasing list always accurately reflects the current state of individual member items.
- Zero risk of desynchronization when items are edited, deleted, or rejected.
- Simplified schema maintenance and zero need for asynchronous event reconciliation.
- Query performance will be optimized with composite database indexes on `(LOWER(name), LOWER(COALESCE(variant, '')), LOWER(unit))`.
