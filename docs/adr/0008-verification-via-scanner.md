# ADR-0008: Domain verification performed by the scanner

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Revised: v0.2 · Open: OAD-05
- Related: ARCHITECTURE §8.1–§8.2, §8.4, ADR-0015, PRD FR-03

## Decision
- Methods: DNS TXT at `_vulnscope-challenge.<host>` and an HTTPS file at `https://<host>/.well-known/vulnscope-verification.txt`.
- Challenge: 32 random bytes, stored hashed, bound to (org, project, host, method), short TTL, single-use; a new challenge invalidates older ones.
- The lookup/fetch runs in the scanner pool through the egress guard; the HTTPS method follows **no redirects**. The comparison happens in the core worker (constant-time).
- Verification is per exact host, has `expires_at`, is revalidated (policy OAD-05), and is revoked on failed revalidation, which suspends scope, scans and sync.
- **v0.2:** verification proves **technical control only**. It is never treated as authorization to scan. Scans also need an explicit, active authorization record (ADR-0015).

## Alternatives
- Verification inside the API — rejected: the API would fetch user-controlled URLs (SSRF).
- HTML meta-tag method — deferred (needs body parsing).

## Consequences
Verification depends on the scanner being up; that failure shows as "check unavailable", never as success.
