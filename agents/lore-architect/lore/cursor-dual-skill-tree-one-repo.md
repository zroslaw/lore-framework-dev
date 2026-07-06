# Cursor Dual Skill Tree (One Repo)

Shipped pattern for Cursor skill naming without breaking Claude Code — **SHIPPED in canonical
`lore-framework` as v21 (commit `f7b1c2b`, manifests `1.21.0`, `release-notes/21.md`, 2026-07-06)
and full-harness-verified against the real v21 tree.**

## Problem

Cursor shows the **skill folder name** in the picker. Plugin manifest `name: "lr"` does **not**
namespace skills the way Claude Code's `/lr:<skill>` does. Unprefixed folders (`boot`, `recall`)
collide visually with unrelated skills and confuse mixed-engine teams.

Cursor docs + empirical check (2026-07): frontmatter `name: lr-boot` inside folder `boot/` does not
fix the picker; renaming the folder to `lr-boot/` does. Category folders like `skills/lr/boot/`
still display as `boot`.

## Solution

Dual trees in one repo:

| Engine | Path | User invokes |
|---|---|---|
| Claude Code | `skills/<skill>/` | `/lr:<skill>` |
| Cursor | `skills/cursor/lr-<skill>/` | `/lr-<skill>` |

Cursor discovery is scoped by `.cursor-plugin/plugin.json`:

```json
"skills": "skills/cursor/"
```

Each cursor wrapper is a thin `SKILL.md` pointer to the same `docs/<skill>.md` as the canonical
skill. Differences only: `name: lr-<skill>`, description uses `/lr-<skill>`, self-location says
**three** levels up (`skills/cursor/lr-<skill>/SKILL.md`).

## Maintenance

After adding or renaming a canonical skill:

```sh
python3 scripts/sync-cursor-skills
```

`/lr:check` step 21 verifies cursor/canonical parity.

## Supersedes

The separate `lore-framework-cursor/` sibling that renamed top-level skill folders is superseded —
delete when convenient.

## Validation status (2026-07-06)

**Full-harness-verified before the ship** — the prior "implemented but unverified" caveat is
retired. The complete lifecycle suite passed **19/19** scenarios + 23 deterministic = **42/42** on
the `claude` engine (~$9.4, ~27 min); `/lr:check` #19/#20/#21 clean; `sync-cursor-skills` confirmed
idempotent (regenerates identically). Running the *complete* suite (not a proportionate subset) as
the last gate before push is the discipline this ship reinforced — see
`execution-testing-catches-blind-ambiguity.md` (pre-ship = pre-push).

## See also

- `slash-command-system.md` — cross-engine invocation table
- `cursor-port-validated-end-to-end.md` — v20 engine profile landing
- `docs/engines/cursor.md` — invocation-syntax binding
- `lifecycle-testing-harness.md` — regression gate before shipping v21
