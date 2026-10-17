---
lore: 1
type: topic
summary: "Session scratch of todos and learnings, updated during work, handed to reflect and merge at finalize."
parent: lore-context.md
---

# Session running notes scratch

End-of-session reflect depends on what the model still remembers; mid-session friction, small todos,
and half-formed improvement ideas are easy to lose.

## Proposal

- **During execution:** keep a lightweight session scratch (open todos, blockers, ideas, bullets worth
  keeping) and append when something breaks or when an improvement idea appears.
- **At reflect:** each active agent reads the scratch through its role lens and drafts reflection
  topics from what belongs to that agent.
- **At merge:** integrate reflections as today; the scratch is input to reflect, not a substitute for
  lore topics.

## Relation to `/lr:note`

One-shot `/lr:note` micro-capture appends a single line into `reflections/` for merge. The scratch
is a **session-scoped buffer** with a defined handoff into reflect→merge, aimed at higher finalize
quality. See `workdir/what-to-improve.md` (C2 vs C2b) and `framework-improvements-backlog.md` §
Finalization / Autopush.

## Open design

- File location (`workdir/session-notes.md`, `.tmp/<session>/`, host-only vs per-agent copy).
- Which framework docs own the convention (`agent-boot.md`, `process-reflection.md`,
  `process-merge.md`).
- How multi-agent sessions partition one scratch vs several.

Status: **not shipped** — backlog and standing list only (user-raised 2026-10-17).
