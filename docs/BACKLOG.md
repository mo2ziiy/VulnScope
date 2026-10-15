# VulnScope — Ordered Implementation Backlog (Phases 01–13)

| Field | Value |
|---|---|
| Status | **APPROVED — DESIGN LEVEL v0.3 — Task 00.4 (owner approval 2026-10-15, DEC-058)** |
| Date | 2026-10-15 |
| Changelog | **v0.3:** AC-LOCK-12…17, `scanner_instances`, heartbeat and new gates (LG-SCN-10, LG-SCN-11, LG-APP-07, LG-IAM-04, LG-IAM-05, LG-OPS-09) assigned. **v0.2:** AC-LOCK, AC-RES and AC-STEP tests assigned; host-lease tables added to 06.3; DEC-043 accepted (order + splits). **v0.1:** initial draft |
| Sources | Contract §9 phase map · PRD · ARCHITECTURE · THREAT_MODEL (SAC) · SECURITY_LAUNCH_GATES (LG) · DATA_MODEL (TX) · API_CONTRACTS (API) · PERMISSIONS (PS) |

## Rules
- **Every row is one approval gate.** Work starts only after the owner writes `Approve Task <previous> — continue` naming the previous task, and stops at the end of the row. Nothing is implemented during 00.4.
- Each task follows contract §2 A–N: plan → implement only that task → run checks → integration/regression → desktop + mobile visual QA where marked → Egyptian Arabic walkthrough → owner approval → commit.
- "Tests" lists the acceptance IDs the task must make pass (or create, for later phases). Previously passing tests must keep passing.
- **VQA** = visual QA in the built-in browser at desktop (1440 px) and mobile (375 px) widths, light and dark.
- "Decision needed" items must be decided (recorded in DECISIONS.md) **before** the task starts. Otherwise the task stops at planning.

## Reordering (accepted by the owner, DEC-043)
The contract's map puts verification (05.2, 05.3) before scanner infrastructure (06.x). Approved ADR-0008 requires verification probes to run **in the scanner**, so 05.2 can't be built honestly before the broker, signed jobs and egress guard exist. Proposed execution order: **05.1 → 06.1 → 06.2a → 06.2b → 05.2 → 05.3 → 05.4 → 06.3 → 06.4**. The scan enqueue API moves from 06.1 to 06.3, because it needs scope + authorization from 05.4. Task IDs stay the same for traceability. Three tasks are split into `a`/`b` parts to keep each reviewable: 01.1, 06.2, 07.5.

## Backlog in execution order

| # | Task | Title | Prereqs | Deliverables | Tests / acceptance | VQA | Decision needed |
|---|---|---|---|---|---|---|---|
| 1 | 01.1a | Environment checks, repo skeleton, tooling | 00.4 approved | ENV-01…07 results in PROJECT_STATE; `git init` (owner approval); pnpm + uv workspaces; lint/format/typecheck config; `.env.example` (placeholders only); README dev commands | Lint/typecheck pass on skeleton; SAC-SEC-01 secret scanning configured | — | OAD-04, OAD-09, DM-OI-04 |
| 2 | 01.1b | Docker Compose, CI skeleton, API health | 01.1a | Compose: postgres, redis-core, redis-scan (Redis ≥ 7), networks `core_net`/`scan_net`; GitHub Actions (lint, test, build, secret scan, dependency audit); FastAPI skeleton with request IDs + error format; Celery core-worker skeleton; outbox relay skeleton; API-001 | SAC-API-01, SAC-API-02; compose health check; CI green | — | — |
| 3 | 01.2 | Brand system and UI primitives | 01.1b | Shield/radar SVG mark; tokens (dark-first + light); typography; primitives (button, input, dialog, toast, table, badge, empty/error states); i18n string catalog; logical CSS (DEC-010) | Vitest component tests; contrast check; axe on primitives page | ✅ | — |
| 4 | 01.3 | App shell and layout patterns | 01.2 | Responsive sidebar, org switcher placeholder (no fake data), loading/empty/error/partial patterns, confirmation dialog pattern; app CSP baseline | SAC-WEB-01 (baseline headers test) | ✅ | — |
| 5 | 01.4 | Visual QA and regression baseline | 01.3 | Playwright screenshot baseline (desktop/mobile, light/dark); axe in CI | Baseline committed; axe 0 serious violations | ✅ | — |
| 6 | 02.1 | Landing hero and primary navigation | 01.4 | Honest copy ("observations", "checks"), tagline, nav | Playwright smoke; axe | ✅ | — |
| 7 | 02.2 | Product sections, features, limitations | 02.1 | How-it-works, features, transparent limitations (PRD §2, §7) | axe; copy review checklist (no "secure"/"guarantee") | ✅ | — |
| 8 | 02.3 | Pricing preview, FAQ, contact, legal placeholders, `/scanner` page | 02.2 | Free-beta pricing preview; legal pages marked "pending legal review"; public `/scanner` page (RoE §15) with abuse-contact placeholder | Link checks; axe | ✅ | — |
| 9 | 02.4 | SEO, performance, accessibility, cross-device QA | 02.3 | Metadata, sitemap, LCP budget check | Lighthouse budget (LCP < 2.5 s on throttled profile); axe | ✅ | — |
| 10 | 03.1 | Supabase local config and JWT verification | 02.4 | Supabase CLI config (`enable_signup=false`, email+password only, TTLs); JWKS verification + auth adapter; migrations: `profiles`, `beta_invites`, `platform_roles`; verify constraints C1–C7, DM-A5 step-up mechanism, A-TM-02/03 | SAC-AUTH-01, SAC-AUTH-02, SAC-WEB-03, SAC-WEB-04, SAC-INV-03, SAC-SEC-02 (web image part), AC-STEP-05 (step-up evidence spike). **Stops if C1 or C2 fails, or if no step-up evidence meets PERMISSIONS SU-1…SU-4** | — | OAD-12 |
| 11 | 03.2 | Invite redemption, bootstrap, login/logout | 03.1 | API-002, API-003, API-004, API-005, API-090…092; TX-01, TX-01b, TX-02; invite page, check-email page, set-password via Supabase link, login/logout UI | SAC-INV-01, SAC-INV-02, SAC-INV-04, SAC-INV-05, SAC-INV-06, SAC-INV-08; PS-13 | ✅ | OAD-14 (local uses the Supabase CLI mail catcher; production SMTP before S2) |
| 12 | 03.3 | Recovery, session expiry, protected routes, step-up, invite cleanup | 03.2 | Password recovery; expiry handling; protected routes; step-up re-auth (⚑); reconciler + cleanup jobs (ARCH §7.1) | SAC-INV-07, SAC-WEB-05; AC-STEP-01…04, AC-STEP-06 (API-022, API-023); PS-15, PS-19…21 | ✅ | DM-A5 outcome from 03.1 |
| 13 | 03.4 | Auth security and regression tests | 03.3 | Negative-test suite for every enabled auth path; CI job against local Supabase | All SAC-AUTH-*, SAC-INV-* green in CI (LG-IAM-02 evidence) | — | — |
| 14 | 04.1 | Organizations and memberships | 03.4 | Migrations: `organizations`, `memberships`, `plan_entitlements`, `audit_events`, `idempotency_keys`, `outbox_events`; API-006, API-007, API-020…027; TX-03, TX-04 (authorization-suspension hook stubbed **off** until 05.4 and documented) | PS-06, PS-07; audit events for org/member actions | ✅ | — |
| 15 | 04.2 | RBAC engine, tenant isolation, cross-tenant suite | 04.1 | Permission catalogue in code = PERMISSIONS.md; per-route declarations; startup check; scoped repositories; generated cross-tenant suite (CI gate); RLS if OAD-01 = yes | SAC-TEN-01, SAC-TEN-02, SAC-TEN-03, SAC-TEN-04; PS-01…04, PS-08, PS-14 | — | **OAD-01**, DM-A1 |
| 16 | 04.3 | Invitations, team UI, audit trail | 04.2 | `org_invitations`; API-008, API-028…031; team page; audit log page | SAC-AUD-01, SAC-DB-01 | ✅ | TM-OD-02 (cap value; default 5 until decided) |
| 17 | 04.4 | Settings, notification preferences, org lifecycle | 04.3 | `notification_preferences`; API-009, API-010; settings pages; org suspend/delete behaviour | PS-16; regression of 04.1–04.3 | ✅ | — |
| 18 | 05.1 | Projects and hosts | 04.4 | Migrations: `projects`, `project_hosts`, `host_deny_list`; API-040…044, API-046…048; host normalizer; TX-05a | SAC-SSRF-01; host limit; duplicate checks | ✅ | — |
| 19 | 06.1 | Scan broker, signed jobs, scanner skeleton, result intake | 05.1 | Streams protocol + scanner ACL (ARCH §9.4); Ed25519 keys + `kid`; scope token mint/verify (API_CONTRACTS §9.1); supervisor/child skeleton (no target network I/O yet); result consumer with consistency checks (§9.4); migrations: `scan_jobs`, `scan_job_hosts`, `probe_jobs`, `platform_controls` | SAC-SCN-01, SAC-SCN-03, SAC-SCN-04, SAC-SCN-05, SAC-SCN-08; AC-RES-03 (intake duplicate detection); AC-LOCK-15 (single publish path) | — | OAD-07 (A unless ACL can't be verified) |
| 20 | 06.2a | Egress guard and DNS stub resolver | 06.1 | Blocked-set module; async stub resolver with completeness rules (RoE §8); resolve-validate-pin connector; peer check; proxy stripping | SAC-SSRF-02, SAC-SSRF-03, SAC-SSRF-04, SAC-SSRF-07, SAC-DNS-01…11 | — | OAD-11 |
| 21 | 06.2b | Scanner sandbox, network zones, fixtures | 06.2a | Hardened scanner image (non-root, read-only FS, no caps); compose network isolation; CI network sandbox; fixture servers (HTTP, TLS, DNS) | SAC-SCN-06, SAC-SSRF-06, SAC-SSRF-08 | — | — |
| 22 | 05.2 | DNS TXT verification | 06.2b | Migrations: `verification_challenges`, `verification_events`; API-049…051; TX-05, TX-06; probe dispatch through the scanner; verification UI | SAC-VER-01, SAC-DNS-12 (verification part) | ✅ | — |
| 23 | 05.3 | HTTPS file verification, expiry, revalidation, revocation | 05.2 | HTTPS method (no redirects); DEC-033 revalidation policy; expiry sweeper | SAC-VER-02, SAC-VER-03, SAC-DNS-12 (revalidation part) | ✅ | — |
| 24 | 05.4 | Scope, authorization, consent UX, RoE text | 05.3 | Migrations: `scope_versions`, `scan_authorizations`; API-052…056; TX-07, TX-08; TX-04 consenter-suspension hook **on** (DEC-034); consent screen with scope diff and RoE-1 text | SAC-AUTHZ-01, SAC-AUTHZ-02, SAC-AUTHZ-03; AC-STEP-06 (API-055); PS-05, PS-09, PS-18 | ✅ | — |
| 25 | 06.3 | HTTP/TLS collector, redirects, scan API, dispatch | 05.4 | Collector per RoE §2–§11; redirect semantics (ARCH §9.3); API-060…063; TX-09, TX-10, TX-16; host-lease protocol (DATA_MODEL §5.1) with migrations `host_scan_leases`, `scan_dispatch_attempts`; `scan_observations` | SAC-SCN-02, SAC-SCN-07, SAC-SSRF-05, SAC-ROE-04; AC-LOCK-01…07, AC-LOCK-12…14; AC-RES-05; fixture assertion for AC-LC-11 (no request to unauthorized host) | — | — |
| 26 | 06.4 | Cancellation, kill switch, timeouts, quotas, retries | 06.3 | RoE §14 model (supervisor polling, gates, SIGKILL, staleness); deadline sweeper; TX-14 quotas; Redis rate limits; API-093 (kill switch), API-094…095 (deny list), API-097 | SAC-ROE-01, SAC-ROE-02, SAC-ROE-03, SAC-ROE-05, SAC-CAN-01…10, SAC-RL-01; AC-LOCK-08…11, AC-LOCK-16, AC-LOCK-17 (`scanner_instances`, heartbeats, skew pause); AC-RES-06; AC-STEP-06 (API-093) | — | — |
| 27 | 07.1 | Rule framework, evidence schema, fixtures | 06.4 | `packages/rules`; migrations `rule_definitions`, `rule_sets`, `rule_set_members`, `scan_rule_status`, `scan_rule_results`; outcome enum; fixture-per-row of ARCH §9.3; determinism tests | Determinism + unknown-handling tests (ARCH §12) | — | — |
| 28 | 07.2 | HTTPS redirect, TLS, HSTS rules | 07.1 | `transport.https_redirect`, `tls.certificate`, `headers.hsts` (Core v1) | Fixture suite 100%; resolution semantics of ARCH §10.3 rows | — | — |
| 29 | 07.3 | CSP presence, X-Content-Type-Options, Referrer-Policy | 07.2 | Three Core v1 header rules | Fixture suite 100% | — | — |
| 30 | 07.4 | Cookie flags (Core) + Tier 2 preview scaffolding | 07.3 | `cookies.flags`; Tier 2 rules only in `preview` (mixed-content hints, Permissions-Policy, CSP basics, tech hints). **CORS observation is deferred**: it would need an `Origin` header or non-GET request, which RoE-1 forbids (needs RoE-2 + re-consent) | Fixture suite 100%; preview results excluded from score | — | OAD-10 |
| 31 | 07.5a | Fingerprints, lifecycle, history, exceptions | 07.4 | Migrations `findings`, `finding_occurrences`, `finding_history`, `finding_exceptions`, `finding_fp_reports`; TX-11 lifecycle part, TX-12, TX-15; API-096 (incident marking) | AC-LC-01…10, SAC-LC-06 (scan side); AC-RES-01, AC-RES-02, AC-RES-04, AC-RES-07…10 (DATA_MODEL §5.2); AC-STEP-06 (API-096) | — | TM-OD-05 |
| 32 | 07.5b | Coverage, score eligibility, score formula | 07.5a | `scan_scores`, `score_formulas`; eligibility per ADR-0011; API-045 backend | AC-SC-01, AC-SC-02, AC-SC-03 (API level) | — | **OD-01**, **OAD-06** |
| 33 | 08.1 | Dashboard overview and project detail | 07.5b | Overview, project page, current vs historical score UI (ARCH §11.1) | AC-SC-01…03 (UI); LG-HON-01 evidence part | ✅ | — |
| 34 | 08.2 | Scan launch, progress, history, partial/error states | 08.1 | Scan UI using API-060…064; incomplete/partial messaging, "add www" guidance | Playwright flows; no green state on partial/failed | ✅ | — |
| 35 | 08.3 | Findings explorer and evidence detail | 08.2 | API-066…068 UI; filters; escaped evidence rendering | SAC-WEB-02 | ✅ | — |
| 36 | 08.4 | Remediation lifecycle, exceptions, comparison | 08.3 | API-065, API-069…071 UI; closed-by-user vs resolved labels | AC-LC regression via UI flows | ✅ | — |
| 37 | 08.5 | Responsive/accessible UX and regression QA | 08.4 | Full UI pass; screenshot baseline update | axe; Playwright regression; LG-HON-01, LG-HON-03 evidence | ✅ | — |
| 38 | 09.1 | AI provider adapter, secrets, budget, quota | 08.5 | Adapter interface; provider from env; `ai_jobs`, `ai_cache`; TX-14 for AI | SAC-AI-06 | — | **OD-04** + cost approval, OAD-08 |
| 39 | 09.2 | Structured prompts, redaction, injection defense, validation | 09.1 | Prompt v1; redaction; untrusted-field wrapping; schema S-AI-OUT-1; ≥ 30 injection fixtures | SAC-AI-01, SAC-AI-03, SAC-AI-05 | — | — |
| 40 | 09.3 | Finding explanations UI | 09.2 | API-072, API-073 UI; caveats, confidence, references | SAC-AI-04, SAC-AI-07 | ✅ | — |
| 41 | 09.4 | AI grounding evaluation and regression | 09.3 | Live-provider eval run (cost-approved) | SAC-AI-02 (LG-APP-02 evidence) | — | — |
| 42 | 10.1 | Extension MV3 scaffold, side panel, permissions | 09.4 | Manifest (activeTab, sidePanel, storage, identity only); side panel shell | SAC-EXT-05 | ✅ | — |
| 43 | 10.2 | User-initiated passive page analysis | 10.1 | Local Level 1 observations, sanitization, "Local only" labels | SAC-EXT-04, SAC-EXT-06 | ✅ | — |
| 44 | 10.3 | Extension auth and verified project association | 10.2 | `extension_auth_codes`, `extension_token_families`, `extension_tokens`; API-080…083, API-086, API-087; TX-13; connect page | SAC-EXT-01; PS-10 | ✅ | **OAD-02** |
| 45 | 10.4 | Scoped sync, deep links, revocation | 10.3 | `extension_observations`; API-084, API-085, API-078; dashboard Level 2 view | SAC-EXT-02, SAC-EXT-03, SAC-LC-06 (extension side); PS-11, PS-12 | ✅ | — |
| 46 | 10.5 | Browser QA, Chrome Web Store checklist, privacy review | 10.4 | Compliance checklist; privacy disclosures | LG-APP-04 evidence | ✅ | — |
| 47 | 11.1 | Monitoring schedules, revalidation, limits | 10.5 | `monitoring_schedules`; API-057, API-058; scheduler with revalidation first | Schedule tests; PS-18 regression | ✅ | — |
| 48 | 11.2 | Notifications, deduplication, preferences | 11.1 | `notifications`; email adapter; dedup by fingerprint + state | Dedup tests | ✅ | — |
| 49 | 11.3 | PDF and JSON reports, templates, injection tests | 11.2 | `reports`; API-074…077; sandboxed renderer (no network) | SAC-RPT-01, SAC-RPT-02; PS-17 | ✅ | DM-OI-02 (file storage) |
| 50 | 11.4 | Full regression and coverage checks | 11.3 | Coverage report; regression of all phases | All previous SAC/AC green | ✅ | — |
| 51 | 12.1 | Entitlements, quota enforcement, usage page | 11.4 | `usage_counters` completed; API-032 UI; plan limits | SAC-RL-02 (sync limits), quota tests | ✅ | TM-OD-02, beta cohort size |
| 52 | 12.2 | Pricing UX, billing architecture, free-beta defaults | 12.1 | Architecture doc for billing (no live payments) | Review only | ✅ | — |
| 53 | 12.3 | Optional payment provider | 12.2 | **Only with explicit separate authorization** (contract §5.11); otherwise skipped and recorded | Webhook signature/idempotency tests if built | ✅ | Owner authorization + provider choice |
| 54 | 12.4 | Privacy, retention jobs, data export/deletion, onboarding review | 12.3 | Retention jobs per DATA_MODEL §7 (DEC-035); export/deletion flows; `retention_policies` | Retention job tests; LG-LEG-01 preparation | ✅ | Privacy/legal review of DEC-035 |
| 55 | 13.1 | Full E2E, cross-tenant, SSRF, auth, extension, AI tests on staging | 12.4 | Staging deploy on the chosen platform; live egress probes | SAC-NET-01, SAC-NET-02; AC-LOCK-10 on the platform; full suite (LG-SCN-01, LG-SCN-10, LG-SCN-11, LG-SCN-12, LG-APP-07, LG-IAM-04, LG-TEN-01, LG-NET-01 evidence). External dispatch stays disabled until LG-SCN-11 and LG-SCN-12 pass | ✅ | **OAD-03** (must be decided before this task; recommended earlier, before 06.2b) |
| 56 | 13.2 | Observability, alerts, backups, incident procedures | 13.1 | Alerts (LG-OPS-05), redaction test (LG-OPS-06), backup/restore drill (LG-OPS-04), runbooks incl. untrusted marking (LG-OPS-03) | LG-OPS-03…06, LG-OPS-09 evidence | — | — |
| 57 | 13.3 | Deployment runbooks, CI/CD, load tests, rollback, drills | 13.2 | Load test (global concurrency †); kill-switch, control-loss and rotation drills; least-privilege CI | LG-OPS-01, LG-OPS-02, LG-OPS-07, LG-OPS-08, LG-SUP-01…03, LG-SCN-02…05, LG-SCN-07, LG-IAM-01, LG-IAM-03, LG-IAM-05 evidence; **S1 internal-alpha go/no-go** | — | TM-OD-01 tuning |
| 58 | 13.4 | Independent review, beta cohort, release go/no-go | 13.3 | Independent review report; fixes; consent screen review; legal review | LG-SCN-06, LG-SCN-08, LG-SCN-09, LG-TEN-02, LG-LEG-01, LG-ABU-01, LG-ABU-02, LG-APP-01…06, LG-HON-01…03, LG-AUTHZ-01; **S2 go/no-go**; LG-LEG-02 tracked here but required only for public launch | ✅ | **OAD-13**, TM-OD-04, OD-05 (public launch only) |

## Decision schedule (from open items)

| Decision | Status | Must be decided before |
|---|---|---|
| OAD-04 Job framework, OAD-09 Python packaging, DM-OI-04 Postgres/UUIDv7 | open | 01.1a |
| OAD-12 API exposure (Bearer vs BFF) | open | 03.1 |
| OAD-14 Production SMTP | open | S2 (local dev uses the CLI mail catcher) |
| OAD-01 RLS, DM-A1 org-level roles | open / assumption | 04.2 |
| TM-OD-02 Team-invite cap, cohort size | open | 04.3 (default 5), 12.1 |
| OAD-07 Scanner transport, OAD-11 Resolver | open | 06.1 / 06.2a |
| OAD-03 Production platform | open | 13.1 at the latest; recommended before 06.2b so the sandbox design matches |
| OAD-10 Mixed-content depth | open | 07.4 |
| TM-OD-05 Second-instance confirmation | open | 07.5a |
| OD-01 Score formula, OAD-06 Accepted risk vs score | open | 07.5b |
| OD-04 AI provider/budget, OAD-08 AI mode | open | 09.1 |
| OAD-02 Extension auth, DM-A2 | open / assumption | 10.3 |
| DM-OI-02 Report storage | open | 11.3 |
| DM-OI-03 Trigger guards | open | 07.5a |
| TM-OD-01 Egress caps | open (initial values set) | 13.3 |
| OAD-13 Egress proxy (kept open, DEC-038) | open | 13.4 (S2) |
| TM-OD-03 Tier 2 body features | open | 07.4 |
| TM-OD-04 Independent review provider/budget | open | 13.4 |
| OD-03 FP threshold | open | 07.1 |
| OD-05 Name/trademark | open | Public launch |
| DM-A5 Step-up mechanism | assumption | 03.1 (verify) |
