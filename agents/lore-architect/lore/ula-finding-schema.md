# ULA finding schema — the multi-axis bug model

Added v16 (2026-06-08; `df/aiqa/schemas/bugs.schema.json`). Every ULA finding (in `bugs[]`, `crossUnit[]`, preserved in `dismissed[]`) carries **distinct axes** — keep them separate, don't collapse:

- **`impact-summary`** — plain-language essence + impact, readable by ANY engineer regardless of stack (general engineering terms, no stack jargon). Sits *above* the deep-technical `description`.
- **`nature`** — `product` (user/UX impact: wrong/inconsistent/unexpected behaviour) vs `technical` (system internals: memory, leaks, inefficiency, CPU, crashes). Binary; classify by **dominant** nature (a crash is `technical` even if a user feels it). `both` deferred unless dual-nature cases recur.
- **`severity`** — impact IF real: critical / high / medium / low / **negligible**. The `negligible` tier is the important one — "real but harmless", the discharge target for technically-true-no-impact findings.
- **`confidence`** — how sure it IS a bug: high / medium / low. "confirmed" deliberately absent — confirmation is the verify track's job (`ula-bug-verification-track.md`).
- **`category`** *(optional)* — defect TYPE enum (concurrency, error-handling, resource-lifecycle, …) + `other` + free-form `tags`. Distinct from `nature` and `severity`.

**Origin:** the user first asked for a "category" but meant *importance* → that is `severity`, not type. The reframe produced this multi-axis split. The user's other corrective — a *required* `context` field I'd added to "enforce" context-reading was dropped — is its own lesson (`feedback-schemas-as-enforcement-overreach.md`).

## crossUnit[]

Bugs noticed during a unit's pass that belong elsewhere: `external` (one other unit/file) or `interaction` (emergent across several; `targets[]` 1..n). Captured (don't drop in-hand signal), deferred to aggregation. `interaction` bugs are the first concrete content for the reserved above-file layer (`df-per-repo-backbone.md`).

## dismissed[] — preserve, don't drop

When verification (Step D or the aggregation re-verify) judges a finding NOT real, it **moves it to `dismissed[]`**, preserving the ORIGINAL finder fields verbatim, plus `dismissal-reason` and `dismissed-by` (`unit` | `aggregator`). Never deleted — so false-positive rate stays analysable across runs, a wrong dismissal can be revisited, and "found 8 → kept 1, dismissed 7" stays visible (itself the signal of whether finder/verifier work). An application of the **no-silent-drops** principle (don't lose would-be outcomes). Named `dismissed`, not `falsePositives` — it records *our verdict*, not ground truth (the user: "maybe some are interesting"). "Real but harmless" stays in `bugs[]` at `negligible`; only genuine non-bugs go here.

## Conventions

Schema is the canonical **structure**; prompts (`step-a`) carry **how-to-assign** (single-canonical-source). Runtime validator is draft-07 — **inline enums, no `$defs`/`$ref`**.

## See Also

- `aiqa-ula-feature.md`, `ula-bug-verification-track.md`, `single-canonical-source-discipline.md`, `feedback-schemas-as-enforcement-overreach.md`.
