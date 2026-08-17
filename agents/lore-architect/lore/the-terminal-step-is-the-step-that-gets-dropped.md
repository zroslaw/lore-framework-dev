---
lore: 1
type: topic
summary: "The terminal step of a procedure — the one that publishes or confirms the outcome — is the step that gets silently dropped; the fix is an observable postcondition sited where the artifact is assembled, not more emphatic prose."
parent: lore-context.md
---

# The Terminal Step Is the Step That Gets Dropped

**In an executable procedure, the step most likely to be skipped is the last one — the step that
publishes or confirms the outcome.** Every step that *produces* something has its own evidence; the
step that *announces* it has none, so nothing detects its absence.

## The instance (v41, running v40's deferred gates, 2026-08-17)

Four apparently independent fidelity failures turned out to be one defect wearing four hats:

1. `version-check.md`'s boot-upgrade **publish step** plus its outcome line — the stamp was written
   and committed, never pushed, and no line said so.
2. `summarize.md`'s **usage-block attempt** and its mandated warning on failure.
3. The exact mandated **Learning sentence** in the summary.
4. `style.md`'s **confirmation line** — the skill's only observable result.

In every case the actual work was done correctly. Only the terminal step was skipped. The publish
miss reproduced on **both** engines; the summarize misses were Claude-side, the style miss
Codex-side — so this is a property of the procedure shape, not one model's quirk.

Two of the four sit in prose whose **"best-effort" / "non-blocking"** framing makes skipping feel
sanctioned. Wording that licenses a step to fail reads to an executor as wording that licenses the
step not to happen.

## More emphatic prose is not the fix

This is settled by evidence, not preference. The summarize usage step **already carried an explicit
"models get this wrong" callout**, and a run still never invoked the command at all — zero tool
calls. Three further escalating instructions (in the orchestrating doc, in the step intro, and a new
pre-write check) changed nothing.

**The fix is an observable postcondition, sited where the output is produced.** v41 deliberately did
not rewrite the procedures' arguments; it gave each terminal step a checkable result:

- `version-check.md` Step 4 gained a two-part completion check, with a **mandatory** Step 5 outcome
  line naming the disposition.
- `style.md` names its confirmation as the skill's only observable result and pins the exact line
  per component count.

Omission becomes *detectable* rather than merely discouraged. The design question to ask before
touching wording is: **where can a check live at the moment the artifact is assembled?**

## Corollary — a postcondition for a multi-part obligation must cover every part

The completion check written to catch "job half done" itself shipped a job half done. It observed
only working-tree cleanliness, which a **committed-but-unpushed** repo passes — exactly the state it
existed to catch. It now also requires the branch not to be ahead of upstream, or a stated push
reason.

When writing a gate for a multi-part obligation, enumerate each part and confirm the check observes
evidence of *each*. The failure being fixed recurs one level up, inside the fix — a
`a-fix-is-a-change-and-changes-need-review.md` instance with an unusually short radius.

## See Also

- [instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)
  — the sibling structural fix from the same battery: when emphasis fails, move the obligation to
  where the reader demonstrably is.
- [models-copy-what-they-should-compute.md](models-copy-what-they-should-compute.md) — the third
  structural-not-exhortative rule from the same battery.
- [a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md) — two
  of v41's own fixes were defective and caught only by the next gate round.
- [point-of-use-guardrails-beat-recorded-lore.md](point-of-use-guardrails-beat-recorded-lore.md) —
  the same reflex one layer out: a rule recorded as knowledge protects nobody; name its point-of-use
  site.
- [execution-testing-catches-blind-ambiguity.md](execution-testing-catches-blind-ambiguity.md) —
  none of these four were visible to prose review; only running the docs found them.
- [versioning-release-types.md](versioning-release-types.md) — the v41 entry, where the fixes and
  their gate record live.
- [naming-foundational-principles.md](naming-foundational-principles.md) — the meta-rule under which
  this shape was promoted to its own topic.
