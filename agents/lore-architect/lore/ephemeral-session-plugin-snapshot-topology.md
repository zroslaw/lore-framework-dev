---
lore: 1
type: topic
summary: "One Claude host flavor snapshots the whole plugin bundle per session and can serve a stale procedure; the operational rule for detecting and handling the mismatch."
parent: lore/claude-engine-capabilities.md
---

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

**Promoted 2026-08-16.** Second confirmed occurrence (2026-08-16): the snapshot resolved to `VERSION`
31 while the boot-resolved installed root was already at v40 — nine versions behind, with a
**materially obsolete procedure** in the stale `attach.md` (pre-v36 `lr-core` layout, no `--engine`
pass-through, no guest boot-map step). Unlike the first (benign, byte-identical doc) occurrence,
following the snapshot here would have silently executed a v31-shaped procedure. Per the trigger
this topic itself named, the content is now folded into `claude-engine-capabilities.md` § Operational
shape as the canonical summary; this topic remains the atomic record of both confirmed instances and
the operational rule applied (read both `VERSION` files; prefer the boot-resolved root on mismatch;
`diff` the specific doc when the delta matters; say so to the user in one line).

**Open guardrail question:** lore alone doesn't protect here — the cue arrives at slash-command
dispatch, not at a task boundary a session would think to check lore for
(`point-of-use-guardrails-beat-recorded-lore.md`). Candidate point-of-use sites (undecided): a
version-consistency line in the skill self-location preamble, or an `lr-core` check comparing the
invoking skill's root against the booted root. Tracked in `framework-improvements-backlog.md` §
Documentation / Meta.

## See Also

- `claude-engine-capabilities.md` — the hub topic; this snapshot mode's summary now lives in its
  "Operational shape" section, promoted from this topic on the second occurrence.
- `plugin-manifest-versioning.md`, `doctor-stale-plugin-cache.md` — the existing stale-cache
  disciplines this snapshot mode is adjacent to but distinct from (those concern the marketplace
  cache, not a per-session ephemeral copy).
- `macos-case-insensitive-filename-collision-with-memory-files.md` — another host-flavor-specific
  Claude fact recorded the same way (atomic topic, linked from the hub) before being folded in.
- `framework-root-self-location-validated.md` § Operational trap — a related but distinct
  within-session divergence: a manually-pointed boot and a later ordinary slash-command invocation
  resolving to *different* framework roots, with no snapshot involved (each `SKILL.md` self-locates
  independently). This topic is one immutable snapshot taken once, at spawn; that one is
  different-invocations-different-roots by design, from the first invocation of each.
- `point-of-use-guardrails-beat-recorded-lore.md` — why the open guardrail question needs a site,
  not only this topic.
