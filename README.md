# VulnScope

Multi-tenant web security intelligence SaaS: passive, low-impact checks on websites you own and have
authorized, with evidence, remediation guidance, and re-scan verification.

> **Status:** Phase 01 / Task 01.1a — repository skeleton and tooling only. There is no application
> code yet, and nothing here scans anything. External scanning is disabled
> (`SCANNER_ALLOW_EXTERNAL=false`).

Design documents live in [`docs/`](docs/). Start with [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md)
and [`docs/BACKLOG.md`](docs/BACKLOG.md).

## Repository layout

```
apps/web            Next.js app (Task 01.2+)            — placeholder
apps/extension      Chrome MV3 extension (Task 10.1+)    — placeholder
packages/contracts  Shared TS contracts                  — skeleton
packages/rules      Python rule engine                   — skeleton (uv workspace member)
services/api        FastAPI API                          — skeleton (uv workspace member)
services/worker     Celery core worker                   — skeleton (uv workspace member)
services/scanner    Isolated passive scanner             — skeleton (uv workspace member)
infra/              Compose, fixtures (Task 01.1b+)      — placeholder
tools/              Repository tooling scripts (secret scan)
docs/               PRD, architecture, ADRs, threat model, backlog
```

## Prerequisites

| Tool    | Version    | Notes                                           |
| ------- | ---------- | ----------------------------------------------- |
| Node.js | 24.x LTS   | `.node-version`                                 |
| pnpm    | 12.8.2     | pinned in `package.json` → `packageManager`     |
| Python  | 3.12.x     | `.python-version`                               |
| uv      | 0.12.21    | pinned in `pyproject.toml` → `required-version` |
| Git     | any recent |                                                 |

Docker, Docker Compose and the Supabase CLI are **not** needed yet (Tasks 01.1b and 03.1).

## Setup

```bash
pnpm install --frozen-lockfile
```

```bash
uv sync --frozen --all-groups
```

uv is configured to never build packages from source and never download a Python interpreter
(`pyproject.toml` → `[tool.uv]`).

## Checks

JavaScript / TypeScript:

```bash
pnpm lint
```

```bash
pnpm format:check
```

```bash
pnpm typecheck
```

Python:

```bash
uv run --frozen ruff check .
```

```bash
uv run --frozen ruff format --check .
```

```bash
uv run --frozen mypy
```

Secret scanning (SAC-SEC-01 baseline). Scans every tracked and untracked-but-not-ignored file
with all detectors, and the lockfiles with the structured detectors only (entropy detectors off,
because integrity hashes look random). Fails if anything is not already recorded in
`.secrets.baseline`:

```bash
uv run --frozen python tools/check_secrets.py
```

To refresh the baseline after reviewing a finding:

```bash
uv run --frozen detect-secrets scan --baseline .secrets.baseline
```

## Environment variables

Copy `.env.example` to `.env` for local use. `.env` is git-ignored. **Never** put real credentials in
`.env.example`.

## Rules of the road

Work proceeds one approved micro-task at a time (see `docs/BACKLOG.md`). The scanner must never be
pointed at systems you don't own or haven't explicitly authorized (`docs/RULES_OF_ENGAGEMENT.md`).
