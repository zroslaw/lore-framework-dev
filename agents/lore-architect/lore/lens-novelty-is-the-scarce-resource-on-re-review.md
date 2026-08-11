---
lore: 1
type: topic
summary: "On a re-review, inventory the lenses already spent before choosing new ones; let the artifact's life stage pick the lens family, and add a claim-audit lens after a fix round."
parent: lore-context.md
---

# On a Re-Review, Lens Novelty Is the Scarce Resource

`parallel-reviewer-fanout-pattern.md` § Choose lenses per *round*, not per loop says the lens *kind*
must change between rounds. This is the same rule pushed one level out: when a release is reviewed
**again**, in a later loop or a later session, the scarce resource is not reviewer budget or rounds —
it is a lens the artifact has not already been given.

## Inventory the spent lenses first

v37 had been through **twelve** cold lenses across two earlier efforts before the user asked for
another TriLens over the same release. Reaching again for executability, contract integrity, or blast
radius would have bought thinking the release already had.

So the first move on a re-review is not choosing lenses — it is **enumerating the lenses already
spent**, from `versioning-release-types.md` and the session records. The inventory costs one grep,
and it is the thing that makes the new trio actually new. It also belongs in the ship record: "every
lens in this loop was chosen to be new" is a checkable claim; "three rounds, nine lenses" is not.

## Let the artifact's life stage choose the lens family

What the v38 inventory then suggested was a reframing, not a list: v37 was no longer a *proposal*, it
was a **shipped artifact with an installed base**. That picked the round-1 lenses on its own —
concurrency and idempotency in a live multi-session workspace, the hostile-reality input surface, and
three-engine parity — all asking what the released thing does in the world rather than whether its
design is sound. All three found real defects that nine prior lenses had not.

- **Pre-ship lenses ask "is this right?"** — design coherence, contract integrity, executability.
- **Post-ship lenses ask "what happens to this in a real, messy environment?"** — concurrency,
  hostile input, version skew, the state older versions left behind, cross-engine parity.

They are different questions and they find different bugs. Naming the life stage is usually faster
than picking three lenses directly.

## Claim audit — the standing lens for a round that follows fixes

After a round of *fixes*, a **claim audit** lens earns a slot: extract every checkable assertion the
new prose makes and test it. On v38 it independently confirmed the parser-equivalence and
git-semantics claims and caught the one place a release note said "everywhere" while a fourth site
still disagreed. Fix rounds generate confident prose, and confident prose is where overclaims live.

This pairs with the standing round-2 lens ("did the fixes fix it, and did they break anything") —
that one audits the *code and behavior* a fix round produced, this one audits the *claims* it wrote.

## See Also

- `parallel-reviewer-fanout-pattern.md` § Choose lenses per *round*, not per loop — the within-loop
  form of this rule, plus the lens catalog.
- `trilens-loop-feature.md` — the loop re-spawns reviewers each round but never says re-pick the
  lenses; this judgement stays in lore.
- `a-fix-is-a-change-and-changes-need-review.md` — why a fix round needs a round of its own.
- `versioning-release-types.md` — where the spent-lens inventory is recoverable per version.
- `check-own-lore-before-dismissing-a-finding.md` — the triage-side discipline for what the new
  lenses return.
