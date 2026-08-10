---
lore: 1
type: topic
summary: "In a three-round TriLens on v37, rounds 2 and 3 each caught a defect introduced by the previous round's own fix — a review round's output is unreviewed code, and stopping after round 1 ships it."
parent: lore-context.md
---

# A Fix Is a Change, and Changes Need Review

**What happened.** The v37 TriLens ran three rounds over the whole release. Round 1 found ten things
and I fixed them. Round 2 found that **one of my round-1 fixes was worse than the bug it fixed**: to
stop Ctrl-C leaving a half-written clone, I had the signal handler delete any clone with a live
in-flight marker — but the handler killed the process group and deleted immediately, so a Ctrl-C
landing in the few instructions *after* a successful clone deleted a good repository. I traded a
recoverable annoyance for data loss. Round 3 then found that a round-1 doc edit — "run the Register
Agent procedure, skipping its Agents-section step" — skipped a bundled sub-item that ensures the
`CLAUDE.md` import stub, so bulk registration silently stopped repairing the exact whole-engine
outage v37 was built to close.

Both defects were mine, both were introduced *while fixing something else*, and neither was
detectable from the finding that prompted the fix.

**The rule.** A fix is a change. It has the same defect rate as the code it edits, and it is written
under worse conditions: narrow attention on one reported symptom, no fresh read of the surrounding
contract, and the satisfying feeling of closing an item. A review round that ends with fixes applied
has produced **unreviewed code**. Round 1 ending clean is a real stopping condition; round 1 ending
with ten fixes is not.

This is why the loop's "repeat if the changes are considerable" is not a formality, and why the
re-resolve-the-scope instruction matters: the scope of round N+1 includes round N's diff, and that
diff is the part most likely to be wrong.

**The second-order version.** Round 2's fix for my round-1 fix *also* had a flaw — a HEAD-resolves
guard that would preserve a truncated clone forever. The escape from infinite regress is not another
round; it is picking the failure mode you can afford. A directory this run created and never
confirmed complete contains nothing of the user's, so deleting it is lossless and re-cloning is
cheap. The third version has no guard at all and is shorter than both attempts. **When a fix needs a
predicate nobody can get right, the design is wrong, not the predicate.**

**One more thing this round taught.** A reviewer's BLOCKER arrived with an empirical claim — "verified
in bash 3.2, the line after the self-kill is never reached". It did not reproduce here across three
process-group configurations. The hardening was still worth keeping (it removes a dependency on
signal-delivery timing for free), but it went in as hardening, and the record says so. A reviewer
saying "I verified" is evidence, not a gate; see
[a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md) and
[a-gate-that-died-is-not-a-gate.md](a-gate-that-died-is-not-a-gate.md). Repeating someone else's
unverified claim in a commit message is how a claim becomes a fact with no owner — the same failure
as [codex-shortcuts-are-workspace-local.md](codex-shortcuts-are-workspace-local.md), one layer up.

See also [versioning-release-types.md](versioning-release-types.md) for v37's gate record.
