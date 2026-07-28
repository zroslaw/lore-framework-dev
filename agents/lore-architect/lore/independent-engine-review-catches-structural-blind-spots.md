# Independent-Engine Review Catches Structural Blind Spots

A concrete new instance of the "sandboxed-review blind spot" / "gate cannot be a model self-report"
family (`a-gate-cannot-be-a-model-self-report.md`, `lore-beings-mvp-takeover-review.md`) — but this
time the axis is cross-*engine*, not cross-lens or sandbox-capability-blocking.

## The instance

Reviewing my own self-locate-off-Step-0-order proposal (round 1 of the v32 shortcut-bootstrap
design), Codex caught a structural flaw I'd missed: a generated shortcut lives *outside* the plugin
and cannot self-locate a plugin-internal file the way `skills/boot/SKILL.md` can. I'd verified the
*concept* (dual-install ambiguity is real, demonstrated on this machine) but not that specific
mechanism — and my own probe evidence, gathered afterward, ended up reinforcing Codex's correction
rather than my original claim.

Separately in the same review, two engines — Cursor and I — independently found the same
migration-6/`check.md` circularity bug (`fix-the-pointer-not-the-shipped-migration.md`) from
separate reads of the same worktree, before either had seen the other's finding. Per the existing
convergent-findings-are-strong-evidence principle (`parallel-reviewer-fanout-pattern.md`), that's
corroboration, not redundancy — now with a cross-engine instance to cite alongside the existing
cross-lens ones.

## How this differs from the sandbox/self-report family

`a-gate-cannot-be-a-model-self-report.md` and the sandboxed-review-blind-spot instance
(`lore-beings-mvp-takeover-review.md`) are about a check silently substituting unverifiable evidence
for real evidence — the failure mode is invisible because the gate *looks* like it ran. This
instance is different in kind: nothing was silently substituted. I fully engaged with the design
question and still missed a mechanism another engine caught, because a different engine has
different training data, different default assumptions, and a different angle of attack on the same
problem — closer to why independent human reviewers catch different bugs than why a broken sensor
reads "fine." Both are review-diversity arguments, but this one doesn't require an environmental
defect to occur; it happens on a routine, fully-functional review too.

## Operational note

Cross-engine review caught things a single strong model's self-review, and even a same-engine
multi-lens pass (`/lr:trilens-loop`), might not — different engines have different sandbox/tool-
access/training blind spots, the same way different lenses have different failure-mode blind spots.
Worth weighing for genuinely high-stakes design decisions, not routine changes — this was a
boot-path correctness fix, exactly the class where a false-green (or a false-confident single-engine
"looks right") is expensive. Doesn't replace `/lr:trilens-loop` for routine changes; it's a heavier,
occasional tool for design-level decisions where the coordination cost
(`cross-engine-team-substrate-validated.md`) is worth paying.

## See Also

- `a-gate-cannot-be-a-model-self-report.md`, `lore-beings-mvp-takeover-review.md` — the sandbox/
  self-report family this is adjacent to but distinct from (see § above for the distinction).
- `parallel-reviewer-fanout-pattern.md`, `trilens-loop-feature.md` — the same-engine multi-lens
  review this complements, not replaces.
- `cross-engine-team-substrate-validated.md` — the shared-folder substrate the review ran over.
- `fix-the-pointer-not-the-shipped-migration.md` — the corroborated bug this review pass found.
