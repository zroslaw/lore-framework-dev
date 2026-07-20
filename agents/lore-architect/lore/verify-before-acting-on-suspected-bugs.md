**Before repointing, deleting, or "fixing" something you believe is broken, verify the actual filesystem/state directly. Don't act on an inference — especially a dangling-reference claim.**

Stating a wrong diagnosis to the user is cheap to correct; *acting* on it is not. The most dangerous move is "fixing" a bug in code you did **not** just write, on the strength of an inference.

## The v14 near-miss

While wiring `/lr:check` #19, I issued two parallel Read calls (`consistency-checks.md` and `check.md`) and **misattributed the results** — concluded "`docs/check.md` doesn't exist, the skill points to a dangling target" and was about to "fix" `skills/check/SKILL.md` to point elsewhere. Reality (caught by an `ls`+`grep` verification before editing): `check.md` exists and is the real catalog; SKILL.md was already correct. "Fixing" it would have *introduced* the break.

Root of the confusion: `consistency-checks.md` is a **lore-topic name**; the plugin doc is `check.md`. Two similarly-purposed names for different-layer artifacts. (See `consistency-checks.md` for the standing reminder.)

## Verify *which* bug, not just *whether* it's a bug (2026-06-07)

The discipline extends to **diagnosis among competing causes**, not just confirming a bug exists. The ULA workflow failed at an args guard with **two** plausible causes: payload **size** (a huge `args`) vs **string-coercion** (`args` arriving as a JSON string). The size fix was implemented first — and did **not** fix it; the cause was coercion, proven afterward by a 3-line repro (a one-line `JSON.parse` guard was the real fix).

Rule: **when a failure has ≥2 plausible causes and one is cheap to confirm (a minimal repro, or just inspecting the actual call/inputs), confirm before implementing the more invasive candidate.** Flagging the invasive fix's uncertainty up front is good; a repro first is better — it saves the round-trip. (The size fix wasn't wasted here — it unified the split-vs-unit read path and made `source-sha` honest — but that was luck, "good change, wrong bug.") See `workflow-primitive-operational-notes.md` § `args` can arrive as a string.

## Diagnose the *mechanism* before naming a weakness (2026-06-13)

The "verify *which*, not just *whether*" rule extends to **architectural critique**: name the problem from the *verified mechanism*, not a plausible-sounding label — a wrong label misdiagnoses the fix.

In the 2026-06-13 architecture review I called `lore-context.md` "a hand-maintained denormalized index / two-write problem." The user corrected it: `lore-context.md` is **agent-maintained at merge** (not by hand), and the intended design (compacted working-knowledge + summary-topic references) has no denormalization at all. The real defect was **drift** — the actual file had accreted a full topic index + version-history narrative against its own design intent. Same surface symptom (bloat), different mechanism, different fix: a *shape discipline* in merge (`lore-context-shape-discipline.md`, shipped v17), not de-duplication of an index. Had I acted on the "denormalized index" label, I'd have built the wrong mechanism.

Rule: **before naming a weakness, read the real implementation and confirm the mechanism that produces the symptom.** A plausible label for a real symptom is still a hypothesis; the fix follows the mechanism, not the label. This is the critique-time face of "verify which bug" — adjacent to `lore-context-shape-discipline.md`.

## Verify what the code/prompt says before answering "did we implement X" (2026-06-08)

Asked whether a behaviour is implemented — especially in code/prompts you didn't just write, or wrote across sessions — **read the actual artifact before answering**; don't answer from memory of the design intent. Two v16 instances:

1. I claimed ULA's bug-finding step was "clean-room / context-blind" — **wrong**. Clean-room is a Step B (scenarios) property = "don't peek at existing tests"; the bug step (A) is explicitly context-*aware* (reads callers/callees). I'd conflated two adjacent concepts. Caught only by reading the step prompts when the user challenged "did you miss this?".
2. The user asking "did we implement the context-aware finding I requested?" is a *factual* question about the prompts — answered by reading them, not by recalling the design.

Distinguish adjacent concepts before asserting (clean-room-vs-tests ≠ context-blind). Don't reflexively agree OR defend — verify. Sibling: `consistency-sweep-read-not-just-grep.md`.

## Operational rules

- **Verify state directly before mutating it.** `ls`, `cat`, `git` the thing you think is broken before any edit/delete/repoint. An inference is a hypothesis, not a fact.
- **Attribute parallel tool-call results carefully.** When one of N parallel reads errors (or returns empty), confirm *which* path failed before reasoning from it. Empty-result-from-wrong-path is a classic false "missing file" (same trap as `tooling-cwd-safety.md`'s empty-Glob).
- **Diagnosis is cheap, action is not.** When about to fix a "bug" in code you did not author this session, re-verify first. Asymmetric cost: a wrong claim costs a sentence; a wrong fix costs a regression plus the debugging to find it.
- **Confirm the *right* cause before the invasive fix** (see section above) — verification is about *which* bug, not only *whether*.

## Composition

Same spirit as the review/verification disciplines: look before you assert, and look again before you act. The reviewer fan-out's filesystem-verification lens (`parallel-reviewer-fanout-pattern.md`) is this rule applied at review time; the sonnet-subagent review (`sonnet-subagent-review-pattern.md`) is a second pair of eyes for the same reason.

## See Also

- `consistency-checks.md` — carries the standing `check.md` vs `consistency-checks.md` naming reminder that triggered the near-miss
- `tooling-cwd-safety.md` — the empty-result-means-wrong-state sibling (empty Glob ⇒ wrong CWD, not missing file); same "verify before concluding broken" reflex
- `parallel-reviewer-fanout-pattern.md` — the correctness lens runs real bash (filesystem verification) precisely to catch what prose review infers wrongly
- `sonnet-subagent-review-pattern.md` — second-pair-of-eyes discipline for high-stakes changes
- `plugin-manifest-versioning.md` — its open auto-invalidation question is a "verify before acting" candidate (test empirically before dropping the cache-clear footer)
- `consistency-sweep-read-not-just-grep.md` — sibling: a grep sweep verifies tokens; only *reading the prose* verifies semantics (a rename sweep near-miss)
- `canonicalize-testbed-fixes.md` — sibling: verify what actually persisted to disk from a testbed session before declaring a fix done
- `hot-path-latency-can-expose-latent-test-timing-races.md` — the same "confirm which cause, not just whether it's broken" discipline applied to a test-failure diagnosis (stash-and-rerun A/B, not assuming new code is wrong)
- `workflow-primitive-operational-notes.md` — the size-vs-coercion misdiagnosis this session's "which bug" lesson came from
- `lore-context-shape-discipline.md` — the v17 fix that followed from diagnosing the *drift* mechanism (not the mislabeled "denormalized index"); the architectural-critique instance above
