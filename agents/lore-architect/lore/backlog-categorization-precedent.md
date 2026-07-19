# Backlog Restructured Into Top-Level Categories (2026-07-19)

`framework-improvements-backlog.md` had grown into ~30 flat `##` sections after 25+ versions of accretion — the user flagged it as hard to navigate/perceive. Restructured into a two-level hierarchy: top-level `##` **categories** (Major Directions, Session Lifecycle & Durability, Knowledge Quality & Curation, Multi-Agent Collaboration, Workspace & Environment, Framework Upkeep/Distribution/Docs, Ship Closures archive), each holding the prior topical sections demoted to `###`. All item content preserved verbatim — pure reorganization, no deletions, no rewording of existing bullets.

## Operational lesson

When a flat list-shaped lore document (backlog, index, catalog) exceeds roughly 15–20 top-level sections and a user or reviewer flags it as hard to scan, the fix is a **category pass**, not a rewrite: group existing sections under a small number of stable top-level headings by *what kind of concern* they are (direction vs. lifecycle vs. quality vs. collaboration vs. environment vs. upkeep), keep every item's wording untouched, and add a one-line note documenting the new structure so future contributors file new items under the right category from the start.

This is the flat-list analogue of the "sleep pass" consolidation job (`framework-improvements-backlog.md` § Knowledge Quality & Curation § Lore Housekeeping / Consolidation Job) — a periodic *structural* reorganization distinct from incremental additions, done on request rather than on a schedule (no automated trigger exists for the backlog specifically, unlike the sleep-pass design for per-agent `lore/`).

## How to apply

If `framework-improvements-backlog.md`'s categories themselves start feeling stale or mis-sized (e.g. "Major Directions" swallowing too much, or a category with only one item), that's the signal for another category pass — don't let categories silently drift out of shape the same way the flat list did.

## See Also

- `framework-improvements-backlog.md` — the document itself, now carrying a "Structure (since 2026-07-19)" note at its top
- `naming-foundational-principles.md` § "Name every principle has no garbage-collector" (the phrase lives in `framework-improvements-backlog.md` § Architecture-Review Follow-Ups, referenced there by proxy) — the sibling problem for lore *topics* rather than backlog *sections*; both are accretion-without-subtraction failure modes
- `lore-context-shape-discipline.md` — the same no-garbage-collector gap, applied to `lore-context.md` shape rather than backlog structure
