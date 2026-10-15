# ADR-0002: Monorepo layout and core stack

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2
- Related: Contract §3, ARCHITECTURE §3

## Decision
| Area | Choice | Why |
|---|---|---|
| Repo | Monorepo: pnpm workspaces (`apps/web`, `apps/extension`, `packages/contracts`) + Python (`services/api`, `services/worker`, `services/scanner`, `packages/rules`) | One place for contracts, docs, CI; no Nx/Turborepo until a measured need |
| Web | Next.js App Router, TypeScript strict, Tailwind, shadcn/ui + Radix, Lucide, React Hook Form + Zod, TanStack Query | SSR for public pages/SEO, mature accessible primitives, owner already knows React |
| API | FastAPI, Pydantic v2, SQLAlchemy 2, Alembic | Typed validation, OpenAPI out of the box, Python shared with scanner/rules |
| DB | PostgreSQL | Relational integrity for tenants, constraints, JSONB for bounded evidence |
| Jobs | Celery + Redis (ADR-0006) | Time limits, cancellation, retries, beat schedules |
| Extension | Chrome MV3, TypeScript, React side panel, Vite (Plasmo only if justified in 10.1) | Minimal build tooling, no remote code |
| Contracts | OpenAPI → generated TS types; JSON Schema for scan job/result | Single source of truth across two languages |
| Python packaging | uv workspaces (OAD-09, verify in 01.1) | Fast, lockfile |
| Local infra | Docker Compose | Reproducible, free |

Versions: current stable, verified and pinned with lockfiles in 01.1.

## Alternatives
- Node/TS backend (e.g., NestJS) — rejected: scanner/rule ecosystem and the contract favour Python.
- Turborepo/Nx — deferred until build times justify them.

## Consequences
Two languages → shared contracts must be generated, never hand-copied.
