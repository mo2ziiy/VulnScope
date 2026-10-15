# VulnScope — Acceptance Criteria and Traceability

| Field | Value |
|---|---|
| Status | **APPROVED — DESIGN LEVEL v0.3 — Task 00.4 (owner approval 2026-10-15, DEC-058)** |
| Date | 2026-10-15 |
| Purpose | Every requirement → where it's designed → which module enforces it → which test proves it → which gate needs it → which backlog task builds it |

Modules refer to the API modules (ARCHITECTURE §3) plus `scanner`, `rules`, `worker`, `web`, `extension`.

## 1. PRD functional requirements

| PRD | Requirement (short) | Designed in | Module(s) | Acceptance tests | Launch gate | Backlog |
|---|---|---|---|---|---|---|
| FR-01 | Findings only from deterministic, versioned rules with bounded evidence | ARCH §10, ADR-0010 | rules, worker | AC-LC-01…10, fixture suites | LG-HON-03 | 07.1–07.5a |
| FR-02 | Partial/failed/cancelled distinct; coverage always shown | ARCH §9.1, §11 | scans, web | AC-SC-01…03, SAC-CAN-08 | LG-HON-01 | 06.3, 07.5b, 08.2 |
| FR-03 | No scan without active verification **and** explicit authorization | ARCH §8, ADR-0008, ADR-0015 | verification, projects, scans | SAC-AUTHZ-01, SAC-VER-01…03 | LG-AUTHZ-01 | 05.2–05.4, 06.3 |
| FR-04 | Server-side org filtering; never trust client `org_id` | ADR-0005, DATA_MODEL §3 | authz, all repositories | SAC-TEN-01…04, PS-01…04 | LG-TEN-01, LG-TEN-02 | 04.2 |
| FR-05 | Roles + permissions matrix, deny by default | PERMISSIONS | authz | SAC-TEN-03, PS-06…09 | LG-TEN-01 | 04.2 |
| FR-06 | Destructive actions confirmed + audited | PERMISSIONS ⚑ §1.1, API §11 | audit, auth, web | SAC-AUD-01, AC-STEP-01…06, PS-15, PS-19…21 | LG-APP-06 | 03.1, 03.3, 04.3 |
| FR-07 | AI grounded in stored structured data; validated; untrusted content | ADR-0013 | ai, worker | SAC-AI-01…07 | LG-APP-02 | 09.1–09.4 |
| FR-08 | AI can't mark fixed; only verified re-scan | ARCH §10.2 | findings | AC-LC-06 / SAC-LC-06 | LG-HON-02 | 07.5a, 09.3 |
| FR-09 | Extension captures no secrets/history; no remote code | ADR-0012 | extension | SAC-EXT-03…06 | LG-APP-04 | 10.1–10.4 |
| FR-10 | Reports include scope, coverage, limitations, disclaimers | ARCH §15 | reports | SAC-RPT-01, SAC-RPT-02 | LG-APP-03 | 11.3 |
| FR-11 | Demo data only in labeled isolated demo mode | PRD | web | Review checklist per UI task | — | 01.3 onward |
| FR-12 | No dead UI controls | Contract §4 | web | VQA checklist per UI task | — | every ✅ VQA task |
| FR-13 | Sign-up requires invite | ADR-0014, ARCH §7.1 | auth, worker | SAC-INV-01…08 | LG-IAM-01, LG-IAM-02 | 03.1–03.4 |
| FR-14 | Score per §7 PRD, never without coverage | ADR-0011, ARCH §11.1 | scans, web | AC-SC-01…03 | LG-HON-01 | 07.5b, 08.1 |
| FR-15 | Extension data never changes findings/score | ADR-0012 | findings, extension | SAC-LC-06, SAC-EXT-02 | LG-HON-02 | 07.5a, 10.4 |
| FR-16 | Rules enabled only after quality gate | ARCH §12 | rules | Fixture + determinism + FP measurement | LG-HON-03 | 07.1–07.4 |

## 2. PRD non-functional requirements

| NFR | Verified by | Backlog |
|---|---|---|
| Safety (isolated scanner, egress) | SAC-SSRF-*, SAC-DNS-*, SAC-NET-*, LG-SCN-* | 06.1–06.4, 13.1 |
| Impact on targets (RoE) | SAC-ROE-*, SAC-CAN-* | 06.3, 06.4 |
| Security baseline (ASVS L2 reference) | SAC-WEB-*, SAC-API-*, LG-SUP-* | 01.1b, 03.x, 13.x |
| Auth | SAC-AUTH-*, SAC-INV-* | 03.1–03.4 |
| Privacy & retention | DATA_MODEL §7, retention tests | 12.4 |
| Performance (LCP, scan duration) | Lighthouse budget; RoE §7 measurement | 02.4, 06.4, 13.3 |
| Accessibility WCAG 2.2 AA | axe + manual VQA | 01.2–01.4, every ✅ VQA task |
| Responsiveness | VQA at 375 px / 1440 px | every ✅ VQA task |
| i18n / RTL-readiness (DEC-010) | String catalog + logical CSS lint rule | 01.2 onward |
| Reliability (job states, idempotency) | DATA_MODEL §5–§6 tests | 06.x, 07.5a |
| Observability | LG-OPS-05, LG-OPS-06 | 13.2 |
| Cost (no paid service without approval) | Decision schedule (BACKLOG) | 09.1, 11.3, 12.3, 13.x |

## 3. RoE-1 limits → enforcement → tests

| RoE section | Limit | Enforcement point | Tests | Backlog |
|---|---|---|---|---|
| §2–§3 | GET only; no cookies/auth/query/body | Scanner collector | SAC-ROE-04 | 06.3 |
| §4 | ≤ 5 hosts, ≤ 5 paths, host/path format | API normalizer + scope token | SAC-SSRF-01, scope validation tests | 05.1, 05.4 |
| §5 | Budgets (40 req, 120 DNS, 4 MiB, 5 hops) | Scope token + scanner + core consistency check | SAC-ROE-01, SAC-SCN-03 | 06.3, 06.4 |
| §6 | Serial per host, 500 ms gap, 1 scan/host, retries | Scanner + PostgreSQL host leases with fencing (DATA_MODEL §5.1) | SAC-ROE-02, SAC-ROE-05, AC-LOCK-01…17 (gates LG-SCN-10, LG-SCN-11, LG-OPS-09) | 06.3, 06.4, 13.1 |
| §7 | Phase timeouts, 180 s deadline | Scanner + deadline sweeper | SAC-SCN-07, SAC-ROE-01 | 06.3, 06.4 |
| §8 | DNS completeness, any-blocked rule, pinning | Egress guard + stub resolver | SAC-DNS-01…12, SAC-SSRF-02…04 | 06.2a, 05.2, 05.3 |
| §9 | TLS handling | Collector | TLS fixtures (07.2) | 06.3, 07.2 |
| §10 | Request headers | Collector | SAC-ROE-04 | 06.3 |
| §11 | Response caps, no bodies leave scanner | Collector + result schema | SAC-SCN-07, SAC-SCN-04 | 06.3 |
| §12 | Verification/authorization timing (DEC-033, DEC-034) | verification, projects | SAC-VER-01…03, SAC-AUTHZ-03 | 05.2–05.4 |
| §13 | Product rate limits/quotas | API + Redis + TX-14 | SAC-RL-01, SAC-RL-02, SAC-INV-07 | 03.3, 06.4, 12.1 |
| §14 | Cancel/kill ≤ 5 s, Redis loss ≤ 6 s | Supervisor + gates | SAC-CAN-01…10 | 06.4 |
| §15 | Abuse handling, deny list | API-094/095, `/scanner` page | LG-ABU-01 | 02.3, 06.4 |
| §16 | External scanning disabled locally/CI | Config + CI sandbox | SAC-SSRF-08 | 06.2b |
| §17 | Retention (DEC-035) | Retention jobs | Retention tests | 12.4 |

## 4. ADR → backlog

| ADR | Built in |
|---|---|
| 0001 Modular monolith | 01.1a, 01.1b |
| 0002 Stack | 01.1a, 01.2 |
| 0003 Supabase JWT | 03.1 |
| 0004 Bearer API | 03.1 |
| 0005 Tenant isolation | 04.2 |
| 0006 Two brokers / Streams | 01.1b, 06.1 |
| 0007 Scanner isolation (+E-01) | 06.2a, 06.2b, 13.1 |
| 0008 Verification via scanner | 05.2, 05.3 |
| 0009 Signed scope tokens | 06.1, 06.3 |
| 0010 Rule engine | 07.1–07.5a |
| 0011 Score eligibility | 07.5b, 08.1 |
| 0012 Extension trust levels | 10.2–10.4 |
| 0013 AI adapter | 09.1–09.4 |
| 0014 Invite-only | 03.1–03.3 |
| 0015 Control vs authorization | 05.4 |

## 5. Fail-closed behaviour → tests

Every row of THREAT_MODEL §9 has at least one test:

| Condition (THREAT_MODEL §9) | Test |
|---|---|
| JWT/JWKS unverifiable | SAC-AUTH-01 |
| Membership/permission lookup fails | 04.2 fault-injection test (DB down → 503) |
| Supabase admin failure during redemption | SAC-INV-05 / reconciler test (03.3) |
| Verification unknown/expired | SAC-VER-03 |
| Authorization missing/mismatch/outdated | SAC-AUTHZ-01 |
| Host leases can't be established | AC-LOCK-08, AC-LOCK-10, SAC-ROE-05 |
| Kill/cancel flags unreadable | SAC-CAN-08, SAC-CAN-10 |
| Cancel/kill during in-flight work | SAC-CAN-01…06, SAC-CAN-09 |
| Blocked address / bad DNS answer | SAC-DNS-01…11, SAC-SSRF-03 |
| TLS validation fails | 07.2 TLS fixtures |
| Budget/deadline reached | SAC-ROE-01 |
| Result invalid | SAC-SCN-03 |
| Observation truncated | AC-LC-09 |
| AI output invalid | SAC-AI-03 |
| Rate limiter unavailable | SAC-RL-01 (fault injection) |
| Report renderer error | SAC-RPT-01 |

## 6. Truthful lifecycle and score semantics (carried, not changed)

| Approved rule | Where enforced | Test |
|---|---|---|
| Absence ≠ fix (`subject_absent` never resolves) | worker TX-11 | AC-LC-03 |
| `not_applicable` resolves only with a declared reason | rules + worker | AC-LC-02, AC-LC-05 |
| No score for incomplete scans; historical labeled | scans, web | AC-SC-01…03 |
| Extension/AI never change state | findings module has no dependency | AC-LC-06 |
| Unauthorized redirect targets never requested | collector | AC-LC-11 |
| Observations are not authenticated (E-01, E-02) | docs, UI copy, reports | LG-SCN-09 acceptance |
| Results evaluated before a cancel/authorization change never land afterwards | worker TX-11 gates G4–G6 under the scan row lock | AC-RES-01, AC-RES-02 |
| Exactly-once application of an accepted result | `scan_observations` PK, `result_applied_at`, ack after commit | AC-RES-03, AC-RES-04, AC-RES-08 |
| Step-up needs fresh interactive-auth evidence, never `iat` | auth module | AC-STEP-01…06 |

## 7. 00.4 acceptance families → launch gates (all require executed tests)

| Family | What it protects | Defined in | Built in | Launch gate | Stage |
|---|---|---|---|---|---|
| AC-LOCK-01…09, 11…17 | At most one running scan per host globally; publish-once; fencing; clock-skew fail-closed | DATA_MODEL §5.1, §5.3 | 06.1, 06.3, 06.4 | LG-SCN-10 (+ LG-OPS-09 for AC-LOCK-16/17 on staging) | S1 |
| AC-LOCK-10 | Lost committed leases after PostgreSQL failover/restore | DATA_MODEL R-L12 | 06.4, 13.1 | LG-SCN-11 (on the chosen platform) | S1 |
| AC-RES-01…10 | Exactly-once, race-free result application; no late/stale/cancelled results | DATA_MODEL §5.2, §5.3 | 06.1, 06.3, 06.4, 07.5a | LG-APP-07 | S1 |
| AC-STEP-01…06 | Step-up needs fresh interactive-auth evidence, never `iat` | PERMISSIONS §1.1, §6.1 | 03.1, 03.3, 05.4, 06.4, 07.5a | LG-IAM-04 (S1), LG-IAM-05 (S2, production Supabase) | S1 / S2 |

