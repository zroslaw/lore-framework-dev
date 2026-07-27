# `docs/trilens-loop.md` — Don't Auto-Restore What Was Cut (2026-07-25)

`docs/trilens-loop.md` was cut from 325 lines to a single paragraph on 2026-07-25, on explicit, repeated
user instruction ("simplify," then "still a piece of shit... should be one small paragraph, nothing
else"). This was not a routine edit: it followed two rounds of escalating pushback after I initially
defended the length as mostly earned (engine-specific traps, several incident-derived hardening rules —
silent-round handling, the ledger, the native-subagent requirement).

**The rule below is what this topic is for, and it still stands. The one-paragraph shape does not.**
On 2026-07-26/27 the user directed a step-by-step rewrite into a ~75-line structured doc — see
`trilens-loop-v31-restructured.md` for the current shape. That is not a counterexample to the rule:
every expansion was user-directed, none was a "helpful restore."

**Neither shape is shipped** — both live on `wip/lr-core-v31`, not on main; see
`v31-lr-core-parked-2026-07-25.md` for the branch/worktree location. Main's `docs/trilens-loop.md` is
still the full 325-line version described in `trilens-loop-feature.md`.

## How to apply

Do not treat the terse version — if/when it lands — as an oversight to "helpfully" restore. If a future
review or lifecycle-suite failure surfaces real ambiguity from the cut (e.g. a weak-model executor
mishandling the ledger continuity or the silent-round distinction), that's a new, separate,
user-approved decision to re-expand specific parts — not a default reversion to the old shape. Old
content is recoverable from git history if genuinely needed; that is not license to put it back unasked.

**The rule worked end-to-end, and it is worth knowing what "worked" looked like.** The 2026-07-26
round-1 review found real ambiguity from the cut: two cold lenses independently noticed that
`docs/engines/cursor.md`'s `subagent-spawn` binding still named `trilens-loop.md` as the carve-out
for "subagent independence is the semantics," while the compressed doc no longer stated any
engine-binding instruction or the "no subagent mechanism → stop" rule. Per this topic's rule that was
**surfaced and left as an open, undecided deferral**, not auto-fixed. It stayed open across a session
boundary until the user separately chose to restructure the doc, at which point the clause was
re-added deliberately (`trilens-loop-v31-restructured.md`) — the "new, separate, user-approved
decision" this topic asks for, arriving on its own schedule rather than being pre-empted.

Watch the near-miss on the way there, recorded in
`check-own-lore-before-dismissing-a-finding.md`: mid-session I nearly declared the deferral moot from
a misremembered rule. Holding a finding open is the rule's easy half; not *dissolving* it is the hard
half.

This is the concrete instance behind `feedback-comply-promptly-after-repeated-pushback.md` — the
pushback that produced this compression is the same episode that lesson generalizes from.

## See Also

- `v31-lr-core-parked-2026-07-25.md` — where this change currently lives.
- `trilens-loop-v31-restructured.md` — the user-directed restructure that supersedes the
  one-paragraph shape while leaving this rule intact.
- `check-own-lore-before-dismissing-a-finding.md` — the near-miss on dissolving the deferral instead
  of deciding it.
- `feedback-comply-promptly-after-repeated-pushback.md` — the generalized working-style lesson from this
  episode.
- `trilens-loop-feature.md` — the feature topic describing main's current (full-length) doc.
