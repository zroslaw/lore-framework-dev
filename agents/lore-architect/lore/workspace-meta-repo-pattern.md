---
lore: 1
type: topic
summary: "The optional workspace git repo: an envelope around the workspace layer that tracks the manifest, memory file, README and scripts but not child repos; complements domain repos: and can be skipped for solo local use."
parent: lore-context.md
---

# Workspace Meta-Repo Pattern

Optional **workspace git repo** at `<workspace>/` root — an envelope around the v11 workspace
layer, not a fourth framework layer.

**Tracks:** `lore-workspace.md` (workspace-level repo manifest), `AGENTS.md`/`CLAUDE.md` managed
section, `README.md`, workspace scripts.

**Does not track:** child repo directories — `workspace-pull` appends `/<dirname>/` to
`.gitignore`. Recipe vs code: workspace repo versions how to assemble; child repos version their
own history.

Complements (does not replace) domain-level `repos:` in `lore-repo.md` — `workspace-pull` unions
both at pull time. Solo devs can skip workspace git entirely (local-only mode).

First dogfood target: the user's `agent-workspace` directory, which now exists as a workspace repo with `lore-workspace.md`.

## See Also

- `v25-workspace-pull-init-design.md`
- `workspace-vs-domain-vocabulary.md`
- `plugin-vs-agent-repo-separation.md`
