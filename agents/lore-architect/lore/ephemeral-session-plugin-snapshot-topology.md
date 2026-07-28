# Ephemeral Session Plugin Snapshot Topology (Claude)

New Claude engine-capability fact, confirmed twice in one session: at least one Claude Code host
flavor — "local-agent-mode-sessions", evidenced by `--plugin-dir` args pointing at
`~/Library/Application Support/Claude/local-agent-mode-sessions/<ids>/rpm/plugin_<hash>/` —
materializes a **full, physically separate snapshot of the entire plugin bundle per session**, not
a reference into the marketplace cache or the workspace checkout.

`${CLAUDE_PLUGIN_ROOT}` is empty in the host session itself when the workspace's `lore-framework/`
is a plain git checkout, but skill/slash-command dispatch (`/lr:boot`, `/lr:reflect`, ...) resolves
through this ephemeral snapshot regardless of that — confirmed via a deliberate subagent probe
(planted a wrong path hint; real dispatch ignored it and resolved the snapshot anyway) and again
when `/lr:reflect`'s own `SKILL.md` self-location pointed at the snapshot mid-session.

## Concrete consequence observed

The snapshot is taken at session start (`VERSION` 31 in this instance) and does **not** update when
the workspace checkout is git-pulled or, as happened this session, locally committed to a new
version (v32) mid-session. For this session the specific doc read (`process-reflection.md`) was
byte-identical between the stale snapshot and the live v32 checkout, so no functional bug resulted
— but it's a live, general divergence hazard: any doc/skill invoked via real slash-command dispatch
mid-session reflects the *session-start* plugin state on this host flavor, not the live workspace
state, regardless of what the workspace checkout does in the meantime.

## How this differs from the already-documented install modes

Distinct from both the marketplace-cache install mode and the plain workspace-checkout install mode
already covered in `claude-engine-capabilities.md`. Those two update (or fail to update) based on
explicit refresh actions (`claude plugin update`, `git pull`); this per-session snapshot mode
doesn't update at all for the session's lifetime, by construction — the snapshot is taken once, at
spawn.

## Status

Recorded as its own atomic topic rather than inlined into `claude-engine-capabilities.md` — this
repo's practice is not to write durable lore mid-session without cause, and this is a single
confirmed instance without an observed design-decision consequence yet. Promote the content into
the hub topic's "Operational shape" section if this recurs, or if a future finalize/version-check
procedure needs to account for it explicitly (e.g., a version-skew check that trusts session-start
plugin state instead of live workspace state).

## See Also

- `claude-engine-capabilities.md` — the hub topic for Claude-specific operational facts; this
  snapshot mode is a candidate addition to its "Operational shape" section on a second occurrence.
- `plugin-manifest-versioning.md`, `doctor-stale-plugin-cache.md` — the existing stale-cache
  disciplines this snapshot mode is adjacent to but distinct from (those concern the marketplace
  cache, not a per-session ephemeral copy).
- `macos-case-insensitive-filename-collision-with-memory-files.md` — another host-flavor-specific
  Claude fact recorded the same way (atomic topic, linked from the hub) before being folded in.
