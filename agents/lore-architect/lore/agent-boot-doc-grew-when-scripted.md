# `agent-boot.md` Doubled in the Release That Scripted It

Measured 2026-07-28, prompted by the user asking why boot is so big when it should be "run this,
and if it fails read it and follow it."

| | Boot steps | Operating guide | Total |
|---|---|---|---|
| v30 (`main`) | 51 lines | 52 lines | 103 |
| v31 branch | 108 lines | 52 lines | 160 |

**The boot procedure doubled in the release whose purpose was to move it into a script.**
`auto-pull.md` went the other way (100 → 80 lines), so the v31 literate-accelerator thesis holds
there and fails here.

Word breakdown of the v31 file (2,266 words total):

| Section | Lines | Words |
|---|---|---|
| Step 0 — framework root & engine profile | 25 | 371 |
| Steps 1–4 — the actual boot | 47 | 888 |
| Pull freshness | 6 | 113 |
| Manual Boot Procedure (fallback) | 30 | 325 |
| Your Lore / Workdir / Collaborating / Finalization | 52 | 569 |

## Three causes, only one legitimate

1. **A quarter of the file is not boot.** The operating-manual sections are the agent's standing
   instructions; they live here only because boot is *when* they are read. Predates v31. Splitting
   them out is pure filing, zero behavior change.
2. **Step 2 documents the JSON contract field by field — and need not.** `read_next` already solves
   this pattern for `role.md`/`lore-context.md`, and Step 3 is correspondingly two lines. Step 2
   instead hand-writes prose routing for every other field (skew verdict → `version-check.md`;
   teammate `yes` → `teammate-conventions.md`), all of which the script already computed. Emitting
   those paths in `read_next` collapses Step 2 into Step 3. Caveat: `unknown` deliberately routes
   nowhere, so it stays a judgment case — but that is ~5 rules, not 888 words.
3. **The rest is scar tissue and is load-bearing.** The Claude-Code false-negative paragraph, the
   teammate-RULES emphasis, the 180-second timeout note — each was added because something broke,
   most found by the lifecycle harness. Deleting a clause a scenario pins is how a silent
   regression returns (`haiku-ambiguity-detector.md`).

This is `framework-improvements-backlog.md`'s **"no subtraction force"** risk showing up in the
single most-read doc in the framework — every boot on every engine pays ~3K tokens for it.

## Disposition: v32, not v31

**Explicitly not a v31 ship item.** Reopening the most-read procedure doc while v31 is four commits
from shipping moves the ship further out. Filed on `workdir/what-to-improve.md` as a v32-tier item
(A8) per `standing-improvement-list-practice.md`.

## See Also

- `standing-improvement-list-practice.md` — where this is queued and how the tiering works.
- `literate-accelerator-pattern.md` — the v31 thesis this measurement partly contradicts.
- `lore-context-shape-discipline.md` — the sibling shape-over-size discipline for lore, same
  underlying "no subtraction force" problem.
- `haiku-ambiguity-detector.md` — why the scar-tissue clauses cannot simply be trimmed.
- `v31-lr-core-parked-2026-07-25.md` — the ship this was deliberately kept out of.
