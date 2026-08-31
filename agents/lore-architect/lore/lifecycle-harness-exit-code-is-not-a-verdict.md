---
lore: 1
type: topic
summary: "Corrected: run_matrix.py's exit code IS trustworthy (2 on refusal, 1 on failed modules) — the false green came from piping it; only the identity-blocked-renders-as-failed defect is real."
parent: lore-context.md
---

# The Lifecycle Harness's Exit Code — Corrected

**This topic previously said the opposite, and was wrong.** It claimed `run_matrix.py` exits 0 on
refusal and on failed module runs. Verified against the code and by running it, 2026-08-31:

| Claim | Verdict |
|---|---|
| Refusal exits 0 | **False.** `LR_LIFECYCLE` unset returns **2**. |
| Failed module runs exit 0 | **False.** `summarize()` returns `not failed`; `main()` returns `0 if all_ok else 1`. A 9/18 run returned 1. |
| Identity-blocked engines render as `failed 0.0s` | **True, still open.** |

`run_matrix.py` was unchanged since v36 (`9f164e9`), so the original observation ran exactly this
code. Nothing was fixed in between; it was never broken.

## The false green was in the invocation

    python3 run_matrix.py ... 2>&1 | tail -1     # $? is tail's — always 0

Two more shapes of the same thing, same day: a backgrounded wrapper ending in `echo` reported
"exit code 0" for a run whose runner returned 1, and `--dry-run` exits 0 while printing a resolved
plan that resembles the refusal output.

**Operational rule (replacing the old one):** *read* the exit code — it is a real verdict — but
capture it unpiped: `rc=$?` on its own line, or `${PIPESTATUS[0]}`. The previous rule, "never read
the exit code," was wrong in the dangerous direction: it trained us to discard a working signal and
rely on prose instead.

## What is still broken

Plugin-identity refusals render in the summary table as `failed 0.0s` per module, so two blocked
engines read as ~18 test failures when it is two engines that never started. Report them as *did
not run* ([gate-waiver-is-a-record.md](gate-waiver-is-a-record.md)). Duration is the tell —
see [run-duration-is-the-first-triage-signal.md](run-duration-is-the-first-triage-signal.md).
An empty matrix is a related edge: zero configs makes `all_ok` true and exits 0.

## The lesson that outlives the bug

This item sat at the **top of the ranked improvement list** with a costed plan. Executing it as
written would have "fixed" correct code. A backlog entry is a hypothesis, not evidence — verify the
claim against the code before acting on it
([verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md)). The same
discipline that applies to a red test applies to my own notes
([a-red-test-may-be-asserting-a-true-fact.md](a-red-test-may-be-asserting-a-true-fact.md)).

## See Also

- [lifecycle-testing-harness.md](lifecycle-testing-harness.md) — the harness this runner drives.
- [lifecycle-harness-plugin-identity-unverified.md](lifecycle-harness-plugin-identity-unverified.md) — why engines refuse.
- [triage-a-red-module-against-its-own-history.md](triage-a-red-module-against-its-own-history.md).
