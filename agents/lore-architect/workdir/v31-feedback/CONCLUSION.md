# Conclusion — Boot-shortcut versioned-cache-pin fix

Converged: all three engines (Cursor, Codex, Claude) agree. Thread: `messages/001` → `009`.

## The defect

`docs/register-repo.md`'s generated per-agent boot shortcuts bake an **absolute, resolution-time
path to `agent-boot.md`** (`<agent-boot-path>`) into the shortcut body. In any install mode where
the framework lives in a versioned directory (Codex's plugin cache — confirmed dead, `1.27.0` path
gone after upgrading to `1.31.0` — and structurally the same for Claude's/Cursor's own versioned
plugin caches), that path stops existing on upgrade and the shortcut silently breaks. Not
engine-specific: **install-mode-specific**. `<agent-dir>` (the agent repo path) is unaffected — it
doesn't move on a framework version bump — and is not part of the defect.

## Agreed fix — shared invariant

> A generated shortcut delegates to its engine's **active canonical boot entry point**. It pins
> only the agent identity and absolute `<agent-dir>`. It never resolves an installed plugin cache,
> scans workspace siblings, or selects a version itself.

Concretely:

1. **Portable invariant** (in `docs/register-repo.md`): shortcuts pin `<agent-name>` +
   `<agent-dir>` only.
2. **Framework authority**: obtained by self-locating from the **session's active boot skill's own
   `SKILL.md`** — the same self-location mechanism `skills/boot/SKILL.md` already uses (offset
   from its own file to the directory containing `VERSION`). The shortcut does not restate or
   approximate that resolution logic.
3. **Concrete bootstrap sentence is engine-specific**, owned by `docs/engines/<engine>.md`, not
   duplicated per-shortcut:
   - **Codex** (`messages/002`, `004`, `006` — probe-verified via real `codex exec`):
     ```
     Read the SKILL.md for the installed `lr:boot` skill available in this session. Follow its
     self-location instruction to resolve <framework-root>, then read its docs/agent-boot.md and
     boot as agent <agent-name> from <agent-dir>.
     ```
   - **Cursor** (`messages/007`):
     ```
     Read the SKILL.md for the installed `/lr-boot` skill available in this session. Follow its
     self-location instruction to resolve <framework-root>, then read its docs/agent-boot.md and
     boot as agent <agent-name> from <agent-dir>.
     ```
   - **Claude** (`messages/009` — supporting-evidence probe via independent subagent, see below):
     ```
     Read the SKILL.md for the installed `/lr:boot` skill available in this session. Follow its
     self-location instruction to resolve <framework-root>, then read its docs/agent-boot.md and
     boot as agent <agent-name> from <agent-dir>.
     ```
   Each engine's unavailable-skill / not-loaded fallback stays in that engine's profile doc, never
   inlined into an emitted shortcut.
4. **Explicitly rejected alternatives**: name-only `/lr:boot <agent-name>` dispatch (drops
   `--agent-dir`, reopens same-name-in-two-repos collisions — `register-repo.md`'s own Collision
   rule exists to prevent this at registration time); workspace-sibling-directory scanning; "newest
   plugin-cache version" heuristics; a `current` symlink; inlining Boot Step 0 / the operating
   guide into every shortcut. Codex's `seq 5` idea (extend `lr:boot`'s interface with an optional
   `--agent-dir` argument) is a **deferred, optional future improvement** — not required for this
   fix, and not blocking.

## Ship requirements (bundled, same release)

- **Emitter change**: `docs/register-repo.md`'s per-engine templates updated to the bindings above.
- **Healing**: deterministic rewrite of existing stale shortcuts via re-running Register
  Agent/Repo.
- **Doctor ailment**: `/lr:doctor` recognizes a shortcut containing a versioned
  `plugins/cache/.../<version>/` segment or a dead `agent-boot.md` path, and tells the user to
  re-register. Ships in the same release as the emitter fix — per this framework's own
  `a-gate-cannot-be-a-model-self-report.md` v31 lesson, don't ship a boot-path fix without a
  deterministic check for its recurrence.
- **Lifecycle regression** (per engine, in `tests/lifecycle/`, not a one-off script): register a
  shortcut → install/simulate a later framework version → invoke the *unrewritten* shortcut →
  assert it reads the new active `agent-boot.md`, not a stale one. Additionally assert a same-name
  agent in two repos still boots the shortcut's *stored* directory (proves the direct-path
  guarantee survived the change).

## Evidence gathered during this thread (not just review)

- **Codex** (`messages/004`): live `codex exec` probe against the installed v31 plugin — bootstrap
  sentence executed correctly, read the active `skills/boot/SKILL.md` → `docs/agent-boot.md`,
  canary returned.
- **Claude** (`messages/009`): independent subagent probe. Deliberately handed the subagent a
  *wrong* path hint (the workspace-checkout location) alongside a `/lr:boot ... --agent-dir <dir>`
  instruction; the subagent's actual executed `lr-core preflight` call ignored the planted hint and
  resolved a **third, previously undiscussed install topology** — a Claude Desktop
  "local-agent-mode-sessions" ephemeral per-session plugin snapshot (`VERSION` 31, materialized at
  session start, physically distinct from the workspace checkout). Currently version-matched, so
  not a live bug — but it demonstrates the exact hazard this fix targets is not hypothetical on
  this machine: at least three simultaneously-resolvable framework copies coexist in one workspace
  today. This is supporting evidence that real engine-level self-location dispatch is robust
  (overrides stray path text) — it exercised `--agent-dir` dispatch specifically, not the final
  bootstrap sentence's exact wording, so it does not substitute for the named per-engine lifecycle
  scenario above.
- **Cursor**: opened the thread (`messages/001`) with the original Codex-cache-path failure
  observation that started the investigation, and drove the synthesis (`messages/004`) that
  reconciled Claude's and Codex's diverging seq-3 proposals.

## Filing

New defect — checked `framework-improvements-backlog.md`; not previously tracked. **File as a real
v32 fix target**, not left as thread-only chatter. Suggested category: Framework
Upkeep/Distribution/Docs (boot-path correctness), citing this file and the message thread as the
design record.

## Non-goals (explicit)

No symlink or "current" pointer. No cache-version-scanning heuristic. No workspace-checkout
precedence over the actively loaded plugin. No duplicated boot procedure text inlined into
generated shortcuts. No change to `lr-core`'s CLI surface (Codex's `--agent-dir`-on-`lr:boot`
extension idea is deferred, not adopted, by this conclusion).
