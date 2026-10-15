# VulnScope — Permissions Matrix

| Field | Value |
|---|---|
| Status | **APPROVED — DESIGN LEVEL v0.2 — Task 00.4 (owner approval 2026-10-15, DEC-058)** |
| Date | 2026-10-15 |
| Changelog | **v0.2:** §1.5 step-up rewritten (trustworthy fresh-authentication evidence; `iat` explicitly rejected; fail closed); §1.1 step-up rules added; PS-15 split into PS-15/19/20/21; AC-STEP-01…06 added. **v0.1:** initial draft |
| Sources | PRD FR-04, FR-05, FR-06 · ARCHITECTURE §7, §8.4 · ADR-0005, ADR-0012, ADR-0014, ADR-0015 · THREAT_MODEL §4.7 · DEC-034 |
| Used by | `API_CONTRACTS.md` (every endpoint names exactly one permission from this file) |

## 1. Principles
1. **Deny by default.** A permission not listed for a role is denied. A route without a declared permission makes the app fail at startup (SAC-TEN-03).
2. **Roles are org-level** (`owner`, `admin`, `analyst`, `viewer`). Project actions follow the org role (DATA_MODEL DM-A1; per-project roles are post-MVP).
3. **Org context only from the URL path** plus an *active* membership lookup on every request. Nothing is cached across requests, so revocation takes effect on the next request (ADR-0005).
4. **Platform roles are separate.** `platform_admin` grants platform operations only; it gives **no** read access to tenant data (tenant-safe troubleshooting through metadata, IDs and audit summaries only).
5. **Sensitive operations (⚑) need step-up:** trustworthy evidence that the user **interactively authenticated within the last 10 minutes** (§1.1). If freshness can't be established, the request fails closed with `401 auth.reauth_required`.
6. **Background jobs re-check** that the initiator still holds the permission at execution time (scheduled scans are system-initiated but still require active verification + authorization).

Legend: ✅ allowed · — denied · ◐ allowed with the condition in the Notes column.

### 1.1 Step-up rules (⚑)

| ID | Rule |
|---|---|
| SU-1 | Accepted evidence is an **interactive authentication event** (password sign-in, or an explicit re-authentication) with a timestamp issued by the identity provider and carried in the verified JWT. |
| SU-2 | **JWT issuance time (`iat`) is not evidence.** Supabase re-issues access tokens on every refresh, so a fresh `iat` says nothing about when the user last proved their identity. `exp`, `nbf` and session age aren't evidence either. |
| SU-3 | Freshness = `now − auth_event_time ≤ 600 s`, using the server clock, with ≤ 5 s tolerance for skew. |
| SU-4 | Missing, unparseable, ambiguous, or future-dated evidence → `401 auth.reauth_required`. Never fall back to `iat` or allow the operation. |
| SU-5 | The web client responds to `auth.reauth_required` by asking the user to sign in again (through Supabase, never by sending the password to our API), then retries with the new token. |
| SU-6 | The exact Supabase evidence (for example per-method timestamps in the `amr` claim, or a re-authentication flow that updates them) is **verified in 03.1** (DM-A5). Requirement for that verification: refreshing a session must **not** refresh the evidence. If 03.1 can't find evidence that meets SU-1…SU-4, ⚑ operations stay unavailable (fail closed) and 03.1 stops for an owner decision. |
| SU-7 | Every ⚑ operation records the evidence timestamp used in its audit event. |

## 2. Organization-level permissions

| Permission | Owner | Admin | Analyst | Viewer | Notes |
|---|---|---|---|---|---|
| `org:read` | ✅ | ✅ | ✅ | ✅ | Org name, plan, own role |
| `org:update` | ✅ | ✅ | — | — | Name, slug |
| `org:delete` | ✅ | — | — | — | ⚑ Soft delete; typed confirmation; cancels running scans |
| `org:transfer_ownership` | ✅ | — | — | — | ⚑ Target must be an active admin |
| `members:read` | ✅ | ✅ | ✅ | ✅ | Names, roles, status (emails masked for analyst/viewer) |
| `members:manage` | ✅ | ◐ | — | — | Admin: may change roles among analyst/viewer and revoke analyst/viewer. Never self-escalates |
| `members:manage_admins` | ✅ | — | — | — | Grant/revoke admin, revoke admins; last-owner protection |
| `members:leave` | ◐ | ✅ | ✅ | ✅ | Owner can leave only if another active owner exists |
| `invitations:read` | ✅ | ✅ | — | — | |
| `invitations:create` | ✅ | ◐ | — | — | Admin: may invite analyst/viewer only. Owner: up to admin. Team invites capped per org (TM-OD-02, open) |
| `invitations:revoke` | ✅ | ✅ | — | — | |
| `audit:read` | ✅ | ✅ | — | — | |
| `usage:read` | ✅ | ✅ | ✅ | — | |
| `notifications:manage_self` | ✅ | ✅ | ✅ | ✅ | Own preferences only |

## 3. Project-level permissions

| Permission | Owner | Admin | Analyst | Viewer | Notes |
|---|---|---|---|---|---|
| `projects:read` | ✅ | ✅ | ✅ | ✅ | Includes current/historical score views |
| `projects:create` | ✅ | ✅ | — | — | Per-org project limit (plan) |
| `projects:update` | ✅ | ✅ | — | — | Name |
| `projects:archive` | ✅ | ✅ | — | — | Confirmation; disables monitoring; revokes authorization |
| `hosts:manage` | ✅ | ✅ | — | — | Add/remove hosts (≤ 5); removal from the active scope requires a scope change |
| `verification:manage` | ✅ | ✅ | ✅ | — | Create challenges, run checks |
| `scope:read` | ✅ | ✅ | ✅ | ✅ | |
| `scope:manage` | ✅ | ✅ | — | — | New scope version suspends the active authorization (TX-07) |
| `authorization:read` | ✅ | ✅ | ✅ | ✅ | |
| `authorization:consent` | ✅ | ✅ | — | — | ⚑ RoE acknowledgment, basis choice (ADR-0015) |
| `authorization:revoke` | ✅ | ✅ | — | — | Cancels running scans |
| `scans:read` | ✅ | ✅ | ✅ | ✅ | Includes rule results and comparison |
| `scans:create` | ✅ | ✅ | ✅ | — | Requires active verification + authorization (FR-03) |
| `scans:cancel` | ✅ | ✅ | ✅ | — | Any scan of the project |
| `monitoring:manage` | ✅ | ✅ | — | — | Opt-in schedules |
| `findings:read` | ✅ | ✅ | ✅ | ✅ | |
| `findings:accept_risk` | ✅ | ✅ | — | — | Justification ≥ 20 chars; max 12 months |
| `findings:close_not_reproducible` | ✅ | ✅ | ✅ | — | Justification required; shown as "Closed by user" |
| `findings:revoke_exception` | ✅ | ✅ | — | — | |
| `findings:report_fp` | ✅ | ✅ | ✅ | — | Feeds rule FP rate |
| `ai:use` | ✅ | ✅ | ✅ | — | Org quota and budget |
| `ai:read` | ✅ | ✅ | ✅ | ✅ | View generated explanations |
| `reports:create` | ✅ | ✅ | ✅ | — | |
| `reports:read` | ✅ | ✅ | ✅ | ✅ | |
| `reports:download` | ✅ | ✅ | ✅ | ✅ | Short-lived signed link; audit-logged (export) |
| `extension:sync` | ✅ | ✅ | ✅ | — | Plus extension token scope `sync:write` |
| `extension_observations:read` | ✅ | ✅ | ✅ | ✅ | Level 2 data only |

## 4. Self-service, extension and public permissions (no org role)

| Permission | Who | Notes |
|---|---|---|
| `public:none` | Anyone | Health check, invite redemption, extension token exchange. Rate-limited (RoE §13) |
| `self:bootstrap` | Valid JWT whose `sub` has a `provisioned` beta invite | ADR-0014 |
| `self:read` | Valid JWT with an active profile | `/me`, own orgs |
| `self:update` | Valid JWT with an active profile | Display name only |
| `self:create_org` | Valid JWT with an active profile | Beta cap: ≤ 3 orgs created per user † |
| `self:accept_org_invitation` | Valid JWT; invitation email must equal profile email | |
| `self:manage_extension_sessions` | Valid JWT with an active profile | Authorize, list, revoke own extension token families |
| `extension:token_scope` | Valid extension access token | Scopes `projects:read`, `sync:write`; still subject to org permissions in §3 |

## 5. Platform permissions

| Permission | `platform_admin` | Notes |
|---|---|---|
| `platform:invites_manage` | ✅ | Issue/revoke beta invites |
| `platform:kill_switch` | ✅ ⚑ | Global scan kill switch (RoE §14) |
| `platform:deny_list` | ✅ | Per-host kill / deny list (RoE §15) |
| `platform:incident` | ✅ ⚑ | Mark scanner instance results `untrusted` (TX-15) |
| `platform:health_read` | ✅ | Queue depth, error rates; no tenant content |

Org roles grant **none** of the platform permissions. `platform_admin` grants **none** of the org permissions.

## 6. Scenarios (each becomes a test in 04.2 / 03.x / 10.x)

| ID | Scenario | Expected | Test |
|---|---|---|---|
| PS-01 | User A requests org B's project, finding, scan, report or audit event by ID | `404` (never 403, never data) | SAC-TEN-02 |
| PS-02 | User A lists findings with `?project_id=` from org B | `200` with 0 rows, or `404` for path-scoped lists | SAC-TEN-02 |
| PS-03 | Body or query contains `org_id` of org B | Ignored; effective org = path org | SAC-TEN-01 |
| PS-04 | Membership revoked while the user still holds a valid JWT | Next request to that org → `404 org.not_found` | SAC-TEN-02 |
| PS-05 | Membership revoked while a scan initiated by that user is queued | Manual scan → cancelled with reason `initiator_revoked`; authorizations they consented → `suspended` (DEC-034) if they were owner/admin | SAC-AUTHZ-03 |
| PS-06 | Admin tries to grant themselves owner, or to change another admin | `403 authz.forbidden` | 04.2 tests |
| PS-07 | Last owner tries to leave or be demoted | `409 org.last_owner` | 04.2 tests |
| PS-08 | Viewer calls `POST scans`, `PUT scope`, `POST authorizations` | `403 authz.forbidden` | 04.2 tests |
| PS-09 | Analyst tries to consent or change scope | `403 authz.forbidden` | SAC-AUTHZ-02 |
| PS-10 | Extension token user lost all memberships | Extension token families revoked (TX-04); sync → `401` | SAC-EXT-02 |
| PS-11 | Extension token user is a viewer in the target org | Sync → `403` (no `extension:sync`) | SAC-EXT-02 |
| PS-12 | Extension sync for an origin not in the active authorized scope, or verification not `verified` | `409 sync.origin_not_authorized` | SAC-EXT-02 |
| PS-13 | Uninvited JWT calls `/me/bootstrap` | `403 beta.not_invited` + alert | SAC-INV-08 |
| PS-14 | Platform admin calls a tenant data endpoint (`GET …/findings`) | `404` (no membership) | 04.2 tests |
| PS-15 | Sensitive op (⚑) whose authentication evidence is older than 600 s | `401 auth.reauth_required` | AC-STEP-02 |
| PS-19 | Sensitive op with a **freshly refreshed** token (new `iat`) but an old authentication event | `401 auth.reauth_required` | AC-STEP-03 |
| PS-20 | Sensitive op with no or malformed authentication evidence | `401 auth.reauth_required` | AC-STEP-04 |
| PS-21 | Sensitive op right after interactive re-authentication | Allowed (if the role permits); evidence timestamp in audit | AC-STEP-01, AC-STEP-06 |
| PS-16 | Org suspended or deleted | All tenant endpoints → `404`; scans refused; monitoring disabled | 04.4 tests |
| PS-17 | Report download link reused after expiry, or by a non-member | `404` | 11.3 tests |
| PS-18 | Scheduled scan when the consenting admin was demoted | Authorization `suspended` → scheduled scan skipped, owner notified | SAC-AUTHZ-03 |

### 6.1 Step-up acceptance tests (design specifications, not yet executed)

| ID | Pass condition | Backlog |
|---|---|---|
| AC-STEP-01 | Evidence 0–600 s old → ⚑ operation allowed (role permitting) | 03.3 |
| AC-STEP-02 | Evidence 601 s old (server clock controlled) → `401 auth.reauth_required` | 03.3 |
| AC-STEP-03 | Session refreshed (new `iat`, same old evidence) → `401 auth.reauth_required` | 03.3 |
| AC-STEP-04 | Evidence missing / malformed / future-dated by > 5 s → `401 auth.reauth_required` | 03.3 |
| AC-STEP-05 | Verification spike against local Supabase: refresh doesn't change the evidence; re-authentication does (feeds DM-A5) | 03.1 |
| AC-STEP-06 | Every ⚑ endpoint (API-022, API-023, API-055, API-093, API-096) enforces the check; audit event records the evidence timestamp | 03.3 / 05.4 / 06.4 / 07.5a |

## 7. Open points
- TM-OD-02 (team invite caps per org): open.
- `self:create_org` cap (3 orgs per user) is a beta default †, confirmed in 12.1.
- DM-A1 (org-level roles only in MVP) is **confirmed** by the owner. DM-A5 (exact step-up evidence) stays contingent on 03.1 verification (AC-STEP-05).
