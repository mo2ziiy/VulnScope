# VulnScope — Product Requirements Document (PRD)

| Field | Value |
|---|---|
| Status | **APPROVED v0.2 — Task 00.1 (approved by owner 2026-10-14)** |
| Version | 0.2 |
| Date | 2026-10-14 |
| Owner | Product owner (Muhammed) |
| Source of truth | `VulnScope_Claude_Code_Master_Prompt.md` (build contract) |
| Next docs | 00.2 Architecture/ADRs · 00.3 Threat model & RoE · 00.4 ERD, API contracts, backlog |

> Naming note: "VulnScope" is a working name. A trademark/domain check is required before any public launch (see §12, A-01).

### Changelog
- **v0.2 (2026-10-14):** Owner decisions applied — global English-first market, Supabase Auth, free invite-only beta, Solo Developer primary / Agency secondary, English reports, RTL-ready architecture. Added §7 Security posture score (not a guarantee), §8 Data-source trust levels (local / synced / verified cloud), §9 Rule coverage strategy (small reliable core first). Docker Desktop/WSL2 moved from assumption to environment check (§14).
- **v0.1 (2026-10-14):** Initial draft.

---

## 1. Problem statement

Small teams ship websites without a security engineer. When they want to know "is my site configured safely?", they face three gaps:

1. **Signal without context.** Free header/TLS graders output a letter grade and a list of missing headers. They don't explain *whether it matters for this site*, *how to fix it in my framework*, or *how to prove the fix worked*.
2. **Enterprise tools are heavy.** DAST platforms and pentest-grade scanners are priced, configured, and worded for security teams. They are noisy for a solo developer.
3. **No loop.** Findings live in a one-off report. There's no history, no "fixed / reopened" lifecycle, no re-scan comparison, and no way to move from "I'm looking at my site in the browser" to "this is tracked in my project".

## 2. Value proposition

**Discover. Understand. Fix. Verify.**

VulnScope gives developers **evidence-backed, low-impact security observations** about websites they own and have authorized, explains each one in developer language with **framework-specific remediation**, and lets them **re-scan to verify** the change — inside a multi-tenant workspace with an optional Chrome extension.

What we are explicitly **not**: a penetration test, a vulnerability guarantee, a compliance certification, or "the first" scanner. Copy uses the words **"observations"** and **"checks"**, never "we found all your vulnerabilities" or "your site is secure".

### 2.1 Differentiation (positioning hypothesis — to validate)

| Category | Examples (indicative, verify before marketing use) | Their strength | VulnScope angle |
|---|---|---|---|
| Free graders | Mozilla HTTP Observatory, SecurityHeaders.com, Qualys SSL Labs | Free, trusted, instant | Context + framework fixes + history + re-scan diff + workspace |
| Developer-focused DAST SaaS | Detectify, Probely, Intruder, Snyk DAST | Deep active testing, attack surface | Passive-only, low-impact, simpler, explainability-first, honest coverage |
| Self-run tools | OWASP ZAP, Nuclei, Burp Suite | Powerful, flexible | No setup, safe defaults, ownership verification, guided remediation |
| Browser extensions | Various header/tech-detect extensions | Convenient in-tab | Extension tied to a *verified* project, explicit sync, privacy-first |

Defensible combination: **ownership-verified scope + transparent deterministic rules + grounded AI explanations + fix-verify loop + extension-to-dashboard workflow.** None of these alone is unique; the combination and the honesty of the UX are the product.

## 3. Target market and users

**Market:** Global, English-first. No data-residency commitment during beta. Arabic/RTL is a future localization target, and the architecture must not block it (§10, NFR i18n).

| Priority | Persona | Description | Primary job-to-be-done | Beta fit |
|---|---|---|---|---|
| **Primary** | **P1 Solo developer** | Freelancer / indie hacker, ships Next.js, Laravel, WordPress, Django or static sites | "Tell me what's misconfigured, why it matters, and give me the exact fix for my stack — then prove it's fixed." | Free invite-only beta |
| **Secondary** | **P2 Agency** | 3–20 people, many client sites | "Track many client sites and hand clients a truthful report." | Free invite-only beta (team features) |
| Later | P3 Startup eng team | 2–15 engineers, no dedicated AppSec | "Catch security-header/TLS regressions after deploys." | Not a design target in MVP |
| Later | P4 Security team | AppSec engineers | "Low-noise passive baseline across many assets." | Out of MVP focus |

Design rule: **default UX, copy, onboarding and AI tone are optimized for P1.** P2 needs (multi-project overview, roles, client-ready reports) are supported without complicating the P1 first-run path.

Personas are hypotheses; validate with 5–10 interviews before Phase 02 copy is finalized (§11).

## 4. Scope

### 4.1 MVP (= Limited beta, Phases 01–13)

| Module | MVP includes |
|---|---|
| Public site | Landing, how-it-works, features, limitations, pricing preview, docs, privacy, terms (marked "pending legal review"), contact, beta invite request |
| Auth | **Supabase Auth**: sign up (invite-gated), email verification, login/logout, password recovery, session expiry; server-side JWT verification |
| Multi-tenancy | Organizations, roles owner/admin/analyst/viewer, invitations, revocation, audit log, deny-by-default RBAC |
| Projects | Add website, URL/origin normalization, duplicates, per-org limits |
| Ownership verification | DNS TXT and HTTPS `/.well-known/` challenge, expiry, replay resistance, revalidation, revocation |
| Authorized scope | Explicit, exact origins only; subdomains require their own authorization |
| Scans | Job lifecycle (queued/running/completed/partial/failed/cancelled), quotas, rate limits, deadlines, cancellation, idempotency |
| Passive rules | Delivered in tiers — **Core v1 first**, Tier 2 only after Core v1 meets its quality gate (§9) |
| Findings | Versioned rule IDs, severity + confidence, sanitized evidence, remediation, references, fingerprint, first/last seen, resolved/reopened, accepted-risk with justification, occurrences per scan |
| Posture score | Limited, transparent, rule-based score with coverage shown alongside — never a security guarantee (§7) |
| Comparison | Scan-to-scan diff (new / fixed / unchanged / reopened / not-checked) |
| AI assistant | Grounded explanation (plain + technical), framework-aware snippet with caveats, impact, manual validation steps, references, confidence; quota/budget; redaction |
| Chrome extension | Local current-tab observations; explicit, authorized sync to a verified project; dashboard deep links; sign-out/revoke (§8) |
| Monitoring | Opt-in scheduled low-impact checks for verified targets, dedup alerts, email abstraction, disable control |
| Reports | PDF + JSON **in English**, with scope, method, coverage, limitations, status, disclaimers |
| Plans | Entitlements & quotas, usage page, pricing preview, **free beta mode**; live billing only after separate approval (12.3) |
| Admin/support | Health/queue metrics, correlation IDs, safe audit logs, beta invite management, data export/deletion policy |

### 4.2 MVP exclusions (hard "no" for the MVP)

- **Active / intrusive testing:** exploitation, SQLi/XSS payloads, fuzzing, brute force, credential attacks, auth bypass attempts.
- **Network reconnaissance:** arbitrary port scanning, subdomain enumeration/brute force, mass or internet-wide scanning.
- **Aggressive crawling:** MVP scans a bounded set of URLs within the authorized origin (exact limit set in 00.3).
- **Authenticated scanning** (scanning behind the customer's login).
- **Scanning unverified targets**, including from the extension.
- **Autonomous fixes:** AI never edits code, opens PRs, or changes infrastructure.
- **Source code / dependency (SAST/SCA) scanning.**
- **Compliance or safety claims** (SOC 2, PCI, ISO "ready/certified"; "secure", "safe", "hack-proof").
- **Live payments** until Phase 12.3 is separately authorized.
- **Open public sign-up** (beta is invite-only until 13.4 go/no-go).
- **Arabic UI / Arabic reports** (future; architecture stays RTL-ready).
- Mobile apps, Firefox/Safari extensions, SSO/SAML, customer API keys, on-prem.

### 4.3 Post-MVP candidates (not committed)
Arabic localization (UI + reports), GitHub/GitLab issue export, Slack/webhook alerts, CI integration (fail build on regression), Firefox extension, SSO, authenticated passive scans, multi-region workers, additional rule tiers.

## 5. Core user journeys

**J1 — First value (P1, target ≤ 10 min from invite acceptance to first finding):**
Accept invite → sign up → verify email → create org (auto-suggested) → add `https://example.com` → choose DNS TXT or HTTPS file → copy instructions → "Check now" → verified → confirm exact authorized scope + rules-of-engagement checkbox → run scan → live progress → results with coverage summary, posture score with its limitations, and findings.

**J2 — Understand & fix:** open finding → see evidence (sanitized header/cert snippet), severity, confidence, why it matters *for this site* → "Explain with AI" → pick framework (Next.js / Nginx / Apache / Express / Laravel / Django / Cloudflare / Vercel…) → copy snippet with caveats → apply manually.

**J3 — Verify:** re-scan → comparison view shows finding moved to **fixed** (decided by deterministic rule, not the AI) → or **still present / reopened**.

**J4 — Agency team & report (P2):** invite analyst/viewer → manage several client projects → export English PDF/JSON report for a client, including scope, timestamps, coverage, and disclaimers.

**J5 — Extension (see §8 for trust levels):** install → open own site → click action → side panel shows **local observations** labeled "Local only — not uploaded, not verified" → (optional) sign in via browser-based flow → if the tab origin exactly matches a verified, authorized project, user may explicitly **sync** → dashboard shows them as *extension observations* → "Run verified scan" to get official findings.

**J6 — Monitoring:** enable weekly check on a verified project → ownership is revalidated before each run → alert only on new/reopened findings (deduplicated) → one-click disable.

**Unhappy paths that must be designed, not skipped:** invite expired/invalid; verification fails/expires; DNS record removed (verification revoked → scans and sync blocked); scan partial or failed (never shown as "clean", score not shown as complete); target unreachable; quota exhausted; AI unavailable/over budget; member removed mid-session; extension on unverified or non-matching origin.

## 6. Functional requirements (summary — detailed acceptance criteria land in 00.4)

| ID | Requirement |
|---|---|
| FR-01 | Every production finding is produced by a deterministic, versioned rule with bounded sanitized evidence. |
| FR-02 | Scan status `partial`/`failed`/`cancelled` is visually and semantically distinct from `completed`; coverage (checked / not checked / unknown per rule) is always shown. |
| FR-03 | No scan may run unless the project has an active, unexpired ownership verification **and** an explicit authorized scope accepted by an owner/admin. |
| FR-04 | All data access is filtered server-side by organization membership; client-supplied `org_id` is never trusted. |
| FR-05 | Roles: owner, admin, analyst, viewer. Permissions matrix defined in 00.4 before any code; deny by default. |
| FR-06 | Destructive actions require confirmation and are audit-logged. |
| FR-07 | AI output is grounded only in stored structured finding data plus user-approved context; outputs are schema-validated; website content is treated as untrusted. |
| FR-08 | AI cannot mark a finding fixed; only a verified cloud re-scan rule result can. |
| FR-09 | Extension captures no passwords, form values, cookie values, tokens, auth headers, or browsing history; no remote code / `eval`. |
| FR-10 | Reports include scope, method, timestamps, coverage, limitations, scan status, posture-score caveat, and a "not a penetration test" disclaimer. |
| FR-11 | Demo data exists only in an explicitly labeled, isolated demo mode. |
| FR-12 | Every UI control does something real or is not rendered. |
| FR-13 | Sign-up requires a valid, unexpired, single-use beta invite during beta. |
| FR-14 | Posture score follows §7; it is never displayed without its coverage and limitations. |
| FR-15 | Extension observations follow the trust levels in §8; they never create, resolve, or reopen official findings and never change the posture score. |
| FR-16 | A rule may be enabled in production only after passing the rule quality gate in §9. |

## 7. Security posture score — limited, not a guarantee

The product may show a **"Posture score"** for a project, but it is a narrow summary of *which of our passive checks passed*, not a measure of how secure the website is.

**What the score is:**
- A deterministic, documented function of rule results from the **latest verified cloud scan** only.
- Computed only over rules that were actually checked; `not_checked`/`unknown` rules are excluded and reported separately.
- Versioned (score formula version stored with each result) so changes are explainable over time.
- Explainable: every point gained or lost links to a specific rule result.

**What the score is not:**
- Not proof that the site is secure, safe, compliant, or free of vulnerabilities.
- Not comparable with other vendors' grades.
- Not a pentest result; it ignores application logic, authentication, server-side code, dependencies, and infrastructure we do not observe.

**Display rules:**
- Always shown with: coverage (`N of M checks run`), scan status, scan timestamp, rule-set version, and a one-line limitation: *"Based only on passive checks VulnScope ran. Not a guarantee of security."*
- **Partial / failed / cancelled scan →** no headline score; show "Incomplete — score unavailable" plus what was checked.
- No green "Secure"/"Safe" badges, shields, or 100% celebrations. Wording: "No issues found by the checks that ran."
- Same rules apply in PDF/JSON reports and in the extension.

Exact formula and weighting are defined in 07.5 and reviewed with the owner before implementation.

## 8. Data-source trust levels — local, synced, verified

VulnScope handles three kinds of security data. They are stored, labeled, and trusted differently, and the UI must never blur them.

| Level | 1. Local extension observation | 2. Authorized synchronization | 3. Verified cloud scan |
|---|---|---|---|
| **What it is** | What the extension saw in the user's current tab after the user clicked the action | Level-1 observations the user explicitly chose to upload to a project | Deterministic checks run by the isolated scanner worker |
| **Who triggers** | User click on current tab (activeTab) | User click "Sync to project", per sync | Owner/admin/analyst (per RBAC) or opted-in schedule |
| **Preconditions** | None beyond install | Signed in · project has active ownership verification · tab origin **exactly** matches the project's authorized scope · user has sync permission | Active verification + explicit authorized scope + quotas |
| **Where data lives** | Browser only, short retention, user can clear | Server, tied to org + project, labeled `source: extension` | Server, scan results + findings lifecycle |
| **Visible as** | "Local only — not uploaded, not verified" | "Extension observation — from your browser on {date}" | Official findings with scan ID, coverage, score |
| **Affects findings lifecycle?** | No | **No** (may be shown next to findings as supporting context) | **Yes** — the only source that creates/resolves/reopens findings |
| **Affects posture score?** | No | No | Yes (§7) |
| **Appears in reports?** | No | Optional appendix, clearly labeled | Yes |
| **Proves ownership?** | **No** — opening a tab is not proof | No — relies on existing verification | Requires verification; does not create it |

Rules:
- If verification is revoked or expires, sync is blocked and the extension says why.
- The extension never sends data to the cloud without an explicit user action.
- From a synced observation, the user can click "Run verified scan" to get official results.
- Exact sanitized fields and retention periods are defined in 00.3 / 10.2.

## 9. Rule coverage strategy — small, reliable core first

Trust beats breadth. A few checks that are always correct are worth more than many noisy ones. Coverage expands only when the current tier is reliable.

**Core v1 (first to production, Phase 07.2–07.4):**

| Rule area | Observes |
|---|---|
| HTTPS availability & redirect | HTTP→HTTPS redirect on the authorized origin |
| TLS certificate | Validity, hostname match, expiry window, chain trust |
| HSTS | Presence and basic directive sanity (`max-age`, `includeSubDomains` noted, not demanded) |
| CSP presence | Present / absent / report-only (no deep policy analysis yet) |
| X-Content-Type-Options | `nosniff` present |
| Referrer-Policy | Present and value class |
| Cookie flags | `Secure`, `HttpOnly`, `SameSite` on observed `Set-Cookie` (names only, never values) |

**Tier 2 (enabled only after Core v1 passes its gate):** CSP basic misconfigurations (`unsafe-inline`, wildcards), Permissions-Policy, mixed-content indicators, bounded CORS observations, technology disclosure hints.

**Rule quality gate (every rule, every tier):**
1. Versioned rule ID, documented rationale, severity and confidence logic.
2. Local fixtures covering positive, negative, edge, and `unknown` cases; tests pass in CI without external network.
3. Explicit `not_checked` / `unknown` outcomes — never silently "pass".
4. Contextual remediation text + references reviewed.
5. Known limitations documented and shown in the UI.
6. Measured false-positive rate on owner-authorized real sites is acceptable before enabling (threshold set in 00.4).

Tier 2 rules may run in a "preview" state (labeled, excluded from the score) before full enablement.

## 10. Non-functional requirements

| Area | Requirement (initial targets; refine in 00.2/00.3) |
|---|---|
| **Safety** | Scanner runs in an isolated worker with network-level egress restrictions; blocks private/loopback/link-local/reserved/metadata IPv4+IPv6; re-validates every resolved address, redirect, and retry; fails closed. CI never scans external hosts. |
| **Impact on targets** | Low-impact: bounded request count per scan, bounded concurrency per target, timeouts, identifiable User-Agent, honors kill switch. Exact numbers set in 00.3 RoE. |
| **Security** | OWASP ASVS L2 as reference baseline; CSRF/XSS protection, strict CSP on our own app, secure cookies, secret rotation, logging redaction, dependency pinning + audit, SAST in CI. |
| **Auth** | Supabase Auth; API verifies JWT issuer, audience, signature and handles key rotation server-side; profiles and memberships live in our Postgres. Local development uses the Supabase CLI (free). |
| **Privacy** | Don't store full response bodies; evidence truncated and redacted; retention limits; data export & deletion; extension privacy-first. |
| **Performance** | Web: LCP < 2.5 s on 4G mid-range for public pages; app interactions < 200 ms perceived; typical passive scan of a single origin completes < 2 min (target, to be measured). |
| **Accessibility** | WCAG 2.2 AA: keyboard navigation, visible focus, contrast in dark & light themes, semantic forms, reduced-motion support. |
| **Responsiveness** | Mobile (≥ 360 px), tablet, desktop are first-class. |
| **i18n / RTL-readiness** | MVP UI and reports in English only. Must not block Arabic later: all user-facing strings externalized (no hard-coded copy in components), `lang`/`dir` set at the document root, CSS logical properties (`ms-`/`me-`, `start`/`end`) instead of left/right, direction-aware icons, locale-aware date/number formatting, fonts chosen with Arabic-capable fallbacks, report templates parameterized by locale. |
| **Reliability** | Explicit job states, idempotency keys for expensive actions, retries with backoff, health checks, correlation IDs. Beta target 99.5% web availability (no SLA). |
| **Observability** | Structured logs (redacted), request IDs, queue metrics, error tracking. |
| **Maintainability** | TypeScript strict, Python typed (Pydantic v2), migrations, lockfiles, reproducible local dev via Docker Compose, docs kept current. |
| **Cost** | Local/free development path first; no paid service without owner approval; per-org AI budget caps; Supabase free tier during beta. |

## 11. Success metrics (beta)

| Type | Metric | Beta target (hypothesis) |
|---|---|---|
| Activation | Invite accepted → verified project | ≥ 50% |
| Time-to-value | Invite accepted → first completed scan (median) | ≤ 10 min |
| Core value | Users who resolve ≥ 1 finding and confirm via re-scan within 14 days | ≥ 25% of activated |
| AI usefulness | "Explanation helpful" thumbs-up rate | ≥ 70% |
| Trust | Findings reported as false positive by users | ≤ 5% of findings |
| Retention | Activated orgs returning in week 4 | ≥ 30% |
| Safety (guardrail) | Scans against unverified/unauthorized targets | **0** |
| Safety (guardrail) | Cross-tenant data access incidents | **0** |
| Safety (guardrail) | Abuse complaints from scanned third parties | **0** |
| Quality (guardrail) | Partial/failed scans displayed as clean or with a headline score | **0** |
| Quality (guardrail) | Extension observations altering official findings or score | **0** |

Guardrail metrics are launch blockers, not goals.

**Validation plan (before Phase 02 copy freeze):** 5–10 interviews (mostly solo devs, some agencies); test the tagline on a landing draft; run free graders on 10 sites the owner owns/is authorized for and note what they fail to explain.

## 12. Product risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | **Scanner abused against third-party sites** | Med | Critical | Ownership verification + explicit scope + revalidation + rate limits + abuse detection + kill switch + invite-only beta |
| R-02 | **SSRF / internal network access via scanner** | Med | Critical | Isolated worker, network egress policy, per-connection IP validation, CI fixture-only tests, independent review |
| R-03 | **Cross-tenant data leak** | Med | Critical | Server-side tenant filtering, RBAC tests, cross-tenant E2E suite |
| R-04 | **"Commodity" perception** — free graders already show headers | High | High | Lead with context, framework fixes, verify loop; validate with interviews |
| R-05 | **False confidence** — users read a good score or "no findings" as "secure" | High | High | §7 score rules; coverage always visible; partial ≠ clean; no "secure" badges; disclaimers in UI and reports |
| R-06 | **AI hallucination / prompt injection from website content** | Med | High | Grounded structured input, schema validation, untrusted-content handling, caveats, deterministic re-scan for verification |
| R-07 | **Noise / false positives** erode trust | Med | High | §9 small core + quality gate; confidence field; accepted-risk workflow; FP feedback |
| R-08 | **Legal/regulatory** (unauthorized-scan laws across jurisdictions, GDPR, trademark) | Med | High | ToS + RoE, consent records, legal review before public launch, name check |
| R-09 | **Chrome Web Store rejection** (permissions, privacy) | Med | Med | Minimal permissions, activeTab, clear privacy policy, compliance checklist (10.5) |
| R-10 | **AI cost overrun** | Med | Med | Per-org quotas, budget caps, caching of explanations per rule+context |
| R-11 | **Scope creep / solo-builder capacity** | High | High | Micro-task approval gates; strict MVP exclusions; tiered rule rollout |
| R-12 | **Auth provider lock-in or outage** (Supabase) | Low | Med | Server-side JWT verification behind an auth adapter; identity data mirrored in our own `profiles`/`memberships` |
| R-13 | **Confusing extension data with verified results** | Med | High | §8 trust levels, distinct labels, no lifecycle/score impact from extension data |
| R-14 | **Local environment blocks progress** (Docker/WSL2 on Windows) | Med | Med | Environment check in 01.1 before any infra work (§14) |

## 13. Explicit assumptions and confirmed decisions

| ID | Item | Status |
|---|---|---|
| A-01 | "VulnScope" stays a working name; trademark/domain check before public launch. | Assumed |
| A-02 | Market is **global, English-first**; no data-residency commitment in beta. | **Confirmed by owner** (DEC-007) |
| A-03 | Beta is **free**; pricing page is a preview only. | **Confirmed by owner** (DEC-004) |
| A-04 | Owner is the sole developer initially; work proceeds task-by-task with Claude Code. | Assumed |
| A-05 | **Supabase Auth** is the initial auth provider. | **Confirmed by owner** (DEC-008) |
| A-06 | AI provider is configurable; initial default provider decided in 09.1 with cost approval. | Assumed |
| A-07 | MVP UI and reports in **English**; architecture **RTL-ready** for future Arabic. | **Confirmed by owner** (DEC-005, DEC-010) |
| A-08 | Only Chrome (Chromium-based) extension in MVP. | Assumed (contract) |
| A-10 | Beta is **invite-only** until 13.4 go/no-go. | **Confirmed by owner** (DEC-004) |
| A-11 | Legal pages are placeholders marked "pending legal review" until professionally reviewed. | Assumed (contract) |
| A-12 | Scans target only the exact authorized origin(s); bounded URL set, no general crawling. | Assumed (contract) |
| A-13 | Primary persona Solo Developer, secondary Agency. | **Confirmed by owner** (DEC-009) |

(A-09 was removed as an assumption — see §14.)

## 14. Environment checks (verified, not assumed)

These are checked at the start of **Task 01.1** before any tooling is installed. Results are recorded in `docs/PROJECT_STATE.md`. If a check fails, 01.1 stops and offers a documented alternative instead of guessing.

| ID | Check | How (read-only) | If missing |
|---|---|---|---|
| ENV-01 | Docker Desktop installed and engine running | `docker version`, `docker info` | Owner installs Docker Desktop, or we document an alternative |
| ENV-02 | WSL2 available and Docker uses the WSL2 backend | `wsl --status`, `wsl -l -v` | Owner enables WSL2 |
| ENV-03 | Docker Compose v2 | `docker compose version` | Comes with Docker Desktop |
| ENV-04 | Node.js LTS + pnpm | `node -v`, `pnpm -v` | Install via official installers/corepack (owner approval) |
| ENV-05 | Python 3.12+ and a package manager (uv or pip) | `python --version` | Install (owner approval) |
| ENV-06 | Git | `git --version` | Install |
| ENV-07 | Supabase CLI (local auth) | `supabase --version` | Needed by 03.1, not 01.1 |

## 15. Open decisions

| ID | Decision | Needed by | Recommendation |
|---|---|---|---|
| OD-01 | Posture score formula & weighting | 07.5 (draft in 00.4) | Simple, documented, pass-ratio over checked rules weighted by severity |
| OD-02 | Retention period for local extension data and for synced observations | 00.3 | Local: until tab closed / max 24 h; synced: same as scan evidence |
| OD-03 | False-positive threshold that gates enabling a rule | 00.4 | Zero known FPs on fixture suite + owner-authorized sample sites |
| OD-04 | Initial AI provider and monthly beta budget | 09.1 | Decide with cost estimate at that time |
| OD-05 | Final product name / trademark check | Before public launch | Defer |

## 16. Out-of-scope for this document
Architecture, trust boundaries, ADRs (→ 00.2); threat model, abuse cases, rules of engagement, launch gates (→ 00.3); ERD, API contracts, permissions matrix, backlog (→ 00.4).
