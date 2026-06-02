**Verification produces a confidence assessment, not a boolean.** When a framework operation checks whether something happened (a pull succeeded, a spawn took effect, a write-set parsed cleanly), the user-surface vocabulary should make the confidence level visible — not collapse to pass/fail. The departure from binary verification is deliberate: real-world checks routinely sit in a middle state where the operation appears to have worked but full verification was unavailable, and the framework should report that honestly rather than guess.

The principle was named in v15 after the third instance accumulated. Per `naming-foundational-principles.md`, foundational framings deserve their own topic before they go on motivating more mechanisms.

## The instances

1. **Parallel reviewer fan-out — graceful degradation (v13 refinement).** Stalled reviewers that returned partial findings before timing out are *additive evidence*, not failed runs. The pattern degrades gracefully: a single non-stalled reviewer plus partials from the others is often enough breadth to ship, with round 2 closing the gap. "Inconclusive" is treated as input to synthesis rather than a hard fail. See `parallel-reviewer-fanout-pattern.md` § Graceful degradation.

2. **Auto-pull — transport-aware outcome ladder (v13/v14).** Boot/attach/pre-merge auto-pull surfaces a multi-state outcome rather than success/failure: success / fast-fail (network) / timeout (stuck transport) / dirty-tree-conflict / unknown. Boot continues in all cases; failure is reported but not fatal. The transport awareness is the v14 refinement — different failure modes get different recovery messaging. See `auto-pull-mechanism.md`.

3. **`/lr:check` #20 — graduated by blast radius (v15).** Three substeps over migration write-paths declarations: section absent, fenced body absent, body content malformed. All three land at error-severity because each failure mode degrades the gate the same way (blanket-dirty fallback or silently-empty write-set). Severity is graduated by blast radius and they all sit at the high end. See `consistency-checks.md` check #20.

4. **`/lr:spawn-teammate` Step 7c — graduated by detection confidence (v15).** Reads `~/.claude/teams/<team>/config.json` after `Agent` returns; backend-aware; race-tolerant. Four states surfaced to Step 8:
   - **`verified-live`** — full check passed (config present + `isActive: true` + backend-specific check passed).
   - **`verified-inconclusive`** — partial check passed (config present + `isActive: true`; backend-specific check N/A for this backend, e.g., non-iterm2 lacks `tmuxPaneId`).
   - **`unverified`** — check failed after 5×~50ms retry on the config-write race.
   - **`spawn-errored`** — `Agent` itself returned an error.

   The middle state (`verified-inconclusive`) is the load-bearing one: it tells the user "we believe it worked, but our backend-specific check doesn't apply here, so we can't promise" — strictly more honest than collapsing to either `verified-live` (over-promising) or `unverified` (under-reporting). See `spawn-teammate-feature.md` § v15 changes.

## The common shape

Every instance has a **first-class "inconclusive" / "weakened" state** distinct from both pass and fail. That third (or fourth) state is where the design move lives:

- It doesn't claim success it can't prove.
- It doesn't fail-loud over conditions that don't actually warrant failure.
- It surfaces the confidence level so downstream code (and humans) can decide.

The departure from binary is what the principle is *about*. Binary verification compresses real-world ambiguity into a yes/no, then forces downstream code to reinvent the missing nuance — typically badly, ad hoc, with vocabulary drift.

## Why the family deserves a name

Future features will reinvent this ad hoc. Vocabulary is already drifting:

- spawn-teammate Step 7c uses `verified-live` / `verified-inconclusive` / `unverified` / `spawn-errored`.
- check #20 uses error/warning (now consolidated to error after a v15 round-5 promotion).
- auto-pull uses success/failure-with-mode.

Each invents its own labels for the same shape. Without the principle named as its own topic, feature authors will default to binary-then-add-an-edge-case-flag — the worst of both worlds. Naming the principle lets future authors plan for an inconclusive state up front, choose vocabulary deliberately, and compose with the existing instances.

## Authoring checklist when adding a new verification surface

1. **Name the inconclusive state explicitly.** Not "kind-of-success." A real label that downstream code can match on. Examples from existing instances: `verified-inconclusive`, `partial-return`, `timeout`.
2. **Document what each state means** in the doc that defines the verification — what conditions produce it, what downstream behavior follows.
3. **Treat inconclusive as additive information**, not a failure to be hidden. Surface it to the user.
4. **Be backend-aware** when the check varies by environment (spawn-teammate's iterm2 vs non-iterm2 split). Failing the backend-specific check should not contaminate the cross-backend signal.
5. **Be race-tolerant** when the check races against a write-side operation. Spawn-teammate uses 5×~50ms retry; pick the equivalent for your check.
6. **Choose severity by blast radius** when reporting graduated failures (check #20's pattern). All three substeps degrade the same way → all at error.

## Connection to existing lore

- **`dirty-tree-gates-write-vs-read-distinction.md`** — adjacent, distinct: that topic is about *whether* to gate; this topic is about *how to report* gate outcomes. The two compose: a gate decides to refuse, a verification decides what confidence to attach to the gate's outcome.
- **`parallel-reviewer-fanout-pattern.md` § Graceful degradation** — the v13 instance, prose only; this topic is the named principle.
- **`naming-foundational-principles.md`** — the meta-rule that says principles deserve their own topic before continuing.
- **`feedback-don-t-defer-completable-scope.md`** — applied during the v15 ship: the topic was promoted on the same finalization, not deferred to v16.

## See Also

- `parallel-reviewer-fanout-pattern.md` — first instance (graceful degradation)
- `auto-pull-mechanism.md` — second instance (transport-aware ladder)
- `consistency-checks.md` — third instance (check #20, graduated by blast radius)
- `spawn-teammate-feature.md` — fourth instance (Step 7c, graduated by detection confidence)
- `naming-foundational-principles.md` — meta-rule licensing the promotion
