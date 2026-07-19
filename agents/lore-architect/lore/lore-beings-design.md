# Lore Beings — Settled Design (Anchor)

The autonomous-agents direction's beings shape has a **settled design** as of 2026-07-19, agreed in a full dialogue-mode session with the user. The complete design lives in **`workdir/draft-lore-beings.md`** (which supersedes and replaced the same-day `draft-agent-beings.md`). Status: design agreed, ready to guide an MVP build; **nothing shipped**.

This topic is the anchor: the settled decisions at a glance, with the draft as the single detailed source. Don't restate draft detail here — extend the draft, then refresh this summary.

## Naming (settled)

- The module is **Lore Beings**; an autonomous agent is a **being** — an ordinary lore agent plus a `being.md` descriptor (`agents/<name>/being.md`).
- The supervisor daemon is the **Being Keeper**. It must **not** be personified — it is keeper-of-beings, unconscious substrate, not an entity with agency. "Lore-keeper" was rejected because it reads as keeper-of-the-lore. This rationale binds future features: never give the Keeper voice or judgment.
- CLI **`lrb`**; skills **`lrb-*`** inside the `lr` plugin (module-prefix precedent from `df-*`). Machine home `~/.lore-beings/`; workspace state `<workspace>/.lr-beings/` (gitignored).

## Settled decisions (user decisions marked; detail in draft §§)

- **Keeper is machine-level, not workspace-level** — one daemon per machine under launchd (`KeepAlive`, no scheduling in launchd itself), serving a registry of workspaces; installed to `~/.lore-beings/` by `lrb install` because per-engine plugin installs are unstable homes for a daemon.
- **Keeper internals** — single process, single-threaded ~30s tick loop, sessions as OS subprocesses, atomic-rename `state.json`, schedule tables always rebuilt from `being.md` (never stored).
- **No framework-canonical existential tasks** (user decision, reversing my initial design): task content is agent-level — per-task prompts live in the agent's own directory; the `being.md` body is the generic being prompt read at every wakeup; the framework injects only the runtime contract (headless, budget facts, `lrb schedule`) via the Keeper's spawn prompt. Canonical task templates only if patterns converge later.
- **Engines are explicit user configuration, never auto-detected** (user decision): `lrb engines add/remove/list`; probe-at-add is validation, not discovery. Permissions are Keeper-level per engine; default = engine defaults; full-permissions only by explicit config.
- **Model selection** — `model-tier: flagship|standard|light` + machine-level tier→model mapping per engine; `engine-preference` ordered list; explicit engine+model pin wins; never silently substitute.
- **Budgets in dollars** (primary; tokens recorded too) — the only cross-model-comparable unit; wall-clock timeout as the universal fallback guard.
- **MVP relaxations** (user decisions): no per-being locks (parallel sessions allowed, even same being; worktree-per-session is a later idea), no failure policy (fail visibly, learn first), one machine-wide concurrency cap (~3) kept as fork-bomb guard.
- **First being is the Chronicler** (user decision) — a purpose-built zero-blast-radius test being, *not* lore-architect: one existential task (morning) that self-schedules midday observation + night diary sessions via the outbox, making the self-scheduling path the main thing under test. Light tier, ~$1/day, reflect-only. MVP success = "the Chronicler lives for a week."
- **Python stdlib, floor 3.9, one file** — Node/TS, Go, bash considered and rejected (rationale in draft §11).
- **Autonomy levels** (observe / reflect-only / finalize-branch / full) carried over from the earlier draft unchanged — graduated finalization policy per being.

## Governing principle

`agent-being-consciousness-substrate-split.md` — a being's consciousness (reasoning, planning, judgment) is the LLM; its vegetative nervous system (scheduling, spawning, monitoring, budget enforcement, kill switch) is deterministic code, never a model. Every design decision routes through the diagnostic: judgment → LLM; enforcement/bookkeeping → Keeper.

## See Also

- `workdir/draft-lore-beings.md` — the full agreed design (single detailed source)
- `agent-being-consciousness-substrate-split.md` — the governing named principle
- `autonomous-agents-vision.md` — the parent vision this design concretizes
- `autonomous-agents-substrate.md` — earlier substrate findings; the switchboard-daemon sketch the Keeper generalizes
- `wait-primitive-feature.md` — `lr-wait`, the in-session synchronous wait primitive; the Keeper owns between-session existence, and the outbox is symmetric to `lr-emit`
- `framework-improvements-backlog.md` § Major Directions § Autonomous Agents / Lore Beings — the direction's backlog home
- `feedback-draft-only-when-user-triggers.md` — working-style feedback captured during the same design dialogue
