---
lore: 1
type: topic
summary: "Every path committed to a workspace or lore agent repo must be relative; the absolute-path shortcut bug also made S11 report every agent unregistered, because a checker matching on a value lies about absence when the value is wrong."
parent: lore-context.md
---

# A committed absolute path publishes local config as shared config

**Rule (user, 2026-08-30): all paths committed to workspace and lore agent repos must be relative.**
Runtime arguments may be absolute; committed artifacts may not.

Found and fixed 2026-08-30, drafted for v44 and **unshipped** (see
[skill-announcement-convention.md](skill-announcement-convention.md) for v44's status). Generated
per-agent shortcuts embedded an **absolute** agent directory. Shortcuts are committed —
`.claude/commands/`, `.codex/skills/`, and `.cursor/skills/` all travel with the workspace repo — so
every registration published one machine's filesystem layout as if it were team configuration.

The user spotted it from the symptom side: "looks like there could be a bug related to the check if
agents are locally registered... related to absolute/relative paths."

## The part that was not obvious

The broken shortcut is the *smaller* half. The larger half:

> **A checker that matches on a value misreports absence when the value is wrong.**

`workspace_scan.shortcut_targets()` identified registration by comparing the shortcut's embedded path
against the agent directory. On a cloned workspace both sides were absolute and from different
machines, so **S11 reported every agent as unregistered** — the shortcut sitting right there in git,
and the diagnostic saying it was missing.

So a wrong value does not merely fail; it makes a *diagnostic lie about a different thing*, and the
lie routes the user to a fix (`register-agent`) for a problem they do not have. Watch for this shape
anywhere a finding is derived by comparing two independently-produced values. One occurrence so far —
it stays recorded here rather than promoted to its own topic until a second independent instance
appears (`naming-foundational-principles.md`).

## Fix shape worth reusing

- **New placeholder `<agent-dir-rel>`, kept distinct from `<agent-dir>`.** One word was doing two
  jobs: an absolute *runtime argument* (`preflight --agent-dir`, correct as-is, never committed) and
  a *committed path*. Splitting the placeholder is what made every call site auditable.
- **The reader accepts both forms** — relative resolved against the workspace, absolute as legacy —
  so a workspace mid-migration reports correctly either way.
- **A relative target found in the user-global `~/.codex/skills/` is skipped, not resolved.** A
  relative path is meaningful only against the workspace containing it; joining a user-global
  shortcut's path onto whichever workspace happens to be open would claim registration falsely.
- **The migration regenerates the artifact rather than substituting the path.** A shortcut old enough
  to carry an absolute agent dir usually carries other retired forms too — this workspace's own
  `lr-tax-advisor-agent.md` also had an absolute `agent-boot.md` path that `/lr:check` #18 already
  rejected and nobody had noticed.

## Ordering lesson

This was drafted one version *after* v43 made a cloned workspace arrive with `lr` already configured
([project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md)). The feature and
its precondition landed out of order: v43 promised a working clone, v44 makes the clone work.

> **When a release's premise is "someone else can now use this," audit what else that person
> receives.** Every committed artifact is part of the promise.

## See Also

- `realpath-for-identity-logical-for-contract-shape.md` and
  `macos-var-symlink-realpath-ambiguity.md` — resolve both sides before comparing or subtracting
  paths; the same comparison seam, a different way to get it wrong.
- `one-question-one-code-path.md` — the sibling failure where a checker and a doer disagree; here a
  single checker disagrees with reality.
- `workspace-lifecycle-four-commands.md` — where S11 and the rest of the finding catalog live.
- `placeholder-vocabulary.md` — home of the `<agent-dir-rel>` / `<agent-dir>` split.
