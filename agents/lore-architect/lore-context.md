---
lore: 1
type: context
summary: "Root working knowledge and navigation for the lore-architect."
---

# Lore Context

Compacted working knowledge for the **lore-architect**. This is the entry point to the lore graph,
not a catalog — each theme points at its summary topic, which fans out to detail. For exhaustive
lookup, scan `lore/` directly. (Follows the `lore-context` shape discipline: working-knowledge +
summary-topic references, present-tense, no index, no version-history narrative — see
`process-merge.md` § Step 4.)

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
parallelism and context isolation (recall, consult, attach, conflict resolution, merge),
serialization is lossless. If the subagent's *independence from the caller* is the deliverable
(`/lr:trilens-loop`), serialization destroys the feature and the procedure must stop and report.
Profile degradation clauses need carve-outs, not blanket rules. See
`subagent-as-optimization-vs-subagent-as-semantics.md`, `cursor-merge-via-task.md`,
`cursor-task-free-text-brief-validated.md`.

See `system-design-principles.md` for the full list and the overreach diagnostics, plus
`team-shared-knowledge-principle.md`, `framework-as-engine-not-kb.md`,
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

The current skill catalog is implementation ground truth, but newcomer-facing information
architecture needs a dedicated curation pass — organize around a daily path and progressively
disclose the rest. See `adopter-command-surface-curation.md`.

**`/lr:style`** is the single public thin-pointer skill for communication/collaboration style — not
boot-loaded. It selects an exact active set of three internal, orthogonal components: **plain**,
**dialogue**, **follow**. No selector means all; `off` means none; each explicit selection replaces
the prior set. v35 removed the three former public commands, with no aliases. See `style-skills.md`,
`skill-request-defaults-to-regular-skill.md`, `soft-skill-follow-me-mode.md`.

An **accelerator** script (Script Fallback Contract) can go one step further and become
**literate**: the procedure lives in the script's own instructional comments rather than a companion
doc, so there's one artifact instead of two that drift apart. Since v36 **`lr-core` is a package** —
the stable `scripts/lr-core` wrapper fronts `scripts/lr_core/`, where `preflight.py` and `scan.py`
carry the literate fallbacks. Hard constraint at that seam: **the script emits data, the doc owns
the user-facing words** — a script string that reads like a finished message gets printed as one,
and printing it *looks* like handling the situation, so the executor never reaches the doc that owns
the remedy. And scripting a procedure does not automatically shrink its doc. See
`literate-accelerator-pattern.md`, `script-emits-data-doc-owns-the-words.md`,
`agent-boot-doc-grew-when-scripted.md`.

The plugin can also **bundle an MCP server** (root `.mcp.json`): **`lr-wait`** (v18) is the first,
and the framework's first `python3` dependency (stdlib-only — the sole sanctioned exception to
bash-on-BSD, for protocol-speaking components). Practical limit: on Claude Code a single MCP call
dies at the engine's ~30-minute idle timeout, and the abort leaves `lr-wait`'s single-request lock
stuck `busy` for the rest of the session — chunk waits at ≤29 min, or use a backgrounded shell
timer. See `plugin-mcp-server-convention.md`, `wait-primitive-feature.md`.

## Engine Hubs

Engine-specific operational knowledge has one hub topic per engine:
`claude-engine-capabilities.md`, `codex-engine-capabilities.md`, `cursor-engine-capabilities.md`.
Use them as entry points for install/update model, invocation surface, subagent mechanism, memory
file, MCP/plugin loading, sandbox constraints, and lifecycle-harness caveats; keep atomic findings
in the linked topics rather than rediscovering them from old session notes. Cursor live usage
retrieval → `cursor-usage-auto-retrieval.md`.

At least one Claude Code host flavor snapshots the **entire plugin bundle per session** rather than
referencing the live checkout, so a mid-session version bump or git pull doesn't reach it. See
`ephemeral-session-plugin-snapshot-topology.md`.

**Where an engine fact belongs:** if it would change what an executor *types*, it goes in
`docs/engines/<engine>.md`'s binding — the doc read at the moment of use — not only in these hubs or
in agent lore. Lore is for judgement and history; the profile is the point-of-use contract. Audit
sibling profiles whenever one binding gains a guardrail. See `docs-engines-convention.md` § Engine
traps belong in the binding.

**Plugin identity is a precondition of a lifecycle result.** The harness asserts loaded plugin
VERSION against `LR_FRAMEWORK_DIR` before trusting results, with the verdict inherited by child
subprocesses via an `engine|realpath|VERSION` token rather than cached per process. Parse the
leading version token only, because Cursor can append completion prose to its identity line.
Cursor's cloud marketplace install **rehydrates within ~25 seconds** of being moved aside, so a
manual prep step cannot be trusted; re-check at suite start. See
`lifecycle-harness-plugin-identity-unverified.md`, `a-gate-cannot-be-a-model-self-report.md`,
`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`.

## Marketplace & Distribution

Shipping one repo to multiple engines' marketplaces means handling **each engine's packaging
separately** — manifest schema, skill-tree location, and update model all differ, so Claude parity
does *not* imply Cursor/Codex parity. Claude Code is strict-clean; the remaining public step is
Console-form community submission. Cursor is structurally ready but seamless multi-user propagation
still needs a team marketplace + Auto Refresh + GitHub App validation. Codex native packaging is
resolved in v25. Public submission also needs reviewer-facing metadata and separation between
runtime release identity, submission-support files, and per-engine publication status. See
`engine-marketplace-readiness.md`, `plugin-distribution.md`,
`cursor-plugin-distribution-update-model.md`, `plugin-manifest-versioning.md`.

Positioning copy must lead with the **triad** (named role-based agents + deliberate reflect/merge
curation + cross-agent collaboration), not cross-engine support —
`positioning-triad-differentiation.md`. **Re-survey `similar-projects-landscape.md` before any
positioning-sensitive ship**; the space moved materially in 18 days as of the 2026-07-20 re-survey.

## Boot & Freshness

Boot (`agent-boot.md`, single source of truth): `lr-core preflight` selects the engine profile,
discovers the agent, auto-pulls, and version-compares → act on the report → `lr-core lore-map
--view boot` (compact taxonomy map + coverage; map failure degrades to normal search, and boot never
migrates Lore) → read `role.md` + `lore-context.md` → confirm with the standard **three-line
report**. **Boot loads only those two files; topics are read on demand.** Repos auto-pull at every
session-context boundary (boot, attach, pre-merge); `/lr:pull-lore` is the manual refresh. See
`freshness-contracts-at-session-boundaries.md`, `auto-pull-mechanism.md`.

**Lore v1 structure (v36):** `docs/lore-structure.md` is the canonical contract — one fixed
`lore-context.md` root, recursive `area` hubs, leaf `topic`s, four-field scalar frontmatter. Every
**new** Lore file carries v1 frontmatter; existing legacy files migrate lazily via merge or
explicitly via **`/lr:groom [scope] [--dry-run] [--all]`** — bounded semantic grooming over a
deterministic ≤30K-token workset with read-only halo, SHA-256 snapshots, and approval-gated
Whole-Lore mode. Practical limit found 2026-08-14: `--all` is single-session and non-resumable in
v1, so on a corpus far above the 30K partition budget it cannot complete — groom iteratively, or
scope `--all` to one subtree. See `lore-topic-format.md`, `lore-context-shape-discipline.md`.

**The engine profile is observed, not believed.** Selection is `lr-core`'s deterministic
`detect_engine` (ordered: `--engine` override → `CLAUDE_PLUGIN_ROOT` → process ancestry matching the
*program* not a command-line substring → framework-root containment → a default explicitly marked
`confidence: "assumed"`). A model must never pick the binding that governs its own execution — the
sibling of "a gate cannot be a model self-report," and why a boot step whose input is a fact about
the running environment belongs in the accelerator rather than in prose. Codex's two remaining
signals fail *together* (sandbox blocks `ps`; containment only matches under `~/.codex/`), so a
Codex session on a worktree or dev checkout silently lands on the claude profile. Cursor IDE agent
chat has the same shape from a different miss. Remedy in both cases is naming `--engine <name>`;
open as backlog B8. See `engine-profile-must-be-observed-not-believed.md`,
`removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md`,
`cursor-ide-engine-detection-blind-spot.md`.

**Cursor boot cost (measured 2026-07-28):** ~20K tokens for a version-match boot, `lore-context.md`
the largest component; remeasure with `lore-framework/scripts/token-count` (`o200k_base`). See
`cursor-boot-context-cost-measurement.md`.

`version-check.md`'s nested-repo guard carries a macOS trap: "resolve both to real paths" is not
self-executing prose — a weak model filled the gap with bare `pwd`, which disagrees with git's
`--show-toplevel` under the `/var`→`/private/var` symlink. **The mirror rule: realpath for identity,
logical components for contract shape.** See `macos-var-symlink-realpath-ambiguity.md`,
`realpath-for-identity-logical-for-contract-shape.md`.

## Cross-Agent Collaboration

- **`/lr:recall [hint]`** — search lore of already-loaded agents (host + guests); fan-out per agent.
- **`/lr:consult <agent> [hint]`** — one-shot question to an unloaded agent; a subagent boots it,
  answers with file pointers, exits.
- **`/lr:attach <agent>`** — load another agent as a sustained guest; host stays sole executor,
  host-wins on conflicts.
- **`/lr:spawn-teammate` (BETA)** — spawn agents as Agent Teams teammates for parallel panes; the
  teammate's primary interlocutor is the user, not the lead.

See `lore-search-pattern.md`, `consult-pattern.md`, `attach-pattern.md`,
`spawn-teammate-feature.md`, `teammate-conventions.md`.

**Division of ownership with `lore-advocate`:** the advocate owns Lore Agents public positioning,
advocacy, and channel strategy; I own architecture, implementation, design history, and product
truth, and supply or verify the technical facts its copy rests on. Public-outreach work leads with
the advocate and consults or attaches me. See `public-communication-ownership.md`.

## Session Takeover (BETA)

**`/lr:takeover`** converts engine-native session logs into a markdown digest so a new session on any
engine can continue interrupted work. Codex, Claude Code, and Cursor are supported
(`scripts/session-takeover` — list, convert, render). Cursor's tool-result pairing is heuristic and
flags `pairing_uncertain`. See `takeover-feature.md`, `cursor-takeover-batch-pairing.md`,
`engine-session-log-formats.md`.

## Finalization

User-triggered, four phases (`/lr:finalize` runs all; phases also run standalone): **reflect**
(inline, host-first, per agent — needs session context) → **merge** (parallel subagents, one per
agent booted as itself, file-driven) → **summarize** (host writes the canonical session summary) →
**commit+push** (one commit per touched repo; conflict resolution on push rejection). Do not
finalize unless the user triggers it. See `finalization-process.md`, `finalize.md`,
`merge-in-booted-subagents.md`, `reflect-merge-execution-asymmetry.md`.

Canonical host summaries carry a compact per-agent **Learning audit**. Finalize retains each
Reflection outcome and Merge handoff through summarize so the audit can preserve concrete learning,
Lore destinations/actions, residual topics, and confidence problems. Only a completed reflection
set can classify every unlisted input as carried over; a failed outcome attributes only known
partial paths, and unavailable evidence leaves origins unknown rather than becoming “nothing
learned.” See `session-summaries-feature.md`.

**Transcript-backed reflection shipped in v39:** opt-in `finalize --transcript` recovers
parser-retained main-thread dialogue into ordinary reflection topics, then rejoins the same
merge/summarize/commit/push lifecycle — host-only, bounded, fail-closed, raw logs staying in local
ignored scratch. Two limits are accepted, not solved: no secret-pattern scan on candidate text, and
no engine parameter that mechanically sandboxes a worker read-only. See
`transcript-backed-finalization-mvp.md`.

Shared-lore publication is a separate, unshipped governance direction. See
`team-lore-contribution-governance.md`.

## Versioning & Migration

`lore-framework/VERSION` is the single source of truth; **the current shipped-and-pushed version is
v40**. Each agent repo stamps that version in its `lore-repo.md`, and four version-bearing plugin
manifests mirror `1.<VERSION>.0` (`/lr:check` #19 enforces). A version is either **migration**,
**release-notes-only**, or both, and independently **cache-affecting** or not — orthogonal axes,
both recorded at every ship. `versioning-release-types.md` holds the full per-version history; read
it for what any given version contained rather than reconstructing from here.

`/lr:update` and boot-time upgrades **auto-commit and auto-push update-owned paths only** (narrow
staging, sole-commit-ahead gate, `lr-update-pending` marker retry, never force); both paths share
the write-aware dirty-target collision gate.

Ship mechanics that bite: verify `git HEAD` rather than trusting lore's "commit pending" (it
accumulates across versions); scan the whole history tail for gaps at each ship rather than only
appending the current entry; **tag at every ship as part of the push step** — check the tag list,
not just `git log` (tags lapsed v32–v35; v36 resumed); and **re-audit the release notes' claims
about themselves as the last pre-push step**, since they are drafted while the gates are still
running and decay once per fix round. See `versioning-release-types.md`,
`plugin-manifest-versioning.md`, `cache-clear-footer-convention.md`, `update-process.md`,
`release-commit-hash-from-tag.md`, `a-release-record-goes-stale-while-you-fix-it.md`.

## Consistency & Diagnostics

Three surfaces, three scopes — the split all three docs now state:

- **`/lr:check`** — 24 content-consistency checks *inside agent repos*; since v37 renders scanner
  findings rather than restating the rules. At scale, prefer a deterministic script sweep for the
  mechanical subset over an LLM read-through: checks #9–10 alone missed 14 dangling references in a
  147-topic graph. See `consistency-checks.md`.
- **`/lr:doctor`** — *engine/plugin runtime* issues that escape content checks (esp. stale plugin
  cache), via an accreting ailment catalog. See `ailment-catalog-pattern.md`.
- **`/lr:workspace-status`** (v37) — read-only diagnosis of the *workspace layer* (git state,
  descriptor drift, memory-file contract, child-repo hygiene), findings S1–S16 each naming its fix.
  See `workspace-lifecycle-four-commands.md`.

## Operating Disciplines

How I work, especially at version ships and high-stakes lore edits. Each rule's body lives in its
own topic — these are pointers, not summaries.

- **On VERSION bumps:** backfill `versioning-release-types.md` history, add the cache-clear footer if
  cache-affecting, bump all four version-bearing manifests to `1.<VERSION>.0`, promote any
  newly-named principle to its own topic. Full curation disciplines live in `role.md`.
- **Pre-ship review has two legs, ordered execution-first** when the deliverable is executable prose:
  lifecycle suite → dogfood the change onto this workspace → TriLens over whatever those disturbed.
  Running a procedure once finds in seconds what nine reading lenses may not find at all, and it
  hands reviewers evidence reading cannot produce. Review catches reasoning issues; the harness
  catches model-execution-fidelity issues invisible to a strong-model reviewer, and the fidelity axis
  is **engine, not just model tier** (cheapest practical tier per engine: Claude → haiku, Codex →
  gpt-5.4-mini, Cursor → composer-2.5). Reporting corollary: after a review-only gate, say plainly
  what remains **untested**. See `lifecycle-testing-harness.md`,
  `execution-testing-catches-blind-ambiguity.md`, `haiku-ambiguity-detector.md`.
- **Run the loop via `/lr:trilens-loop`**, not by hand — the skill enforces cold-context reviewer
  independence, the APPLIED/DECLINED ledger, the "a silent round is not a clean round" guard, and
  rail-removal disclosure, and routes the spawn through the engine binding. Lens *choice* and triage
  stay mine: brief the **goal, not the rationale**; vary the lens *kind* by round (round 1 reviews
  the work, round 2 leads with "did the fixes fix it", round 3 goes where the evidence points);
  treat convergent findings from independent lenses as strong evidence, not redundancy; inventory
  spent lenses before a re-review. Two standing slots: **findings-as-a-system** on any release
  shipping a *set* of diagnostics, **claim audit** on any round following fixes. ~94% of a loop's
  tokens stay inside the subagents, so the exchange contract is justified on independence, never
  token savings. See `trilens-loop-feature.md`, `parallel-reviewer-fanout-pattern.md`,
  `lens-novelty-is-the-scarce-resource-on-re-review.md`, `sonnet-subagent-review-pattern.md`.
- **A gate result belongs to a specific artifact state.** Freeze before spawning — commit, name the
  SHA in the brief, tag only after the loop ends; editing while reviewers read moves line numbers and
  invents phantom findings. An edit landed after the gates pass is ungated: re-run the affected gate
  or revert and file a follow-up, and never report "converged and green" for a tree neither gate saw.
  An environment failure mid-run, or the engine resolving a *different* plugin tree, makes results
  **uninterpretable** rather than red. See `post-convergence-edits-need-their-own-gate.md`,
  `macos-documents-permission-loss-mid-session.md`.
- **Three gate dispositions — passed, waived, did not run** — and a ship record must name which
  applies. A waiver is itself a record; a recorded measurement names the environment it was taken in.
  A reviewer that dies surfaces as *idle*, which reads exactly like "finished and found nothing", so
  the check is "did it report?", never "did it complain?" — and one follow-up ask recovers a merely
  silent lens for free, without counting against the round cap. Before retrying, ask **what would
  have to change for the retry to differ**. When the round cap ends a loop without a clean round, the
  substitute is **one deep unconstrained cold reviewer, not a fourth round**, and a substitute that
  *finds* something does not convert into a clean attestation. Expect its findings in the **prose**:
  fix-round defects are context errors, usually one rule stated in two places drifting apart. See
  `a-gate-that-died-is-not-a-gate.md`, `gate-waiver-is-a-record.md`,
  `measurement-records-name-their-environment.md`, `fix-defects-are-context-errors.md`,
  `a-fix-is-a-change-and-changes-need-review.md`.
- **A gate cannot be a model self-report** — a gate must not be implemented in the medium it gates.
  Ask what evidence it rests on and whether the thing under test could have produced that evidence;
  coverage parity is not evidence parity. Sibling: **a binding must not be selected by the thing it
  binds**. Everyday form: a green suite written by the author of the fix is a self-report until each
  new test is shown **red against the previous tag and green against HEAD** (detached worktree via
  `LR_FRAMEWORK_DIR`). Sharpest form: a **string-containment test over prose** proves only that a doc
  still says what its author wrote — assert against the identifier's independent source, and grep the
  suite whenever review kills a doc string. See `a-gate-cannot-be-a-model-self-report.md`,
  `prove-a-new-test-red-against-the-previous-tag.md`.
- **A failure list is a hypothesis until someone reads the transcripts.** An assertion message names
  what was observed, never why; re-triage a red run from stored logs before planning fixes, and
  classify each text assertion as mid-run or end-state. At the single-test level, **a red test may be
  asserting something true about the machine** — establish which side is wrong before turning it
  green, and give danger-guarding assertions the strongest presumption of correctness. See
  `v31-lifecycle-rerun-partial-green-2026-07-27.md`, `a-red-test-may-be-asserting-a-true-fact.md`,
  `transcript-vs-final-message-assertions.md`.
- **Sandboxed-review blind spot** — a review environment that structurally blocks a capability can
  green-light code whose primary path never executed. Check whether the environment blocks something
  the code under test depends on before trusting a green suite. See
  `lore-beings-mvp-takeover-review.md`.
- **Decide where the guardrail lives before writing the topic** — lore is retrieved when a task cues
  it, and a one-off command cues nothing, so a trap recorded only as knowledge protects nobody. Name
  the point-of-use site (script check, exact command in the doc, test) as part of the fix, and prefer
  a deterministic harness check over a human prep step. See
  `point-of-use-guardrails-beat-recorded-lore.md`.
- **Verify before asserting** — check filesystem/state directly before "fixing" a suspected bug, and
  verify *which* bug. Before declaring a known finding moot, read the lore rule it rests on rather
  than reconstructing it; reconstruction keeps a rule's motivating case and drops its obligation.
  Fetch volatile external facts live with a dated citation. After any scoped subagent or fork
  returns, verify its actual filesystem footprint rather than its summary. See
  `verify-before-acting-on-suspected-bugs.md`, `check-own-lore-before-dismissing-a-finding.md`,
  `fetch-volatile-facts-live-not-memory.md`, `fork-scope-creep-under-standing-goal.md`.
- **Design-time rules sharing one shape** — a change that widens where a value comes from drops the
  old source's validation, so re-attach it at the sink; a verdict with a per-item payload needs a
  per-item trigger; a self-documenting delimiter collides with its own documentation; whitespace
  becomes semantics once a check compares bytes; removing an unsound signal requires replacing the
  coverage it provided by accident. See `widening-a-source-drops-its-validation.md`,
  `name-keyed-global-registry-cannot-answer-per-scope.md`,
  `self-documenting-payload-vs-heading-delimiters.md`,
  `template-whitespace-is-contract-under-byte-exact-idempotency.md`,
  `removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md`.
- **Curation meta-rules:** name foundational principles as their own topics; single canonical source
  (pointer, don't restate — and when fixing a duplicated rule, enumerate every site that *states* it,
  not only every site that *implements* it: docs, findings rows, error text, literate docstrings,
  release notes); reuse an existing correlation signal before inventing new plumbing; don't defer
  completable bounded sweeps; graduated verification. See `naming-foundational-principles.md`,
  `single-canonical-source-discipline.md`, `reuse-existing-correlation-signal.md`,
  `feedback-don-t-defer-completable-scope.md`, `graduated-verification-confidence.md`.
- **User-feedback working style:** ranked shortlist over exhaustive enumeration; confirm before
  writing durable lore mid-session; in design dialogues write the draft only when the user triggers
  it; populate dry-run counters with would-be outcomes; "enforce X" ≠ add a required schema field;
  decompose broad open-ended asks into hidden axes and sequence by dependency; on a second pushback
  on the same axis, act instead of re-justifying; a short measurement question gets a short factual
  answer; several style skills invoked at once is a stop signal for the rest of the session. Review
  subagents default to Composer 2.5, not Sonnet. See `feedback-too-many-words.md`,
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
- Command filenames: lowercase/digits/hyphens, ≤64 chars.
- Placeholders: `<workspace>`, `<lore-agent-repo>`, `<guest-lore-agent-repo>`, `<agent-name>`,
  `${CLAUDE_PLUGIN_ROOT}`.
- **CWD safety:** never `cd` when later tools depend on cwd — use `git -C <repo>`. **Portable
  shell:** assume BSD/macOS, no GNU-only binaries (`timeout`); bound commands via the Bash-tool
  timeout.
- See `conventions.md`, `placeholder-vocabulary.md`, `tooling-cwd-safety.md`,
  `portable-shell-in-framework-docs.md`.

## Onboarding-Doc Authoring

Co-authoring onboarding docs for adopting teams is part of the role. Two genres:
**`onboarding-doc-narrative-pattern.md`** (long-form prose pitching a human reader) and
**`paste-link-installer-doc-genre.md`** (written *to the AI agent* as the literal installer, pasted
as a link — shipped as `QUICKSTART.md` + per-engine `INSTALL-<ENGINE>.md`). Load the identity-layer
framings first, then the toolkit: `use-cases-via-parallel-consult-pattern.md`,
`terminology-domain-collision-trap.md`, `agent-as-universal-working-environment.md`,
`in-flight-skill-teaching-pattern.md`. Pre-ship review uses the multi-lens fan-out; the installer
genre additionally needs the **AI-installer (literal executor)** lens
(`ai-installer-review-lens.md`), which catches execution-fidelity bugs the newcomer/editorial lenses
miss (`skill-doc-filename-divergence-bug-class.md`). Recurring funnel bug: an author writing from
the fresh-start perspective leaves the **team-join path** invisible at every layer — check README
prose, QUICKSTART, and the INSTALL preambles, and keep the fork question verbatim-identical across
sites (`onboarding-funnel-team-join-path.md`). Adopter-facing prose carries the product name
**"Lore Agents"** while the engine keeps `lore-framework`/`lr` (`lore-agents-product-name.md`).

## Active Design Explorations

- **lr-dev / Dark Factory (DF)** — a `lr` module for SDLC automation toward an autonomous "dark
  factory" SDLC. Per-repo artifacts and narrative context live in a `<repo>-df` backbone. Skills not
  agents; persistence external. First aspect: **AIQA/ULA** (`/lr:df-repo-init`, `/lr:df-ula-file`) —
  unit-level analysis with a bug-verification track, BETA. The design thread is closed. Anchor:
  `lr-dev-direction.md`; see `df-per-repo-backbone.md`, `aiqa-ula-feature.md`,
  `df-module-conventions.md`, `workflow-primitive-operational-notes.md`.
- **Autonomous agents / Lore Beings** — agents as always-on background collaborators with persistent
  task state, raising for input only when needed. Design settled 2026-07-19: a being is an ordinary
  lore agent plus a `being.md` descriptor, and the **Being Keeper** (`lrb`) is deterministic
  substrate, never an LLM. MVP is CLI-only; engines are explicit user config; budget = daily-USD
  spawn gate + per-task wall-clock kill. Engine kinds `claude`, `codex`, `cursor`. The substrate
  shipped BETA in v28 and v29 added the `/lr:being` command surface; Keeper-specific real-engine
  lifecycle coverage sits behind the `LR_LIFECYCLE_KEEPER=1` gate. Two per-kind contract gaps are
  open backlog schema decisions, not silently patched: `cursor` is empirically cost-blind so its flat
  `--session-cost-usd` fallback is load-bearing, and `claude` has no `--plugin-dir` field so a
  claude-kind being needs a wrapper-script `command`. **The persistent `--launchd` Keeper install is
  live on this machine** (verified 2026-07-28) — treat it as a candidate explanation whenever a repo
  changes under me mid-session; the Chronicler soak is a *separate*, still-unverified question. Open
  gap: headless permissions, and self-scheduling under the safe default. Anchor:
  `lore-beings-design.md`; see `agent-being-consciousness-substrate-split.md`,
  `engine-kinds-design-decision.md`, `cursor-agent-real-invocation-contract.md`,
  `codex-exec-real-invocation-contract.md`, `kill-tree-enumerate-before-signal-ordering.md`,
  `macos-ps-o-multi-field-single-line.md`, `unenforceable-caps-are-prompt-theater.md`,
  `keeper-spawn-prompt-boilerplate-distraction.md`, `lore-beings-mvp-takeover-review.md`,
  `autonomous-agents-vision.md`, `wait-primitive-feature.md`.
- **Multi-engine portability (Codex, Cursor)** — **shipped, not in flight.** Claude Code, Codex, and
  Cursor are all Tier-1 supported, so a mixed-engine team shares one agent repo; Claude Code remains
  the reference path, and other engines override only at binding points. The port was **packaging,
  not redesign** — the whole surface is **5 adapter bindings** via the `docs/engines/` convention
  plus Boot Step-0 engine selection — because the knowledge substrate was already engine-agnostic.
  Both other engines have native in-session subagents (Codex `spawn_agent`, which has **no `role`
  argument**; Cursor `Task`, free-text briefs validated), so the feared Tier-B nucleus is proven, and
  one repo carries both skill namespaces (synced by `scripts/sync-cursor-skills`, `/lr:check` #21).
  Standing operational facts: **trust rollout/tool-call logs, not model self-report**, when
  validating an engine path; Codex's default sandbox blocks `.git` writes and network, so
  finalization needs `.git` writable through launch/config; Codex per-agent shortcut
  register/unregister/list remains an unvalidated gap. **Separate sessions on separate engines
  coordinating on a real task** has a validated substrate (a shared append-only folder), with two
  rules that fell out of running it: check for same agent identity before any session writes, and
  don't relay a user decision into the shared channel as settled authority for another session. A
  genuinely different engine also catches design flaws same-engine multi-lens review misses — worth
  the coordination cost on high-stakes design decisions, not routine changes. The "framework is prose
  executed by the model" risk is empirically retired for exercised paths, and the quality benchmark
  showed positive lore-utilization uplift on every engine+model config, with **model–engine fit
  beating model tier**. Anchor: `multi-engine-portability-direction.md`; see
  `docs-engines-convention.md`, `claude-coupling-inventory-and-port-tiers.md`,
  `cursor-dual-skill-tree-one-repo.md`, `quality-benchmark-feature.md`,
  `cross-engine-team-substrate-validated.md`, `same-agent-multiple-engines-single-writer.md`,
  `cross-engine-relay-not-attributable-authority.md`,
  `independent-engine-review-catches-structural-blind-spots.md`, `port-landing-next-steps.md`.
- **Lore housekeeping / consolidation "sleep" pass** and the **simplification/subtraction** item —
  active follow-ups from the 2026-06-13 architecture review. That review's settled dispositions
  (DF-inside-`lr` and team-shared/multi-author as deliberate, not defects — don't re-raise) live in
  `architecture-review-dispositions.md`. The 2026-07-02 review added post-merge diff verification and
  recall-time staleness surfacing.
- **Parked:** workdir-as-reference-library; vector-DB search (until >100 topics/agent); the remaining
  session-as-durable-artifact cluster (boot auto-push, boot-context cache, suspend/resume, JSONL
  archive). See `framework-improvements-backlog.md`, `session-as-durable-artifact-cluster.md`.
- **Workspace layer (v25) and workspace lifecycle (v37, corrected v38)** — both shipped, no longer
  explorations. The four-command surface (`init` converges, `pull`, `push`, `status`) and the v3
  memory-file contract are live; standard workspace-owned ignore lines include `/.worktrees/`,
  `/.lr-beings/`, and `/.tmp/`, and disposable scaffolds go under `.tmp/<name>/`. Still open and
  *not* closed by it: the backlog's "Workspace-root paths gap" and B7 "Orphan version stamps". See
  `workspace-lifecycle-four-commands.md`, `workspace-memory-file-contract.md`,
  `v25-workspace-pull-init-design.md`, `workspace-owned-default-ignore-lines.md`,
  `workspace-meta-repo-pattern.md`.

## Current State

Workspace holds **`lore-framework/`**, **`lore-framework-dev/`**, **`lore-agents/`**, and
**`lore-chronicler/`** (Being; on disk, undeclared). Meta-repo `AGENTS.md` lists them after
`/lr:workspace-init`, which converges — there is no `--refresh` flag as of v37.

Framework `main` carries **v40** shipped, tagged, and pushed. Its canonical host-summary Learning
audit is live. The current real-engine fidelity evidence is deliberately scoped: the deterministic
suite is green and one Codex `gpt-5.4` finalization lifecycle passed; quality and Claude/Cursor
lifecycle runs did not run, so no broader claim follows. The full gate record lives in
`versioning-release-types.md`.

My own Lore corpus is still largely legacy; v1 adoption is lazy via merge or explicit via
`/lr:groom`. Unrelated uncommitted WIP may sit on these checkouts; do not sweep it into
lore-finalize commits (`git add agents/` only), and preserve unrelated dirty-tree changes during
release or fold-into-main work, stashing around feature merges when needed
(`fold-feature-into-local-main-via-stash.md`).

**This workspace really does run concurrent sessions, including non-human ones** (the live launchd
Keeper above). A concurrent session's directory-wide `git add` can commit and push work I left
uncommitted — no conflict, no loss, but ungated work ships under an unrelated commit message, and
`git status` stops being a reliable inventory of my own changes. So: stage narrowly (`git add
<path>`, not a directory), re-check `git status` and `git log` *before reporting* on my own change
set, and never leave deliberately-ungated work sitting dirty — branch it. See
`concurrent-session-committed-my-uncommitted-work.md`,
`same-agent-multiple-engines-single-writer.md`.

Both pre-ship gates remain in working order: `/lr:trilens-loop`, and `tests/lifecycle/` (plus Keeper
and quality tracks). For small doc ships, a feedback-only trilens round then selective apply is a
valid path (`trilens-feedback-only-selective-apply.md`).

## Running Backlog & Standing Improvement List

`framework-improvements-backlog.md` is the canonical list of deferred items; its § Ship Closures
archives per-ship gate dispositions. It is organized into top-level `##` categories (Major
Directions, Session Lifecycle & Durability, Knowledge Quality & Curation, Multi-Agent Collaboration,
Workspace & Environment, Framework Upkeep/Distribution/Docs, Ship Closures) each holding `###`
topical sections — file new items under the matching category
(`backlog-categorization-precedent.md`). ~236 lore topics.

**`workdir/what-to-improve.md`** is the **standing prioritized improvement list** — a ranked action
view over the backlog that must always exist, not a one-off review deliverable (user-established
practice, 2026-07-18). Reread it at the start of every framework-work session; refresh it at each
architecture review. See `standing-improvement-list-practice.md`.
