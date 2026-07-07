# Quality-harness operational lessons (learned from real failures)

Three failures during the 2026-07-06/07 benchmark runs, each now encoded in
`tests/quality/`; keep them in mind for any future eval harness:

1. **A broken judge must INVALIDATE the score, never count as FAIL.** When the Claude
   subscription session limit hit mid-batch, every judge call returned "You've hit your
   session limit…", the naive `startswith("PASS")` parser scored them all FAIL, and two
   whole configs were silently corrupted (S3=0 everywhere, uplift nonsense). Fix: the judge
   returns None unless the reply parses as PASS/FAIL and exit==0; one retry for transients;
   the runner marks the cell invalid ("-"), excludes it from scoring, and fails the suite
   loudly listing the invalid cells. A partial scorecard still prints — valid cells remain
   usable.
2. **One slow engine run must not kill the suite.** codex at 16-way concurrency blew the
   420s per-run timeout and the raw TimeoutExpired crashed the whole unittest. Fix: catch
   per-probe, score that probe as a failed run (exit 124), continue.
3. **Batch by billing quota, not by CPU.** 80 concurrent claude-billed runs (5 configs × 16,
   plus judges — judges are claude-billed even for cursor/codex configs!) burned the
   subscription's rolling window twice. Working pattern: one claude-engine config at a time,
   ~8-way concurrency; cursor/codex configs can run alongside since only their judges touch
   claude quota. Session limits surface as exit-1 runs with the limit message as the final
   text.

## Known measurement artifact (open)

The S3 judge sees the **final message only**. Engines/models that write files and summarize
(cursor+sonnet chronically; haiku and gpt-5.4-mini occasionally) get judged "no code shown"
even when the code exists in the workspace. This deflated cursor+sonnet's treatment score
(62.5%) by some unknown amount. Next improvement: give the judge the workspace diff
(`git -C … diff` + untracked files) alongside the final message. Until then, interpret
cross-config gaps involving file-writing engines with care.

## See Also

- `quality-benchmark-feature.md` — the benchmark these lessons come from (cluster anchor).
- `benchmark-measurement-design-principles.md` — the design-level companion (fix the judge; deterministic-first).
- `benchmark-findings-engines-models.md` — the findings these artifacts qualify.
- `lifecycle-testing-harness.md` — the sibling harness sharing the deterministic-assertion discipline.
- `headless-cli-smoke-testing-discipline.md` — the earlier operational lesson family for headless engine runs.
