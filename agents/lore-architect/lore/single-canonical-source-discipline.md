**Pointer-not-restatement: when two doc sites mention the same grammar/rule/spec, one must be canonical and the other(s) must be pointer-only.** No inline restatement "for clarity" — that's the failure mode. Looks fixed today; drifts silently tomorrow when one site updates and the others don't.

The negative form of `shared-procedure-doc-pattern.md`. That topic is the positive form (one doc carries the body, callers point at it); this is the discipline that prevents inline copies leaking back in once the pointer is established.

The principle was operationalized concretely during v15's seven-round multi-lens review. Multiple rounds caught the same drift pattern; the rule that emerged is "pointer-only, no inline summary."

## How drift looks in practice

The v15 review surfaced three distinct drifts of the same shape:

1. **`(none)` sentinel grammar across three sites.** Round 2 found `conventions.md` showed em-dash form, `version-check.md` said "space/hyphen/em-dash," `check.md` said "space/em-dash only." Three subtly different specs of the same sentinel. Round 5 declared `conventions.md` canonical and added pointers from the other two — but `version-check.md` *still inlined* the separator list alongside the new pointer ("pointer-AND-restatement"). Round 6 stripped the restatement; pointer-only.

2. **The four standing teammate RULES.** v15 initial design had RULES restated in three places (spawn-prompt, `teammate-conventions.md`, `conventions.md` § Teammate Discipline). Round 1 caught the drift hazard. Collapse to single canonical site (`teammate-conventions.md`); spawn prompt becomes one-sentence recap; conventions § becomes a maintainer's index. Round 5 caught a residual half-fix in the spawn prompt's recap (covered RULES 1+2 only) — fixed by reframing as "if the boot-time load works, all four rules load; the recap is best-effort fallback." See `spawn-teammate-feature.md` § v15 changes.

3. **Glob token grammar.** Round 5's sentinel fix declared `conventions.md` canonical for sentinels, but Glob token grammar lived only in `check.md` #20.3 — split source of truth (sentinels canonical, globs not). Round 6 hoisted Glob token grammar to a sibling subsection in `conventions.md`; `check.md` and `version-check.md` now both point at it.

The pattern across all three: *establishing a canonical site is necessary but not sufficient*. The pointer-only discipline is what prevents the canonical from being shadowed by helpful-looking inline copies.

## The operational rule

> When two doc sites mention the same grammar/rule/spec, **one** must be declared canonical and the other(s) must be pointer-only. "Pointer-AND-restatement" is the failure mode — it looks fixed but the restatement still drifts. Resist the temptation to "leave the inline summary for clarity"; the cost is silent drift.

## Verification trick — grep across all sites

Useful sanity check during multi-lens review (works as a Lens 3 / correctness exercise):

1. Pick the rule/grammar/spec.
2. Grep for it across **all** doc sites.
3. List every occurrence.
4. Check whether each occurrence is a pointer or a restatement.
5. Restatement = drift hazard, even if briefly correct today.

This caught all three v15 drifts. The mechanical character of the check makes it reproducible — review rounds N and N+1 should converge on the same set of sites.

## Why "for clarity" is a trap

Reviewers and authors both default to leaving inline summaries "for the reader's convenience." Three failure modes:

1. **Drift.** The canonical site updates; the inline summary doesn't. Future readers landing on the inline summary get the old rule.
2. **Half-fixes.** A targeted fix updates one inline copy and misses others. The doc set looks consistent at edit-time but isn't across the full surface.
3. **False finalization.** A reviewer flags the drift, the author "fixes" by aligning the inline copy to the canonical at this moment — without removing the inline copy. Drift resumes immediately.

Pointer-only avoids all three. The slight loss of read-flow at the pointer site is the price; the price is paid once, the alternative pays compounding interest forever.

## Composing with shared-procedure-doc-pattern

Both topics are about "central body, thin pointers" but at different layers:

- `shared-procedure-doc-pattern.md` — *positive form*. Specifies how to factor a procedure into a single canonical doc with multiple call sites, including audience banner, inputs/invariants/per-site verbosity table, See Also reciprocation. Used when designing the procedure.
- `single-canonical-source-discipline.md` — *negative form*. Specifies the discipline that prevents the canonical site from being shadowed by parallel inline copies once it exists. Used during review and ongoing maintenance.

The positive form establishes the pattern; the negative form maintains it. Both compose with `naming-foundational-principles.md` (each named principle gets its own topic) and with `parallel-reviewer-fanout-pattern.md` (multi-round review is where drift surfaces).

## When inline summary IS acceptable

Narrow cases — judge per situation:

- **Bootstrap context** where the reader has not yet loaded the canonical doc and a one-line recap genuinely accelerates them. Caveat: this is rare; the boot-time teammate-conventions load is exactly *not* this case (boot is when the canonical doc loads cleanly).
- **Audience that won't follow pointers** — e.g., user-facing release notes where readers won't navigate to a procedure doc. Even there, prefer a single sentence + link over a parallel re-spec.
- **Single-step pointers where the canonical doc lives at a path the reader can't access** in their current context (separate plugin, external repo) — restatement may be unavoidable. Document it explicitly so future maintainers know to re-sync.

In framework code/docs, default to pointer-only. The bootstrap-recap exception is the only one v15 retained, and it's framed as "best-effort fallback if the canonical load fails," not "for clarity."

## See Also

- `shared-procedure-doc-pattern.md` — the positive form this discipline maintains.
- `parallel-reviewer-fanout-pattern.md` — multi-round review surfaces the drift; the v15 7-round convergence is the worked example.
- `naming-foundational-principles.md` — the meta-rule licensing this topic's promotion.
- `framework-defined-role-pattern.md` — adjacent: same "central body, thin per-instance role.md" shape applied to roles.
- `spawn-teammate-feature.md` — v15 teammate-conventions integration is one worked instance.
- `consistency-sweep-read-not-just-grep.md` — detecting restatement drift after the fact: grep finds tokens, only reading the prose finds the false restatement.
