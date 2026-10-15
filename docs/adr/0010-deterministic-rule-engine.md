# ADR-0010: Deterministic, versioned rule engine with tiers

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Revised: v0.2
- Related: ARCHITECTURE §9.3, §10, §12, PRD §9, DEC-013

## Decision
- `packages/rules`: each rule is a pure function `evaluate(snapshot, config) → RuleResult[]` with a stable ID and semver; no network, clock or randomness.
- Rules run in the core worker over the scanner's bounded observation snapshot.
- **Outcomes (v0.2):** `pass` (confirmed pass), `fail`, `not_applicable` (proven, with a coded reason), `subject_absent`, `inconclusive`, `not_checked`, `error`. Results are per subject; coverage is judged per rule.
- **Resolution (v0.2):** a finding resolves only on a verified cloud scan, for the same fingerprint, from a complete observation with stored evidence, when the outcome is `pass` or a `not_applicable` whose reason is listed in that rule's `resolving_na_reasons` (default: empty). `subject_absent`, `inconclusive`, `not_checked` and `error` never change state. Per-rule semantics for Core v1: ARCHITECTURE §10.3. Acceptance criteria: AC-LC-01…11.
- Users may close a finding as `closed_by_user` (exception type `not_reproducible`, justification, audited). It's shown and counted separately from "resolved".
- Fingerprint = hash(project_id, rule_id + major version, subject_key). Evidence values are excluded.
- Rule states `draft → preview → enabled → deprecated`; promotion is gated by fixtures, determinism, unknown-handling and FP measurement. Adding a resolving reason is a rule version change.

## Alternatives
- Rules inside the scanner — rejected (more code in the hostile-input zone, harder to test).
- Treating every `not_applicable` as resolving (v0.1) — rejected: unsafe; absence or inapplicability is not proof of a fix unless the rule defines the evidence.

## Consequences
Fixture servers are a first-class part of the repo (07.1), with one fixture per outcome row. Some genuinely fixed findings (e.g., a removed cookie) stay open until the user closes them.
