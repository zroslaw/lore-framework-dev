---
lore: 1
type: topic
summary: "Prose review is structurally blind to execution-fidelity ambiguity, because the reviewer resolves it as charitably as the author did; run the doc against a real (weaker) model — and run that leg first."
parent: lore-context.md
---

**Doc wording that a strong model resolves correctly by inference can still be genuinely ambiguous — and prose review alone won't catch it, because the reviewer is itself a strong model exercising the same charitable inference the doc's author relied on.** Only running the literal text against a weaker (or just different) model surfaces the gap.

## Why This Matters

The framework's core mechanism is prose executed by a model (see `multi-engine-portability-direction.md` § Dominant shared risk). Pre-ship review — `parallel-reviewer-fanout-pattern.md`, `sonnet-subagent-review-pattern.md` — is powerful for structural and reasoning issues, but structurally blind to this specific bug class: a strong-model reviewer reading ambiguous instructions will resolve the ambiguity the same charitable way a strong-model executor would, and see nothing wrong. The two failure modes require two different catches — review catches "is this reasoning sound," execution testing catches "does this literal text produce the intended tool calls on the model that will actually run it."

## The Concrete Instance

`agent-boot.md` had already been through multiple rounds of `parallel-reviewer-fanout-pattern.md` review across several version ships. Neither bug below was ever flagged by prose review. Both were found the first time the lifecycle testing harness (`lifecycle-testing-harness.md`) ran haiku against the doc and the run failed:

- Step 1's "search all directories in the current working directory" read as unambiguous to every sonnet run, but haiku anchored to the plugin directory it had just read the doc from, then escalated to a filesystem-wide `find` — which is what triggered spurious macOS TCC permission prompts the user noticed.
- Step 2's "best-effort... never blocks boot" was over-generalized by haiku into "skippable," so it skipped auto-pull outright.

Full case study, fixes, and the debugging technique that pinpointed both (tracing actual tool calls via `--output-format stream-json --verbose` rather than reading only final text output): `agent-boot-doc-fidelity-fixes.md`.

**Second instance, a different doc (v25, 2026-07-12).** `docs/process-reflection.md` told the model to write into "the current agent's `reflections/` directory" but never stated the path. Sonnet infers `agents/<agent-name>/reflections/`; the Codex lifecycle run on `gpt-5.4-mini` took it literally and wrote to `<repo>/reflections/` (repo root), where merge, `/lr:check` #12, and the reflect test never look — so the file was silently orphaned while the model believed it had succeeded. This confirms the bug class is not specific to `agent-boot.md`: it recurs anywhere a procedure doc names a filesystem location by role ("the agent's X directory") without anchoring an explicit path. Curation rule that falls out: **when a doc tells the model to write to a named directory, spell out the path.** Full case study (incl. the rollout-log tracing that pinpointed the wrong write path): `reflect-path-anchoring-fidelity-fix.md`.

## Operational Guidance

This is why the lifecycle testing harness has standing value **before** either engine port ships, not just as a port-readiness gate — it's a live doc-fidelity check on Claude Code's own procedures. It is now the second, empirical leg of pre-ship review discipline: for any release that changes a procedure doc the harness covers, run the relevant lifecycle scenarios against real engine execution (ideally at more than one model tier) before shipping, in addition to — not instead of — multi-lens prose review. See `role.md` § Lore-Curation Disciplines.

## Pre-ship = pre-push, and it's the *complete* suite

A sharpening from the v21 ship (2026-07-06). I shipped v21, then proposed running the paid lifecycle
suite "after / on request," having gated the pre-push check to a proportionate subset (deterministic
`test_wait.py` + `/lr:check` + a single boot smoke). The user corrected twice: "You had to do it
before the push" and "run all tests before we ship."

- **Pre-ship means pre-push.** The push is the irreversible delivery step; "ship it if ok" presumes
  "ok" was *fully* established beforehand. The last gate before `commit + push` is the empirical
  suite, not a promise to run it afterward.
- **The gate is the complete suite, not a subset.** Proportionality reasoning ("v21 doesn't touch
  the procedures those scenarios exercise, so skip them") is a *review-time* judgment — it is not a
  substitute for running the gate the user considers part of shipping. A green subset is not the
  ship signal when a fuller suite exists and can run.
- **Treat the gated/paid engine cost as part of the ship**, not a reason to defer. The full run is
  ~$9–10 / ~25–30 min (v21 reference: 42/42, ~$9.4, ~27 min). Run it in the background, wait, push
  only on green. See `lifecycle-testing-harness.md`, `versioning-release-types.md`.

## The two legs are genuinely independent (v30 evidence)

v30 is the cleanest demonstration that neither leg substitutes for the other, in *both* directions:

- The review loop **converged clean** — four rounds, 14 → 6 → 1 → 0 findings, on the very doc under
  test — and the subsequent lifecycle run still exposed a weak-model fidelity gap (codex's cheapest
  tier declaring a silent round clean instead of following the retry-then-report rule) that four rounds
  of prose review had not predicted.
- The lifecycle run went **green 3/3 engines** on scenarios that a review lens had separately caught
  real defects in — a self-contradiction between two rules, and a profile that did not actually
  document the trap the procedure doc pointed at.

Corollary that bit me in the same ship: **each leg certifies the artifact state it actually ran
against.** Two doc edits made after both gates passed were ungated work, and the recheck was destroyed
by an environment failure. See `post-convergence-edits-need-their-own-gate.md`.

## Order the legs: execution first, review second (v37, 2026-08-10)

The two legs are independent, but they are not interchangeable *in sequence*. When the deliverable is
executable prose, **run the execution leg first** — it is the cheaper of the two and it produces
evidence the review leg cannot generate by reading.

The v37 evidence: three TriLens rounds and nine cold lenses over the release. Round 3's `BLOCKER` was
a bulk-registration step that skipped the `CLAUDE.md` import stub — reopening the exact whole-engine
outage v37 exists to close. A reviewer found it by noticing that a helper's three sub-items had been
bundled under one name. *Running* `register-repo` once against a workspace without the stub would
have found it in seconds, with no reviewer at all.

Ordering for a procedure-touching release:

1. Lifecycle suite against the change.
2. Dogfood the change onto this workspace (converge it onto the new version).
3. *Then* TriLens over whatever those two disturbed — a failed lifecycle run or a surprising dogfood
   hands reviewers evidence that reading alone cannot produce.

For prose-only changes the order does not matter; there is nothing to run.

**Reporting corollary.** After a review-only gate, say plainly what remains *untested*. "Three rounds,
nine lenses, 28 findings" implies coverage it does not have: reading is the only thing a review round
does. v37's real remaining gap was never a missing finding — it was that S1–S14 had no unit coverage,
the lifecycle suite had not run, and the framework's own workspace had never been converged onto the
release. That is the same discipline `a-gate-that-died-is-not-a-gate.md` applies to a gate that was
launched, applied here to a gate that was never launched at all.

## The weak-model sharpening

The execution-fidelity leg of this principle has a named, sharper form: **the weakest available model (haiku) is an *ambiguity detector*.** Where it stumbles, the doc is usually under-specified — a stronger model silently resolves the gap. The operative bar is therefore not "works on sonnet" but "explanatory enough that even haiku executes it faithfully," which doubles as a port-readiness bar (non-Claude engines are also not top-tier). See `haiku-ambiguity-detector.md` for the principle, its concrete instance (the defer-clarity fix), and the generalizable "put reassurance adjacent to the alarming message" rule.

## Diagnostic

When a procedure doc has been reviewed multiple times and still ships with an execution bug, don't conclude review failed — conclude the bug was in the blind spot review structurally can't see. The fix isn't a fourth review round; it's running the doc through an actual weaker/different-model execution and watching what it does. A failure on haiku that passes on sonnet is a pointer to the exact sentence to fix, not a reason to dismiss the run.

## See Also

- `agent-boot-doc-fidelity-fixes.md` — the first concrete case study this principle generalizes from.
- `reflect-path-anchoring-fidelity-fix.md` — the second case study (reflect path anchoring), in a different doc.
- `v25-lifecycle-scenario-fixes.md` — the v25 lifecycle run that surfaced the reflect-path bug alongside three harness-staleness fixes.
- `lifecycle-testing-harness.md` — the tool that operationalizes execution testing.
- `multi-engine-portability-direction.md` — the "framework is prose executed by the model" risk this is direct first-hand evidence for.
- `parallel-reviewer-fanout-pattern.md`, `sonnet-subagent-review-pattern.md` — the prose-review disciplines this complements, not replaces.
- `trilens-loop-feature.md` — the shipped instrument for the review leg (v30); the harness remains the empirical leg.
- `post-convergence-edits-need-their-own-gate.md` — both legs certify a specific artifact state; edits after a gate are ungated.
- `haiku-ambiguity-detector.md` — the sharpened weak-model form of the execution-fidelity leg.
- `a-gate-that-died-is-not-a-gate.md` — the three dispositions a ship record must name; § Order the legs
  is the "never launched" case.
- `a-fix-is-a-change-and-changes-need-review.md` — the v37 three-round run this ordering came out of.
- `naming-foundational-principles.md` — the meta-rule this topic's own existence follows.
- `quality-benchmark-feature.md`, `benchmark-measurement-design-principles.md` — the same "measure by running, not by reviewing" premise applied to lore *utilization* (did knowledge change behavior) rather than procedure fidelity.
