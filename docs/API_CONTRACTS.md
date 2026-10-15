# VulnScope — API Contracts

| Field | Value |
|---|---|
| Status | **APPROVED — DESIGN LEVEL v0.3 — Task 00.4 (owner approval 2026-10-15, DEC-058)** |
| Date | 2026-10-15 |
| Changelog | **v0.3:** `heartbeat` result message (clock-skew evidence, DATA_MODEL R-L17); `started` handling sets the cancel flag when late; publish rules reference R-L8/R-L15. **v0.2:** step-up convention (no `iat`); API-063 cancel semantics; scope token adds `attempt`, `lease_epochs`, `start_by`, `deadline_at` with new timing bounds; result messages carry `attempt`; §9.4 points to the DATA_MODEL §5.2 order; new failure/log codes. **v0.1:** initial draft |
| Sources | ARCHITECTURE §6–§14 · ADR-0003…0015 · RoE-1 · THREAT_MODEL · DATA_MODEL · PERMISSIONS |
| Scope | §1–§8 public REST API (`/api/v1`) · §9 internal scanner contracts (not exposed) · §10 error codes · §11 audit actions |

The OpenAPI document is generated from code (Pydantic) starting in 01.1 and must match this contract. Changes to this file after approval are versioned decisions.

---

## 1. Conventions

| Topic | Rule |
|---|---|
| Base | `https://<api-host>/api/v1` · JSON only (`application/json; charset=utf-8`) · UTF-8 |
| Auth | `Authorization: Bearer <token>`: Supabase access JWT (users) or extension access token (extension endpoints). **Cookies are ignored** (ADR-0004). CORS allowlist: web origin(s) + extension origin |
| Org context | Only from the path `/orgs/{org_id}/…` + active membership (PERMISSIONS §1). Any `org_id` in the body/query is ignored |
| IDs | UUID strings. Foreign or unknown IDs → `404` |
| Request ID | Server sets `X-Request-Id` on every response (client-supplied value accepted only if it's a UUID, otherwise replaced). It appears in errors and audit events |
| Idempotency | `Idempotency-Key` (1–100 chars, `[A-Za-z0-9_-]`) **required** where the table says *Idem = R*. Same key + same body → stored response; same key + different body → `409 idempotency.mismatch`; kept 24 h |
| Pagination | Cursor based: `?limit=` (1–100, default 25) and `?cursor=` (opaque). Response `{ "data": [...], "next_cursor": "…" or null }`. Sort order is fixed per endpoint (newest first unless stated) |
| Filtering | Only the documented query params; unknown params → `400 request.unknown_parameter` |
| Concurrency | Mutable resources return `ETag: "<version>"`; updates require `If-Match` → mismatch `409 conflict.version` |
| Timestamps | RFC 3339 UTC (`2026-10-14T12:00:00Z`) |
| Async work | `202 Accepted` + resource with `status`; poll the resource `GET` (SSE is a later enhancement for AI only, OAD-08) |
| Caching | Authenticated responses: `Cache-Control: private, no-store` (SAC-WEB-05) |
| Limits | Request body ≤ 64 KiB (extension sync ≤ 64 KiB, others ≤ 16 KiB unless stated). Strings have explicit max lengths; extra JSON fields → `400 request.invalid` |
| Rate limits | RoE §13 values; `429` with `Retry-After` |
| Step-up (⚑) | Endpoints marked ⚑ (API-022, API-023, API-055, API-093, API-096) require trustworthy evidence of **interactive authentication within 600 s** (PERMISSIONS §1.1, SU-1…SU-7). JWT `iat` is **not** evidence. No evidence / stale evidence → `401 auth.reauth_required`. The exact Supabase mechanism is verified in 03.1 (DM-A5, AC-STEP-05) |

### 1.1 Error format (all non-2xx)

```json
{
  "error": {
    "code": "scan.verification_expired",
    "message": "Human-readable English sentence.",
    "request_id": "0192f3c4-…",
    "details": { "host": "www.example.com" }
  }
}
```

`code` is stable and machine-readable (catalogue §10). `message` is never parsed by clients. `details` never contains other tenants' data, secrets, or stack traces (SAC-API-01).

### 1.2 Status codes used

`200` OK · `201` Created · `202` Accepted · `204` No Content · `400` invalid request · `401` unauthenticated / re-auth required · `403` authenticated but forbidden (only inside an org the caller belongs to) · `404` not found **or not visible** · `409` state conflict · `410` gone (invites, uniform) · `413` payload too large · `422` semantically invalid input (e.g. bad host) · `429` rate/quota limit · `503` dependency unavailable (fail closed).

## 2. Path shorthands

| Shorthand | Expands to |
|---|---|
| `{o}` | `/orgs/{org_id}` |
| `{p}` | `/orgs/{org_id}/projects/{project_id}` |

Columns: **Perm** = the single permission from PERMISSIONS.md · **Idem** = R required / — · **OK** = success status.

## 3. Public, identity and self-service

| ID | Method | Path | Perm | Idem | OK | Notes |
|---|---|---|---|---|---|---|
| API-001 | GET | `/health` | `public:none` | — | 200 | `{status:"ok"}`; no dependency details |
| API-002 | POST | `/beta-invites/redeem` | `public:none` | — | 202 | ADR-0014, TX-01. Body `{token}`. Uniform `410 invite.invalid_or_used`. Rate limits RoE §13 |
| API-003 | POST | `/me/bootstrap` | `self:bootstrap` | — | 201 | TX-02; `403 beta.not_invited` |
| API-004 | GET | `/me` | `self:read` | — | 200 | Profile + memberships summary |
| API-005 | PATCH | `/me` | `self:update` | — | 200 | `{display_name}` |
| API-006 | GET | `/me/orgs` | `self:read` | — | 200 | Paginated; only active memberships |
| API-007 | POST | `/orgs` | `self:create_org` | R | 201 | TX-03 |
| API-008 | POST | `/org-invitations/accept` | `self:accept_org_invitation` | — | 200 | Body `{token}`; email must match profile |
| API-009 | GET | `{o}/me/notification-preferences` | `notifications:manage_self` | — | 200 | |
| API-010 | PUT | `{o}/me/notification-preferences` | `notifications:manage_self` | — | 200 | |

## 4. Organizations, members, invitations, audit, usage

| ID | Method | Path | Perm | Idem | OK | Notes |
|---|---|---|---|---|---|---|
| API-020 | GET | `{o}` | `org:read` | — | 200 | |
| API-021 | PATCH | `{o}` | `org:update` | — | 200 | `If-Match` |
| API-022 | DELETE | `{o}` | `org:delete` | — | 202 | ⚑ step-up; body `{confirm_slug}` |
| API-023 | POST | `{o}/ownership-transfer` | `org:transfer_ownership` | — | 200 | ⚑; `{target_membership_id}` |
| API-024 | GET | `{o}/members` | `members:read` | — | 200 | Paginated; filters `role`, `status` |
| API-025 | PATCH | `{o}/members/{membership_id}` | `members:manage` | — | 200 | `{role}`; changes involving `admin` require `members:manage_admins` (checked in the service; returns 403) |
| API-026 | DELETE | `{o}/members/{membership_id}` | `members:manage` | — | 204 | Revoking an admin requires `members:manage_admins`; TX-04 |
| API-027 | POST | `{o}/members/me/leave` | `members:leave` | — | 204 | `409 org.last_owner` |
| API-028 | GET | `{o}/invitations` | `invitations:read` | — | 200 | |
| API-029 | POST | `{o}/invitations` | `invitations:create` | R | 201 | `{email, role}`; issues beta invite if needed |
| API-030 | DELETE | `{o}/invitations/{invitation_id}` | `invitations:revoke` | — | 204 | |
| API-031 | GET | `{o}/audit-events` | `audit:read` | — | 200 | Filters `action`, `actor_id`, `target_type`, `from`, `to` |
| API-032 | GET | `{o}/usage` | `usage:read` | — | 200 | Current period counters vs plan limits |

## 5. Projects, hosts, verification, scope, authorization

| ID | Method | Path | Perm | Idem | OK | Notes |
|---|---|---|---|---|---|---|
| API-040 | GET | `{o}/projects` | `projects:read` | — | 200 | Filters `status`; each item has `current_score` only (never historical, AC-SC-03) |
| API-041 | POST | `{o}/projects` | `projects:create` | R | 201 | `{name, primary_host}`; `422 host.invalid` per normalizer |
| API-042 | GET | `{p}` | `projects:read` | — | 200 | |
| API-043 | PATCH | `{p}` | `projects:update` | — | 200 | `If-Match` |
| API-044 | POST | `{p}/archive` | `projects:archive` | — | 200 | |
| API-045 | GET | `{p}/score` | `projects:read` | — | 200 | `{current_score, historical_score}` (ARCH §11.1) |
| API-046 | GET | `{p}/hosts` | `projects:read` | — | 200 | |
| API-047 | POST | `{p}/hosts` | `hosts:manage` | — | 201 | `{host}`; ≤ 5; deny-listed hosts → `422 host.denied` |
| API-048 | DELETE | `{p}/hosts/{host_id}` | `hosts:manage` | — | 204 | `409 scope.host_in_active_scope` |
| API-049 | POST | `{p}/hosts/{host_id}/challenges` | `verification:manage` | — | 201 | `{method}` → instructions with token shown **once** |
| API-050 | POST | `{p}/hosts/{host_id}/verification-checks` | `verification:manage` | R | 202 | Enqueues probe; RoE §13 limits |
| API-051 | GET | `{p}/hosts/{host_id}/verification` | `projects:read` | — | 200 | Status, expiry, last check, recent events |
| API-052 | GET | `{p}/scope` | `scope:read` | — | 200 | Active scope version + ETag |
| API-053 | PUT | `{p}/scope` | `scope:manage` | — | 200 | `If-Match`; TX-07; response includes `authorization_status: "suspended"` when consent is needed again |
| API-054 | GET | `{p}/authorizations` | `authorization:read` | — | 200 | History, newest first |
| API-055 | POST | `{p}/authorizations` | `authorization:consent` | R | 201 | ⚑; TX-08; body below |
| API-056 | POST | `{p}/authorizations/{authorization_id}/revoke` | `authorization:revoke` | — | 200 | Cancels running scan |
| API-057 | GET | `{p}/monitoring` | `projects:read` | — | 200 | |
| API-058 | PUT | `{p}/monitoring` | `monitoring:manage` | — | 200 | `{enabled, interval}`; min 24 h (RoE §13) |

## 6. Scans, findings, AI, reports, extension observations

| ID | Method | Path | Perm | Idem | OK | Notes |
|---|---|---|---|---|---|---|
| API-060 | POST | `{p}/scans` | `scans:create` | R | 202 | TX-09; body `{}` (scope is the active one); errors in §10 |
| API-061 | GET | `{p}/scans` | `scans:read` | — | 200 | Filters `status`, `from`, `to` |
| API-062 | GET | `{p}/scans/{scan_id}` | `scans:read` | — | 200 | Status, coverage, `score` (only if eligible), limitations |
| API-063 | POST | `{p}/scans/{scan_id}/cancel` | `scans:cancel` | — | 202 | TX-16. Non-terminal → `202` with `cancel_requested_at`; repeated cancel → same `202`; already terminal → `200` with the unchanged scan (no-op). The scan shows `cancelled` only after scanner confirmation or the deadline (DATA_MODEL §5.1 R-L6) |
| API-064 | GET | `{p}/scans/{scan_id}/rule-results` | `scans:read` | — | 200 | Filters `outcome`, `rule_id`, `tier`; includes `preview` flag |
| API-065 | GET | `{p}/scans/compare` | `scans:read` | — | 200 | `?base=&head=` same project; diff by fingerprint (ARCH §10) |
| API-066 | GET | `{o}/findings` | `findings:read` | — | 200 | Filters `project_id`, `state`, `severity`, `confidence`, `rule_id`; sort `severity`, `last_seen` |
| API-067 | GET | `{o}/findings/{finding_id}` | `findings:read` | — | 200 | Evidence, remediation, references, `needs_rescan` |
| API-068 | GET | `{o}/findings/{finding_id}/history` | `findings:read` | — | 200 | Transitions + occurrences |
| API-069 | POST | `{o}/findings/{finding_id}/exceptions` | `findings:accept_risk` | — | 201 | `type=accepted_risk`; `type=not_reproducible` is checked against `findings:close_not_reproducible` instead (service-level, same endpoint) |
| API-070 | POST | `{o}/findings/{finding_id}/exceptions/{exception_id}/revoke` | `findings:revoke_exception` | — | 200 | |
| API-071 | POST | `{o}/findings/{finding_id}/false-positive-reports` | `findings:report_fp` | — | 201 | `{note}` |
| API-072 | POST | `{o}/findings/{finding_id}/ai-explanations` | `ai:use` | R | 202 | TX-14 quota; cache hit → `200` with existing job |
| API-073 | GET | `{o}/findings/{finding_id}/ai-explanations/{job_id}` | `ai:read` | — | 200 | |
| API-074 | POST | `{p}/reports` | `reports:create` | R | 202 | `{scan_id, format}` |
| API-075 | GET | `{p}/reports` | `reports:read` | — | 200 | |
| API-076 | GET | `{p}/reports/{report_id}` | `reports:read` | — | 200 | |
| API-077 | POST | `{p}/reports/{report_id}/download-link` | `reports:download` | — | 201 | Signed URL valid ≤ 5 min, single member; audited |
| API-078 | GET | `{p}/extension-observations` | `extension_observations:read` | — | 200 | Labeled Level 2 |

The service-level secondary checks in API-025, API-026 and API-069 are listed in PERMISSIONS §2–§3 and are part of the 04.2 permission tests.

## 7. Extension endpoints (OAD-02 option A, assumption DM-A2)

| ID | Method | Path | Perm | Idem | OK | Notes |
|---|---|---|---|---|---|---|
| API-080 | POST | `/extension/authorizations` | `self:manage_extension_sessions` | — | 201 | Called by the web app's connect page with the user's JWT. Body `{code_challenge, code_challenge_method:"S256", redirect_uri, device_label}` → `{code}` (≤ 2 min) |
| API-081 | POST | `/extension/token` | `public:none` | — | 200 | `{code, code_verifier}` → `{access_token, refresh_token, expires_in: 900}` |
| API-082 | POST | `/extension/token/refresh` | `public:none` | — | 200 | TX-13; reuse → `401 extension.token_reuse` + family revoked |
| API-083 | POST | `/extension/token/revoke` | `extension:token_scope` | — | 204 | Revokes own family |
| API-084 | GET | `/extension/projects` | `extension:token_scope` | — | 200 | Requires scope `projects:read`. Returns the user's projects (across active memberships) with hosts that are `verified` **and** in an active authorized scope: `{org_id, project_id, name, hosts[], can_sync}` |
| API-085 | POST | `{p}/extension-observations` | `extension:sync` | — | 201 | Requires extension scope `sync:write`; body ≤ 64 KiB, schema S-EXTOBS-1; `409 sync.origin_not_authorized` (PS-12) |
| API-086 | GET | `/me/extension-sessions` | `self:manage_extension_sessions` | — | 200 | |
| API-087 | DELETE | `/me/extension-sessions/{family_id}` | `self:manage_extension_sessions` | — | 204 | |

## 8. Platform administration (`/admin`, never under an org)

| ID | Method | Path | Perm | Idem | OK | Notes |
|---|---|---|---|---|---|---|
| API-090 | POST | `/admin/beta-invites` | `platform:invites_manage` | R | 201 | `{email}` |
| API-091 | GET | `/admin/beta-invites` | `platform:invites_manage` | — | 200 | Status only, no tokens |
| API-092 | POST | `/admin/beta-invites/{invite_id}/revoke` | `platform:invites_manage` | — | 200 | |
| API-093 | PUT | `/admin/kill-switch` | `platform:kill_switch` | — | 200 | ⚑ `{enabled, reason}` |
| API-094 | POST | `/admin/host-deny-list` | `platform:deny_list` | — | 201 | `{host, reason, expires_at?}`; cancels running scans for the host |
| API-095 | DELETE | `/admin/host-deny-list/{host}` | `platform:deny_list` | — | 204 | |
| API-096 | POST | `/admin/scanner-incidents` | `platform:incident` | R | 202 | ⚑ `{instance_id, from, to}` → TX-15 |
| API-097 | GET | `/admin/health/queues` | `platform:health_read` | — | 200 | Depths, error rates; no tenant content |

## 8.1 Key request/response schemas (abbreviated; full schemas generated from Pydantic)

```text
Project        { id, name, status, hosts: Host[], current_score: Score|null, created_at }
Host           { id, host, is_primary, verification_status: unverified|verified|unknown|revoked,
                 verified_at|null, verification_expires_at|null, last_check_at|null }
Challenge      { id, method: dns_txt|https_file, expires_at,
                 instructions: { record_name?, record_value?, file_url?, file_content? } }   // token shown once
Scope          { version, scope_hash, entries: [{ host_id, host, https_port: 443,
                 http_redirect_probe: bool, paths: string[1..5] }] }
AuthorizationCreate { scope_version: int, scope_hash: string, basis: asset_owner|written_authorization_from_owner,
                 reference_note?: string<=200, roe_version: "RoE-1", acknowledge_roe: true }
Authorization  { id, scope_version, basis, roe_version, consented_by, consented_at, expires_at,
                 status, status_reason|null }
Scan           { id, status, trigger, queued_at, started_at|null, finished_at|null, failure_code|null,
                 coverage: { core_enabled, core_determinate, tier2_run }, score_eligible: bool,
                 score: Score|null, trust_status, limitations: string[] }
Score          { value, scan_id, completed_at, coverage, formula_version, rule_set_version }
ScoreView      { current_score: Score|null,
                 historical_score: (Score & { superseded_by_scan_id, superseded_reason })|null }
RuleResult     { rule_id, rule_version, subject_key, outcome, reason_code|null, severity|null,
                 confidence|null, evidence|null, preview: bool }
Finding        { id, project_id, rule_id, subject_key, state, severity, confidence, first_seen_scan_id,
                 last_seen_scan_id, resolved_in_scan_id|null, resolution_reason|null,
                 latest_evidence, needs_rescan, remediation, references[], exception|null }
ExceptionCreate { type: accepted_risk|not_reproducible, justification: string(20..2000), expires_at? }
AIExplanationRequest { framework: enum, user_context?: string<=500 }
AIExplanation  { id, status, framework, output|null: { plain, technical, impact, steps[], snippet,
                 caveats[], manual_validation[], confidence, reference_ids[] }, error_code|null }
ExtensionObservationCreate { origin, observed_at, extension_version,
                 headers: [{ name, value<=1024 }]<=100, cookies: [{ name, secure, httponly, samesite }]<=50,
                 mixed_content_hints: [{ scheme, host }]<=50, tls_summary? }   // no cookie values, no query strings
```

## 9. Internal contracts (core worker ↔ scanner; never exposed publicly)

### 9.1 Scope token (JWS compact, EdDSA, ADR-0009)

```text
header  { alg: "EdDSA", kid: "<key id>", typ: "vs-scope+jwt" }
payload {
  iss: "vulnscope-core", aud: "vulnscope-scanner",
  sub: "<scan_id or probe_id>", jti: "<job_nonce base64url>",
  iat, exp,                              // exp = deadline_at + 10 s; exp - iat = 250 s (must be <= 300 s)
  attempt: int,                          // = scan_jobs.current_attempt at dispatch
  start_by,                              // iat + 60 s: scanner must pick up before this, else `rejected`
  deadline_at,                           // start_by + 180 s: hard stop, checked at every gate (RoE §7, §14.3)
  lease_epochs: [int],                   // fencing tokens, one per host in sorted host order (DATA_MODEL §5.1)
  kind: "scan" | "probe",
  org_id, project_id,
  verification_event_ids: [uuid],        // scan: one per host; probe: []
  authorization_id: uuid | null,         // null only for probes
  rule_set_version, roe_version: "RoE-1",
  scan_ref,                              // value for the VulnScope-Scan-Ref header
  hosts: [{ host, https_port: 443, http_redirect_probe: bool, paths: [string] }],
  probe: null | { method: "dns_txt" | "https_file", host },
  budget: { http_requests: 40, http_per_host: 20, redirect_hops: 5, dns_queries: 120,
            bytes: 4194304, deadline_s: 180 }
}
```

Jobs reach `scan:jobs` **only** through the relay's publish path (DATA_MODEL §5.1 R-L8, R-L15): a committed `publish_started_at` marker precedes every `XADD`, and an attempt is published at most once. The scanner rejects the job (publishes `rejected`, makes **no** network request) if: signature invalid, `kid` unknown, `aud`/`iss` wrong, expired, `exp - iat > 300`, picked up after `start_by` on a **first** delivery (`start_window_missed`; claimed or re-read entries are never executed and never published as `rejected`, DATA_MODEL R-L14), `sub` ≠ message `scan_id`, `attempt` missing, budget above RoE maxima, any host not a valid hostname (SAC-SCN-01). The token authenticates the **job** only; it says nothing about the authenticity of returned observations (THREAT_MODEL §4.5).

### 9.2 Job message (`scan:jobs` stream entry)

```text
{ v: 1, type: "scan" | "probe", id: "<scan_id|probe_id>", attempt: int, token: "<JWS>" }
```

No other field is read. Everything the scanner needs is inside the signed token.

### 9.3 Result messages (`scan:results` stream entries)

```text
{ v: 1, type: "started" | "result" | "cancelled" | "control_unavailable" | "rejected" | "heartbeat",
  id: "<scan_id|probe_id>", attempt: int, job_nonce: "<base64url>", instance_id, image_digest_reported,
  sent_at, payload: <type-specific> }
```

| `type` | Payload | Core action |
|---|---|---|
| `started` | `{ picked_up_at }` | `queued → running` only for the current attempt + nonce, received (DB clock) before `start_by + 5 s` (DATA_MODEL §5.1 R-L9). Otherwise: attempt `rejected` **and** the scan's cancel flag is set, so the scanner stops within ≤ 5 s (RoE §14). Also feeds the R-L17 lag measurement |
| `heartbeat` | `{ uptime_ms, running_attempts: [{ id, attempt }] }`; envelope `id` = `instance_id`, `attempt` = 0 | Sent every 10 s by each supervisor. Core updates `scanner_instances` lag = DB receive time − `sent_at`; thresholds and fail-closed pause per DATA_MODEL R-L17. No change to scan state |
| `result` (scan) | Scan observation snapshot S-OBS-1 (≤ 512 KiB) | TX-11 per DATA_MODEL §5.2 (gates G1–G9; exactly-once application; `XACK` after commit) |
| `result` (probe) | `{ method, outcome_code, txt_records?: [string<=255]<=10, https?: { status, body_excerpt<=4096 } }` | TX-06 |
| `cancelled` | `{ reason: "user" | "kill" | "revoked" }` | → `cancelled` for the current attempt; R-L5 lease release |
| `control_unavailable` | `{}` | → `failed` `control_unavailable` |
| `rejected` | `{ reason_code }` | → `failed` `scope.invalid` + security log |

**S-OBS-1 (scan observation snapshot)**, abbreviated:

```text
{
  scan_id, job_nonce, roe_version, started_at, finished_at,
  budget_used: { http_requests, dns_queries, bytes, redirect_hops_max },
  dns: [{ host, outcome: ok|dns_answer_oversized|dns_incomplete|dns_ambiguous|dns_malformed
          |destination_blocked|host_not_found|transient, address_count, families_complete: bool }],
  tls: [{ host, outcome, version?, cipher?, ocsp_stapled?, chain?: [{ subject, issuer, not_before,
          not_after, san: [string]<=50 }]<=5, error_code? }],
  requests: [{ seq, url, host, scheme, port, method: "GET", address_used, started_at, duration_ms,
               outcome: ok|timeout|reset|refused|tls_invalid|blocked|out_of_scope|cancelled|budget,
               status?, headers?: [{ name, value<=8192, truncated }]<=100,
               set_cookies?: [{ name<=256, secure, httponly, samesite, path?, domain?, max_age_present }]<=50,
               body?: { content_type, bytes_read, truncated, decompress_aborted },
               location?: string<=2048, location_in_scope?: bool,
               observation_complete: bool }]<=40,
  http_first_hop: [{ host, status?, location_scheme?, location_host?, location_in_scope? }],
  errors: [{ code, host?, detail<=200 }]<=50
}
```

No cookie values, no request/response bodies, no query strings from `Location` beyond the 2048-char string (stored truncated, rendered escaped).

### 9.4 Core-side checks on every result (THREAT_MODEL §4.5: consistency, **not** authenticity)
1. Message `id` exists, `job_nonce` matches, state allows the transition, first `result` only.
2. JSON Schema S-OBS-1 strict (no extra fields), size caps.
3. Every `requests[].url` and `dns[].host` inside the token's scope; `out_of_scope` requests must have no `status` (they were not sent).
4. `budget_used` ≤ token budget; request count consistent with `requests[]`.
5. Timestamps inside `[dispatched_at, deadline_at]`.
6. `instance_id` and `image_digest_reported` recorded; platform-reported digest compared where available.
Failure of 1–5 → scan `failed` `result.invalid`, alert. None of these checks proves the observations are true. The exact order (validate → evaluate → lock → re-check gates → apply → ack) and the rejection outcomes for stale, duplicate, cancelled, revoked, late, untrusted and superseded results are defined in **DATA_MODEL §5.2**.

### 9.5 Outbox event types (internal)
`scan.dispatch`, `scan.cancel_flag`, `probe.dispatch`, `controls.mirror_kill_switch`, `notification.send`, `report.render`, `ai.generate`, `retention.run`, `extension.revoke_families`.

## 10. Error code catalogue

| Code | HTTP | Meaning |
|---|---|---|
| `request.invalid` / `request.unknown_parameter` / `request.too_large` | 400 / 400 / 413 | Validation |
| `auth.invalid_token` / `auth.reauth_required` | 401 | JWT invalid / step-up needed |
| `authz.forbidden` | 403 | Member lacks permission |
| `org.not_found` / `resource.not_found` | 404 | Not found or not visible |
| `org.last_owner` | 409 | Last-owner protection |
| `conflict.version` / `idempotency.mismatch` | 409 | Concurrency |
| `invite.invalid_or_used` | 410 | Uniform invite failure |
| `beta.not_invited` | 403 | Bootstrap without provisioned invite |
| `host.invalid` / `host.denied` / `host.limit` | 422 / 422 / 409 | Host normalizer, deny list, ≤ 5 |
| `verification.challenge_expired` / `verification.check_in_progress` | 409 | |
| `scope.invalid` / `scope.host_unverified` / `scope.host_in_active_scope` | 422 / 409 / 409 | |
| `authorization.scope_mismatch` / `authorization.roe_outdated` | 409 | Consent body doesn't match the current scope/RoE |
| `scan.authorization_required` | 409 | No active authorization or hash/RoE mismatch |
| `scan.verification_expired` / `scan.verification_unknown` | 409 | Host not usable (revalidation may be enqueued, `details.revalidation_probe_ids`) |
| `scan.already_running` | 409 | One active scan per project |
| `scan.kill_switch` / `scan.host_denied` | 503 / 409 | Platform controls |
| `quota.exceeded` / `rate.limited` | 429 | Plan quota / RoE §13 |
| `sync.origin_not_authorized` | 409 | PS-12 |
| `extension.token_reuse` | 401 | Family revoked |
| `ai.over_budget` / `ai.unavailable` | 429 / 503 | |
| `jobs.unavailable` / `dependency.unavailable` | 503 | Fail closed |

Scan-level `failure_code` values (not HTTP): `host_lock_unavailable`, `start_window_missed`, `result.late`, `result.untrusted`, `result.apply_error`, `evaluation_error`, `authorization_suspended`, `scope_changed`, `scanner.unavailable`, `control_unavailable`, `scope.invalid`, `result.invalid`, `target_unreachable`, `deadline_exceeded`, `initiator_revoked`, `authorization_revoked`, `verification_revoked`, `host_denied`, `kill_switch`.

## 11. Audit action catalogue (SAC-AUD-01)

`invite.issued`, `invite.redeemed`, `invite.revoked`, `profile.bootstrapped`, `org.created`, `org.updated`, `org.deleted`, `org.ownership_transferred`, `member.role_changed`, `member.revoked`, `member.left`, `invitation.created`, `invitation.revoked`, `invitation.accepted`, `project.created`, `project.archived`, `host.added`, `host.removed`, `verification.challenge_created`, `verification.succeeded`, `verification.failed`, `verification.revoked`, `scope.changed`, `authorization.consented`, `authorization.suspended`, `authorization.revoked`, `scan.requested`, `scan.cancelled`, `finding.exception_created`, `finding.exception_revoked`, `finding.fp_reported`, `report.created`, `report.downloaded`, `monitoring.changed`, `extension.session_created`, `extension.session_revoked`, `extension.token_reuse_detected`, `extension.observation_synced`, `platform.kill_switch_changed`, `platform.deny_list_changed`, `platform.incident_marked`, `security.beta_not_invited`, `security.result_rejected`, `security.stepup_denied`.

Result-handling log codes (not HTTP, not scan status): `result.duplicate`, `result.stale_attempt`, `result.unexpected_state`.
