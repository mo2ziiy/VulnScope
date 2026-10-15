# ADR-0013: Provider-agnostic AI adapter with grounding

- Status: accepted (design level, owner approval 2026-10-14) · Date: 2026-10-14 · Task: 00.2 · Open: OAD-08, OD-04
- Related: ARCHITECTURE §14, PRD FR-07/FR-08

## Decision
- AI calls run as core-worker jobs (the API has no AI egress); results are cached by (fingerprint, rule version, framework, prompt version).
- Adapter interface: `generate(structured_input, output_schema, budget) → validated_output`; provider and model come from the environment.
- Input: the stored structured finding + rule rationale/references + the user-selected framework. Redaction before sending; site-derived strings are delimited as untrusted data.
- Output: JSON Schema validated; references restricted to the rule catalog; rendered as escaped text / a restricted Markdown subset.
- The AI has no tools, cannot change findings or start scans; per-org quota and budget are enforced before the call.

## Alternatives
- Synchronous streaming from the API (OAD-08 B) — better perceived latency, but spreads egress and budget logic.

## Consequences
The UI needs a pending state (poll/SSE). Provider choice deferred to 09.1 with a cost approval.
