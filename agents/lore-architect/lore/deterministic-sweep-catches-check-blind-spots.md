# Deterministic Sweeps Catch What LLM-Executed Checks Miss at Scale

At current scale (147 lore topics in lore-architect alone), an LLM read-through of `/lr:check`'s
reference-integrity checks (#9–10) misses cross-reference rot it's nominally supposed to catch.

## The Finding (2026-07-18 review)

A short Python script did a mechanical regex sweep: every `.md` reference in `lore-context.md`
and every lore topic, checked for a matching file in `lore/`; plus every `docs/*.md` reference
across the plugin tree, checked against real files. It found **14 unresolved references**, at
least 8 of them genuine rot from renamed/deleted files: `contributions-feature.md`,
`workspace-sync.md`, `dev-repo-lore.md`, `dev-module-conventions.md`, `codex-binding-design.md`,
`beta-refinement-workflow.md`, and two Codex-multiagent filename variants
(`codex-multiagent-research.md`, `codex-multiagent-live-capture.md`).

A prior `/lr:check` run — the same checks, run by an LLM reading files directly — had reported
clean.

## Why

The gap isn't a missing check; `/lr:check` #9–10 promise exactly this coverage. It's that an
LLM-executed mechanical check degrades at **O(topics × references)** in a way a deterministic
script doesn't — extraction reliability drops as the corpus grows even though the check's *logic*
(does this filename exist?) never changed. This is the empirical evidence behind backlog item
"script-back the mechanical subset of `/lr:check`" (`workdir/what-to-improve.md` item A1) — cite
this directly when that item is designed, rather than re-deriving the case.

## Operational Takeaway

When auditing lore/doc reference integrity at this scale — or running `/lr:check` for real, not
just trusting a clean report — prefer a quick script-based sweep for the purely mechanical subset
(existence checks, version-string comparisons, glob-grammar validation). Reserve the LLM for
checks that are genuinely semantic (heading-vs-summary drift, staleness judgment calls), where a
script can't substitute.

This composes with `consistency-sweep-read-not-just-grep.md`, a sibling lesson pointed the other
way: that one shows grep-alone misses semantic drift (meaning changed, no token changed) and
argues for adding a read; this one shows LLM-alone misses mechanical existence rot at scale and
argues for adding a script. Together: match the checking method to the nature of the check —
deterministic tooling for mechanical properties, LLM judgment for semantic ones.

## See Also

- `consistency-checks.md` — the check catalog; #9–10 are the checks this finding is about
- `consistency-sweep-read-not-just-grep.md` — sibling lesson, opposite direction
- `verify-before-acting-on-suspected-bugs.md` — verify state directly rather than trusting a prior
  report
- `framework-improvements-backlog.md` — item A1, the script-back-the-mechanical-subset fix
- `feedback-don-t-defer-completable-scope.md` — the rot cleanup itself is a completable bounded
  sweep, not a deferred follow-up
