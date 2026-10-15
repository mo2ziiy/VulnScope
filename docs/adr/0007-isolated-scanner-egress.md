# ADR-0007: Isolated scanner and egress controls

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Revised: v0.2 · Open: OAD-03, OAD-11, OAD-13
- Related: ARCHITECTURE §4, §9.2–§9.4, Contract §6

## Decision
- `services/scanner` is the only component that performs network I/O toward customer infrastructure, including verification probes.
- **Credentials (v0.2 correction):** the scanner is *not* credential-less. It holds scan-broker ACL credentials (minimum ACL in ARCHITECTURE §9.4), the broker TLS CA, and public scope-token keys. It holds no DB, Redis-core, Supabase, AI or email credentials, no signing private key, and no cloud IAM role.
- **Network reachability:** `redis-scan`, the configured public DNS resolver, and public unicast IPs on TCP 80/443 only. Private, loopback, link-local, CGNAT, metadata, ULA, multicast, documentation and reserved ranges are denied at network level.
- **In-code egress guard** for every connection and redirect hop: scope check → budget/kill switch → resolve A/AAAA → validate every IP (including IPv4-mapped, NAT64 and 6to4 embeddings) → connect to the validated IP (pinning) with Host/SNI → verify the peer address → bounded request → manual redirect evaluation. Unauthorized redirect targets are **never** requested (§9.3).
- No proxy env (`trust_env` off), no auto-redirects, no JS execution, response caps, non-root, read-only filesystem, dropped capabilities, resource limits, short-lived instances.
- **Credential rotation:** broker password from the secret store, dual-password rotation (zero downtime), scheduled plus immediate on suspicion; scope-token keys rotate via `kid`.
- The scanner collects; it doesn't evaluate rules (ADR-0010).
- Local/CI: external scanning disabled by default; fixture servers only.

## Guarantees and their limits (v0.2)
- **Network isolation** (holds even if scanner code is compromised) protects VulnScope's infrastructure: no internal, private or metadata access.
- It does **not** stop requests to arbitrary *public* hosts. Only the signed scope token, enforced in scanner code, does that (ADR-0009), and only while the code is intact.
- A fully compromised scanner could still read queued jobs, drop jobs, falsify results for visible scans, and send traffic to public hosts. Mitigations: rate/bandwidth caps, monitored NAT + flow logs, result fencing (running state + nonce + one result), kill switch to zero, optional scope-enforcing egress proxy (OAD-13), independent review (13.4). Signed/pinned images are listed separately because they address a different threat.
- *Erratum E-01 (2026-10-14, owner-approved):* signed/pinned image digests prevent **wrong-image deployment**. They do **not** authenticate scanner observations or prevent runtime result fabrication by a compromised scanner (THREAT_MODEL §4.5, R-RES-02).

## Alternatives
- URL validation in the API only — rejected by the contract (insufficient).
- Third-party scanning proxy — adds vendor trust and cost.

## Consequences
The production platform must support per-service egress rules (OAD-03). Independent review before the external beta (13.4).
