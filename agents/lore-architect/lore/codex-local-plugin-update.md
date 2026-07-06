# Updating a Local Codex Plugin Install (local-source marketplace)

Operational lore extending `codex-cli-plugin-loading-findings.md`: how to make a local Codex
install pick up a new plugin version after the framework changes. Verified on `codex-cli 0.142.5`.

## The setup on this machine

`~/.codex/config.toml` registers the marketplace as a **local source**:
`[marketplaces.lore-framework] source_type = "local"`, `source =
"/Users/yaroslav/Documents/git-repos/lore-framework"`. It points at the **local working copy**, not
the GitHub remote — so there is nothing to git-fetch; the repo just needs to be at the desired
commit. The plugin installs into `~/.codex/plugins/cache/lore-framework/lr/<version>/`.

## What does NOT work for a local marketplace

- `codex plugin marketplace upgrade <name>` → errors: *"marketplace is not configured as a Git
  marketplace."* `upgrade` only refreshes **Git** snapshots.
- `codex plugin marketplace add <same-local-path>` → no-op: *"already added."*
- `codex plugin list` shows the **installed** version, not the available one — so after bumping
  `marketplace.json` it still reports the old version until the plugin is reinstalled.

## What works — remove + re-add the plugin

```sh
codex plugin remove lr@lore-framework      # drops old cache (e.g. 1.18.0) + config entry
codex plugin add   lr@lore-framework       # re-reads live marketplace.json, installs new version
```

`add` re-reads the current `marketplace.json` from the local source and copies the plugin into
`cache/.../lr/<new-version>/`, re-enabling it. After a v19 update the cache held only `1.19.0` (old
`1.18.0` gone), `VERSION`=19, `docs/engines/` present, `config.toml` kept `enabled = true`.

## Verify after

`codex plugin list | grep lr@lore-framework` → `installed, enabled  <new-version>`, and spot-check
`~/.codex/plugins/cache/lore-framework/lr/<new-version>/VERSION`.

## If it were a Git marketplace instead

Then `codex plugin marketplace upgrade <name>` would be the fetch step (the only place a git-remote
source matters). Repointing this machine's local source at the GitHub remote is the prerequisite
for that path.

## Lifecycle-test preflight implication

If a Codex lifecycle rerun is supposed to validate newly-shipped plugin docs or skills, first
verify the installed plugin version under `~/.codex/plugins/cache/...`. This session hit the trap
directly during the v22 targeted `R > F` rerun: the source repo was already at v22, but the
installed plugin still pointed at `1.21.0`, so the scenario surfaced the old generic
`version-check.md` warning from the cached copy rather than the newly-shipped Codex-specific
guidance. Refreshing the installed plugin to `1.22.0` with `codex plugin add lr@lore-framework`
before rerunning made the test exercise the intended behavior and pass.

## See Also

- `codex-cli-plugin-loading-findings.md` — the plugin-loading model this extends (persistent local
  install, not a per-invocation `--plugin-dir` flag).
- `docs-engines-convention.md` — the `docs/engines/` layer whose presence in the new cache confirms
  the update landed.
- `codex-engine-capabilities.md` — the per-engine hub topic for Codex operational facts.
