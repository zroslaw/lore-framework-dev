# First Steps — Lore Framework on Cursor (manual trial)

Goal: load the `lr` plugin into Cursor and boot a lore agent by hand.
Paths assume this machine:
- Workspace (where agent repos live): `/Users/yaroslav/Documents/git-repos`
- Plugin repo: `/Users/yaroslav/Documents/git-repos/lore-framework`

> Heads-up: last probe hit an **account usage-limit** (`ActionRequiredError: You've hit your
> usage limit`) before any real run. Login and model listing worked — it's a quota cap, not a
> tooling bug. If you hit it again, the trial is blocked until the limit resets/upgrades, not
> because of anything we can fix here.

## Option A — Cursor CLI (mirrors the Claude workflow)

`cursor-agent` has a **`--plugin-dir` flag** with the same name and per-invocation semantics
as Claude Code's own — so this is the low-friction path (no persistent install):

```sh
cd /Users/yaroslav/Documents/git-repos
cursor-agent --plugin-dir ./lore-framework --trust
```

Useful flags: `-p`/`--print` (headless), `--output-format json`, `--force`/`--yolo`
(skip confirmations), `--workspace <path>`. Check auth first: `cursor-agent status`.

## Option B — Cursor IDE

Cursor discovers skills from `.agents/skills/` or `.cursor/skills/` (project) and their
`~/` equivalents. Simplest for a trial: symlink our skills in, then open the workspace:

```sh
mkdir -p ~/.agents/skills
ln -s /Users/yaroslav/Documents/git-repos/lore-framework/skills ~/.agents/skills/lore-framework
```

(Cursor can also install skills from a GitHub repo via Customize > Rules — untested against
our layout, where skills live in a `skills/` subdir rather than repo root.)

## Boot an agent

Most reliable (what `/lr:boot` expands to; the fallback that doesn't depend on skill wiring):

> Read `lore-framework/docs/agent-boot.md` and boot as agent `lore-architect` from
> `/Users/yaroslav/Documents/git-repos/lore-framework-dev/agents/lore-architect`.

Then work normally; to finalize: "run reflection and merge for this session."

Also try (Cursor uses `/name`, nicer than Codex's `$`): `/lr-lore-architect-agent` or the
skill picker. If the colon in `lr:boot` breaks resolution, use the natural-language boot.

## Known rough edges (expected, not bugs)

- **`${CLAUDE_PLUGIN_ROOT}`** likely won't resolve — same gap as Codex; point the agent at
  the plugin path if it can't find a doc.
- Cursor auto-manages **git worktrees** for parallel/background agents. Our framework expects
  top-level checkouts on default branches. For a single-session manual trial this won't bite,
  but don't run parallel agents against the agent repos yet — verify worktree interplay first.
- Per-agent shortcut commands and team/workflow features are Claude conventions — out of scope.

## What's verified vs not

Verified: `--plugin-dir` exists and mirrors Claude's; login healthy; `--list-models` works.
**Not** verified: any actual skill load or boot — the quota cap blocked the first run. Treat
this whole doc as "should work, unconfirmed" until a run gets through.
