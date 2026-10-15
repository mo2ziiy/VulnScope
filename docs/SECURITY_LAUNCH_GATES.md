# VulnScope — Security Launch Gates

| Field | Value |
|---|---|
| Status | **APPROVED v0.2 — Task 00.3 (approved by owner 2026-10-14)** · Alignment v0.3 (owner-authorized 2026-10-15, DEC-053): gates for AC-LOCK, AC-RES, AC-STEP and clock-skew monitoring added; nothing removed or weakened · Qualifications 2026-10-15 (DEC-056, DEC-057): LG-SCN-12 added; LG-SCN-10 and LG-OPS-09 clarified |
| Date | 2026-10-14 |
| Changelog | **v0.2:** LG-SCN-01 now includes SAC-DNS; LG-SCN-07 reworded (wrong-image control only); new LG-SCN-09 (explicit acceptance of R-RES-02 and R-RES-13); LG-OPS-01/02 aligned to RoE §14 (≤ 5 s / ≤ 6 s, SAC-CAN); new LG-OPS-08 (control-channel loss drill). **v0.1:** initial draft |
| Sources | PRD §11 guardrails · ARCHITECTURE §17–§19 · THREAT_MODEL.md §8–§10 · RULES_OF_ENGAGEMENT.md |
| Decided at | 13.4 go/no-go (external beta); internal alpha gate checked at the end of Phase 08 or later on owner request |

A gate is **passed** only with linked evidence (test run, report, config export, drill log). "Planned" or "mostly done" counts as **not passed**. **Design specifications never satisfy a gate**: every SAC/AC named in a gate must have been implemented as an executable test and **run**, with the run linked (CI job, log, or drill record) for the exact commit being released. Any failed **blocking** gate means no-go. There are no waivers for blocking gates; a non-blocking gate may be deferred only with a written owner decision in `DECISIONS.md`.

## Stages

| Stage | Who is scanned | Who uses it | Requires |
|---|---|---|---|
| **S0 Local / CI** | Fixture servers only (`SCANNER_ALLOW_EXTERNAL=false`) | Owner | SAC tests of completed phases green |
| **S1 Internal alpha** | Only hosts on the owner's allowlist file (owner-controlled) | Owner only | All `S1` gates below |
| **S2 External invite beta** | Any host with active verification + authorization | Invited cohort (≤ 50 orgs †) | All `S1` + `S2` gates below |

## Gates

Status for every gate today: **not started**.

### Scanner and network (LG-SCN, LG-NET)

| ID | Gate | Evidence | Stage | Blocking |
|---|---|---|---|---|
| LG-SCN-01 | All SAC-SSRF-01…08, SAC-DNS-01…12 and SAC-SCN-01…08 pass in CI | CI run link | S1 | Yes |
| LG-SCN-02 | Production platform enforces per-service egress policy (OAD-03 decided, policy exported) | Platform config export + review note | S1 | Yes |
| LG-NET-01 | Live probe from a deployed scanner: RFC1918, link-local, CGNAT, metadata (IPv4 + IPv6), Postgres, Redis-core, API, worker all **refused** (SAC-NET-01, SAC-NET-02) | Probe log | S1 | Yes |
| LG-SCN-03 | Scanner ACL verified on the production Redis version (SAC-SCN-08), or OAD-07 B adopted | Test log | S1 | Yes |
| LG-SCN-04 | RoE limits measured on staging against fixtures (SAC-ROE-01…05) | Test log with timings | S1 | Yes |
| LG-SCN-05 | Egress caps and flow-log alerting live (THREAT_MODEL §4.2); a test burst triggers an alert | Alert screenshot / log | S2 | Yes |
| LG-SCN-06 | OAD-13 decided (scope-enforcing egress proxy adopted, or explicitly rejected with owner sign-off and residual risk R-RES-01 accepted) | DECISIONS entry | S2 | Yes |
| LG-SCN-07 | Scanner image: non-root, read-only FS, no capabilities, digest pinned at deploy, platform-reported digest checked (SAC-SCN-05, -06). This is a **wrong-image** control; it does not authenticate observations (THREAT_MODEL §4.5) | Policy test + config | S1 | Yes |
| LG-SCN-09 | **Residual-risk acceptance** recorded in `DECISIONS.md`, signed by the owner: R-RES-02 (fabricated observations by a compromised scanner) and R-RES-13 (compromised supervisor ignores flags), listing the compensating controls verified in place: hardening + recycling (LG-SCN-07), anomaly and denied-egress alerts (LG-OPS-05), untrusted-marking runbook (LG-OPS-03), infrastructure kill drill (LG-OPS-02); TM-OD-05 decided | DECISIONS entry + evidence links | S2 | Yes |
| LG-SCN-10 | Host-lease protocol: AC-LOCK-01…09 and AC-LOCK-11…17 implemented and passing against real PostgreSQL + Redis with the fixture scanner (RoE §6 invariant: at most one running scan per host globally). AC-LOCK-14 must show that the signed token's `start_by`/`deadline_at` are validated **explicitly on every delivery and redelivery, including `XAUTOCLAIM`-claimed entries**; the 90 s claim idle time is recovery configuration only and isn't accepted as evidence (DEC-057) | CI run | S1 | Yes |
| LG-SCN-12 | **Clock-offset bound before external dispatch** (DEC-056): either (a) independently validated clock-offset bounds for the DB and scanner hosts (e.g. time-sync daemon offset **and** error-bound metrics from the platform, checked against a trusted reference, with alerting), or (b) a protocol demonstrated safe without the ±5 s assumption, with tests. One-way heartbeat lag (LG-OPS-09) **does not** satisfy this gate | Evidence report + test log | S1 | Yes |
| LG-SCN-11 | PostgreSQL failover safety on the **chosen platform** (OAD-03): AC-LOCK-10 executed there (promotion and PITR restore), and either the in-transaction identity guard (DATA_MODEL R-L12 b) or a demonstrated zero-data-loss configuration (R-L12 e). Until this passes, external dispatch stays disabled | Test log + platform config export | S1 | Yes |
| LG-SCN-08 | **Independent review** of scanner network boundary and egress guard; all high/critical findings fixed (Contract §6) | Review report | S2 | Yes |

### Identity, tenancy, authorization (LG-IAM, LG-TEN, LG-AUTHZ)

| ID | Gate | Evidence | Stage | Blocking |
|---|---|---|---|---|
| LG-IAM-01 | Supabase constraints C1–C7 verified on the **production** project (sign-up disabled, OAuth off, admin invite works, TTLs set) | Config export + negative-test log | S2 | Yes |
| LG-IAM-02 | SAC-AUTH-01, SAC-AUTH-02, SAC-INV-01…08 pass | CI run | S1 | Yes |
| LG-IAM-04 | Step-up: AC-STEP-01…04 and AC-STEP-06 implemented and passing; AC-STEP-05 executed against local Supabase with its result recorded (DM-A5 resolved, or ⚑ operations disabled) | CI run + 03.1 spike record | S1 | Yes |
| LG-IAM-05 | Step-up evidence re-verified on the **production** Supabase project: session refresh doesn't refresh the evidence; re-authentication does | Test log | S2 | Yes |
| LG-IAM-03 | Custom SMTP configured (OAD-14) and invite/confirmation emails deliver | Delivery test | S2 | Yes |
| LG-TEN-01 | Cross-tenant suite (SAC-TEN-01…04) passes with 0 failures | CI run | S1 | Yes |
| LG-TEN-02 | **Independent review** of tenant isolation; high/critical fixed (Contract §6) | Review report | S2 | Yes |
| LG-AUTHZ-01 | SAC-AUTHZ-01…03 and SAC-VER-01…03 pass | CI run | S1 | Yes |

### Application security (LG-APP)

| ID | Gate | Evidence | Stage | Blocking |
|---|---|---|---|---|
| LG-APP-01 | CSP and XSS tests (SAC-WEB-01…05) pass | E2E run | S1 | Yes |
| LG-APP-02 | AI injection eval (SAC-AI-01…07) passes thresholds | Eval report | S2 | Yes |
| LG-APP-03 | Report injection tests (SAC-RPT-01, -02) pass | Fixture run | S2 | Yes |
| LG-APP-04 | Extension: SAC-EXT-01…06 pass; Chrome Web Store compliance and privacy checklist (10.5) complete | Checklist + run | S2 (if extension ships) | Yes |
| LG-APP-06 | API/DB baseline: SAC-API-01, SAC-API-02, SAC-DB-01, SAC-AUD-01, SAC-RL-01, SAC-RL-02, SAC-SEC-02, SAC-RPT-02 pass; SAC-LC-06 passes as part of LG-HON-02 | CI run | S1 | Yes |
| LG-APP-07 | Scan-result application: AC-RES-01…10 implemented and passing (cancel/authorization races, duplicates, stale attempts, late, untrusted, rule-set mismatch) | CI run | S1 | Yes |
| LG-APP-05 | Lifecycle and score criteria AC-LC-01…11, AC-SC-01…03 pass | CI run | S1 | Yes |

### Supply chain and secrets (LG-SUP)

| ID | Gate | Evidence | Stage | Blocking |
|---|---|---|---|---|
| LG-SUP-01 | Dependency audit (pnpm, Python, base images): no unaddressed critical/high | Audit report | S1 | Yes |
| LG-SUP-02 | Secret scanning clean (SAC-SEC-01, -02) | CI run | S1 | Yes |
| LG-SUP-03 | CI uses least-privilege tokens; no production secrets available to PR builds | CI config review | S2 | Yes |

### Operations (LG-OPS)

| ID | Gate | Evidence | Stage | Blocking |
|---|---|---|---|---|
| LG-OPS-01 | Per-scan cancel: SAC-CAN-01…06, SAC-CAN-09, SAC-CAN-10 pass; network quiescence ≤ 5 s after the flag write in every phase | Timing log | S1 | Yes |
| LG-OPS-02 | **Kill-switch drill** on staging with concurrent scans: all scanner network activity quiescent ≤ 5 s after activation, no new job picked (SAC-CAN-07); scale-to-zero ≤ 5 min | Drill log | S2 | Yes |
| LG-OPS-08 | **Control-channel loss drill** on staging: scan broker made unreachable mid-scan → quiescence ≤ 6 s, no observations published, scans end `failed` (SAC-CAN-08) | Drill log | S2 | Yes |
| LG-OPS-03 | Incident runbooks: scanner compromise (including marking results `untrusted` and reverting resolutions), secret leak (service-role, signing, broker, DB), cross-tenant leak, abuse complaint | Runbook docs | S2 | Yes |
| LG-OPS-04 | Backup and restore drill for Postgres succeeds | Drill log | S2 | Yes |
| LG-OPS-05 | Monitoring and alerts: auth failures, `beta.not_invited`, denied egress, result rejections, acked-without-result, result anomalies (THREAT_MODEL §4.5), digest mismatch, control staleness, AI budget | Alert list + test triggers | S2 | Yes |
| LG-OPS-06 | Log redaction test: no tokens, cookies, challenge tokens, keys in logs | Test log | S1 | Yes |
| LG-OPS-09 | Clock-skew monitoring live on staging: scanner heartbeats, lag metrics, alerting; injected skew (> 5 s behind, > 5 s ahead, missing heartbeats) pauses dispatch (AC-LOCK-16, AC-LOCK-17 on staging). Heartbeat lag is an **operational signal**, not proof of synchronization; the bound itself is gated by LG-SCN-12 | Drill log + alert evidence | S1 | Yes |
| LG-OPS-07 | Secret rotation rehearsed once each: broker password, signing key (`kid`), service-role key | Drill log | S2 | No (deferrable with written decision) |

### Legal and abuse (LG-LEG, LG-ABU)

| ID | Gate | Evidence | Stage | Blocking |
|---|---|---|---|---|
| LG-LEG-01 | ToS, Privacy Policy, and RoE-1 reviewed by a qualified professional | Review note | S2 | Yes |
| LG-LEG-02 | Product name / trademark check (OD-05) | Note | Public launch (after beta) | No for S2 |
| LG-ABU-01 | Public `/scanner` page, abuse contact monitored, per-host kill tested (RoE §15) | Page URL + test | S2 | Yes |
| LG-ABU-02 | Consent screen reviewed: exact scope shown, nothing pre-checked, basis choice, RoE text version | UI review + screenshots | S2 | Yes |

### Product honesty guardrails (from PRD §11)

| ID | Gate | Evidence | Stage | Blocking |
|---|---|---|---|---|
| LG-HON-01 | 0 cases of partial/failed scans shown as clean or with a current score (AC-SC-01…03 + UI review) | Test + screenshots | S1 | Yes |
| LG-HON-02 | 0 code paths where extension data or AI changes findings/score (AC-LC-06 / SAC-LC-06) | Test | S1 | Yes |
| LG-HON-03 | Only Core v1 rules that passed the rule quality gate are `enabled`; others `preview` | Rule registry export | S1 | Yes |

## Internal alpha (S1) extra rule
External targets are limited to an **allowlist file** of owner-controlled hosts, checked at dispatch, in addition to verification and authorization. Removing it is part of the S2 go decision.

## Go / no-go record
At 13.4 the owner records in `DECISIONS.md`: date, stage, list of gates with evidence links, any deferred non-blocking gates with reasons, and the decision.
