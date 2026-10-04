---
lore: 1
type: area
summary: "How I gate, review and record a ship: cheapest-first gates, the three dispositions, TriLens judgement, artifact-state ownership, and why a gate is never a model self-report."
parent: lore-context.md
---

# Gates and Review Discipline

The essential rules live below (moved here from `lore-context.md`); each rule's full body is in the member topics.

## Standing rules

- **Gates: cheapest-first order, both expensive ones on request** (`role.md` carries the full rule).
  deterministic tests → `/lr:check` → dogfood → (on request) lifecycle suite → (on request) TriLens;
  TriLens last because dogfooding produces the evidence its reviewers read. The three instruments
  have three different blind spots: running a procedure once finds what nine reading lenses may not
  (the fidelity axis is **engine**, not model tier), while **review and a deterministic suite are
  orthogonal, not redundant** — none of v46's five blockers was reachable by the suite written
  alongside the code, because they hid in the intersections a suite partitions away. After an
  ungated ship, say plainly what remains **untested**; **when a gate is waived and the user still
  asks "is this safe to ship?", run the blast-radius audit and record it beside the waiver** — it
  bounds what the unrun gate could have caught and its read-every-shared-code-edit step is the abort
  condition. **Cheapest-first prices compute, never the user** — a free probe against live OS state
  can charge the human six password prompts; validate on a copy. See
  `feedback-pre-ship-gates-on-request.md`,
  `defects-hide-in-the-intersections-a-suite-partitions.md`,
  `blast-radius-audit-when-a-gate-is-waived.md`, `gate-waiver-is-a-record.md`,
  `lifecycle-testing-harness.md`, `execution-testing-catches-blind-ambiguity.md`,
  `haiku-ambiguity-detector.md`, `live-system-state-validate-on-a-copy-first.md`.

- **When TriLens is requested, run it via `/lr:trilens-loop`**, not by hand — the skill enforces what
  a hand-run pass forgets and routes the spawn through the engine binding. Lens *choice* and triage
  stay mine: brief the **goal, not the rationale**; vary the lens *kind* by round; inventory spent
  lenses before a re-review, and spend the expensive ones (operator recovery, new state as state)
  **early**. **Convergent findings from independent lenses are strong evidence; near-total divergence
  means the lenses were well chosen.** **Brief one reviewer per round on a lens that reads
  *outward*** — system fit, neighbouring contracts, release completeness: a new command inherits
  promises its neighbours published, and no test inside the new module can see the collision
  (`a-new-command-inherits-its-neighbours-published-promises.md`). **Ask reviewers to name the
  categories they ruled out clean.** **When lenses are spent and the loop still stalls, change the
  *unit* and the *question* — a shippable subset, the call graph, the installed population — not the
  rigor.** See `trilens-loop-feature.md`,
  `parallel-reviewer-fanout-pattern.md`,
  `lens-novelty-is-the-scarce-resource-on-re-review.md`, `sonnet-subagent-review-pattern.md`.

- **A gate result belongs to a specific artifact state.** **`git status` on every repo is the first
  command of a release review**, ahead of the diff and the notes: a dirty tree means the review's
  subject does not exist yet, and a commit leaves a SHA where a dirty file leaves nothing
  (`a-release-review-starts-with-git-status.md`). Freeze
  before spawning — commit, name the SHA in the brief, tag only after the loop ends; **collect all
  reports, then apply**. An edit landed after the gates pass is ungated: re-run the affected gate or
  revert and file a follow-up. **A demo of a write operation is not evidence until it runs the next
  ordinary read** — publish then pull, commit then boot
  (`a-demo-must-test-the-state-it-leaves-behind.md`). An environment failure mid-run, or the engine
  resolving a *different* plugin tree, makes results **uninterpretable** rather than red. See
  `post-convergence-edits-need-their-own-gate.md`,
  `macos-documents-permission-loss-mid-session.md`.

- **Three gate dispositions — passed, waived, did not run** — and a ship record must name which
  applies, **in the release notes before lore**: an accuracy audit passes cleanly over an absent
  section, so audit **presence first, then accuracy**, and a **countable claim about the whole tree**
  earns a check before the notes assert it. A waiver is itself a record; a measurement names its
  environment. A reviewer that dies surfaces as *idle*, indistinguishable from "found nothing", so
  the check is "did it report?", never "did it complain?". When the round cap ends a
  loop without a clean round, **classify the findings by origin first**: a stable core with a
  churning periphery has outgrown prose review, so tier it — one deep unconstrained cold reviewer,
  not a fourth round. **The cut is itself a change**: review each tier as the subset it ships as, and
  ship a *detection* tier first only if later tiers preserve what it measures
  (`non-convergence-diagnose-before-reviewing-again.md`,
  `tiering-a-reviewed-spec-creates-unreviewed-seams.md`,
  `a-detection-tier-must-outlive-the-cure-it-measures.md`). **Reserve `lens`, `round`, and `converged` for
  `/lr:trilens-loop`** — borrowed gate vocabulary corrupts the disposition record in the scrollback,
  where no check can see it (`dont-borrow-gate-vocabulary-for-non-gates.md`). Expect fix-round
  findings in the **prose**: context errors, usually one rule stated in two places drifting apart —
  and expect the fix's **regression test to miss the branch the fix added**, because it tests the
  report that prompted it rather than the states the fix made newly reachable
  (`a-fix-s-regression-test-misses-the-branch-the-fix-added.md`). See
  `a-gate-that-died-is-not-a-gate.md`, `gate-waiver-is-a-record.md`,
  `measurement-records-name-their-environment.md`, `fix-defects-are-context-errors.md`,
  `a-fix-is-a-change-and-changes-need-review.md`.

- **A gate cannot be a model self-report** — never implement a gate in the medium it gates. Ask what
  evidence it rests on and whether the thing under test could have produced it; coverage parity is
  not evidence parity. Sibling: **a binding must not be selected by the thing it binds**. Everyday
  form: a green suite written by the fix's author is a self-report until each new test is shown **red
  against the previous tag and green against HEAD**, and a **string-containment test over prose**
  proves only that a doc still says what its author wrote. See
  `a-gate-cannot-be-a-model-self-report.md`,
  `prove-a-new-test-red-against-the-previous-tag.md`.

- **A failure list is a hypothesis until someone reads the transcripts.** An assertion names what was
  observed, never why; re-triage from stored logs cheapest-first — the module's verdict history in
  `results/*/summary.json`, then **durations before assertions** (seconds where minutes are normal =
  the engine never ran) — and capture the runner's exit code **unpiped**, or you read the pipeline's
  status and manufacture a false green. **A red test may be asserting something true about the
  machine**: establish which side is wrong before turning it green, and give danger-guarding
  assertions the strongest presumption of correctness.
  See `triage-a-red-module-against-its-own-history.md`,
  `lifecycle-harness-exit-code-is-not-a-verdict.md`, `a-red-test-may-be-asserting-a-true-fact.md`,
  `v31-lifecycle-rerun-partial-green-2026-07-27.md`, `transcript-vs-final-message-assertions.md`.

## Members

- [a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md)
- [a-gate-that-died-is-not-a-gate.md](a-gate-that-died-is-not-a-gate.md)
- [gate-waiver-is-a-record.md](gate-waiver-is-a-record.md)
- [blast-radius-audit-when-a-gate-is-waived.md](blast-radius-audit-when-a-gate-is-waived.md)
- [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md)
- [defects-hide-in-the-intersections-a-suite-partitions.md](defects-hide-in-the-intersections-a-suite-partitions.md)
- [dont-borrow-gate-vocabulary-for-non-gates.md](dont-borrow-gate-vocabulary-for-non-gates.md)
- [non-convergence-diagnose-before-reviewing-again.md](non-convergence-diagnose-before-reviewing-again.md)
- [tiering-a-reviewed-spec-creates-unreviewed-seams.md](tiering-a-reviewed-spec-creates-unreviewed-seams.md)
- [a-detection-tier-must-outlive-the-cure-it-measures.md](a-detection-tier-must-outlive-the-cure-it-measures.md)
- [a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md)
- [a-fix-s-regression-test-misses-the-branch-the-fix-added.md](a-fix-s-regression-test-misses-the-branch-the-fix-added.md)
- [fix-defects-are-context-errors.md](fix-defects-are-context-errors.md)
- [lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md)
- [review-grounding-beats-lens-novelty.md](review-grounding-beats-lens-novelty.md)
- [settle-conflicting-reviewer-claims-in-the-source.md](settle-conflicting-reviewer-claims-in-the-source.md)
- [parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md)
- [trilens-loop-feature.md](trilens-loop-feature.md)
- [ai-installer-review-lens.md](ai-installer-review-lens.md)
- [a-release-record-goes-stale-while-you-fix-it.md](a-release-record-goes-stale-while-you-fix-it.md)
- [a-release-review-starts-with-git-status.md](a-release-review-starts-with-git-status.md)
- [prove-a-new-test-red-against-the-previous-tag.md](prove-a-new-test-red-against-the-previous-tag.md)
- [a-red-test-may-be-asserting-a-true-fact.md](a-red-test-may-be-asserting-a-true-fact.md)
- [measurement-records-name-their-environment.md](measurement-records-name-their-environment.md)
- [execution-testing-catches-blind-ambiguity.md](execution-testing-catches-blind-ambiguity.md)
- [a-demo-must-test-the-state-it-leaves-behind.md](a-demo-must-test-the-state-it-leaves-behind.md)
- [a-new-command-inherits-its-neighbours-published-promises.md](a-new-command-inherits-its-neighbours-published-promises.md)
- [a-negative-grep-proves-the-pattern-absent.md](a-negative-grep-proves-the-pattern-absent.md)
- [a-displayed-attribute-can-have-more-than-one-source.md](a-displayed-attribute-can-have-more-than-one-source.md)
- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md)
- [lifecycle-testing-harness.md](lifecycle-testing-harness.md)
