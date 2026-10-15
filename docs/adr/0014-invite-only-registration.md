# ADR-0014: Invite-only registration with atomic redemption

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 (v0.2) · Open: OAD-14
- Related: ARCHITECTURE §7.1, ADR-0003, PRD FR-13, DEC-004

## Context
The beta is invite-only (DEC-004). A post-sign-up API check can't stop an uninvited person from creating an identity at the provider. Enforcement has to happen before any identity exists.

## Decision
1. **Provider gate:** public sign-up disabled in Supabase (`enable_signup = false` locally). Only email + password is enabled. No reliance on Auth Hooks; if one is verified available in 03.1, it can only be an extra layer.
2. **Invites:** `beta_invites` with a hashed 32-byte token, a **required bound email**, status, `expires_at`, a partial unique index for one live invite per email, and a unique `supabase_user_id`. Team invites also issue a beta invite for the same email.
3. **Atomic redemption:** one conditional `UPDATE … SET status='redeeming', redeem_attempt_id=… WHERE token_hash=… AND status='pending' AND expires_at>now() RETURNING …`. Exactly one concurrent attempt wins; every later write is fenced by `redeem_attempt_id`.
4. **Provisioning:** the API (service-role key, core zone only) creates the identity **for the bound email only** through the Supabase Admin API. Supabase emails the set-password link. Idempotent lookup by email before creating.
5. **Activation:** the first authenticated `POST /me/bootstrap` requires an invite with `supabase_user_id = sub` in `provisioned` state and a confirmed email. It then creates the profile and membership and marks the invite `activated`. Any other `sub` → `403 beta.not_invited` + alert (backstop).
6. **Replay protection:** single-use status transition, hashed token, token in the URL fragment, the same response for unknown/used/expired, rate limits.
7. **Cleanup:** expire `pending`; reconcile stale `redeeming`; delete unconfirmed identities from stale `provisioned` invites after N days; remove orphan identities; revocation deletes identities that aren't activated yet.

## Constraints to verify in 03.1 (03.1 stops if any fails)
- Disabled sign-up blocks every enabled self-service creation path.
- Admin invite/create still works while sign-up is disabled.
- Invite-link expiry setting, and custom SMTP requirements (OAD-14).

## Alternatives
- Post-sign-up validation only (v0.1) — rejected: identities could be created without an invite.
- Issuing Supabase invites at invite creation time — rejected: creates identities before acceptance and multiplies cleanup.
- Unbound invite codes — out of scope for MVP.

## Consequences
- \+ No identity exists without a redeemed invite; races and replays are handled in one SQL statement.
- − Depends on Supabase admin behaviour, so negative tests run against local Supabase in CI.
- − A small reconciler job to own.
