# Draft — Closing the TriLens fix boundary

**Status:** design, not implemented. Targets `/lr:trilens-loop` (shipped v30).
**Evidence:** `fix-defects-are-context-errors.md`, `a-fix-is-a-change-and-changes-need-review.md`.
**Backlog:** `framework-improvements-backlog.md` § Multi-Agent Collaboration.

## Problem

Across v37 and v38, every TriLens round after the first found a defect created by the previous
round's fix. The loop catches these — that part works. What it cannot catch is the **last** round's
fixes:

> N rounds of review produce N rounds of fixes; only N−1 of those get reviewed.

So whenever the loop ends on findings rather than on a clean round, the shipped tree contains
unreviewed material **by construction**. Both v37 and v38 ended that way, at the three-round ceiling.

Two further facts shape the design:

- **7 of 8 fix-defects were context errors** (scope, placement, prerequisites, completeness), not
  logic errors. Reviewing a fix pass for *correctness* looks in the wrong place.
- The fixer is the only participant who is never cold. Reviewer independence is the loop's premise,
  and repairs are exempt from it.

## Decisions

**D1 — The final round is fix-free.**
On the last round the host applies nothing. Findings are triaged and recorded as `DEFERRED`, and go
to the backlog or the next release. The shipped tree then equals exactly what the last reviewers
read. This converts "unreviewed fixes" into "known deferred findings" — strictly better as a record,
because a deferred finding is visible and an unreviewed fix is not.

Consequence to accept openly: a genuine BLOCKER on the final round forces a choice — ship with it
deferred (unacceptable for a blocker), or spend a round. So D1 needs D2.

**D2 — A fix-audit pass, which is not a round.**
One cold reviewer, given only (a) the findings ledger with dispositions and (b) the diff of the
repairs. Not a lens on the release — a lens on the repairs. It does not count against the three-round
ceiling, on the same reasoning that exempts a dead-lens retry: the ceiling exists to bound *review
breadth*, and this is a bounded, single-purpose check that the loop's own output is sound.

Brief is deliberately narrow, and asks the context questions rather than the correctness one:
- Does each fix close the finding it cites, or only narrow it?
- What else implements this rule, and what else *states* it? Name any site left stale.
- Does the enclosing container still hold — table renders, procedure reachable, prerequisites
  established, ordering preserved?
- Which propositions did the fix add? List every "ensures / prevents / guarantees / agrees" and say
  whether it is true.

**D3 — The host declares blast radius before applying.**
One line per finding, in the ledger, before the edit: implementations touched, statements of the same
rule, container requirements. Cheap, and it is the direct antidote to the keyhole effect that
produced 7 of 8 defects. Also gives D2 something to check the fix *against*.

**D4 — Re-read in the container, never in the diff.**
After applying, read the whole enclosing unit — the whole table, the whole procedure, the whole
function. Context errors are invisible in a diff by definition, and every defect in the sample was
one.

**D5 — Deterministic checks where they exist.**
A markdown structure lint (table integrity, heading nesting, link targets) over changed docs would
have caught the v38 blank line with no judgement involved. Prefer this to any of the above wherever
it is available: point-of-use guardrails beat recorded discipline.

## Open questions

- **Q1.** Does D2 run every round, or only after the final one? Every round is more thorough and
  roughly doubles reviewer count; final-only is cheap but leaves mid-loop fix defects to the next
  round, which is where they already get caught. Leaning final-only.
- **Q2.** Does D1 change the ceiling's meaning — is it now "three reviewing rounds plus a fix-free
  verification round", i.e. effectively four? Argues for restating the ceiling as *rounds that may
  produce fixes*, which is what it was always trying to bound.
- **Q3.** Should D3's blast-radius line be required in the ledger (enforceable, and the ledger is
  already a shipped artifact of the loop) or advisory?
- **Q4.** D5 needs a home: a new deterministic check in `lr-core`, an item in `/lr:check`, or a
  pre-commit-style hook. `/lr:check` is the natural fit but it is agent-repo-scoped, not
  framework-repo-scoped.

## Cost

D3 and D4 are free (host discipline, no extra agents). D2 adds one subagent per loop. D1 removes
work. D5 is the only build item of any size.

## Sequencing

D3 + D4 first — free, and they attack the dominant failure class immediately. Then D1 + D2 together,
since D1 is unsafe without D2. D5 independently, whenever Q4 resolves.
