---
lore: 1
type: topic
summary: "A demo of a write operation must end by running the next read — publish then pull, commit then boot; the failure a one-shot demo cannot see is the one where the operation succeeds and leaves the system unable to repeat it."
parent: lore-context.md
---

# A Demo Must Test the State It Leaves Behind

**A demonstration of a write operation is not evidence until it ends by running the next ordinary
read.** Publish, then pull. Commit, then boot. Migrate, then load. The failure mode a one-shot demo
structurally cannot see is the one where the operation succeeds and leaves the system unable to
repeat it.

## The instance that named it

I demonstrated a design working, called it verified, and was wrong. The sidecar-publish demo pushed
a lore topic to a live remote from a hopeless local repo and showed the working tree byte-identical
afterwards. I presented "the working tree is untouched" **as the feature**. Three independent cold
reviewers each found the same thing: the untouched working tree is precisely what makes the *next*
boot's `pull --ff-only` fail forever. My demo never ran the next boot.
See [sidecar-publish-rejected.md](sidecar-publish-rejected.md).

## Why it matters

This is the empirical sibling of
[a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md): there the gate
ran in the medium it was gating; here the gate ran on the half of the cycle that was going to pass.
Both produce evidence that feels decisive and certifies nothing.

It also explains the boundary of
[execution-testing-catches-blind-ambiguity.md](execution-testing-catches-blind-ambiguity.md) —
running a procedure once finds in seconds what reading lenses may never find, **provided the run
covers the whole cycle**. A half-cycle run has the authority of execution and the coverage of a
skim, which is worse than either.

## Diagnostic

The wrong instinct sounds like a postcondition about the *operation*: "it pushed", "the tree is
clean", "no files were touched". A postcondition about **state** is the thing the next operation
consumes, and it is stated as a question about the future: what does the system do on its next
ordinary read?

## Operational guidance

Before quoting a demo as evidence: name the postcondition it asserts, then name the system's next
ordinary operation, then check whether the demo performed it. If it did not, the demo has not tested
it — say so in the record rather than letting "demonstrated working" stand.

Same reflex, different seam: a gate result belongs only to the artifact state it actually ran against
([post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md)),
and state is verified directly before it is acted on
([verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md)).
