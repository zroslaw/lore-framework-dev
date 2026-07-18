# Consistency Sweeps: Grep Catches Tokens, Reading Catches Prose

For a rename/restructure consistency pass, a clean grep is **necessary but not sufficient**. Grep finds mechanical references to the *old token*; it cannot find prose that became **semantically false** but shares no token with the change.

## The instance (2026-06-07, DF rename)

After the DF rename, a grep sweep for old tokens (`dev-aiqa`, `<repo>-aiqa`, `<unit>`, `index.md`, `dev/`) came back **clean**. But a **semantic read** of the step prompts found `split.md` still asserting that a unit id "becomes the unit's directory" — which is **false** under per-file granularity (the unit is a *field*, not a folder). Grep missed it because the stale sentence contained no renamed token. The same read surfaced the `source-sha` integrity bug (`rev-parse HEAD:<path>` vs `git hash-object`).

## The rule

Do **both**, every rename/restructure:

1. **Grep for the literal old tokens** — fast, catches mechanical references (paths, names, identifiers).
2. **Read the prose of the touched files** — catches statements that are now false but share no token with the rename (a layout claim, an invariant, an example that no longer holds).

The *read* is what surfaces semantic drift. When a user asks for a "gaps/inconsistencies pass" after a restructure, the grep is the warm-up; the read is the work.

## Why this generalizes

A rename changes *names*; a restructure changes *facts*. Names are greppable; facts are not. Any sweep that only matches the changed token verifies the easy half and silently passes the hard half. This is the sweep-time sibling of `canonicalize-testbed-fixes.md` (a green *run* is weak evidence) and `verify-before-acting-on-suspected-bugs.md` (verify state, not inference). It also complements the "pointer-AND-restatement" drift pattern in `parallel-reviewer-fanout-pattern.md` — restatement drift likewise hides where no shared token points back.

## See Also

- `parallel-reviewer-fanout-pattern.md` — the "pointer-AND-restatement" drift the read-the-prose lens is built to catch; round-2 filesystem-verification reviewer is this rule at review time.
- `verify-before-acting-on-suspected-bugs.md` — verify state directly; a clean grep is an inference, not a fact.
- `canonicalize-testbed-fixes.md` — sibling: a green run is even weaker than a clean grep.
- `single-canonical-source-discipline.md` — the discipline that *prevents* the restatement drift this rule *detects*.
- `df-per-repo-backbone.md` — the DF rename/restructure whose sweep produced this lesson.
- `deterministic-sweep-catches-check-blind-spots.md` — sibling lesson, opposite direction: LLM-alone misses mechanical existence rot at scale, where this topic shows grep-alone misses semantic drift.
