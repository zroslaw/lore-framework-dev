---
lore: 1
type: topic
summary: "The v43 project-scope plugin settings feature: committed .claude/settings.json and .cursor/settings.json written by workspace-init, its three code-enforced guarantees, finding S18, and the residual Cursor risk."
parent: lore-context.md
---

# Project-Scope Plugin Configuration (v43)

A Lore workspace can carry **committed** files that make the `lr` plugin available to anyone who
clones it, with no per-person install. Shipped in v43.

| Engine | File | Mechanism |
|---|---|---|
| Claude Code | `.claude/settings.json` | `extraKnownMarketplaces` + `enabledPlugins`; both are "any file" scope per the settings reference, so a committed project file works |
| Cursor | `.cursor/settings.json` | `plugins."<marketplace>/<plugin>"`, optionally carrying `gitUrl` so no prior marketplace registration is needed |
| Codex | — | none; `openai/codex#18115` is open upstream |

**Key formats are reversed between the two engines, and that is not a typo to be "fixed":**
`lr@lore-framework` on Claude, `lore-framework/lr` on Cursor. Cursor accepts only `https://` and
`git@` URLs for `gitUrl`; omitting `gitRef` tracks the default branch.

## Load-bearing design decisions

- **The merge is code, not prose.** `scripts/lr_core/plugin_config.py`, invoked by `workspace-init`
  Step 4 via `lr-core workspace-plugin-config [--dry-run]`, reporting a per-file
  `created` / `updated` / `unchanged` / `error` action. These two files carry a team's permissions,
  hooks, and env — a model-executed JSON merge is exactly how those get clobbered.
- **Never overwrite an existing value for our own keys.** `"lr@lore-framework": false` is a
  deliberate opt-out; converging it back to `true` makes the choice unstickable. Reported as `kept`.
- **A file is rewritten only when a key was actually added.** Content is preserved; whitespace is
  not, since a real write re-serialises at two-space indent. Say that precisely — "re-serialised
  verbatim" was an overstatement caught in review.
- **An unparseable file is refused, not clobbered.** Cursor tolerates comments and trailing commas
  where strict JSON does not.
- **Codex's absence is reported, never silently omitted.** Naming two engines out of three reads as
  "all of them"; `data.unsupported_engines` carries it and Step 9 must say it out loud.
- Both paths joined `MANAGED_PATHS`, so `workspace-push` publishes them. They are **the first
  managed paths whose content is mostly not ours**, which strengthens rather than weakens
  `workspace-push`'s "note when the diff extends beyond the managed region" rule.
- New finding **S18** (info): `missing` and `unresolvable` route differently, and a plugin the user
  explicitly disabled is context, never drift.

## Residual risk

That Cursor actually *reads* `.cursor/settings.json` for plugins is established from its shipped
code, not from an end-to-end run; `docs/engines/cursor.md` § Load surfaces records it as
**unverified**. Neither engine hot-reloads, so a teammate picks the plugin up on their next fresh
session, and Claude Code applies `extraKnownMarketplaces` only after the teammate trusts the folder.

## See Also

- [cursor-plugin-install-is-account-side.md](cursor-plugin-install-is-account-side.md) — the manual
  path this replaces for Cursor.
- [engine-bundle-reading-has-an-evidence-grade.md](engine-bundle-reading-has-an-evidence-grade.md) —
  why the Cursor half ships as unverified.
- [workspace-lifecycle-four-commands.md](workspace-lifecycle-four-commands.md) — the surface it
  extends.
- [a-reported-error-is-not-proof-the-file-survived.md](a-reported-error-is-not-proof-the-file-survived.md),
  [one-question-one-code-path.md](one-question-one-code-path.md),
  [adding-a-write-means-updating-the-approval-gate.md](adding-a-write-means-updating-the-approval-gate.md)
  — the three defects independent reviews found in this feature, each promoted to a rule.
