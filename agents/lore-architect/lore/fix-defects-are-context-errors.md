---
lore: 1
type: topic
summary: "Across v37-v39, defects introduced by TriLens fixes are context errors rather than logic errors and concentrate in the prose describing a fix — and the round cap guarantees the last round's fixes ship unreviewed."
parent: lore-context.md
---

# Fix Defects Are Context Errors, and the Round Cap Guarantees They Ship

[a-fix-is-a-change-and-changes-need-review.md](a-fix-is-a-change-and-changes-need-review.md)
established that a review round's output is unreviewed code. Three releases now show the same
pattern — v37, v38 and v39 each ran the loop to its ceiling, and in all three, **every round after
the first found a defect created by the previous round's fix**. That is enough data to ask *why*, and
the answer is more specific than "fixes are risky".

## It is mostly the loop working

The observation is largely evidence of a functioning process: fix-defects exist everywhere, and here
they get caught. The real problem is at the boundary, and it is arithmetic:

> N rounds of review produce N rounds of fixes, but only N−1 of those rounds' fixes get reviewed.

Unless a round returns **zero** findings — and therefore produces zero fixes — the shipped tree
contains unreviewed material by construction. The three-round ceiling does not merely cut the loop
short; it guarantees this outcome whenever the loop ends on findings rather than on silence. This is
the structural reason a clean round is the only true stopping condition, and why "all findings
applied" must never be recorded as convergence
([trilens-loop-feature.md](trilens-loop-feature.md) § When the round cap bites).

## What kind of defects they are

Classifying all eight self-inflicted defects across the two releases:

| Failure kind | Count |
|---|---|
| Right change, wrong **context** — scope, placement, prerequisites, completeness | 7 |
| Wrong **logic** | 1 |

Almost none were "the fix computed the wrong thing." A blank line that broke a markdown table so a
newly added finding row would not render; a paragraph made unreachable by a precondition that already
handled the case; a rule fixed in both implementations but left stale in the doc that users are
pointed to; an instruction telling an executor to compare against a baseline no step ever captured.
Each is correct in isolation and wrong in its surroundings.

**Design consequence:** a fix pass should be reviewed for *context*, not correctness. Asking "is this
change right?" finds one defect in eight. Asking "what else does this touch, and does its container
still work?" finds seven.

## v39 sharpens it: the drift is in the prose, not the code

v39 ran four consecutive fix rounds (three TriLens rounds plus the substitute round), each finding a
defect introduced by the previous round's fix — and the distribution was lopsided in a way worth
planning around:

- Round 1 fixed a containment gap in the script. That guard needed one correction (round 2) and was
  then correct for the rest of the release.
- Every defect found by rounds 2, 3 and the substitute round was in *prose about* the guard, not the
  guard: a Cleanup rule stating the pre-fix semantics, an engine-profile binding table left behind
  while two sibling sentences in the same file were updated, a deleted step, a circular retry
  sentence, and release-note claims that had gone stale.

Three of the four were the same shape — **one rule stated in more than one place, with the sites
drifting apart**. That is
[single-canonical-source-discipline.md](single-canonical-source-discipline.md) failing under edit
pressure, and it is predictable enough to plan for: the code has a compiler, a test suite, and a type
system of sorts; the prose has none of those, so each edit to it is an unverified change to an
implementation. It also explains why mechanism 1 below bites hardest on docs — execution never visits
the documentation.

Two triage practices fall out, on top of the ones below:

- **After changing a rule, enumerate every site that states it** before moving on — not just the site
  the finding named. v39 round 1's Cursor-profile fix updated two sentences and missed the binding
  table, which is the site an executor actually consults.
- **Give at least one round a lens that reads the artifact as a whole document rather than as a
  diff.** v39's cold-read lens found the buried step and the unreachable Cleanup path that three
  diff-scoped lenses had walked past.

The concrete v39 pair is recorded in
[realpath-for-identity-logical-for-contract-shape.md](realpath-for-identity-logical-for-contract-shape.md)
(correct in code from round 2, wrong in its prose restatement two rounds later) and
[a-release-record-goes-stale-while-you-fix-it.md](a-release-record-goes-stale-while-you-fix-it.md)
(the release notes as the prose that decays once per round).

## Why it is systematic

Four mechanisms, each independently sufficient:

1. **A finding is a keyhole.** It names a path and a line — superb for locating, actively harmful for
   scoping. The fixer teleports to the named spot and never looks *up* (is this already handled
   elsewhere?), *sideways* (what else states this rule?), or *out* (does the enclosing table,
   procedure, or function still hold?). You find a bug by tracing execution, and execution never
   visits the documentation — which is exactly why the doc goes stale while both implementations get
   fixed.

2. **The fixer is the only hot reader in a loop built on cold ones.** Reviewer independence is the
   loop's whole premise, but the person applying fixes gets *hotter* every round — more context, more
   investment, more of a story about what the release is. Nobody reads a fix cold except the next
   round's reviewers. That is precisely why it is always the *next* round that finds it.

3. **Fixes trade visible failures for invisible ones.** You optimise against the failure you were
   shown, and that one is by definition the one someone could see. v37's clone-cleanup fix stopped
   Ctrl-C leaving a half-written clone and introduced deleting a *completed* one — a recoverable
   annoyance traded for data loss. v38's pathspec commit fixed a visible sweep-in of another session's
   staged files and introduced invisible content substitution. This is why fix-defects skew *worse*
   than the originals, not merely as frequent.

4. **The rationale is more dangerous than the change.** Both false claims in v38 —
   "the two parsers agree", "the race has no window to land in" — sat in explanatory prose written to
   justify fixes that were themselves sound. Made silently, neither defect would have existed. A fix
   mints new propositions, and they ship carrying the confidence of the fix rather than the scrutiny
   of a claim. See [script-emits-data-doc-owns-the-words.md](script-emits-data-doc-owns-the-words.md)
   for the sibling failure at a different seam.

## Practices

Cheap, and aimed at the 7-of-8:

- **State the blast radius before editing.** One line per finding: what else *implements* this rule,
  what else *states* it, and what the container requires (rendering, ordering, prerequisites). This is
  the direct antidote to the keyhole.
- **Re-read the fix in its container, not in the diff.** A diff shows `+| S16 | … |` and looks
  perfect; the rendered table shows a row that is not in the table. Context errors are invisible in
  diffs — which is the only kind of error we make here.
- **Treat every "ensures / prevents / guarantees / agrees" as a testable claim.** Test it, or downgrade
  the verb. A claim-audit lens after a fix round earns its slot for exactly this reason
  ([lens-novelty-is-the-scarce-resource-on-re-review.md](lens-novelty-is-the-scarce-resource-on-re-review.md)).
- **Prefer a deterministic check over the discipline** wherever one exists — a markdown-table lint
  would have caught the blank line with no judgement involved
  ([point-of-use-guardrails-beat-recorded-lore.md](point-of-use-guardrails-beat-recorded-lore.md)).

## The structural fix

Do not try to make fixes defect-free; that is not achievable. **Make the boundary safe instead** — the
proposal is a fix-free final round plus a fix-audit pass that does not consume a round. Design:
`workdir/draft-trilens-fix-boundary.md`; tracked in
[framework-improvements-backlog.md](framework-improvements-backlog.md) § Multi-Agent Collaboration.

See also [post-convergence-edits-need-their-own-gate.md](post-convergence-edits-need-their-own-gate.md),
[parallel-reviewer-fanout-pattern.md](parallel-reviewer-fanout-pattern.md),
[a-gate-that-died-is-not-a-gate.md](a-gate-that-died-is-not-a-gate.md).
