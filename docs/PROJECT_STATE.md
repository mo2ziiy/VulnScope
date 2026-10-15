# PROJECT_STATE

- **Current task:** Phase 01 / Task 01.1a — **implemented, awaiting owner review/approval**. No git commit made. Task 01.1b **not started** (needs explicit approval).
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
| `pnpm typecheck` | exit 0 |
| `uv run --frozen ruff check .` | exit 0 (first run: 2× S607 from misplaced `noqa` in `tools/check_secrets.py` → fixed, re-run clean) |
| `uv run --frozen ruff format --check .` | exit 0 (10 files) |
| `uv run --frozen mypy` | exit 0 (5 source files, strict) |
| `uv run --frozen python tools/check_secrets.py` | exit 0 (58 files; baseline: 27 plugins, 0 findings) |
| Negative tests (temporary `.negcheck/`, deleted afterwards) | eslint exit 1, tsc exit 2, ruff exit 1 (incl. S307 `eval`), mypy exit 1, secret scan exit 1 on planted AWS example key — all failed as expected |

SAC-SEC-01 status: **local baseline configured and passing** (detect-secrets). CI secret scanning (gitleaks) is Task 01.1b. Client-bundle scanning applies once bundles exist.

## State
- **Repo:** git initialized (`main`), **no commits**; 34 new files + existing `docs/` and contract file are untracked; `node_modules/`, `.venv/`, `.mypy_cache/`, `.ruff_cache/` ignored; LF line endings
- **Services:** none running · **External scanning:** disabled (`SCANNER_ALLOW_EXTERNAL=false` in `.env.example`; no scanner code exists)
- **Tests:** only the tooling checks above. No application/implementation tests exist. All SAC/AC/AC-LOCK/AC-RES/AC-STEP remain design specifications
- **Blockers for 01.1b:** ENV-01, ENV-02, ENV-03 (owner must enable Virtual Machine Platform and install Docker Desktop); PostgreSQL version still to be chosen with evidence (DEC-064)
- **Open decisions:** OAD-03 · OAD-13 (DEC-038) · OAD-02 (DM-A2 provisional) · DM-A5 (03.1) · TM-OD-01…05 · PRD OD-01, 03, 04, 05 · ARCHITECTURE OAD-01, 06…08, 10…12, 14 · DM-OI-01…03 · PostgreSQL version (DEC-064)
- **Latest commit:** none
- **Next:** owner review of 01.1a → approval → first commit (on owner instruction) → 01.1b only after explicit approval
