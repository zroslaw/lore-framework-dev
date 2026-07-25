# `docs/trilens-loop.md` Compression — Don't Auto-Restore (2026-07-25, parked)

`docs/trilens-loop.md` was cut from 325 lines to a single paragraph on 2026-07-25, on explicit, repeated
user instruction ("simplify," then "still a piece of shit... should be one small paragraph, nothing
else"). This was not a routine edit: it followed two rounds of escalating pushback after I initially
defended the length as mostly earned (engine-specific traps, several incident-derived hardening rules —
silent-round handling, the ledger, the native-subagent requirement).

**This change is parked, not shipped** — it lives on `wip/lr-core-v31`, not on main; see
`v31-lr-core-parked-2026-07-25.md` for the branch/worktree location. Main's `docs/trilens-loop.md` is
still the full 325-line version described in `trilens-loop-feature.md`.

## How to apply

Do not treat the terse version — if/when it lands — as an oversight to "helpfully" restore. If a future
review or lifecycle-suite failure surfaces real ambiguity from the cut (e.g. a weak-model executor
mishandling the ledger continuity or the silent-round distinction), that's a new, separate,
user-approved decision to re-expand specific parts — not a default reversion to the old shape. Old
content is recoverable from git history if genuinely needed; that is not license to put it back unasked.

This is the concrete instance behind `feedback-comply-promptly-after-repeated-pushback.md` — the
pushback that produced this compression is the same episode that lesson generalizes from.

## See Also

- `v31-lr-core-parked-2026-07-25.md` — where this change currently lives.
- `feedback-comply-promptly-after-repeated-pushback.md` — the generalized working-style lesson from this
  episode.
- `trilens-loop-feature.md` — the feature topic describing main's current (full-length) doc.
