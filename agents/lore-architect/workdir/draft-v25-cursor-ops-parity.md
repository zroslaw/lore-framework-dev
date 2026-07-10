# Draft — v25 Cursor Ops Parity

Status: **approved — ready to implement** (Round 4, 2026-07-10).
Session: 2026-07-10.

Supersedes: nothing (extends Cursor Tier-1 lifecycle from v20–v24).
Related: `cursor-engine-capabilities.md`, `INSTALL-CODEX.md`, `INSTALL-CURSOR.md`,
`framework-improvements-backlog.md`.

## Review history

| Round | Date | Verdict | Key outcome |
|-------|------|---------|-------------|
| 1 | 2026-07-10 | Approve with changes | Cache-clear; canonical fallback; Tier B discovery-first; doctor cross-refs |
| 2 | 2026-07-10 | Approve with (small) changes | Drop A6; mandatory harness; extend check #19; `cursor-agent` primary |
| 3 | 2026-07-10 | Approve with changes | Install bootstrap model; fallback file-path rules; doctor atomicity; gate ordering; drop hook template |
| 4 | 2026-07-10 | **APPROVE (ready to implement)** | Zero blocking issues; 5 implementation nits incorporated below |

---

## The Problem

Cursor has **Tier-1 lifecycle parity** (v20–v24) but **operator ergonomics lag Codex**: no install/refresh
scripts, no README self-install block, undocumented mid-session fallback, Claude-centric Quick Start,
unclear IDE vs CLI load surfaces, no doctor ailment, and **`.cursor-plugin/plugin.json` unchecked by
`/lr:check` #19** (lagged at `1.23.0` while `.claude-plugin/plugin.json` reached `1.24.0`).

## Objective

Ship **v25** as **Cursor ops parity**: documented install sequence, refresh scripts, team automation,
first-class mid-session fallback contract, doctor coverage, three-manifest discipline — **without**
changing Tier-1 lifecycle semantics or claiming Cursor-native subagent fan-out.

### Semantic commitment

The framework commits that when a host is pointed at a local checkout, it can execute Lore by reading
**`.cursor-skills/lr-<skill>/SKILL.md`** (which delegate to `docs/<procedure>.md`). Procedure docs must
remain self-contained for file-driven execution. This is a maintainability contract, not prose-only.

## Non-Goals (v25)

- Cursor `/lr:takeover` conversion (`store.db` blocked)
- Native parallel subagent fan-out
- Quality-benchmark tier restructure
- New `/lr:*` skills (doctor ailment text only)
- Marketplace publish as ship criterion
- **Runnable `workspaceOpen` hook templates** (API unverified — probe notes only)
- **Tier B marketplace install in v25** unless probe completes with pass criteria **before** final gate

## Success Criteria

1. Documented **install sequence** (clone + helper script + launch) works for a new teammate.
2. `cursor-refresh-plugin` updates checkout and states fresh-session requirement.
3. README includes Cursor self-install block and engine-syntax legend.
4. `INSTALL-CURSOR.md` matches `INSTALL-CODEX.md` depth.
5. `docs/engines/cursor.md` is canonical for fallback + load surfaces + refresh contract.
6. `doctor-cursor-session-without-plugin` ailment (atomic) with differential routing.
7. `/lr:check` #19 + `conventions.md` cover **all three** manifests.
8. Script smoke tests (temp HOME) + full `LR_LIFECYCLE=1` on `claude` + **real Cursor fallback smoke**
   pass on **final tree** immediately before commit + push.
9. `VERSION` 25 / manifests `1.25.0` / `release-notes/25.md` with near-top cache-clear section.

---

## Design Principles

- **Codex parity for ops shapes, not mechanisms**
- **Deterministic load:** `cursor-agent --plugin-dir <checkout>` (verified)
- **Persistent load:** symlink / IDE / marketplace — **unverified until D2/probe; may not ship as "install"**
- **Session boundary is real** — no hot-reload
- **Engine-specific content in engine profiles** — no Cursor prose in universal `agent-boot.md`
- **Portable BSD-safe bash** for scripts
- **Atomic doctor ailments** — one root cause per topic

---

## Pre-implementation decisions (settled)

| # | Decision | Resolution |
|---|----------|------------|
| D1 | CLI binary | **`cursor-agent`** in all examples; footnote: `agent` may alias on some installs |
| D2 | Symlink creates install? | **Gates symlink step** — if IDE doesn't load from `~/.cursor/plugins/local/`, script skips symlink creation and documents `--plugin-dir` only |
| D3 | Tier B in v25? | **Deferred by default** — probe runs parallel; Tier B docs/code only if pass criteria met before final gate |
| D4 | Doctor slug | `doctor-cursor-session-without-plugin` |
| D5 | `agent-boot.md` Cursor note | **Dropped** — fallback pre-boot via `cursor.md` |
| D6 | Harness gate | **Last** — after all content + manifests; immediately before commit + push |

---

## Deliverables — Tier A (required)

| # | Item | Notes |
|---|------|-------|
| A1 | `scripts/install-cursor-plugin` | Post-clone helper; see § Install model |
| A2 | `scripts/cursor-refresh-plugin` | Git pull + VERSION diff + launch hint |
| A3 | `INSTALL-CURSOR.md` | Full restructure; no hook template |
| A4 | README bounded sweep | Engine legend + Concepts/Quick Start/skills table/memory file |
| A5 | `docs/engines/cursor.md` | Canonical fallback + load surfaces + refresh + file-driven invocation |
| A7 | `docs/doctor-cursor-session-without-plugin.md` | Atomic ailment + differential routing |
| A7b | Register in `docs/doctor.md` Catalog + `doctor-stale-plugin-cache.md` See Also | |
| A8 | `release-notes/25.md` | Near-top cache-clear; engine-specific refresh |
| A9 | VERSION 25; three manifests → 1.25.0 | |
| A10 | Verify `version-check.md` | One-line re-read after A3 |
| A12 | Extend check #19 + `conventions.md` § Plugin Manifest Versioning | + lore topic updates at finalize |

**Dropped:** A6 (`agent-boot.md` note), C1 (runnable hook template in INSTALL).

---

## Install model (fixes Round 3 circular bootstrap)

v25 does **not** claim a single self-contained script for users with zero prior clone. It ships a
**documented two-step install sequence**:

### Step 1 — Bootstrap checkout (user or agent)

```bash
git clone https://github.com/zroslaw/lore-framework.git "${LORE_FRAMEWORK_DIR:-$HOME/src/lore-framework}"
```

Or update existing: `git -C "$LORE_FRAMEWORK_DIR" pull --ff-only`

### Step 2 — Post-clone helper

```bash
bash "$LORE_FRAMEWORK_DIR/scripts/install-cursor-plugin" "$LORE_FRAMEWORK_DIR"
```

The helper **requires** an existing checkout (validates `VERSION` file present). It does not replace
Step 1.

### Step 3 — Launch (deterministic)

```bash
cursor-agent --plugin-dir "$LORE_FRAMEWORK_DIR"
```

### What the helper does (A1)

```bash
scripts/install-cursor-plugin [--no-pull] [--no-symlink] [TARGET_DIR]
```

1. Resolve `TARGET_DIR` to absolute path; default `$LORE_FRAMEWORK_DIR` or `$HOME/src/lore-framework`.
2. **Validate:** `VERSION` exists under `TARGET_DIR`; else exit 1 with "run git clone first".
3. If not `--no-pull` and git repo → run git with portable-shell fast-fail env (same as
   `scripts/workspace-sync`): `GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10' git -C "$TARGET_DIR" pull --ff-only` (warn on failure, continue).
4. **Symlink (D2-gated):** only if D2 probe **passed** (recorded in C2) and not `--no-symlink`:
   - `mkdir -p ~/.cursor/plugins/local`
   - Refuse to replace existing **non-symlink** at `~/.cursor/plugins/local/lore-framework` (exit 1)
   - `ln -sfn "$TARGET_DIR" ~/.cursor/plugins/local/lore-framework`
5. Print: VERSION, `cursor-agent --plugin-dir` command, symlink status (created / skipped / unverified),
   pointer to `INSTALL-CURSOR.md`.

**Edge cases:** dirty checkout (pull may fail — warn), wrong remote (out of scope), dangling symlink
(`ln -sfn` replaces), paths with spaces (quote-safe), repeated invocation (idempotent).

**README / INSTALL agent block:** agents run Steps 1–3 when asked to install Lore.

---

## A2 — `scripts/cursor-refresh-plugin`

```bash
scripts/cursor-refresh-plugin [TARGET_DIR]
```

**Path resolution order:** positional `TARGET_DIR` → env `LORE_FRAMEWORK_DIR` → valid symlink target
at `~/.cursor/plugins/local/lore-framework` → `$HOME/src/lore-framework` → error.

**Behavior:**

1. Validate checkout (`VERSION` exists).
2. `OLD_HEAD=$(git -C "$TARGET_DIR" rev-parse HEAD)`; read `VERSION` before.
3. `GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10' git -C "$TARGET_DIR" pull --ff-only`
   (exit non-zero on failure — print error; team wrapper aborts; no `--force-continue`).
4. `NEW_HEAD=...`; read `VERSION` after.
5. If `OLD_HEAD != NEW_HEAD`: print VERSION before→after + `git log --oneline -n 10 "$OLD_HEAD..$NEW_HEAD"`.
6. Print fresh-session reminder + `cursor-agent --plugin-dir "$TARGET_DIR"`.

No marketplace branch until Tier B pass (no commented placeholders).

---

## A5 — `docs/engines/cursor.md` (canonical)

### Detecting "plugin not loaded" on Cursor

**Do not use `${CLAUDE_PLUGIN_ROOT}`** — it is always empty on Cursor, even when the plugin loaded.

Use: expected plugin skill (e.g. `/lr-boot`) **not available** in the session skill list.

### Mid-session fallback (canonical — only copy)

When plugin skills are unavailable and the user provides a checkout path:

1. Treat that path as `<framework-root>` (must contain `VERSION`).
2. Read `docs/engines/cursor.md` (this file) for engine bindings.
3. For a requested operation `/lr-<skill>`: read `.cursor-skills/lr-<skill>/SKILL.md` and follow it
   (it delegates to the correct `docs/<procedure>.md`).

**Name mapping is not mechanical** — always use the wrapper SKILL, not `docs/<skill>.md` guesswork.
Examples: `lr-boot` → `agent-boot.md`; `lr-merge` → `process-merge.md`; `lr-register-repo` →
`register-repo.md`.

User must communicate checkout path (paste in chat, `AGENTS.md`, workspace layout).

### Refresh contract

- Update checkout on disk (`git pull`).
- **New session required** — no hot-reload:
  - **CLI:** new `cursor-agent --plugin-dir <path>` process
  - **IDE:** new agent chat / restart (exact gesture varies; symlink path D2-dependent)
- Running session: fallback above (works **before** boot — Step 0 engine profile optional)

### Load surfaces (honest table)

| Surface | Mechanism | Verified |
|---------|-----------|----------|
| Agent CLI | `cursor-agent --plugin-dir <checkout>` | **Yes** (v20+) |
| Local plugins dir symlink | `~/.cursor/plugins/local/` | **D2 probe** |
| IDE chat without `--plugin-dir` | Customize / local plugins | **D2 probe** |
| Marketplace | TBD | **Deferred (Tier B)** |

---

## A7 — Doctor: `doctor-cursor-session-without-plugin`

Follow `docs/doctor.md` § Authoring an Ailment schema: **Symptoms**, **Diagnosis** (include
differential table below), **Remedy**, **Why It Happens**, **See Also**.

**Register** as `#### doctor-cursor-session-without-plugin` under `docs/doctor.md` § Catalog §
Plugin & runtime (not just See Also — required for step-2 matching).

**Atomic root cause:** Cursor agent session started **without** the Lore plugin loaded.

**Symptoms:**

- `/lr-boot`, `/lr-doctor`, etc. not in skill list
- User expected Lore slash commands after opening IDE chat or CLI without `--plugin-dir`

**Not this ailment (differential routing):**

| Symptom | Route to |
|---------|----------|
| Skills listed but wrong/old content after upgrade | `doctor-stale-plugin-cache` (Claude-specific remedy; Cursor → refresh checkout + new session) |
| `R > F` version stamp mismatch | `version-check.md` / INSTALL refresh |
| Invalid/missing checkout path | Install sequence § Step 1 |

**Diagnosis:**

1. Confirm `/lr-boot` missing from skill list.
2. Confirm whether session is IDE chat vs `cursor-agent` CLI.
3. Check checkout `VERSION` at known path vs expected.

**Remedy:**

```bash
bash "$LORE_FRAMEWORK_DIR/scripts/cursor-refresh-plugin" "$LORE_FRAMEWORK_DIR"
cursor-agent --plugin-dir "$LORE_FRAMEWORK_DIR"
```

**Same-session workaround:** `cursor.md` § Mid-session fallback (file-driven via `.cursor-skills/`).

**Why It Happens:** Cursor loads plugin skills at session start only; IDE chat and CLI sessions
started without `--plugin-dir` (and without a verified local-plugin path) have no registered `/lr-*`
skills.

**Note:** `/lr-doctor` itself is unavailable in this state — user reads this topic directly or uses
fallback boot.

---

## A12 — Three-manifest discipline

**Current state (verify at implementation):**

| File | Current version |
|------|-----------------|
| `VERSION` | 24 |
| `.claude-plugin/plugin.json` | 1.24.0 |
| `.claude-plugin/marketplace.json` (lr) | 1.24.0 |
| `.cursor-plugin/plugin.json` | 1.23.0 ← **lag** |

**Changes:**

1. `docs/check.md` #19 — read all **three** files; all must equal `1.<N>.0`; graceful skip if
   `marketplace.json` missing (existing backlog item).
2. `docs/conventions.md` § Plugin Manifest Versioning — "**three** manifests" not two. Frame
   `.cursor-plugin/plugin.json` as **consistency hygiene / mechanical parity** — do **not** claim it
   is a verified Cursor cache-detection lever (that mechanism is verified for Claude only).
3. `role.md` § Plugin-manifest-version bump — list all three.
4. `plugin-manifest-versioning.md`, `consistency-checks.md` lore topics — same.
5. v25 bump all three to `1.25.0`.

---

## A4 — README bounded sweep (not two phrases only)

Minimum scope:

1. **Engine syntax legend** (once, near Quick Start): `/lr:<skill>` Claude, `/lr-<skill>` Cursor,
   `$lr-<skill>` Codex; fallback pointer to `INSTALL-CURSOR.md`.
2. **Concepts** — workspace = directory you run your coding agent from (not "Claude Code").
3. **Boot / Finalize** — engine-neutral phrasing with syntax legend reference.
4. **Quick Start** — "open coding agent from workspace root"; `/lr:init` → `AGENTS.md` on Codex/Cursor.
5. **Skills table** — add column or footnote for Cursor invocation where names differ.
6. **Directory layout** — `.cursor/skills/` for Cursor registered shortcuts; `AGENTS.md` memory file.
7. **Cursor install block** — Steps 1–3 from § Install model.

---

## A8 — `release-notes/25.md`

- **Clear Plugin Cache** section **near top** (not bottom footer) per `role.md` discipline.
- Claude: targeted `~/.claude/plugins/cache/lore-framework/` clear + new session.
- Cursor: `scripts/cursor-refresh-plugin` + `cursor-agent --plugin-dir` + new session.
- Codex: existing `codex plugin add` pattern (unchanged).
- Note: cache-affecting because `doctor.md` catalog + `cursor.md` contract + `conventions.md` change.
- Migration: none.
- Harness: full lifecycle run noted.

---

## Tier B — Probe (parallel, non-blocking, **deferred from v25 unless pass before final gate**)

Record in `workdir/cursor-marketplace-probe-notes.md`.

### Full checklist

| Step | Action | Pass criterion |
|------|--------|----------------|
| 0 | `cursor-agent --help \| grep -i plugin` | Document available commands or "none" |
| 1 | D2: install script symlink only; fresh IDE chat | `/lr-boot` visible without `--plugin-dir` |
| 2 | If step 0 found marketplace commands, run them | `/lr-boot` without `--plugin-dir` on CLI |
| 3 | After `git pull` in checkout, repeat step 2 | Updated VERSION reflected in session |

**If step 0 finds no plugin commands:** Tier B closed — marketplace not viable on this CLI build.

**If D2 fails:** INSTALL states persistent install = checkout + `--plugin-dir` only; A1 skips symlink by default
or prints warning.

**No INSTALL hook template** regardless of probe outcome.

---

## Testing & verification plan

### 1. Script smoke (temp HOME) — before lifecycle gate

- `install-cursor-plugin` on fresh temp dir clone
- Idempotent re-run
- `cursor-refresh-plugin` with unchanged/changed VERSION
- Pull failure exits non-zero

### 2. Manual Cursor fallback smoke — **required**

- IDE or CLI session **without** plugin
- User provides checkout path
- Boot `lore-architect` via `.cursor-skills/lr-boot/SKILL.md` → `agent-boot.md`
- At least one renamed procedure: e.g. `lr-merge` → `process-merge.md`

### 3. D6 — full `LR_LIFECYCLE=1` on `claude` — **last gate**

Run against **final tree** (all docs, scripts, manifests, release notes) immediately before
commit + push. Per `role.md` § Empirical pre-ship verification — complete suite, not subset.

### 4. Optional

- Targeted Cursor harness scenarios (supplement only)

---

## Implementation order (final)

1. D2 probe + document in C2
2. A10 verify version-check
3. A12 check #19 + conventions.md
4. A1, A2 scripts + temp-HOME smoke
5. A5 cursor.md
6. A7 doctor ailment
7. A3 INSTALL-CURSOR
8. A4 README sweep
9. Tier B probe (if time; before gate if pursuing B)
10. A8 release-notes/25.md
11. A9 VERSION + manifests
12. **Cursor fallback smoke**
13. **D6 full lifecycle on claude**
14. commit + push framework
15. Post-ship finalize (same session): lore topics + `versioning-release-types.md` v25 entry
    (**cache-affecting: yes** — scripts + SKILL-referenced doc changes)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Install script bootstrap confusion | Two-step model explicit in README/INSTALL |
| Symlink false promise | D2 gates creation |
| Fallback name mapping wrong | Always via `.cursor-skills/lr-*/SKILL.md` |
| Doctor ailment too broad | Atomic slug + differential table |
| Harness run too early | D6 absolutely last |
| Three-manifest discipline drift | A12 updates conventions + check + role |

---

## Open questions — resolved by lore-architect (2026-07-10)

| # | Question | Decision |
|---|----------|----------|
| 1 | Default clone path | **`$HOME/src/lore-framework`**; override via `LORE_FRAMEWORK_DIR` |
| 2 | Remote `curl \| bash` | **Defer** — two-step clone + script is sufficient for v25 |
| 3 | `scripts/cursor-lore` PATH wrapper | **Defer** — team automation snippet in INSTALL is enough |
| 4 | Refresh pull failure | **Exit 1** — no `--force-continue`; team wrapper aborts |
| 5 | Tier B in v25 | **Out of scope unless probe passes before step 13** — do not block ship |
| 6 | D2 symlink default if probe not run pre-ship | **`--no-symlink` default** until D2 recorded in C2; script prints "run with symlink after D2 pass" |
| 7 | `agent` alias | **Document as footnote only**; all examples use `cursor-agent` |

---

## Implementation handoff (next session)

**Start here:** this file + `lore-framework/` checkout on a feature branch.

**Do not re-design.** Four review rounds converged; scope is locked.

**First actions:**

1. Run **D2 probe** on the implementer's machine; write `workdir/cursor-marketplace-probe-notes.md`
   (even a negative result is valuable).
2. Follow § Implementation order steps 2–15.
3. Framework PR is **`lore-framework/` only**. Lore-architect finalize (step 15) is a **separate
   commit** in `lore-framework-dev/agents/lore-architect/`.

**Ship checklist (copy-paste):**

```
[ ] D2 probe notes written
[ ] scripts/install-cursor-plugin + cursor-refresh-plugin (chmod +x, temp-HOME smoke)
[ ] check #19 + conventions.md three-manifest
[ ] cursor.md, doctor ailment + catalog registration, INSTALL-CURSOR, README
[ ] release-notes/25.md (cache-clear near top)
[ ] VERSION 25; all three manifests 1.25.0
[ ] Cursor fallback smoke (file-driven boot, no plugin)
[ ] LR_LIFECYCLE=1 claude green on final tree
[ ] Post-ship finalize: cursor-engine-capabilities, backlog, versioning-release-types v25
```

**Estimated scope:** ~15 framework files + 2 scripts; no new `/lr:*` skills; release-notes-only migration.

---

## See also

- `design-doc-before-implement.md`
- `cache-clear-footer-convention.md`
- `docs-engines-convention.md`
- `plugin-manifest-versioning.md`
- `ailment-catalog-pattern.md` — atomic ailments
- `feedback-don-t-defer-completable-scope.md`
