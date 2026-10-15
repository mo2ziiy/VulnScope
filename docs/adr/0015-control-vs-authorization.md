# ADR-0015: Technical control verification vs authorization to scan

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 (v0.2) · Open: OAD-15
- Related: ARCHITECTURE §8.2–§8.4, ADR-0008, ADR-0009, PRD FR-03, DEC-003

## Context
A DNS record or file proves someone could change the host's configuration. It doesn't prove a legal right to test it. Agencies, hosting staff, or an attacker with CMS upload access can pass a control check.

## Decision
- Two independent records, **both required** for every scan and every dispatch:
  - **Verification** (technical control, ADR-0008).
  - **Authorization** (`scan_authorizations`): scope snapshot hash (hosts, ports, paths), basis (`asset_owner` / `written_authorization_from_owner`), optional reference note, `roe_version`, `consented_by`, `consented_at`, optional `expires_at`, revocation fields.
- Only owner/admin can consent. Nothing is pre-checked. The consent screen shows the exact scope, the RoE summary and the basis. Agencies choose "written authorization from owner".
- Any scope change or RoE version bump blocks scans until re-consent (with a diff). Authorization is suspended on abuse complaints regardless of verification, and on the consenting user's role loss (OAD-15, recommended).
- Each `scan_job` stores `verification_id` and `authorization_id`. Scope tokens carry both. Reports and audit logs show both facts separately.
- ToS places responsibility for the authorization claim on the user. Legal review before public launch.

## Alternatives
- Treat verification as authorization — rejected: control isn't permission.
- Require uploaded written authorization documents — deferred: storage, privacy and review burden; the reference note is enough for MVP.

## Consequences
One more step in onboarding (consent after verification). Clearer accountability and audit trail.
