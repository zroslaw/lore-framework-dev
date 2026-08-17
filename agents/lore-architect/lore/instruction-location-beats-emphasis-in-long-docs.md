---
lore: 1
type: topic
summary: "Once a procedure doc is long enough that an executor pages it, an obligation's location decides whether it runs — three rewrites inside the doc changed nothing and relocation did; fractional step numbers are the same defect in miniature."
parent: lore-context.md
---

# Instruction Location Beats Emphasis in Long Docs

**Place an obligation where the reader demonstrably is.** Past a certain length an executor stops
reading a procedure doc whole and starts paging it, and everything after its last page might as well
not exist. No amount of emphasis reaches text that is never read.

## The instance (v41, 2026-08-17)

`summarize.md` is 492 lines. Across runs the agent read lines 1–100, 100–249, and 250–349, and
**never reached line 383**, where the obligation to add the usage block lived. It had the command
and it had the schema; it never got the line joining them.

Three successive rewrites *inside* that doc did not move execution. One later run read the exact
chunk containing the newly-added note and still made **zero** tool calls for it.

What worked was **relocation**: moving the obligation into the 96-line orchestrating `finalize.md`
Phase 3 — a doc short enough to be read whole — and stating it as that phase's **ordered opening
action** rather than as a description of what happens later.

Treat "doc long enough to be paged" as its own defect class. `summarize.md` is still over the line
and was filed to `framework-improvements-backlog.md` rather than solved in v41.

## The same defect in miniature: fractional step numbers

A step numbered fractionally (`3.5`) reads to an executing model as an **optional aside** and gets
skipped between the whole-numbered steps. `summarize.md` had exactly two fractional steps, and those
were exactly the two that failed the gate — one skipped entirely across two runs with zero tool
calls, the other mangled. Sub-numbering plus hedging language is a skip signal.

Renumbering the doc flat (1–14) made the step run. Again: three emphatic instructions to run it
changed nothing; the structural change did. **Check cross-references and test assertions before
renumbering** — step numbers are cited from other docs and asserted in the suite.

## The rule

When repeated prose emphasis fails to make a step execute, **stop adding words and look at the
step's structural position**: how far into the doc it sits, whether the doc is read whole, whether
its numbering marks it as optional, and whether it is phrased as an order or a description.

## See Also

- [the-terminal-step-is-the-step-that-gets-dropped.md](the-terminal-step-is-the-step-that-gets-dropped.md)
  — the sibling from the same battery: the terminal step's fix is an observable postcondition.
- [models-copy-what-they-should-compute.md](models-copy-what-they-should-compute.md) — third member
  of the same family of structural-not-exhortative doc fixes.
- [single-canonical-source-discipline.md](single-canonical-source-discipline.md) — relocating an
  obligation means *moving* it, not adding a second statement of it.
- [haiku-ambiguity-detector.md](haiku-ambiguity-detector.md),
  [execution-testing-catches-blind-ambiguity.md](execution-testing-catches-blind-ambiguity.md) — the
  cheap-tier execution gate that makes paging behavior observable at all.
- [versioning-release-types.md](versioning-release-types.md) — the v41 entry recording the fix and
  the still-open doc-length item.
