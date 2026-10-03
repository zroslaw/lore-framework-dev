---
lore: 1
type: topic
summary: "User directive: fewest concepts, data, code, and instructions while staying extensible — cut what the MVP does not exercise, defer it with a reintroduction trigger, and run the minimalism lens in every review round."
parent: lore-context.md
---

# Feedback — MVP minimalism: don't introduce what isn't needed now

User directive (2026-07-19, Lore Beings design review): keep an initial design and its draft **as simple as possible**, leaving all complexity for the future. If fields, attributes, or logic are not needed *now*, do not introduce or implement them — even when the generalized version is already designed and agreed.

**Why:** unused generality is pure carrying cost — more schema to document, parse, validate, and keep consistent, with zero exercised value until the triggering need arrives. The settled-design dialogue naturally produces the general shape (tiers, ladders, fallback chains); a deliberate second pass is needed to shrink it to the MVP subset.

**How to apply:**

- After a design settles, run an explicit **simplification pass** with the test: "does the MVP exercise this field/branch/file?" If not, cut it.
- Cut ≠ discard: move each cut to a deferred-seams section **with the concrete trigger that reintroduces it** ("when a second engine ships", "when a real being needs a second behavior"). Git history preserves the full design.
- Review deliverable is a **ranked shortlist of cuts** plus an explicit "what I deliberately did not cut" list (safety substrate stays), then apply on the user's go-ahead.
- Unenforceable limits are prime cut candidates — see `unenforceable-caps-are-prompt-theater.md`.

**Reaffirmed 2026-10-03 as the governing lens for framework features** — the fewest concepts, data,
code, and instructions while staying extensible; the user asked for minimalism to be one of the
reviewers and the main direction ([feedback-autonomous-design-cycle.md](feedback-autonomous-design-cycle.md)):

- Run the minimalism-and-extensibility lens in **every** review round, not once — rounds 2 and 3
  still found cuts after fixes added weight.
- Keep **honest concept accounting**: a redefinition of an existing term counts and is reported as
  such, never as "0 concepts".

First worked example: the Lore Beings MVP simplification pass (`lore-beings-design.md` § MVP simplification pass — tiers, `autonomy:`, per-session caps, `timezone:`, `lrb-*` skills all cut with named reintroduction triggers).

## See Also

- `feedback-schemas-as-enforcement-overreach.md` — don't add schema for enforcement; composes with this (both trim unexercised structure)
- `feedback-layered-decomposition-for-open-ended-asks.md` — the design-dialogue sibling: decompose and sequence the big ask; this topic governs what the settled design *ships first*
- `feedback-too-many-words.md`, `feedback-don-t-defer-completable-scope.md`, `feedback-confirm-before-writing-lore.md`, `feedback-draft-only-when-user-triggers.md` — the user-feedback working-style family
- `lore-beings-design.md` — the design the directive was issued on
- `unenforceable-caps-are-prompt-theater.md` — principle surfaced during the same pass
