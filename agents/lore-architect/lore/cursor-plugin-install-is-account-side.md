---
lore: 1
type: topic
summary: "Cursor has no non-interactive plugin install: install is a server-side account operation, the local .cloud-plugin-manifest.json is a cache and not an install path, and marketplace names differ between CLI and UI."
parent: lore/cursor-engine-capabilities.md
---

# Cursor Plugin Install Is an Account Operation, Not a File I Can Write

Verified 2026-08-25 against `cursor-agent 2026.08.04-aaa8809`, Cursor staff confirmation, and a read
of the shipped bundle.

**There is no non-interactive plugin install on Cursor.** `cursor-agent plugin` exposes only
`marketplace {add,list,remove,update}`. Cursor staff, in the forum thread about the missing CLI
install, say plainly: *"There isn't a separate non-interactive command like
`cursor-agent plugin install <plugin-id>` yet."* Grepping the shipped bundle agrees — the only
`plugin install` strings there are filesystem path guards.

**Install lives on the server.** The bundle carries Connect RPC clients for `InstallUserPlugin`,
`InstallTeamPlugin`, `UninstallUserPlugin`, and `SetTeamMarketplacePluginPolicies`.

## The trap: the local manifest looks like an install record

`~/.cursor/plugins/cache/.cloud-plugin-manifest.json` holds plugin name, `pluginId`,
`marketplaceSlug`, and `resolvedCommitSha` — exactly what an install record would hold. It is a
**downloaded cache of server state and is overwritten on the next sync**. Writing it is not an
install path. This is worth naming because it is the first thing a capable agent finds when it goes
looking for a scriptable install, and it looks authoritative. It is guarded at the point of use in
`INSTALL-CURSOR.md` § Do not hand-edit the plugin manifest
([point-of-use-guardrails-beat-recorded-lore.md](point-of-use-guardrails-beat-recorded-lore.md)).

## What is scriptable

- `cursor-agent plugin marketplace add <git-url> [--git-ref <ref>]` — account-level, one command.
- `cursor-agent plugin marketplace update <name>` — re-index after a ship.
- `cursor-agent plugin marketplace list --format json` — the observable postcondition for the add.

Only the **enable** step is interactive, and it is **once per account**, not per machine: the
install syncs to the user's other machines and CLI sessions. Cursor's own CLI tip prints
`use /plugins in interactive mode`; the working command is `/plugin` — the tool was wrong about
itself.

## Marketplace naming is derived, and differs by entry point

The marketplace name comes from the repo's marketplace manifest `name`, and Cursor falls back to
`.claude-plugin/marketplace.json` when `.cursor-plugin/marketplace.json` is absent (lookup order is
`[".cursor-plugin/marketplace.json", ".claude-plugin/marketplace.json"]`). Ours resolves to
`lore-framework`.

**The UI prefixes the GitHub owner; the CLI does not.** The same repo added twice appears as
`lore-framework` (CLI) and `zroslaw-lore-framework` (UI) — two registrations of one repo, not a
stale duplicate. Renaming the manifest cannot remove the owner prefix; that is Cursor UI behaviour.
Never promise a user that a rename will fix a name they saw in the UI.

## Team marketplaces are the only zero-touch path

A team marketplace with a plugin marked **Required** auto-installs for everyone in the distribution
group and cannot be uninstalled. Dashboard → Plugins; Team/Enterprise only; no CLI.

## See Also

- [cursor-plugin-distribution-update-model.md](cursor-plugin-distribution-update-model.md) — the
  three install/update paths; this topic supersedes its former "marketplace is Tier-B / unvalidated"
  status.
- [cursor-engine-capabilities.md](cursor-engine-capabilities.md) — the engine hub.
- [project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md) — the committed
  per-project alternative (v43) that avoids the interactive enable step entirely.
- [engine-bundle-reading-has-an-evidence-grade.md](engine-bundle-reading-has-an-evidence-grade.md) —
  how these facts were obtained and at what grade.
