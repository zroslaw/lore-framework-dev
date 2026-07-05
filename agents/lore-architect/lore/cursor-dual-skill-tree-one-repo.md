# Cursor Dual Skill Tree (One Repo)

Shipped pattern for Cursor skill naming without breaking Claude Code — **implemented in canonical
`lore-framework` source as v21 (2026-07-05); local only until the framework remote is pushed.**

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

## See also

- `slash-command-system.md` — cross-engine invocation table
- `cursor-port-validated-end-to-end.md` — v20 engine profile landing
- `docs/engines/cursor.md` — invocation-syntax binding
