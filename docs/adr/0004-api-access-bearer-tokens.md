# ADR-0004: API access via Bearer tokens, no cookie auth on the API

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Open: OAD-12
- Related: ARCHITECTURE §6

## Context
The web app (Vercel) and the API (container platform) are different origins. The extension also calls the API.

## Decision
- The API accepts only `Authorization: Bearer` — the Supabase access JWT for users, a scoped extension token for the extension. It never reads cookies.
- CORS allowlist: the web origin(s) and the published extension origin. No wildcard.
- Next.js server components call the API server-side with the same user token (no privileged service token).

## Alternatives
- **Next.js BFF**: browser talks only to Next.js with HttpOnly cookies; Next.js proxies to a private API. Stronger against token theft via XSS, but doubles request paths, needs CSRF protection, and the extension would still need direct API access.

## Consequences
- \+ No CSRF on the API; one auth path for web and extension.
- − Access token readable by JS → strict CSP, escaped rendering and short token TTL are mandatory (00.3).
