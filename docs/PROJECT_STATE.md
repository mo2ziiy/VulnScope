# PROJECT_STATE

- **Current task:** Phase 01 / Task 01.1b, in owner-approved microtasks. Done: 01.1b-02a (local PostgreSQL 18.6, committed `f300710` + `5a5d53d`). Redis architecture review done; decisions recorded as DEC-069…071 (`962b803`). D-1 decided for local development: Valkey 9.1.2, standard `valkey/valkey` image (DEC-072). Next Redis/Valkey work needs its own approval.
- **Task 01.1a:** implemented and pushed (`bfc6a3c`, `6e0ea90`, state sync `26a5a91`); the remediation passed independent code review. A separate final 01.1a approval isn't recorded in this file.
- **Phase 00:** complete at documentation/design level (DEC-058); post-Phase-00 audit pass approved 2026-10-15.

## Environment checks (2026-10-15)

| ID | Result | Needed by | Status |
|---|---|---|---|
| ENV-01 Docker | Docker Engine 29.8.2 (client + server), Docker Desktop (re-checked 2026-10-15) | 01.1b | PASS |
| ENV-02 WSL2 | Default version 2, default distribution `Ubuntu`; Docker Engine runs (re-checked 2026-10-15) | 01.1b | PASS |
| ENV-03 Compose | Docker Compose v5.6.0 (re-checked 2026-10-15) | 01.1b | PASS |
| ENV-04 Node + pnpm | Node v24.16.0 (24.x LTS); pnpm **12.8.2** | 01.1a | PASS |
| ENV-05 Python + uv | Python 3.12.10 (Microsoft Store CPython at `…\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe`); uv **0.12.21** | 01.1a | PASS |
| ENV-06 Git | 2.50.1.windows.1 | 01.1a | PASS |
| ENV-07 Supabase CLI | not found | 03.1 | Not needed yet |

## Tool installation record (owner-approved)
- **pnpm 12.8.2** — `npm install -g pnpm@12.8.2` (registry.npmjs.org; sha512 integrity, registry signature, provenance attestation). Installed `pnpm@12.8.2` + official platform binary `@pnpm/exe.win32-x64@12.8.2`. **The official `preinstall`/`postinstall` scripts (`node install.js`) executed during this install.**
- **uv 0.12.21** — `winget install --id astral-sh.uv --exact --version 0.12.21 --source winget --disable-interactivity` (no agreement flags, no admin). SHA256 matches Astral's official release checksum; Authenticode valid + timestamped, signer `OpenAI OpCo, LLC` (consistent with the reported OpenAI–Astral acquisition; manifest publisher Astral Software Inc.). **Approved deviation (DEC-066):** winget added the package folder `%LOCALAPPDATA%\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe` to the **user** PATH (Developer Mode off → no Links symlinks). Machine PATH unchanged.
- No other global tools installed. WSL2, Docker, Windows settings untouched.

## Project dev dependencies (project-local, locked)

| Package | Version | Lockfile |
|---|---|---|
| typescript | 6.0.3 | `pnpm-lock.yaml` |
| eslint | 10.11.0 | `pnpm-lock.yaml` |
| @eslint/js | 10.0.1 | `pnpm-lock.yaml` |
| typescript-eslint | 8.71.0 | `pnpm-lock.yaml` |
| prettier | 3.9.9 | `pnpm-lock.yaml` |
| ruff | 0.16.9 | `uv.lock` |
| mypy | 2.3.1 | `uv.lock` |
| detect-secrets | 1.5.0 | `uv.lock` |

- pnpm: 97 packages total (5 direct + 92 transitive); no peer warnings; no installed package declares install scripts.
- uv: 14 packages (3 direct + 11 transitive: ast-serialize 0.13.0, certifi 2026.7.22, charset-normalizer 3.5.2, idna 3.20, librt 0.16.0, mypy-extensions 1.1.0, pathspec 1.1.1, pyyaml 6.0.3, requests 2.34.2, typing-extensions 4.16.0, urllib3 2.8.0); all from wheels; `no-build = true`, `python-downloads = "never"`, `required-version = "==0.12.21"`.

## Checks run (2026-10-15) — actual executions

| Command | Result |
|---|---|
| `pnpm install --frozen-lockfile` | exit 0 ("Lockfile passes supply-chain policies") |
| `uv sync --frozen --all-groups` | exit 0 |
| `pnpm lint` | exit 0 |
| `pnpm format:check` | exit 0 (first run failed on `eslint.config.mjs`, `README.md` → formatted with Prettier, re-run clean) |
| `pnpm typecheck` | exit 0 — runs `tsc 6.0.3` in `packages/contracts` (checks `src/index.ts`, the only TS file) |
| `uv run --frozen ruff check .` | exit 0 (first run: 2× S607 from misplaced `noqa` in `tools/check_secrets.py` → fixed, re-run clean) |
| `uv run --frozen ruff format --check .` | exit 0 (10 files) |
| `uv run --frozen mypy` | exit 0 (5 source files, strict) |
| `uv run --frozen python tools/check_secrets.py` | exit 0 (58 files with all detectors + 2 lockfiles with structured detectors; baseline: 27 plugins, 0 findings) |
| Negative tests (temporary `.negcheck/`, deleted afterwards) | eslint exit 1, tsc exit 2, ruff exit 1 (incl. S307 `eval`), mypy exit 1, secret scan exit 1 on planted AWS example key — all failed as expected |

## Independent review remediation (2026-10-15, committed in `6e0ea90`, passed independent code review)

| Item | Finding | Fix (minimal) | Evidence |
|---|---|---|---|
| 1 TypeScript typecheck | Effective today (tsc runs on `packages/contracts/src/index.ts`), but `pnpm -r --if-present typecheck` exits 0 when no workspace package defines `typecheck` → could pass vacuously | Root script → `pnpm -r typecheck` (fails if any workspace package lacks the script) | Vacuous case: with `--if-present` exit 0, without exit 1. Negative test: intentional TS2322 → exit 1; restored → exit 0, no diff |
| 2a Secret scan, unusual filenames | **Bug:** `git ls-files` quotes non-ASCII names (`"caf\303\251 secret.txt"`); the hook couldn't open the quoted path and skipped it with exit 0 → a synthetic key was missed | NUL-separated listing (`git ls-files -z`), skip paths that no longer exist | Negative test A (non-ASCII + space name) now exit 1 |
| 2b Secret scan, lockfiles | Lockfiles were excluded entirely; detect-secrets also treats `.lock` as non-text, so `uv.lock` was skipped even when named | Second pass over lockfiles with structured detectors only (entropy detectors off; integrity hashes are high-entropy) and the non-text filter disabled for that pass | Negative tests C (`uv.lock`) and D (`pnpm-lock.yaml`) now exit 1; clean lockfiles exit 0. Only `uv.lock` among tracked files was classified non-text |
| 2c Baseline | 0 findings, so nothing silently accepted; no `pragma: allowlist` in tracked files | — | Inspected |
| 3 Git state | Initial commit `bfc6a3c` (`chore: bootstrap monorepo skeleton, tooling and Phase 00 design docs`) and remediation commit `6e0ea90` (`fix(tooling): harden typecheck and secret scanning`) on `main`, both pushed to `origin/main` of `https://github.com/mo2ziiy/VulnScope.git`. The initial commit's message differs from the later-requested `chore: initialize VulnScope monorepo and tooling`; history was not rewritten | This file updated | `git log`, `git ls-remote` |

Remaining limitations: the general pass still uses detect-secrets' default heuristics (binary-like extensions are skipped; only `uv.lock` was affected among tracked files); the scan covers tracked and untracked-but-not-ignored files only (ignored files such as a local `.env` are never committed, so they aren't scanned).

SAC-SEC-01 status: **local baseline configured and passing** (detect-secrets). CI secret scanning (gitleaks) is Task 01.1b. Client-bundle scanning applies once bundles exist.

## Task 01.1b progress

| Microtask | Result | Commit |
|---|---|---|
| PostgreSQL version | PostgreSQL 18 selected for local development (DEC-067) | `6344c75` |
| Broker-loss security review | Constraints C-a…C-h recorded; execution permit is a candidate only (DEC-068) | `b29f535` |
| 01.1b-02a Local PostgreSQL | `infra/compose.yaml` (image pinned by digest, `127.0.0.1:55432`, uid 999, read-only rootfs, no capabilities, limits), `infra/postgres/pg_hba.conf` (no `trust`/`md5`/`password`; TCP `scram-sha-256`, socket `peer` for `postgres` only), `tools/gen_local_secrets.py`. Validated: auth matrix over TCP (IPv4/IPv6, host port, `core_net`) and socket, persistence across `down`/`up`, and fresh initialization on an isolated temporary project | `f300710` |
| Fresh-init hardening | `POSTGRES_INITDB_ARGS` so new clusters' generated `pg_hba.conf` has no `trust` rules; validated on an isolated temporary project | `5a5d53d` |
| Redis architecture review | Local decisions DEC-069 (accepted), engine DEC-070 (provisional, later superseded by DEC-072), open items DEC-071 | `962b803` |
| D-1 technology review | Valkey 9.1.2 (`valkey/valkey`, not `valkey-bundle`) accepted for local development only (DEC-072). Candidate index digest `sha256:418652cf…11eb9dfd` from registry metadata, to be re-verified before any pull. No image pulled; production engine not chosen (OAD-03, LG-SCN-03) | this docs change |

Known residuals:
- The existing local volume `vulnscope_pgdata` still holds the image-generated data-directory `pg_hba.conf` with `trust` rules. It isn't loaded (`hba_file` points to `/etc/postgresql/pg_hba.conf`). Fixing it means touching the volume, so it needs owner approval.
- The running `vulnscope-postgres-1` was created before `5a5d53d`, so the next `docker compose up` recreates the container. The volume and data are kept, and `POSTGRES_INITDB_ARGS` is ignored for an existing cluster.

Documentation reconciliation required (separate approved tasks; nothing below is changed yet):
- DATA_MODEL R-L5 and API_CONTRACTS §9.3 still describe terminal-message-based early lease release, which DEC-068 C-a suspends.
- DATA_MODEL R-L9 accepts any `started` inside the start window, so two scanners could start the same attempt (broker-loss review RC-3). Still unresolved.
- ARCHITECTURE §8.3 shows the API checking the kill switch in Redis-core. The authoritative check is PostgreSQL (`platform_controls`, TX-09). The wording should say so.
- ARCHITECTURE §4 (local development networking) puts fixtures on `scan_net`; DEC-069 records an `internal` `scan_net` as provisional and leaves the D-2 split open.
- Valkey is now the local engine (DEC-072). These still say "Redis" / "Redis ≥ 7" and need wording that names Valkey as the local engine while keeping "≥ 7 with ACL selectors" as a compatibility requirement (not proof of equivalence):
  - ADR-0006: decision text and the scanner ACL note ("Redis ≥ 7 selectors").
  - ARCHITECTURE §9.4: the "Minimum ACL (Redis ≥ 7 selectors …)" heading.
  - THREAT_MODEL §4.6: the "ACL selectors need Redis ≥ 7.0" row, and R-RES-12 wording.
  - THREAT_MODEL A-TM-04: "Redis ≥ 7 with ACL selectors is available locally and on the chosen platform", which needs a Valkey local / platform-engine split.
  - Also found: BACKLOG row 01.1b ("Redis ≥ 7") and THREAT_MODEL SAC-SCN-08 ("Integration with Redis ≥ 7").
- Third-party licence and supply-chain review have no launch gate (DEC-070, DEC-072).

## State
- **Repo:** `main` at `https://github.com/mo2ziiy/VulnScope` (private): `bfc6a3c` → `6e0ea90` → `26a5a91` → `6344c75` → `b29f535` → `f300710` → `5a5d53d` → `962b803`, all pushed, history linear, no force-push; `node_modules/`, `.venv/`, `.mypy_cache/`, `.ruff_cache/`, `infra/.secrets/` ignored; LF line endings
- **Services (local):** `vulnscope-postgres-1` (PostgreSQL 18.6, healthy, `127.0.0.1:55432`, volume `vulnscope_pgdata`). No Redis, API, worker or scanner exists · **External scanning:** disabled (`SCANNER_ALLOW_EXTERNAL=false` in `.env.example`; no scanner code exists)
- **Tests:** the tooling checks above plus the manual 01.1b-02a infrastructure validations. No application/implementation tests exist. All SAC/AC/AC-LOCK/AC-RES/AC-STEP remain design specifications
- **Blocking for external dispatch:** LG-SCN-03, LG-SCN-10, LG-SCN-11, LG-SCN-12, OAD-13 and the other applicable scanner gates (DEC-068 C-g, DEC-071)
- **Local engine:** Valkey 9.1.2 (DEC-072). The production engine is still open (OAD-03, LG-SCN-03)
- **Open decisions:** D-4 `redis-scan` persistence (DEC-071) · D-2 local scan network split · OAD-03 · OAD-07 · OAD-13 (DEC-038) · OAD-02 (DM-A2 provisional) · DM-A5 (03.1) · TM-OD-01…05 · PRD OD-01, 03, 04, 05 · ARCHITECTURE OAD-01, 06, 08, 10…12, 14 · DM-OI-01…03 · R-L5 replacement and execution permit (DEC-068 candidate)
- **Latest commit:** `962b803` docs: record Redis infrastructure decisions and project state
- **Next:** owner review of DEC-072 → 01.1b-02b-1 `redis-core` on Valkey (re-verify digest, approved pull, DEC-069 configuration) only after its own approval. The doc reconciliation above is a separate task
