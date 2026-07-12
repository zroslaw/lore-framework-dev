# v25 Lifecycle Scenario Fixes (2026-07-12)

The Codex/Cursor lifecycle run on the v25 tree surfaced four issues (one real bug, three
test/harness staleness). All fixed and re-verified green on Claude Code + `haiku`
(`Ran 4 tests in 268s, OK`; the four touched scenarios: reflect, workspace-init, workspace-pull,
check). Report: `workdir/v25-lifecycle-codex-cursor-2026-07-12.md`.

## The four

1. **Real bug — reflect path anchoring.** See `reflect-path-anchoring-fidelity-fix.md`.
2. **`test_18` stale** — asserted the pre-v25 `<!-- lr:init:start -->` markers; v25 hard-renamed
   `/lr:init` → `/lr:workspace-init`. Updated prompt (→ `lr:workspace-init` skill), Codex
   translation (→ `docs/workspace-init.md`), marker assertions, and test name.
3. **`test_19` stale — and passing only by model recovery.** `WORKSPACE_SYNC_PROMPT` pointed at the
   renamed `lr:workspace-sync` skill and a **non-existent** `docs/workspace-sync.md`
   (→ `workspace-pull`). It had been "passing" because the model improvised its way to the right
   behavior — a green scenario silently resting on a broken reference. Renamed everything to
   `workspace-pull`.
4. **`test_20` check "timeout" was over-work, not a hang.** The rollout log showed `gpt-5.4-mini`
   faithfully executing all 23 checks and grinding check #21 (cursor-tree parity — 30 wrapper diffs
   against the *framework* tree) at the 420s mark. The scenario's only assertion is that check flags
   the seeded broken cross-reference in the fixture. Narrowed `CHECK_PROMPT` to run checks on the
   workspace's own agent repos and list broken cross-references by filename, dropping "print the full
   report verbatim." Finished in 125s on haiku.

## Reusable lessons

- **Hard-rename hygiene reaches the lifecycle harness.** When a plugin skill is hard-renamed, sweep
  the harness prompts *and* the Codex doc-path translations (`docs/<old>.md` won't exist) *and* the
  test method names — not just the plugin files. A lifecycle scenario that reads a renamed doc path
  fails or, worse, passes by model recovery, hiding the stale reference. This is
  `feedback-don-t-defer-completable-scope.md` applied to test fixtures.
- **A lifecycle scenario's prompt should target its own assertion.** "Print the full report
  verbatim" made a weak model execute (and reproduce) framework-wide checks irrelevant to the one
  thing the test asserts, blowing the per-run timeout. Scope the prompt to what the assertion needs;
  the prior session's own approved plan was "narrow the assertion or raise the timeout for that
  scenario," and narrowing is the deterministic, cheaper choice.
- **Green-on-haiku is the confirmation bar** — the weak tier both re-triggers latent ambiguity and
  doubles as a non-Claude-engine readiness proxy (`haiku-ambiguity-detector.md`).

## v25 ship state

Feature scope complete on `lore-framework/main` (unpushed); static `/lr:check`, `plugin validate
--strict`, and these four lifecycle scenarios green. Remaining before push tracked in
`framework-improvements-backlog.md` § v25 SHIP CHECKLIST: the full `LR_LIFECYCLE=1` suite is the
last gate (still deferred by the user this session), then push, then community-marketplace submit.
The PNG-logo migration was folded into the v25 tree this session (working tree still dirty with the
untracked PNGs + deleted `assets/logo.svg` — commit or back out before pushing v25).

See `v25-workspace-pull-init-design.md`, `lifecycle-testing-harness.md`,
`execution-testing-catches-blind-ambiguity.md`, `reflect-path-anchoring-fidelity-fix.md`.
