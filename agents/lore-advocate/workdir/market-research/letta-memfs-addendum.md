# Letta MemFS — Addendum to the Landscape Study (2026-09-12)

Read from `docs.letta.com/letta-code/memfs` on 2026-09-12, after the landscape study was written.
Sharpens the axis-1 and axis-2 comparison in
[multi-agent-specialist-landscape.md](multi-agent-specialist-landscape.md) §1; it corrects nothing
there, it adds structural detail.

## Memory layout — three tiers

- `system/` — loaded into the agent's system prompt **every turn**: identity and critical rules.
- `reference/` — kept out of context until needed.
- `skills/` — agent-owned procedures, versioned with its memory.

## `persona.md` and `human.md`

Both live in `system/`. `persona.md` is the agent's identity; their own example reads *"I am a Letta
agent. I remember durable preferences and improve with use."* `human.md` holds the user's preferences
and project context. A developer writes them at setup; the agent may then edit them as it learns.

**The point for us:** `persona.md` is a personality and a voice, not a job description. There is no
declared domain, so nothing bounds what the agent considers worth saving. This is the concrete
evidence behind the role-as-relevance-boundary claim.

## Their "subagents" are memory maintenance, not specialists

Built-ins are `general-purpose`, `recall`, `history-analyzer`, plus two memory workers — **dreaming**
and **memory doctor** — which run in git worktrees so they can rewrite memory concurrently while the
user works. Letta's subagents are staff for the memory system; ours are named professionals with
domains. The word is shared, the concept is not; do not let a comparison table imply equivalence.

## Update mechanism — three triggers

1. The agent calls a memory-editing tool mid-work; every edit auto-commits.
2. The sleeptime / "dreaming" process fires on a step interval (default ~5) and rewrites memory
   unattended.
3. `/remember` — explicit, but the exception.

Default is continuous and unattended. Ours is whole-session and role-scoped: same substrate, opposite
control model. That is the contrast to draw — not manual vs. automatic.
