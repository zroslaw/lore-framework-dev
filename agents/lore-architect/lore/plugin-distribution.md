The `lr` plugin is distributed from its GitHub repository through engine-specific marketplace
metadata. Claude and legacy Codex installs can consume the Claude marketplace file; native Codex
installs prefer the Codex-native marketplace when present.

Marketplace submission has two layers that should not be conflated:

- **Runtime package metadata** — engine manifests and marketplace files that installers consume.
- **Reviewer-facing submission metadata** — root files such as `MARKETPLACE.md` (copy/paste directory
  fields for Claude Code, Codex, and Cursor) and `PRIVACY.md` (privacy policy URL required by the
  Claude Console submission form).

Keep future submission language precise: `lr--v1.25.0` / runtime commit `09fe4f0` names the release
artifact; `MARKETPLACE.md` and `PRIVACY.md` support review on `main`; per-engine public availability
must be stated only after that engine's live submission/distribution path is verified.

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

Before a public Claude community submission: run `claude plugin validate --strict`, create and push
the plugin tag with `claude plugin tag --push`, ensure `MARKETPLACE.md` has current directory copy,
and ensure root `PRIVACY.md` is reachable from the repository URL.

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

Codex formal packaging is resolved as of v25 on `codex-cli 0.142.5`: Codex still accepts the legacy
`.claude-plugin/marketplace.json` fallback, but when `.agents/plugins/marketplace.json` exists it
prefers the native marketplace file. `.codex-plugin/plugin.json` carries the plugin `version`;
`.agents/plugins/marketplace.json` carries marketplace source/policy metadata and no per-plugin
version. A root-source entry works with `source: { source: "local", path: "./" }`; the valid no-auth
policy enum is `ON_USE`.

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
