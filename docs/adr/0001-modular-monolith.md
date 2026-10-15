# ADR-0001: Modular monolith with two worker pools

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2
- Related: ARCHITECTURE §2–§4, PRD R-11

## Context
Solo builder, beta scale, but strict separation is needed where the risk lives (network I/O toward customer sites). Microservices would multiply deploys, service-to-service auth, and failure modes without a measured benefit.

## Decision
- One FastAPI service (`services/api`) split into domain modules with service/repository layers; modules never read each other's tables.
- One **core worker** pool (Celery) for DB-backed async work.
- One **scanner** pool, deployed separately in an isolated zone — the only deliberate split, justified by security, not scale.
- Web (Next.js) and extension are separate clients.

## Alternatives
- Microservices per domain — rejected: cost and complexity, no scale need.
- Scanner inside the core worker — rejected: SSRF blast radius would include DB credentials.

## Consequences
- \+ Simple deploy and local dev; clear seams to extract later.
- − API deploy is a larger blast radius → mitigated by module boundaries and tests.
