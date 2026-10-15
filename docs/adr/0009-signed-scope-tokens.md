# ADR-0009: Signed scope tokens for scan jobs

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Revised: v0.2
- Related: ARCHITECTURE §8.3, §9.2–§9.4, ADR-0015

## Decision
- At dispatch, the core worker re-checks verification **and authorization** (ADR-0015) and scope, then mints an **Ed25519-signed** token: `scan_id`, `org_id`, `project_id`, `verification_id`, `authorization_id`, allowed host(s), ports (443 plus optional same-host port-80 probe), paths, request budget, `rule_set_version`, a job nonce, short `exp`, `kid`.
- The scanner holds only the public keys. It rejects jobs with a bad signature, an expired token, or a mismatched `scan_id`, and enforces the token on every request and redirect hop.
- The private key lives only in the core worker's secret store; rotation via `kid`.
- The core worker accepts results only for a `running` scan with the matching job nonce, at most once.

## What this guarantees, and what it doesn't (v0.2)
- **Guarantees, while scanner code is intact:** a compromised broker can't inject or widen jobs, and the scanner won't contact hosts, ports or paths outside the authorized scope, including through redirects.
- **Doesn't guarantee:** anything once the scanner process itself is compromised. A compromised scanner can ignore the token. That case relies on network isolation (internal protection only) and on the residual-risk controls in ADR-0007.

## Alternatives
- HMAC shared secret — rejected: a scanner compromise would allow forging jobs.
- No token, trust the broker — rejected: a broker compromise would mean arbitrary scanning.

## Consequences
Key management work in 06.1; the token is part of the scan job JSON Schema.
