# Quality-harness operational lessons (learned from real failures)

Failures during the 2026-07-06/07/09 benchmark runs, each now encoded in `tests/quality/`;
keep them in mind for any future eval harness:

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

   **Corollary — ad-hoc/shakeout runs too, not just full-matrix batching (2026-07-09).** The
   quota-doubling risk isn't limited to the 5-config matrix case above — a single ad-hoc
   shakeout run of `tests/quality/` on the default engine (unset `LR_ENGINE`, i.e. claude+sonnet)
   hit the same session-limit failure with only 36 runs, because the S3 judge is *always*
   claude+haiku regardless of `LR_ENGINE`: a claude+sonnet agent run draws on the subscription
   quota **twice** (agent + judge), while a cursor or codex agent run draws on it only once
   (judge). **Standing rule: any ad-hoc/manual run of `tests/quality/` for shakeout, debugging,
   or validating new probes defaults to `LR_ENGINE=cursor` (composer-2.5), never the bare claude
   default** — unless the task specifically requires testing claude's engine behavior (e.g.
   verifying a claude-specific S1 tool-trace fix, where cursor's headless mode can't even score
   S1). This is a standing default — don't re-ask before every run.

4. **Sanitize captured text at every capture boundary, not just at the failure site
   (2026-07-09).** Passing captured engine output into `subprocess.run(["claude", "-p", prompt,
   ...])` crashed with `ValueError: embedded null byte` — `execve` requires NUL-terminated C
   strings, and reading a file with `encoding="utf-8", errors="ignore"` does **not** strip
   `\x00` (it's valid UTF-8, just not touched by the *replace-invalid-bytes* logic). This
   surfaced only on the cursor engine — cursor writes files directly, so a stray control byte in
   generated output reached the artifact-capture path that claude/codex's message-based capture
   never exercised. Fix: `_strip_nulls(s)` in `harness.py`, applied at every capture boundary —
   inside `ProbeRun.__init__` (engine stdout/tool-trace text, all three engines), inside
   `collect_workspace_artifacts` (both the git-diff string and each file read), and again
   defensively inside `judge_s3` as the last line of defense before the subprocess call. Any
   future consumer of this text (a new judge call, a future S2 check) would otherwise hit the
   same crash blind.

## Known measurement artifact — FIXED (2026-07-09)

The S3 judge used to see the **final message only**. Engines/models that write files and
summarize (cursor+sonnet chronically; haiku and gpt-5.4-mini occasionally) got judged "no code
shown" even when the code existed in the workspace — this deflated cursor+sonnet's treatment
score (62.5%) by some unknown amount in the v1 results.

Fixed: the judge now also sees workspace artifacts. `collect_workspace_artifacts(workspace)` in
`harness.py` runs `git diff` on the fixture repo plus reads every untracked/new file (capped at
8K chars/file, 40K total) before the fixture is deleted — wired into `run_one()` in
`test_quality.py` right after `run_probe()`. `judge_s3()` gained an `artifacts=""` param,
appended to the judge prompt as a "FILES THE AGENT WROTE IN ITS WORKSPACE" section when
non-empty, with an instruction that file-delivered code counts the same as code printed in the
response. `score_s2_from()` now checks grounding against `text + artifacts` combined — safe
against false positives since agents don't edit lore topics, so the artifact capture (diff + new
files only) can't echo needle content back into the check. Interpret pre-fix v1 cross-config
gaps involving file-writing engines with this history in mind; new runs use the fixed judge.

## See Also

- `quality-benchmark-feature.md` — the benchmark these lessons come from (cluster anchor).
- `benchmark-measurement-design-principles.md` — the design-level companion (fix the judge; deterministic-first).
- `benchmark-findings-engines-models.md` — the findings these artifacts qualify.
- `quality-benchmark-v2-catalog.md` — the v2 catalog these lessons apply to going forward.
- `lifecycle-testing-harness.md` — the sibling harness sharing the deterministic-assertion discipline.
- `headless-cli-smoke-testing-discipline.md` — the earlier operational lesson family for headless engine runs.
