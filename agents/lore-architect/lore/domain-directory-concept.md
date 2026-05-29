**Vocabulary note (v11+):** what was called the "domain directory" pre-v11 is now the **workspace** — the top-level working directory Claude is launched from. "Domain" is now the conceptual scope of a single agent repo (Activities domain, tax-advice domain, etc.). This topic preserves the historical concept under its old name; the canonical filesystem term is workspace. See `workspace-vs-domain-vocabulary.md`.

The workspace is the top-level working directory containing agent repos and any other repositories or data relevant to the work being done.

**Structure:**
```
<workspace>/
├── agent-repo-1/            # Agent repos (one or more)
├── agent-repo-2/
├── other-repos/             # Any other workspace content (often declared via repos: in lore-repo.md)
└── .claude/commands/        # Optional registered agent boot commands
```

**Key properties:**
- The user always runs Claude from the workspace root.
- Agents have visibility across the entire workspace — all sibling repos.
- `lore-framework/` is installed as a plugin; doesn't need to be a sibling.
- Multiple agent repos can coexist (multi-domain workspace).
- Sibling repo layout chosen over git submodules for simplicity.
- v11+: agent repos can declare workspace siblings via `repos:` in `lore-repo.md`; `/lr:workspace-sync` clones missing ones and pulls all top-level repos.

**Plugin vs old setup:**
Previously `lore-framework/` lived in the workspace as a sibling repo and commands were copied to `.claude/commands/` during setup. Now the plugin is installed via the marketplace and no setup step is needed.

## See Also

- `workspace-vs-domain-vocabulary.md` — the v11 vocabulary split and disambiguation rules.
- `workspace-sync-utility.md` — the workspace-level git orchestration skill.
- `agent-discovery-nesting-constraint.md` — agent repos must sit at the workspace root to be discoverable.
