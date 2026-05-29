When shipping a substantive change (script, skill, doc set), run **three parallel reviewers with mutually-exclusive lenses**. Different from `sonnet-subagent-review-pattern.md`, which is single-lens role-as-perspective; this is multi-lens adversarial fan-out specifically for shipped artifacts.

## Triggers

Use this when shipping:
- A new script that processes user-controlled input.
- A skill rename or hard-rename of an existing one.
- A doc sweep across many files.
- A vocabulary or schema change.

Don't use this for trivial commits — overhead isn't worth it. Reach for it when the change has meaningful blast radius.

## Lens choice — pick three that don't overlap

Round 1 of v11 used: **correctness/bash semantics**, **security/parser robustness**, **UX/docs/framework fit**.

Round 2 of v11 used: **terminology coherence**, **newcomer experience**, **release readiness/disclosure**.

The lens choice should be deliberate per ship. Lenses that worked well:

- **Correctness / bash semantics** — bugs, races, edge cases, idiomatic shell. Catches array-handling, trap bugs, locale issues.
- **Security / parser robustness** — adversarial input, command injection, path traversal, hostile content. Critical when user-controlled data drives execution.
- **UX / output quality** — does the user see actionable error messages? Is output scannable? Are exit codes consistent?
- **Terminology coherence** — when a vocabulary change sweeps multiple files, did the migration actually hold together? Are there half-migrated contradictions?
- **Newcomer experience** — walk through the docs as a first-time user. Where does the path break down? What's missing? What's mis-routed?
- **Release readiness / disclosure** — are breaking changes mentioned? Is auto-upgrade safe? Are version stamps consistent? Is the backlog updated?
- **Framework fit / architecture** — does the change compose cleanly with existing patterns? Does it violate any framework principles?

**Rule:** the lenses should be *mutually exclusive* — if two reviewers are likely to find the same issues, you've wasted a slot.

## Brief structure for each reviewer

Effective briefs share this shape:

1. **Context** — what's shipping, what changed.
2. **Files to review** — concrete absolute paths. Include "files NOT in scope but might still need a check" — that's where misses hide.
3. **What to look for** — explicit list under each lens's specialty. Examples of failure modes you want them to consider.
4. **What to skip** — generic advice ("use set -e"), nits, low-confidence findings.
5. **Output format** — severity (BLOCKER / HIGH / MEDIUM / LOW), file:line, issue, one-sentence fix, final verdict.
6. **Cap on length** — ~600 words per reviewer. Keeps reports digestible.

## How to apply findings

After the fan-out completes:

1. **Verify each BLOCKER/HIGH** before acting — read the file, confirm the reviewer's claim. Reviewers occasionally hallucinate or work from stale state.
2. **Apply BLOCKER + HIGH first**, then MEDIUM, then triage LOW.
3. **Cross-check overlap.** If two reviewers flagged the same issue from different angles, fix once and note both.
4. **Flag deferred items to backlog** explicitly — don't lose them.
5. **Acknowledge what was deferred** in the final summary so the user knows what's not in scope.

## Cost

Three parallel agents typically run 30s–3min. Cost is real but not prohibitive — appropriate for substantive ships. Don't over-use; reserve for changes that warrant the scrutiny.

## When the reviewers disagree

Trust your own judgment after reading the actual code/docs. Reviewers operate from limited context. The user's standard ("production-ready, high quality") is the bar — not consensus among reviewers.

## Two rounds, not one, when the change is large

v11 used two rounds: round 1 caught script-level issues (security, correctness, basic UX); round 2 (after a sweep was added) caught terminology coherence, newcomer experience, and release readiness — issues that didn't exist when round 1 ran. Each round was tightly scoped to its phase of work.

## Composition with `sonnet-subagent-review-pattern.md`

That pattern is **single-lens role-as-perspective** — one reviewer booted as the agent itself, used for principle-class lore additions and structural changes within an agent's own knowledge. This pattern is **multi-lens adversarial fan-out** — three reviewers with disjoint specialty lenses, used for shipped framework artifacts (scripts, skills, doc sweeps, schema changes). Often complementary: use sonnet-subagent for the lore-side polish; use parallel-reviewer for the public-facing ship.

## See Also

- `sonnet-subagent-review-pattern.md` — single-lens role-as-perspective review (different shape, often complementary).
- `use-cases-via-parallel-consult-pattern.md` — adjacent: parallel fan-out for *content gathering*, not review.
- `yaml-parser-shell-hardening-checklist.md` — operational distillation of the security lens; pre-applies what reviewers would otherwise catch.
