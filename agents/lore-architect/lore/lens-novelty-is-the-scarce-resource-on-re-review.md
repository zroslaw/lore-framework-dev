---
lore: 1
type: topic
summary: "On a re-review, inventory the lenses already spent before choosing new ones; life stage picks the lens family, a fix round adds a claim audit; and when novelty runs out, change the unit and the question rather than the rigor."
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

**A third, cheaper companion: the redundancy pass.** After a fix round, also ask *what does this now
say twice?* A fix adds a mechanism, and the new mechanism often re-expresses a fact an existing one
already carried — two overlapping enums, a state duplicating a lock file's existence, a stored
timestamp the filesystem already keeps. Unlike the claim audit, this one needs no cold context and no
review slot: the defects are visible in the diff. Note that a simplicity lens run *before* the fix
round does not cover it, because it only ever saw the revision it was given. See
`fix-defects-are-context-errors.md` § The second shape.

## Life stage also picks the lens on a pre-implementation doc

The pre-ship / post-ship split above has a third stage worth naming: a **design doc awaiting
handover**. Its failure mode is neither unsound reasoning nor messy-environment behavior but
**unbuildable specificity**, so the standing slot there is the **implementation-fidelity (executor)
lens** — briefed as the engineer who must build it from the document alone and cannot ask the
authors anything, and explicitly instructed to verify the doc's claims about existing code. On the
2026-08-23 design-doc review it out-yielded both a lean-design lens and a runtime-failure-modes lens
on *factual* defects. Full brief shape and case: `parallel-reviewer-fanout-pattern.md` § Lens choice.

## Novelty picks the lens, life stage picks the family — and ordering decides when

A third axis, learned when a loop failed to converge (2026-09-13): **spend the expensive lenses
early.** The two that found the largest holes in that spec — the **operator's recovery experience**
and **new persistent state examined as state** — were both spent in the last rounds, after the
cheaper structural lenses had already driven two rounds of fixes. Any round that introduces a state
file or a new stopping point should get those two lenses *in that round*, not two rounds later. See
`non-convergence-diagnose-before-reviewing-again.md`, which also covers what to do when the cap
arrives anyway.

## Change the unit, and the question, before adding rigor

When novelty itself runs out, the next move is not a new lens — it is a new **unit** of review. The
v46 spec had spent eleven lenses across three rounds (adversarial, simplicity ×4,
framework-coherence, alternative-designs, executor fidelity, conflict-classification, operator
recovery, claim audit, marker-as-state, first-principles regression) and still would not converge
(14 → 16 → 13 findings). Every one of them was a **correctness** lens asked of the **whole
document**.

Round 4 changed neither rigor nor model tier. It changed two other things, and found six real
findings including a BLOCK where the correctness lenses had stalled:

- **The unit** — Tier A alone, as a shippable artifact, instead of the whole spec.
- **The question** — not "is this right?" but "does this ship, to real users, on the tree that
  exists?"

The three lenses then followed from that: tier-boundary/partial-ship, call-site/integration reality
(read the shipped call graph, not the spec's prose), and installed-population/first-boot-after-upgrade.
All three are **situational** — they ask what happens when the artifact meets a specific reality —
where the spent eleven were all **analytical**.

**The move: when correctness lenses stop yielding, the remaining risk is usually not in the design
but at its boundary with something real** — a subset, a call site, an installed population, an
upgrade. Ask what reality the artifact has never been held against, and make that the lens.

Two corroborations from that round. The call-site lens found what prose review structurally cannot:
the shipped code's real statuses, and the tests pinning a contract the spec had silently changed
(`execution-testing-catches-blind-ambiguity.md`). The installed-population lens caught a cry-wolf
defect — warning on the ordinary unpushed-commit state — that no correctness lens flags, because the
code is *correct*; it is the user's attention that the finding spends. The tier-boundary lens has its
own topic: `tiering-a-reviewed-spec-creates-unreviewed-seams.md`.

## See Also

- `parallel-reviewer-fanout-pattern.md` § Choose lenses per *round*, not per loop — the within-loop
  form of this rule, plus the lens catalog.
- `trilens-loop-feature.md` — the loop re-spawns reviewers each round but never says re-pick the
  lenses; this judgement stays in lore.
- `a-fix-is-a-change-and-changes-need-review.md` — why a fix round needs a round of its own.
- `non-convergence-diagnose-before-reviewing-again.md` — what to do when the cap arrives anyway, and
  the tiering response whose seams the new unit of review exists to catch.
- `versioning-release-types.md` — where the spent-lens inventory is recoverable per version.
- `check-own-lore-before-dismissing-a-finding.md` — the triage-side discipline for what the new
  lenses return.
