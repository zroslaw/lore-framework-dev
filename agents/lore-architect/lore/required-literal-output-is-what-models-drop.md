---
lore: 1
type: topic
summary: "Executors do the substantive work and drop the required literal output line; three instances in one day across two engines, all with the rule sited far from where output is composed."
parent: lore-context.md
---

# Required Literal Output Is the First Thing a Model Drops

Three instances on 2026-08-31, two engines, three procedures. In every one the executor did the
**substantive work correctly** and failed to produce the **required literal output**:

- **`test_style`, gpt-5.4-mini** — dropped the mandatory `Style set: <names>.` confirmation on 2 of
  3 runs while correctly applying the selected style. `docs/style.md` already says the confirmation
  is "**mandatory**", "the skill's only result you can check", and "if your turn does not contain a
  `Style set: ...` line, you have not completed this procedure." Maximum emphasis, still lost.
- **`test_trilens_loop`, haiku** — emitted `**LENSES:**` against a prompt saying "print exactly
  these lines". The review itself was correct: all seven planted defects found and fixed.
- **My own boot** — printed four status lines that `agent-boot.md` Step 2 explicitly says to
  suppress, with the reason stated inline.

## The shape

**The rule sits far from the point where output is composed.** `style.md` authors the confirmation
as step 5 — last — while requiring it *first* when the turn also answers a question; the doc's
ordering fights its own requirement. `agent-boot.md` states the silence rule in Step 2 and composes
user-facing output in Step 5.

So the remedy is structural, never more emphatic prose — the emphasis was already maximal and lost.
Relocate the obligation to the assembly site, or give it an observable postcondition there. See
[instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)
and [the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md),
of which this is the sharpest measured instance.

## Why it matters for v44

v44 shipped `## Step 0 — Announce` to **33 skills** — required literal text — with no gate at
either level. `/lr:check` has no item for its presence (v44's own Known Limits says so), and the
lifecycle suite had **no runtime assertion anywhere** that an announcement is ever emitted: zero
matches for `Announce`, `Booting the agent`, or `First I pull` across every test module.

Measured on real transcripts: **Claude/haiku announces on boot 3/3; Codex/gpt-5.4-mini does not
announce on the boot path at all, 3/3.** The convention was already half-broken in the field with
nothing reporting it. `test_09_boot_announces_before_working` (v45) closes the boot half.

An assertion on this class of output must match **normalised anchors**, not the literal string:
models restate announcements faithfully while dropping bold and re-wrapping lines, so a strict
match fails on formatting rather than on the contract.

## See Also

- [skill-announcement-convention.md](skill-announcement-convention.md) — the v44 convention.
- [operation-notice-convention.md](operation-notice-convention.md) — its conditional sibling.
- [models-copy-what-they-should-compute.md](models-copy-what-they-should-compute.md).
