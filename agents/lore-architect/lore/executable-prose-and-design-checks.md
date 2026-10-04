---
lore: 1
type: area
summary: "Why procedures fail to execute and what to change (structure, not wording), plus design-time checks for guards, approval gates, intervals and optional steps."
parent: lore-context.md
---

# Executable Prose and Design Checks

Rules for writing procedures an executor will actually follow, and for designing guards that don't fail in the intersections. Moved from `lore-context.md`; bodies live in the members.

## Standing rules

- **When a procedure doesn't execute, change structure — not wording.** Sharpest measured case:
  **required literal output is the first thing an executor drops**, against prose already at maximum
  emphasis. Three shapes immune to emphasis — the **terminal step** that publishes an outcome (fix:
  an observable postcondition where the artifact is assembled); an obligation's **location** in a doc
  long enough to be paged; anything the model can **copy instead of compute**. See
  `required-literal-output-is-what-models-drop.md`,
  `the-terminal-step-is-the-step-that-gets-dropped.md`,
  `instruction-location-beats-emphasis-in-long-docs.md`, `models-copy-what-they-should-compute.md`.

- **Decide where the guardrail lives before writing the topic** — lore is retrieved when a task cues
  it, and a one-off command cues nothing. Name the point-of-use site (script check, exact command,
  test) as part of the fix, and prefer a deterministic check over a human prep step
  (`point-of-use-guardrails-beat-recorded-lore.md`).

- **Design-time checks:** preserve validation when widening sources; derive diagnostics and remedies
  from the same predicate; use tri-state lock claims; make file durability structural; update the
  approval surface when adding writes. **Price an interval constant against the real event cadence
  and the knob it may silently override** (`a-rate-floor-is-wrong-in-both-directions.md`). **An
  optional step's every exit continues on the pre-feature path**
  (`an-optional-step-must-fail-back-to-baseline.md`).
  The underlying patterns route through
  `system-design-principles.md`, `one-question-one-code-path.md`,
  `a-reported-error-is-not-proof-the-file-survived.md`, and
  `adding-a-write-means-updating-the-approval-gate.md`.

## Members

- [required-literal-output-is-what-models-drop.md](required-literal-output-is-what-models-drop.md)
- [the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md)
- [instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)
- [models-copy-what-they-should-compute.md](models-copy-what-they-should-compute.md)
- [appended-docstring-step-must-match-execution-position.md](appended-docstring-step-must-match-execution-position.md)
- [step-number-cross-references-fail-silently.md](step-number-cross-references-fail-silently.md)
- [adding-a-write-means-updating-the-approval-gate.md](adding-a-write-means-updating-the-approval-gate.md)
- [per-site-authoring-is-not-duplication.md](per-site-authoring-is-not-duplication.md)
- [single-canonical-source-discipline.md](single-canonical-source-discipline.md)
- [one-question-one-code-path.md](one-question-one-code-path.md)
- [short-circuit-on-the-condition-not-a-proxy.md](short-circuit-on-the-condition-not-a-proxy.md)
- [classification-tables-enumerate-exit-paths-not-interesting-cases.md](classification-tables-enumerate-exit-paths-not-interesting-cases.md)
- [an-optional-step-must-fail-back-to-baseline.md](an-optional-step-must-fail-back-to-baseline.md)
- [scripted-prose-edit-needs-a-read-back.md](scripted-prose-edit-needs-a-read-back.md)
- [self-documenting-payload-vs-heading-delimiters.md](self-documenting-payload-vs-heading-delimiters.md)
- [widening-a-source-drops-its-validation.md](widening-a-source-drops-its-validation.md)
- [a-change-set-is-wider-than-its-diff.md](a-change-set-is-wider-than-its-diff.md)
- [a-rate-floor-is-wrong-in-both-directions.md](a-rate-floor-is-wrong-in-both-directions.md)
- [guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md)
- [consistency-sweep-read-not-just-grep.md](consistency-sweep-read-not-just-grep.md)
