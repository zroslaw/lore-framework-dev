---
lore: 1
type: topic
summary: "lore-context.md is every-session working knowledge and the entry to the lore graph, not an index — shape over size; and a fast-moving scalar has no business living in a slow-moving summary."
parent: lore-context.md
---

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

## A fast-moving scalar has no business in a slow-moving summary (2026-08-30)

The shape rule has a corollary about *which values* belong here at all.

Booting for framework work on 2026-08-30, I read "the current shipped-and-pushed version is **v41**"
from my loaded `lore-context.md` § Versioning while the framework repo was at **v43**, tagged
`lr--v1.43.0` at HEAD, clean and pushed. I caught it only because I ran `git log` before branching
and saw `fix(v43): apply findings from three independent reviews` at the tip. Had I trusted the
summary I would have created a `v42` branch, bumped `VERSION` to 42, and started rewriting a version
that already shipped — on top of two releases whose contents I did not know I was building on.

**Why this line in particular decays.** `lore-context.md` is compacted working knowledge, optimized
to change slowly. The current version number is the fastest-moving fact in it, and it updates only
when a finalization happens to rewrite that sentence. A ship finalized from a *different* agent's
session, or a merge that declines to touch the Versioning section, leaves it silently behind. The
document's virtue is its stability, which is exactly what disqualifies it as the home for a value
that changes every release.

> **Any fast-moving scalar living in a slow-moving summary is a stale read waiting to happen.**
> Prefer a pointer to where the value is authoritative ("read `VERSION`") over a copy of the value.

Worth applying to the other dated facts here at the next groom: corpus size, backlog counts, and most
of § Current State.

**The operational rule.** At the start of any framework-work session, establish the version from the
repo, never from lore:

```
cat VERSION
git log --oneline -5
git tag --list 'lr--v1.4*' | tail -3
git rev-list -n1 <latest-tag>   # confirm the tag is at HEAD
```

Treat the context's version line as *last known*, never as *current*.

**One unresolved detail, and it sharpens the lesson.** The committed `lore-context.md` had already
carried v43 since 2026-08-26 (commit `3368a0f`), so the v41 the session acted on did not come from
the file on disk as it then stood. Whatever the route — a boot before the pull landed, or a context
loaded from an earlier state — the conclusion widens rather than narrows: **a compacted summary can
be stale on disk or stale in a loaded context, and neither is distinguishable from the inside.** Only
the repo answers the question.

Same instinct, applied to SHAs: `release-commit-hash-from-tag.md`. Same reflex, generally:
`verify-before-acting-on-suspected-bugs.md`, `measurement-records-name-their-environment.md`.

## Relationships

- **Per-session sibling:** the merge maintains this shape incrementally at every finalization (`process-merge.md` § Step 4).
- **Periodic consolidation sibling:** the **lore housekeeping / consolidation "sleep" pass** (parked — `framework-improvements-backlog.md`) is the deep restructuring that strengthens hubs, consolidates over-granular topics, and removes stale ones — the *active* form of the "naming has no garbage-collector" gap (`naming-foundational-principles.md`).
- First applied as a manual groom of the lore-architect's own `lore-context.md` the day it shipped (~6.4K → ~1.4K words).

See `process-merge.md` § Step 4, `conventions.md` § Lore Context, `naming-foundational-principles.md`, `framework-improvements-backlog.md`, `lore-search-pattern.md`.
