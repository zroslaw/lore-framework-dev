---
lore: 1
type: topic
summary: "Read the per-module duration column before any assertion message: seconds-long runs mean the engine never ran (limit or identity), full durations mean a real failure to triage."
parent: lore-context.md
---

# Read Durations Before Reading Assertions

The per-module duration column separates failure categories faster than any assertion message, and
it costs nothing. From the 2026-08-31 two-engine run:

- **2.7s / 3.0s / 3.2s** where the test normally takes minutes → the engine never ran. Cause there:
  `You've hit your session limit · resets 1pm (Asia/Bangkok)`, with `$0.0000 1s` per call. Six
  Claude modules were **uninterpretable, not failed**
  ([macos-documents-permission-loss-mid-session.md](macos-documents-permission-loss-mid-session.md)).
- **0.0s** → plugin-identity blocked; the engine never started. Renders as `failed`, which reads as
  ~18 test failures when it is two engines that did nothing
  ([lifecycle-harness-exit-code-is-not-a-verdict.md](lifecycle-harness-exit-code-is-not-a-verdict.md)).
- **Full duration (250–1300s) with a single `FAIL:`** → a real assertion worth triaging.

Confirm a limit hit by counting the message across the run's `debug/` tree rather than inferring it:
`grep -rl "session limit" debug/<engine>/<module>/ | wc -l` against the call count. On that run it
was 14/14 calls in one module and **1/5 in another** — which also identifies the *boundary* module,
the one mid-flight when the limit landed, whose result is therefore also suspect.

Order stays cheapest-first: **durations → contamination sweep (limit / identity) → the module's own
verdict history in `results/*/summary.json`
([triage-a-red-module-against-its-own-history.md](triage-a-red-module-against-its-own-history.md))
→ only then a transcript.**

A related read: `ERROR:` rather than `FAIL:` in a unittest summary is usually infrastructure — on
that run `test_13` was a `subprocess.TimeoutExpired`, i.e. *did not complete*, not a framework
defect.
