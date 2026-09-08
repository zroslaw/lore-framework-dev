# Design — `/lr:check` as the installation front door

Status: **draft**, 2026-09-08. Author: lore-architect, in dialogue with the user.
Target: v46 (v45 is already in flight on `v45-boot-announcements`; see § Sequencing).

---

## 1. Problem

Colleagues shown Lore Agents could not get installed cleanly. Reported symptoms, in the
user's words:

- "workspace got installed incorrectly"
- "ppl run agents somewhere outside of the workspaces"
- "didn't see workspace level commands"

Three diagnostics already exist and, between them, already cover most of the underlying
conditions. The gap is **reachability and framing**, not coverage:

| | scans | finds |
|---|---|---|
| `/lr:workspace-status` | workspace git + wiring | all 18 of its findings (S1–S18) |
| `/lr:check` | agent repo content | all 24 of its checks |
| `/lr:doctor` | plugin runtime | only the 3 ailments in its catalog, and only if the user names a symptom |

**The mapping from those three quotes to the four defects below is inferred, not confirmed.**
The quotes are short, secondhand and paraphrased; nobody has reproduced a colleague's actual
directory layout or engine state. D-b and D-d are the readings I find most likely, and the
machinery in § 3.1 and § 6.5 is built on them. Confirming them is cheap and worth doing before
implementation: ask two of the affected people for `pwd`, `ls`, and which command they typed.
If the real cause is something else, this design still improves the product but will not
unstick the person who reported it.

Four concrete defects follow from that shape:

- **D-a. Three doors.** A newcomer must already know which layer is broken in order to pick
  the command that would tell them which layer is broken.
- **D-b. The wrong-directory case is a shrug.** `workspace-scan` returns
  `applicable: false` outside a workspace, and `docs/workspace-status.md` § Step 1 says to
  "report that in one line and stop — it is an ordinary state, not an error." The person
  who is lost gets one line and no diagnosis. This is symptom 2, exactly.
- **D-c. Nothing checks the plugin install itself.** No code path answers *which framework
  root did this session resolve, what version is it, is it the newest one on this disk, is
  there a newer one published.* `/lr:doctor` covers a fragment of that in prose, symptom-driven.
- **D-d. State 2 gets state 3's findings.** `run_workspace_scan` sets
  `applicable = has_workspace_descriptor or bool(find_repos(workspace))`. A folder holding a
  lore repo but no `lore-workspace.md` is therefore "applicable", so S10 fires
  `agents_md_absent`, S18 fires missing plugin config, S17 fires missing routing
  descriptions — telling someone who never ran `workspace-init` that their workspace is
  broken. This is symptom 1, and it is manufactured by us.

## 2. Goal

One command — `/lr:check` — that answers *"is my Lore installation healthy?"* from any
directory, on any engine, and that names the rung the user is standing on and the next rung up.

---

## 3. The state ladder

Three cumulative states. Each is a strict superset of the one below.

| State | Condition | Meaning |
|---|---|---|
| **1 — plugin** | the command ran at all | the `lr` plugin is loaded in this session |
| **2 — repos** | ≥1 top-level subdirectory of cwd contains `lore-repo.md` | lore agent repos are reachable from here |
| **3 — workspace** | `lore-workspace.md` exists in cwd | this is an initialized Lore workspace |

**State 3 is defined solely by `lore-workspace.md` in the session's own directory** — user's
decision, 2026-09-08. That file is what `/lr:workspace-init` creates, so the descriptor is
both the marker and the definition.

**No change to the scanner is needed to know the state.** `run_workspace_scan` already emits
both halves: `applicable` (false ⇒ state 1) and `descriptors.lore_workspace`
(`workspace_scan.py:1266`, true ⇒ state 3, else state 2). See § 6.1.

### 3.1 State 1 has four sub-cases, and they carry the diagnosis

State 1 is where the user's colleagues actually are, so it must diagnose rather than shrug
(fixes D-b). One upward walk from cwd plus one depth-1 look downward distinguishes:

- **1a — adrift.** Nothing found in either direction.
  → *"No lore repos here. To start one: `/lr:create-repo <name>`."*
- **1b — inside a repo.** cwd is, or is below, a directory containing `lore-repo.md`.
  → *"You are inside the lore repo `<name>`, not at the workspace root. `cd <path>` and re-run."*
- **1c — below a workspace.** An ancestor contains `lore-workspace.md`.
  → *"The workspace root is `<path>`, N levels up. `cd` there and re-run."*
- **1d — above a workspace.** An immediate child of cwd contains `lore-workspace.md`.
  → *"There is a workspace at `<path>`, one level down. `cd` there and re-run."*

1b and 1c can both hold; report the workspace root, the more useful target.

**1d is not optional polish.** Without it, launching the agent one directory too high — from
`~`, from a projects folder — falls into 1a and is told *"No lore repos here. To start one:
`/lr:create-repo <name>`"*: confident, wrong, and it steers the user into creating a duplicate
repo beside a workspace a plain `ls` would have shown them. Today's behavior for that case is
a neutral one-line shrug, which is **less harmful** than what 1a would say. Launching from the
parent folder is a highly plausible form of the reported symptom, so shipping 1a–1c without 1d
would make the targeted user worse off, not better. `find_repos` is depth-1 and matches
`lore-repo.md` only, so it cannot see this case
(`preflight.py`, `find_repos` — *"Top-level only, deliberately"*).

**Bounds of the two probes**, stated so they do not grow into a filesystem search:

- Upward: cwd and its ancestors to the filesystem root, testing only for the two descriptor
  filenames.
- Downward: **immediate children of cwd only**, testing only for `lore-workspace.md`. A
  workspace two or more levels below is not found, and that limit is reported honestly rather
  than papered over with a deeper walk.

**Reuse, do not re-invent.** Two directory climbs already exist: `preflight._agent_dir_from_relative`
(walk to filesystem root) and `workspace_refresh.resolve_workspace_root`. The latter already
special-cases a session running inside `.worktrees/<repo>/<slug>/` — this framework's own
convention for non-default-branch work, and a case 1a–1d otherwise handles badly. The new walk
must compose with it, not shadow it: **resolve the workspace root through
`resolve_workspace_root` first**, and use the sub-case walk only for what that does not answer.

**Boundary against the existing scope guard.** `docs/check.md` § 1 forbids walking up to a
parent looking for a workspace. That guard is about **what gets checked**; this walk is about
**where the user is**. The rule must be written explicitly, or a later executor will conflate
them:

> `check` never inspects anything outside the session's own directory. The two probes read
> nothing but the presence of `lore-repo.md` / `lore-workspace.md` and report a path. They
> never descend into what they find.

`check.md` § 1 also claims *"(Booting has the same guard — see `agent-boot.md` Step 1.)"*
**That cross-reference is unsupported** — `agent-boot.md` Step 1 has no such statement; it
only distinguishes cwd from the framework directory. The behavior it describes is real
(`find_repos` never walks up), but the citation points at prose that does not exist, and once
`check` deliberately diverges from `boot` here the sentence becomes actively misleading.
`check.md` is rewritten wholesale by this ship, so fix it there rather than leaving it to be
swept up by accident.

---

## 4. Command surface

### Before (33 skills)

```
check              agent repo content, 24 checks
doctor             plugin runtime, symptom-matched against 3 ailments
workspace-status   workspace layer, 18 findings — read-only
workspace-init     workspace layer — writes (converges)
workspace-pull     workspace layer — writes (consumes)
workspace-push     workspace layer — writes (publishes)
```

### After (31 skills)

```
check              the front door — plugin + repos + workspace, read-only
workspace-init     unchanged
workspace-pull     unchanged
workspace-push     unchanged
```

`workspace-*` becomes three **actions**, all writers. `check` is the single **diagnosis**.
That is a cleaner story than four workspace verbs where one is secretly a diagnostic.

### 4.1 Why `/lr:doctor` goes

Doctor does not repair — it **routes**. Every remedy in its catalog is another command or a
manual shell step:

| Ailment | Remedy today |
|---|---|
| `doctor-stale-plugin-cache` | clear the cache directory, restart the engine |
| `doctor-stale-shortcut-bootstrap` | run `/lr:boot` or `/lr:update` once |
| `doctor-cursor-session-without-plugin` | relaunch with `--plugin-dir`, or `workspace-init` |

So `check` can absorb the whole catalog and still never write. No contract change.

**Doctor's symptom-matching entry point is not carried over.** It existed because doctor
could not enumerate — it held three ailments and no way to sweep for them, so the user had to
supply the search key. Once every ailment is a computed finding, the user runs the command and
reads the answer instead of describing a symptom to be matched. (I told the user earlier I
would keep it as an optional argument; on writing it out, it earns nothing.)

Their fates differ, and the third is the honest one:

- `stale-plugin-cache` → becomes **P2**, a *deterministic* finding (§ 6.2). This is a strict
  upgrade: today it is prose the user must recognise; tomorrow it is computed.
- `stale-shortcut-bootstrap` → already covered by today's checks #7 and #18; the ailment doc
  becomes that finding's fix doc.
- `cursor-session-without-plugin` → **has no home inside `check`.** It describes a session in
  which no `/lr-*` command exists. It moves to `INSTALL-CURSOR.md`. See § 9.

### 4.2 Why `/lr:workspace-status` goes

Its 18 findings become `check`'s workspace section verbatim; nothing is lost. Two commands
that both report workspace health re-create D-a.

The one capability worth preserving is *scoped* invocation — an experienced user in a large
workspace who wants only the workspace layer. That becomes an argument, not a command:
`/lr:check --workspace`. A flag is cheaper than a skill.

**`docs/workspace-status.md` is not simply deleted.** It is today the canonical wording
catalog for the S-findings, read by four consumers (`workspace-status`, `check` #22–24,
`workspace-init` Step 1, and `agent-boot.md` Step 2's workspace-refresh rendering). Its
catalog moves to a new `docs/findings-catalog.md` (§ 6.4).

---

## 5. What the report looks like

The report is the feature. Everything else serves it.

All four are **Phase 1** renderings — what actually ships first (§ 10), including its honest
treatment of the repo count.

**State 3, healthy:**

```
Lore health — state 3 of 3: workspace

  ✓ Plugin      lr v44 · current · newest version installed
  ✓ Repos       3 repos · 14 agents · no problems found
  ✓ Workspace   agent-workspace · no problems found

  Everything checks out.
```

**State 3, with findings:**

```
Lore health — state 3 of 3: workspace

  ✓ Plugin      lr v44 · current
  ⚠ Repos       3 repos · 14 agents · ~2 problems found
                  1 missing file, 1 agent with no shortcut
  ⚠ Workspace   agent-workspace · 3 problems
                  2 changes not yet published, 1 repo on the wrong branch

  1 error, 4 warnings. The repo count is approximate — see below.
  Say "detail" for the full list, or run /lr:check --full.
```

Two things that mockup is doing deliberately:

- **The repo count carries a `~` and a caveat; the workspace count does not.** In Phase 1 the
  repo layer is LLM-executed and is known to under-extract at O(topics × refs)
  (measured 2026-07-18, `what-to-improve.md` A1), while the workspace count is
  script-computed. Rendering both in identical type would manufacture exactly the false
  confidence § 6.2 forbids. The `~` disappears in Phase 2.
- **Category labels are plain English, not our section headings.** "1 missing file", not
  "1 structure"; "2 changes not yet published", not "2 publication". Report Rule 2 means most
  readers see only this line, so it is the last place our internal taxonomy belongs.

**State 2:**

```
Lore health — state 2 of 3: lore repos, no workspace

  ✓ Plugin      lr v44 · current
  ✓ Repos       1 repo · 3 agents · no problems found
  — Workspace   no lore-workspace.md here

  To reach state 3, run /lr:workspace-init. It adds a shared repo list teammates can
  clone, the AGENTS.md memory file every engine reads, and committed plugin settings
  so a clone arrives already configured.
```

**State 1b — the case your colleagues hit:**

```
Lore health — state 1 of 3: plugin only

  ✓ Plugin      lr v44 · current
  — Repos       you are inside one — see below
  — Workspace   not here — see below

  You are inside the lore repo `lore-agents`, not at the workspace root, which is
  where lore commands expect to run. The workspace root is /Users/x/agent-workspace,
  2 levels up — cd there and re-run.
```

The Repos row must not read *"none in this directory"* while the sentence below says *"you
are inside a repo"*. Both are true — the row counts repos in **subdirectories** of cwd (§ 3's
state-2 test) — but a reader who does not know that scoping sees a flat contradiction, in the
one example built to prove the fix works. Any row whose truth depends on knowing our scoping
rules must defer to the sentence instead of stating a bare count.

**State 1d — launched one directory too high:**

```
Lore health — state 1 of 3: plugin only

  ✓ Plugin      lr v44 · current
  — Repos       none in this directory
  — Workspace   not here — see below

  There is a Lore workspace at /Users/x/agent-workspace, one level down.
  cd there and re-run.
```

### 5.1 Report rules

1. **The state line is first, always, and is the mandatory literal output.** It is the one
   line the whole command exists to produce, and per
   `required-literal-output-is-what-models-drop.md` it is therefore the line most likely to
   be dropped. It is sited at the top of the render step, not in a closing instruction.
2. **Summary by default; detail on request.** Each layer gets one line with a count and its
   category breakdown. The full finding list appears only on `--full` or when the user asks.
3. **Every rung below the current one is shown as passed, not omitted.** The ladder must be
   visible or the user cannot see what they have.
4. **The upgrade sentence is required whenever state < 3**, and names what the next rung buys
   — not just the command that gets there.

---

## 6. Implementation

### 6.1 No change to existing code

An earlier draft of this design claimed the scanner had to be taught to emit
`has_workspace_descriptor`, and called that its "only change". **That was wrong.** Everything
the state ladder and the repo layer need is already in today's `run_workspace_scan` output:

| Needed | Already emitted as |
|---|---|
| state 1 vs 2/3 | `applicable` (`workspace_scan.py:1200`) |
| state 2 vs 3 | `descriptors.lore_workspace` (`:1266`) |
| engine profile | `engine` (`:1201`, before the early return, so it survives state 1) |
| repos + agent counts | `agents_by_repo` (`:1284`) |

So the state is a two-line derivation in the consumer:

```python
state = 1 if not d["applicable"] else (3 if d["descriptors"]["lore_workspace"] else 2)
```

`agents_by_repo` is not a lucky accident either — its own comment says it is kept precisely
because "the flat `agents` list cannot answer 'which repo is this agent from', which
`register-repo`'s Agents-section rendering **and any per-repo report** need." This is that
report.

**`applicable` keeps its exact current meaning and is not repurposed.** Three consumers key
off it (`workspace_refresh`, `check` #22–24, `workspace-init`); changing it would break them
silently.

**One trap for the implementer.** `run_workspace_scan` returns early at `:1207` when
`applicable` is false. A `state` field naively inserted after that point would be absent in
state 1 — the single case this whole design exists to fix. Deriving state in the consumer,
as above, sidesteps it entirely; that is the second reason not to add the field.

Existing workspace finding logic stays unchanged. The new freshness finding (§ 6.8)
also requires successful-pull timestamp recording in the pull paths; see § 7.
`workspace_scan.py`'s module docstring changes for P1 in § 6.3.

### 6.2 New: `lr-core check`

One subcommand, one JSON object, so the doc makes one call:

```
python3 "<framework-root>/scripts/lr-core" check --workspace "<cwd>" [--engine <name>]
```

No `--full` flag on the script: everything it computes is cheap, so it always emits all of
it. `--full` is a *rendering* choice in the doc, plus the trigger for the expensive per-agent
lore maps the doc invokes separately.

It makes **one** call to `run_workspace_scan` and reads three of its four layers out of that
single result. Plugin checks and the freshness check in § 6.8 add computation:

| Layer | Source |
|---|---|
| engine | `run_workspace_scan` output — it already calls `detect_engine` at `:1196` |
| repos | `run_workspace_scan` output — it already calls `discover_workspace` at `:1259` |
| workspace | `run_workspace_scan` output, plus per-repo freshness (§ 6.8) |
| plugin | new `lr_core/plugin_scan.py` — P-findings |

An earlier draft listed `preflight.detect_engine` and `preflight.discover_workspace` as
separate sources alongside the scan. That would have run **both twice per invocation**, and
would have violated this design's own "never a second detector" rule in the same table that
states it. `run_workspace_scan` was extracted for in-process reuse for exactly this purpose;
its docstring says so.

**Import-cycle trap.** `plugin_scan.py` must import `preflight` *inside the calling function*,
not at module level — `preflight` imports siblings at load time and a top-level import cycles
the module graph. This has bitten us before:
`deferred-import-breaks-lr-core-preflight-cycle.md`.

Emitted shape:

```
{ok, data: {state, context, engine, plugin, repos, workspace, findings, summary}, warnings, errors}
```

- `context` — the state-1 sub-case (§ 3.1): `{case: "1a"|"1b"|"1c"|"1d", repo, workspace_root}`.
  No `levels_up`: it is arithmetic over `workspace` and `workspace_root`, both already present,
  and the doc owns the sentence anyway.
- `summary` — counts per layer per severity, plus per-category counts. **In Phase 1 the
  script counts P and S only**; the repo layer is still LLM-executed, so its count comes from
  the doc and the report must not present it as a computed figure (§ 10).
- `findings` — the P and S lists, each `{id, severity, layer, category, data}` and
  **nothing sentence-shaped**, per `script-emits-data-doc-owns-the-words.md`. R-findings join
  this list in Phase 2.

### 6.3 The plugin layer (P-findings) — the genuinely new part

This closes D-c. All of it is filesystem inventory plus one bounded network call.

| ID | Fires when | Sev |
|---|---|---|
| **P1** | a newer release exists upstream | info |
| **P2** | a newer tree exists **locally** than the one this session loaded | warn |
| **P3** | `detect_engine` returned `confidence: assumed` | warn |
| **P4** | version-bearing manifests in the loaded tree disagree with its `VERSION` | error |
| **P5** | Codex only — a stale `~/.codex/.tmp/marketplaces/` copy is present | warn |
| **P6** | a `migrations/<N>.md` in the loaded tree has a malformed `## Write Paths` | error |
| **P7** | Cursor skill-tree parity drift in the loaded tree | error |

P5 earns its place from § 2's goal, not § 1's symptom list: a stale `.tmp/marketplaces/` copy
can outrank the cache, so Codex silently executes a **different tree than the one everything
else in this report describes** — which makes every other finding uninterpretable. That is
"installed correctly for this engine" in the strictest sense.

**P1 — upstream.** `git ls-remote --tags --refs <repository> 'lr--v1.*'`, take the highest
`N`, compare to the loaded `VERSION`.

- The URL comes from `repository` in `<framework-root>/.claude-plugin/marketplace.json`
  (`https://github.com/zroslaw/lore-framework`). **Not a hardcoded constant** — a fork must
  probe its own origin.
- `git ls-remote` was chosen over an HTTPS fetch of the raw `VERSION` file because it is
  host-agnostic: no GitHub-specific URL shape. Measured 0.9 s cold on this machine.
- Reuse the existing fail-fast transport env (`GIT_TERMINAL_PROMPT=0`,
  `GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10'`). That pair is currently
  inline in **two** places (`preflight.py:258`, `workspace_refresh.py:327`); a third copy is
  drift — **extract it to `common.py` and call it from all three.**
- Any failure — no network, sandbox, timeout, non-zero exit — yields `upstream: "unknown"`
  and **no finding**. Codex's default sandbox blocks the network, so this must be an ordinary
  outcome, not a warning. The report says "upstream not checked", not "failed".
- Upstream **older** than local is not a finding either: it is a dev checkout ahead of the
  tags, or the v32–v35 tag gap recorded in `versioning-release-types.md`.
- `--no-network` skips the probe outright.

**P1 breaks a documented invariant, deliberately, and the doc that states it must be fixed in
the same ship.** `workspace_scan.py:23` currently reads: *"**No network.** Every git query
below reads local refs only, so this is safe to run on every `/lr:check`."* That sentence
makes a promise about `/lr:check`, and P1 breaks it. The scanner's own no-network property is
untouched — the call lives in `plugin_scan.py` — so the fix is to correct the sentence's
scope, not the behavior: it may promise nothing about `/lr:check` any more.

This is a user-directed trade: an upstream comparison against GitHub was asked for explicitly.
It costs ~0.9 s on a warm connection, is skippable, and fails silently. But `check` stops
being a no-network command, and the design says so plainly rather than letting a stale
comment carry the old promise.

**P2 — stale cache, now deterministic.** Compare the resolved `<framework-root>`'s `VERSION`
against every other `lr` tree discoverable in this engine's install locations:

| Engine | Locations |
|---|---|
| Claude | `~/.claude/plugins/cache/<mp>/lr/<ver>/`, `~/.claude/plugins/marketplaces/<mp>/VERSION` |
| Codex | `~/.codex/plugins/cache/<mp>/`, `~/.codex/.tmp/marketplaces/` (→ P5) |
| Cursor | `~/.cursor/plugins/{cache,local,marketplaces}/` |

If any holds a higher version, the session is running an old tree — the exact signature
`doctor-stale-plugin-cache.md` describes in prose today. `data.newer_at` names where.

**P2 cannot rescue the session that most needs it, and must say so.** A session actually stuck
on a stale cache is running the *old* `docs/check.md` — today's 24 checks, no state ladder, no
plugin layer, no P2. The new finding only exists in the tree the stuck session is not loading.
This is the identical self-masking trap `doctor-stale-plugin-cache.md` already discloses about
itself (*"this ailment can mask its own diagnostic tool"*), and inheriting doctor's catalog
means inheriting its bootstrap note. **P2's catalog entry carries that note**, and it belongs
in `INSTALL-<ENGINE>.md` too: *if `/lr:check` does not mention a plugin layer at all, you are
looking at an old cached copy of it — clear the cache first.* Without this, P2 reads as
closing a gap it can only close for sessions that were never in it.

**P4 absorbs today's check #19** and moves it out of the repo section, where it never
belonged: it is a fact about the loaded plugin, not about anyone's agent repo. Check #19's
closing note ("for an end user, a mismatch more likely signals a stale plugin cache — see
`/lr:doctor`") becomes a cross-reference from P4 to P2, since the command it names is gone.

P4 must carry #19's skip rules verbatim — prose an LLM reads charitably, a script does not:
`marketplace.json` and `.codex-plugin/plugin.json` are **skipped gracefully when absent** (not
an error), `.agents/plugins/marketplace.json` is excluded entirely (its schema has no version
field), and pairwise disagreement **among the manifests actually read** is its own error.
Losing any of these turns a valid install into a reported defect.

**No dev-gating for P6 and P7.** An earlier draft gated them behind a new "is the framework
root a working checkout in this workspace" detector. That detector is unnecessary machinery:
both checks read files that ship correctly formed in every release, so **a correct install
makes them silent by construction**. The gate would have added a environment detector to
suppress noise that does not occur. (The justification was also half-invented: check.md's
"teeth mainly … during framework development" caveat exists for #19 and #20, but **not** for
#21.) They run unconditionally; when they do fire on an end user's machine, the install is
genuinely damaged and saying so is correct.

### 6.4 One catalog, three namespaces

Today's 24 checks redistribute across three layer namespaces:

| Today | Becomes | Layer |
|---|---|---|
| checks #1–#18 | **R** findings | repo |
| checks #19–#21 | **P4, P6, P7** | plugin (they check the framework, not agent repos) |
| checks #22–#24 | already render **S** findings — unchanged | workspace |

The S-prefix survives untouched on purpose: 16 files reference those IDs. Renaming them
would be a large change that buys nothing.

**One naming caveat.** `docs/version-check.md` already uses a bare `R` as a live symbol — the
`version` field from the booting agent's `lore-repo.md`, compared against `F` in its `R > F` /
`R < F` cases. That is a scalar in a different procedure, not a finding-ID namespace, so the
collision is weak; `P`/`R`/`S` maps onto Plugin/Repo/Workspace too cleanly to give up. The
catalog states the distinction in one line so nobody has to rediscover it.

Finding wording lives in one new doc, `docs/findings-catalog.md`. **In Phase 1 it holds P and
S** — the two script-computed layers, which is where the script/doc seam needs a single
canonical site. The R-findings stay where they are, in `docs/check.md`, which both executes
and words them; they move into the catalog in Phase 2 when the script starts computing them.
There is no point at which the same finding is worded twice.

The R namespace is specified in § 6.7. It is **designed now and implemented in Phase 2**
(user decision, 2026-09-08) — designing it here is what keeps the catalog schema, the fix
tiers and the summary contract from being retrofitted around it later.

This also kills an existing drift. `docs/workspace-status.md` states it is "the only place a
finding's wording exists", while `check.md` #22–24 restate that wording anyway — two copies
of nine findings. After this change there is one.

### 6.5 State-dependent rendering — the collapse rule

Fixes D-d, and it is one rule rather than a per-finding table:

> **When `state < 3`, the findings listed as `collapses: uninitialized` collapse into the
> single upgrade sentence** instead of being listed individually. That set is **S4, S5, S10,
> S17, S18**.

An earlier draft derived this set instead — "findings whose fix names `/lr:workspace-init`" —
and presented the derivation as free because "every finding names its fix". It is not free and
it does not work. The catalog's Fix column is **compound conditional prose**, not a command
token: S18's is *"`workspace-init` (writes both files; an unparseable file must be fixed by
hand first)"*, S4's names `workspace-init` **and** a manual move for the enclosing-repo case.
Deriving from it would have required a schema migration of the Fix column that § 7 never
listed as work — complexity hidden behind "the data already supports it", not removed.

**S3 is deliberately not in the set**, which is the second thing the derivation got wrong: its
condition is "git-tracked but no origin", which is equally true of a fully converged workspace
that simply has no remote. It does not mean "you never initialized a workspace", so collapsing
it under that sentence would state something false.

Five explicit IDs is smaller than a schema migration and cannot silently mis-classify a sixth.
The set lives in `docs/findings-catalog.md` beside the words, so every consumer that renders
findings — `check`, `workspace-init`, and boot's workspace-refresh leg — inherits it.

### 6.6 The fix contract

The user's requirement: report, then ask before applying. Three tiers. **Each finding declares
its tier as a column in the catalog** — the tier is not inferred from the Fix prose, for the
same reason the collapse set is enumerated rather than derived (§ 6.5): S4's fix is
`workspace-init` *and* a manual directory move, so no parser can sort it into one tier. A
finding whose fix spans tiers declares the **most restrictive** one it touches.

1. **Fix is an `lr` command** (`workspace-init`, `workspace-pull`, `workspace-push`,
   `update`, `register-agent`). `check` offers to run it; on yes it invokes the skill, which
   carries its own announcement and its own approval. This is the majority of fixes.
2. **Fix is a bounded shell command** (`git -C <repo> checkout <branch>`,
   `git worktree prune`). Printed exactly. `check` does not run it.
3. **Fix touches system or engine state** (clear the plugin cache, restart the engine,
   relaunch with `--plugin-dir`). Printed exactly, never run — clearing a plugin cache
   mid-session removes the tree the session is executing from. Consistent with
   `live-system-state-validate-on-a-copy-first.md`.

**`check` itself writes nothing, in any tier.** Tier 1 is delegation to a command that owns
its own write contract, not `check` acquiring one. Stating this as an invariant matters: the
moment `check` can write, it stops being safe to run reflexively, which is the whole point.

---

### 6.7 The repo layer (R-findings) — designed now, built in Phase 2

Today's checks #1–#18 are executed by the model reading files. That is the measured weak
point: a deterministic sweep on 2026-07-18 found 14 unresolved lore references that checks
#9–#10 nominally cover, because an LLM under-extracts at O(topics × refs)
(`what-to-improve.md` A1). The front door's summary promises a count, so the count has to be
computed.

**Almost all of it is already mechanical, and most primitives exist.** New module
`lr_core/repo_scan.py`; the "Source" column is what it calls, not what it reimplements.

| ID | Was | Fires when | Source |
|---|---|---|---|
| R1 | #2 | `lore-repo.md` frontmatter missing/blank `description` or `version` | `describe_repo` |
| R2 | #3 | repo's `version` stamp ≠ framework `VERSION` | compare |
| R3 | #4 | repo has `lore-repo.md` but no agents (info) | `discover_workspace` |
| R4 | #5 | `role.md` missing `description`, or carrying a legacy `version` | `repo_agents` |
| R5 | #8 | agent dir missing `role.md`/`lore-context.md`/`lore/`/`workdir/` | filesystem |
| R6 | #9–#11 | Lore v1 validation items, unresolved legacy refs, context over size | `lore_map` graph |
| R7 | #12 | `reflections/` exists and is non-empty | filesystem |
| R8 | #13 | uncommitted changes under the repo's lore paths | `git -C` status |
| R9 | #14 | a topic committed more recently than `lore-context.md` | `git -C` log |
| R10 | #6a | agent has no registered shortcut (info) | `shortcut_inventory` |
| R11 | #6b, #7 | a shortcut's `from` target does not exist | `shortcut_targets` |
| R12 | #18 | shortcut in a legacy or invalid format | § below |
| R13 | #16a | shortcut older than the agent's `role.md` | `git -C` log + stat |
| R14 | #17 | orphaned pre-plugin `lr-*.md` command duplicating a plugin skill | filesystem |
| R15 | #16b | shortcut agent name differs from the target role heading after mechanical normalization | parsed shortcut + target `role.md` |

**Exact shortcut-name matching is scripted (R15).** Extract the agent name from the
shortcut's boot instruction and the first H1 from its resolved target `role.md`. Trim and
case-fold both; treat runs of spaces and hyphens as the same separator. Thus
`lore-architect` matches `Lore Architect`. Do not infer synonyms or strip arbitrary words.
Compare against the resolved target, not a global name lookup. Missing targets belong to
R11; missing/unparseable names are reported as unable to compare, never a match.

A difference is a review finding, not proof that the shortcut points to the wrong agent.
AI can explain an intentional alias; it does not silently suppress the scripted result or
rename anything without approval.

**Only check #15 requires AI as its primary detector:** whether `lore-context.md` still
accurately describes the topics it summarizes. Report that assessment separately from the
15 computed R-finding types, with its actual coverage; say "not reviewed" when skipped.

**R6 runs in-process, in one pass, for every agent.** `lore_map` already builds the graph and
already emits `validation`; calling it as 14 subprocesses would dominate the runtime of the
whole command. Measure before shipping: if one pass over this workspace's 14 agents does not
stay comfortably inside a couple of seconds, R6 moves behind `--full` and the summary says so
rather than quietly costing every invocation.

**R12 is the one to be careful with**, and it must not be written from scratch. Check #18's
rules run ~50 lines with per-engine variations and one exemption that inverts the rule:
shortcuts in the user-global `~/.codex/skills/` **require** an absolute `from` target, so
flagging them like workspace-local ones would report a correct file as broken and, followed
literally, rewrite it into a form that cannot work. There is already a test pinning this
contract (`tests/test_shortcut_bootstrap_contract.py`) and a generator that writes the
canonical form (`register-repo`, migration 44). R12 derives its rules from the **same** source
those use — a second copy of the format rules is exactly the diagnostic/remedy divergence
`one-question-one-code-path.md` describes, and here the divergence would corrupt user files
rather than merely misreport.

**No network anywhere in this layer.** Every git call reads local refs.

### 6.8 Repo freshness — last verified check older than 24 hours

**User decision, 2026-09-08:** report stale freshness information and recommend a pull.
This is the age of the last successful upstream check, not the age of the latest commit.
An inactive repo can be fully current; old check information does not prove missing commits.

Add **S19** (warning) in Phase 1, computed per git repo with an upstream remote: the workspace
root plus every top-level repo covered by `workspace-pull`, including non-Lore repos.
At state 2 it still runs for the discovered child git repos; no workspace descriptor is
required. Missing repos remain S6; local-only repos without a remote are not applicable.
Deduplicate by resolved repo path. S19 never collapses into the workspace-init suggestion.

- `age_seconds > 86400` → stale. Exactly 24 hours is not stale yet.
- Missing, unreadable, non-finite, or future timestamp → freshness unknown; recommend a pull
  without inventing an age. S19 carries a reason to distinguish unknown from stale.
- Otherwise → recently checked. This is not a promise that upstream has not changed since.
- Report repo name, last verified check time, age, and the recommendation. Example:
  "lore-agents: last checked 31 hours ago. Run `/lr:workspace-pull`."
  At state 2 recommend `git -C <repo> pull --ff-only` for affected repos.
- The command only reads timestamps and local Git state. It does not fetch or pull, and
  running `check` never resets the freshness clock. `--no-network` still includes S19.

**Reuse the per-repo success marker.** `preflight.py` already writes `lr-last-pull` in the
Git directory after a successful `git pull --ff-only`, including "already up to date".
Use its resolver/reader rather than assuming `.git` is a directory. Extend `workspace-pull`
to record the same marker after each successful clone or pull, including the workspace root.
Share the writer through a small callable helper; do not create a second timestamp format.
A skipped or failed operation must not advance the marker; partial runs update successful
repos only. A failed marker write leaves freshness unknown or old and must be reported.

This initial implementation records successful framework-managed pulls as verified checks.
Manual Git operations are not reliably recorded by this marker: label it "last verified
framework check" in details. Do not use `FETCH_HEAD` modification time as proof of success,
commit dates as check times, or the workspace-wide auto-refresh time as evidence for every
child. A failed pull may have fetched successfully, but conservatively retains the old marker.

S19 belongs to the workspace layer and its own `freshness` category; count each affected
repo once. Keep existing behind/ahead findings separate: they describe known Git differences,
while S19 describes how old the evidence is. A single pull recommendation can cover both.

## 7. Change set

Enumerated because a contract change touches sites the diff never shows
(`a-change-set-is-wider-than-its-diff.md`).

**New — Phase 1**
- `scripts/lr_core/plugin_scan.py` — P-findings
- `scripts/lr_core/cli.py` — `check` subcommand
- `docs/findings-catalog.md` — P and S wording, fix tiers, the collapse set
- `tests/test_lr_core_check.py`

**New — Phase 2** (§ 6.7, designed here, built later)
- `scripts/lr_core/repo_scan.py` — R1–R15
- `docs/findings-catalog.md` gains the R entries; `docs/check.md` sheds them
- `tests/test_lr_core_repo_scan.py`

**Edited for freshness — Phase 1**
- `scripts/workspace-pull` — record success per repo, including clone and root paths
- `scripts/lr_core/preflight.py` and the shared timestamp helper — reuse the marker contract
- `docs/workspace-pull.md` and pull documentation — describe the marker and failure behavior
- `docs/findings-catalog.md` — S19 wording and pull recommendation
- `tests/test_lr_core_check.py` and pull tests — freshness boundaries and success-only stamps

**Rewritten**
- `docs/check.md` — front-door procedure, new Step 0 announcement, restates no finding wording,
  and drops its unsupported `agent-boot.md` Step 1 cross-reference (§ 3.1)
- `skills/check/SKILL.md` **and** `.cursor-skills/lr-check/SKILL.md` — neither is a no-op
  edit. Today `skills/check/SKILL.md` has **no `argument-hint` frontmatter and no
  `$ARGUMENTS` in its body**, so § 12's scope argument has nothing to arrive through; follow
  `skills/recall/SKILL.md`, which carries both. Its `description` also still reads *"Run
  consistency checks across the domain and all agents"*, which no longer describes the
  command. Re-run `scripts/sync-cursor-skills` after.

**Deleted**
- `skills/doctor/`, `.cursor-skills/lr-doctor/`
- `skills/workspace-status/`, `.cursor-skills/lr-workspace-status/`
- `docs/workspace-status.md` (catalog migrated)
- **`docs/doctor.md`** — the ~120-line orchestrator the deleted skill pointed at. An earlier
  draft of this change set dropped it silently: it named 14 of the 15 files referencing
  "doctor", and the one it missed was the one that *is* the command. Its "Authoring an
  Ailment" schema is worth keeping — move it into `docs/findings-catalog.md` as the schema
  for a fix doc, and delete the rest.

**Renamed — 2 files, not 3.** `doctor-stale-plugin-cache.md` and
`doctor-stale-shortcut-bootstrap.md` → `fix-*.md`. `doctor-cursor-session-without-plugin.md`
is **not** renamed; it folds into `INSTALL-CURSOR.md` (§ 9). An earlier draft said "3 files"
and then excepted one in the next sentence — read literally that leaves an orphan
`fix-cursor-session-without-plugin.md` nothing points at.

**And the renames are not filesystem operations.** Their bodies need rewriting:
- `doctor-stale-plugin-cache.md`'s bootstrap note tells the reader to *"re-attempt
  `/lr:doctor` to verify"* — a command that will not exist. It becomes P2's bootstrap note
  (§ 6.3).
- Both files' **See Also** sections point at `docs/doctor.md`, which is deleted.
- `doctor-cursor-session-without-plugin.md` has a "Not this ailment" table routing to the bare
  slug `doctor-stale-plugin-cache` and to `docs/doctor.md`; and `INSTALL-CURSOR.md`'s
  troubleshooting table **already has a row pointing at the file being folded in**. This is a
  reconciliation of two overlapping tables plus a self-referencing row, not a paste.

**Edited.** An earlier draft claimed 16 files reference `workspace-status` and 14 reference
`doctor`. **Both counts were low** — the grep behind them missed repository-root `.md` files.
Verified counts, excluding historical `release-notes/`: **19** and **15**. Re-grep anyway.

- `docs/workspace-init.md` — two sites: the Step 1 catalog pointer **and** the hard-coded
  `AGENTS.md` generation template (~line 504) whose skill table has a `workspace-status` row.
  Fixing only the first leaves every regenerated `AGENTS.md` advertising a dead command.
- `docs/conventions.md` — two sites, and one is load-bearing: **line 377 sits inside the
  literal cache-clear-footer template** that every cache-affecting release note copies
  verbatim, and it cites `docs/doctor-stale-plugin-cache.md` by path. This ship *is*
  cache-affecting, so its own release note would propagate the dead filename. Line 524 cites
  it again.
- `docs/workspace-push.md`, `docs/workspace-pull.md`, `docs/agent-boot.md` (Step 2 refresh
  rendering pointer), `docs/register-repo.md`, `docs/create-repo.md`, `docs/create-agent.md`,
  `docs/version-check.md`, `docs/update.md`, `docs/engines/codex.md`, `docs/engines/cursor.md`,
  `scripts/workspace-pull`, `scripts/lr_core/workspace_scan.py` (module docstring, § 6.3),
  `migrations/44.md`
- `README.md`, `INSTALL-CLAUDE.md`, `INSTALL-CURSOR.md` (`INSTALL-CODEX.md` references
  neither command — verified, do not edit it blind)
- **`QUICKSTART.md` and `FIRST-STEPS.md`** — both send a brand-new user to
  `/lr:workspace-status` by name (`QUICKSTART.md` ~92–99, `FIRST-STEPS.md` ~145). These are
  the onboarding docs this design exists to serve, and an earlier draft omitted both.
  Beyond repointing them: **neither file, nor any `INSTALL-*.md`, tells a stuck user to run
  `/lr:check` first.** Collapsing three doors into one only helps someone who knew to reach
  for one of the three, so each of these gains an explicit "something feels wrong — start
  with `/lr:check`" line. That is part of this ship, not a follow-up.
- `AGENTS.md` skill table in this workspace, and `/lr:workspace-init`'s regeneration of it

**Version ship** (per role.md § Lore-Curation Disciplines): `VERSION` bump, four manifests to
`1.<N>.0`, `versioning-release-types.md` backfill, **cache-affecting → cache-clear footer
hoisted** (skills are deleted; a stale cache keeps showing `/lr:doctor` and
`/lr:workspace-status`, which is exactly the confusion this ship removes).

No migration is required — nothing in a user repo needs rewriting.

---

## 8. Tests

Every new test must be shown **red against `lr--v1.44.0` and green against HEAD**, in a
detached worktree via `LR_FRAMEWORK_DIR` (`prove-a-new-test-red-against-the-previous-tag.md`).
A green suite written by the fix's author is a self-report until then.

| Test | Asserts |
|---|---|
| state ladder | fixtures for 1/2/3 → correct derived `state` |
| state-1 sub-cases | inside a repo → `1b`; below a workspace → `1c`; **above one → `1d`**; none → `1a` |
| **1d precedence** | a workspace one level down is reported, never "no lore repos here" |
| probe bounds | nothing outside cwd opened beyond the two descriptor filenames; a workspace **two** levels down is *not* found (the honest limit, pinned) |
| worktree | a session in `.worktrees/<repo>/<slug>/` resolves through `resolve_workspace_root`, not into a wrong sub-case |
| scanner untouched | `applicable` and every other field byte-identical to v44 for all fixtures |
| P2 | a fabricated higher-version cache dir fires it; equal versions do not |
| P1 offline | probe failure → `upstream: "unknown"`, zero findings, exit 0 |
| P1 online | **injected**, never a live network call from the suite |
| P4 skips | absent `marketplace.json` / `.codex-plugin/plugin.json` → no finding, not an error |
| collapse set | at state 2, S4/S5/S10/S17/S18 collapse and **S3 does not** |
| **catalog coverage** | every finding ID the script can emit has an entry in `docs/findings-catalog.md`, with a fix tier |

Phase 1 freshness tests: exactly 24h / over 24h; missing, invalid, non-finite and future
markers; repo without remote; Git directory file/worktree resolution; successful no-change
pull; failed/skipped pull; partial workspace pull; successful clone; marker-write failure.
Assert that `check` makes no repo network calls or timestamp writes, that state 2 includes
S19, and that a workspace-wide success timestamp cannot hide one stale child.

Phase 2 adds (§ 6.7):

| Test | Asserts |
|---|---|
| R1–R15 vs today | each fires on a fixture that today's check #N also flags — no silent coverage loss in the port |
| **R12 home-shortcut exemption** | an absolute `from` target in `~/.codex/skills/` is **not** flagged; a workspace-local one is |
| R12 single source | the format rules come from the same source `register-repo` and migration 44 write, not a copy |
| R6 cost | one in-process pass over all agents stays inside the budget § 6.7 names |
| R15 names | exact and normalized matches; real mismatch; intentional alias remains a review finding; missing target/name; duplicate names in different repos compare the resolved target |
| exact vs reviewed | the summary counts R1–R15 and reports the AI summary-accuracy assessment separately, never folded into the number |

Fixtures for P2 and P5 already exist on the development machine — cache versions `1.42.0`,
`1.43.0` and `1.44.0` side by side, and a `~/.codex/.tmp/marketplaces/lore-framework.v32.bak-20260831`.
Useful for manual confirmation; the suite itself must **fabricate** its own trees, since a test
that depends on one machine's disk is not a test.

The last one is the load-bearing test. It mechanically enforces the seam that
`script-emits-data-doc-owns-the-words.md` says fails by default — a script finding with no
words is a symptom shown to a user with no remedy — and it can genuinely fail, which a
string-containment test over prose cannot.

---

## 9. Explicitly out of scope

**State 0 — no plugin loaded.** The user's third symptom ("didn't see workspace level
commands") is a state in which `/lr:check` does not exist either. Two of doctor's three
ailments describe it. No command can be the answer; `doctor-stale-plugin-cache.md` admits
this in its own bootstrap note.

**And a second reading of symptom 3 that this design only half-closes.** "Didn't see workspace
level commands" need not mean *no* plugin — a **partially stale cache** shows some skills and
not others, which is one of `doctor-stale-plugin-cache.md`'s own listed signatures and is at
least as likely as no plugin at all. P2 is built to catch exactly that, and cannot reach the
session suffering it (§ 6.3). So of symptom 3's two plausible readings, this design closes
neither from inside a session: one is State 0, the other is P2's bootstrap trap. Both land in
the installer docs. That is the honest accounting — an earlier draft disclosed only the first.

State 0 belongs to the paste-link installer genre already recorded in
`paste-link-installer-doc-genre.md` — `QUICKSTART.md` plus per-engine
`INSTALL-<ENGINE>.md`, written to the AI agent as the literal installer. This design does
**not** solve it, and shipping this without also fixing the installer docs leaves one third
of the reported symptom untouched. Named here so it is not mistaken for covered.

**Script-backing the repo layer.** Most R-findings are mechanical and most primitives
already exist (`discover`, `lore-map`, `shortcut_inventory`), but converting them is item A1
on `workdir/what-to-improve.md`, sized independently. See § 10.

---

## 10. Phasing

**Phase 1 — the front door.** State ladder, plugin layer, doctor merge, workspace section
reusing today's scan plus S19 freshness and successful-pull recording. The repo section runs as it does today (LLM-executed) and the summary
says so rather than claiming a count it cannot guarantee. Delivers the whole user-visible
value: any directory, any engine, one command, correct rung, correct next step.

Default-run cost stays low — the plugin and workspace layers are deterministic and fast; the
per-agent deep lore validation runs only under `--full`.

**Phase 2 — build the repo layer (completes A1).** Implements § 6.7: R1–R15 computed, the `~`
in § 5 gone, the O(topics × refs) under-extraction measured on 2026-07-18 removed. Only summary accuracy (#15) stays with the model; R15 discrepancies may need AI interpretation.

**Designed in this document, not deferred to a later design** (user decision, 2026-09-08).
The split matters: the catalog schema, the fix-tier column and the summary's exact-vs-
approximate contract are all shaped by what R will eventually emit, so specifying R now costs
one section and saves retrofitting three things later. Only the code is deferred.

"Completes", not "subsumes": A1 asks for checks "~#2–3, #9–11, #13–14, #19–21", and #19–21
become P4/P6/P7, which **Phase 1 already scripts**. So Phase 1 delivers part of A1 and Phase 2
the rest.

---

## 11. Sequencing

`v45-boot-announcements` is already in flight in a worktree (one commit, four doc files,
including `docs/conventions.md`). This lands on its own branch off `main` as **v46**, or
folds into v45 if that branch has not shipped. The only overlap is `conventions.md`.

---

## 12. Settled decisions — 2026-09-08

1. **Scoped invocation uses flags:** `/lr:check --workspace`. The user delegated the choice
   and preferred the existing `--` convention. `skills/check/SKILL.md` needs `argument-hint`
   + `$ARGUMENTS` added (§ 7). This skill flag selects the workspace layer; the internal
   `lr-core check --workspace "<cwd>"` argument supplies the scan directory.
2. **Ailment-doc Diagnosis sections — keep them for now.** They are the hand-run confirmation
   steps from doctor's symptom-matching workflow, made largely vestigial once P2 and P4 compute
   the fact. Revisit once `/lr:check` has accumulated its full functionality. Filed in
   `framework-improvements-backlog.md` § Framework Upkeep so the revisit is not lost. One part
   of them must survive regardless: the bootstrap trap in § 6.3 has no computed path.
3. **The repo layer is designed now (§ 6.7), implemented in Phase 2.** Not deferred to a
   later design pass.
4. **No symptom confirmation before building.** The § 1 mapping stays inferred and is
   disclosed as such; the decision is to design well for `check` rather than gate the work on
   interviewing colleagues. The residual risk is unchanged and stated: if the real cause is
   the stale-cache reading rather than the wrong-directory one, this ship improves the product
   without unsticking the person who reported it.

5. **Script shortcut-name matching and repo freshness.** R15 performs mechanical name comparison;
   S19 warns when the last verified repo check is more than 24 hours old and recommends a pull.
