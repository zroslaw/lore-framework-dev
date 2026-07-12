The `lr` plugin is distributed from its GitHub repository through marketplace metadata that both
Claude Code and Codex consume.

## Marketplace setup

`.claude-plugin/marketplace.json` in the lore-framework repo root (versions track `1.<VERSION>.0`, not the `1.0.0` shown historically — see `plugin-manifest-versioning.md`):
```json
{
  "name": "lore-framework",
  "owner": { "name": "Yaroslav Panasyuk" },
  "plugins": [
    {
      "name": "lr",
      "source": "./",
      "description": "Persistent knowledge system for AI agents",
      "version": "1.25.0",
      "repository": "https://github.com/zroslaw/lore-framework",
      "license": "MIT"
    }
  ]
}
```

Critical details:
- `source` must be `"./"` not `"."` — the trailing slash is required
- `version`, `repository`, `license` are required in the plugin entry (not just top-level)

## Claude Code installation

```
/plugin marketplace add zroslaw/lore-framework
/plugin install lr@lore-framework
```

## Codex installation

Codex uses a persistent plugin install rather than a per-invocation plugin directory:

```bash
codex plugin marketplace add zroslaw/lore-framework
codex plugin add lr@lore-framework
```

The repository README is also an agent-facing install contract: when a user gives Codex the repo
URL and asks it to install Lore, Codex should run these commands itself, request only necessary
permissions, and ask the user to restart Codex. A local checkout path can replace the GitHub
marketplace identifier. See `codex-cli-plugin-loading-findings.md`; updating an existing local
source install is covered by `codex-local-plugin-update.md`.

> **⚠ Codex packaging discrepancy (2026-07-12, unresolved).** The commands above (validated at
> port time, consuming `.claude-plugin/marketplace.json`) disagree with the *current* official
> Codex build-plugins spec, which describes a distinct `.codex-plugin/plugin.json` manifest +
> `.agents/plugins/marketplace.json`. We ship neither. Verify on a real current Codex build which
> packaging Codex actually loads before claiming Codex marketplace-readiness. Full analysis:
> `engine-marketplace-readiness.md`.

As of v22, the framework also ships top-level engine-readable install pages next to the README:
`INSTALL-CODEX.md` and `INSTALL-CURSOR.md`. Use those as the canonical entrypoints for fresh-engine
installs and refresh instructions; the README stays the short cross-engine overview.

## Local development

```bash
claude --plugin-dir ./lore-framework
```

`/reload-plugins` picks up changes without restarting. Reports "0 skills" even when working — this is a display quirk.

## What does NOT work

`pluginDirs` in `.claude/settings.json` is not supported. There is no project-level persistent plugin configuration other than marketplace installation.

## See Also

- `engine-marketplace-readiness.md` — public-marketplace submission + visibility across engines
- `cursor-plugin-distribution-update-model.md` — Cursor update/auto-refresh model
- `plugin-manifest-versioning.md` — the `1.<VERSION>.0` discipline
- `codex-engine-capabilities.md`
- `cursor-engine-capabilities.md`
- `claude-engine-capabilities.md`
