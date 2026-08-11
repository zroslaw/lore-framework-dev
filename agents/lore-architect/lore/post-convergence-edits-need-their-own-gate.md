---
lore: 1
type: topic
summary: "A gate result belongs to a specific artifact state — re-run or revert post-gate edits, and freeze the tree before spawning reviewers so the round has one state to certify."
parent: lore-context.md
---

# Post-Convergence Edits Need Their Own Gate

**A gate result belongs to a specific artifact state.** An edit made after the gates have passed is
ungated work, and the honest report says so.

## The instance (v30, 2026-07-25)

The order of work was: review loop converged (14 → 6 → 1 → 0 findings) → lifecycle suite green on 3/3
engines → **then** I noticed a weak-model fidelity gap in the Codex transcript and edited the doc twice
more to fix it.

Those two edits were outside both gates. The recheck that should have covered them was destroyed by an
unrelated macOS permission failure (`macos-documents-permission-loss-mid-session.md`), and by the time
it could run again the result was ambiguous — one scenario passed, one failed, and I could not
attribute the failure to my edit versus known weak-tier model variance without a further run.

## The rule

Two acceptable dispositions, no third:

1. **Re-run the affected gate** on the edited artifact.
2. **Revert the edit** back to the gated state and file the finding as follow-up.

What is *not* acceptable is reporting "converged and green" for an artifact that is neither, because
the last edits came after both. When I hit this I did say the edits were unverified and offered the
user the choice — that part was right; making the edits inside the gate window in the first place was
the error.

## Corollary — record what state a gate result belongs to

The harness's evidence is only as good as the artifact version it ran against. Record the commit or
working-tree state a gate result belongs to, or the result silently migrates onto a different artifact.
This is the same failure the "commit pending can accumulate across versions" note in
`versioning-release-types.md` guards against, one level down: there it's a version stamp drifting off
its commit, here it's a green run drifting onto edited files.

Practical shape: when reporting a gate, name the state — "19/19 at `<sha>`", "clean round against the
working tree as of the R4 fixes" — not just the count.

## Applies to both legs of pre-ship verification

- **Review convergence** (`/lr:trilens-loop`, `parallel-reviewer-fanout-pattern.md`) — a clean round
  certifies the tree the reviewers actually read. Edits after it are unreviewed, which is why the
  pattern already routes new edits back to the owning lens rather than assuming an earlier clean
  verdict still covers them.
- **Lifecycle suite** (`lifecycle-testing-harness.md`) — green certifies the doc text the engine
  actually executed. This is the sharper sibling of "pre-ship = pre-push": the push is not the only
  boundary that matters; each *edit* moves the boundary.

## Point it at the *input* too — freeze before spawning (v38, 2026-08-11)

The same discipline runs backwards. If a gate result belongs to one artifact state, then every
reviewer in a round must see the **same** state, and that state must still exist when their findings
arrive. On v38 round 2 I spawned three reviewers against an **uncommitted working tree** and kept
editing while they read. One opened its report with a process note: files had changed under it, one
finding had been fixed out from under it, and it asked to be re-run against a frozen snapshot. The
objection was correct, and it degrades the whole round — findings point at line numbers that have
moved, a reviewer can report a defect that no longer exists, and worse, a reviewer can *miss* one
because it read the already-fixed half of an inconsistent pair.

Practice, from round 3 which was run correctly:

- **Commit before spawning.** Name the commit SHA in the brief and say the tree is clean and frozen.
  Reviewers can then run `git diff <previous-tag>..HEAD` themselves — orientation they produce
  without the host handing over a diff.
- Freezing is about **immutability during the round, not finishedness**: reviewers can perfectly well
  be spawned against a commit that is not yet the final release commit.
- **Tag only after the loop ends**, so the release commit can gain follow-up commits without the tag
  ever pointing at a state no reviewer saw.
- Second benefit in this workspace specifically: it stops ungated work sitting dirty where a
  concurrent or unattended session can sweep it into an unrelated commit
  (`concurrent-session-committed-my-uncommitted-work.md`).

## See Also

- `execution-testing-catches-blind-ambiguity.md` — § pre-ship = pre-push, the discipline this sharpens.
- `lifecycle-testing-harness.md` — the gate whose result this constrains.
- `parallel-reviewer-fanout-pattern.md`, `trilens-loop-feature.md` — the review leg.
- `graduated-verification-confidence.md` — "unverified after the last two edits" is a confidence
  level, not a boolean failure; report it as such.
- `macos-documents-permission-loss-mid-session.md` — the environment failure that made the recheck
  uninterpretable in this instance.
- `verify-before-acting-on-suspected-bugs.md` — the sibling reflex on the diagnosis side.
- `concurrent-session-committed-my-uncommitted-work.md` — why a dirty tree is doubly unsafe here.
