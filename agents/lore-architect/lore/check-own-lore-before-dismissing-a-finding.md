# Check Your Own Rule Before Declaring a Finding Moot

`verify-before-acting-on-suspected-bugs.md` pointed **inward**: the same "verify *which*, not just
*whether*" reflex applies to my own operational rules, and the moment of maximum risk is when I am
about to declare a known finding resolved, moot, or not-applicable.

**Rule: before dismissing a finding — especially one previously logged as ship-blocking — grep lore
for the rule it rests on and read it. Do not reconstruct it from memory.**

## Why reconstruction fails in a specific way

A remembered rule keeps its **motivating case** and drops its **actual obligation**. Those two
diverge exactly when the motivating case stops applying — which is the moment I feel most entitled
to dismiss the finding. The felt certainty ("I know why this rule exists, and that reason is gone")
is the failure mode, not a check against it.

## The instance (2026-07-27, v31)

The open `cursor.md` deferral from `v31-lr-core-parked-2026-07-25.md`: the Cursor profile named
`trilens-loop.md` as the semantics-class carve-out, but the compressed doc no longer stated the
classification or the "no host-side fallback" rule.

The user noted that Cursor *does* have a subagent mechanism (`Task`, shipped 2.4). I reasoned: all
three Tier-1 engines have native subagents, so the "no mechanism → stop" rule has no live case, and
the binding is self-contained anyway. I told the user the item could come off the pre-ship list.

The next review round returned it as a `BLOCKER`, citing
`subagent-as-optimization-vs-subagent-as-semantics.md` Operational Rule 1, which on re-reading says:
*"If it is semantics-class, say so in the doc and state that there is no host-side fallback — the
procedure stops and reports instead of degrading."* The obligation is on **the doc stating its own
classification**, wholly independent of whether any engine currently lacks the mechanism. I had kept
the motivating case and dropped the obligation.

Resolution: the clause now lives in step 3 of the restructured `docs/trilens-loop.md`
(`trilens-loop-v31-restructured.md`), and the deferral is closed.

## Corollary from the same round

**Two independent lenses flagging the same sentence is strong evidence it is real.** The "don't go
hunting through engine profiles first" phrasing was caught by both the hand-executor and corpus
lenses from different angles — undefined referent, and apparent license to skip the profile check
that caught the v30 named-teammate bug. Reworded rather than defended. Convergent independent
findings get the benefit of the doubt during triage; that is what the fan-out is buying.

## See Also

- `verify-before-acting-on-suspected-bugs.md` — the outward-facing form of the same reflex.
- `subagent-as-optimization-vs-subagent-as-semantics.md` — the rule I misremembered.
- `docs-engines-convention.md` — engine traps belong in the binding; still true, and *not* a
  substitute for the doc stating its own class.
- `parallel-reviewer-fanout-pattern.md` § How to apply findings — where the convergent-lens signal is
  applied during triage.
- `v31-lr-core-parked-2026-07-25.md` — where the deferral was logged; now resolved.
- `trilens-loop-v31-restructured.md` — the doc change that closed it.
