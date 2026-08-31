---
lore: 1
type: topic
summary: "Release notes describe gates that are still running when they are written, so they are the artifact most likely to be false at push time — re-audit the release's own claims about itself as the last pre-push step."
parent: lore-context.md
---

# A Release Record Goes Stale While You Fix the Release

v39's release notes asserted **"Not run: multi-lens TriLens review"** while the TriLens loop was
underway and its findings were being applied — and the deterministic test count was wrong in three
successive states (429 written, 431 after one fix round, 432 actually discovered). Each was true when
written and false by the time anyone would read it.

The cause is structural, not carelessness: a release record describes gates whose results do not
exist yet when the record is drafted, and then every review round changes the thing the record
describes. Nothing recomputes it. It is the one artifact in a ship whose subject is the ship itself,
so it decays once per round while everything else decays only when touched.

Standing practice, as the **last** step before tag and push:

- Re-audit every self-referential claim in the release notes against the tree being pushed — gate
  dispositions, review rounds and findings counts, test counts, what was waived, what is unreviewed.
- **Measure counts, do not derive them.** The 431 was arrived at by adjusting a previous number
  rather than running the suite; the real figure was 432 discovered / 384 run / 48 skipped, and
  stating all three is more useful than a single total that hides the skipped real-engine tier.
- Keep a **claim-audit lens** in any round that follows fixes
  ([parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md) already names it as a
  standing slot) — on v39 that lens is what caught the release denying its own review.
- Record the honest shape even when it is unflattering: v39 ships with "no reviewer returned clean on
  the shipped tree," because the substitute round's own fix is unreviewed.

## Presence before accuracy (v44, 2026-08-31)

The audit above assumes the release notes *make* self-referential claims. v44 was one step short of
that: `release-notes/44.md` was complete on what changed and carried **no Verification section at
all** — no gate dispositions, no "what remains untested", no known limits. The full and accurate
gate record existed the whole time, in my own lore.

An accuracy audit passes cleanly over an absent section. There is nothing there to look wrong.

So the pre-push audit has two steps, in this order:

1. **Presence** — does the file have a Verification section and, where applicable, Known Limits?
2. **Accuracy** — is every claim in them true of the tree being pushed?

Note the adjacency: v42 shipped with its gate paragraph left as an unreplaced assembly-time
placeholder, and v44 nearly shipped with no such paragraph at all. Two consecutive-ish releases,
two forms of the same gap, which is enough recurrence to earn a mechanical check rather than another
rule — see [consistency-checks.md](consistency-checks.md) § When a ship's claim earns a check.

**Write the gate record into the release notes first, then copy it into lore — not the reverse.**
The direction matters because recording it in lore satisfies every discipline I hold and *feels*
like completion, while the artifact the user actually reads stays empty. Lore is my record; the
release notes are theirs.

## See Also

- [versioning-release-types.md](versioning-release-types.md) § Backfill discipline — the sibling rule
  for this history list, and the v39 entry this practice produced.
- [gate-waiver-is-a-record.md](gate-waiver-is-a-record.md),
  [a-gate-that-died-is-not-a-gate.md](a-gate-that-died-is-not-a-gate.md) — the disposition vocabulary
  a re-audit has to get right: passed, waived, did not run.
- [fix-defects-are-context-errors.md](fix-defects-are-context-errors.md) — why the prose describing a
  fix is the part most likely to be wrong, release notes included.
- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md) — a
  gate result belongs to a specific artifact state; the record must name which.
- [consistency-checks.md](consistency-checks.md) § When a ship's claim earns a check — where the
  presence gap above should be closed mechanically.
