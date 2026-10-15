# VulnScope — Scanner Rules of Engagement (RoE-1)

| Field | Value |
|---|---|
| Status | **APPROVED RoE-1 (doc revision v0.2) — Task 00.3 (approved by owner 2026-10-14)** · Erratum E-03 applied 2026-10-15 (§6 enforcement mechanism only; no limit changed) |
| Date | 2026-10-14 |
| Changelog | **v0.2:** §8 DNS completeness rewritten (complete-answer validation, oversized/truncated/ambiguous answers fail closed, no silent truncation); §14 cancellation/kill rewritten (stop-new vs abort-in-flight, per-phase checks, per-scan child process, Redis-unavailable fail-closed, ≤ 5 s bound replaces ≤ 16 s); §7 note on cancellation vs timeouts. **v0.1:** initial draft |
| Applies to | `services/scanner` (all probes and scans), core-worker dispatch, API enqueue |
| Sources | PRD §4.2, §9, §10 · ARCHITECTURE §8–§9.4 · ADR-0007, 0008, 0009, 0015 · THREAT_MODEL.md |
| Versioning | Users acknowledge a specific RoE version (`roe_version = RoE-1`). Any change that increases what the scanner may do bumps the version and requires re-consent (ARCHITECTURE §8.4). Tightening a limit is a minor revision (RoE-1.x) and needs no re-consent. |

All numbers below are **initial beta limits**. They are enforced in code (scanner + dispatch) and covered by tests (SAC-xx in THREAT_MODEL.md §8). Values marked † still need measurement or confirmation in the phase shown; until then they stay at the value given (the stricter side).

---

## 1. Purpose and principles
1. **Passive, low-impact observation only.** The scanner reads what any browser would receive from a normal `GET`. It never tries to change state, authenticate, or trigger errors.
2. **Exact authorized scope.** Only hosts with an active verification **and** an active authorization (ADR-0015), and only the ports and paths listed in the signed scope token.
3. **Fail closed.** If anything is unknown, blocked, over budget, or unauthorized, the scanner stops that action and records `inconclusive` / `not_checked` / `error`. It never guesses.
4. **Identifiable and stoppable.** Every request identifies VulnScope; any scan can be stopped per scan, per host, or globally.

## 2. What the scanner may do

| Allowed | Detail |
|---|---|
| DNS | `A`, `AAAA` lookups for authorized hosts; `TXT` lookup of `_vulnscope-challenge.<host>` for verification |
| HTTPS `GET` | To `https://<authorized host>:443/<authorized path>` |
| HTTP `GET` | To `http://<authorized host>:80/` (redirect probe) and same-host port-80 redirect hops |
| TLS inspection | One handshake per authorized host on 443 to read the certificate chain, negotiated version and cipher; **no application data is sent** on this connection |
| Verification fetch | `GET https://<host>/.well-known/vulnscope-verification.txt`, no redirects |

## 3. What the scanner must never do
- Any method other than `GET` (no `HEAD`, `OPTIONS`, `POST`, `PUT`, `DELETE`, `PATCH`, `TRACE`, `CONNECT`). *A bounded CORS observation (Tier 2) that needs a preflight-style request requires an RoE version bump.*
- Request bodies, query strings, fragments, form submissions, or file uploads.
- Send cookies, `Authorization`, API keys, or credentials of any kind; keep a cookie jar; replay `Set-Cookie` values.
- Follow a redirect outside the signed scope (other host, port, or scheme combination not listed).
- Payloads, fuzzing, brute force, injection strings, path guessing, directory enumeration, `robots.txt`/sitemap crawling, link following beyond configured paths.
- Port scanning, subdomain enumeration, zone transfers (`AXFR`), reverse-DNS sweeps, ICMP.
- Execute JavaScript, render pages, run a headless browser, or load sub-resources.
- Connect to an IP literal host, a non-default port, or any address in the blocked set (ARCHITECTURE §9.2).
- Use proxy environment variables or any proxy, unless OAD-13 (scope-enforcing egress proxy) is adopted.
- Retry a `4xx`/`5xx` response, or retry after an explicit refusal, beyond §6 limits.

## 4. Scope limits

| Limit | Value | Enforced by |
|---|---|---|
| Hosts per project scope | ≤ 5 authorized hosts (e.g., apex + `www`) | API (project/scope) + token |
| Paths per host | `/` + up to **4** owner-configured paths (total 5) | API + token |
| Path format | Absolute, same-origin, normalized, ≤ 256 chars, no query, no fragment, no `..`, no encoded slashes | API normalizer |
| Ports | 443 (HTTPS); 80 only for the redirect probe and same-host hops | Token |
| Host format | DNS hostname, IDNA/punycode-normalized, lowercased, no trailing dot, no IP literals, no userinfo, ≤ 253 chars | API normalizer |

## 5. Request budget per scan

| Budget | Value |
|---|---|
| HTTP(S) requests per scan (all hosts, all hops) | **≤ 40** |
| HTTP(S) requests per host per scan | **≤ 20** |
| Redirect hops per chain | **≤ 5** |
| TLS inspection handshakes per host per scan | **1** (+1 retry on network error) |
| DNS queries per scan | **≤ 120** (each connection resolves `A` + `AAAA` afresh, §8.8: 40 requests × 2 + TLS inspections + retries) |
| Verification probe (one check) | 1 DNS TXT query **or** 1 HTTPS GET (+ address resolution) |
| Total bytes downloaded per scan | **≤ 4 MiB** |

When a budget is exhausted, the scanner stops and marks the remaining rules `not_checked` (`budget_exhausted`). The scan becomes `partial`.

## 6. Concurrency, pacing and retries

| Limit | Value | Enforced by |
|---|---|---|
| In-flight requests per target host | **1** (strictly serial) | Scanner |
| Minimum gap between requests to the same host | **500 ms** (≤ 2 req/s) | Scanner |
| Running scans per project | **1** | API |
| Running scans per **host** across all orgs | **1** | PostgreSQL host lease with fencing epoch, acquired all-or-nothing at dispatch (DATA_MODEL §5.1). *Erratum E-03 (2026-10-15): replaces the obsolete Redis-core lock; the limit itself is unchanged* |
| Concurrent scans per scanner instance | **≤ 4** | Scanner |
| Concurrent scans globally (beta) | **≤ 20** † (13.3 load test) | Dispatch |
| Retries per request | **≤ 1**, only for connect timeout / connection reset / DNS `SERVFAIL`; backoff 2 s | Scanner |
| Retries after HTTP status | **0** (`4xx`/`5xx` are observations, not errors) | Scanner |
| Port-80 refusal confirmation | Second attempt after **5 s**, on every validated address | Scanner |

## 7. Timeouts

| Phase | Timeout |
|---|---|
| DNS query (per resolver attempt) | **2 s**, max 2 attempts across 2 resolvers; **5 s** total per hostname resolution including any TCP fallback (exceeded → `dns_incomplete`) |
| TCP connect | **5 s** |
| TLS handshake | **5 s** |
| Time to response headers | **10 s** |
| Whole request (including body read) | **15 s** |
| Scan running deadline (hard) | **180 s** → `partial` (or `failed` if nothing was observed) |
| Typical scan target | ≤ 60 s † (measured in 06.4) |
| Queue wait before pickup | **10 min** → `failed` `scanner.unavailable` |
| Verification probe deadline | **30 s** |

Phase timeouts bound how long an operation may take when **nobody cancels it**. Cancellation and the kill switch don't wait for these timeouts: they interrupt the operation (§14). So the cancel bound (≤ 5 s) is independent of the longest phase timeout (15 s).

## 8. DNS behavior
**Core rule (v0.2): a hostname is usable only if its *complete* DNS answer was received, parsed and validated. The scanner never truncates an answer, ignores addresses beyond a limit, or proceeds on a partial answer. Anything it can't validate completely fails closed.**

1. **Resolver path.** The scanner uses its own stub resolver (async, cancellable), talking only to the **configured public recursive resolvers** (two, from config; OAD-11). It never uses the OS resolver (`getaddrinfo`), `/etc/hosts`, search domains, or the platform's internal resolver. Queries use the FQDN with a trailing dot. The stub resolver exposes the full response (flags, RCODE, all sections), which the OS resolver doesn't.
2. **Both families, both complete.** The scanner queries `A` and `AAAA` separately. A hostname is usable only when **both** queries finished with a definite result: answers, or `NOERROR` with no data (NODATA). If one family times out, errors, or is truncated, the host is `dns_incomplete`, even if the other family returned public addresses.
3. **Address limit = rejection limit, not a reading limit.** Each resolution may contain at most **16** addresses in total (`A` + `AAAA` combined, after de-duplication). **All** of them are validated. If an answer has **more than 16**, the host is rejected with `dns_answer_oversized`, and nothing is connected. *(v0.1 said "max 8 addresses considered", which could be read as ignoring the rest. That wording is withdrawn.)*
4. **Any blocked address blocks the host.** If any one of the validated addresses is in the blocked set (including IPv4 embedded in IPv6 forms), the whole hostname is blocked for this scan (`destination_blocked`). The scanner never "picks the public one".
5. **Truncation.** A UDP response with the `TC` bit set is retried over TCP to the same resolver. If the TCP answer is also truncated, fails, or is cut mid-record, the host is `dns_incomplete`. EDNS0 UDP buffer is 1232 bytes; the maximum accepted message is 64 KiB over TCP. Larger → `dns_answer_oversized`.
6. **Ambiguity.**
   - CNAME chains: max depth **8**. Loops or depth > 8 → `dns_ambiguous`.
   - An `A`/`AAAA` record whose owner name is neither the query name nor a name in its CNAME chain → `dns_ambiguous`.
   - Malformed or unparseable messages, a query-ID or question mismatch → `dns_malformed`.
   - Answers from the two resolvers are never merged. The secondary is asked only after a transient failure of the primary, and its answer must be complete on its own.
7. **Response codes.** `NXDOMAIN` and NODATA are **definite**. `SERVFAIL`, `REFUSED`, and timeouts are **transient** (one retry via the secondary resolver, RoE §6). `FORMERR`/`NOTIMP` → `dns_malformed`.
8. **Resolve per connection, validate, pin.** Every new connection does a fresh, complete resolution (steps 2–7). The scanner connects to a validated IP, sets `Host`/SNI to the hostname, and verifies the socket peer address equals that IP. It never re-resolves between check and connect. TTLs are ignored (no caching across connections).
9. Address order is deterministic: IPv4 sorted, then IPv6 sorted. Max **2** connection attempts across validated addresses per request.
10. DNSSEC is **not validated** in MVP (documented limitation; THREAT_MODEL R-RES-07).
11. **Verification TXT.** The TXT answer for `_vulnscope-challenge.<host>` must be complete (same truncation and malformation rules) and contain at most **10** records and **4 KiB** total. A larger answer → the check fails with `dns_answer_oversized`. The scanner compares only records with the prefix `vulnscope-verify=`. For **revalidation**, oversized/incomplete/malformed TXT answers count as **transient** (verification → `unknown`, scans blocked), not as a definite failure (§12).

| DNS outcome code | Meaning | Rule effect | Scan effect |
|---|---|---|---|
| `dns_answer_oversized` | > 16 addresses, > 64 KiB, TXT > 10 records / 4 KiB | Rules for that host `error` | `partial`, or `failed` if no host is usable |
| `dns_incomplete` | One family missing, truncation not recoverable, timeout | `inconclusive` | same |
| `dns_ambiguous` | CNAME loop/depth, out-of-chain address records | `error` | same |
| `dns_malformed` | Unparseable / mismatched / FORMERR / NOTIMP | `error` | same |
| `destination_blocked` | Any address in the blocked set | `error` | same |
| `host_not_found` | `NXDOMAIN` | `inconclusive` (target unreachable) | `failed` if no host is usable |

## 9. TLS handling
1. The **inspection** connection (one per host) records: chain subjects/issuers, validity dates, SAN list (bounded to 50 names), negotiated protocol and cipher, OCSP stapling presence. Verification is evaluated *offline* by the rule engine; no HTTP data is sent on this connection.
2. **HTTP fetches** over TLS require a valid certificate (system trust store pinned in the image, hostname verification on). If validation fails, the fetch isn't made, and header rules for that host are `inconclusive` (`tls_invalid`). The TLS rule reports the certificate problem.
3. TLS 1.2 and 1.3 only for fetches; ALPN `http/1.1` only (no HTTP/2 in MVP). No client certificates, no session resumption across scans.
4. SNI is always the authorized hostname.

## 10. Request shape

| Header | Value |
|---|---|
| `User-Agent` | `VulnScopeBot/1 (+https://<public-domain>/scanner; passive security checks)` |
| `VulnScope-Scan-Ref` | Opaque public reference (not the internal scan UUID); lets site owners correlate with an abuse report |
| `Accept` | `text/html,application/xhtml+xml;q=0.9,*/*;q=0.5` |
| `Accept-Encoding` | `gzip, identity` |
| `Connection` | `close` |
| Not sent | `Cookie`, `Authorization`, `Referer`, `Origin`, custom auth headers |

## 11. Response limits

| Limit | Value | On exceeding |
|---|---|---|
| Header block size | **64 KiB** | Stop reading → observation truncated → affected rules `inconclusive` |
| Header count | **100** | Same |
| Single header value kept | **8 KiB** read; evidence stores ≤ **1 KiB** | Truncated, flagged |
| `Set-Cookie` headers parsed | **50**; names ≤ 256 chars; **values are discarded immediately** | Extra ignored, observation flagged incomplete |
| Body read (compressed) | **256 KiB** | Stop reading |
| Body after decompression | **1 MiB**, ratio ≤ **20:1** | Abort decode → `inconclusive` |
| Verification file | **4 KiB**, no redirects | Mismatch |
| Stored evidence per rule result | **2 KiB** | Truncated |
| Result payload per scan to broker | **512 KiB** | Core rejects → `failed` `result.invalid` |

**Body content is never sent to the broker.** The scanner sends only bounded extracted features: content type, length, and (for Tier 2 later) scheme+host of referenced sub-resources. Raw bodies never leave scanner memory and are never stored (PRD §10 Privacy).

## 12. Verification and authorization timing

| Item | Value |
|---|---|
| Challenge TTL | **72 h**, single-use, replaced by any new challenge |
| Verification validity (hard expiry) | **30 days** from the last successful check |
| Revalidation before a manual scan | If the last successful check is older than **24 h** (OAD-05 B) |
| Revalidation before a scheduled scan | **Always** |
| Definite failure (record/file absent, value mismatch, `NXDOMAIN`) | Verification → `revoked`; scope suspended; owner notified |
| Transient failure (`SERVFAIL`, timeout, oversized/incomplete/malformed TXT answer per §8.11, 5xx on the file) | Verification → `unknown`; **scans blocked** until a successful check; not revoked. After 3 consecutive transient failures over ≥ 24 h → `revoked` |
| Authorization expiry | **12 months**, or earlier on scope change, RoE version bump, revocation, abuse suspension, or the consenting user losing owner/admin (OAD-15 B, proposed) |

## 13. Product-level rate limits and quotas (beta)

| Limit | Value |
|---|---|
| Manual scans per project per day | **10** |
| Scans per org per day | **30** |
| Scans per user per day (across orgs) | **20** |
| Scans per **host** per day (across all orgs) | **20** |
| Scheduled monitoring interval | min **24 h**; default weekly |
| Verification checks | **10 per challenge per hour**, **30 per org per hour** |
| Invite redemption attempts | **10 per IP per hour**, **5 per token per hour** |
| Projects per org (beta) | **10** † (12.1) |

Exceeding a limit returns `429` with a structured code. Nothing is silently queued.

## 14. Cancellation and kill switch

### 14.1 Two different things: stop new work, abort in-flight work

| Term | Meaning |
|---|---|
| **Stop new** | After the scan's abort signal is set, **no new network operation begins** for that scan: no DNS query, no TCP connect, no TLS handshake, no request bytes written, no new redirect hop. |
| **Abort in-flight** | Any operation **already running** (DNS query waiting, connect pending, handshake in progress, headers or body being read) is **interrupted and its socket closed**. It doesn't run to its phase timeout. |
| **Network quiescence** | The scan has no open sockets and sends no further packets. This is what the targets below measure. |

A request whose bytes were already written can't be "un-sent". The server may still process that single `GET`. Abort guarantees we stop reading and close the connection; it doesn't guarantee the server never saw the request. That's acceptable because the request is a passive `GET`.

### 14.2 Execution model
- Each scan runs in its **own child process** under a scanner **supervisor** (max 4 children per instance, §6). All network I/O in the child is non-blocking and cancellable (async sockets, async stub resolver, async TLS). No blocking OS resolver calls.
- The **supervisor** runs a control watcher that polls `scan:kill` and `scan:cancel:{scan_id}` for each running child every **1.0 s**, with a **0.5 s** Redis operation timeout.
- When a flag is seen set, the supervisor sets the child's local **abort event** (via a pipe). The child checks this event at every gate (§14.3). An abort event also cancels every pending I/O task of the child.
- If the child hasn't reported quiescence **2.0 s** after the abort event, the supervisor sends `SIGKILL`. The kernel then closes all its sockets.
- **Control freshness:** each child gets the timestamp of the supervisor's last *successful* poll. A gate refuses to start new work if that timestamp is older than **2.5 s** (§14.4).

### 14.3 Where the checks happen (per phase)

| Phase | Gate check *before* starting | Behaviour *during* the phase on abort |
|---|---|---|
| Picking up a job | Kill flag clear and fresh (successful read within the last **1.5 s**); otherwise the supervisor doesn't call `XREADGROUP` (blocking read limited to 1 s) | — |
| DNS query (each `A`/`AAAA`/`TXT`, each retry) | Abort event clear + control fresh + budget left | Pending query cancelled, UDP/TCP socket closed |
| TCP connect | Same | Pending connect cancelled, socket closed |
| TLS handshake (fetch or inspection) | Same | Handshake cancelled, socket closed |
| Writing request bytes | Same, checked **immediately** before the write | — (write is a single small buffer) |
| Reading response headers | Checked before each read of ≤ **16 KiB** | Read cancelled, socket closed, partial headers discarded |
| Reading response body | Checked before each read of ≤ **16 KiB** | Read cancelled, socket closed, partial body discarded |
| Pacing wait / redirect hop / next path | Checked when the wait starts; the wait itself is interruptible | Wait ends immediately; no next request |
| Publishing results | Checked; a cancelled scan publishes only a `cancelled` notice (no observations) | — |

Rules whose observations were interrupted are `not_checked` (`cancelled`). An aborted scan never publishes partial observations as if complete.

### 14.4 Redis unavailable during an active scan (fail closed)
- If a poll fails (error or timeout), the supervisor retries on the next tick.
- If **no successful poll** has happened for **> 2.5 s**, control is **stale**. Every gate refuses new work, and the supervisor sets the abort event for **all** children (reason `control_unavailable`). After 2.0 s, still-running children get `SIGKILL`.
- The scanner doesn't pick up new jobs until polls succeed again.
- Results can't be published while Redis is down. The scanner tries to publish a `control_unavailable` notice for up to **30 s**, then discards it. The core marks the scan `failed` (`control_unavailable` if the notice arrives, otherwise `scanner.unavailable` at the queue/running deadline). No observations from the aborted part are ever used.
- If the core can't write a cancel flag because Redis is down, the scanner aborts anyway through staleness. Either way, cancellation can't be "lost".

### 14.5 Timing budget and guarantees

| Step | Worst case |
|---|---|
| Flag written → supervisor sees it | 1.0 s poll interval + 0.5 s operation timeout = **1.5 s** |
| Supervisor → child abort event | ≤ **0.1 s** |
| Cooperative abort (cancel tasks, close sockets) | ≤ **2.0 s**, else `SIGKILL` |
| `SIGKILL` → kernel closes sockets | ≤ **0.5 s** (budget) |
| **Total: flag write → network quiescence** | **≤ 4.1 s → guarantee stated as ≤ 5 s** |
| Redis outage start → stale detected | last success + 2.5 s (worst case ≈ 3.0 s after outage start, given a 0.5 s poll in flight) |
| **Total: Redis outage → network quiescence** | ≈ 3.0 + 0.1 + 2.0 + 0.5 = **5.6 s → guarantee stated as ≤ 6 s** |

These bounds don't depend on phase timeouts (§7), because every phase is interruptible. The 16 s figure in doc v0.1 is withdrawn.

### 14.6 Controls

| Control | Mechanism | Measurable target |
|---|---|---|
| User cancel | Core sets `scan:cancel:{scan_id}` (TTL = scan deadline + 60 s) | No new operation after the abort event; network quiescence **≤ 5 s** after the flag write; scan `cancelled` |
| Authorization/verification revoked mid-scan | Core sets the cancel flag on the revocation event | Same as user cancel |
| Per-host kill (abuse report) | Host added to a deny list checked at enqueue and dispatch; cancel flags set for running scans of that host | Running scans quiescent **≤ 5 s**; new scans refused immediately |
| Global kill switch | `scan:kill` + Redis-core flag; API refuses scans; supervisors stop picking jobs and abort all children | All scanner network activity quiescent **≤ 5 s** after activation; no new job picked (drill: LG-OPS-02) |
| Redis (scan broker) unavailable | Staleness rule §14.4 | Network quiescence **≤ 6 s** after outage start |
| Infrastructure kill | Scale scanner deployment to zero | Within **≤ 5 min** (platform dependent, OAD-03) |

## 15. Opt-out and abuse handling
1. A public page `/scanner` explains what the bot does, its User-Agent, the scan-ref header, and how to report abuse.
2. Abuse contact: a monitored address on the public domain (set up before external beta).
3. On a credible complaint about a host: per-host kill immediately, the authorization suspended, the org notified, review within **2 business days**. Verification alone doesn't lift the suspension.
4. Site owners can request a permanent host deny-list entry.

## 16. Environment-specific rules

| Environment | External targets | Notes |
|---|---|---|
| Local dev | **Disabled** (`SCANNER_ALLOW_EXTERNAL=false`) | Fixture servers on `scan_net` only |
| CI | **Disabled, enforced** | Tests fail if any non-fixture connection is attempted |
| Internal alpha | Only hosts the owner personally controls, listed in an allowlist file | Stage S1 in SECURITY_LAUNCH_GATES.md |
| External beta | Any host passing verification + authorization | All launch gates passed |

## 17. Data collected and retention (proposed for OD-02)

| Data | Retention (beta) |
|---|---|
| Scan observations / evidence | **180 days** †, then deleted (12.4) |
| Scan job metadata and rule results (no evidence) | Life of the project + 30 days |
| Extension Level 1 (local) | Tab session; max **24 h**; never uploaded without action |
| Extension Level 2 (synced) | **90 days** |
| AI interactions | **90 days** |
| Audit events | **1 year** |
| Raw response bodies | **Never stored** |
