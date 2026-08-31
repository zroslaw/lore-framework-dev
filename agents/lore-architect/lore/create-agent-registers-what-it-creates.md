---
lore: 1
type: topic
summary: "v44 draft: /lr:create-agent registers the agent it creates rather than offering to, because an unregistered agent is invisible to everyone else and lands in workspace-status finding S11; being.md still opts out."
parent: lore-context.md
---

# Create-Agent Registers What It Creates (v44 draft)

`/lr:create-agent` used to stop after scaffolding `role.md`, `lore-context.md`, `lore/` and
`workdir/`, and merely *offer* `/lr:register-agent`. But registration is the sole membership
authority for the workspace memory file's `## Agents` section, so an agent created and not
registered was bootable by name and **invisible to everyone else** — and landed straight into
`workspace-status` finding **S11**. The framework's own skill produced the state its own diagnostic
reports.

## What changed (drafted in v44, unshipped)

- `docs/create-agent.md` **step 8** runs the Register Agent procedure in `docs/register-repo.md`.
- **Step 9** reports and names `/lr:workspace-push`, because the shortcut and the memory-file edit
  land uncommitted in the **workspace** repo, not the agent repo — a different repo than the one the
  user just watched get scaffolded.
- **Step 1** gained a zero-repo branch that offers `/lr:create-repo` instead of scaffolding an agent
  directory no discovery could find — the case a reader following the README's opening example hits.

This is [the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md)
in its structural form: the step that *publishes* an outcome had been split from the step that
*produces* it, so the artifact routinely shipped unpublished. The fix is to put publication inside
the producing procedure, not to document it harder.

## Open: who decides registration for a Being

`docs/being.md` deliberately keeps its opt-out — "do not register a shortcut unless the user asks."
The user declined twice to change the being path, so that stays. But the coupling now rests on a
**cross-doc inference**: `create-agent.md` step 8 defers to callers, and `being.md` step 3 is the
caller declining. That is exactly the seam where obligations get dropped.

Worse, the two callers disagree about *who decides*: step 8 forbids asking, `being.md` says "unless
the user asks." Unresolved; carried in the backlog and `workdir/what-to-improve.md`.

## See Also

- [the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md)
  — the shape, and why more emphatic prose is not the fix.
- [committed-artifacts-carry-relative-paths.md](committed-artifacts-carry-relative-paths.md) — the
  other half of the v44 registration work, and the earlier S11 false report.
- [registered-shortcuts-are-framework-owned.md](registered-shortcuts-are-framework-owned.md) — what
  registration generates and the recognition boundary it must respect.
- [skill-announcement-convention.md](skill-announcement-convention.md) — the v44 worktree this is
  drafted in, and its gate record.
- [lore-beings-design.md](lore-beings-design.md) — the being path that opts out.
