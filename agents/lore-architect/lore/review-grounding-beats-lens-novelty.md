---
lore: 1
type: topic
summary: "When a review loop stalls, the instrument to change is grounding, not lens novelty — license a reviewer to distrust the document's claims about other files and verify them against those files."
parent: lore-context.md
---

# When a Loop Stalls, Change the Grounding, Not the Lens

When a three-lens loop hits its round cap,
[non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md)
prescribes one deep unconstrained cold reviewer as the substitute for a fourth round. On the v46
lore-sync spec (2026-09-13) that reviewer returned **BLOCK with thirteen findings — three BLOCKER —
after nine prior lens passes had found none of them.**

**What made the difference was not depth of reasoning. It was grounding.** The brief told the
reviewer to verify the spec's claims against the live framework files rather than trust them, and it
did: it read `update.md`, `resolve-conflicts.md`, `workspace-init.md`, `engines/cursor.md` and
`process-merge.md` and compared. All three blockers were claims the spec made about another document
that had drifted or was never true:

- `update.md` states the zero-ahead condition in **three** places; the spec removed one and
  explicitly preserved another, so the fix was inert
  ([a-change-set-is-wider-than-its-diff.md](a-change-set-is-wider-than-its-diff.md)).
- `resolve-conflicts.md`'s subagent brief still commissioned push-and-retry work the spec's own edits
  removed.
- `workspace-init.md:297` contains a sanctioned `git add -A` that the spec's new git-safety
  convention would have outlawed on sight.

## Why lenses cannot find these

A lens reads the artifact **on its own terms** and judges coherence. Coherence is exactly what a
much-revised spec has plenty of; every internal cross-reference lines up because the author kept them
lined up. The residual risk lives at the document's boundary with the files it describes, and a
reviewer only crosses that boundary if told to.

So the axis to vary when novelty runs out is not which question to ask, but **what the reviewer is
allowed to treat as fact**:

- Change the **unit** — review a subset, a call site, an installed population
  ([lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md)
  § Change the unit).
- Change the **grounding** — send the reviewer to the filesystem, with the document demoted from
  premise to hypothesis. This topic.

## Operational

Put it in the brief explicitly: *"verify every claim this document makes about another file against
that file; its assertions about current code may be old."* **The reviewer will not do it by
default** — unlicensed, distrusting the author's description of their own codebase reads as rudeness,
so it silently accepts the premises. This is the general form of
[parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md)
§ Filesystem-grounded correctness, which asked for commands proving listed claims; here the reviewer
also decides *which* claims are worth checking.

The same reflex, applied to my own work, is
[verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md); the reason a
self-assessment cannot substitute is
[a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md). Worked instance:
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).
