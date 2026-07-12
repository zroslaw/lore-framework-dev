# Cursor Plugin Distribution & Update Model

How the `lr` plugin propagates to Cursor users, and what "seamless updates" actually requires there.
Grounded in Cursor's official plugin docs (cursor.com/docs) + our port lore, 2026-07-12.

## Three install/update paths (they update differently)

| Path | Update behavior |
|---|---|
| **Cursor Marketplace / individual install** | **Manual.** End users update through the plugins UI ("Customize"). A push to the repo does nothing until they click. |
| **Team marketplace (GitHub-based)** | **Auto-refresh available but opt-in.** Toggle **"Enable Auto Refresh"** + install the **Cursor GitHub App** on the repo; Cursor then re-indexes "at most once every 10 minutes, batching rapid pushes to the latest commit." |
| **Local checkout + `--plugin-dir`** (our verified path today) | **Fully manual:** `git pull` + `scripts/cursor-refresh-plugin`, then a **fresh session**. |

## Two hard invariants (all paths)

- **No hot reload.** Cursor never picks up plugin changes mid-session. Even auto-refresh only rewrites the on-disk plugin; the running session must restart to see it. This is why `scripts/cursor-refresh-plugin` + the "start a fresh session" reminder exist (`cursor-engine-capabilities.md`).
- **Auto-refresh updates existing plugins only.** A brand-new plugin needs a re-import of the repo URL. Irrelevant while `lr` stays a single plugin; relevant if we ever split into multiple plugins.

## Does pushing auto-update everyone? — No, not by default

Only a **team marketplace with Auto Refresh + the Cursor GitHub App** propagates a push automatically, and even then it's "within ~10 min, on the user's next fresh session," not instant. Plain marketplace installs and `--plugin-dir` checkouts are manual.

## Making updates seamless (the framework updates often)

"Update" has **two layers**, and we already own the harder one:

- **Plugin-code layer** (skills/docs/scripts on disk) → governed by *Cursor's* mechanism. The only "push once, everyone converges" lever is **team marketplace + Auto Refresh**.
- **User-artifact layer** (agent repos' `lore-repo.md` version, generated boot shortcuts, migrations) → governed by *us*, and **already seamless**: `agent-boot.md` runs the version-check migration walk on **every boot**, no prompt. Frequent `VERSION` bumps just need a migration/release-note per version, which the ship discipline already requires.

Ranked levers:
1. **Publish via a team marketplace + enable Auto Refresh (+ Cursor GitHub App).** Biggest lever; turns "push to main" into "installs converge on next fresh session." Currently **Tier-B / unvalidated** for us (only `--plugin-dir` is validated) — standing up + validating this is the concrete unlock. See backlog § Marketplace Distribution & Visibility.
2. **Keep the manifest-version bump** (`1.<VERSION>.0`, check #19). Honest change signal even though Cursor's cache use of `version` is undocumented; not a *verified* Cursor cache lever (`cursor-engine-capabilities.md`).
3. **Lean on boot-time auto-upgrade** for the user-artifact half — already shipped and engine-agnostic.
4. **Point the marketplace at a release branch/tag, not raw `main`.** Because re-index batches every 10 min, tracking `main` ships half-committed states to every user. Gate the tracked branch behind the green pre-ship (lifecycle) gate — matters more the more often we update.
5. **Normalize the restart.** No hot-reload is a Cursor invariant; make the fresh-session step routine rather than trying to eliminate it.

**Bottom line:** the user-artifact half is already seamless via boot-time auto-upgrade; the plugin-code half becomes seamless the moment a team marketplace with Auto Refresh is stood up and validated. That's validation work, not redesign.

## See Also

- `cursor-engine-capabilities.md` — refresh script, no-hot-reload, invocation surface
- `engine-marketplace-readiness.md` — cross-engine marketplace submission + manifest visibility
- `plugin-distribution.md` — the cross-engine distribution overview
- `plugin-manifest-versioning.md` — the `1.<VERSION>.0` discipline and its Claude-vs-Cursor status
- `freshness-contracts-at-session-boundaries.md` — auto-pull/auto-upgrade at boot
