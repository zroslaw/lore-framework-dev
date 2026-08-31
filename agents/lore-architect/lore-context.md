---
lore: 1
type: context
summary: "Root working knowledge and navigation for the lore-architect."
---

# Lore Context

Compacted working knowledge for the **lore-architect** — entry point to the lore graph, not a
catalog. Each theme points at its summary topic, which fans out to detail; scan `lore/` directly for
exhaustive lookup. (Shape rule: working knowledge plus summary-topic references, present tense, no
index — `lore-context-shape-discipline.md`, `process-merge.md` § Step 4.)

## Who I Am

Architect and maintainer of the lore system — the `lr` framework plugin and the agent ecosystem on
it. I work across two repos: **`lore-framework/`** (the distributed plugin — changes to how agents
work go here) and **`lore-framework-dev/`** (my own agent repo — my lore, workdir, sessions). I'm
both builder and user: I use lore to track my own design knowledge. See `role.md`.

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
git-as-metadata, delete-don't-mark, knowledge graph by filename reference, concise context with
detail on demand, skill/doc separation, repo-level versioning. Framework owns the universal; agents
own repo/host/workflow specifics.

**Subagent as optimization vs subagent as semantics** — classify what a subagent is *for* before
letting any engine degrade a spawning procedure to serial host-side execution. If it buys
parallelism and context isolation (recall, consult, attach, merge), serialization is lossless. If
the subagent's *independence from the caller* is the deliverable (`/lr:trilens-loop`), serialization
destroys the feature and the procedure must stop and report. See
`subagent-as-optimization-vs-subagent-as-semantics.md`, `cursor-merge-via-task.md`,
`cursor-task-free-text-brief-validated.md`. A `lr_core` import trap sits under
`deferred-import-breaks-lr-core-preflight-cycle.md`.

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

**Skill Purpose Announcement** — shipped in v44: every skill opens with `## Step 0 — Announce`,
its text authored in that skill's own doc, in framework concepts not internals. Announcements are
*onboarding material*, not status lines; the **rule** is shared, the **text** is not. **Nothing in
`/lr:check` enforces Step 0** — 33 sites, no mechanical guard — and until v45 nothing asserted an
announcement was ever *emitted*: measured, Claude announces on boot 3/3 and **Codex does not at all**
(`test_09_boot_announces_before_working`). Its conditional sibling, drafted in v45, is the
**Operation Notice**: fired only when a procedure does something consequential the user did not ask
for (boot migrating a repo, the workspace auto-refresh), and **silent on a no-op by design**. See
`skill-announcement-convention.md`, `operation-notice-convention.md`,
`required-literal-output-is-what-models-drop.md`, `per-site-authoring-is-not-duplication.md`.

The current skill catalog is implementation ground truth, but newcomer-facing information
architecture needs a dedicated curation pass — organize around a daily path and progressively
disclose the rest. See `adopter-command-surface-curation.md`.

**`/lr:style`** is the single public skill for communication style (not boot-loaded): it selects an
exact active set of three orthogonal components — **plain**, **dialogue**, **follow** — where no
selector means all, `off` means none, and each selection replaces the prior set. See
`style-skills.md`, `skill-request-defaults-to-regular-skill.md`, `soft-skill-follow-me-mode.md`.

An **accelerator** script (Script Fallback Contract) can become **literate**: the procedure lives in
the script's own instructional comments rather than a companion doc — one artifact instead of two
that drift apart. **`lr-core` is a package**: the stable `scripts/lr-core` wrapper fronts
`scripts/lr_core/`, where the literate fallbacks live. Hard constraint at that seam: **the script
emits data, the doc owns the user-facing words** — a finished-sounding script string *looks* like
handling the situation, so the executor never reaches the doc that owns the remedy. Scripting a
procedure does not automatically shrink its doc. See
`literate-accelerator-pattern.md`, `script-emits-data-doc-owns-the-words.md`,
`agent-boot-doc-grew-when-scripted.md`.

The plugin can also **bundle an MCP server** (root `.mcp.json`): **`lr-wait`** is the first, and the
framework's first `python3` dependency (stdlib-only — the sole sanctioned exception to bash-on-BSD,
for protocol-speaking components). Practical limit: on Claude Code a single MCP call dies at the
engine's ~30-minute idle timeout, and the abort leaves `lr-wait`'s single-request lock stuck `busy`
for the session — chunk waits at ≤29 min, or use a backgrounded shell timer. See
`plugin-mcp-server-convention.md`, `wait-primitive-feature.md`.

## Engine Hubs

Engine-specific operational knowledge has one hub topic per engine:
`claude-engine-capabilities.md`, `codex-engine-capabilities.md`, `cursor-engine-capabilities.md` —
entry points for install/update model, invocation surface, subagent mechanism, memory file,
MCP/plugin loading, sandbox constraints, boot cost, and harness caveats. Keep atomic findings in the
linked topics rather than rediscovering them from old session notes. At least one Claude Code host
flavor snapshots the **entire plugin bundle per session**, so a mid-session version bump or git pull
doesn't reach it (`ephemeral-session-plugin-snapshot-topology.md`).

**Where an engine fact belongs:** if it would change what an executor *types*, it goes in
`docs/engines/<engine>.md`'s binding — the doc read at the moment of use — not only in these hubs or
in agent lore. Lore is for judgement and history; the profile is the point-of-use contract. Audit
sibling profiles whenever one binding gains a guardrail (`docs-engines-convention.md`).

**Plugin identity is a precondition of a lifecycle result.** The harness asserts the loaded plugin's
VERSION against `LR_FRAMEWORK_DIR` on engine-emitted evidence, not self-report; Cursor's cloud
install rehydrates over `--plugin-dir` within ~25s of a move-aside, so re-check at suite start
(`lifecycle-harness-plugin-identity-unverified.md`,
`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`). On Codex the tree that wins can be a stale
**`~/.codex/.tmp/marketplaces/`** copy the precheck never enumerates, and identity is probed *once
per suite* then inherited, so one flap makes the whole arm uninterpretable — B10 closed this way
(`codex-stale-tmp-marketplace-outranks-cache.md`).

## Marketplace & Distribution

Shipping one repo to multiple engines' marketplaces means handling **each engine's packaging
separately** — manifest schema, skill-tree location, and update model all differ, so Claude parity
does *not* imply Cursor/Codex parity. Claude Code is strict-clean (remaining step: Console-form
community submission); Codex packaging is resolved. **On Cursor the marketplace install is the
primary documented path** (`--plugin-dir` is for framework development), and install is an
**account-side server operation with no non-interactive CLI** — the local
`.cloud-plugin-manifest.json` is a cache that looks like an install record; never write it. A
workspace can now skip per-person install entirely via committed project-scope settings. See
`engine-marketplace-readiness.md`, `plugin-distribution.md`,
`cursor-plugin-distribution-update-model.md`, `cursor-plugin-install-is-account-side.md`,
`project-scope-plugin-config-feature.md`, `plugin-manifest-versioning.md`.

Positioning copy leads with the **triad** — named role-based agents + deliberate reflect/merge
curation + cross-agent collaboration — not cross-engine support
(`positioning-triad-differentiation.md`), and **re-survey `similar-projects-landscape.md` before any
positioning-sensitive ship**: that space moves in weeks, not quarters.

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
via merge or explicitly via **`/lr:groom [scope] [--dry-run] [--all]`** (bounded ≤30K-token worksets,
read-only halo, approval-gated Whole-Lore mode). `--all` is single-session and non-resumable, so on a
large corpus it cannot complete — groom iteratively or scope it to one subtree
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

**Two `<framework-root>`s can be live in one session** — three causes: Claude's plugin cache keeps
several versions, a manual boot differs from slash-command dispatch, one host flavor snapshots the
bundle per session. Never pick the highest version; the dispatched one is *observable* in the
base-directory line a slash command prints, and booting off the wrong tree is invisible
(`claude-plugin-cache-holds-multiple-versions.md`, `framework-root-self-location-validated.md`,
`ephemeral-session-plugin-snapshot-topology.md`).

`version-check.md`'s nested-repo guard carries a macOS trap: "resolve both to real paths" is not
self-executing prose — a weak model filled the gap with bare `pwd`, which disagrees with git under
the `/var`→`/private/var` symlink. **Realpath for identity, logical components for contract shape.**
See `macos-var-symlink-realpath-ambiguity.md`,
`realpath-for-identity-logical-for-contract-shape.md`.

## Cross-Agent Collaboration

**`/lr:recall [hint]`** searches loaded agents' lore (host + guests, fan-out per agent);
**`/lr:consult <agent>`** puts a one-shot question to an unloaded agent via a subagent that boots,
answers with file pointers, and exits; **`/lr:attach <agent>`** loads a sustained guest with the host
still sole executor; **`/lr:spawn-teammate` (BETA)** spawns agents as Agent Teams teammates whose
primary interlocutor is the user, not the lead. See `lore-search-pattern.md`,
`consult-pattern.md`, `attach-pattern.md`, `spawn-teammate-feature.md`, `teammate-conventions.md`.

**Division of ownership with `lore-advocate`:** the advocate owns public positioning, advocacy, and
channel strategy and leads outreach work; I own architecture, implementation, design history, and
product truth, and verify the technical facts its copy rests on. See
`public-communication-ownership.md`.

## Session Takeover (BETA)

**`/lr:takeover`** converts engine-native session logs into a markdown digest so a new session on any
engine can continue interrupted work (`scripts/session-takeover`). See `takeover-feature.md`,
`cursor-takeover-batch-pairing.md`, `engine-session-log-formats.md`.

## Finalization

User-triggered, four phases (`/lr:finalize` runs all; phases also run standalone): **reflect**
(inline, host-first, per agent — needs session context) → **merge** (parallel subagents, one per
agent booted as itself, file-driven) → **summarize** → **commit+push** (one commit per touched repo;
conflict resolution on push rejection). Do not finalize unless the user triggers it. See `finalization-process.md`, `finalize.md`,
`merge-in-booted-subagents.md`, `reflect-merge-execution-asymmetry.md`.

Canonical host summaries carry a compact per-agent **Learning audit** built from the retained
Reflection outcomes and Merge handoffs. Only a *completed* reflection set lets an unlisted input be
called carried over; failed or unavailable evidence leaves origins unknown rather than becoming
"nothing learned." See `session-summaries-feature.md`.

**Transcript-backed reflection:** opt-in `finalize --transcript` recovers main-thread dialogue into
ordinary reflection topics, then rejoins the same lifecycle. **Chunk overlap makes merge the semantic
reducer** — expect ~three near-duplicate candidates per insight and consolidate aggressively. Design,
bounds and accepted limits: `transcript-backed-finalization-mvp.md`.

Shared-lore publication is a separate, unshipped governance direction. See
`team-lore-contribution-governance.md`.

## Versioning & Migration

`lore-framework/VERSION` is the single source of truth — **establish the current version from the
repo at the start of any framework-work session, never from this file**: `cat VERSION`,
`git log --oneline -5`, `git tag --list 'lr--v1.4*'`, then confirm the tag is at HEAD. Last known
here: **v44** (`lr--v1.44.0`) — *last known*, not *current*. A fast-moving scalar in a slow-moving
summary is a stale read waiting to happen, and a summary can be stale on disk *or* stale in a loaded
context (`lore-context-shape-discipline.md`). Each agent repo stamps the version in its
`lore-repo.md`, and four version-bearing plugin manifests mirror `1.<VERSION>.0` (`/lr:check` #19).
A version is either **migration**, **release-notes-only**, or both, and independently
**cache-affecting** or not — orthogonal axes, both recorded at every ship.
`versioning-release-types.md` holds the per-version history; read it rather than reconstructing.

`/lr:update` and boot-time upgrades **auto-commit and auto-push update-owned paths only** (narrow
staging, sole-commit-ahead gate, `lr-update-pending` marker retry, never force); both paths share
the write-aware dirty-target collision gate.

Ship mechanics that bite: verify `git HEAD` over lore's "commit pending"; scan the whole history tail
for gaps; **tag as part of the push step** — check the tag list, not just `git log`; **re-audit the
release notes' claims about themselves last**, since they decay once per fix round. See
`versioning-release-types.md`,
`plugin-manifest-versioning.md`, `cache-clear-footer-convention.md`, `update-process.md`,
`release-commit-hash-from-tag.md`, `a-release-record-goes-stale-while-you-fix-it.md`.

## Consistency & Diagnostics

Three surfaces, three scopes:

- **`/lr:check`** — content-consistency checks *inside agent repos*, rendering scanner findings
  rather than restating rules; at scale prefer a deterministic script sweep over an LLM read-through
  (`consistency-checks.md`).
- **`/lr:doctor`** — *engine/plugin runtime* issues that escape content checks (esp. stale plugin
  cache), via an accreting ailment catalog (`ailment-catalog-pattern.md`).
- **`/lr:workspace-status`** — read-only diagnosis of the *workspace layer* (git state, descriptor
  drift, memory-file contract, child-repo hygiene), findings S1–S18 each naming its fix
  (`workspace-lifecycle-four-commands.md`).

## Operating Disciplines

How I work, especially at version ships and high-stakes lore edits. Each rule's body lives in its
own topic — these are pointers, not summaries.

- **On VERSION bumps:** backfill `versioning-release-types.md`, add the cache-clear footer if
  cache-affecting, bump all four manifests to `1.<VERSION>.0`, promote any newly-named principle to
  its own topic. Full curation disciplines: `role.md`.
- **Both expensive pre-ship gates are on request, not default (user decision 2026-08-22).** The
  lifecycle suite and `/lr:trilens-loop` run only when the user asks; deterministic tests,
  `/lr:check`, and dogfooding stay default. **The disposition record did not change** (see the three
  dispositions below), and after an ungated ship say plainly what remains **untested**. Default-off
  is a cost decision, not a claim the gates are unnecessary — v40 is the standing counter-example.
  See `feedback-pre-ship-gates-on-request.md`, `gate-waiver-is-a-record.md`.
- **Gate order is cheapest-first: deterministic tests → `/lr:check` → dogfood the change onto this
  workspace → (on request) lifecycle suite → (on request) TriLens.** An *order*, not just a policy
  about defaults — 540 stdlib tests run in minutes at zero cost and catch what the ~30-minute paid
  suite would find later (`unittest discover` fails here; run modules individually per
  `tests/README.md`). TriLens comes *after* dogfooding, which produces the evidence the reviewers
  read. Running a procedure once finds in seconds what nine
  reading lenses may not find at all, and the fidelity axis is **engine, not just model tier**
  (cheapest practical tier: Claude → haiku, Codex → gpt-5.4-mini, Cursor → composer-2.5). See
  `lifecycle-testing-harness.md`, `execution-testing-catches-blind-ambiguity.md`,
  `haiku-ambiguity-detector.md`.
- **When a procedure doesn't execute, change structure — not wording.** The sharpest measured case:
  **required literal output is the first thing an executor drops** — three instances in one day
  across two engines, substance right and the mandated line missing, decorated, or suppressed-rule
  ignored, against prose already at maximum emphasis
  (`required-literal-output-is-what-models-drop.md`). Three shapes, all immune to
  more emphatic prose: the **terminal step** that publishes an outcome is the one silently dropped
  (fix: an observable postcondition where the artifact is assembled); once a doc is long enough to be
  **paged**, an obligation's location decides whether it runs; and anything the model can **copy
  instead of compute** will be copied. See
  `the-terminal-step-is-the-step-that-gets-dropped.md`,
  `instruction-location-beats-emphasis-in-long-docs.md`, `models-copy-what-they-should-compute.md`.
- **When TriLens is requested, run it via `/lr:trilens-loop`**, not by hand — the skill enforces what
  a hand-run pass forgets and routes the spawn through the engine binding. Lens *choice* and triage
  stay mine: brief the **goal, not the rationale**; vary the lens *kind* by round; inventory spent
  lenses before a re-review. **Convergent findings from independent lenses are strong evidence;
  near-total divergence means the lenses were well chosen.** **Ask reviewers to name the categories
  they ruled out clean**, not only what they found — a silent category is indistinguishable from an
  unexamined one. See `trilens-loop-feature.md`, `parallel-reviewer-fanout-pattern.md`,
  `lens-novelty-is-the-scarce-resource-on-re-review.md`, `sonnet-subagent-review-pattern.md`.
- **A gate result belongs to a specific artifact state.** Freeze before spawning — commit, name the
  SHA in the brief, tag only after the loop ends; editing while reviewers read invents phantom
  findings. **Collect all reports, then apply** — broken on v43, and the third reviewer spent its
  opening on my process. An edit landed after the gates pass is ungated: re-run the affected gate or
  revert and file a follow-up. An environment failure mid-run, or the engine resolving a *different*
  plugin tree, makes results **uninterpretable** rather than red. See
  `post-convergence-edits-need-their-own-gate.md`,
  `macos-documents-permission-loss-mid-session.md`.
- **Three gate dispositions — passed, waived, did not run** — and a ship record must name which
  applies, **in the release notes before lore** — a lore-only record satisfies every discipline I
  hold while the user's artifact stays empty (v44 had no Verification section, and an accuracy audit
  passes cleanly over an absent one), so audit **presence first, then accuracy**. Sibling: a
  **countable claim about the whole tree** ("all 33 skills do X") earns a check before the notes may
  assert it — verified once by hand is verified for one commit
  (`a-release-record-goes-stale-while-you-fix-it.md`, `consistency-checks.md`). A waiver is itself a record; a measurement names
  the environment it was taken in. A reviewer that dies surfaces as *idle*, which reads exactly like
  "finished and found nothing", so the check is "did it report?", never "did it complain?"; before
  retrying, ask **what would have to change for the retry to differ**. When the round cap ends a loop
  without a clean round, the substitute is **one deep unconstrained cold reviewer, not a fourth
  round**. **Reserve `lens`, `round`, and `converged` for `/lr:trilens-loop`** — naming another
  tool's fan-out (e.g. the built-in `/simplify`) with gate vocabulary corrupts the disposition record
  in the scrollback, where no check can see it (`dont-borrow-gate-vocabulary-for-non-gates.md`).
  Expect fix-round findings in the **prose**: context errors, usually one rule stated in two places
  drifting apart, plus redundancy added while fixing. See
  `a-gate-that-died-is-not-a-gate.md`, `gate-waiver-is-a-record.md`,
  `measurement-records-name-their-environment.md`, `fix-defects-are-context-errors.md`,
  `a-fix-is-a-change-and-changes-need-review.md`.
- **A gate cannot be a model self-report** — never implement a gate in the medium it gates. Ask what
  evidence it rests on and whether the thing under test could have produced it; coverage parity is
  not evidence parity. Sibling: **a binding must not be selected by the thing it binds**. Everyday
  form: a green suite written by the fix's author is a self-report until each new test is shown **red
  against the previous tag and green against HEAD** (detached worktree via `LR_FRAMEWORK_DIR`), and a
  **string-containment test over prose** proves only that a doc still says what its author wrote; a
  test that cannot fail independently is documentation in a test's clothes. See
  `a-gate-cannot-be-a-model-self-report.md`,
  `prove-a-new-test-red-against-the-previous-tag.md`.
- **A failure list is a hypothesis until someone reads the transcripts.** An assertion message names
  what was observed, never why; re-triage a red run from stored logs before fixes — cheapest first,
  the module's own verdict history in `results/*/summary.json`, which on v44 sorted three flakes from
  one real regression in seconds. The runner's exit code **is** a verdict —
  2 on refusal, 1 on any failed module — but capture it **unpiped**, since piping it (or wrapping it
  in a command ending in `echo`) reports the pipeline's status and manufactures a false green; an
  identity-blocked engine still renders as `failed 0.0s` when it is *did not run*, and **durations
  triage faster than assertions** (seconds where minutes are normal = the engine never ran) (`triage-a-red-module-against-its-own-history.md`,
  `lifecycle-harness-exit-code-is-not-a-verdict.md`). At the
  single-test level, **a red test may be asserting something true about the machine** — establish
  which side is wrong before turning it green, and give danger-guarding assertions the strongest
  presumption of correctness. See `v31-lifecycle-rerun-partial-green-2026-07-27.md`,
  `a-red-test-may-be-asserting-a-true-fact.md`,
  `transcript-vs-final-message-assertions.md`.
- **Sandboxed-review blind spot** — a review environment that structurally blocks a capability can
  green-light code whose primary path never ran; check for one before trusting a green suite
  (`lore-beings-mvp-takeover-review.md`).
- **Decide where the guardrail lives before writing the topic** — a trap recorded only as knowledge
  protects nobody: lore is retrieved when a task cues it, and a one-off command cues nothing. Name
  the point-of-use site (script check, exact command, test) as part of the fix, and prefer a
  deterministic harness check over a human prep step (`point-of-use-guardrails-beat-recorded-lore.md`).
- **Verify before asserting** — check filesystem/state directly before "fixing" a suspected bug, and
  verify *which* bug. **A negative grep proves the searched pattern absent, never the capability
  absent** — read the entry point before an absence claim carries a decision, and state the absence
  at the granularity actually verified. Read the lore rule a finding rests on before declaring it
  moot; fetch volatile external facts live with a dated citation; after any scoped subagent or fork
  returns, verify its filesystem footprint, not its summary. **An engine fact carries a grade too** —
  ran it / read the shipped code / read the docs — and an undocumented route never goes into a
  contract like an install doc (`engine-bundle-reading-has-an-evidence-grade.md`,
  `a-negative-grep-proves-the-pattern-absent.md`). See
  `verify-before-acting-on-suspected-bugs.md`, `check-own-lore-before-dismissing-a-finding.md`,
  `fetch-volatile-facts-live-not-memory.md`, `fork-scope-creep-under-standing-goal.md`.
- **Design-time rules sharing one shape** — a change that widens where a value comes from drops the
  old source's validation, so re-attach it at the sink; a verdict with a per-item payload needs a
  per-item trigger; a self-documenting delimiter collides with its own documentation; whitespace
  becomes semantics once a check compares bytes; removing an unsound signal requires replacing its
  accidental coverage; a guard keyed on a state **normal** for heavy users opts them out silently
  (prefer reporting over guarding); a proxy condition fails exactly where a user acts deliberately
  (write the real condition in words first); a lock-claim must return a **tri-state result, not a
  bool**. See
  `widening-a-source-drops-its-validation.md`,
  `name-keyed-global-registry-cannot-answer-per-scope.md`,
  `self-documenting-payload-vs-heading-delimiters.md`,
  `template-whitespace-is-contract-under-byte-exact-idempotency.md`,
  `removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md`,
  `guarding-on-a-normal-state-excludes-what-matters-most.md`,
  `short-circuit-on-the-condition-not-a-proxy.md`,
  `lock-claim-directory-creation-vs-contention.md`.
  Three more, all in code I had written and tested: a **catch block is not a durability guarantee**
  (`open(path,"w")` truncates before writing; `UnicodeDecodeError` is a `ValueError`, not an
  `OSError`); a **diagnostic and its remedy must derive from one code path**, or the finding routes
  users to a fix that can never succeed; and a procedure's **approval surface is a separate site from
  its action list**, so adding a write means updating the confirmation template, the dry-run output,
  and every hand-maintained enumeration. See
  `a-reported-error-is-not-proof-the-file-survived.md`, `one-question-one-code-path.md`,
  `adding-a-write-means-updating-the-approval-gate.md`.
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
- **User-feedback working style:** **commit to a recommendation** — a balanced menu of options I could
  have resolved myself reads as absence of judgement and costs trust ("boneless", 2026-08-23); state
  the view and the reason, then at most one question, reserving open questions for decisions
  genuinely the user's (cost, scope, risk appetite). `/lr:style follow` gives the user the
  *direction*, not my silence on the *substance*. **Structure is not brevity** — lead with the shape
  of the change in one breath, save the section-by-section plan for after the yes. Also: ranked
  shortlist over exhaustive enumeration; re-establish where we are after a mode change; confirm
  before writing durable lore mid-session; in design dialogues draft only when the user triggers it;
  populate dry-run counters with would-be outcomes; "enforce X" ≠ add a required schema field;
  decompose broad open-ended asks into hidden axes; on a second pushback on the same axis, act
  instead of re-justifying; a measurement question or a decision already made wants a short
  verdict, not a briefing; several style skills at once is a stop signal, and a second signal next
  turn means cut hard rather than compress. Review subagents default to Composer 2.5. See
  `feedback-commit-to-a-recommendation.md`, `feedback-too-many-words.md`,
  `feedback-confirm-before-writing-lore.md`, `feedback-draft-only-when-user-triggers.md`,
  `feedback-schemas-as-enforcement-overreach.md`,
  `feedback-layered-decomposition-for-open-ended-asks.md`, `feedback-mvp-minimalism.md`,
  `feedback-comply-promptly-after-repeated-pushback.md`,
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
  shell:** assume BSD/macOS, no GNU-only binaries (`timeout`); bound commands via the Bash-tool
  timeout.
- See `conventions.md`, `placeholder-vocabulary.md`, `tooling-cwd-safety.md`,
  `portable-shell-in-framework-docs.md`.

## Onboarding-Doc Authoring

Co-authoring onboarding docs for adopting teams is part of the role. Two genres, each with its own
toolkit: **`onboarding-doc-narrative-pattern.md`** (long-form prose for a human reader) and
**`paste-link-installer-doc-genre.md`** (written *to the AI agent* as the literal installer, pasted
as a link — `QUICKSTART.md` + per-engine `INSTALL-<ENGINE>.md`). Load the identity-layer framings
first; the installer genre also needs the **AI-installer (literal executor)** lens
(`ai-installer-review-lens.md`). Recurring funnel bug: an author writing from the fresh-start
perspective leaves the **team-join path** invisible at every layer
(`onboarding-funnel-team-join-path.md`). Adopter-facing prose carries the product name
**"Lore Agents"** while the engine keeps `lore-framework`/`lr` (`lore-agents-product-name.md`).

## Active Design Explorations

- **lr-dev / Dark Factory (DF)** — a `lr` module for SDLC automation toward an autonomous "dark
  factory" SDLC; per-repo artifacts and narrative context live in a `<repo>-df` backbone; skills not
  agents, persistence external. First aspect: **AIQA/ULA** (`/lr:df-repo-init`, `/lr:df-ula-file`),
  unit-level analysis with a bug-verification track, BETA. Design thread closed. Anchor:
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
  safe default, and two per-kind contract decisions in the backlog. Anchor: `lore-beings-design.md`
  (routes to the per-kind contracts and Keeper findings); see also
  `agent-being-consciousness-substrate-split.md`, `kill-tree-enumerate-before-signal-ordering.md`,
  `lore-beings-mvp-takeover-review.md`, `autonomous-agents-vision.md`, `wait-primitive-feature.md`.
- **Multi-engine portability (Codex, Cursor)** — **shipped, not in flight.** All three engines are
  Tier-1 on one shared agent repo; Claude Code is the reference path and others override only at the
  **5 adapter bindings** (`docs/engines/`). One repo carries both skill namespaces (synced by
  `scripts/sync-cursor-skills` — **python3 despite the missing extension** — checked by `/lr:check`
  #21). Standing facts: **trust rollout/tool-call logs, not model self-report** when validating an
  engine path; Codex's default sandbox blocks `.git` writes and network, so finalization needs `.git`
  writable; a genuinely different engine catches design flaws same-engine review misses, worth the
  cost on high-stakes decisions only, and **model–engine fit beats model tier**. Anchor:
  `multi-engine-portability-direction.md`; see also `docs-engines-convention.md`,
  `cursor-dual-skill-tree-one-repo.md`.

- **Lore housekeeping / consolidation "sleep" pass** and the **simplification/subtraction** item —
  active follow-ups from the 2026-06-13 architecture review. That review's settled dispositions
  (DF-inside-`lr` and team-shared/multi-author as deliberate, not defects — don't re-raise) live in
  `architecture-review-dispositions.md`. The 2026-07-02 review added post-merge diff verification and
  recall-time staleness surfacing.
- **Parked:** workdir-as-reference-library; vector-DB search (until >100 topics/agent); the remaining
  session-as-durable-artifact cluster (boot auto-push, boot-context cache, suspend/resume, JSONL
  archive). See `framework-improvements-backlog.md`, `session-as-durable-artifact-cluster.md`.
- **Workspace layer** — shipped, no longer an exploration. Live: the four-command surface (`init`
  converges, `pull`, `push`, `status`) over one deterministic scanner; the v3 memory-file contract
  and its AI routing map in `AGENTS.md`; automatic 16h workspace refresh as a second `lr-core
  preflight` leg; committed project-scope plugin settings so a clone arrives configured (no Codex
  equivalent, said out loud). Workspace-owned ignore lines include `/.worktrees/`, `/.lr-beings/`,
  `/.tmp/`; disposable scaffolds go under `.tmp/<name>/`. Standing scanner limit: `workspace_scan`
  detects dirty trees only for the workspace **root**, and `workspace-pull` phase 4 fast-forwards
  child repos with no dirty check at all — **ask git per repo**. Still open: the backlog's
  "Workspace-root paths gap" and B7 "Orphan version stamps". See
  `workspace-lifecycle-four-commands.md`, `workspace-memory-file-contract.md`,
  `workspace-auto-refresh-design.md`, `project-scope-plugin-config-feature.md`,
  `v25-workspace-pull-init-design.md`, `workspace-owned-default-ignore-lines.md`,
  `workspace-meta-repo-pattern.md`.

## Current State

Workspace holds **`lore-framework/`**, **`lore-framework-dev/`**, **`lore-agents/`**, and
**`lore-chronicler/`** (Being; on disk, undeclared); meta-repo `AGENTS.md` lists them after
`/lr:workspace-init`, which converges (no `--refresh` flag).

**Recent ships have gone out without a real-engine gate**, so the fixes they landed are themselves
unreviewed; per-ship dispositions and what stays untested live in `versioning-release-types.md`
(establish the current version from the repo, per § Versioning).

My Lore corpus is still largely legacy; v1 adoption is lazy via merge or explicit via `/lr:groom`.
Unrelated uncommitted WIP may sit on these checkouts: never sweep it into lore-finalize commits
(`git add agents/` only), and stash around feature merges
(`fold-feature-into-local-main-via-stash.md`).

**This workspace runs concurrent sessions, including non-human ones** (the live launchd Keeper).
Another session's directory-wide `git add` can commit and push work I left uncommitted — no loss,
but ungated work ships under an unrelated message and `git status` stops being a reliable inventory
of my changes. So: stage narrowly (`git add <path>`, never a directory), re-check `git status` and
`git log` *before reporting* on my own change set, and branch deliberately-ungated work rather than
leaving it dirty. See `concurrent-session-committed-my-uncommitted-work.md`,
`same-agent-multiple-engines-single-writer.md`. For small doc ships, a feedback-only trilens round
then selective apply is valid (`trilens-feedback-only-selective-apply.md`).

## Running Backlog & Standing Improvement List

`framework-improvements-backlog.md` is the canonical store of deferred items in `##` categories of
`###` sections — file new items under the matching category
(`backlog-categorization-precedent.md`); its § Ship Closures archives per-ship gate dispositions.
**`workdir/what-to-improve.md`** is the **standing prioritized improvement list** — a ranked action
view over that backlog which must always exist (user practice, 2026-07-18). Reread it at the start of
every framework-work session; refresh it at each architecture review.
See `standing-improvement-list-practice.md`.
