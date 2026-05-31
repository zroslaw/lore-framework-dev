# lr-dev — SDLC Extension (active design direction)

Opened 2026-05-31 with the user. A major new direction: **`lr-dev`**, a module/mode of the `lr` plugin dedicated to development & SDLC automation. North star (user): convert the SDLC into a **dark factory** — software built internally and autonomously by lore agents, fed only inputs plus occasional follow-ups. Same family as `autonomous-agents-vision.md`: autonomous-agents is the *substrate/process* direction (always-on background workers); lr-dev is the *what-they-do-in-software-development* direction. They converge on the dark-factory end state.

**Status: active exploration, not shipped.** This topic is an orienting pointer. The detailed design lives in the drafts and backlog listed under *Where the detail lives* — do not duplicate that detail here. This file is the anchor (analogous to how `autonomous-agents-vision.md` anchors the parked autonomous direction).

## Why QA is the beachhead

First concrete, intentionally-safe feature: **automatically find bugs/inconsistencies and raise unit-test coverage**. QA is the correct beachhead, not just the easy one: a dark factory needs *trustable autonomy*, which needs *cheap automatic verification*. QA is the one SDLC activity that carries its own oracle (tests pass/fail, coverage moves, bugs reproduce) and has near-zero blast radius (tests additive, bug reports advisory). Bootstrap autonomy on the activity that checks itself.

## Key framings introduced (promote to standalone topics as they're decided)

- **Three-tier knowledge model** — framework / **repo** / agent. lr-dev adds the middle tier. The cut is objective-vs-subjective: **repo lore = what's true about the artifact** (product + technical + per-file), agent-agnostic, survives onboarding a fresh agent; **agent lore = what the worker learned doing the work**, lost if the agent is deleted. Repo lore is the maximal expression of `team-shared-knowledge-principle.md` — knowledge that belongs to the team's artifact, not to any one worker.
- **lr-dev as mode + two-gate capability** — writing repo lore requires (Gate A: repo is lr-dev-enabled, signaled softly in the source repo's `CLAUDE.md` pointing at the repo-lore remote) ∧ (Gate B: agent is in lr-dev mode, permanent via `role.md` or temporary via `/lr:dev-on`). Else read-only. **Mode = loaded operating context + acknowledged capability, like boot — not a persisted flag; enforcement is by-convention**, consistent with the framework's agent-driven nature (cf. `agents-are-executors-first.md`). lr-dev mode is a behavioral overlay: unlocks repo-lore writes, extends finalization to repo lore, exposes the feature skills.
- **Repo-lore structure** — separate repo *now* → mergeable into the source repo's `lore/` later; new descriptor **`dev-repo-lore.md`** (frontmatter `version` + `source-repo` remote; its filename is the discovery marker for the new repo *kind*, parallel to `lore-repo.md`). 2-level product/technical taxonomy, **stored separately, no cross-duplication**, with `product-lore-context.md` / `tech-lore-context.md` entry points. **Per-artifact `.lore.md` mirror** — sparse, lean, refers *up* to category topics; freshness via finalization-on-touch.
- **lr-dev as a growing feature catalog** — capabilities accrete by accretion discipline, same shape as `ailment-catalog-pattern.md` (open-ended, additive, each member potentially a complex multi-workflow feature). First feature: bug-finding & coverage.
- **Test scenarios as a bidirectional IR** — what-to-test (framework-agnostic scenarios) decoupled from how (test code). Forward: scenario→code; reverse: code→scenario (gap analysis). **Coverage ≠ meaningfulness guard:** every "expected" must cite its source of intent (product lore), or generated tests merely canonize current/buggy behavior.
- **Multi-lens review promoted to a reusable skill** — the user independently reinvented `parallel-reviewer-fanout-pattern.md`; promote it to an lr-dev skill (`lr:dev-review`) usable for any code change. The quality workflow is its first consumer. This is the framework's existing finalization-review pattern graduating into a user-facing capability.
- **Standardized deliverable-format rules** — stable IDs, `class: product|technical` tag, intent-source citation, confidence/status, real counts (the dry-run-summary-counts feedback: populate previews with would-be outcomes, not zeros). Three schemas: test scenario, bug report, file report.

## Where the detail lives

- `workdir/draft-lr-dev.md` — general concept (knowledge model, mode/capability §3 + §3.1 mechanism, repo lore, review skill, integration seams).
- `workdir/draft-lr-dev-quality.md` — first feature: file-by-file workflow (file/unit quality-analyst roles), the three schemas, format rules.
- `framework-improvements-backlog.md` § lr-dev — backlog home; includes the cross-cutting item that **`/lr:update`, boot auto-upgrade, and version-check/auto-pull must walk the new `dev-repo-lore.md` repo kind**, not just agent repos.

## Open decisions (carry to next session)

- `role.md` permanent-mode declaration: frontmatter `extensions: [lr-dev]` (leaning this) vs role-body marker.
- Where File reports physically live + prune-vs-retain.
- Skill-namespacing syntax; mode-switch skill specifics; scenario→code binding; generated-vs-human de-dup; per-artifact staleness between non-lr-dev touches.

## Operational note

The user has a **second, concurrent idea** to explore in a separate session that should carry the essential points from this one — these drafts + this topic are that carry-forward. Next natural concrete move on *this* thread: ground the test-scenario schema on the `My-Turbo-Boost-Switcher` mouse repo.

## See Also

- `autonomous-agents-vision.md` — sibling major direction; same dark-factory end state, different axis (process/substrate vs SDLC activity).
- `team-shared-knowledge-principle.md` — repo lore is its maximal expression (knowledge owned by the artifact, agent-agnostic).
- `knowledge-vs-skills-distinction.md` — the repo/agent lore cut refines the knowledge axis; lr-dev mode is a skills-layer overlay.
- `parallel-reviewer-fanout-pattern.md` — the review pattern promoted into the `lr:dev-review` skill.
- `ailment-catalog-pattern.md` — accretion discipline modeled for the lr-dev feature catalog.
- `framework-improvements-backlog.md` § lr-dev — running backlog, including the migration/repo-kind cross-cutting item.
