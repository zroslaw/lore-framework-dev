**Before repointing, deleting, or "fixing" something you believe is broken, verify the actual filesystem/state directly. Don't act on an inference — especially a dangling-reference claim.**

Stating a wrong diagnosis to the user is cheap to correct; *acting* on it is not. The most dangerous move is "fixing" a bug in code you did **not** just write, on the strength of an inference.

## The v14 near-miss

While wiring `/lr:check` #19, I issued two parallel Read calls (`consistency-checks.md` and `check.md`) and **misattributed the results** — concluded "`docs/check.md` doesn't exist, the skill points to a dangling target" and was about to "fix" `skills/check/SKILL.md` to point elsewhere. Reality (caught by an `ls`+`grep` verification before editing): `check.md` exists and is the real catalog; SKILL.md was already correct. "Fixing" it would have *introduced* the break.

Root of the confusion: `consistency-checks.md` is a **lore-topic name**; the plugin doc is `check.md`. Two similarly-purposed names for different-layer artifacts. (See `consistency-checks.md` for the standing reminder.)

## Operational rules

- **Verify state directly before mutating it.** `ls`, `cat`, `git` the thing you think is broken before any edit/delete/repoint. An inference is a hypothesis, not a fact.
- **Attribute parallel tool-call results carefully.** When one of N parallel reads errors (or returns empty), confirm *which* path failed before reasoning from it. Empty-result-from-wrong-path is a classic false "missing file" (same trap as `tooling-cwd-safety.md`'s empty-Glob).
- **Diagnosis is cheap, action is not.** When about to fix a "bug" in code you did not author this session, re-verify first. Asymmetric cost: a wrong claim costs a sentence; a wrong fix costs a regression plus the debugging to find it.

## Composition

Same spirit as the review/verification disciplines: look before you assert, and look again before you act. The reviewer fan-out's filesystem-verification lens (`parallel-reviewer-fanout-pattern.md`) is this rule applied at review time; the sonnet-subagent review (`sonnet-subagent-review-pattern.md`) is a second pair of eyes for the same reason.

## See Also

- `consistency-checks.md` — carries the standing `check.md` vs `consistency-checks.md` naming reminder that triggered the near-miss
- `tooling-cwd-safety.md` — the empty-result-means-wrong-state sibling (empty Glob ⇒ wrong CWD, not missing file); same "verify before concluding broken" reflex
- `parallel-reviewer-fanout-pattern.md` — the correctness lens runs real bash (filesystem verification) precisely to catch what prose review infers wrongly
- `sonnet-subagent-review-pattern.md` — second-pair-of-eyes discipline for high-stakes changes
- `plugin-manifest-versioning.md` — its open auto-invalidation question is a "verify before acting" candidate (test empirically before dropping the cache-clear footer)
