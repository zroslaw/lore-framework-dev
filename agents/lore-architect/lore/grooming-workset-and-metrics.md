---
lore: 1
type: topic
summary: "Running /lr:groom repeatedly on an uncommitted tree: the default workset crowds in its own output, so commit between runs or scope slices; which metrics to snapshot and what they cannot see."
parent: lore-context.md
---

# Grooming Workset and Metrics

Lessons from the 2026-10-04 five-run `/lr:groom` exercise. The restructuring technique itself is in `lore-context-shape-discipline.md` (hub demotion) and `lore-topic-format.md` (lossless split).

## The default workset crowds itself in

`lore-workset` ranks every uncommitted file first ("recently_changed"), and grooming never commits. Across consecutive default runs the recent tier grew (5, 14, 32, 84 files) until it exceeded even a 90,000-token budget and the rotation tier, the only one that reaches unreviewed Lore, returned zero files. Consecutive runs then re-review their own output.

- Workarounds (state them openly in the record): raise `--budget` visibly (the doc forbids only *silent* increases) and pick slices by hand: smallest legacy files, unreviewed root topics, `--scope lore-context.md` partitions.
- Suggested framework fix (filed in the report): skip files whose SHA is already recorded in `workdir/lore-grooming-state.yaml`.
- Before a multi-run exercise, commit between runs (user-authorized) or plan scoped slices up front. Unmark from the cursor any file only skimmed, not read: `cursor.py` marks the whole workset reviewed.

## Metrics and their blind spot

Snapshot after each run (`workdir/grooming-exercise/measure.py`, report `report.md`): mapped files/% and mapped tokens %, legacy count, lore-context tokens, boot map tokens, boot footprint, root child count, area hub count, total lore tokens, validation issues (must stay 0).

Calibration (5 runs): mapped files 42.0% → 60.2%, legacy 178 → 125, boot footprint −19%. Converting ~15 small legacy topics costs about 14k tokens of reading and adds ~15 mapped files; roughly eight more such runs clear the remaining 125. Stale-fact repair (`workspace-status`, `doctor`, "nothing shipped yet") is invisible to every structural metric, so record it separately. Read-before-convert paid off: reading each legacy file in full surfaced a stale claim in about one file in three.
