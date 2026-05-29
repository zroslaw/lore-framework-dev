v11 split a long-conflated term into two distinct concepts. The split was load-bearing — it unlocked the `/lr:workspace-sync` feature design.

## Before v11

- "Domain" / "domain directory" / `<domain>` placeholder all meant *the parent directory containing agent repos*.
- "Lore Framework Domain" was the canonical CLAUDE.md section header in `/lr:init` output.
- Agent repos were called "agent repos" with no conceptual term for the *scope* they cover.

## After v11

- **Workspace** (filesystem) = parent directory. New `<workspace>` placeholder. The dir Claude is run from. Holds one or more agent repos and any sibling repos they declare via `repos:`.
- **Domain** (conceptual, prose only — no brackets) = the scope of a single agent repo. "Activities domain," "tax-advice domain," "lore-framework domain." `<domain>` placeholder retired.
- A **multi-domain workspace** is several agent repos coexisting side-by-side, each self-sufficient elsewhere but composed here for cross-domain collaboration.

## Why the split unlocked the feature

Without the split, "the domain has multiple agent repos that each declare their dependencies" was incoherent — the domain was *the* agent repo container. With the split, "agent repo (domain) declares siblings → workspace (filesystem) gathers them" is the natural framing. The feature falls out of the vocabulary cleanly.

## Disambiguation rules (used in the v11 sweep, ~13 framework docs)

- "domain dir" / "domain root" / "domain directory" → **workspace** (filesystem sense)
- "across domains" / "multi-agent domains" → **workspaces** or "across multiple agents' knowledge" depending on context
- "domain expertise" / "domain knowledge" / "domain facts" → unchanged (legitimate prose sense)
- `<domain>` placeholder → `<workspace>`
- The `/lr:init` canonical payload header was edited too — existing workspaces see show-diff-and-confirm on next `/lr:init`, the standard drift protocol.

## Operational rule

When extending the framework, prefer **workspace** for filesystem operations and **domain** only for prose discussion of scope. The reviewer caught a case where "across domains" without disambiguation became ambiguous (cross-workspace? cross-agent-repo?) — explicit "(different agent repos)" parenthetical is sometimes the right tool.

## See Also

- `terminology-domain-collision-trap.md` — the broader principle this is an instance of (newcomer-prose hygiene; "domain" loose-English vs LRF technical sense).
- `placeholder-vocabulary.md` — the placeholder catalog post-rename.
- `plugin-vs-agent-repo-separation.md` — the prior conceptual split this builds on (plugin-repo vs agent-repo).
- `workspace-sync-utility.md` — the feature whose design the vocabulary split unlocked.
