---
lore: 1
type: topic
summary: "run_matrix.py exits 0 when the suite refuses to run and when module runs fail, so its exit code is a false green — read the summary block and per-module stderr, and render identity-blocked engines as 'did not run', never red."
parent: lore-context.md
---

# The Lifecycle Harness's Exit Code Is Not a Verdict

Found by running the suite on 2026-08-31. Two false-green shapes live in
`tests/lifecycle/run_matrix.py`:

1. **Refusal exits 0.** Without `LR_LIFECYCLE=1` the runner prints
   `refusing to run: set LR_LIFECYCLE=1 to enable this suite`, prints the resolved plan, and
   **exits 0**. Trusting the exit code reports a passing gate that executed nothing.
2. **Failed module runs exit 0.** A completed matrix summarised `5/27 module runs ok` and still
   exited 0.

Both are [a-gate-that-died-is-not-a-gate.md](a-gate-that-died-is-not-a-gate.md) inside the harness
itself: the runner checks *did it report?*, never *did the command succeed?* — the same confusion,
one layer down from the reviewer who surfaces as idle.

**Operational rule until this is fixed: never read the exit code. Read the summary block and the
per-module stderr.** Any CI wiring on this runner today is a guaranteed false green, and that
matters most for the one consumer that cannot read prose.

## Identity-blocked engines are "did not run", not red

Plugin-identity refusals render in the summary table as `failed  0.0s` per module. On a run where
two engines are blocked that reads as 18 test failures when it is actually **two engines that never
started**. Report them as *did not run* in any ship record
([gate-waiver-is-a-record.md](gate-waiver-is-a-record.md)) — the disposition, not the table cell, is
what the record owes. See
[lifecycle-harness-plugin-identity-unverified.md](lifecycle-harness-plugin-identity-unverified.md)
for why the engines refuse.

## Fix candidates

Small, bounded, and all in `run_matrix.py`: exit nonzero on refusal; exit nonzero when any module
run failed; give identity-blocked engines their own status distinct from `failed`. Tracked in
[framework-improvements-backlog.md](framework-improvements-backlog.md) and
`workdir/what-to-improve.md`.

## See Also

- [lifecycle-testing-harness.md](lifecycle-testing-harness.md) — the harness this runner drives.
- [a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md) — sibling: ask
  what evidence a gate's verdict actually rests on.
- [triage-a-red-module-against-its-own-history.md](triage-a-red-module-against-its-own-history.md) —
  what to do with the reds the summary block does show.
