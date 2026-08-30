---
lore: 1
type: topic
summary: "Renumbering a Step N heading breaks every doc citing that number silently, and the stale reference still reads plausibly; grep for citations first, cite sections by name, and never number a heading that runs before the numbered steps."
parent: lore-context.md
---

# A cross-reference by step number survives a rename and points at the wrong thing

Renaming or renumbering a `### Step N` heading breaks every doc that cites "Step N" — with no error,
no broken link, and a stale reference that still reads perfectly plausibly. This is the worst class
of doc cross-reference: it fails silently **and** looks correct.

Hit 2026-08-30 while inserting `## Step 0 — Announce` into `agent-boot.md`, which already had a
`## Step 0 — Framework root`
([skill-announcement-convention.md](skill-announcement-convention.md)).

## Measure before choosing the fix

The user asked the obvious question — why not just shift every step by one? Rather than argue from
instinct I grepped, and the answer decided itself:

- **Renumber:** ~30 edits across 10 files. Sixteen external references to `agent-boot.md` Steps 1–3
  live in `conventions.md`, `auto-pull.md`, `spawn-teammate.md`, `check.md`, `version-check.md`,
  `teammate-conventions.md`, and all three engine profiles. One is in `migrations/33.md`, a shipped
  historical migration that must not be rewritten. And `agent-boot.md`'s manual-boot section exists
  *specifically* to stop readers confusing two step numberings — renumbering means rewriting the
  paragraph whose whole job is preventing step-number confusion.
- **Rename instead:** 2 edits. Nothing external cited Step 0 — every external citation was Step 1, 2,
  or 3. `## Step 0 — Framework root` became `## Framework root`, shedding a number its own text said
  it was only borrowing ("before the numbered steps").

Actual cost came to 6, not 2: the grep also caught **all three engine profiles** citing boot's
"Step 0" for framework-root self-location. I would have broken every one of them silently. They now
name the section (`agent-boot.md` § Framework root) instead of a number — the sibling-profile audit
`docs-engines-convention.md` calls for, arriving through a different door.

## Standing rules

1. **Before renaming or renumbering any procedure heading, grep the whole repo for citations of that
   number** — sibling docs, engine profiles, and migrations. The migrations are the ones you must
   find and must *not* edit.
2. **Prefer citing a section by name over by number.** A name survives renumbering; a number does
   not, and its failure is invisible.
3. **A heading that says it runs "before the numbered steps" should not carry a number.** Two other
   docs had the same borrowed-number shape with zero references, so renaming them was free:
   `workspace-init.md`'s `### Step 0 — Context` → `### Context`, and `process-merge.md`'s
   `### Step 0: Refresh the Repo` → `### Refresh the Repo`.

## See Also

- `consistency-sweep-read-not-just-grep.md` — the complement: grep verifies tokens, only reading
  verifies facts. Here grep is the *cheap* half and it is what made the decision.
- `single-canonical-source-discipline.md` — a step number cited elsewhere is a second statement of
  the doc's structure, with the same drift surface and no check watching it.
- `instruction-location-beats-emphasis-in-long-docs.md` — why the Step 0 slot was worth contesting in
  the first place.
