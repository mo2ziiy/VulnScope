# ADR-0011: Strict posture-score eligibility

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Revised: v0.2 · Open: OD-01, OAD-06
- Related: ARCHITECTURE §11–§11.1, PRD §7, DEC-011

## Decision
- A scan is score-eligible only if its status is `completed` **and** every enabled Core rule is determinate at rule level. No coverage threshold.
- The score is computed only over determinate Core rules (`not_applicable` excluded from the denominator); Tier 2 / preview rules never count.
- Stored with `formula_version` and `rule_set_version`; comparisons across versions are flagged.
- **Current vs historical (v0.2):**
  - The API exposes `current_score` (non-null only if the **latest finished scan** is eligible) and a separate `historical_score`. There is no fallback `score` field.
  - If the latest scan is incomplete, the headline shows "Latest scan incomplete — no current score" with no number, gauge or grade color.
  - A previous eligible score may appear only in a subordinate "History" element, labeled "Historical — previous complete scan", with its original timestamp, coverage, rule-set version and age.
  - Lists, sorting, reports' summaries, alerts and the extension never use the historical score.
  - Acceptance criteria AC-SC-01…03.

## Alternatives
- Coverage threshold (e.g., ≥ 80%) — rejected: could show a good score while TLS was never checked.
- Showing the last complete score next to the incomplete status (v0.1) — rejected: easily read as current.

## Consequences
More scans show "Incomplete" (e.g., apex→`www` redirects) → onboarding guides users to verify and authorize those hosts.
