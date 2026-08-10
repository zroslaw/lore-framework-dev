---
lore: 1
type: topic
summary: "The judgement layer for multi-lens adversarial review fan-out: lens choice per ship and per round, brief shape, triage, convergence profiles, stall handling, and when not to fan out."
parent: lore-context.md
---

When shipping a substantive change (script, skill, doc set), run **three parallel reviewers with mutually-exclusive lenses**. Different from `sonnet-subagent-review-pattern.md`, which is single-lens role-as-perspective; this is multi-lens adversarial fan-out specifically for shipped artifacts.

## This pattern is now a shipped skill — run `/lr:trilens-loop`

Since framework **v30** the loop has a plugin implementation: **`/lr:trilens-loop`**
(`trilens-loop-feature.md`, `lore-framework/docs/trilens-loop.md`). It was promoted directly from this
topic. **Reach for the skill rather than hand-assembling the fan-out** — the doc enforces what a
hand-run pass forgets:

- Reviewer independence (cold-context subagents; context-inheriting forks forbidden).
- The APPLIED / DECLINED / ACCEPTED-not-applied ledger fed back to each later round, so settled items
  stay settled.
- The three termination guards — round cap, reviewer-gated stop on any latest `BLOCK`, and "a silent
  round is not a clean round."
- Routing the executor through the engine's `subagent-spawn` binding, which is exactly how I *stopped*
  hitting the named-teammate trap below (I hit it live while hand-running the v30 review).
- Disclosure of any rail the invocation switched off, and a convergence ledger that comes out as a
  record rather than something reconstructed from memory at summary time.

**What stays here:** the judgement layer. The skill picks *that* three lenses are chosen and enforces
the loop's mechanics; it does not tell you *which* lenses fit this change, how to read a convergence
profile, what to do when reviewers disagree or stall, or when not to fan out at all. That is the rest
of this topic. Read it for lens choice and triage; invoke the skill to execute.

Hand-running is still legitimate for cases outside the skill's change-scoped default — e.g. reviewing a
committed artifact, or a fan-out that is not a review at all
(`use-cases-via-parallel-consult-pattern.md`).

## Triggers

Use this when shipping:

- A new script that processes user-controlled input.
- A skill rename or hard-rename of an existing one.
- A doc sweep across many files.
- A vocabulary or schema change.
- **Doc-only edits that ship as a `VERSION` bump** (added in v12) — release notes, new skill docs, conventions changes. The pattern's overhead is fine; the catch rate justifies it.

Don't use this for trivial commits — overhead isn't worth it. Reach for it when the change has meaningful blast radius: anything that gets a version stamp, anything that hits production users.

For routine edits (single-file polish, lore topic additions inside an agent's own knowledge), still skip — overhead isn't worth it. For lore additions, prefer `sonnet-subagent-review-pattern.md` (single-lens role-perspective).

## Lens choice — pick three that don't overlap

Round 1 of v11 used: **correctness/bash semantics**, **security/parser robustness**, **UX/docs/framework fit**.

Round 2 of v11 used: **terminology coherence**, **newcomer experience**, **release readiness/disclosure**.

Round 1 of v12 (doc-only ship) used: **UX/newcomer/discoverability**, **framework architectural consistency**, **correctness/safety/accuracy with filesystem verification**.

The lens choice should be deliberate per ship. Lenses that worked well:

- **Correctness / bash semantics** — bugs, races, edge cases, idiomatic shell. Catches array-handling, trap bugs, locale issues.
- **Security / parser robustness** — adversarial input, command injection, path traversal, hostile content. Critical when user-controlled data drives execution.
- **UX / output quality / discoverability** — does the user see actionable error messages? Is output scannable? Are exit codes consistent? For doc edits: will a real user hitting a real problem find this skill, understand it, apply the fix?
- **Terminology coherence** — when a vocabulary change sweeps multiple files, did the migration actually hold together? Are there half-migrated contradictions?
- **Newcomer experience** — walk through the docs as a first-time user. Where does the path break down? What's missing? What's mis-routed?
- **Release readiness / disclosure** — are breaking changes mentioned? Is auto-upgrade safe? Are version stamps consistent? Is the backlog updated?
- **Framework architectural consistency** — does the change compose with the three-layer model, skill-doc pattern, framework-scope-vs-agent-scope, naming-foundational-principles meta-rule, sibling-skill non-overlap? Especially powerful when the architecture reviewer is given the architect's own `lore-context.md` as a baseline — applies the architect's stated meta-rules to the change being reviewed.
- **Correctness with filesystem verification** — for doc edits that promise commands, paths, or behaviors, the correctness reviewer should run actual bash commands (`ls ~/.claude/plugins/cache/`, `cat .../VERSION`, `find ...`) and ground every finding in observed state. Catches defects pure prose review misses.
- **Findings as a system** — hand one reviewer the *set* of diagnostics/messages a release ships and
  ask whether they cohere: do two findings ever give the user contradictory remedies, does any of them
  describe state inaccurately? This lens has no analogue in ordinary code review and was
  disproportionately productive on v37 — it caught S6 and S13 handing contradictory remedies, and S12
  calling framework scratch state "your own files, nothing will touch them". **Any release that ships
  a set of diagnostics deserves it.**
- **AI-installer (literal executor)** — for the paste-link installer doc genre (`paste-link-installer-doc-genre.md`): brief the reviewer to read the doc *as the agent that must execute it literally*, tracing each instruction against real files/commands rather than judging tone. Catches a distinct class the newcomer/editorial lenses miss — see `ai-installer-review-lens.md` for the full brief shape and the empirical case that justified naming it as a fourth lens.

**Rule:** the lenses should be *mutually exclusive* — if two reviewers are likely to find the same issues, you've wasted a slot. Tell each lens explicitly what to skip (what the others will catch).

## Brief structure for each reviewer

Effective briefs share this shape:

1. **Context** — what's shipping, what changed.
2. **Files to review** — concrete absolute paths. Include "files NOT in scope but might still need a check" — that's where misses hide.
3. **What to look for** — explicit list under each lens's specialty. Examples of failure modes you want them to consider.
4. **What to skip** — generic advice ("use set -e"), nits, low-confidence findings, *and what the other lenses will catch*.
5. **Anchor docs** — for architectural review, point at `lore-architect/lore-context.md`. For correctness review, list internal claims to verify with filesystem checks.
6. **Output format** — severity (BLOCKER / HIGH / MEDIUM / LOW), file:line, issue, one-sentence fix, final verdict.
7. **Cap on length** — ~600 words per reviewer. Keeps reports digestible.

## Brief the goal, not the rationale

Give the reviewer the **goal** of the change — what the artifact is for, so it can judge fitness for
purpose — but **not your rationale for each decision**.

Rationale pre-empts the criticism you are paying the reviewer to produce. A reviewer told *why* you
chose X evaluates whether your reasoning is internally coherent; a reviewer told only *what X is for*
evaluates whether X actually serves the purpose. The second is the useful question.

This is the same independence rule applied at two levels, and both are needed:

- **Spawn level** — the subagent must not inherit the caller's conversation (no context-inheriting
  fork). See `subagent-as-optimization-vs-subagent-as-semantics.md`.
- **Brief level** — the brief must not hand over the caller's justifications. A cold-context subagent
  handed a brief full of "we did X because Y" is only nominally independent.

Concretely, in item 1 of the brief structure above, **Context** means *what changed and what it is
for* — not the design argument. The shape used in v30's own self-review (21 findings across 4 rounds):
context = what changed and what it is for; files = absolute paths including adjacent out-of-scope
material; this lens = what to look for; what to skip = nits plus what the *other* lenses own; output
format = severity / `file:line` / issue / one-sentence fix, then a verdict line.

**Caveat worth keeping:** on later rounds you *do* deliberately feed back dispositions
(APPLIED / DECLINED + reason). That is not rationale for the design — it is the record of what was
already adjudicated, and without it fresh reviewers re-raise settled items every round. See
§ Persistent reviewers across rounds below.

## Result delivery differs by spawn kind (named teammate vs background subagent)

The v18 `lr-wait` ship validated this pattern on **feature code**, not just doc releases: a 3-lens fan-out (correctness / framework-fit / product-UX) over the script + MCP server surfaced a genuine MUST-FIX (an `lr-emit` infinite-loop hang, empirically reproduced by the reviewer) plus several should-fixes; all three verdicts were ship-with-fixes.

That run also exposed a spawn-mechanics gotcha — **how a reviewer's report comes back depends on how you spawned it:**

- **Plain background subagents (no `name`)** — the subagent's final message *is* returned to you as the `Agent` tool result. This is the default for review fan-out; reach for it when you just want findings back.
- **Named teammates (given a `name`, so they run as Agent-Teams teammates)** — do **not** auto-return their final report to the lead. In the v18 run one teammate proactively `SendMessage`'d its findings; the other two only sent idle notifications and each had to be `SendMessage`'d to request the report. If you use named teammates for review, **explicitly instruct them in the spawn prompt to `SendMessage` their full findings to the lead before going idle.**

Either way, the downstream discipline is unchanged — distinct lens + exact file paths + "read-only, report don't edit," then synthesize per "How to apply findings" below.

**This trap now lives where an executor actually reads it.** Recording it here since v18 did not stop
me hitting it: while hand-running the v30 review I spawned all three reviewers with `name`s, all three
went idle without reporting, and the round had to be re-run unnamed. Knowledge in agent lore protects
you only if you think to recall it. v30 moved the fact into `docs/engines/claude.md`'s `subagent-spawn`
binding — the doc read *at the moment of spawning* — along with the `fork` context-inheritance trap.
See `docs-engines-convention.md` § Engine traps belong in the binding, not only in agent lore.

The engine-neutral form of the requirement, which is what the skill states: **the report must actually
come back to you.** Phrased that way, a trap in any engine is caught by the requirement rather than by
an engine-specific warning that only covers the engine you thought about.

## How to apply findings

After the fan-out completes:

1. **Verify each BLOCKER/HIGH** before acting — read the file, confirm the reviewer's claim. Reviewers occasionally hallucinate or work from stale state.
2. **Apply BLOCKER + HIGH first**, then MEDIUM, then triage LOW.
3. **Cross-check overlap — and weight it up, don't dedupe it away.** If two reviewers flagged the same issue from different angles, fix once and note both. **Convergence across independent lenses is strong evidence the finding is real**, and is the signal most likely to be lost during triage: the second report reads as redundant right when the first one is being argued with. Two lenses on the same sentence gets reworded, not defended — that agreement is what the fan-out is being paid for. See `check-own-lore-before-dismissing-a-finding.md`.
4. **Flag deferred items to backlog** explicitly — don't lose them.
5. **Acknowledge what was deferred** in the final summary so the user knows what's not in scope.

## Cost

Three parallel agents typically run 30s–3min. Cost is real but not prohibitive — appropriate for substantive ships including doc-only `VERSION` bumps. Don't over-use; reserve for changes that warrant the scrutiny.

### The wire is cheap; the reasoning is what you pay for (measured 2026-07-27)

One `/lr:trilens-loop` round, three cold sonnet reviewers over **two** changed doc files:

| Lens | Tokens | Tool calls |
|---|---|---|
| hand-executor fidelity | 44.2k | 4 |
| internal consistency | 31.1k | 2 |
| corpus coherence | 98.8k | 30 |
| **total** | **174.1k** | **36** |

Host side: ~1.6k out in briefs, ~3.5k back in findings, ~5–8k for verification and edits. **Roughly
94% of the loop's cost happened inside subagents and never entered host context.**

Three things follow, and the first two are corrections to how I used to reason about this:

1. **A reviewer's budget is dominated by its own reasoning, not by the material handed to it.** The
   two lenses that mostly read the two changed files (~4k of actual content between them) still spent
   44k and 31k. So the "don't send the diff, let the reviewer discover the changes" rule is close to
   **cost-neutral**; pasting the diff would have saved a rounding error. **Never justify the exchange
   contract as a token-saving measure** — that framing is measurably weak and will not survive
   scrutiny. Justify it on what it actually buys: *independence* (a reviewer that reads the tree
   itself is not steered by the author's framing) and *host-context preservation* (174k of reading
   returned as ~3.5k of pointers; reviewers narrating their reasoning back would have put maybe
   30–50k into the host mid-review, while it holds the ledger, moving it materially closer to
   compaction).
2. **Trimming the brief buys nothing.** At ~1.6k out for three briefs, the brief is noise-level. Budget
   belongs in *rounds* and *lens independence*, not in model size and not in brief length.
3. **The expensive lens earned it.** Corpus coherence at 99k / 30 tool calls produced the round's
   `BLOCKER` and its stale-release-note finding, precisely because it spent its budget reading
   *other* files to compare against. A diff would not have shortened that work. Cost per lens is a
   poor proxy for value per lens.

## When the reviewers disagree

Trust your own judgment after reading the actual code/docs. Reviewers operate from limited context. The user's standard ("production-ready, high quality") is the bar — not consensus among reviewers.

## Choose lenses per *round*, not per loop (v37, 2026-08-10)

The lens rule above ("pick three that don't overlap") applies within a round. Across rounds, let the
round number change the *kind* of lens. Re-running the same trio over a changed tree buys the same
thinking three times.

The shape that worked over v37 (nine lenses, three rounds):

- **Round 1 — lenses about the release itself.** Script↔doc equivalence (the Script Fallback Contract
  is this framework's signature failure mode), destructive safety (the procedures delete and commit on
  a real machine), cold-user coherence (a late change had left stale copies of a superseded claim in
  four docs).
- **Round 2 — one lens aimed at round 1's own output.** "Did the fixes fix it, and did they break
  anything" caught a fix of mine that was worse than the bug
  (`a-fix-is-a-change-and-changes-need-review.md`). **Make this the standing first lens of round 2 in
  any loop where round 1 ended with fixes applied.** The other two go where round 1 didn't:
  executability (simulate being the agent that runs the doc) and the installed base (version skips,
  mixed-version teammates, state older versions left behind).
- **Round 3 — narrow to where the evidence says the risk concentrated.** On v37 that was shell signal
  handling, the finding set as a system, and whether ~20 piecemeal prose patches still read as one
  document. The last of those found the round's blocker — patch-on-patch editing is exactly how a doc
  acquires two rules for one thing.

General shape: **round 1 reviews the work, round 2 reviews the fixes and widens the frame, round 3 goes
where the evidence points.** This is the multi-round refinement of the v13 note below, which framed
round 2 as a single verification reviewer; the lens *kinds* are the part that must change, not
necessarily the reviewer count.

## Two rounds, not one, when the change is large

Two rounds proved valuable in v11, v12, and v13 ships:

- **v11**: round 1 caught script-level issues (security, correctness, basic UX); round 2 (after a sweep was added) caught terminology coherence, newcomer experience, and release readiness.
- **v12**: round 1 (three lenses, ~25 findings) caught the targeted vs broader cache-wipe scoping (filesystem-verified by correctness reviewer), broken cross-references (architecture reviewer), and the bootstrap-note chicken-and-egg case (UX reviewer). Round 2 (single reviewer, narrow scope) confirmed shipping with one nit. The verdict-grade ("ship as-is" vs "more rounds") was the actual value of round 2, not new findings.
- **v13**: round 1 (correctness, architecture, UX in parallel) had two reviewers stall after partial returns; the third (UX) returned a full report with 19 findings. Round 2 (single focused reviewer with filesystem verification) caught cross-doc contradictions round 1 structurally couldn't, plus verified the dirty-tree-no-gate decision live in `/tmp`.
- **v15**: **seven rounds** to convergence — exceptional, due to combined four-task scope (write-aware gate + spawn-teammate Step 7 + Step 7c verification + teammate-conventions anchoring). R1 (12 findings, max-effort recall-mode) surfaced latent invariants the new gate exposed; R2 (8) caught self-contradictions and dangling references; R3 (12, parallel multi-lens with role-as-perspective) caught `(none)` sentinel grammar drift across 3 sites and `/lr:check` #20 missing entirely; R4 (9) the parser's fenced-body-terminator bug; R5 (6) Glob token grammar narrower in conventions than parser; R6 (2) Glob example violating its own grammar (`agents/!(legacy)` parens not in declared char class); R7 clean → SHIP. Findings clustered around the previous round's edits ("fix-the-fixes" surface). Convergence by progressively smaller findings count is the ship signal.

Each round was tightly scoped to its phase of work.

**Refinement (v13):** plan round 2 deliberately as **a single focused reviewer with filesystem access and the full diff in scope** — not just "more rounds if needed." Round 1 is "find issues per lens" (breadth, parallel, lens-isolated). Round 2 is "verify fixes and catch cross-doc drift" (depth, sequential, full diff). Two distinct jobs.

## Persistent reviewers across rounds via SendMessage (validated variant)

When the reviewers are spawned as **named teammates**, keep the *same* named reviewer agents across rounds and send round N+1 as a `SendMessage` follow-up instead of spawning fresh reviewers. Validated on the 2026-07-17 onboarding/rebrand review (three sonnet teammates — newcomer, AI-installer, editorial — four rounds to convergence on Claude Code):

- **Same agents, follow-up messages.** They retain full context of the files and their own prior findings, so later rounds are fast and focused (no re-reading the tree from scratch).
- **Feed dispositions back explicitly.** Open each round's brief with a numbered **APPLIED / DECLINED(+reason)** list for that reviewer's previous findings, plus a short digest of *other* lenses' changes that touched their territory. This stops declined taste-calls from resurfacing and re-anchors the reviewer on the delta — no reviewer re-raised a settled item across four rounds.
- **Route new edits to the owning lens.** When a fix lands in text that is literally that lens's dimension (e.g. an INSTALL preamble is AI-installer territory), send the already-clean installer lens back over just that delta rather than assuming its earlier clean verdict still covers it.
- **A scoped final round is legitimate.** When the only remaining change is a one-line wording fix in one lens's dimension, a single-reviewer confirmation round closes convergence; the other lenses' clean verdicts remain valid for a tree unchanged in their dimensions.
- Convergence profile on that run: R1 = 21 findings (17 applied), R2 = 8 (6 applied, **two of them real bugs introduced by R1 fixes** — the fixes-create-seams pattern), R3 = 1, R4 = 0. Consistent with the 2–3-round doc-release norm, stretched by a large R1 batch.
- Also confirmed on that run: sonnet reviewers **do** run CLIs and slug-check anchors when the brief explicitly instructs it ("you may run `claude plugin --help`", "verify per GitHub anchor rules"). Earlier misses on such catches were briefing gaps, not model-capability gaps — see `ai-installer-review-lens.md` (execute-the-CLI-help brief).

This is the persistent-teammate counterpart to the "Result delivery differs by spawn kind" note above: named teammates don't auto-return, so instruct each to `SendMessage` its findings; the payoff is context that survives across rounds.

## v15 operational lessons — multi-round convergence

v15 went through **seven rounds** before shipping. Each round caught real issues; convergence was the ship signal. Operational lessons:

- **"Pointer-AND-restatement" is the dominant drift pattern.** Multiple v15 rounds caught the same shape: a fix declares one site canonical, but other sites still inline the rule "for clarity." Discipline: pointer-only, no inline summary. The restatement still drifts. See `single-canonical-source-discipline.md`.
- **Lens 3's "construct in /tmp and run" is load-bearing.** Lens 1 (UX) and Lens 2 (architectural) tend to trust the doc's framing; Lens 3 reads with adversarial intent — *what would an LLM following this literally produce?* — and the bash verification is the load-bearing part. Without it, Lens 3 collapses into another prose review. v15's parser body-terminator bug (which would have silently let migration 2's prose paragraph slip into the write-set) was caught only because Lens 3 constructed migration variations in `/tmp` and ran the parser shape against them.
- **Self-contradicting examples are worth grepping for.** R6 caught conventions.md's Glob token example using parens that violated its own declared character class. Useful sanity check: every time you write a "valid" example, mechanically verify each character against the spec.
- **Multi-round terminates predictably.** Round N findings cluster around round N-1's edits — the "fix-the-fixes" surface is real. When round N finds only cosmetic issues, the next round is the ship gate. Don't keep adding rounds for diminishing returns; convergence is the signal.
- **For doc-only releases**, expect 2–3 rounds typical, 5+ for releases that re-shape multiple cross-cutting docs (v15 took 7 — exceptional, due to combined four-task scope). Single-pass review is insufficient when the patch reshapes shared procedural infrastructure; multi-round convergence is now the architect's default discipline (`role.md` § Lore-Curation Disciplines).

## Graceful degradation when a parallel reviewer stalls

Parallel reviewer fan-out can stall on individual reviewers — Claude's stream-watchdog timeouts, network blips, model errors. The pattern degrades gracefully if you treat partial returns as additive evidence rather than failed runs.

**v13 instance:** two of three round-1 reviewers (correctness + architecture) timed out after 600s. Each returned a partial finding before stalling — both genuine: correctness caught a stale `Step 3` reference; architecture caught a missing boot-ordering rationale gap. The UX reviewer returned a full 19-finding report. **The pattern still produced enough material to ship safely.** Round 2 then verified the fixes plus surfaced two more contradictions.

**Operational rules when reviewers stall:**

1. **Don't abort on partial returns.** A stalled reviewer that returned even one finding before timing out has done useful work. Treat it as additive evidence, not a discarded run. Read what came back; act on it.
2. **A single non-stalled reviewer is often enough breadth.** If at least one of N reviewers returned a full report, you have a baseline. The stalled reviewers' partials supplement.
3. **Round 2 closes the gap.** A focused single-reviewer round 2 with the full diff in scope catches cross-doc drift round 1's per-doc reviewers structurally cannot. Especially valuable when round 1 had stalls — round 2 is the consistency check.
4. **Internal contradictions across docs are the highest-yield round-2 finding.** Round 1's per-doc reviewers each see one slice; round 2 with the full diff catches drift like "doc A says X, doc B references the now-removed X."
5. **Filesystem verification beats prose review.** Round 2 should run actual bash commands (constructing scenarios in `/tmp`, `ls`/`cat`/`diff` against the real cache or repo). The v13 dirty-tree-no-gate decision was *verified live* by setting up dirty-tree scenarios and observing git's actual behavior — irreplaceable evidence vs prose claims.

6. **A reviewer that went idle without reporting may simply not have spoken.** Ask once for its
   findings and verdict before writing the lens off — see
   `a-gate-that-died-is-not-a-gate.md` § Alive but silent, which owns the rule.

**Don't mistake graceful degradation for tolerance of broken reviewers.** If reviewers are stalling consistently across runs, that's a workflow signal — the brief may be too long, the model may be wrong-sized, or the prompt may be triggering the watchdog. Investigate. Graceful degradation is the safety net, not the design goal.

## Filesystem-grounded correctness — the v12 escalation

For doc edits that promise concrete commands, paths, or behaviors, the correctness reviewer should ground every finding in **actually run bash commands** rather than prose evaluation:

- `ls ~/.claude/plugins/cache/` to verify path layout
- `cat .../VERSION` to confirm version stamps
- `diff -r ...` to verify file equivalence
- `find ~/.claude/plugins -maxdepth 2 -type l` to map symlink structure

The v12 ship's targeted-vs-broader cache-wipe defect (40MB of unrelated plugin state at risk) was caught only because the correctness reviewer ran ~12 actual filesystem commands. Pure prose review would have shipped the broader command as the default.

Builds into the brief: list the claims; ask the reviewer to run commands proving each.

## Architecture lens reading the architect's own lore

For framework-architectural review, point the architecture reviewer at `lore-architect/lore-context.md` as a baseline. This lets it apply the architect's own meta-rules ("name foundational principles as their own topics", three-layer model, framework-scope-vs-agent-scope) to the change being reviewed.

Several v12 findings traced directly back to architect-authored principles, which the architect would have applied if reviewing solo — but the gap between authoring a principle and applying it consistently is exactly what an outside lens catches.

## When NOT to fan out — the per-item-uniformity test

The pattern's strength is **independent claims under independent adversarial framing**. Its inverse failure is fanning out across items that share a uniform property a single agent could audit in bulk — e.g., "every scenario cites a real intent source," "every entry has a stable ID." A dedicated agent per item adds parallel cost without adding rejection power.

**Default question before any fan-out:** *"Would a single agent looking at all N items at once produce the same verdicts as N separate agents?"* If yes, batch.

Worked example from the lr-dev quality workflow prototype: v1 spent 19 parallel agents on per-scenario intent-citation verification → zero scenarios dropped (the schema constraint already enforced it). v2 dropped that stage entirely and kept per-item adversarial verify only for *bugs* (which really are independent claims). See `workflow-primitive-operational-notes.md` § Right-size the verify fan-out — the same principle, codified for the Workflow primitive.

## Composition with `sonnet-subagent-review-pattern.md`

That pattern is **single-lens role-as-perspective** — one reviewer booted as the agent itself, used for principle-class lore additions and structural changes within an agent's own knowledge. This pattern is **multi-lens adversarial fan-out** — three reviewers with disjoint specialty lenses, used for shipped framework artifacts (scripts, skills, doc sweeps, schema changes, doc-only `VERSION` bumps).

Often complementary: use sonnet-subagent for the lore-side polish; use parallel-reviewer for the public-facing ship.

## See Also

- `trilens-loop-feature.md` — **the shipped skill this pattern was promoted into (v30)**; invoke it rather than hand-assembling the fan-out.
- `trilens-loop-v31-restructured.md` — the parked v31 doc, whose host/reviewer exchange contract the § Cost measurement above was taken against.
- `check-own-lore-before-dismissing-a-finding.md` — triage-time discipline: verify the rule a finding rests on before calling it moot; convergent lenses get the benefit of the doubt.
- `subagent-as-optimization-vs-subagent-as-semantics.md` — why reviewer independence has no host-side fallback.
- `post-convergence-edits-need-their-own-gate.md` — a clean round certifies only the artifact state the reviewers read.
- `docs-engines-convention.md` — where engine spawn traps belong (the named-teammate trap's real home).
- `sonnet-subagent-review-pattern.md` — single-lens role-as-perspective review (different shape, often complementary).
- `use-cases-via-parallel-consult-pattern.md` — adjacent: parallel fan-out for *content gathering*, not review.
- `yaml-parser-shell-hardening-checklist.md` — operational distillation of the security lens; pre-applies what reviewers would otherwise catch.
- `feedback-don-t-defer-completable-scope.md` — applied during triage (don't defer fixes that fit in current session).
- `ailment-catalog-pattern.md` — the v12 ship that validated this pattern's application to doc-only edits.
- `single-canonical-source-discipline.md` — the dominant drift pattern multi-round review catches; pointer-only, no inline restatement.
- `graduated-verification-confidence.md` — partial returns from stalled reviewers as additive evidence is one instance of this principle.
- `workflow-primitive-operational-notes.md` — the right-size-the-fan-out rule codified for the dynamic Workflow tool; complementary inverse case.
- `consistency-sweep-read-not-just-grep.md` — the read-the-prose half of a rename/restructure sweep; the manual sibling of the filesystem-verification review lens.
- `paste-link-installer-doc-genre.md` — the onboarding-doc genre the AI-installer lens is built for.
- `skill-doc-filename-divergence-bug-class.md` — the bug class the AI-installer lens caught that a prose lens missed.
