# Draft — `lr-core` CLI: deterministic substrate for mechanical skill steps

Status: **design draft, not implemented** (drafted 2026-07-25, design dialogue with the user).
Implementation deferred — this doc is the resume point.

## 1. Motivation & Evidence

The mechanical halves of high-frequency procedures (boot, attach, consult, recall, finalize
phase 4) are executed as prose by the LLM. Measured cost (2026-07-25, this session's own boot):
**9 tool calls across ~6 sequential rounds, ~450 lines of procedure prose loaded** — of which only
two Reads (`role.md`, `lore-context.md`) were the actual agent. Fan-out multiplies this: merge,
consult, attach, and recall each re-execute the full choreography, including redundant `git pull`s
of repos pulled minutes earlier.

Prior positions this design rests on:
- 2026-07-18 review verdict: *mechanical procedures executed as LLM instructions don't hold at
  current scale* (`workdir/what-to-improve.md` A1; `deterministic-sweep-catches-check-blind-spots.md`).
- Consciousness/substrate split: judgment = LLM, scheduling/mechanics = deterministic code
  (`agent-being-consciousness-substrate-split.md`; the Being Keeper is the shipped precedent).
- Core principle exception already sanctions this: *pure mechanical operations requiring no
  judgment use scripts delegated from skills* (`system-design-principles.md`).
- Scripting also raises the haiku-fidelity floor: fewer prose steps to misexecute
  (`haiku-ambiguity-detector.md`, `agent-boot-doc-fidelity-fixes.md`).

Explicitly **rejected** alternatives (with reasons, so they aren't re-raised):
- **Boot-context cache / prebuilt boot bundle** — the cost is procedure execution, not the two
  Reads; a bundle duplicates canonical content (drift + invalidation machinery). Stays parked
  (`framework-improvements-backlog.md` § Agent Boot-Context Caching).
- **Scripting judgment surfaces** — reflect/merge content, summarize narrative, trilens
  orchestration, doctor matching, migration application. These are the product or are
  semantics-bearing (`subagent-as-optimization-vs-subagent-as-semantics.md`).

## 2. Shape: one CLI, subcommands

One executable, **`scripts/lr-core`** (python3 shebang, **stdlib only** — the `lrb.py` /
`wait-server.py` precedent; the sanctioned exception to bash-on-BSD). No pip, no network beyond
git subprocesses, POSIX/macOS-first like the rest of `scripts/`.

Why one file, not five scripts: one artifact to port-test per engine, one home for shared
discovery/git code, uniform JSON + exit-code contract, uniform sandbox degradation.

Invocation: `python3 <framework-root>/scripts/lr-core <subcommand> [flags]` (or direct exec).
`<framework-root>` is already resolved by boot Step 0 / `${CLAUDE_PLUGIN_ROOT}` — **Step 0 stays
prose**: the engine must locate the framework before it can run any script, and engine-profile
selection gates *how* scripts are run.

### Subcommands

| Subcommand | Replaces (prose) | Serves |
|---|---|---|
| `discover` | repo/agent scan | boot Step 1, `list-agents`, `list-repos`, `check` |
| `preflight` | boot Steps 1–3 + 5, attach/consult mechanical half | boot, attach, consult, merge subagent boots |
| `scan` | topic enumeration + git dates | recall / `lore-search.md`, groom report (B3), B4 measurement |
| `finalize-git` | finalize Phase 4 choreography | finalize, resolve-conflicts detection |
| `check` | mechanical subset of `/lr:check` | A1 on the standing list |

#### `discover [--workspace <dir>]`
Scan workspace-root dirs for `lore-repo.md`; parse frontmatter (`description`, `version`,
`repos:`); enumerate `agents/<name>/` with `role.md` (+ `description` from its frontmatter);
detect registered shortcuts. Pure read. Output: repo list + agent list, JSON.

#### `preflight --agent <name>|--agent-dir <path> [--ttl <sec>] [--no-pull] [--fresh]`
1. Resolve agent via `discover` logic (explicit path wins; not-found → list available, exit 2).
2. **Auto-pull with TTL cache**: skip pull if last successful pull < TTL (default 600 s).
   Stamp file: `<repo>/.git/lr-last-pull` (inside `.git/` → never committed, no gitignore
   change, survives worktree conventions). `--fresh` bypasses; `/lr:pull-lore` calls with
   `--fresh`. Pull itself = current `auto-pull.md` semantics verbatim: `--ff-only`,
   `GIT_TERMINAL_PROMPT=0`, `BatchMode=yes`, internal ~60 s subprocess timeout; skip
   non-git/no-origin repos; failures are *data*, never fatal.
3. **Version compare**: repo `lore-repo.md` stamp vs `<framework-root>/VERSION`. Report
   match/mismatch/unreadable — the *upgrade* (migrations) stays prose (`version-check.md`),
   the script only detects.
4. **Teammate detection**: parent-process args scan for `--agent-id` (encapsulates the
   `ps -o args=` traps: header, multi-field single-line — `macos-ps-o-multi-field-single-line.md`).
   `ps` blocked (sandbox) → `"teammate": "unknown"`, never a failure.
5. Emit one JSON report: agent paths, files-to-read list (`role.md`, `lore-context.md`),
   pull outcome (`pulled|fresh|skipped|failed` + detail), version verdict, teammate verdict,
   warnings.

Guest-capable by construction (`--agent-dir` anywhere, no host assumptions) — attach and
consult call the same subcommand.

#### `scan --agent-dir <path> [--stale-days 180] [--format json|md]`
Manifest of `lore/` topics: filename, first non-empty body line, last-commit ISO date
(batched `git log`), age-days, staleness flag, approx size. Handed to the Explore subagent as
its reading map (semantic search stays LLM). Ships B2 (staleness surfacing) as a side effect;
output doubles as B4 measurement data and B3 groom-report input.

#### `finalize-git --plan | --commit | --push [--repo <path>]... [--session <short-uuid>]`
- `--plan`: per touched repo, scoped status of agent-subtree changes → JSON (the LLM/user
  review gate consumes this; **the gate itself stays with the LLM**).
- `--commit`: scoped `git add` (explicit paths, never `-A`), one commit per repo,
  `Finalize session <short-uuid>` default message.
- `--push`: push; on rejection emit a structured conflict report (which agent subtrees,
  which files) — conflict *resolution* stays LLM (`resolve-conflicts.md`).

#### `check [--mechanical-only]`
Script-backed mechanical subset of `/lr:check` (~#2–3, #9–11, #13–14, #19–21: existence,
version stamps, dangling topic references, manifest parity, cursor-tree parity). LLM keeps
semantic checks. Detail: standing list A1.

### Output & exit-code contract (uniform)

Every subcommand prints one JSON object:
`{ "ok": bool, "data": {...}, "warnings": [str], "errors": [str] }`

Exit codes:
- **0** — completed (possibly with warnings; degraded conditions like a failed pull are
  *reported in data*, not exit-code failures — matches today's degraded-mode boot).
- **2** — could not complete; caller must fall back to the prose procedure (see § 4).
- Anything else / no JSON / interpreter missing — treat as 2.

## 3. Doc changes (canonical-source resolution)

Tension with `single-canonical-source-discipline.md` resolved as: **prose procedure docs remain
the normative spec; the script is the fast-path implementation; the spec is read only on
fallback.** So `auto-pull.md`, boot Steps 1–3/5 etc. are not deleted — they leave the *happy
path*. Drift between script and spec is gated by the lifecycle harness plus a `check` item
(script version banner ↔ VERSION).

- `agent-boot.md` → Step 0 unchanged (prose); Steps 1–3+5 collapse to "run `lr-core preflight`,
  read its report" + fallback pointer; Step 4 (read role + lore-context) and Step 6 (confirm)
  unchanged. Target: ~50 lines.
- `attach.md`, `consult.md` → mechanical half delegates to `preflight --agent-dir <guest>`.
- `lore-search.md` → brief gains "attach the `scan` manifest"; staleness note added.
- `finalize.md` Phase 4 → delegates to `finalize-git`; review gate prose unchanged.
- `pull-lore.md` → `preflight --fresh --no-report-quiet` per active agent (verbose table kept).
- `list-agents.md` / `list-repos.md` (new docs, fixes A2) → thin wrappers over `discover`.
- `conventions.md` → new § **Script Fallback Contract** (below).

## 4. Script Fallback Contract (framework-level instruction)

User-set requirement (2026-07-25): **scripts must never become single points of failure; the
engine takes over on script failure — for all framework scripts, as default behavior.**

New `conventions.md` section (draft wording, kept brief by design):

> **Script Fallback Contract.** Framework scripts are accelerators over canonical prose
> procedures, never replacements. When a doc delegates a step to a script and the script
> **fails to complete** (exit ≥ 2, interpreter missing, unparsable output):
> 1. **Notify the user** — one line, immediately: what script failed and that you are
>    proceeding manually.
> 2. **Take over manually** — execute the canonical prose procedure the doc points to,
>    resolving what you can along the way. The flow must reach the same end state.
> 3. **Diagnose briefly, don't stall** — if the cause is quick to identify (missing python3,
>    permissions), say so; otherwise finish the flow and report the failure at the end for
>    follow-up. Never abort the surrounding flow because a script died.
>
> Distinguish this from a script *reporting* a degraded condition (exit 0 + warning, e.g.
> "pull failed"): that is data — handle it per the procedure doc, no takeover needed.

Each delegating doc carries exactly **one line**: *"If the script fails: Script Fallback
Contract (`conventions.md`) — take over manually per `<spec-doc>` §…"* — pointer, not
restatement (single-canonical-source).

Existing scripts (`workspace-pull`, `sync-cursor-skills`, `session-takeover`, plugin-refresh
scripts) get retrofitted with the same one-line pointer in their calling docs. `lrb` (Being
Keeper) is **exempt by design** — it is substrate that must never be impersonated by an LLM
(budget/kill enforcement); its failure mode is "Keeper down", not "engine takes over".

Harness implication: add a lifecycle scenario that deliberately breaks the script
(e.g. `chmod -x` / bogus interpreter) and asserts the engine completes boot manually **and**
surfaces the notification. This is the empirical gate for the contract itself.

## 5. Execution plan (phased ships)

Each ship = normal discipline: trilens to convergence + **full** lifecycle suite per engine at
cheap tiers (claude→haiku, codex→gpt-5.4-mini, cursor→composer-2.5), manifests `1.<V>.0`,
`versioning-release-types.md` backfill, cache-clear footer (all ships touch `scripts/` +
SKILL-referenced docs → **cache-affecting**).

1. **Ship 1 — substrate + boot path.** `lr-core` skeleton (JSON/exit contract, discovery
   module) + `discover` + `preflight` (incl. TTL cache); slim `agent-boot.md`; attach/consult
   delegation; `conventions.md` § Script Fallback Contract + retrofit pointer lines; new
   fallback lifecycle scenario; unit tests in `lore-framework-dev/tests/`.
   *Biggest risk & biggest win; everything else reuses its plumbing.*
2. **Ship 2 — recall.** `scan` + `lore-search.md` integration (B2 shipped; B4 data starts
   accumulating).
3. **Ship 3 — finalize.** `finalize-git` + `finalize.md`/`resolve-conflicts.md` wiring.
4. **Ship 4 — consistency & lists.** `check` subcommand (A1) + reference-rot cleanup in the
   same pass (completable sweep); `list-agents`/`list-repos` over `discover` (A2).
5. **Ship 5 — opportunistic.** Scaffolding halves of `register-agent`/`register-repo`/
   `create-repo` if friction is felt; skeleton-only, role content stays LLM.

## 6. Open questions (decide at implementation)

- **python3 availability** on minimal Codex/Cursor sandboxes — verify empirically per engine
  before Ship 1 (fallback contract covers absence, but absence-by-default on a Tier-1 engine
  would gut the win).
- Preflight running `discover` on every boot: cheap enough, or TTL-cache the discovery too?
  (Measure first.)
- `lr-core check` vs existing `/lr:check` numbering — keep check numbers stable in prose,
  script maps to them by id.
- Windows: out of scope (framework is POSIX-first throughout); revisit only on demand.

## 7. Related lore

`system-design-principles.md`, `agent-being-consciousness-substrate-split.md`,
`haiku-ambiguity-detector.md`, `auto-pull-mechanism.md`,
`freshness-contracts-at-session-boundaries.md`, `single-canonical-source-discipline.md`,
`subagent-as-optimization-vs-subagent-as-semantics.md`,
`macos-ps-o-multi-field-single-line.md`, `portable-shell-in-framework-docs.md`,
`framework-improvements-backlog.md` (§ Boot-Context Caching — stays parked),
`workdir/what-to-improve.md` (A1, A2, B2, B3, B4 all touched by this plan).
