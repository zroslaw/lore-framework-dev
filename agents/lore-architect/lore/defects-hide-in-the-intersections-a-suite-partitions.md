---
lore: 1
type: topic
summary: "v46's five review blockers were each unreachable by its own 42-test suite; the five hiding places — between test classes, in another module's contract, in unvaried configuration, in time, in a later fix's branch."
parent: lore-context.md
---

# Defects Hide in the Intersections a Test Suite Partitions Away

v46 shipped with a 42-test suite written alongside the implementation, and three review rounds
found **five blockers, none of which that suite could reach**. The pattern is worth keeping because
it says *where* to look, rather than "test more":

- **Between two test classes that each cover half.** `TestDryRun` had no worktree fixture;
  `TestWorktrees` never passed `--dry-run`. Their intersection crashed the whole run.
- **In a contract owned by a different module.** The workspace-repo staging scope collided with
  `workspace-push`'s published promise; nothing in the new module's own tests could see it
  ([a-new-command-inherits-its-neighbours-published-promises.md](a-new-command-inherits-its-neighbours-published-promises.md)).
- **In configuration the tests never vary.** `core.worktree` redirection — every fixture was an
  ordinary clone ([git-dash-c-needs-toplevel-guard.md](git-dash-c-needs-toplevel-guard.md)).
- **In the time dimension no unit test has.** Merge ownership claimed after the merge instead of
  before was only visible by asking "what if it dies *here*".
- **In the branch a later fix introduced** —
  [a-fix-s-regression-test-misses-the-branch-the-fix-added.md](a-fix-s-regression-test-misses-the-branch-the-fix-added.md).

**Evidence for the on-request gate policy**
([feedback-pre-ship-gates-on-request.md](feedback-pre-ship-gates-on-request.md)): review here was
not redundant with the deterministic suite, it was **orthogonal** to it, and the suite's authorship
alongside the code is exactly why
([a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md)). The converse
is already recorded — review is blind to execution fidelity
([execution-testing-catches-blind-ambiguity.md](execution-testing-catches-blind-ambiguity.md)).
Three instruments, three blind spots.

**Cheap operational tightening that came out of it:** brief one reviewer per round on a lens that
**reads outward** — system fit, neighbouring contracts, release completeness — not only inward at
the new code.
