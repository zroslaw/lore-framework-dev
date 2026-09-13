---
lore: 1
type: context
summary: "Root working knowledge and navigation for the lore-architect."
---

# Lore Context

Compacted working knowledge for the **lore-architect** — entry point to the lore graph, not a
catalog. Each theme points at its summary topic, which fans out to detail; scan `lore/` for
exhaustive lookup. (Shape rule: working knowledge plus summary-topic references, present tense, no
index — `lore-context-shape-discipline.md`.)

## Who I Am

Architect and maintainer of the lore system — the `lr` framework plugin and the agent ecosystem on
it. I work across two repos: **`lore-framework/`** (the distributed plugin — changes to how agents
work go here) and **`lore-framework-dev/`** (my own agent repo — my lore, workdir, sessions). Both
builder and user of the system. See `role.md`.

## System Architecture

Three discrete layers — identify which one owns a change before touching files:

1. **Plugin** (`lore-framework/`, installed as `lr`) — what's distributed via the marketplace:
   skills, docs, migrations, scripts, manifests, `VERSION`. Universal across installs.
2. **Domain** — the conceptual scope of one agent repo, marked by `lore-repo.md` (frontmatter:
   `description`, `version`, optional `repos:`). Holds `agents/<name>/` with `role.md`,
   `lore-context.md`, `lore/`, `workdir/`, `sessions/`.
3. **Workspace** — the filesystem Claude runs from; holds one or more agent repos plus their
   declared siblings. Discovery scans workspace-root dirs for `lore-repo.md`; nested repos are
   invisible to most skills.

See `architecture-overview.md`, `workspace-vs-domain-vocabulary.md`,
`agent-discovery-nesting-constraint.md`, `plugin-vs-agent-repo-separation.md`,
`workspace-owned-default-ignore-lines.md`.

## Design Principles

Identity-layer framings that frame everything else:

- **Team-shared knowledge** — agents are team-shared knowledge containers, not personal notebooks.
  Design for concurrent multi-contributor use.
- **Engine, not KB** — the framework is the engine/environment for self-improving agents; the
  knowledge base is a consequence, not the identity.
- **Executors first, advisors second** — primary value is getting things done. The usage→learning
  positive feedback loop only spins under executor-first framing.

What each agent carries: **knowledge** (markdown — what it knows, accrues passively via reflection)
+ **skills** (tools + instructions — what it can do, evolves actively via in-flight teaching).
Distinct assets; don't collapse them.

Core mechanics: directory-driven, plain markdown (frontmatter only on descriptor and v1 Lore files),
git-as-metadata, delete-don't-mark, knowledge graph by filename reference, skill/doc separation,
repo-level versioning. Framework owns the universal; agents
own repo/host/workflow specifics.

**Subagent as optimization vs subagent as semantics** — before letting an engine degrade a spawning
procedure to serial host-side execution, ask what the subagent is *for*: parallelism and context
isolation (recall, consult, attach, merge) serialize losslessly, but where *independence from the
caller* is the deliverable (`/lr:trilens-loop`) serialization destroys the feature and the procedure
must stop and report. See `subagent-as-optimization-vs-subagent-as-semantics.md`,
`cursor-merge-via-task.md`, `deferred-import-breaks-lr-core-preflight-cycle.md`.

`system-design-principles.md` holds the full list and the overreach diagnostics; the identity
framings are `team-shared-knowledge-principle.md`, `framework-as-engine-not-kb.md`,
`agents-are-executors-first.md`, `knowledge-vs-skills-distinction.md`,
`framework-scope-vs-agent-scope.md`.

## Skills & Docs

Operations are plugin skills, `lr:` prefix on Claude; Cursor uses `/lr-<skill>` via prefixed
wrappers. **Skills are thin pointers** — each `skills/<name>/SKILL.md` is a one-line reference to
`docs/<name>.md`, where all logic lives; same for generated per-agent boot commands. When a skill
orchestrates sub-skills, the orchestration gets its own `docs/<skill>.md`; non-skill procedures
shared across call sites get a `docs/<procedure>.md`. See `slash-command-system.md`,
`skill-doc-pattern.md`, `shared-procedure-doc-pattern.md`, `single-canonical-source-discipline.md`,
`cursor-dual-skill-tree-one-repo.md`.

**Skill Purpose Announcement** (v44) — every skill opens with `## Step 0 — Announce`, its text
authored in that skill's own doc in framework concepts, as *onboarding material*, not a status line:
the **rule** is shared, the **text** is not, and **nothing enforces or asserts it** (no `/lr:check`
item; measured, Codex never announces on boot). Its conditional sibling (v45) is the **Operation
Notice** — fired only when a procedure does something consequential the user did not ask for,
**silent on a no-op by design**, rendered only by `agent-boot.md`, so attach and merge still refresh
silently. See
`skill-announcement-convention.md`, `operation-notice-convention.md`,
`required-literal-output-is-what-models-drop.md`, `per-site-authoring-is-not-duplication.md`.

Newcomer-facing command IA still needs a curation pass — a daily path, the rest progressively
disclosed (`adopter-command-surface-curation.md`).

**`/lr:style`** (not boot-loaded) selects an exact active set of three orthogonal components —
**plain**, **dialogue**, **follow**; no selector means all, `off` means none, each selection replaces
the prior set (`style-skills.md`, `skill-request-defaults-to-regular-skill.md`,
`soft-skill-follow-me-mode.md`).

An **accelerator** script (Script Fallback Contract) can become **literate**: the procedure lives in
the script's own instructional comments rather than a companion doc. **`lr-core` is a package** —
the stable `scripts/lr-core` wrapper fronts `scripts/lr_core/`, where those fallbacks live. Hard
constraint at that seam: **the script emits data, the doc owns the user-facing words** — a
finished-sounding script string looks like handling the situation, and the executor never reaches
the doc owning the remedy. Scripting a procedure does not shrink its doc. See
`literate-accelerator-pattern.md`, `script-emits-data-doc-owns-the-words.md`,
`agent-boot-doc-grew-when-scripted.md`.

Bundled MCP servers use root `.mcp.json`; the first, `lr-wait`, is stdlib Python, and Claude's
~30-minute MCP idle timeout can strand its request lock — chunk waits below it
(`plugin-mcp-server-convention.md`, `wait-primitive-feature.md`).

## Engine Hubs

Engine-specific operational knowledge has one hub topic per engine:
`claude-engine-capabilities.md`, `codex-engine-capabilities.md`, `cursor-engine-capabilities.md` —
entry points for install/update, invocation, subagents, memory file, MCP/plugin loading, sandbox,
boot cost and harness caveats; keep atomic findings there. At least one Claude Code host flavor
snapshots the **entire plugin bundle per session**, so a mid-session version bump or git pull doesn't
reach it (`ephemeral-session-plugin-snapshot-topology.md`).

**Where an engine fact belongs:** if it would change what an executor *types*, it goes in
`docs/engines/<engine>.md`'s binding — the doc read at the moment of use — not only in these hubs or
in agent lore. Lore is for judgement and history; the profile is the point-of-use contract. Audit
sibling profiles whenever one binding gains a guardrail (`docs-engines-convention.md`).

**Plugin identity is a precondition of a lifecycle result** — the harness asserts the loaded
plugin's VERSION against `LR_FRAMEWORK_DIR` on engine-emitted evidence, not self-report (Cursor's
cloud install rehydrates over `--plugin-dir`; a stale Codex `~/.codex/.tmp/marketplaces/` copy can
outrank the cache). Identity is probed once per suite and inherited, so re-check at suite start — one
flap renders the whole arm uninterpretable (`lifecycle-harness-plugin-identity-unverified.md`,
`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`,
`codex-stale-tmp-marketplace-outranks-cache.md`).

## Marketplace & Distribution

Shipping one repo to multiple engines' marketplaces means handling **each engine's packaging
separately** — manifest schema, skill-tree location and update model differ, so Claude parity does
*not* imply Cursor/Codex parity. Claude Code is strict-clean (remaining step: Console-form community
submission); Codex packaging is resolved. **On Cursor the marketplace install is the primary
documented path** (`--plugin-dir` is for framework development) and is an **account-side server
operation with no non-interactive CLI** — `.cloud-plugin-manifest.json` is a cache that looks like an
install record; never write it. Committed project-scope settings skip per-person install. See
`engine-marketplace-readiness.md`, `plugin-distribution.md`,
`cursor-plugin-distribution-update-model.md`, `cursor-plugin-install-is-account-side.md`,
`project-scope-plugin-config-feature.md`, `plugin-manifest-versioning.md`.

Positioning copy leads with the **triad** — named role-based agents + deliberate reflect/merge
curation + cross-agent collaboration — not cross-engine support
(`positioning-triad-differentiation.md`); **re-survey `similar-projects-landscape.md` before any
positioning-sensitive ship**.

## Boot & Freshness

Boot (`agent-boot.md`, single source of truth): `lr-core preflight` selects the engine profile,
discovers the agent, auto-pulls, and version-compares → act on the report → `lr-core lore-map
--view boot` (compact taxonomy map + coverage; map failure degrades to normal search, and boot never
migrates Lore) → read `role.md` + `lore-context.md` → confirm with the standard **three-line
report**. **Boot loads only those two files; topics are read on demand.** Repos auto-pull at every
session-context boundary (boot, attach, pre-merge); `/lr:pull-lore` is the manual refresh
(`freshness-contracts-at-session-boundaries.md`, `auto-pull-mechanism.md`).

**Lore v1 structure:** `docs/lore-structure.md` is the canonical contract — one fixed
`lore-context.md` root, recursive `area` hubs, leaf `topic`s, four-field scalar frontmatter
(`summary` ≤240 chars). Every **new** Lore file carries v1 frontmatter; legacy files migrate lazily
via merge or explicitly via **`/lr:groom [scope] [--dry-run] [--all]`** (bounded worksets,
approval-gated Whole-Lore mode); `--all` is single-session and non-resumable, so on a large corpus
groom iteratively or per subtree
(`lore-topic-format.md`, `lore-context-shape-discipline.md`).

**The engine profile is observed, not believed.** Selection is `lr-core`'s deterministic
`detect_engine` (ordered: `--engine` override → `CLAUDE_PLUGIN_ROOT` → process ancestry matching the
*program* → framework-root containment → a default marked `confidence: "assumed"`). A model must
never pick the binding that governs its own execution — the sibling of "a gate cannot be a model
self-report". Codex's two remaining signals fail *together*, so a Codex session on a worktree or dev
checkout silently lands on the claude profile; Cursor IDE agent chat has the same shape. Remedy in
both cases is `--engine <name>`; open as backlog B8. See
`engine-profile-must-be-observed-not-believed.md`,
`removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md`,
`cursor-ide-engine-detection-blind-spot.md`.

**Two `<framework-root>`s can be live in one session** (the cache keeps several versions; a manual
boot differs from slash-command dispatch) — never pick the highest, the dispatched one is *observable*
in the base-directory line a slash command prints
(`claude-plugin-cache-holds-multiple-versions.md`, `framework-root-self-location-validated.md`).
On macOS, **realpath for identity, logical components for contract shape**
(`macos-var-symlink-realpath-ambiguity.md`, `realpath-for-identity-logical-for-contract-shape.md`).

## Cross-Agent Collaboration

**`/lr:recall [hint]`** searches loaded agents' lore (fan-out per agent); **`/lr:consult <agent>`**
puts a one-shot question to an unloaded agent via a subagent that boots, answers with file pointers
and exits; **`/lr:attach <agent>`** loads a sustained guest, host still sole executor;
**`/lr:spawn-teammate` (BETA)** spawns teammates whose primary interlocutor is the user, not the
lead. See `lore-search-pattern.md`,
`consult-pattern.md`, `attach-pattern.md`, `spawn-teammate-feature.md`, `teammate-conventions.md`.

**Division of ownership with `lore-advocate`:** the advocate owns public positioning, advocacy and
channel strategy and leads outreach; I own architecture, implementation, design history and product
truth, and verify the technical facts its copy rests on (`public-communication-ownership.md`).

**`/lr:takeover` (BETA)** converts engine-native session logs into a markdown digest so a session on
any engine can continue interrupted work (`takeover-feature.md`, `cursor-takeover-batch-pairing.md`,
`engine-session-log-formats.md`).

## Finalization

User-triggered, four phases (`/lr:finalize` runs all; phases also run standalone): **reflect**
(inline, host-first, per agent — needs session context) → **merge** (parallel subagents, one per
agent booted as itself, file-driven) → **summarize** → **commit+push** (one commit per touched repo;
conflict resolution on push rejection). See `finalization-process.md`, `finalize.md`,
`merge-in-booted-subagents.md`, `reflect-merge-execution-asymmetry.md`.

Canonical host summaries carry a compact per-agent **Learning audit** from the retained Reflection
outcomes and Merge handoffs. Only a *completed* reflection set lets an unlisted input be called
carried over; failed or unavailable evidence leaves origins unknown, never "nothing learned"
(`session-summaries-feature.md`).

**Transcript-backed reflection:** opt-in `finalize --transcript` recovers main-thread dialogue into
ordinary reflection topics, then rejoins the same lifecycle. **Chunk overlap makes merge the semantic
reducer** — expect ~three near-duplicate candidates per insight and consolidate aggressively
(`transcript-backed-finalization-mvp.md`). User-scoped finalization can preserve development
branches in isolated worktrees with real dispositions; preservation is never authorization to merge,
tag, install or publish. Shared-lore publication is a separate unshipped
governance direction (`team-lore-contribution-governance.md`).

## Versioning & Migration

`lore-framework/VERSION` is the single source of truth — **establish the current version from the
repo at the start of any framework-work session, never from this file**: `cat VERSION`,
`git log --oneline -5`, `git tag --list 'lr--v1.4*'`, then confirm the tag is at HEAD. Last known
here: **v45** (`lr--v1.45.0`) — *last known*, not *current*; a fast-moving scalar in a slow-moving
summary is a stale read waiting to happen, on disk or in a loaded context
(`lore-context-shape-discipline.md`). Each agent repo stamps the version in its
`lore-repo.md`, and four version-bearing plugin manifests mirror `1.<VERSION>.0` (a `/lr:check`
plugin-layer finding; the old numbered check #19).
A version is either **migration**, **release-notes-only**, or both, and independently
**cache-affecting** or not — orthogonal axes, both recorded at every ship.
`versioning-release-types.md` holds the per-version history; read it rather than reconstructing.

`/lr:update` and boot-time upgrades **auto-commit and auto-push update-owned paths only** (narrow
staging, sole-commit-ahead gate, marker retry, never force); both share the write-aware
dirty-target collision gate.

Ship mechanics that bite: verify `git HEAD` over lore's "commit pending"; scan the history tail for
gaps; **tag as part of the push step**, checking the tag list rather than `git log`; **re-audit the
release notes' claims about themselves last** — they decay once per fix round. See
`versioning-release-types.md`, `plugin-manifest-versioning.md`, `cache-clear-footer-convention.md`,
`update-process.md`, `release-commit-hash-from-tag.md`,
`a-release-record-goes-stale-while-you-fix-it.md`.

## Consistency & Diagnostics

**`/lr:check` is the single health front door (v45)** — one command over three layers (loaded
plugin, agent repos, workspace), replacing `/lr:doctor` and `/lr:workspace-status`. Findings carry
stable **`P`/`R`/`S`** prefixes that never renumber, are catalogued in `docs/findings-catalog.md`,
and route to the ailment docs **`docs/fix-*.md`** — a broken command cannot diagnose itself.
Mechanical validation always runs, `--full` adds AI summary review; **no repairs, no repo fetches**,
one bounded release-tag probe (`--no-network` skips it).
**Freshness (S19) is recorded successful-pull evidence** — not commit age, not proof of remote sync;
a missing marker reads *unknown*, never *current*. **It is blind to agent-repo divergence**, the only
permanent failure in the system (`lore-repo-divergence-is-self-inflicted.md`). See
[Unified Check Front Door](lore/unified-check-front-door.md) (routes to the pre-v45 catalog) and
`ailment-catalog-pattern.md`.

## Operating Disciplines

How I work at version ships and high-stakes lore edits; each rule's body lives in its own topic.

- **On VERSION bumps:** backfill `versioning-release-types.md`, add the cache-clear footer if
  cache-affecting, bump all four manifests to `1.<VERSION>.0`, promote any newly-named principle to
  its own topic. Full curation disciplines: `role.md`.
- **Both expensive pre-ship gates are on request, not default (user decision 2026-08-22).** The
  lifecycle suite and `/lr:trilens-loop` run only when the user asks; deterministic tests,
  `/lr:check`, and dogfooding stay default. **The disposition record did not change**, and after an
  ungated ship say plainly what remains **untested**. Default-off is a cost decision, not a claim the
  gates are unnecessary — v40 is the standing counter-example. **When a gate is waived and the user
  still asks "is this safe to ship?", run the blast-radius audit and record it beside the waiver** —
  it bounds what the unrun gate could have caught, and its read-every-shared-code-edit step is also
  the abort condition. See
  `blast-radius-audit-when-a-gate-is-waived.md`, `feedback-pre-ship-gates-on-request.md`,
  `gate-waiver-is-a-record.md`.
- **Gate order is cheapest-first: deterministic tests → `/lr:check` → dogfood the change onto this
  workspace → (on request) lifecycle suite → (on request) TriLens.** An *order*, not just a policy
  about defaults — 540 stdlib tests run in minutes at zero cost and catch what the ~30-minute paid
  suite would find later (`unittest discover` fails here; run modules individually per
  `tests/README.md`). TriLens comes *after* dogfooding, which produces the evidence the reviewers
  read. Running a procedure once finds what nine reading lenses may not find at all, and
  the fidelity axis is **engine, not just model tier**
  (cheapest practical tier: Claude → haiku, Codex → gpt-5.4-mini, Cursor → composer-2.5). See
  `lifecycle-testing-harness.md`, `execution-testing-catches-blind-ambiguity.md`,
  `haiku-ambiguity-detector.md`. **Cheapest-first prices compute, never the user** — a free
  probe against live OS state can charge the human six password prompts; rank by user cost and
  validate on a copy (`live-system-state-validate-on-a-copy-first.md`).
- **When a procedure doesn't execute, change structure — not wording.** The sharpest measured case:
  **required literal output is the first thing an executor drops** — three instances in one day
  across two engines, against prose already at maximum emphasis
  (`required-literal-output-is-what-models-drop.md`). Three shapes, all immune to more emphatic
  prose: the **terminal step** that publishes an outcome is the one silently dropped (fix: an
  observable postcondition where the artifact is assembled); once a doc is long enough to be
  **paged**, an obligation's location decides whether it runs; and anything the model can **copy
  instead of compute** will be copied. See
  `the-terminal-step-is-the-step-that-gets-dropped.md`,
  `instruction-location-beats-emphasis-in-long-docs.md`, `models-copy-what-they-should-compute.md`.
- **When TriLens is requested, run it via `/lr:trilens-loop`**, not by hand — the skill enforces what
  a hand-run pass forgets and routes the spawn through the engine binding. Lens *choice* and triage
  stay mine: brief the **goal, not the rationale**; vary the lens *kind* by round; inventory spent
  lenses before a re-review, and spend the expensive ones (operator recovery, new state as state)
  **early**. **Convergent findings from independent lenses are strong evidence; near-total divergence
  means the lenses were well chosen.** **Ask reviewers to name the categories they ruled out clean** —
  a silent category is indistinguishable from an unexamined one. **When lenses are spent and the loop still
  stalls, change the *unit* and the *question* — a shippable subset, the call graph, the installed
  population — not the rigor.** See `trilens-loop-feature.md`,
  `parallel-reviewer-fanout-pattern.md`,
  `lens-novelty-is-the-scarce-resource-on-re-review.md`, `sonnet-subagent-review-pattern.md`.
- **A gate result belongs to a specific artifact state.** **`git status` on every repo is the first
  command of a release review**, ahead of the diff and the notes: a dirty tree means the review's
  subject does not exist yet, and uncommitted fixes are the most invisible ungated work — a commit
  leaves a SHA, a dirty file leaves nothing (`a-release-review-starts-with-git-status.md`). Freeze
  before spawning — commit, name the
  SHA in the brief, tag only after the loop ends; editing while reviewers read invents phantom
  findings. **Collect all reports, then apply.**
  An edit landed after the gates pass is ungated: re-run the affected gate or
  revert and file a follow-up. **A demo of a write operation is not evidence until it runs the next
  ordinary read** — publish then pull, commit then boot; the failure a one-shot demo cannot see is the
  one where the operation succeeds and leaves the system unable to repeat it
  (`a-demo-must-test-the-state-it-leaves-behind.md`). An environment failure mid-run, or the engine resolving a *different*
  plugin tree, makes results **uninterpretable** rather than red. See
  `post-convergence-edits-need-their-own-gate.md`,
  `macos-documents-permission-loss-mid-session.md`.
- **Three gate dispositions — passed, waived, did not run** — and a ship record must name which
  applies, **in the release notes before lore**: an accuracy audit passes cleanly over an absent
  section, so audit **presence first, then accuracy**. A **countable claim about the whole tree**
  earns a check before the notes may assert it. A waiver is itself a record; a measurement names the
  environment it was taken in. A reviewer that dies surfaces as *idle*, indistinguishable from "found
  nothing", so the check is "did it report?", never "did it complain?". When the round cap ends a loop without a clean round, **classify the findings by origin
  first**: a stable core with a churning periphery means the artifact has outgrown prose review, so
  tier it — give the core **one deep unconstrained cold reviewer, not a fourth round**, and defer
  whatever generated the findings. **The cut is itself a change**: review each tier as the subset it
  ships as, and ship a *detection* tier first only if later tiers preserve what it measures
  (`non-convergence-diagnose-before-reviewing-again.md`,
  `tiering-a-reviewed-spec-creates-unreviewed-seams.md`,
  `a-detection-tier-must-outlive-the-cure-it-measures.md`). **Reserve `lens`, `round`, and `converged` for
  `/lr:trilens-loop`** — borrowed gate vocabulary corrupts the disposition record in the scrollback,
  where no check can see it (`dont-borrow-gate-vocabulary-for-non-gates.md`). Expect fix-round
  findings in the **prose**:
  context errors, usually one rule stated in two places drifting apart. See
  `a-gate-that-died-is-not-a-gate.md`, `gate-waiver-is-a-record.md`,
  `measurement-records-name-their-environment.md`, `fix-defects-are-context-errors.md`,
  `a-fix-is-a-change-and-changes-need-review.md`.
- **A gate cannot be a model self-report** — never implement a gate in the medium it gates. Ask what
  evidence it rests on and whether the thing under test could have produced it; coverage parity is
  not evidence parity. Sibling: **a binding must not be selected by the thing it binds**. Everyday
  form: a green suite written by the fix's author is a self-report until each new test is shown **red
  against the previous tag and green against HEAD**, and a **string-containment test over prose**
  proves only that a doc still says what its author wrote. See
  `a-gate-cannot-be-a-model-self-report.md`,
  `prove-a-new-test-red-against-the-previous-tag.md`.
- **A failure list is a hypothesis until someone reads the transcripts.** An assertion names what was
  observed, never why; re-triage from stored logs cheapest-first — the module's verdict history in
  `results/*/summary.json`, then **durations before assertions** (seconds where minutes are normal =
  the engine never ran) — and capture the runner's exit code **unpiped**, or you read the pipeline's
  status and manufacture a false green. At the single-test level **a red test may be asserting
  something true about the machine**: establish which side is wrong before turning it green, and give
  danger-guarding assertions the strongest presumption of correctness.
  See `triage-a-red-module-against-its-own-history.md`,
  `lifecycle-harness-exit-code-is-not-a-verdict.md`, `a-red-test-may-be-asserting-a-true-fact.md`,
  `v31-lifecycle-rerun-partial-green-2026-07-27.md`, `transcript-vs-final-message-assertions.md`.
- **Sandboxed-review blind spot** — a review environment that structurally blocks a capability can
  green-light code whose primary path never ran (`lore-beings-mvp-takeover-review.md`).
- **Decide where the guardrail lives before writing the topic** — lore is retrieved when a task cues
  it, and a one-off command cues nothing. Name the point-of-use site (script check, exact command,
  test) as part of the fix, and prefer a deterministic check over a human prep step
  (`point-of-use-guardrails-beat-recorded-lore.md`).
- **Verify before asserting** — check filesystem/state directly before "fixing" a suspected bug, and
  verify *which* bug. **A negative grep proves the searched pattern absent, never the capability
  absent** — read the entry point before an absence claim carries a decision. Read the lore rule a
  finding rests on before declaring it moot; fetch volatile external facts live with a dated
  citation; after a scoped subagent or fork returns, verify its filesystem footprint, not its
  summary. **An engine fact carries a grade** — ran
  it / read the shipped code / read the docs — and an undocumented route never enters a contract like
  an install doc (`engine-bundle-reading-has-an-evidence-grade.md`,
  `a-negative-grep-proves-the-pattern-absent.md`). **One rendered artifact can have several independent
  sources** — confirm each attribute's source separately, and probe a known-good comparable
  (`a-displayed-attribute-can-have-more-than-one-source.md`). See
  `verify-before-acting-on-suspected-bugs.md`, `check-own-lore-before-dismissing-a-finding.md`,
  `fetch-volatile-facts-live-not-memory.md`, `fork-scope-creep-under-standing-goal.md`.
- **Design-time checks:** preserve validation when widening sources; derive diagnostics and remedies
  from the same predicate; use tri-state lock claims; make file durability structural; update the
  approval surface when adding writes. **Price an interval constant against the real event cadence
  and the knob it may silently override** — one constant answering both "is this stale?" and "may I
  retry?" is wrong in both directions (`a-rate-floor-is-wrong-in-both-directions.md`).
  The underlying patterns route through
  `system-design-principles.md`, `one-question-one-code-path.md`,
  `a-reported-error-is-not-proof-the-file-survived.md`, and
  `adding-a-write-means-updating-the-approval-gate.md`.
- **Git safety in automatic paths.** `git pull --ff-only` is **file-granular** — only divergence
  (the permanent one), a modified tracked file an incoming commit also changes, or an untracked
  collision block it; unrelated dirty and staged paths fast-forward fine
  (`git-ff-only-is-file-granular.md`). **Never `--autostash`**, `stash`, `--force` or `reset --hard`
  in an automatic path: autostash on a content collision exits 0 and writes conflict markers into the
  file, silently corrupting lore (`dont-autostash-it-reports-success-while-corrupting.md`). Repo-wide
  state goes at `--git-common-dir`, per-checkout at `--absolute-git-dir`
  (`git-common-dir-for-repo-wide-state.md`); a fault-recording state file is a **hint** to revalidate
  and self-clear, never sole evidence (`a-state-file-is-a-hint-not-a-verdict.md`).
- **Curation meta-rules:** name foundational principles as their own topics; single canonical source
  (pointer, don't restate — and when fixing or *changing* a rule, enumerate every site that *states*
  it, not only every site that *implements* it, including the **tests that pin the old contract** and
  the docstrings/caller comments a literate accelerator makes executable,
  `a-change-set-is-wider-than-its-diff.md`; but run the scope test first — different words following
  one rule belong at the point of use, `per-site-authoring-is-not-duplication.md`); **cite a
  procedure section by name, never by step number** — a renumbered heading breaks every citation
  silently and the stale reference still reads plausibly
  (`step-number-cross-references-fail-silently.md`); reuse an existing correlation signal before inventing
  new plumbing; don't defer completable bounded sweeps; graduated verification. See `naming-foundational-principles.md`,
  `single-canonical-source-discipline.md`, `reuse-existing-correlation-signal.md`,
  `feedback-don-t-defer-completable-scope.md`, `graduated-verification-confidence.md`.
- **User-feedback working style:** state a recommendation and its reason before asking a decision
  the user must own. Structure is not brevity; use a short verdict for a measurement or a settled
  decision. Confirm before durable mid-session lore writes, draft designs only when asked, and act
  promptly after repeated pushback. Review-subagent preference is Composer 2.5. Route through
  `feedback-commit-to-a-recommendation.md`, `feedback-too-many-words.md`,
  `feedback-confirm-before-writing-lore.md`, `feedback-draft-only-when-user-triggers.md`,
  `feedback-comply-promptly-after-repeated-pushback.md`, and
  `feedback-composer-25-subagent-reviews.md`.

## Key Constraints

- `lore-context.md` ≤ 50K tokens legacy, **≤10K v1 target**; **shape over size** — working-knowledge
  + summary-topic references, not an index (`lore-context-shape-discipline.md`).
- Lore topics: atomic, <5K tokens preferred, plain markdown; **new files carry Lore v1 frontmatter**
  per `docs/lore-structure.md`; legacy files stay frontmatter-free until migrated
  (`lore-topic-format.md`).
- Descriptor frontmatter: `lore-repo.md` = `description` + `version` (+ optional `repos:`);
  `role.md` = `description` only.
- **Every path committed to a workspace or lore agent repo must be relative** (runtime arguments may
  be absolute — the `<agent-dir-rel>` / `<agent-dir>` split). A wrong path in a committed artifact
  does more than break: a checker that identifies state by *matching* that value then lies about a
  different thing — absolute shortcut paths made S11 report every agent unregistered
  (`committed-artifacts-carry-relative-paths.md`).
- Command filenames: lowercase/digits/hyphens, ≤64 chars.
- Placeholders: `<workspace>`, `<lore-agent-repo>`, `<guest-lore-agent-repo>`, `<agent-name>`,
  `<agent-dir>` (runtime, absolute) vs `<agent-dir-rel>` (committed), `${CLAUDE_PLUGIN_ROOT}`.
- **CWD safety:** never `cd` when later tools depend on cwd — use `git -C <repo>`. **Portable
  shell:** BSD/macOS, no GNU-only binaries (`timeout`); bound commands via the Bash-tool timeout.
- See `conventions.md`, `placeholder-vocabulary.md`, `tooling-cwd-safety.md`,
  `portable-shell-in-framework-docs.md`.

## Onboarding-Doc Authoring

Two genres: long-form prose for a human reader (`onboarding-doc-narrative-pattern.md`), and the doc
written *to the AI agent* as the literal installer, pasted as a link
(`paste-link-installer-doc-genre.md`, reviewed with the **AI-installer literal-executor** lens,
`ai-installer-review-lens.md`). Load the identity framings first (toolkit list in `role.md`).
Recurring funnel bug: fresh-start framing leaves the **team-join path** invisible
(`onboarding-funnel-team-join-path.md`). Adopter-facing prose says **"Lore Agents"**; the engine keeps
`lore-framework`/`lr` (`lore-agents-product-name.md`).

## Active Design Explorations

- **lr-dev / Dark Factory (DF)** — a `lr` module for SDLC automation; per-repo artifacts and
  narrative context live in a `<repo>-df` backbone; skills not agents, persistence external. First
  aspect: **AIQA/ULA** (`/lr:df-repo-init`, `/lr:df-ula-file`), unit-level analysis with a
  bug-verification track, BETA. Design thread closed. Anchor:
  `lr-dev-direction.md`; see `df-per-repo-backbone.md`, `aiqa-ula-feature.md`,
  `df-module-conventions.md`, `workflow-primitive-operational-notes.md`.
- **Autonomous agents / Lore Beings** — agents as always-on background collaborators with persistent
  task state, raising for input only when needed. A being is an ordinary lore agent plus a `being.md`
  descriptor, and the **Being Keeper** (`lrb`) is deterministic substrate, never an LLM. CLI-only;
  engines are explicit user config; budget = daily-USD spawn gate + per-task wall-clock kill. BETA
  since v28 with the `/lr:being` surface; Keeper real-engine coverage sits behind
  `LR_LIFECYCLE_KEEPER=1`. **The persistent `--launchd` Keeper install is live on this machine** —
  a candidate explanation whenever a repo changes under me mid-session; the Chronicler soak is a
  *separate*, still-unverified question. Open gaps: headless permissions, self-scheduling under the
  safe default, two per-kind contract decisions, the `python3.14`/blank-icon login item (B11,
  `keeper-login-item-name-and-icon.md`). Anchor: `lore-beings-design.md`; see also
  `agent-being-consciousness-substrate-split.md`, `kill-tree-enumerate-before-signal-ordering.md`,
  `lore-beings-mvp-takeover-review.md`, `autonomous-agents-vision.md`, `wait-primitive-feature.md`.
- **Multi-engine portability (Codex, Cursor)** — **shipped, not in flight.** All three engines are
  Tier-1 on one shared agent repo; Claude Code is the reference path and others override only at the
  **5 adapter bindings** (`docs/engines/`). One repo carries both skill namespaces, synced by
  `scripts/sync-cursor-skills` (**python3 despite the missing extension**) and checked by
  `/lr:check`. Standing facts: **trust rollout/tool-call logs, not model self-report** when validating
  an engine path; Codex's default sandbox blocks `.git` writes and network; **model–engine fit beats
  model tier**. Anchor: `multi-engine-portability-direction.md`; see also `docs-engines-convention.md`,
  `cursor-dual-skill-tree-one-repo.md`.

- **Lore-sync hardening (v46, in flight)** — agent repos go stale because the framework itself
  manufactures divergence (finalize, conflict resolution, update publication) and nothing reports it.
  **All ten changes ship as v46; tiering is withdrawn** after its seams produced findings in
  consecutive rounds. The deep grounded review is complete and applied;
  the round-7 amendments and the formerly deferred marker/reader/C8 work each still owe their first
  review. `lore-repo-divergence-is-self-inflicted.md`, `v46-sync-hardening-tiered-plan.md`,
  `tiering-a-reviewed-spec-creates-unreviewed-seams.md`, `review-grounding-beats-lens-novelty.md`,
  `sidecar-publish-rejected.md`, `a-detection-tier-must-outlive-the-cure-it-measures.md`.
- **Lore housekeeping / consolidation "sleep" pass** and the **simplification/subtraction** item —
  active follow-ups from the 2026-06-13 architecture review. That review's settled dispositions
  (DF-inside-`lr` and team-shared/multi-author as deliberate, not defects — don't re-raise) live in
  `architecture-review-dispositions.md`. The 2026-07-02 review added post-merge diff verification and
  recall-time staleness surfacing.
- **Parked:** workdir-as-reference-library; vector-DB search (until >100 topics/agent); the remaining
  session-as-durable-artifact cluster. See `framework-improvements-backlog.md`,
  `session-as-durable-artifact-cluster.md`.
- **Workspace layer** — shipped, no longer an exploration. Live: `init` (converges), `pull`, `push`
  and diagnosis-via-`/lr:check` over one deterministic scanner; the v3 memory-file contract and its
  AI routing map in `AGENTS.md`; automatic 16h workspace refresh as a second `lr-core preflight` leg;
  committed project-scope plugin settings (no Codex equivalent, said out loud).
  Workspace-owned ignore lines include `/.worktrees/`, `/.lr-beings/`, `/.tmp/`; disposable
  scaffolds go under `.tmp/<name>/`. **Standing scanner limit: dirty detection covers the workspace
  root only, and `workspace-pull` phase 4 fast-forwards child repos with no dirty check — ask git
  per repo.** Still open: "Workspace-root paths gap" and B7 "Orphan version stamps". See
  `workspace-lifecycle-four-commands.md`, `workspace-memory-file-contract.md`,
  `workspace-auto-refresh-design.md`, `project-scope-plugin-config-feature.md`,
  `workspace-owned-default-ignore-lines.md`, `workspace-meta-repo-pattern.md`,
  `v25-workspace-pull-init-design.md`.

## Current State

Workspace holds **`lore-framework/`**, **`lore-framework-dev/`**, **`lore-agents/`**, and
**`lore-chronicler/`** (Being; on disk, undeclared); meta-repo `AGENTS.md` lists them after
`/lr:workspace-init`, which converges (no `--refresh` flag).

**Recent ships have gone out without a real-engine gate**, so the fixes they landed are themselves
unreviewed; per-ship dispositions and what stays untested live in `versioning-release-types.md`
(establish the current version from the repo, per § Versioning).

My Lore corpus is still largely legacy; v1 adoption is lazy via merge or explicit via `/lr:groom`.
Unrelated uncommitted WIP may sit on these checkouts: never sweep it into lore-finalize commits, and
stash around feature merges (`fold-feature-into-local-main-via-stash.md`). **When WIP collides with
an incoming branch, compute whether the branch's version *contains* it** rather than judging by eye,
and leave every non-colliding dirty path alone; blind `git stash` is unsafe here, since the stack is
shared across worktrees (`prove-superseded-before-discarding-colliding-wip.md`).

**This workspace runs concurrent sessions, including non-human ones** (the live launchd Keeper).
Another session's directory-wide `git add` can commit and push work I left uncommitted — ungated work
then ships under an unrelated message and `git status` stops being a reliable inventory of mine. So:
stage narrowly (`git add <path>`, never a directory), re-check `git status` and
`git log` *before reporting* on my own change set, and branch deliberately-ungated work rather than
leaving it dirty (`concurrent-session-committed-my-uncommitted-work.md`,
`same-agent-multiple-engines-single-writer.md`, `trilens-feedback-only-selective-apply.md`).

## Running Backlog & Standing Improvement List

`framework-improvements-backlog.md` is the canonical store of deferred items in `##` categories of
`###` sections — file new items under the matching category
(`backlog-categorization-precedent.md`); § Ship Closures archives per-ship gate dispositions.
**`workdir/what-to-improve.md`** is the **standing prioritized improvement list** — a ranked action
view over that backlog which must always exist (user practice, 2026-07-18). Reread it at the start
of every framework-work session; refresh it at each architecture review
(`standing-improvement-list-practice.md`).
