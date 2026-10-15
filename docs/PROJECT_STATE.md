# PROJECT_STATE

- **Current task:** Phase 01 / Task 01.1a — implemented; initial snapshot committed and pushed on the owner's instruction (2026-10-15). **Independent review remediation done locally, uncommitted, awaiting owner review.** Task 01.1a is **not** owner-approved yet. Task 01.1b **not started** (needs explicit approval).
- **Phase 00:** complete at documentation/design level (DEC-058); post-Phase-00 audit pass approved 2026-10-15.

## Environment checks (2026-10-15)

| ID | Result | Needed by | Status |
|---|---|---|---|
| ENV-01 Docker | `docker` not found | 01.1b | **FAIL** — blocker for 01.1b |
| ENV-02 WSL2 | `Ubuntu` registered as v2 (stopped); WSL reports *Virtual Machine Platform* not enabled; firmware virtualization = True | 01.1b | **FAIL** — owner action, blocker for 01.1b |
| ENV-03 Compose | not found | 01.1b | **FAIL** — blocker for 01.1b |
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

## Independent review remediation (2026-10-15, uncommitted)

| Item | Finding | Fix (minimal) | Evidence |
|---|---|---|---|
| 1 TypeScript typecheck | Effective today (tsc runs on `packages/contracts/src/index.ts`), but `pnpm -r --if-present typecheck` exits 0 when no workspace package defines `typecheck` → could pass vacuously | Root script → `pnpm -r typecheck` (fails if any workspace package lacks the script) | Vacuous case: with `--if-present` exit 0, without exit 1. Negative test: intentional TS2322 → exit 1; restored → exit 0, no diff |
| 2a Secret scan, unusual filenames | **Bug:** `git ls-files` quotes non-ASCII names (`"caf\303\251 secret.txt"`); the hook couldn't open the quoted path and skipped it with exit 0 → a synthetic key was missed | NUL-separated listing (`git ls-files -z`), skip paths that no longer exist | Negative test A (non-ASCII + space name) now exit 1 |
| 2b Secret scan, lockfiles | Lockfiles were excluded entirely; detect-secrets also treats `.lock` as non-text, so `uv.lock` was skipped even when named | Second pass over lockfiles with structured detectors only (entropy detectors off; integrity hashes are high-entropy) and the non-text filter disabled for that pass | Negative tests C (`uv.lock`) and D (`pnpm-lock.yaml`) now exit 1; clean lockfiles exit 0. Only `uv.lock` among tracked files was classified non-text |
| 2c Baseline | 0 findings, so nothing silently accepted; no `pragma: allowlist` in tracked files | — | Inspected |
| 3 Git state | Initial commit `bfc6a3c` on local `main` = `origin/main` of `https://github.com/mo2ziiy/VulnScope.git`. Its message (`chore: bootstrap monorepo skeleton, tooling and Phase 00 design docs`) differs from the later-requested `chore: initialize VulnScope monorepo and tooling`; history not rewritten (owner decision pending) | This file updated | `git log`, `git ls-remote` |

Remaining limitations: the general pass still uses detect-secrets' default heuristics (binary-like extensions are skipped; only `uv.lock` was affected among tracked files); the scan covers tracked and untracked-but-not-ignored files only (ignored files such as a local `.env` are never committed, so they aren't scanned).

SAC-SEC-01 status: **local baseline configured and passing** (detect-secrets). CI secret scanning (gitleaks) is Task 01.1b. Client-bundle scanning applies once bundles exist.

## State
- **Repo:** initial commit `bfc6a3c` pushed to `main` of `https://github.com/mo2ziiy/VulnScope` (private; remote was empty); 61 files; local `main` = `origin/main`. Uncommitted remediation changes in 4 files (root package manifest, the scan script under `tools/`, the README, and this file); `node_modules/`, `.venv/`, `.mypy_cache/`, `.ruff_cache/` ignored; LF line endings
- **Services:** none running · **External scanning:** disabled (`SCANNER_ALLOW_EXTERNAL=false` in `.env.example`; no scanner code exists)
- **Tests:** only the tooling checks above. No application/implementation tests exist. All SAC/AC/AC-LOCK/AC-RES/AC-STEP remain design specifications
- **Blockers for 01.1b:** ENV-01, ENV-02, ENV-03 (owner must enable Virtual Machine Platform and install Docker Desktop); PostgreSQL version still to be chosen with evidence (DEC-064)
- **Open decisions:** OAD-03 · OAD-13 (DEC-038) · OAD-02 (DM-A2 provisional) · DM-A5 (03.1) · TM-OD-01…05 · PRD OD-01, 03, 04, 05 · ARCHITECTURE OAD-01, 06…08, 10…12, 14 · DM-OI-01…03 · PostgreSQL version (DEC-064)
- **Latest commit:** `bfc6a3c` chore: bootstrap monorepo skeleton, tooling and Phase 00 design docs
- **Next:** owner review of the remediation → decision on committing it (and on the initial commit message) → owner approval of 01.1a → 01.1b only after explicit approval
