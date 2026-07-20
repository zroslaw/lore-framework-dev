# Adding real work to a fast hot path can expose latent test timing races

Adding real work to a previously near-instantaneous hot path — e.g. a `ps -eo pid,ppid` subprocess
call inside `_kill`, added 2026-07-20 for the Being Keeper's cursor kill-tree fix — can retroactively
break existing tests that relied on that path's speed as an **implicit synchronization primitive**.
Specifically: tests that send a signal and immediately recheck aliveness in the same tick, assuming
the OS "hasn't had time" to deliver/process the signal yet.

## Where this bit us

Two `test_lrb.py` tests (`test_timeout_kills_long_running_session`,
`test_sigkill_after_grace_period_when_sigterm_is_ignored`) broke this way when `_kill` grew slower
after the `_descendant_pids` ppid-walk was added (see
`kill-tree-enumerate-before-signal-ordering.md`, `cursor-agent-real-invocation-contract.md`). Both
tests were written against a `_kill` fast enough that "signal sent, then check" and "signal sent,
delivered, and processed" were indistinguishable in practice — a timing coincidence the tests
depended on without stating it.

## Diagnosis approach that worked

Don't assume the new code is wrong just because a previously-green test now fails. `git stash` the
change and re-run the exact same failing scenario against the unmodified code to confirm whether
the fix or a latent test assumption is the actual cause. Here the original code passed 3/3 and the
modified code failed 3/3 deterministically — proving genuine timing sensitivity introduced by the
new latency, not flakiness, and pointing at the added latency rather than a logic bug in the fix
itself. This is the same "verify *which* cause, not just whether something's broken" discipline as
`verify-before-acting-on-suspected-bugs.md`, applied to test failures instead of suspected
production bugs — the A/B comparison (stash vs. not) is the cheap repro that confirms cause before
touching either side.

## Fix pattern

Two options, chosen per test based on what the test's premise actually depends on:

1. **Relax the assertion** to accept either same-tick or next-tick observation, when the exact tick
   doesn't matter and only the eventual outcome does (`test_timeout_kills_long_running_session`).
2. **Add an explicit small `time.sleep()` synchronization point** where the test's premise
   genuinely depends on a specific ordering — e.g. the child must have installed its SIGTERM-ignore
   handler before SIGTERM is ever sent, or the test silently exercises the wrong code path entirely
   (`test_sigkill_after_grace_period_when_sigterm_is_ignored`).

Don't default to option 2 everywhere — an unnecessary sleep just slows the suite without fixing
anything if the test didn't actually need same-tick timing.

## Operational recommendation

Whenever a hot path used by tests as an implicit sync point grows real work (a subprocess call, I/O,
a new syscall), re-run the full test file for that module before trusting a green partial run — the
breakage may not be adjacent to the code you touched. Treat "test passed instantly before, fails
now" as a specific, checkable hypothesis (added latency), not generic flakiness.

## See Also

- `kill-tree-enumerate-before-signal-ordering.md` — the fix whose added latency exposed this
- `cursor-agent-real-invocation-contract.md` — the feature context (cursor `setsid`-escape gap)
- `verify-before-acting-on-suspected-bugs.md` — the general "confirm which cause, not just whether"
  discipline this diagnosis technique instantiates for test failures specifically
