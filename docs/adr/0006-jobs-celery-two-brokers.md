# ADR-0006: Celery jobs with separate core and scan brokers

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Revised: v0.2 · Open: OAD-04, OAD-07
- Related: ARCHITECTURE §4, §8.3, §9.4

## Decision
- Celery with Redis for **core** jobs, using **two Redis instances**: `redis-core` (core jobs, rate limits, cache) and `redis-scan` (scan/probe streams, cancel and kill flags).
- **v0.2:** the scanner side does **not** run Celery. It's a minimal **Redis Streams** consumer (`scan:jobs` via consumer group, `scan:results`, read-only `scan:cancel:*` and `scan:kill`). Celery/kombu needs broad key patterns and commands that a tight ACL can't express. The core worker bridges Celery tasks to and from the streams.
- Scanner ACL (Redis ≥ 7 selectors), verified with tests in 06.1:
  `-@all +hello +ping (~scan:jobs +xreadgroup +xack +xautoclaim) (%W~scan:results +xadd) (%R~scan:cancel:* %R~scan:kill +get +exists)`.
- The `core` ACL user has read/write on `scan:*` with no admin commands. An ops/admin user is never deployed with any service.
- Explicit job lifecycle, deadlines, idempotency keys, retries with backoff, cancellation (cancel flag checked by the scanner between requests).
- The kill switch is mirrored: `redis-core` (API refuses new scans) and `scan:kill` (scanner aborts).

## Alternatives
- Single Redis with ACLs — rejected: leaves one network path from scanner to core data.
- Celery on both sides — rejected in v0.2: the ACL would be too broad.
- HTTPS pull gateway for the scanner (OAD-07 B) — fallback if the ACL can't be verified or the platform makes private Redis hard.
- Dramatiq / arq for core jobs — simpler, less mature scheduling and time limits (OAD-04).

## Consequences
- \+ A scanner compromise can't read or forge core jobs, and can't touch cancel/kill flags.
- − One more managed Redis; a small custom Streams consumer/bridge to own and test.
