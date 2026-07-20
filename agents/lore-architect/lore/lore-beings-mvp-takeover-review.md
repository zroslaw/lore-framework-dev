# Lore Beings MVP — Codex takeover third review

On 2026-07-19, Codex took over an intermediate Lore Beings MVP implementation left in paired
worktrees after Claude Code had completed roughly 2.5 implement-review cycles and run out of tokens
at the third review point:

- `.worktrees/lore-framework/lore-beings-mvp`
- `.worktrees/lore-framework-dev/lore-beings-mvp`

Important provenance boundary: this Codex session did **not** have a raw exported Claude Code
transcript. The reliable inputs were the worktree files, the user's description, existing
main-branch lore/draft notes, and review findings produced in this session. When summarizing this
handoff, do not claim the full Claude Code transcript was imported.

## Third-review findings fixed

The first visible failure was environmental: the Keeper's re-adopted-PID identity test failed under
Codex because `ps` can be blocked by sandboxing. The fix made PID identity tri-state: confirmed
match, confirmed mismatch, or unknown. Confirmed mismatch can be reaped; unknown keeps the running
entry visible but refuses to signal it.

Three independent review lenses then found the main third-pass issues:

- Task names could escape log paths because they were used directly in filenames.
- `daily-usd` and engine `total_cost_usd` accepted negative or non-finite values.
- Accepted outbox requests could carry unbounded timeouts or malformed payloads.
- Timezone-aware `--at` values could crash comparisons against naive machine-local `datetime.now()`.
- Cron fields accepted out-of-range and reversed ranges.
- Pre-midnight sessions finishing after midnight could charge the new day's budget.
- The self-scheduling command in the spawn prompt needed shell quoting.
- Tests left child processes/pipe handles open, producing noisy ResourceWarnings.
- Docs/draft drifted on `install --launchd`, `spawned-late`, result-log shape, schema exactness, and
  sandboxed PID-verification caveats.

All of those were fixed in the worktree checkpoint with matching tests where appropriate.

## Checkpoint state (superseded — see below)

The session deliberately made **local worktree commits only**, with no push and no release claim:

- `lore-framework` branch `lore-architect/lore-beings-mvp`: `2badbdb` — "Checkpoint Lore Beings
  Keeper MVP"
- `lore-framework-dev` branch `lore-architect/lore-beings-mvp-dev`: `961ac22` — "Checkpoint Lore
  Beings Keeper tests"

Verification after the fixes:

- Focused Keeper suite: `test_lrb.py` passed 70/70 quietly.
- Broader dev unit discovery: 129 tests passed, with 25 lifecycle tests skipped because
  `LR_LIFECYCLE=1` was off.

At the time this was "a useful checkpoint for more review/testing, not a shipped framework
release." **That has since changed (2026-07-20):** a fourth review pass ran on real, unsandboxed
macOS — the sandbox that blocked `ps` during this Codex pass had silently kept the PID-identity
confirmed-match/confirmed-mismatch branches from ever executing (see `role.md` § Lore-Curation
Disciplines and `macos-ps-o-multi-field-single-line.md` for the bug this surfaced), and a `codex`
engine kind was added (`engine-kinds-design-decision.md`, `codex-exec-real-invocation-contract.md`).
Both worktrees were then merged into their repos' main branches (`lore-framework` ff-only,
`lore-framework-dev` via a `--no-ff` merge since main had diverged with a v27 finalize commit), and
the result shipped as **v28** (commit `44bc57d`, BETA, release-committed but not yet pushed — see
`versioning-release-types.md` and `lore-beings-design.md`). It is still not a persistent
`--launchd` daemon install on any real machine.

## Operational lesson

For daemon/scheduler code, the third review should stay adversarial even after a green suite. The
highest-value catches were not happy-path failures; they were state poisoning, path containment,
PID reuse, malformed accepted files, and cross-midnight accounting. The review shape that worked
was: runtime/process lifecycle, parser/security/filesystem safety, and product/docs/framework fit.

A sharper lesson emerged one pass later: **this review's own sandbox silently disabled its
highest-value check.** `ps` was blocked, so every PID-identity test took the "unknown, can't
verify" branch — the suite went green without the confirmed-match/confirmed-mismatch logic ever
running once. A green suite from a review environment with a known-blocked capability does not
verify the code paths that depend on that capability; see `role.md` § Lore-Curation Disciplines and
`macos-ps-o-multi-field-single-line.md` for the concrete bug this cost.

## Fifth pass (2026-07-20): the coverage gap this review named turned out to be real

The B1-only claude coverage (§ Third-review findings fixed doesn't cover this — B1 shipped in the
fourth pass) carried an explicit "claude coverage is representative, B2/B3 deferred" justification
(`test_lrb_lifecycle.py`'s original docstring, § lifecycle-testing-harness.md). Adding B2/B3
(codex/cursor kill-tree scenarios) and running them for real immediately falsified that
justification for cursor: **a real grandchild process survived the Keeper's hard kill under
cursor**, confirmed live on the test machine (the orphaned `sleep`/`sh`/sandbox-wrapper chain was
still running and had to be manually SIGKILLed). Root cause: cursor-agent's sandboxed tool
execution runs each shell command inside a freshly `setsid`'d session — a new process group that
`killpg(pgid-of-the-direct-child)` cannot reach. Fix: `_kill` now also walks the full ppid-descendant
tree (`_descendant_pids`) and signals every descendant directly, not just the process group —
catches a descendant regardless of which session/group it escaped into. Critical ordering
requirement discovered while building the regression test: **descendants must be enumerated BEFORE
signaling the parent, not after** — killing the parent first can let the OS reparent a surviving
child to PID 1, silently breaking the very ppid chain the walk depends on. Codex's own equivalent
scenario (B2) separately surfaced one non-reproducing early-completion (the model didn't block for
the instructed duration, similar in shape to the already-documented cursor backend flakiness) —
retried clean, not a Keeper defect. See `_descendant_pids`/`_kill` in `scripts/lrb.py`,
`test_kill_reaches_a_grandchild_that_escaped_into_a_new_session` in `test_lrb.py`, and
`test_lrb_lifecycle.py`'s B2/B3. Reinforces this topic's own operational lesson one more level: not
just "verify the review environment's capabilities," but "an explicit engine-agnostic-therefore-
skippable justification is itself a claim to verify empirically, not a settled fact" — see
`execution-testing-catches-blind-ambiguity.md`. The ordering fix and its second-order test breakage
are written up as their own general-purpose topics: `kill-tree-enumerate-before-signal-ordering.md`
and `hot-path-latency-can-expose-latent-test-timing-races.md`; the regression test's macOS-portable
reproduction technique is `testing-simulate-process-escape-without-setsid-binary.md`.
