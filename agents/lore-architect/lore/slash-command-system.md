The framework packages operations as `lr` plugin skills. User-facing invocation and optional
per-agent shortcut artifacts follow each engine's native conventions.

**Plugin skill naming (Claude Code syntax):**
- `/lr:<action>` — all framework operations: boot, reflect, merge, summarize, finalize, register-repo, unregister-repo, create-repo, create-agent, list-agents, list-repos, check, workspace-sync, update, recall, attach, consult, init, spawn-teammate (BETA)
- `/lr-<agent-name>-agent` — optional per-agent boot commands, generated into `.claude/commands/`

**Cursor plugin skill naming (folder = picker identity):**
- `/lr-<action>` — same operations, prefixed wrappers under `.cursor-skills/lr-<action>/`, loaded via `.cursor-plugin/plugin.json`. Canonical `skills/<action>/` stays for Claude Code. See `cursor-dual-skill-tree-one-repo.md`.

Codex exposes optional per-agent autocomplete through engine-native personal skills:
`~/.codex/skills/lr-<agent-name>-agent/SKILL.md`, invoked as `$lr-<agent-name>-agent`. Like the
Claude command, each is a thin absolute-path delegation to canonical `agent-boot.md`.

**Two kinds of `/lr:` skill:** most are **operations** (the list above — they *do* framework work).
A second category is **style skills** (`/lr:plain-language`, `/lr:dialogue`, `/lr:follow-me`) — they
change how the agent *communicates or collaborates*, not what it does. Both kinds share the exact
same thin-pointer mechanics; the split is only about what the skill affects. See `style-skills.md`.

**How skills work:**
- Each skill lives in `skills/<name>/SKILL.md` with YAML frontmatter (`description`, `argument-hint`)
- Skills are thin references — the body is a one-line pointer to a doc in `${CLAUDE_PLUGIN_ROOT}/docs/<file>.md`. All operational logic lives in the doc, which the model reads at invocation time. Keeps skills short, docs authoritative, and logic in one place. See `skill-doc-pattern.md`.
- `$ARGUMENTS` captures user input after the skill name

**Boot flow (single source of truth):**
Direct boot and every per-agent shortcut delegate to `agent-boot.md`, which contains the boot
procedure (discover agent → read files → confirm) and all operating instructions.

1. `/lr:boot <agent-name>` — `Read ${CLAUDE_PLUGIN_ROOT}/docs/agent-boot.md and boot as agent <name>.` Works anywhere the plugin is installed.
2. Per-agent shortcut — one line that reads the absolute canonical `agent-boot.md` path and boots
   the named agent from its absolute agent directory. Claude Code stores it in
   `.claude/commands/lr-<agent-name>-agent.md`; Codex stores it in
   `~/.codex/skills/lr-<agent-name>-agent/SKILL.md`. Plugin-safe absolute-path delegation replaced
   the pre-v5 sibling-path form; see `plugin-compat-template-audit.md`.

Registered per-agent shortcuts are convenience wrappers — the logic they trigger is identical to
direct boot. Never inline boot steps or operating instructions into these artifacts; only
`agent-boot.md` changes.

`/lr:register-repo`, unregister, and list operations select artifact location and display syntax
from the active engine profile. The Codex-aware generation/removal path is currently documented
but not yet lifecycle-tested as an implementation; keep that gap explicit rather than claiming
operational support prematurely.

**Discovery:**
- `/lr:list-agents` — combines engine-native registered shortcuts and directory scan; always finds all agents
- `/lr:list-repos` — scans for directories containing `lore-repo.md`

**Lore recall:**
- `/lr:recall [hint]` — user-triggered mid-session lore recall. Dispatches an Explore subagent with the current session context as a search brief, returns a compact synthesis. See `lore-search-pattern.md`.

**Migration/upgrade:**
- `/lr:update [--dry-run]` — reconciles user-side artifacts with the installed framework version. Walks versions `R+1` through `F`, applying `migrations/<N>.md` and displaying `release-notes/<N>.md` as appropriate. Stamps the new version on success. See `update-process.md`, `versioning-release-types.md`.

**Note:** `/reload-plugins` reports "0 skills" even when skills are working correctly — this is a display quirk, not a failure.
