# ADR-0003: Supabase Auth with server-side JWT verification

- Status: accepted (design level, owner approval 2026-10-14) (provider itself accepted in DEC-008) · Date: 2026-10-14 · Task: 00.2 · Revised: v0.2
- Related: ARCHITECTURE §6–§7.1, ADR-0014, PRD §10 Auth

## Decision
- Supabase Auth handles identity only: email confirmation, password set/reset, login, sessions.
- **Public sign-up is disabled at Supabase.** Identities are created only server-side by our API after atomic invite redemption (ADR-0014). *(v0.2: replaces "sign-up completes only with a valid invite checked by our API", which ran too late to stop identity creation.)*
- The API verifies every access JWT itself: signature via JWKS (cached, rotation by `kid`), `iss`, `aud`, `exp`, `nbf`. The exact signing algorithm and JWKS availability for our Supabase project are verified in 03.1.
- The service-role key is used only by the API/core worker for invite redemption, reconciliation and cleanup; it never leaves the core zone.
- Profiles, organizations, memberships and roles live in **our** Postgres. Supabase roles/claims are not used for authorization.
- The browser never queries a database directly (no Supabase data APIs for app data).
- MVP enables email + password only; OAuth providers stay disabled until tested against the disabled-sign-up control.
- Local dev: Supabase CLI (free).

## Alternatives
- Self-built auth — more security surface for a solo builder.
- Clerk / Auth0 — paid tiers; not chosen.

## Consequences
- \+ Vendor handles password storage and email flows.
- − Outage blocks login → JWKS cache, auth adapter, identity mirrored locally (PRD R-12).
- − Custom SMTP is needed for beta email volume (OAD-14).
