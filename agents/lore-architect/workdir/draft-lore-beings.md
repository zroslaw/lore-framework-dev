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

Descriptor frontmatter is intentionally small and strict: unexpected top-level keys
or task keys are configuration errors, not ignored hints. Notes:
- Frontmatter-on-descriptor-files is the existing convention (`lore-repo.md`,
  `role.md`); no new file-format rule.
- Task names are safe slugs because they become state/log path components. Task
  prompts are relative paths inside the agent directory, never absolute or
  escaping paths. `daily-usd` and result costs must be finite nonnegative numbers;
  `timeout-minutes` must be positive and bounded. `at:` one-shots use naive
  local ISO datetimes; timezone-aware datetimes are rejected until a real
  distributed-team requirement justifies timezone semantics.
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
- **Deviation from this spec, adopted during the build (2026-07-19):** `lrb install`
  copies the script and writes the plist, but does **not** load it into launchd unless
  `--launchd` is explicitly passed. Rationale: unconditionally bootstrapping a
  persistent, real, machine-level daemon that spends real API money on a schedule — as
  a side effect of the *first* `install` invocation, including routine dev/test
  iteration — is exactly the class of hard-to-reverse action that warrants an explicit
  opt-in gate, not implicit installer behavior. `$LRB_HOME` and
  `$LRB_LAUNCHAGENTS_DIR` env overrides make the whole CLI sandboxable for tests as a
  result. This is judged the right call (independent review concurred) and is now the
  spec, not just an implementation detail — see `docs/beings.md` for the CLI-facing
  wording. Consequence: a bare re-run of `install` after an update does not restart an
  already-running daemon (only `--launchd` does); `lrb status` shows the *running*
  daemon's recorded version (from `$LRB_HOME/daemon.info`) precisely so this drift
  stays visible in the meantime.
- **Update:** re-run `lrb install --launchd` after a framework update → re-copy +
  restart the daemon. A running daemon doesn't notice its source changed; the running
  daemon's installed version is shown in `lrb status`, so drift is visible.
  (`/lr:doctor` should learn this symptom.)
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
`logs/` (per-session stdout log containing the final JSON result, sibling stderr
log, and per-being ledger: one line per finished session — task, duration, cost,
outcome).

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

`lrb` subcommands (v1 set, trimmed): `install` (copy + write plist; `--launchd`
loads/restarts), `status` (`--json` for agents; beings, last runs, running now,
spend vs cap, failures, config errors, log-dir paths, Keeper version), `pause` /
`resume` (all beings; backed by the `~/.lore-beings/paused`
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

## 16. Build & hardening notes (2026-07-19 — MVP built, independently reviewed)

The MVP (`lore-framework/scripts/lrb.py`, `docs/beings.md`, `lore-framework-dev/tests/test_lrb.py`,
the Chronicler at `lore-chronicler/`) was built to this spec, verified end-to-end (36 tests,
a real standalone `lrb daemon` run, and a real smoke test against the actual Chronicler with the
real `claude` engine — both an existential-task same-day catch-up fire and a self-scheduled
one-shot completed successfully, cost captured correctly), then independently reviewed across two
rounds by a fresh model instance (a different model tier than the one that built it — cross-model
review, not self-review). Round 1 found the tick-loop architecture, budget model, and outbox flow
faithful to this spec, but surfaced real bugs the design discussion hadn't anticipated — all fixed
in the same pass, taking the suite to 52 tests:

- **A being's config values were validated for presence only, not validity** — a bad `schedule` or
  non-integer `timeout-minutes` passed `load_being_file` silently, then raised uncaught deep in the
  tick loop, wedging not just that being but (compounding: `tick()` had no per-workspace exception
  boundary) every later workspace in the same tick, forever. Fixed: `load_being_file` now validates
  cron syntax (all 5 fields) and rejects a schedule that fires more than once/day (existential tasks
  are once-daily by design — the same-day dedup means only the first fire would ever run anyway;
  multiple intraday runs belong on the outbox) as visible config errors; `tick()` now isolates each
  workspace so one bad being/workspace can't stop others from ticking.
- **Cost capture was fragile in a way that silently disabled the budget cap** — stderr was merged
  into the same log file as the engine's stdout JSON, so any stderr noise (a CLI update notice, a
  warning) broke the whole-file JSON parse, read cost as $0.00, and let the daily-usd spawn gate
  never trip. Fixed: stderr now goes to a sibling `.stderr.log`; result parsing also falls back to
  scanning for the last parseable JSON line as a second line of defense.
- **PID-reuse could kill an unrelated process after a reboot** — a re-adopted `running` entry (no
  live `Popen` handle) was trusted by pid alone; after a reboot the OS can reassign that pid to any
  other same-user process, and the Keeper's overdue-timeout logic would SIGTERM/SIGKILL it. Fixed:
  identity verified via `ps -p <pid> -o command=` against the recorded engine command before
  signaling any pid the Keeper didn't spawn itself this run (both the tick loop and `lrb stop`).
- **`lrb` was never actually on PATH** — `lrb install` copies the script into `$LRB_HOME` but
  creates no PATH entry, so the spawn prompt's instruction to self-schedule via `lrb schedule`
  couldn't work even with permissions solved. Fixed: the spawn prompt now embeds the concrete
  invocation (`sys.executable` + the running script's own path), computed fresh per spawn.
- **The being.md example in this very draft (and `docs/beings.md`) used inline `# comment`
  annotations the parser didn't strip**, silently corrupting `engine`/`schedule`/`prompt` values.
  Fixed: comments are now stripped respecting quotes.
- **Medium-severity findings also fixed:** the concurrency cap was per-workspace, not machine-wide
  as specified (§9) — now computed across all registered workspaces; nothing stopped two Keepers
  running concurrently and double-spawning/racing on `state.json` — now an `flock`-based
  single-instance lock; a kill signaled only the direct child, not the session's process group, so
  Bash/MCP-server grandchildren could survive a "hard kill" — now `start_new_session=True` +
  `killpg`; a stale accepted one-shot could fire days late against the wrong day's budget/context —
  now dropped (`missed`) past its own day, matching the existential-task policy; an unparseable
  outbox `at` defaulted to firing immediately instead of failing safe — now rejected visibly;
  engine-not-configured was invisible in `lrb status` — now surfaced as a config error; a stale
  `.gitignore` gap could let `.lr-beings/` session logs get committed — `lrb workspaces add` now
  appends it automatically when the workspace is a git repo; the launchd plist hardcoded
  `/usr/bin/python3` and didn't pass through the installing user's `PATH`, so an engine with a
  `#!/usr/bin/env` shebang could resolve fine manually but fail under launchd in production — both
  fixed.
- **A genuine, not-yet-closed gap the build surfaced (confirms §7's framing, doesn't contradict
  it):** self-scheduling — and any of a being's designed write actions — needs a permission
  decision the default (`permission_mode: default`) can't satisfy headlessly, since there's no user
  to approve the Bash/Write call. Observed live: the Chronicler correctly followed its own
  `being.md` "never block on a human" guidance and reported the denial instead of hanging, but §13's
  success criteria (diary written, outbox used daily) are structurally unreachable under the safe
  default. This is not a bug in the Keeper — it's §7's "explicit user configuration, never
  auto-detected" working as designed, applied to a case the original design discussion didn't
  spell out. Resolving it (full permission mode vs. a future scoped-`--allowedTools` mechanism) is
  an explicit user decision, deliberately not made by this build. See `docs/beings.md` § outbox for
  the user-facing framing.

All round-1 fixes landed with matching test coverage (frontmatter-with-comments,
bad-schedule/bad-timeout config errors, multi-occurrence-cron rejection,
stderr-noise-doesn't-break-parsing, garbage-stdout-vs-hard-crash outcome classification, PID-reuse
non-signaling, single-instance-lock refusal, SIGKILL-after-ignored-SIGTERM,
pause/concurrency-cap/existential-budget-gate).

**Round 2** independently re-verified every round-1 fix against a fresh full read of the code (not
a diff review) plus its own test run, confirmed all 12 H/M findings genuinely closed, and endorsed
the H1 PID-identity approach specifically (including a live-verified explanation of a macOS
framework-Python quirk hit and worked around during round 1: a running process's own
`sys.executable` can legitimately not match what `ps` reports for that same process, which is why
identity verification was kept for the kill paths — where it's proven correct against real spawned
engine sessions — but dropped from the purely-cosmetic daemon-self-detection display). Round 2 also
surfaced one new medium finding: the day/month/weekday syntax-validation probe added in round 1
checked only a single sample value per field, and `_cron_field_matches` short-circuits on the first
matching comma-part — so a schedule like `"30 8 1,junk * *"` passed `load_being_file` (the "1" part
matched the probe value, "junk" was never reached), then could raise uncaught during the rollover's
missed-fire check specifically (`_fire_existential_tasks` already had a matching guard;
`_check_missed_from_prev_day` didn't), wedging that one workspace's tick forever. Fixed: the syntax
probe now iterates every value in each field's legal range (guaranteeing something falls through to
every non-`*` comma-part), `*/0` now raises `ValueError` instead of `ZeroDivisionError`, and
`_check_missed_from_prev_day` gained the same defensive `except ValueError: continue` as the fire
path. Round 2 also closed three low-severity findings (a refused second daemon no longer truncates
the incumbent's lock-file pid record; the launchd plist now XML-escapes interpolated paths; `lrb
status` no longer hides a being's currently-running sessions just because its engine was removed
mid-flight) and added 3 more tests (55 total). Status: **MVP built, hardened, cross-model-reviewed
across two rounds — not yet installed as a persistent `--launchd` daemon on any real machine.** That
remains a deliberate, separate, user-triggered step.

**Codex takeover / third review (same day):** a later Codex session took over the intermediate
worktree result after the user reported Claude Code had completed about 2.5 implement-review
cycles and run out of tokens before the third review. Codex did not have the raw exported Claude
Code transcript; its reliable inputs were the paired worktrees, the user's description, and the
Claude Code build notes already preserved above. Three fresh review lenses found and fixed the
remaining high/medium edges: tri-state PID identity under sandboxed `ps`, safe task-name log paths,
finite nonnegative `daily-usd` and result costs, bounded outbox timeouts, malformed accepted
outbox requests, timezone-aware one-shot `--at` requests, cron range validation, cross-midnight
spend attribution, shell-quoted self-scheduling commands, test ResourceWarnings, and documentation
drift. Local checkpoint commits, not pushed: framework worktree `2badbdb` ("Checkpoint Lore Beings
Keeper MVP") and dev worktree `961ac22` ("Checkpoint Lore Beings Keeper tests"). Verification at
handoff: 70 focused Keeper tests passed, then 129 broader dev-unit tests passed with 25 lifecycle
tests skipped because `LR_LIFECYCLE=1` was off. This remains a worktree checkpoint that merits
more review before release or persistent daemon installation.

**Fourth review (2026-07-20, lore-architect back on real macOS):** running the Codex checkpoint's
suite on unsandboxed macOS immediately failed both PID-reuse tests — and exposed a real Keeper bug
Codex's environment structurally could not see (its sandbox blocked `ps`, forcing every identity
check down the "unknown" path, so the confirmed-match/confirmed-mismatch branches were never
exercised against real `ps` output):

- **PID-identity false mismatch on macOS** — `ps -p <pid> -o lstart= -o command=` joins both
  fields on ONE line on macOS (the code assumed one per line), so the recorded `process_start`
  embedded the full command line. The command string of a live process is not stable: macOS
  framework Python re-execs `bin/python3.x` into `Python.app/…/MacOS/Python` moments after spawn
  (the exact quirk round 1 had already documented for `_daemon_status`, not connected to this
  path). Net effect: a genuinely alive re-adopted session read as a *confirmed* PID-reuse mismatch
  and was reaped while still running — dropped from `running`, its timeout no longer enforced, its
  cost read from a partial log. Fixed: `lstart` and `command` are now fetched by two separate `ps`
  calls so "start" is pure start-time; command containment plus start equality is stable across
  re-exec. (Old-format `process_start` values in a pre-fix `state.json` would now read as
  mismatch → reaped-as-dead, never signaled; zero real deployments exist, so no migration shim.)
- **Test bug** — the mismatch-path test judged its sandbox-vs-real branch on
  `bstate["running"][0]` *after* the poll had already reaped it (IndexError on real macOS); it now
  judges via the entry reference captured before the poll.
- **Minor** — `process_outbox` now persists the normalized `timeout_minutes` into the accepted
  file before the rename (accepted/ files ARE the pending schedule; previously the normalization
  was in-memory only, functionally masked by `_spawn_accepted`'s revalidation).

Also re-probed clean this round: frontmatter parser vs CRLF/tabs/duplicate-keys/NaN, cron
occurrence counting, and Chronicler discovery via the real `discover_beings`. Verification:
70/70 focused Keeper tests and 129 broader dev-unit tests (25 lifecycle skipped) on real macOS
with working `ps` — the configuration the third review couldn't exercise. New checkpoints:
framework worktree `aac55b3`, dev worktree `3d4a26f`. Operational lesson, extending the third
review's: sandbox-degraded review environments don't just miss findings, they can *green-light*
code whose primary path never ran — a suite that passes under a blocked capability must be re-run
where the capability works before it counts as verification.
