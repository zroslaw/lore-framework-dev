# ULA Produces Two Output Kinds — Structured + Narrative

Realization that motivated the DF repo's `file-lore.md` aspect (2026-06-03; landing file named `file-lore.md` as of the 2026-06-07 naming lock — see `df-per-repo-backbone.md`).

A ULA unit pass yields **two distinct kinds of output**:

1. **Structured artifacts** — `bugs.yaml`, `scenarios.yaml`, `gap.yaml`. Schema-governed, machine-readable. Answer: *what* bugs, *what* tests, *what* gaps.
2. **Narrative file/unit context** — design intent, the "why", tribal knowledge, architectural chains spanning multiple bugs, severity calibration. Answers: *what does this unit actually do, why is it built this way, what must a fixer know first.*

The second kind **does not fit any of the three schemas** — it is not a bug entry, not a test scenario, not a coverage delta. Yet it is exactly what a developer needs before touching the code.

**Concrete demonstration** (single-unit pass on `run-task-as-admin`, see `ula-validated-turbo-boost-switcher.md`): the conversation surfaced a three-layer error-swallowing chain, a deprecation that makes the whole mechanism defunct on modern macOS, and a severity reordering (the alarming-sounding fd leak is near-zero impact for a menu-bar app; the quiet deprecation silently breaks the core feature). None of that lives in the YAMLs.

**Where it comes from:** the narrative emerges from the *interpretive conversation* around the pass, not from the A→B→C agent output. A fully automated pipeline would drop it; an interactive session is where it is richest.

**Resolution:** this is the "context" aspect, captured in the per-file `file-lore.md` in the DF repo. See `df-per-repo-backbone.md`. Related: `aiqa-ula-feature.md`, `ula-validated-turbo-boost-switcher.md`.
