# Subagent as Optimization vs Subagent as Semantics

A framework procedure that spawns subagents is doing one of **two structurally different things**, and
the distinction decides whether an engine is allowed to degrade that procedure to serial host-side
execution.

- **Subagent as optimization** — the subagent buys parallelism plus context isolation. Serial
  host-side execution reaches the *same answer*, just slower. Every pre-v30 fan-out site is this kind:
  `/lr:recall`, `/lr:consult`, `/lr:attach`, `/lr:merge`, conflict resolution.
- **Subagent as semantics** — the subagent's *independence from the caller* is the deliverable, not a
  speed-up. `/lr:trilens-loop` is the first of these: it exists precisely to remove the authoring
  session's bias toward its own work.

## Why it matters

Cursor's conservative `subagent-spawn` binding ("execute host-side, serially") is a **lossless**
degradation for every optimization-class site — which is exactly why it shipped in v20 and passed
19/19 lifecycle. Applied to a semantics-class procedure the same clause is **feature-destroying**: a
host reviewing its own changes is not a slower review, it is not a review at all. One profile clause,
correct in one case and invalid in the other.

## Operational rules

1. **Classify before writing the doc.** When adding a procedure that spawns subagents, decide which
   kind it is. If it is semantics-class, say so in the doc and state that there is **no host-side
   fallback** — the procedure stops and reports instead of degrading. **The obligation is on the doc
   stating its own classification, and it does not lapse when every current engine happens to have a
   native subagent mechanism.** I misread it that way once and nearly closed a real gap as moot; a
   review round returned it as a `BLOCKER` citing this rule. See
   `check-own-lore-before-dismissing-a-finding.md`.
2. **A profile's degradation clause needs a carve-out, not a blanket rule.** v30 added exactly that to
   `docs/engines/cursor.md`: semantics-class procedures (`trilens-loop.md`) must use native `Task`; the
   remaining optimization-class fan-outs default serial host-side until deliberately upgraded. **Merge**
   upgraded to `Task` on 2026-07-28 (`cursor-merge-via-task.md`) — still optimization-class, but no
   longer serial on Cursor. Recall, consult, attach version-reconcile, and conflict resolution remain
   serial until their own upgrade. Do not extend `Task` to those without evidence.
3. **Independence has a second level: the brief.** A cold-context subagent handed the caller's
   rationale is only nominally independent — see `parallel-reviewer-fanout-pattern.md` § Brief the
   goal, not the rationale.
4. **Don't read "the conservative profile passed the whole suite" as "the conservative profile is
   adequate."** It was adequate for the procedures that existed when it was validated. Every new
   procedure re-opens the question.

## Where this sits

This is a **third axis** on the engine-degradation question, orthogonal to the two I already track:

- **Model tier** — a weaker model executes the same doc differently
  (`execution-testing-catches-blind-ambiguity.md`, `haiku-ambiguity-detector.md`).
- **Capability availability** — the environment structurally blocks something the procedure depends on,
  so a branch never runs (the sandboxed-review blind spot in `role.md`; concrete instances in
  `lore-beings-mvp-takeover-review.md` and `macos-documents-permission-loss-mid-session.md`).
- **Procedure class** — this topic: whether the subagent mechanism itself is semantically load-bearing.

## See Also

- `trilens-loop-feature.md` — the first semantics-class procedure and the reason this axis got named.
- `cursor-engine-capabilities.md` — the profile whose degradation clause needed the carve-out.
- `cursor-merge-via-task.md` — optimization-class merge upgraded to `Task` on Cursor (2026-07-28).
- `cursor-task-free-text-brief-validated.md` — the probe that closed the brief-shape unknown.
- `docs-engines-convention.md` — the five bindings; `subagent-spawn` is the one this constrains.
- `multi-engine-portability-direction.md` — the direction this refines: parity is per-procedure-class,
  not per-engine.
- `codex-native-multi-agent-subsystem.md`, `claude-engine-capabilities.md` — the engines whose native
  mechanisms satisfy the semantics class today.
- `check-own-lore-before-dismissing-a-finding.md` — the near-miss where Rule 1 was reconstructed from memory and lost its obligation.
- `trilens-loop-v31-restructured.md` — where the semantics-class classification now lives in the doc itself (parked on `wip/lr-core-v31`).
- `naming-foundational-principles.md` — the meta-rule under which this earned its own topic.
