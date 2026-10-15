# ADR-0005: Tenant isolation and RBAC enforcement

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Open: OAD-01
- Related: ARCHITECTURE §7, PRD FR-04/FR-05

## Decision
1. Org context only from the path `/api/v1/orgs/{org_id}/…`, accepted after an active membership lookup for the JWT `sub`.
2. Static permission matrix `role → permissions` (defined in 00.4). Every route declares its required permission via a dependency; a startup check fails if any route has none (deny by default).
3. Org-scoped repositories: every method requires `org_id`; child objects join back to the org.
4. Foreign or unknown IDs → 404.
5. Jobs carry org/project/initiator and re-check authorization at execution time.
6. A cross-tenant test suite is a CI gate (04.2).
7. Postgres RLS as a second layer — pending (OAD-01, recommended yes).

## Alternatives
- Schema-per-tenant / DB-per-tenant — rejected for beta (migration cost).
- RLS only, without app checks — rejected (harder to test and to produce clear errors).

## Consequences
Every new endpoint must go through the scoped repository pattern; code review checks for it.
