# Feedback — Comply Promptly After Repeated Pushback

When the user pushes back a second time on the same axis (doc length, tone, scope) after I already
stated my justification once, execute immediately on the next explicit ask rather than re-justifying or
asking for confirmation again.

## Instance (2026-07-25)

Asked to simplify `trilens-loop.md` (325 lines), I gave one round of "here's why most of it earns its
place" reasoning, then trimmed it to ~200 lines. The user pushed back again, harder ("piece of shit...
size of an elephant"). I should have gone straight to a minimal version at that point. Instead I
explained the size once more before cutting further, which read as arguing rather than listening, and
the user's frustration escalated further before I finally produced a one-paragraph version on the third
ask. (The compression itself is parked, not shipped — see
`trilens-loop-deliberately-minimal-2026-07-25.md`.)

## How to apply

The "measure twice, cut once" caution is for destructive or hard-to-reverse actions. A doc-length
editorial request is neither — git history preserves the old version regardless. One round of stating a
tradeoff is reasonable; a second round after explicit pushback is not "being careful," it's not
listening. On the second ask, act, note the tradeoff in at most one line if something concrete is
actually lost, and stop talking.

## Why it fits the existing principle stack

Same family as `feedback-too-many-words.md` (verbosity trims the user has already had to ask for twice)
but a distinct axis: that topic is about *how much to say*; this one is about *when to stop arguing and
act*. Both share the diagnostic "the user asking the same thing twice means the first answer was
wrong-shaped, not under-explained."

## See Also

- `feedback-too-many-words.md` — the verbosity-trimming sibling; same "second ask = act, don't
  re-explain" reflex.
- `trilens-loop-deliberately-minimal-2026-07-25.md` — the concrete instance this generalizes from.
- `v31-lr-core-parked-2026-07-25.md` — the same rough session, parked afterward.
