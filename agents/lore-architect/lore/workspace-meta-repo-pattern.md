Optional **workspace git repo** at `<workspace>/` root — an envelope around the v11 workspace
layer, not a fourth framework layer.

**Tracks:** `lore-workspace.md` (workspace-level repo manifest), `AGENTS.md`/`CLAUDE.md` managed
section, `README.md`, workspace scripts.

**Does not track:** child repo directories — `workspace-pull` appends `/<dirname>/` to
`.gitignore`. Recipe vs code: workspace repo versions how to assemble; child repos version their
own history.

Complements (does not replace) domain-level `repos:` in `lore-repo.md` — `workspace-pull` unions
both at pull time. Solo devs can skip workspace git entirely (local-only mode).

First dogfood target: user's `agent-workspace` directory (not yet scaffolded).

## See Also

- `v25-workspace-pull-init-design.md`
- `workspace-vs-domain-vocabulary.md`
- `plugin-vs-agent-repo-separation.md`
