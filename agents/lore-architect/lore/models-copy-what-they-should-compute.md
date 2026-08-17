---
lore: 1
type: topic
summary: "In executable prose, anything the model can copy instead of compute will be copied: examples get printed verbatim and machine-resolved paths get retyped and silently corrected. Remove the copyable artifact rather than warning against it."
parent: lore-context.md
---

# Models Copy What They Should Compute

**If a doc hands the executor a value that looks like the answer, it will be used as the answer** —
even when the doc says to compute one. The fix is structural: take the copyable artifact away, don't
exhort against copying it.

## Form 1 — a concrete example gets printed verbatim (v41)

`style.md` gained a table listing concrete component names per count. That gave the model a
copyable two-component example. On a run where a *different* pair was actually selected, the agent
printed the example verbatim: `Style set: plain and dialogue.` for a dialogue+follow selection.

This was a **self-inflicted regression** introduced by v41's own fix and caught only because the
lifecycle gate re-ran after the fix (`a-fix-is-a-change-and-changes-need-review.md`).

Repair: replace copyable concrete pairs with a **pattern plus a punctuation rule**, and say
explicitly not to take names from the document. An example the model must adapt is safe; an example
it can emit unchanged is a trap whenever emitting it is cheaper than computing.

## Form 2 — a machine-resolved identifier gets retyped and "corrected" (v41)

`summarize.md`'s usage step ran a resolver that returned the correct log path, then had the model
retype that path into a follow-up call. The model silently changed hyphens back to underscores.

The mechanism is worth remembering: **Claude Code encodes project directories by rewriting `_` to
`-`**, so the correct resolved path *looks* like a typo of the temp directory the agent has been
staring at all session. The model fixes what isn't broken.

Repair, again structural rather than exhortative: make the two commands **one shell pipeline**
passing the path through a variable, and document the path as **opaque**.

## The general rule

Any doc step where a machine emits an identifier that must feed the next command should **pipe it,
never re-transcribe it**. And any doc that must show a shape should show a shape, not a fillable
instance.

Both forms are invisible to prose review — a strong reader substitutes correctly and never notices
the affordance — and both surfaced only under the cheap-tier lifecycle gate.

## See Also

- [the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md),
  [instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)
  — the other two structural-not-exhortative doc rules from the same v41 battery.
- [a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md) — the
  copy-the-example defect was introduced by a fix and caught by the next gate round.
- [execution-testing-catches-blind-ambiguity.md](execution-testing-catches-blind-ambiguity.md),
  [haiku-ambiguity-detector.md](haiku-ambiguity-detector.md) — why only execution finds this class.
- [claude-engine-capabilities.md](claude-engine-capabilities.md) — the `_`→`-` project-directory
  encoding behind Form 2.
- [macos-var-symlink-realpath-ambiguity.md](macos-var-symlink-realpath-ambiguity.md) — sibling: prose
  that a model must "resolve" is prose a model will resolve wrongly; name the exact command instead.
