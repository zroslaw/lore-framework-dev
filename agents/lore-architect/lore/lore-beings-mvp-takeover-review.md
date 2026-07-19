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

## Checkpoint state

The session deliberately made **local worktree commits only**, with no push and no release claim:

- `lore-framework` branch `lore-architect/lore-beings-mvp`: `2badbdb` — "Checkpoint Lore Beings
  Keeper MVP"
- `lore-framework-dev` branch `lore-architect/lore-beings-mvp-dev`: `961ac22` — "Checkpoint Lore
  Beings Keeper tests"

Verification after the fixes:

- Focused Keeper suite: `test_lrb.py` passed 70/70 quietly.
- Broader dev unit discovery: 129 tests passed, with 25 lifecycle tests skipped because
  `LR_LIFECYCLE=1` was off.

This is a useful checkpoint for more review/testing, not a shipped framework release and not a
persistent `--launchd` daemon install.

## Operational lesson

For daemon/scheduler code, the third review should stay adversarial even after a green suite. The
highest-value catches were not happy-path failures; they were state poisoning, path containment,
PID reuse, malformed accepted files, and cross-midnight accounting. The review shape that worked
was: runtime/process lifecycle, parser/security/filesystem safety, and product/docs/framework fit.
