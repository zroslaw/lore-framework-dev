# Landing a Sibling Build via Working-Tree Diff (not hand-merge)

A reusable technique for folding a validated change set that lives in a sibling repo/build back
into the canonical repo — without hand-merging dozens of files. Used to land the multi-engine
Codex port from the no-remote `lore-framework-codex` build into canonical `lore-framework` for
v19 (see `port-landing-next-steps.md`, `docs-engines-convention.md`).
Applies whenever a validated change set sits in a sibling that shares a base commit with the target.

## The setup that made it clean

The codex build's working tree was `v17-HEAD + lr-wait (uncommitted) + style skills + port` — i.e.
it already contained v18's changes. The real framework was at committed v18. So:

**`diff -rq <real-v18> <codex-build>`, filtered to content files, isolates exactly the port** —
everything identical (all of lr-wait) drops out; what differs is only port-touched files.

## The safety check that justifies wholesale copy

Before trusting "copy the differing files wholesale," verify the one file that BOTH v18 and the
port modified (`conventions.md`) — confirm the sibling build's copy contains *both* v18's change
(the "Plugin MCP Servers" section) AND the port's change (`<framework-root>`). That proves the
build's working tree is a true superset (v18 ∪ port), so copying its version of each port-touched
file preserves v18's work rather than clobbering it. Without that check, wholesale copy risks
reverting v18 edits in co-touched files.

## Procedure

1. `diff -rq` the two trees, excluding `.git/`, `sessions/`, `workdir/`, `agents/`, `tests/`, and
   the ceremony-owned files (`VERSION`, `README`, manifests, `release-notes/`).
2. Verify a co-touched file contains both change sets (the superset check above).
3. Copy the differing files + any new dirs (here: `docs/engines/`) target-ward.
4. Re-run `diff -rq`; the only remaining content diffs should be the ceremony-owned files.
5. Apply anything the sibling build did NOT carry. Here the defer-clarity fix was staged separately
   (never in the build), so it was authored fresh during landing — see `haiku-ambiguity-detector.md`.

## Caveat

The sibling build deliberately deferred some areas (lr-wait `.mcp.json`, `migrations/*`, df) — they
still carry `${CLAUDE_PLUGIN_ROOT}`. After the copy, grep the target for remaining tokens and
confirm each is legitimate (a detection signal, the claude profile's literal-path fallback, an
"it's empty" note, or a deferred subsystem) rather than an un-ported leak.

## See Also

- `docs-engines-convention.md` — the change set this technique landed into v19.
- `haiku-ambiguity-detector.md` — the separately-staged fix that step 5 caught (not in the build).
- `framework-root-self-location-validated.md` — the bulk of the copied port surface.
- `single-canonical-source-discipline.md` — why folding back to one canonical copy matters.
