# Lore-Context Shape Discipline

`lore-context.md` is an agent's **every-session working knowledge and the entry point to the lore graph — not an index of all topics**. Shape, not size, is the governing constraint. Landed in the framework at v17; the canonical rule lives in `process-merge.md` § Step 4 + `conventions.md` § Lore Context, this topic carries the rationale.

## The drift it prevents

The merge process used to resist `lore-context.md` growth only with a **size ceiling** (≤50K, "summarize older entries"). A size gate with no shape rule lets the file grow comprehensive: it accretes (a) a flat enumeration of every topic — a de-facto index — and (b) per-version "vN did X" narrative history. Both are bloat: the catalog duplicates what `ls lore/` already gives; the history duplicates git / release-notes / the topic's own content. The file becomes large, hard to read, and costly at every boot (boot loads exactly this file).

## The shape

- **Compacted, present-tense working knowledge** the agent uses across most sessions.
- **References to the most important / summary topics — not enumerations of detail topics.** Point at a theme's summary topic; let *it* fan out. If a significant theme has no summary topic, create one (strengthen the graph's mid-tier) rather than inlining the cluster.
- **No version-history narrative** — present tense; "vN did X" belongs elsewhere.

## Why it's safe to strip the index

Topic discovery does **not** depend on `lore-context.md` listing topics. The real discovery mechanism is the on-demand `lore/` directory scan (`agent-boot.md` § Searching Your Lore, `lore-search-pattern.md`). Dropping the enumeration orphans nothing — every topic stays on disk and stays scan-discoverable. The discipline still asks: when you remove something from `lore-context.md`, keep it reachable from a summary topic the context references (preserve graph navigability from the entry point) — but exhaustive link coverage is the directory scan's job, not the context's.

## Relationships

- **Per-session sibling:** the merge maintains this shape incrementally at every finalization (`process-merge.md` § Step 4).
- **Periodic consolidation sibling:** the **lore housekeeping / consolidation "sleep" pass** (parked — `framework-improvements-backlog.md`) is the deep restructuring that strengthens hubs, consolidates over-granular topics, and removes stale ones — the *active* form of the "naming has no garbage-collector" gap (`naming-foundational-principles.md`).
- First applied as a manual groom of the lore-architect's own `lore-context.md` the day it shipped (~6.4K → ~1.4K words).

See `process-merge.md` § Step 4, `conventions.md` § Lore Context, `naming-foundational-principles.md`, `framework-improvements-backlog.md`, `lore-search-pattern.md`.
