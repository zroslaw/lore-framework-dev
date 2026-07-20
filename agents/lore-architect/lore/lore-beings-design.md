# Lore Beings — Settled Design (Anchor)

The autonomous-agents direction's beings shape has a **settled design** as of 2026-07-19, agreed in a full dialogue-mode session with the user, then reworked the same day by a user-directed **MVP simplification pass** (directive: keep the initial design as simple as possible; introduce nothing the MVP doesn't exercise — see `feedback-mvp-minimalism.md`). The complete design lives in **`workdir/draft-lore-beings.md`** (which supersedes and replaced the same-day `draft-agent-beings.md`). **Status (2026-07-20): released as v28 (BETA), release-committed but not yet pushed.** MVP built (`lore-framework/scripts/lrb.py`, `docs/beings.md`, `lore-framework-dev/tests/test_lrb.py`, the Chronicler at `lore-chronicler/`), real-engine-validated across two engine kinds, independently reviewed and hardened across four review passes — see the draft's **§16 "Build & hardening notes"** for the Claude Code build+review pass, `lore-beings-mvp-takeover-review.md` for the Codex third-review takeover (worktree checkpoint, now merged to main), and `engine-kinds-design-decision.md` + `macos-ps-o-multi-field-single-line.md` for the fourth-pass real-macOS findings that landed in the v28 release commit. Both source worktrees (`.worktrees/lore-framework/lore-beings-mvp`, `.worktrees/lore-framework-dev/lore-beings-mvp`) are merged into main and eligible for deletion once the push lands. **Remaining gate: the full framework lifecycle suite (`LR_LIFECYCLE=1`) is still owed before push** — this session ran the unit suite (135 tests) plus targeted real-engine e2e smoke, which is real signal but not the same gate; next session should either run the full suite and push, or explicitly note a partial-gate ship if the user chooses. **Keeper-specific real-engine lifecycle coverage now exists** (2026-07-20): `tests/lifecycle/keeper_harness.py` + `test_lrb_lifecycle.py`, 8 scenarios gated behind a *separate* higher-blast-radius flag `LR_LIFECYCLE_KEEPER=1`, verified claude 6/6 + codex 1/1 + cursor 1/1 — see `lifecycle-testing-harness.md` § Keeper coverage.

Open gaps found at real-engine verification: self-scheduling needs a permission decision the safe default can't satisfy headlessly; the `cursor` kind is empirically cost-blind so its `--session-cost-usd` flat fallback is load-bearing, not optional (`cursor-agent-real-invocation-contract.md`); and the `claude` kind has no `--plugin-dir` mechanism, so a claude-kind being needs a wrapper-script `command` to load `lr:` skills at all (`engine-kinds-design-decision.md`). The last two are filed as backlog schema decisions, not silently patched. **Not yet installed as a persistent `--launchd` daemon on any real machine** — that step is a deliberate, separate, user-triggered action. MVP success criterion unchanged: "the Chronicler lives for a week" (not yet run).

This topic is the anchor: the settled decisions at a glance, with the draft as the single detailed source. Don't restate draft detail here — extend the draft, then refresh this summary.

## Naming (settled)

- The module is **Lore Beings**; an autonomous agent is a **being** — an ordinary lore agent plus a `being.md` descriptor (`agents/<name>/being.md`).
- The supervisor daemon is the **Being Keeper**. It must **not** be personified — it is keeper-of-beings, unconscious substrate, not an entity with agency. "Lore-keeper" was rejected because it reads as keeper-of-the-lore. This rationale binds future features: never give the Keeper voice or judgment.
- CLI **`lrb`**. **MVP is CLI-only** — `lrb-*` skills are deferred with the namespace reserved (module-prefix precedent from `df-*`). Machine home `~/.lore-beings/`; workspace state `<workspace>/.lr-beings/` (gitignored).

## MVP shape (post-simplification-pass)

- **`being.md` frontmatter is 5 keys:** `description`, `engine`, `model`, `daily-usd`, `existential-tasks` (each task: `name`, `schedule`, `prompt`, `timeout-minutes`).
- **Model selection is plain `engine:` + `model:`.** Engine not configured → config error, don't run — never substitute. The tier system (`model-tier`, `models.json` per-engine mapping, ordered `engine-preference` fallback, pin-wins-over-tier) is deferred until a second engine ships.
- **Engine invocation is dispatched by a small closed `kind` enum** (`ENGINE_KINDS = ("claude", "codex", "cursor")`), not a config-time invocation template — Codex and Cursor contracts differ from `claude` on argv and cost reporting; cost-blind or missing-USD kinds use a mandatory or optional flat `--session-cost-usd` per finished session. See `engine-kinds-design-decision.md`, `codex-exec-real-invocation-contract.md`, `cursor-agent-real-invocation-contract.md`.
- **No `autonomy:` field.** The Keeper never parsed it (finalization behavior is prompt-level, not substrate-enforced), so as schema it did nothing. MVP behavior is fixed reflect-only, stated as prose in the `being.md` body. The 4-level ladder (observe / reflect-only / finalize-branch / full) is retained as deferred design; promote to a field only when a real being needs a second behavior.
- **Budget enforcement is exactly two mechanisms:** daily `daily-usd` cap as **spawn gate** + per-task `timeout-minutes` **hard kill**. Per-session USD caps were cut as unenforceable (`unenforceable-caps-are-prompt-theater.md`). Overshoot is documented as designed: spawn-gate cap can overshoot by ≤ (concurrency cap × worst single-session cost). Dollars stay the primary budget unit (tokens recorded too); wall-clock timeout is the universal fallback guard.
- **Machine-local time everywhere;** `timezone:` deferred.
- **One `config.json`** in `~/.lore-beings/` (workspaces + engines with permission modes) instead of three files; `models.json` died with tiers.
- **One-shots are never in `state.json`** — `outbox/accepted/` files ARE the pending schedule (rebuilt-never-stored applied uniformly), moved to `done/` on spawn. `state.json` = `spent_today_usd`, `running`, `last_runs` only. One-shot horizon = next 24h (keeps outbox budget validation and the daily cap on the same clock; matches "morning plans today"). No per-day one-shot cap in outbox validation — daily budget + machine-wide concurrency cap already bound a runaway scheduler.
- **Trimmed v1 CLI:** `install` (doubles as restart), `status`, `pause`/`resume` (all-beings only), `stop`, `engines add|remove|list`, `workspaces add|remove|list`, `schedule`. Dropped: `restart`, `logs <being>`, per-being pause/resume.
- **Missed-fire policy: same-day catch-up.** Laptop sleep must not silently kill the day (the biggest real gap found — morning-wakeup at 8:30 with the lid closed). A task whose time passed today but hasn't run fires once on next tick, ledger-marked `spawned-late`; past midnight → dropped, status-marked `missed`.
- **Result-capture contract:** Keeper redirects engine stdout to the per-session log; Claude headless `--output-format json` final JSON *is* the result. No separate result-file protocol. Session summary = final output message captured in the log — explicitly not the `sessions/YYYY/MM/` finalization machinery.
- **Stub engine for tests:** `lrb engines add` accepts a stub script printing canned result JSON → dev-repo tests exercise the full Keeper loop deterministically at zero API cost.

**Preservation pattern:** every cut lives in the draft's §15 "Open seams" with an explicit reintroduction trigger (e.g. tiers ← second engine ships; `autonomy:` field ← second behavior needed). Nothing silently disappeared; git history keeps the full pre-pass design.

## Settled decisions (user decisions marked; detail in draft §§)

- **Keeper is machine-level, not workspace-level** — one daemon per machine under launchd (`KeepAlive`, no scheduling in launchd itself), serving a registry of workspaces; installed to `~/.lore-beings/` by `lrb install` because per-engine plugin installs are unstable homes for a daemon.
- **Keeper internals** — single process, single-threaded ~30s tick loop, sessions as OS subprocesses, atomic-rename `state.json`, schedule tables always rebuilt from `being.md` (never stored).
- **No framework-canonical existential tasks** (user decision, reversing my initial design): task content is agent-level — per-task prompts live in the agent's own directory; the `being.md` body is the generic being prompt read at every wakeup; the framework injects only the runtime contract (headless, budget facts, `lrb schedule`) via the Keeper's spawn prompt. Canonical task templates only if patterns converge later.
- **Engines are explicit user configuration, never auto-detected** (user decision): `lrb engines add/remove/list`; probe-at-add is validation, not discovery. Permissions are Keeper-level per engine; default = engine defaults; full-permissions only by explicit config.
- **MVP relaxations** (user decisions): no per-being locks (parallel sessions allowed, even same being; worktree-per-session is a later idea), no failure policy (fail visibly, learn first), one machine-wide concurrency cap (~3) kept as fork-bomb guard.
- **First being is the Chronicler** (user decision) — a purpose-built zero-blast-radius test being, *not* lore-architect: one existential task (morning) that self-schedules midday observation + night diary sessions via the outbox, making the self-scheduling path the main thing under test. Light-model, ~$1/day, reflect-only. The Chronicler gets **its own tiny agent repo** (e.g. `lore-chronicler/`) — makes zero-blast-radius structural, deletable wholesale.
- **Python stdlib, floor 3.9, one file** — Node/TS, Go, bash considered and rejected (rationale in draft §11).

## Governing principles

- `agent-being-consciousness-substrate-split.md` — a being's consciousness (reasoning, planning, judgment) is the LLM; its vegetative nervous system (scheduling, spawning, monitoring, budget enforcement, kill switch) is deterministic code, never a model. Every design decision routes through the diagnostic: judgment → LLM; enforcement/bookkeeping → Keeper.
- `unenforceable-caps-are-prompt-theater.md` — a limit belongs in the substrate contract only if the substrate can actually enforce it; the sharpening that cut per-session USD caps and shaped the two-mechanism budget model.

## See Also

- `workdir/draft-lore-beings.md` — the full agreed design (single detailed source; §15 "Open seams" holds all deferred cuts with reintroduction triggers)
- `lifecycle-testing-harness.md` § Keeper coverage — the `LR_LIFECYCLE_KEEPER=1` real-engine Keeper scenarios
- `keeper-spawn-prompt-boilerplate-distraction.md` — operational lesson: keep one-shot `prompt`s explicit so cheap models don't fixate on the self-scheduling boilerplate
- `lore-beings-mvp-takeover-review.md` — Codex takeover of the intermediate Claude Code worktree result, third-review fixes, local checkpoint commits, and verification
- `engine-kinds-design-decision.md` — the per-engine `kind` dispatch that shipped the `codex` engine kind in v28
- `codex-exec-real-invocation-contract.md` — the empirical `codex exec` contract behind the codex engine kind
- `macos-ps-o-multi-field-single-line.md` — the fourth-review-pass real-macOS bug, and the sandbox-blind-spot lesson it taught
- `versioning-release-types.md` — the v28 history entry (release-committed, not yet pushed)
- `agent-being-consciousness-substrate-split.md` — the governing named principle
- `unenforceable-caps-are-prompt-theater.md` — the enforceability sharpening
- `feedback-mvp-minimalism.md` — the simplification-pass working style applied here
- `autonomous-agents-vision.md` — the parent vision this design concretizes
- `autonomous-agents-substrate.md` — earlier substrate findings; the switchboard-daemon sketch the Keeper generalizes
- `wait-primitive-feature.md` — `lr-wait`, the in-session synchronous wait primitive; the Keeper owns between-session existence, and the outbox is symmetric to `lr-emit`
- `framework-improvements-backlog.md` § Major Directions § Autonomous Agents / Lore Beings — the direction's backlog home
- `feedback-draft-only-when-user-triggers.md` — working-style feedback captured during the same design dialogue
