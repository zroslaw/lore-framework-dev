# First Steps — Lore Framework on Codex (manual trial)

Goal: install the `lr` plugin into Codex and boot a lore agent by hand.
Paths assume this machine:
- Workspace (where agent repos live): `/Users/yaroslav/Documents/git-repos`
- Plugin repo: `/Users/yaroslav/Documents/git-repos/lore-framework`

## 1. Install the plugin (one-time)

Codex has **no `--plugin-dir` flag** — plugins install persistently from a marketplace.
Our existing Claude `marketplace.json` works as-is:

```sh
codex plugin marketplace add /Users/yaroslav/Documents/git-repos/lore-framework
codex plugin add lr@lore-framework
```

`lr@lore-framework` = plugin `lr` from marketplace `lore-framework`.
Verify it landed (should list ~26 skills incl. `boot`):

```sh
codex plugin list
```

Installed path is `~/.codex/plugins/cache/lore-framework/lr/<version>/`.
To update later after you change the plugin: `codex plugin update lr@lore-framework`
(or remove + re-add).

## 2. Start a session in the workspace

```sh
cd /Users/yaroslav/Documents/git-repos
codex --sandbox workspace-write
```

Note on network: auto-pull (boot) and finalize push need network. Codex's default
sandbox blocks it. For a first trial that's fine — boot continues in **degraded mode**
and just prints a one-line "pull failed" warning. To actually exercise auto-pull/push,
enable network for the workspace-write sandbox in `~/.codex/config.toml`.

## 3. Boot an agent

Most reliable (this is exactly what the `/lr:boot` skill expands to, and it's the path
we verified passing):

> Read the file at `~/.codex/plugins/cache/lore-framework/lr/<version>/docs/agent-boot.md`
> and boot as agent `lore-architect` from
> `/Users/yaroslav/Documents/git-repos/lore-framework-dev/agents/lore-architect`.

Then just work normally, and to finalize: "run reflection and merge for this session"
(or ask it to read `docs/finalize.md`).

Also worth trying (may or may not surface — untested): the `/skills` picker, or invoking
a skill inline with `$`. If skill names with a colon (`lr:boot`) don't resolve, fall back
to the natural-language boot above.

## Known rough edges (expected, not bugs)

- **`${CLAUDE_PLUGIN_ROOT}` resolves to empty string on Codex.** If the agent seems unable
  to find a `docs/*.md` file, point it at the install path above. (This is the #1 thing the
  planned engine-adapter work fixes.)
- Skill invocation syntax and per-agent shortcut commands (`/lr-<agent>-agent`) are Claude
  conventions — don't expect them to work verbatim yet. Natural-language boot is the fallback.
- Team/workflow/spawn-teammate features are Claude-only — out of scope for this trial.

## What we already verified

Marketplace install + a full boot happy-path (role + lore-context canaries printed,
auto-pull + version check ran, clean tree, no stray commits). Everything above step 3's
"most reliable" path is confirmed working on `codex` 0.142.5.
