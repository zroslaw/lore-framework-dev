# A Diverged Branch's Two-Way Diff Is Not a Merge Preview

Found 2026-07-27, trilens-loop round 1 over the parked v31 branch (release-truthfulness lens).

## The false BLOCKER

A cold reviewer reported a `BLOCKER`: `lore-framework-dev`'s `wip/lr-core-v31` branch had forked from
an older commit on `main`, and `main` had since advanced four commits. The reviewer read
`git diff main..HEAD` and saw it **delete** those four commits' files, concluding a merge would
silently discard four finalized sessions' worth of lore.

The observation (branch is stale relative to `main`) was true. The consequence (merge discards work)
was not. `git diff main..HEAD` between two diverged histories renders the *other* side's exclusive
commits as deletions — that's a property of how a two-way diff displays divergence, not a preview of
what an actual merge produces.

## Verification and outcome

Verified with `git merge-tree --write-tree main <branch>`: zero conflicts, and the resulting tree
contained **both** `main`'s four commits' content **and** the branch's own new material. Nothing would
have been lost. The `BLOCKER` was overridden and the override stated explicitly — the trilens loop's
own rule (never finish on an outstanding BLOCK without saying you're overriding it) is what kept this
from silently sliding into "the loop says ship."

## Generalizable rule

A cold reviewer (or anyone) evaluating a diverged branch's readiness-to-merge should never infer merge
behavior from a two-way `diff` against the target — `git diff A..B` and "what happens when A and B
merge" are different questions, and the first can look alarming while the second is fine. Use
`git merge-tree` (or an actual test merge in a throwaway location) to answer the merge question
directly.

This is a specific instance of `verify-before-acting-on-suspected-bugs.md`, promoted to its own topic
because the failure mode — misreading a diff's rendering convention as ground truth — is a distinct,
nameable trap rather than a generic "double-check it" reminder.

## See Also

- `verify-before-acting-on-suspected-bugs.md` — the parent discipline this is a specific instance of.
- `v31-lr-core-parked-2026-07-25.md` — the concrete session and branch this happened on.
- `post-convergence-edits-need-their-own-gate.md` — adjacent framing about what a review result
  actually certifies; this is about what a *diff* actually certifies.
