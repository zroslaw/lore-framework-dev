# Use-cases section via parallel /lr:consult fan-out

Pattern for filling concrete-example sections of onboarding/showcase docs by fanning `/lr:consult` calls out in parallel to the agents that actually did the work.

## When it applies

Any reader-facing section that needs *concrete examples* — use-cases, war-story walkthroughs, "what an agent actually does" anecdotes. The host (typically `lore-architect`) does not have the operational detail; the working agents do.

## Procedure

1. **Map the use-case list to agents.** For each example, identify the 1–3 agents most likely to hold the lore. Multi-agent triages (e.g., Globaltix Calendar) should consult *all* contributors, not just the obvious one — each agent surfaces a different layer (oncall = data plane, supplier-api agent = endpoint semantics, repo-expert agent = code path).
2. **Dispatch consults in parallel, in the background.** Single message, multiple `Agent` calls with `run_in_background: true`. Avoids serialization across what is otherwise 5+ minutes of independent boot+search work.
3. **Brief each consult tightly.** 4-part brief from `consult.md`, plus a structured output shape: 2–4 bullets per use case, with concrete details (ticket IDs, file paths, Slack permalinks, capacity numbers) and pointers to lore topics + workdir artifacts. Ask explicitly for "Nothing relevant" if the consultant lacks material — better than fabricated content.
4. **Weave returns into the doc.** Each subsection labels which agents contributed and what each one supplied. Multi-agent subsections benefit from a one-bullet-per-agent shape — the reader sees how the agents *compose*, which is half the point of the showcase.

## Why this works

- **Authenticity** — the bullets are real, with real ticket IDs and permalinks. No copy-paste from a Confluence page; the content *is* what the agents already know.
- **Self-illustrating** — the doc demonstrates the very feature it's documenting. Adding a "meta" subsection that explicitly names the consults used (host + N consultants) closes the loop reader-facing. See the meta-closer subsection guidance in `onboarding-doc-narrative-pattern.md`.
- **Cheap** — five parallel consults completed in ~120 seconds wall-clock; serial would have been ~5 minutes plus context bloat.

## Caveats observed

- One consultant (oncall-agent) flagged a framing mismatch: the user's original "KKday allowed origins" framing didn't match the actual investigation in lore (which was empty-offers/pax-mismatch). The consult mechanism caught this — the synthesis included an explicit "Nothing relevant under this framing; here's what I actually have" caveat. Honor those caveats when weaving — adjust the doc's framing rather than forcing the lore to fit. **General principle:** consult returns are the ground truth; if the host's framing doesn't match the consultant's lore, the framing is wrong.
- Some material lived in user-memory (`~/.claude/projects/.../memory/`) rather than agent lore. Surface this as a gap to migrate — onboarding docs are a good audit trigger for "lore that should have been written but wasn't."

## Composition with sonnet review

Pre-publication sonnet review (see `sonnet-subagent-review-pattern.md`) is still appropriate for the assembled section before commit, especially for high-stakes onboarding docs. Run it *after* weaving consult returns, *before* finalize.

## See also

- `consult-pattern.md` — the underlying mechanism.
- `onboarding-doc-narrative-pattern.md` — the surrounding doc structure (including §2 use-cases section and the meta-closer subsection that names this fan-out).
- `sonnet-subagent-review-pattern.md` — the pre-publication review step.
