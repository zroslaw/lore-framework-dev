Design heuristic: before inventing new session-identity or correlation plumbing to answer "which external process/log/session is *this one*, from the inside, with no explicit identity primitive available," check whether an **existing** mechanism already establishes a comparable correlation/identity signal for a *related* purpose — even one designed for a different consumer (human debugging vs. automated pipeline).

## The concrete instance (session-archive feature)

`docs/summarize.md` already generates a fresh UUID (Step 1) purely for record-correlation, and documents (Step 12) that a user can later find the matching native JSONL by `grep -rl "<uuid>" ~/.claude/projects/` — because running the UUID-generation command is itself a recorded tool call that lands the UUID text in the transcript. That was designed as an **after-the-fact, human-run** lookup.

The session-archive feature needed the same "which log is this" answer but **proactively, from inside the same automated procedure**. The fix was to run the identical grep **immediately after Step 1** rather than build a separate discovery/identity mechanism. Payoff: no new session-identity machinery (env vars, PID tricks, engine-specific session APIs), no second parallel identity concept — it composes cleanly with the existing invariant (one UUID everywhere).

## Generalizable rule

Before designing a new "how do I identify X from inside the system" mechanism, search for anywhere the codebase already establishes a comparable correlation/identity signal for a related purpose, and ask whether **running that same signal-producing step earlier / more proactively** solves the new problem too. A signal built for one consumer (retrospective human debugging) often serves another (proactive automated pipeline) unchanged, just invoked at a different point.

## See Also

- `single-canonical-source-discipline.md` — the adjacent principle: don't restate/reimplement, reuse or point to the one true mechanism. This is its design-time cousin (reuse an existing signal rather than invent a parallel one).
- `takeover-feature.md` — where the original UUID-grep correlation trick is documented for its original (manual, retrospective) use case.
- `naming-foundational-principles.md` — the meta-rule licensing this heuristic's own topic.
