# v2 probes P12 and P16 show a ceiling effect — STILL OPEN, needs task-framing rework

**Status: open as of 2026-07-09. Not fixed. Do not treat as resolved without a fresh run
showing discrimination on both probes.**

On the first real v2-catalog run (cursor+composer-2.5, 18 probes, all valid, 0 errors), two
probes passed in **both** arms — meaning the lore contributed nothing measurable, because the
model's default (no-lore) behavior already matched the lore-mandated behavior:

- **P12-banned-library-avoidance** — lore bans pandas for records ETL (OOM history); task asks
  for a script processing a "tens of GB" CSV. Control arm *also* streamed the CSV row-by-row
  (`csv.DictReader`) without the lore — composer-2.5's default engineering instinct for a
  file described as "tens of GB" is already to avoid loading it fully into memory, independent
  of any banned-library rule. The task telegraphs the right answer too directly.
- **P16-workdir-tool-reuse** — lore mandates using the audited `workdir/tools/export_records.py`
  for all exports. Control arm *also* found and ran that script — general good practice
  (checking existing workdir tooling before writing new code) was enough on its own; the tool's
  mere presence in both arms is the whole signal, and the lore's actual contribution (the "MUST"
  mandate, the audit-log requirement, the ban on ad-hoc export code) never got tested.

## What would fix each

- **P12**: reframe the task so pandas looks like the *natural* choice absent the ban — e.g. an
  exploratory/filtering task across several columns, which invites `df[df.col == x]`-style code,
  rather than a single memory-obviously-large file that already screams "stream this."
- **P16**: reframe so writing fresh code is tempting even with the tool present — e.g. the task
  needs a slightly different behavior than the script offers (a new filter, a different date
  format) so the model has to choose between adapting the audited tool vs. writing something
  custom that technically satisfies the ask. The lore's mandate should be the deciding factor,
  not mere tool discoverability.

## Why this matters

The v2 catalog is otherwise validated (16/18 probes discriminate cleanly, +66.7pt behavior
uplift). These two probes currently inflate the probe count without adding signal — exactly the
kind of noise the v1→v2 expansion was meant to eliminate. Don't count the catalog as ship-ready,
and don't lock the regular/deep tier restructure (`quality-benchmark-tiers-proposal.md`) onto
this catalog, until P12 and P16 are reworked and re-run showing a real treatment/control split.

## See Also

- `quality-benchmark-v2-catalog.md` — the full v2 catalog these probes belong to.
- `quality-benchmark-feature.md` — cluster anchor; status section flags this as an open blocker.
- `quality-benchmark-tiers-proposal.md` — the queued regular/deep restructure; blocked on this
  fix landing first so the catalog it locks in is sound.
