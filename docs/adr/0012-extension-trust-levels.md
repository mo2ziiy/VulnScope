# ADR-0012: Extension data trust levels and authentication

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Open: OAD-02, OD-02
- Related: ARCHITECTURE §13, PRD §8, DEC-012

## Decision
- **Level 1 (local):** user-initiated via `activeTab`, sanitized, kept in `chrome.storage.session` / memory with a TTL; never sent without an explicit action.
- **Level 2 (synced):** explicit "Sync" → the API checks token scope, membership, permission, active verification, and that the origin is exactly in the authorized scope → stored in `extension_observations` (`source=extension`).
- **Level 3 (verified scan):** the only writer of findings and score. The findings module has **no code dependency** on `extension_observations`.
- Auth (recommended, OAD-02 A): `chrome.identity.launchWebAuthFlow` to the web app's connect page → the API issues an opaque, scoped, short-lived, hashed-at-rest, refresh-rotated, revocable extension token. No Supabase refresh token in the extension.

## Alternatives
- Supabase session inside the extension (OAD-02 B) — more token power and lifetime.
- Pairing code (C) — more UX friction.

## Consequences
Two separate data models for "observations" are intentional; UI labels must keep them distinct.
