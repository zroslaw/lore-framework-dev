---
lore: 1
type: topic
summary: "An empty grep proves the searched pattern absent, never the capability absent — before asserting an absence as load-bearing evidence, read the entry point instead of resting on a pattern search."
parent: lore-context.md
---

# A Negative Grep Proves the Pattern Absent, Not the Capability

**The instance (2026-08-23).** I wrote into a design doc that `scripts/workspace-pull` "accepts no
arguments — there is no argv handling in the script at all", and used it as load-bearing evidence for
an architectural decision. It was false: the script's header reads
`Usage: workspace-pull [WORKSPACE_DIR]` and line 46 is `WORKSPACE_INPUT="${1:-.}"`.

The error came from grepping for `--[a-z-]*` and option-parsing idioms, finding nothing, and
concluding the capability was absent. **The grep was correct; the inference was not.** A positional
argument does not match a flag pattern.

## Why this one is invisible

A negative grep proves only that *the pattern I searched for* is absent. It says nothing about the
capability I actually care about, which may be implemented in a shape I did not think to search for.
There is no signal distinguishing "not there" from "not searched for" — an empty result looks exactly
like a clean answer, which is why it gets promoted straight into a claim.

## How to apply

- **Before asserting an absence, read the entry point** — a script's header, usage line, and first
  ~50 lines — rather than resting on a pattern search.
- **State absences at the granularity actually verified.** "No flag parser" was true and sufficient
  for the argument I was making; "no argv handling at all" was neither.
- **A finding whose whole job is to justify a decision deserves a direct read**, not a grep. The
  weight the claim carries sets the evidence standard.

Caught by a cold-context reviewer explicitly instructed to verify the doc's claims against real code
— two of three reviewers found it independently, which is what promoted it from nit to rule. The lens
that catches this class is the implementation-fidelity one in
[parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md) § Lens choice.

## See Also

- [consistency-sweep-read-not-just-grep.md](consistency-sweep-read-not-just-grep.md) — the sweep-side
  sibling: a *clean* grep after a rename verifies tokens, never semantics. Same tool, same limit,
  opposite direction.
- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md) — the parent
  reflex: an inference is a hypothesis, not a fact, and the cost asymmetry decides how hard to verify.
- [workspace-lifecycle-four-commands.md](workspace-lifecycle-four-commands.md) § What the scanner
  does not cover — the same session's opposite case: an absence that *was* verified by reading
  `build_findings`, and is real.
