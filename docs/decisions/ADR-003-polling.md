# ADR-003: Selection of HTTP Polling over WebSockets for MVP

## Status
Accepted

## Context
When multiple members submit requests and the manager updates prices or item statuses, the dashboard must reflect changes without requiring manual full-page reloads. We evaluated two architectural approaches for real-time data sync: WebSockets (or Server-Sent Events) versus client-side HTTP polling.

## Decision
For the MVP, we adopt resilient client-side **HTTP Polling** at a 3–5 second interval. The polling hook will automatically pause when the browser tab is hidden (`document.visibilityState === 'hidden'`) to eliminate wasteful queries. The backend API is designed cleanly so that WebSockets or SSE can be plugged in later if needed without altering the underlying data models.

## Alternatives Considered
1. **WebSockets (Full Duplex)**:
   - *Pros*: Sub-millisecond latency, instant bidirectional events.
   - *Cons*: Significant operational complexity on free serverless/container platforms (reconnections, connection limits, stateful socket managers, sticky sessions, proxy timeouts).
2. **Server-Sent Events (SSE)**:
   - *Pros*: Simpler than WebSockets, unidirectional HTTP stream.
   - *Cons*: Still requires open persistent connections and complicates HTTP serverless scaling on tiers like Vercel/Render.

## Consequences
- Radically simplifies backend architecture and deployment to free/low-cost tiers.
- Minimizes failure surface area and eliminates socket reconnection management bugs.
- Network traffic is kept low due to lightweight JSON responses and pause-on-blur client optimization.
