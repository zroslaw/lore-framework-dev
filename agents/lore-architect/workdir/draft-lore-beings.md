# DRAFT — Lore Beings: Autonomous Agents & the Being Keeper

Design draft. Started 2026-07-19 from the Agent Beings brainstorm capture
(`framework-improvements-backlog.md` § Major Directions § Autonomous Agents / Agent
Beings); reworked the same day in a full design dialogue with the user. This version
supersedes the earlier `draft-agent-beings.md` (deleted; superseded content folded in).
Status: **design agreed in dialogue, ready to guide an MVP build — nothing shipped.**

**Simplification pass (user-directed, 2026-07-19):** keep the initial design as simple
as possible — fields, attributes, and logic not needed for the MVP are not introduced
now. Cut in this pass (all preserved as deferred seams, §15): model tiers +
`models.json` + `engine-preference` fallback (→ plain `engine:` + `model:`), the
`autonomy:` schema field (→ fixed reflect-only behavior in prose), `lrb-*` skills
(→ CLI-only), per-session USD budgets + `default-task-usd` (→ daily cap + timeout
only), `timezone:` (→ machine-local time), one-shots in `state.json` (→ `accepted/`
files are the schedule), three config files (→ one `config.json`), per-day one-shot
cap (→ daily budget + concurrency cap bound it), CLI trim (`restart`, `logs`,
per-being pause/resume dropped).

Governing principle: `agent-being-consciousness-substrate-split.md` — a being's
consciousness (reasoning, planning, judgment) is the LLM; its vegetative nervous system
(scheduling, spawning, monitoring, budget enforcement, kill switch) is deterministic
code, never a model. Every decision below routes through the diagnostic: *judgment →
LLM; enforcement/bookkeeping → Keeper.*

---

## 1. Naming (settled with the user, 2026-07-19)

| Thing | Name |
|---|---|
| The module / feature family | **Lore Beings** |
| An autonomous agent | a **being** (an ordinary lore agent + a `being.md` descriptor) |
| The supervisor daemon | the **Being Keeper** (no personality — it's infrastructure, not an agent) |
| CLI | **`lrb`** ("Lore Beings"; short to type: `lrb status`) |
| Skills | **`lrb-*`** — name reserved, **post-MVP** (§12; MVP is CLI-only) |
| Being descriptor | `agents/<name>/being.md` |
| Machine home | `~/.lore-beings/` |
| Workspace state | `<workspace>/.lr-beings/` (gitignored) |
| Plugin docs | `docs/beings/…` |

Naming history, for the record: "keeper of the lore" confusion resolved by **Being**
Keeper; personified names (steward/warden/shepherd) rejected because the supervisor
must read as unconscious substrate, not an entity; body/nervous-system names (Soma,
Vagus, Medulla) explored and dropped in favor of the practical pair.

## 2. Vocabulary

- **Being** — a lore agent with a *lifecycle*: booted on schedule by the Keeper, not
  only interactively. Being-ness is additive — the agent stays fully usable
  interactively. The presence of `being.md` makes an agent a being.
- **Existential task** — a recurring scheduled session type declared in `being.md`
  frontmatter (cron). Part of the being's lifecycle, owned by the agent (see §4 — no
  framework-canonical task set).
- **Work session** — a one-shot session the being schedules for itself via the outbox
  (`lrb schedule`), typically during morning planning.
- **Being Keeper** — the deterministic machine-level daemon owning between-session
  existence. Never an LLM.
- **Outbox** — the file channel through which a running session requests future
  sessions; mirror of `lr-emit`'s inbox philosophy.

Layer ownership: `being.md` is **domain-layer** (part of one agent, in its repo,
team-shared). The Keeper is **machine-level infrastructure** (code shipped in the
plugin, installed once per machine). Workspace state is per-workspace. Module docs are
**plugin-layer**.

## 3. The being descriptor — `agents/<name>/being.md`

Two parts; the split mirrors the consciousness/substrate principle inside the file:

- **Frontmatter (YAML)** — the substrate contract. The *only* part the Keeper parses.
- **Body (prose)** — the generic being prompt: identity-level self-awareness read by
  the *agent* at the start of **every** scheduled session (existential or work). The
  Keeper never reads it.

```markdown
---
description: Being definition for chronicler
engine: claude                # must be in the Keeper's configured engine list (§7)
model: haiku                  # concrete model name for that engine
daily-usd: 1                  # hard daily spend cap — the spawn gate (§8)
existential-tasks:
  - name: morning-wakeup
    schedule: "30 8 * * *"    # cron, machine-local time
    prompt: being/morning-wakeup.md   # path inside this agent's directory
    timeout-minutes: 15       # wall-clock hard kill (§8)
---

# Being — chronicler

Standing guidance I read every time I wake up:
- I am the workspace chronicler; my diary lives in `workdir/diary/`.
- I run unattended. I never block waiting for a human; I escalate by writing
  it in my report.
- I write reflections and session summaries, and commit/push **only those paths**.
  I never merge — merge stays user-triggered (§10).
- A good day: the diary honestly records what happened in the workspace today.
```

Five frontmatter keys total. Notes:
- Frontmatter-on-descriptor-files is the existing convention (`lore-repo.md`,
  `role.md`); no new file-format rule.
- Schedules are plain cron in **machine-local time** — the Keeper runs on the user's
  machine, so local time is correct for realistic first users; a `timezone:` field is
  deferred until a distributed team actually hits the problem (§15). The Keeper is the
  only consumer. Deliberately **not** built on any engine's routines/cron feature:
  engine-specific schedulers can't enforce our budgets/permissions and would break
  multi-engine portability.
- `engine:` + `model:` are plain values, no indirection. Resolution at spawn time:
  engine configured (§7) → spawn with that model string; otherwise **don't run**,
  "config error" in status. Never silently substitute. The tier/preference-list
  system (portable `model-tier` + `models.json` mapping + ordered fallback) is
  deferred until a second engine actually ships (§15).
- The file is team-shared and versioned like everything else. Consequence: a
  teammate's push can change a being's lifecycle; the Keeper enforces whatever the
  current contract says — which is exactly why the cap lives here and why the being
  cannot edit its own cap (see §8 outbox validation).

## 4. Prompt layering — what a woken being reads

Three layers, generic → personal; the framework owns only the mechanics:

1. **Keeper spawn prompt** (assembled by the Keeper; tiny, pointers + runtime
   contract only): boot as `<agent>` from `<path>`; you are running as scheduled
   session `<task>`; you run headless with no user present; your day's spend so far
   is $Y of $Z; this session is killed after N minutes; request future sessions with
   `lrb schedule`; end with a brief session summary as your final output message
   (captured in the session log — *not* the `sessions/YYYY/MM/` finalization
   machinery, which stays user-triggered). Substrate facts the agent can't
   know by itself — never task content.
2. **Normal boot** — `agent-boot.md` procedure: role.md + lore-context.md, auto-pull,
   version check. Unchanged.
3. **`being.md` body** — the generic being prompt (identity, escalation rules,
   where the backlog/diary lives). Same at every wakeup.
4. **The task prompt** — the agent's own file (`agents/<name>/being/<task>.md`), or
   for a self-scheduled work session the prompt text passed to `lrb schedule`.

**Decision (user, 2026-07-19): no framework-defined canonical existential tasks.**
Task content is agent-level — what "morning" means depends entirely on the agent.
The earlier idea of plugin-shipped `docs/beings/morning-wakeup.md` procedure docs is
dropped for now. If patterns converge across many beings, canonical task templates can
be promoted later — promotion after evidence, the framework's usual path.

Rule of thumb: applies to every being → Keeper spawn contract; personal but permanent
→ `being.md` body; a specific task → the task prompt; actual work content → lore +
backlog.

## 5. The Being Keeper — placement, install, update

**One Keeper per machine** (not per workspace — settled after discussion). It serves a
registry of workspaces; beings stay workspace-scoped, the runner is machine-scoped.
One process, one status view, one kill switch.

The engine-install problem it solves: the framework is installed once per engine
(Claude plugin dir, `~/.codex/…`, `~/.cursor/…`), and each engine can move or wipe its
copy on update. A daemon must not live inside any of them. So:

- **Source of the code:** the plugin repo (`lore-framework/scripts/…`), versioned and
  released like everything else; prototyped in `lore-framework-dev` first (the
  `lr-wait` path).
- **Installed copy:** `~/.lore-beings/` — the stable machine home launchd points at.
  `lrb install` (runnable from any engine's plugin copy) copies the script there,
  writes the launchd plist, loads it.
- **Update:** re-run `lrb install` after a framework update → re-copy + restart the
  daemon. A running daemon doesn't notice its source changed; the installed version is
  shown in `lrb status`, so drift is visible. (`/lr:doctor` should learn this
  symptom.)
- **launchd model:** one entry, `KeepAlive` — launchd's job is only "keep this one
  program running" (start at login, restart on crash). All scheduling intelligence is
  inside the Keeper. Linux later = a small systemd unit, same shape.

`~/.lore-beings/` layout: the Keeper script, **one `config.json`** (workspace-root
registry + configured engines with their permission modes, §7), and the launchd plist
source. One file to document, atomic-write, and corrupt — not three; a separate
`models.json` died with the tier system (§3).

## 6. Keeper internals — one process, one loop, no threads

A tick loop (~every 30 s). Each tick:

1. **Config** — re-read `config.json` + discover `being.md` files (workspace-root
   `lore-repo.md` repos → `agents/*/being.md`; same nesting rule as agent discovery).
   Re-parse changed files; a broken frontmatter marks the being "config error" in
   status and skips it — never guess.
2. **Schedules** — recurring tasks due (from `being.md` cron)? accepted one-shots due
   (from `accepted/` files)? → spawn if the daily budget allows and the global
   concurrency cap (§9) permits. A spawned one-shot's request file moves to `done/`.
   **Missed-fire policy (same-day catch-up):** the machine sleeps — a laptop lid
   closed at 8:30 must not silently kill the day. A recurring task whose cron time
   passed today but hasn't run today fires once on the next tick, marked `late` in
   the ledger; a missed one-shot likewise fires late within its day. Past midnight,
   missed fires are dropped and recorded as `missed` in status.
3. **Outbox** — new request files? validate → `accepted/` or `rejected/` (with
   reason).
4. **Running sessions** — poll child processes: finished → read the result, record
   cost to the ledger; over wall-clock timeout → kill; crashed → record visibly.
   **Result-capture contract:** the Keeper redirects the engine's stdout into the
   per-session log file; for Claude headless (`--output-format json`) the log's
   final JSON *is* the result — cost, outcome, final message. No separate
   result-file protocol, nothing the session must remember to write.
5. **State** — persist `state.json` (write-temp + atomic rename, the `lr-emit`
   trick), sleep.

Why no threads: the concurrency that matters is the sessions themselves, and they are
separate OS processes writing their output to log files. The Keeper only starts them
and glances at them each tick. A ~30 s reaction latency is irrelevant at
task-per-hour timescales. Boring by design — this is the safety-critical layer.

**Crash-safety:** all state on disk; launchd restarts the daemon; on start it re-reads
`being.md` files and the outbox dirs (schedule tables — recurring *and* one-shot —
are *always rebuilt, never stored*; `being.md` and `accepted/` are the single sources
of truth) plus `state.json` (only what can't be recomputed), re-adopts running PIDs
(dead PID → close out from its result file), and continues. Lost/corrupt `state.json`
degrades mildly: budget counters reset for the day, `last_runs` recoverable from the
ledger, orphaned sessions finish on their own.

**`state.json` shape** (per workspace, in `<workspace>/.lr-beings/`) — only the
non-recomputable minimum:

```json
{
  "date": "2026-07-19",
  "beings": {
    "chronicler": {
      "spent_today_usd": 0.34,
      "running": [
        { "task": "work-session", "pid": 48213,
          "started": "2026-07-19T15:00:12", "timeout_minutes": 30 }
      ],
      "last_runs": { "morning-wakeup": "2026-07-19T08:30" }
    }
  }
}
```

- `date` drives the daily budget reset (machine-local midnight).
- `running` is a list (parallel sessions of one being are allowed, §9).
- No schedules of any kind in state — `being.md` holds recurring ones, `accepted/`
  holds pending one-shots.

Workspace state dir: `state.json`, `outbox/` (+ `accepted/`, `rejected/`, `done/`),
`logs/` (per-session log + result JSON + per-being ledger: one line per finished
session — task, duration, cost, outcome).

## 7. Engines & permissions — explicit configuration, never detection

**Decision (user): the engine set is explicit user configuration, not
auto-detection.** A safety layer must not change behavior because something unrelated
was installed on the machine.

- `lrb engines add <engine>` / `remove` / `list` — the user declares what the Keeper
  may use (stored in `config.json`). At `add` time the Keeper *verifies* the engine
  works (one `--version` probe) — validation of the user's statement, not discovery. A
  configured engine breaking later is a visible status error, never an automatic
  switch. The Keeper never spawns on anything outside this list. Side effect: `remove`
  doubles as a per-engine control lever.
- **Permissions are Keeper-level, per engine** (in `config.json`). Default: the
  engine's own default permission mode — no extra grants. A full-permissions mode
  (e.g. `--dangerously-skip-permissions`) exists **only by explicit user
  configuration**. The being never chooses its own permission level.

Model selection lives in `being.md` as plain `engine:` + `model:` (§3). No tiers, no
preference lists, no per-engine model mapping — deferred until a second engine ships
(§15).

## 8. Budgets & the outbox

**Unit: dollars (primary).** Rationale: it's what the user cares about, and the only
unit comparable across models (1M light-model tokens ≠ 1M flagship tokens in cost).
Claude's headless JSON reports cost directly; engines reporting only tokens get a
price-table conversion; engines reporting nothing run under the wall-clock timeout
guard alone. The ledger records both dollars and tokens when available.

**Enforcement is exactly two mechanisms, both Keeper-side and both enforceable:**

- **Daily per-being cap (`daily-usd`) as the spawn gate** — cap reached → refuse
  further spawns until machine-local midnight, record the refusal.
- **Per-task wall-clock timeout (`timeout-minutes`) as the hard kill.**

Honest bound: the cap is a *spawn gate*, not a hard ceiling — session cost is known
only at session end, so with sessions in flight the day can overshoot `daily-usd` by
at most (concurrency cap × worst single-session cost). Acceptable for MVP; the
timeout bounds the worst session. Documented so overshoot reads as designed behavior,
not a bug.

Per-session USD caps are deliberately absent: session cost is known only from the
end-of-session result JSON, so a mid-flight dollar kill isn't enforceable — a
"cap" the substrate can't enforce would be prompt-theater. The timeout is the real
in-flight bound; the daily cap is the real spend bound; the ledger records actuals.
Per-session budgets (and a `default-task-usd`) can return later if evidence demands
finer granularity (§15).

How a being knows its state: the spawn prompt injects the day's spend vs cap and the
session's timeout (§4); mid-session, `lrb status --json` reads the same truth from
disk like any tool.

**Outbox — `lrb schedule`:**

```
lrb schedule --agent chronicler --at "2026-07-19T15:00" \
  --timeout-minutes 30 "Observe today's workspace activity and note it"
```

(`--timeout-minutes` optional; Keeper default 30.)

Atomic write into `<workspace>/.lr-beings/outbox/`; the Keeper validates (known
being? daily budget not exhausted? within the next 24 hours?) → `accepted/` or `rejected/` with a
reason, surfaced in status and available to the being's next morning context. The
24-hour horizon keeps validation and budget on the same clock — a request for next
week would be validated against the wrong day's budget — and matches the model:
morning planning schedules *today*; standing rhythms belong in `being.md`. No
separate per-day one-shot cap: the daily budget gate and the machine-wide concurrency
cap already bound a runaway scheduler. **One-shot requests only** — recurring
schedules belong in `being.md`, which only the user (or a reviewed merge) edits. The
asymmetry is deliberate: a being decides *what today looks like*; its standing
lifecycle and cap are part of its reviewed definition. This is mechanically how
"morning planning schedules the day" works.

## 9. Concurrency & failures — deliberately relaxed for MVP (user decisions)

- **No per-being locks.** Parallel sessions are allowed — interactive + scheduled,
  even multiple sessions of the same being. Existing push-conflict resolution
  (`resolve-conflicts.md`) is the backstop. Revisit later if real collisions hurt;
  candidate hardening: one git worktree per session.
- **One guard kept:** a machine-wide cap on concurrent spawned sessions (default 3) —
  purely so a scheduling bug can't fork-bomb the API.
- **Failure policy: none for MVP.** A crashed/timed-out/over-budget session is a red
  line in `lrb status` and the ledger; no retries, no alerting. Learn from real
  failures first, design the policy after.

## 10. Autonomy — fixed at reflect-only for MVP; graduated ladder deferred

**MVP has no `autonomy:` field.** The Keeper never parsed it anyway — finalization
behavior is a prompt-level contract, not substrate enforcement — so as a schema field
it did nothing mechanical. The MVP has exactly one behavior, stated as two sentences
of prose in the `being.md` body (§3): *sessions write `reflections/` and session
summaries, and commit/push only those paths (append-only, the write-set discipline);
merge stays user-triggered, on a reviewed cadence.* This is the already-safe subset of
finalization.

**Deferred design (kept, not discarded):** the graduated autonomy ladder — resolving
the "merge is user-triggered by design" tension the way every framework safety gate
has been resolved (opt-in, graduated, trusted over time):

1. **`observe`** — writes only to `workdir/` and logs. No reflections, no commits.
2. **`reflect-only`** — the MVP behavior above.
3. **`finalize-branch`** — full reflect+merge, committed to a `being/<agent>` branch,
   never the default branch; the user reviews and merges like a PR.
4. **`full`** — full `/lr:finalize` on the default branch, unattended. Earned, not
   default; post-merge diff verification (backlog § Merge Quality) should ship first.

Promote `autonomy:` to a real `being.md` field only when a second behavior is actually
needed by a real being (§15).

## 11. Implementation rules (Python)

- **Stdlib-only Python 3** — the `lr-wait` sanctioned exception class (daemon/protocol
  component). Guaranteed present on every machine that can run the framework at all
  (macOS: git and python3 both come with the Xcode CLT; mainstream Linux ships it).
- **Floor: 3.9.** No `match`, no `X | Y` annotations, no post-2020 syntax.
- **One file.** Install = copy one script. No pip, ever.
- **Version guard at startup** — clear one-line error on too-old Python, then exit.
- **`#!/usr/bin/env python3`** — never a hardcoded interpreter path.
- **Tests run against the floor version** at least once (dev-repo tests, like
  `test_wait.py`).
- **Stub engine for tests** — since engines are explicit config anyway (§7),
  `lrb engines add` accepts a stub: a tiny script that prints a canned result JSON.
  Dev-repo tests exercise the whole Keeper loop (schedule → spawn → capture →
  ledger → budget) deterministically, at zero API cost. No framework-surface change.
- Node/TS considered and rejected: not guaranteed outside the Claude engine path,
  dependency-culture mismatch, TS adds a build step. Go/Rust rejected: shipping
  binaries breaks everything-is-readable-text. Bash rejected: wrong tool for a
  stateful daemon.

## 12. CLI surface — MVP is CLI-only

`lrb` subcommands (v1 set, trimmed): `install` (copy + launchd + load/restart —
doubles as the restart command), `status` (`--json` for agents; beings, last/next
runs, running now, spend vs cap, failures, config errors, log-dir paths, Keeper
version), `pause` / `resume` (all beings; backed by the `~/.lore-beings/paused`
dead-man file, so `touch`/`rm` works even with a wedged CLI), `stop` (kill switch:
SIGTERM running sessions + pause scheduling), `engines add|remove|list`,
`workspaces add|remove|list`, `schedule` (the outbox, §8).

Dropped from v1 (deferred, §15): `restart` (that's `install`), `logs <being>`
(`status` prints the log-dir paths; logs are plain files on disk), per-being
`pause`/`resume` (one being in the MVP; the all-beings switch is enough).

**Skills (`lrb-*`) are post-MVP.** The being reaches `lrb` via Bash (the spawn prompt
says so, §4); the user reaches it via terminal. Plugin skills would add surface, docs,
and Cursor wrapper regeneration for zero MVP function. The `lrb-*` namespace inside
the `lr` plugin (`/lr:lrb-status`, …; module-prefix precedent: the DF module's `df-*`)
is reserved and ships when a non-CLI surface actually needs it (§15).

## 13. MVP — "the Chronicler lives for a week"

**Decision (user): the first being is a purpose-built test being, not lore-architect.**

**The Chronicler** — a being whose entire job is observing the workspace and keeping a
diary. Zero blast radius (writes only to its own repo), peanuts cost (light model),
and self-evidencing output: open the diary and see whether it lived today.

**Placement: its own tiny agent repo** (e.g. `lore-chronicler/`), not a corner of
`lore-agents/`. That makes the zero-blast-radius claim structural — worst case, one
throwaway repo gets messy and is deleted; no shared repo carries MVP debris.

- **One existential task:** `morning-wakeup` (~8:30). Its prompt: read the diary,
  plan, then `lrb schedule` today's **midday observation** session and tonight's
  **diary-writing** session. Night is deliberately *not* a recurring task — the
  self-scheduling path is the main thing under test: if midday and night ran, the
  whole loop worked (cron fired → session spawned → outbox used → Keeper accepted →
  fired again).
- **Midday work session:** observe workspace git activity across repos, note it.
- **Night work session:** write the diary entry, reflect, push reflections
  (reflect-only behavior per the `being.md` body, §10).
- **Config:** `engine: claude`, `model: haiku`, `daily-usd: 1`.
- **Keeper MVP scope:** everything in §5–§9 except multi-workspace polish — one
  workspace in the registry is fine.
- **Success criteria (one week):** (1) every scheduled and self-scheduled session
  fired and completed or failed *visibly* — no silent deaths; (2) zero budget-cap
  breaches; (3) the outbox path worked daily (morning scheduled midday+night);
  (4) the diary reads as a coherent, honest week; (5) reflections accumulated and
  were judged merge-worthy on user review; (6) no lore corruption; push conflicts, if
  any, handled by existing resolution.
- **Explicit non-goals:** teams/hierarchy, delegation, retries/alerting, dashboards,
  full autonomy, locks/worktrees, systemd/Windows, engines beyond Claude, skills.

## 14. Relationship to existing machinery (nothing displaced)

- **`lr-wait`** — unchanged; *within-session* synchronous waiting. A scheduled session
  can still `wait_for_event` mid-task. Keeper = between-session existence.
- **`/lr:spawn-teammate`** — unchanged; interactive parallelism (panes). Beings are
  about *time*.
- **Finalization docs** — untouched until the autonomy-ladder policy ships; then
  `finalization-process.md` gains the per-being policy reference.
- **Engine routines/cron** — deliberately not used (§3).
- **Autonomy ladder fit:** MVP needs ladder step 3 only in its weakest form
  (reflect-only = the already-safe subset) and sidesteps step 4 (the Chronicler's
  "backlog" is its diary). Steps 1–2 (definition-of-done convention, feedback-to-lore)
  proceed independently and first. Step 6 (teams) explicitly out of scope.

## 15. Open seams (deferred, not decided)

Pre-existing seams:

- Notification channel — how reports/failures *reach* the user beyond `lrb status`
  (terminal-notifier / mail / etc.).
- Failure policy (retries, alerting) — after MVP evidence.
- Collision hardening — worktree-per-session if parallel sessions hurt in practice.
- Canonical existential-task templates — only if patterns converge across beings.
- systemd unit (Linux), Windows story.
- Price-table maintenance for engines that report tokens but not cost.
- Machine-wide spend view across many workspaces (ledgers already per-workspace).
- Git identity/attribution for commits made by beings.

Deferred by the 2026-07-19 simplification pass (design retained above or in git
history; reintroduce when the stated trigger fires):

- **Model tiers** (`model-tier: flagship|standard|light`, `models.json` per-engine
  mapping, ordered `engine-preference` fallback, pin-wins-over-tier precedence) —
  when a second engine ships and portability of `being.md` across engines matters.
- **`autonomy:` as a schema field + ladder enforcement** (§10 keeps the ladder
  design) — when a real being needs a second behavior beyond reflect-only.
- **Per-session USD budgets** (`budget-usd` per task, `default-task-usd`,
  `lrb schedule --budget-usd`) — if the daily cap proves too coarse; note the
  mid-flight enforceability problem (§8).
- **`timezone:` in `being.md`** — when a distributed team hits machine-local-time
  limits.
- **`lrb-*` skills** — when a non-CLI surface (engine without Bash reach, or
  discoverability) actually needs them.
- **CLI conveniences** — `logs <being>`, per-being `pause`/`resume`, a separate
  `restart`.
- **Per-day one-shot cap** in outbox validation — only if budget + concurrency
  bounds prove insufficient against a runaway scheduler.
