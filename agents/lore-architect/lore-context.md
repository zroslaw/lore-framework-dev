---
lore: 1
type: context
summary: "Root working knowledge and navigation for the lore-architect."
---

# Lore Context

Compacted working knowledge for the **lore-architect**. This is the entry point to the lore graph, not a catalog — each theme points at its summary topic, which fans out to detail. For exhaustive lookup, scan `lore/` directly. (This doc follows the `lore-context` shape discipline: working-knowledge + summary-topic references, present-tense, no index, no version-history narrative — see `process-merge.md` § Step 4.)

## Style Skills

`/lr:style` is the single public, regular thin-pointer skill for communication/collaboration style — not boot-loaded or surfaced at boot. It selects an exact active set of three internal, orthogonal components: **plain** (sentence-level simple English), **dialogue** (short incremental turns), and **follow** (user-led thinking with small suggestions). No selector means all; `off` means none; each explicit selection replaces the prior set. Version 35 removed the three former public commands, with no aliases. A boot-loaded "soft skills" mechanism was prototyped and rejected in favor of this plain skill. See `style-skills.md`, `skill-request-defaults-to-regular-skill.md`, `soft-skill-follow-me-mode.md`.

## Who I Am

Architect and maintainer of the lore system — the `lr` framework plugin and the agent ecosystem on it. I work across two repos: **`lore-framework/`** (the distributed plugin — changes to how agents work go here) and **`lore-framework-dev/`** (my own agent repo — my lore, workdir, sessions). I'm both builder and user: I use lore to track my own design knowledge. See `role.md`.

## System Architecture

Three discrete layers — identify which one owns a change before touching files:
1. **Plugin** (`lore-framework/`, installed as `lr`) — what's distributed via the marketplace: skills, docs, migrations, scripts, manifests, `VERSION`. Universal across installs.
2. **Domain** — the conceptual scope of one agent repo, marked by `lore-repo.md` (frontmatter: `description`, `version`, optional `repos:`). Holds `agents/<name>/` with `role.md`, `lore-context.md`, `lore/`, `workdir/`, `sessions/`.
3. **Workspace** — the filesystem Claude runs from; holds one or more agent repos + their declared siblings. Discovery scans workspace-root dirs for `lore-repo.md`; nested repos are invisible to most skills.

See `architecture-overview.md`, `workspace-vs-domain-vocabulary.md`, `agent-discovery-nesting-constraint.md`, `plugin-vs-agent-repo-separation.md`, `workspace-owned-default-ignore-lines.md`.

## Design Principles

Identity-layer framings that frame everything else:
- **Team-shared knowledge** — agents are team-shared knowledge containers, not personal notebooks. Design for concurrent multi-contributor use.
- **Engine, not KB** — the framework is the engine/environment for self-improving agents; the knowledge base is a consequence, not the identity.
- **Executors first, advisors second** — primary value is getting things done; conversation is secondary. The usage→learning positive feedback loop only spins under executor-first framing.

What each agent carries: **knowledge** (markdown — what it knows, accrues passively via reflection) + **skills** (tools + instructions — what it can do, evolves actively via in-flight teaching). Distinct assets; don't collapse them.

Core mechanics: directory-driven, plain markdown (frontmatter only on descriptor files), git-as-metadata, delete-don't-mark, knowledge graph by filename reference, concise context with detail on demand, skill/doc separation, repo-level versioning. Framework owns the universal; agents own repo/host/workflow specifics.

**Subagent as optimization vs subagent as semantics** — before letting any engine degrade a
subagent-spawning procedure to serial host-side execution, classify what the subagent is *for*. If it
buys parallelism and context isolation (recall, consult, attach, conflict resolution — merge too on
Cursor since 2026-07-28 via `Task`), serialization is lossless. If the subagent's *independence from
the caller* is the deliverable (`/lr:trilens-loop`), serialization destroys the feature — the procedure
must stop and report. Profile degradation clauses need carve-outs, not blanket rules. On Cursor, `Task`
free-text briefs are validated and merge + trilens use them; recall/consult/attach/conflict resolution
stay serial until upgraded. See `subagent-as-optimization-vs-subagent-as-semantics.md`,
`cursor-merge-via-task.md`, `cursor-task-free-text-brief-validated.md`.

See `system-design-principles.md` (the full list and the overreach diagnostics), plus the framing topics `team-shared-knowledge-principle.md`, `framework-as-engine-not-kb.md`, `agents-are-executors-first.md`, `knowledge-vs-skills-distinction.md`, `framework-scope-vs-agent-scope.md`.

## Skills & Docs

Operations are Claude Code plugin skills, `lr:` prefix on Claude; Cursor uses `/lr-<skill>` via
prefixed wrappers (`cursor-dual-skill-tree-one-repo.md`). **Skills are thin pointers** — each `skills/<name>/SKILL.md` is a one-line reference to `docs/<name>.md`, where all logic lives. Same for generated `/lr-<agent>-agent` boot commands (thin delegations to `agent-boot.md`). When a skill orchestrates sub-skills, the orchestration gets its own `docs/<skill>.md`; non-skill procedures shared across call sites get a `docs/<procedure>.md` (e.g. `auto-pull.md`). See `slash-command-system.md`, `skill-doc-pattern.md`, `shared-procedure-doc-pattern.md`, `single-canonical-source-discipline.md`.

The current skill catalog is implementation ground truth, but newcomer-facing information architecture needs a dedicated curation pass: organize it around a daily path and progressively disclose the rest. See `adopter-command-surface-curation.md`.

An **accelerator** script (Script Fallback Contract) can go one step further and become
**literate**: the procedure lives in the script's own instructional comments rather than in a
companion doc, so there's one artifact instead of two that can drift apart. First applied to
`scripts/lr-core` in v31; since v36 **`lr-core` is a package** — the stable `scripts/lr-core`
wrapper fronts `scripts/lr_core/`, where `preflight.py` and `scan.py` carry the literate fallbacks
(`lore_graph`/`lore_map`/`lore_workset` are implementations with no manual takeover; doc pointers
name the module). Hard constraint at that seam: **the script emits data, the doc owns
user-facing words** — a script string that reads like a finished message gets printed as one, and
printing it *looks* like handling the situation, so the executor never reaches the doc that owns
the remedy. And scripting a procedure does not automatically shrink its doc: `auto-pull.md` shrank,
`agent-boot.md` doubled. See `literate-accelerator-pattern.md`,
`script-emits-data-doc-owns-the-words.md`, `agent-boot-doc-grew-when-scripted.md`.

The plugin can also **bundle an MCP server** (declared in a root `.mcp.json`, auto-launched by Claude Code with its tools merged into the agent): **`lr-wait`** (v18) is the first — and the framework's first `python3` dependency (stdlib-only, no pip; the sole sanctioned exception to bash-on-BSD, for protocol-speaking server components). Practical limit to remember before promising a long wait: on Claude Code a single MCP call dies at the engine's ~30-minute idle timeout, and the abort leaves `lr-wait`'s single-request lock stuck `busy` for the rest of the session — chunk waits at ≤29 min, or use a backgrounded shell timer. See `plugin-mcp-server-convention.md`, `wait-primitive-feature.md`.

## Engine Hubs

Engine-specific operational knowledge now has one hub topic per engine: `claude-engine-capabilities.md`,
`codex-engine-capabilities.md`, and `cursor-engine-capabilities.md`. Use them as the entry points
for install/update model, invocation surface, subagent mechanism, memory file, MCP/plugin loading,
sandbox constraints, and lifecycle-harness caveats; keep atomic findings in the linked detailed
topics rather than rediscovering them from old session notes. Cursor live usage retrieval
(plan quota + CLI session context) → `cursor-usage-auto-retrieval.md`. On Cursor, merge and trilens
run via native `Task` with validated free-text briefs; other fan-outs remain serial host-side until
upgraded (`cursor-merge-via-task.md`, `cursor-task-free-text-brief-validated.md`).

At least one Claude Code host flavor ("local-agent-mode-sessions") snapshots the **entire plugin
bundle per session** rather than referencing the live checkout — skill dispatch resolves through
that frozen snapshot for the session's whole lifetime, so a mid-session version bump or git pull to
the workspace checkout doesn't reach it. See `ephemeral-session-plugin-snapshot-topology.md`.

**Where an engine fact belongs:** if it would change what an executor *types*, it goes in
`docs/engines/<engine>.md`'s binding — the doc read at the moment of use — not only in these hubs or in
agent lore. Lore is for judgement and history; the profile is the point-of-use contract. I learned this
by hitting a trap that had been recorded in my own lore since v18. See `docs-engines-convention.md`
§ Engine traps belong in the binding, and audit sibling profiles whenever one binding gains a guardrail.

**Plugin identity is a precondition of a lifecycle result.** The lifecycle harness asserts loaded
plugin VERSION against `LR_FRAMEWORK_DIR` before trusting results, including per-run
`framework_dir` overrides, with the verdict inherited by child subprocesses via an
`engine|realpath|VERSION` token rather than cached per process. Codex reads
`~/.codex/config.toml` + plugin cache; Cursor walks `~/.cursor/plugins/{local,marketplaces,cache}`;
the loaded-plugin probe covers Claude too. Parse the leading version token only, because Cursor can
append completion prose directly to its required identity line. The Cursor arm was originally an
engine-side prompt and passed while the suite ran on v30 — a gate implemented in the medium it
gates is not a gate. Cursor's cloud marketplace install also **rehydrates within ~25 seconds** of
being moved aside, so a manual prep step cannot be trusted; re-check at suite start, which is what
the harness check is for. See
`lifecycle-harness-plugin-identity-unverified.md`, `a-gate-cannot-be-a-model-self-report.md`,
`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`.

## Marketplace & Distribution

Shipping one repo to multiple engines' plugin marketplaces means handling **each engine's packaging
separately** — manifest schema, skill-tree location, and update model all differ, so Claude parity
does *not* imply Cursor/Codex parity. Claude Code is strict-clean; remaining public-distribution step
is Console-form community submission. Cursor is structurally ready, but seamless multi-user
propagation still needs a team marketplace + Auto Refresh + Cursor GitHub App validation. Codex
native packaging is resolved in v25: legacy Claude marketplace fallback still works, native
`.agents/plugins/marketplace.json` is preferred when present, and `.codex-plugin/plugin.json` is the
Codex version-bearing manifest. Public submission also needs reviewer-facing metadata (`MARKETPLACE.md`
directory copy + root `PRIVACY.md`) and precise separation between runtime release identity,
submission-support files, and per-engine verified publication status. See `engine-marketplace-readiness.md`, `plugin-distribution.md`,
`cursor-plugin-distribution-update-model.md`, `plugin-manifest-versioning.md`.

Positioning copy for README/marketplace submission must lead with the **triad** (named
role-based agents + deliberate reflect/merge curation + cross-agent collaboration), not
cross-engine support — see `positioning-triad-differentiation.md`. **Re-survey the
competitive landscape (`similar-projects-landscape.md`) before any positioning-sensitive
ship** — README rewrite, marketplace submission, public announcement — the space moved
materially in just 18 days as of the 2026-07-20 re-survey.

## Boot & Freshness

Boot (`agent-boot.md`, single source of truth): `lr-core preflight` selects the engine profile, discovers the agent, auto-pulls, and version-compares → act on the report → `lr-core lore-map --view boot` (compact taxonomy map + coverage; map failure degrades to normal search, and boot never migrates Lore) → read `role.md` + `lore-context.md` → confirm with the standard **three-line report** (Booted / Agent Lore / Context Footprint, ceiling-rounded thousands). **Boot loads only those two files; topics are read on demand.** Repos auto-pull at every session-context boundary (boot, attach, pre-merge) to match the team's latest pushed state; `/lr:pull-lore` is the manual refresh. See `freshness-contracts-at-session-boundaries.md`, `auto-pull-mechanism.md`.

**Lore v1 structure (v36):** `docs/lore-structure.md` is the canonical contract — one fixed
`lore-context.md` root (v1 target ≤10K est. tokens, error >20K; legacy keeps 50K until migrated),
recursive `area` hubs, leaf `topic`s, four-field scalar frontmatter (`lore`, `type`, `summary`,
`parent`). Every **new** Lore file carries v1 frontmatter; existing legacy files migrate lazily via
merge or explicitly via **`/lr:groom [scope] [--dry-run] [--all]`** — bounded semantic grooming
over a deterministic ≤30K-token workset with read-only halo, SHA-256 snapshots, and approval-gated
Whole-Lore mode.

**The engine profile is observed, not believed.** Profile selection is `lr-core`'s deterministic
`detect_engine` (ordered: `--engine` override → `CLAUDE_PLUGIN_ROOT` → process ancestry, matching the
*program* not a command-line substring → framework-root containment → a default explicitly marked
`confidence: "assumed"`). A model must never pick the binding that governs its own execution — the
sibling of "a gate cannot be a model self-report," and the reason a boot step whose input is a fact
about the running environment belongs in the accelerator rather than in prose. Deleting the old
unsound "`~/.codex/` exists → codex" rung also removed the coverage it was providing by accident:
Codex's two remaining signals fail *together* (sandbox blocks `ps`; containment only matches under
`~/.codex/`), so a Codex session on a worktree or dev checkout silently lands on the claude profile —
handled by making the no-signal branch legible and naming `--engine codex` as the remedy, in
`docs/engines/codex.md` § Detection blind spot. **Cursor IDE agent chat has the same shape from a
different miss:** ancestry sees only deliberately-excluded `Cursor` / Helper programs (so
Claude-in-Cursor-terminal stays correctly unlabeled), and a workspace checkout as
`<framework-root>` misses `~/.cursor/` containment — so IDE chat (not `cursor-agent` CLI) also
lands on `assumed` → Claude until `--engine cursor`. Open as backlog B8. See
`engine-profile-must-be-observed-not-believed.md`,
`removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md`,
`cursor-ide-engine-detection-blind-spot.md`.

**Cursor boot cost (measured 2026-07-28):** a version-match boot is ~20K tokens (~8–9% of a 256K window); `lore-context.md` is the largest file (~9K), `version-check.md` adds ~3.9K only on skew. Remeasure with `lore-framework/scripts/token-count` (`o200k_base`). See `cursor-boot-context-cost-measurement.md`, `agent-boot-doc-grew-when-scripted.md`.

`version-check.md`'s nested-repo guard has a macOS-specific trap: "resolve both to real paths" is not
self-executing prose — a weak model filled the gap with bare `pwd`, which disagrees with git's
`--show-toplevel` under macOS's `/var`→`/private/var` symlink, producing a false "not its own git root"
verdict. Fixed by naming the exact `os.path.realpath()` one-liner instead of the vague instruction. See
`macos-var-symlink-realpath-ambiguity.md`.

## Cross-Agent Collaboration

- **`/lr:recall [hint]`** — search lore of already-loaded agents (host + guests); fan-out per agent.
- **`/lr:consult <agent> [hint]`** — one-shot question to an unloaded agent; a subagent boots it, answers with file pointers, exits.
- **`/lr:attach <agent>`** — load another agent as a sustained guest; host stays sole executor, host-wins on conflicts.
- **`/lr:spawn-teammate` (BETA)** — spawn agents as Agent Teams teammates for parallel panes; the teammate's primary interlocutor is the user, not the lead.

See `lore-search-pattern.md`, `consult-pattern.md`, `attach-pattern.md`, `spawn-teammate-feature.md`, `teammate-conventions.md`.

## Session Takeover (BETA)

**`/lr:takeover`** converts engine-native session logs into a markdown digest so a new session on any engine can continue interrupted work. Codex, Claude Code, and Cursor are supported (`scripts/session-takeover` — list, convert, render). Cursor pairs tool results from `store.db` to JSONL `tool_use` batches via batch-window name matching; same-name parallel batches and interrupted sessions set `pairing_uncertain`. See `takeover-feature.md`, `cursor-takeover-batch-pairing.md`, `engine-session-log-formats.md`.

## Finalization

User-triggered, four phases (`/lr:finalize` runs all; phases also run standalone): **reflect** (inline, host-first, per agent — needs session context) → **merge** (parallel subagents, one per agent booted as itself, file-driven — integrates reflections into `lore/`, `lore-context.md`, `role.md`) → **summarize** (host writes the canonical session summary + short guest summaries) → **commit+push** (one commit per touched repo; conflict-resolution on push rejection). Do not finalize unless the user triggers it. See `finalization-process.md`, `finalize.md`, `merge-in-booted-subagents.md`, `reflect-merge-execution-asymmetry.md`.

Shared-lore publication is a separate, unshipped governance direction: retain direct publish for trusted teams, but use Git branches, review, and protections where the team's risk model requires them. See `team-lore-contribution-governance.md`.

## Versioning & Migration

`lore-framework/VERSION` is the single source of truth; **the current shipped-and-pushed version is
v38** (full entry in `versioning-release-types.md`, don't reconstruct it from here). Each agent repo stamps that
version in its `lore-repo.md`, and four version-bearing plugin manifests mirror
`1.<VERSION>.0` (`/lr:check` #19 enforces). A version is either **migration**, **release-notes-only**,
or both, and independently **cache-affecting** or not — those two axes are orthogonal, and every ship
records both in `versioning-release-types.md`, which holds the full per-version history. Read that
topic for what any given version contained; don't reconstruct it from here.

`/lr:update` and boot-time upgrades now **auto-commit and auto-push update-owned paths only**
(narrow staging, sole-commit-ahead gate, `lr-update-pending` marker retry, never force); both paths
share the write-aware dirty-target collision gate — the old "update writes through dirty files"
asymmetry is gone.

Ship mechanics that bite: verify `git HEAD` rather than trusting lore's "commit pending" (it
accumulates across versions); scan the whole history tail for gaps at each ship rather than only
appending the current entry; and **tag at every ship as part of the push step** — check the tag
list, not just `git log`, when verifying ship state (tags lapsed v32–v35; v36 resumed). See
`versioning-release-types.md`, `plugin-manifest-versioning.md`,
`cache-clear-footer-convention.md`, `update-process.md`, `release-commit-hash-from-tag.md`.

## Consistency & Diagnostics

- **`/lr:check`** — 24 content-consistency checks (descriptor/version, structure, references, size/state, drift, four-manifest #19, migration write-paths #20, cursor-tree parity #21, workspace-layer checks #22–24, which since v37 render scanner findings rather than restating the rules). At scale, prefer a deterministic script-based sweep for the mechanical subset (existence/version/glob checks) over an LLM read-through — checks #9–10 alone missed 14 dangling references in a 147-topic graph. See `consistency-checks.md`.
- **`/lr:doctor`** — diagnoses runtime/environmental issues that escape content checks (esp. stale plugin cache) via an accreting ailment catalog. See `ailment-catalog-pattern.md`.
- **`/lr:workspace-status`** (v37) — read-only diagnosis of the *workspace* layer (git state, descriptor drift, memory-file contract, child-repo hygiene), findings S1–S16 each naming its fix. The three-way split all three docs now state: status = this workspace's git/descriptor state, check = content consistency inside agent repos, doctor = engine/plugin runtime. See `workspace-lifecycle-four-commands.md`.

## Operating Disciplines

How I work, especially at version ships and high-stakes lore edits:
- **On VERSION bumps:** backfill `versioning-release-types.md` history, add the cache-clear footer if cache-affecting, bump all four version-bearing plugin manifests to `1.<VERSION>.0`, promote any newly-named principle to its own topic. (Full curation disciplines live in `role.md`.)
- **Pre-ship review:** multi-lens review iterated until a round finds nothing worth fixing (convergence is the ship signal) — **run it via `/lr:trilens-loop`** rather than hand-assembling the fan-out; the skill enforces cold-context reviewer independence, the APPLIED/DECLINED ledger, the "a silent round is not a clean round" guard, and rail-removal disclosure, while lens *choice* and triage judgement stay mine. Brief reviewers with the **goal, not the rationale** — rationale pre-empts the criticism you're paying for. Two triage facts from a measured live round: **~94% of a loop's tokens stay inside the subagents**, so withholding the diff is cost-neutral and the exchange contract must be justified on independence, never token savings; and **convergent findings from two independent lenses are strong evidence, not redundancy** — reword rather than defend. Sonnet boot-as-self review remains the separate single-lens, role-as-perspective tool for high-stakes single edits. **Vary the lens *kind* by round:** round 1 reviews the work, round 2 leads with "did the fixes fix it, and did they break anything", round 3 goes where the evidence says risk concentrated — the shipped doc does not say this (`parallel-reviewer-fanout-pattern.md` § Choose lenses per round). Across loops, **lens novelty is the scarce resource**: inventory the lenses already spent before picking new ones, and let the artifact's life stage — proposal vs shipped-with-an-installed-base — choose the family (`lens-novelty-is-the-scarce-resource-on-re-review.md`). Two standing slots: **findings-as-a-system** on any release shipping a *set* of diagnostics, **claim audit** on any round that follows fixes. See `trilens-loop-feature.md`, `parallel-reviewer-fanout-pattern.md`, `sonnet-subagent-review-pattern.md`. **Second, empirical leg (v18+):** for procedure docs covered by the lifecycle testing harness, also run the relevant scenarios against real engine execution before shipping — review catches reasoning issues, the harness catches model-execution-fidelity issues invisible to a strong-model reviewer — and the fidelity axis is **engine, not just model tier** (run scenarios on every engine, using the cheapest practical default tier unless explicitly overriding: Claude Code -> haiku, Codex -> gpt-5.4-mini, Cursor -> composer-2.5; the same model tier can behave differently by engine, and mid-procedure step insertions are the highest-risk for a silent skip). **Order the two legs execution-first** when the deliverable is executable prose: lifecycle suite, then dogfood the change onto this workspace, *then* TriLens over whatever those disturbed — running a procedure once finds in seconds what nine reading lenses may not find at all, and it hands reviewers evidence reading cannot produce. Reporting corollary: after a review-only gate, say plainly what remains **untested**; "three rounds, nine lenses, 28 findings" implies coverage it does not have. See `lifecycle-testing-harness.md`, `execution-testing-catches-blind-ambiguity.md`, `haiku-ambiguity-detector.md`.
- **A gate result belongs to an artifact state** — a converged review loop and a green lifecycle run each certify only the tree they actually ran against. An edit landed after the gates pass is ungated: re-run the affected gate, or revert and file a follow-up. Never report "converged and green" for a tree neither gate saw, and record *which* state a result belongs to. **Pointed at the gate's input: freeze before spawning** — commit, name the SHA in the brief, tag only after the loop ends; editing while reviewers read moves line numbers, invents phantom findings, and lets a reviewer miss a defect by reading the already-fixed half of a pair. Also: an environment failure mid-run (e.g. macOS TCC revocation) or the engine resolving a *different* plugin tree makes results **uninterpretable**, not red — fix and re-run rather than debugging the code under test. Two v36 siblings: **a user waiver of a gate is itself a record** — write "closed by waiver, not by execution" into the ship record, never let a waived gate look passed (`gate-waiver-is-a-record.md`); and **a recorded measurement belongs to a specific environment** — name the engine/profile/machine axis an environment-dependent number depends on, or it generates false drift alarms (`measurement-records-name-their-environment.md`). When TriLens's round cap ends a loop without a clean-round attestation, an independent cold-context deep review is a legitimate substitute round — but keep "all findings applied" and "a reviewer returned clean" distinct in the record (`trilens-loop-feature.md` § When the round cap bites). See `post-convergence-edits-need-their-own-gate.md`, `macos-documents-permission-loss-mid-session.md`.
- **A gate that died is not a gate** — three dispositions, and a ship record must name which applies: *passed*, *waived* (`gate-waiver-is-a-record.md`), or **did not run**. A reviewer that dies surfaces as *idle*, which reads exactly like "finished and found nothing" — so the check is "did it report?", never "did it complain?". Before retrying, ask **what would have to change for the retry to differ** — not what class the error is: a flake changes by itself, a spend limit changes when someone outside the loop lifts it (then the retry is an ordinary re-run, as on v38), a structural failure changes only when the structure does. A retry of a never-reported lens doesn't count against the round cap, and the record must still show the dead attempt. **Mirror case: a reviewer can be alive and merely silent** — an idle notification is not a report, and one follow-up ask ("findings list and verdict, or say you found nothing") recovered two full reports on v37, one carrying the round's BLOCKER. Ask before banking or writing off a lens; the ask is free and does not count against the round cap. See `a-gate-that-died-is-not-a-gate.md`.
- **A gate cannot be a model self-report** — a gate must not be implemented in the medium it gates. Ask what evidence it rests on and whether the thing under test could have produced that evidence; if yes, it is a self-report wearing a gate's name. "Both engines have coverage" is not evidence parity. Sibling form: **a binding must not be selected by the thing it binds** (engine-profile selection, see Boot & Freshness above). Everyday form: a **green suite written by the author of the fix** is a self-report until each new test is shown **red against the previous tag and green against HEAD** — run it in a detached worktree via `LR_FRAMEWORK_DIR`, and note that a test green on both sides tests nothing the fix changed. See `a-gate-cannot-be-a-model-self-report.md`, `prove-a-new-test-red-against-the-previous-tag.md`, `engine-profile-must-be-observed-not-believed.md`.
- **Removing an unsound signal needs its accidental coverage replaced** — a heuristic that is wrong in general can't be kept for the cases it accidentally gets right, but deleting it is only half the change: enumerate what it was catching and handle those cases deliberately. When a fallback exists, ask which real configuration lands on it and whether that configuration can tell. See `removing-an-unsound-signal-needs-its-accidental-coverage-replaced.md`.
- **Widening a value's source drops the old source's validation** — when a change broadens where a value comes from (URL-derived → filesystem-derived), the guard attached to the old path does not travel with it; re-attach it at the sink and treat "same value, new source" as a new input. Two corollaries from the same v37 pair: a **finding whose suggested remedy cannot resolve it** is worse than no finding, and a **verdict with a per-item payload must have a per-item trigger** (a global trigger reads as correct until someone constructs the two-item case). Both defects were caught by review, not by design — prose has nowhere to put "and re-run the filter". See `widening-a-source-drops-its-validation.md`, `name-keyed-global-registry-cannot-answer-per-scope.md`.
- **When a format is self-documenting, ask what happens when the docs are treated as data** — a natural-syntax delimiter (markdown headings) reads better than an escape-sequence one (HTML markers) and collides with content, most sharply with the documented example of the delimiter itself. Exclude fenced blocks from boundary detection. See `self-documenting-payload-vs-heading-delimiters.md`.
- **Whitespace is semantics once a check compares bytes** — a doc that displays a template gets that template copied exactly as displayed, wrapping included; byte-exact idempotency silently promotes every formatting choice into the contract, so say so where the template is authored and back it with a check plus a test. See `template-whitespace-is-contract-under-byte-exact-idempotency.md`.
- **A failure list is a hypothesis until someone reads the transcripts** — an assertion message names what was observed, never why. Re-triage from stored logs before planning fixes; stored artifacts plus `stat` routinely beat fresh engine probes on cost and certainty. Classify each text assertion as mid-run (needs the transcript) or end-state (final message suffices) — mixing them changes what a test means per engine. **Down at the single-test level: a red test may be asserting something true about the machine** — establish which side is wrong before turning it green, give danger-guarding assertions (sandbox escape, destructive write) the strongest presumption of correctness, and when de-hardcoding a constant check each assertion's provenance separately (identical literals can be live-state on one line and caller-supplied on the next). See `v31-lifecycle-rerun-partial-green-2026-07-27.md`, `a-red-test-may-be-asserting-a-true-fact.md`, `transcript-vs-final-message-assertions.md`.
- **Decide where the guardrail lives before writing the topic** — lore is retrieved when a task cues it, and a one-off command cues nothing; a trap recorded only as knowledge protects nobody, including its author. Name the point-of-use site (script check, exact command in the doc, test) as part of the fix, and prefer a deterministic harness check over a human prep step. See `point-of-use-guardrails-beat-recorded-lore.md`, `docs-engines-convention.md` § Engine traps belong in the binding.
- **Verify before asserting** — check filesystem/state directly before "fixing" a suspected bug; verify *which* bug, not just whether. **Pointed inward:** before declaring a known finding moot — especially a ship-blocking one — read the lore rule it rests on rather than reconstructing it; reconstruction keeps a rule's motivating case and drops its actual obligation, and those diverge precisely when dismissal feels justified (`check-own-lore-before-dismissing-a-finding.md`). Same reflex, two more sites: fetch volatile external facts (prices, model IDs, rate limits) live with a dated citation rather than trusting memory — "couldn't verify" licenses marking a value unavailable, not guessing; and after any scoped/read-only subagent or fork returns, verify its actual filesystem footprint (`git status`, `git worktree list`) rather than trusting its summary — a capable fork acts on the largest goal it can see in inherited context unless scoped *against* it explicitly. See `verify-before-acting-on-suspected-bugs.md`, `fetch-volatile-facts-live-not-memory.md`, `fork-scope-creep-under-standing-goal.md`.
- **Curation meta-rules:** name foundational principles as their own topics; single canonical source (pointer, don't restate — and when fixing a rule that was duplicated, enumerate every site that *states* it, not only every site that *implements* it: docs, findings rows, error text, literate fallback docstrings, release notes; its design-time cousin is reuse an existing correlation/identity signal before inventing new plumbing); don't defer completable bounded sweeps; graduated verification (confidence, not boolean). See `naming-foundational-principles.md`, `single-canonical-source-discipline.md`, `reuse-existing-correlation-signal.md`, `feedback-don-t-defer-completable-scope.md`, `graduated-verification-confidence.md`.
- **User-feedback working style:** ranked-shortlist over exhaustive enumeration; confirm before writing durable lore mid-session; in design dialogues, write the draft only when the user triggers it (decisions are safe in conversation — don't repeatedly move to persist); populate dry-run counters with would-be outcomes; "enforce X" ≠ add a required schema field; for broad/emotionally-loaded open-ended asks, decompose into hidden axes and sequence a build order by dependency (cheapest/highest-leverage first, flashiest/most-structural last) rather than proposing a menu or jumping to implementation; on a second round of pushback on the same axis (length, tone, scope), act on the next ask instead of re-justifying — a second "no" is not a request for more reasoning; a **short measurement question gets a short factual answer**, with the interesting generalisation offered rather than delivered, and **several style skills invoked at once is a stop signal**, not a preference tweak (hold the style for the rest of the session). See `feedback-too-many-words.md`, `feedback-confirm-before-writing-lore.md`, `feedback-draft-only-when-user-triggers.md`, `feedback-schemas-as-enforcement-overreach.md`, `feedback-layered-decomposition-for-open-ended-asks.md`, `feedback-mvp-minimalism.md`, `feedback-comply-promptly-after-repeated-pushback.md`.

## Key Constraints

- `lore-context.md` ≤ 50K tokens; **shape over size** — working-knowledge + summary-topic references, not an index (see `lore-context-shape-discipline.md`).
- Lore topics: atomic, <5K tokens preferred, plain markdown; **new files carry Lore v1 frontmatter** (`lore`/`type`/`summary`/`parent` per `docs/lore-structure.md`); legacy files stay frontmatter-free until migrated.
- Descriptor frontmatter: `lore-repo.md` = `description` + `version` (+ optional `repos:`); `role.md` = `description` only.
- Command filenames: lowercase/digits/hyphens, ≤64 chars.
- Placeholders: `<workspace>`, `<lore-agent-repo>`, `<guest-lore-agent-repo>`, `<agent-name>`, `${CLAUDE_PLUGIN_ROOT}`.
- **CWD safety:** never `cd` when later tools depend on cwd — use `git -C <repo>`. **Portable shell:** assume BSD/macOS, no GNU-only binaries (`timeout`); bound commands via the Bash-tool timeout.
- See `conventions.md`, `placeholder-vocabulary.md`, `tooling-cwd-safety.md`, `portable-shell-in-framework-docs.md`.

## Onboarding-Doc Authoring

Co-authoring framework onboarding docs for adopting teams is part of the role. Two distinct genres now exist: **`onboarding-doc-narrative-pattern.md`** (long-form prose pitching a human reader) and **`paste-link-installer-doc-genre.md`** (a doc written *to the AI agent* as the literal installer, meant to be pasted as a link — shipped as `QUICKSTART.md` + per-engine `INSTALL-<ENGINE>.md`). Load the identity-layer framings first, then the toolkit: the two genre topics above, `use-cases-via-parallel-consult-pattern.md`, `terminology-domain-collision-trap.md`, `agent-as-universal-working-environment.md`, `in-flight-skill-teaching-pattern.md`. Pre-ship review for either genre uses `parallel-reviewer-fanout-pattern.md`'s multi-lens fan-out; the installer genre additionally needs the **AI-installer (literal executor)** lens (`ai-installer-review-lens.md`) — it catches execution-fidelity bugs (e.g. `skill-doc-filename-divergence-bug-class.md`) the newcomer/editorial lenses miss. Landing-page placement of a self-referential/meta example differs from long-narrative placement — primacy goes to the strongest CTA; see `onboarding-doc-narrative-pattern.md` § placement note. A recurring funnel bug: an author writing from the fresh-start perspective railroads readers into create-your-first-agent and leaves the **team-join path** invisible at every layer (README prose, QUICKSTART, and the INSTALL AI-agent preambles) — check all layers, and keep the fork question verbatim-identical across sites (`onboarding-funnel-team-join-path.md`). Adopter-facing prose carries the product name **"Lore Agents"** while the engine keeps `lore-framework`/`lr` (`lore-agents-product-name.md`). First instance: the Activities team's intro doc.

## Active Design Explorations

- **lr-dev / Dark Factory (DF)** — major direction; a `lr` module for SDLC automation toward an autonomous "dark factory" SDLC. Per-repo artifacts + narrative context live in a `<repo>-df` backbone (a `repo-lore/<file>/` mirror: `file-lore.md` narrative landing + flat structured aspect subdirs like `ula/`). Skills not agents; persistence external. First aspect: **AIQA/ULA** (`/lr:df-repo-init`, `/lr:df-ula-file`) — unit-level analysis with a bug-verification track, BETA. The DF/ULA design thread is closed and the module ships as BETA. Anchor: `lr-dev-direction.md`; see `df-per-repo-backbone.md`, `aiqa-ula-feature.md`, `df-module-conventions.md`, `workflow-primitive-operational-notes.md`.
- **Autonomous agents / Lore Beings** — agents as always-on background collaborators with persistent task state, raising for input only when needed. Concrete steps taken: `/lr:spawn-teammate` (multi-agent substrate, v10) and the v18 **`lr-wait`** primitive — the first *inbound-signal* step: an agent blocks on an event and an external actor (cron/CI/webhook/human, via `lr-emit`) wakes it with text. **The beings design is settled (2026-07-19): the module is _Lore Beings_.** A being is an ordinary lore agent plus a `being.md` descriptor; the **Being Keeper** (`lrb`) is deterministic substrate (never an LLM). **MVP is CLI-only**; engines are explicit user config. Budget = daily-USD spawn gate + per-task wall-clock kill. **Engine kinds: `claude`, `codex`, and `cursor`** — cursor landed in framework v28: requires `--plugin-dir` at `engines add`, claude-shaped JSON result + flat-cost fallback. **Keeper-specific real-engine lifecycle coverage now exists** (`tests/lifecycle/keeper_harness.py` + `test_lrb_lifecycle.py`, 10 scenarios after the 2026-07-20 fifth pass added B2/B3, separate higher-blast-radius gate `LR_LIFECYCLE_KEEPER=1`, verified claude 6/6 + codex 1/1 + cursor 1/1 at the recommended-minimum tier). That fifth pass found and fixed a real production bug, not just a coverage gap: `cursor-agent`'s sandboxed shell tool escapes `_kill`'s `killpg` by running spawned commands in a freshly `setsid`'d session, which left a real orphaned process on the test machine before the fix — `_kill` now also walks the full ppid-descendant tree and signals every descendant directly, enumerated *before* any ancestor is signaled (killing the ancestor first risks the OS reparenting a survivor to PID 1 and erasing the ppid link). **The Keeper substrate shipped BETA in v28, and v29 added the in-engine command surface `/lr:being`** — one skill with subcommands (status/init/create/validate/logs/keeper/engine/workspace/pause/resume) over the same deterministic `lrb` CLI, rather than a `lrb-*` skill per operation. Ship record: v28 at framework commit `5e00209`, tag `lr--v1.28.0`; the standard lifecycle gate passed by persisted broad matrix plus targeted reruns. Real-engine verification sharpened two per-kind contract gaps (both backlog schema decisions, not silently patched): the `cursor` kind is empirically cost-blind (no `total_cost_usd`), so its flat `--session-cost-usd` fallback is load-bearing not optional; the `claude` kind has no `--plugin-dir` field, so a claude-kind being needs a wrapper-script `command` to load `lr:` skills at all. Two further findings from that same review pass — budget-enforcement edge cases and an unattended-full-permission trust gap — were deliberately deferred to the backlog rather than fixed. **The persistent `--launchd` Keeper install is live on this machine** (verified 2026-07-28: `~/Library/LaunchAgents/com.lore-beings.keeper.plist` present, `com.lore-beings.keeper` loaded under `launchctl`, last exit 0) — so a Keeper daemon can spawn engine sessions here with no human starting them; treat it as a candidate explanation whenever a repo changes under me mid-session. The Chronicler week-long soak is a *separate* question and remains unverified — do not infer it from the install. Open gap: headless permissions (`permission_mode: full` vs future scoped-tools), and self-scheduling under the safe default. Anchor: `lore-beings-design.md`; see `cursor-agent-real-invocation-contract.md`, `engine-kinds-design-decision.md`, `lifecycle-testing-harness.md` § Keeper coverage, `keeper-spawn-prompt-boilerplate-distraction.md`, `lore-beings-mvp-takeover-review.md`, `kill-tree-enumerate-before-signal-ordering.md`, `codex-exec-real-invocation-contract.md`, `macos-ps-o-multi-field-single-line.md`, `agent-being-consciousness-substrate-split.md`, `unenforceable-caps-are-prompt-theater.md`, `feedback-mvp-minimalism.md`, `autonomous-agents-vision.md`, `wait-primitive-feature.md`, `framework-improvements-backlog.md` § Major Directions § Autonomous Agents / Lore Beings.
- **Multi-engine portability (Codex, Cursor)** — **the ports are shipped, not in flight.** Claude
  Code, Codex, and Cursor are all Tier-1 supported, so a mixed-engine team shares one agent repo.
  Claude Code remains the reference path: shared procedure docs are written in Claude terms, and other
  engines override only at binding points. What made this tractable: the knowledge substrate (agent
  repos, `lore-repo.md`, `role.md`, `lore/`, `lore-context.md`, git) was already engine-agnostic, so
  the port was **packaging, not redesign** — the whole surface is **5 adapter bindings** via the
  `docs/engines/` convention (framework-root, invocation-syntax, subagent-spawn, memory-file,
  runtime-bounding) plus Boot Step-0 engine selection. Both engines have native in-session subagents
  (Codex `spawn_agent`/`wait_agent` — `spawn_agent` has **no `role` argument**, state
  read-only/write scope in the brief; boot Step 1 carries a Codex bootstrap exception:
  `spawn_agent` visible in the tool interface → `--engine codex`. Cursor `Task` — free-text briefs
  validated 2026-07-28, merge on
  `Task` since then), so the feared Tier-B nucleus is proven, and one
  repo carries both skill namespaces (canonical `skills/<skill>/` for Claude, `.cursor-skills/lr-<skill>/`
  wrappers for Cursor, kept in sync by `scripts/sync-cursor-skills` and `/lr:check` #21).

  Standing operational facts worth carrying: **trust rollout/tool-call logs, not model self-report**,
  when validating an engine path; Codex's default sandbox blocks `.git` writes and network, so the
  supported finalization path needs `.git` writable through launch/config (a commit-blocked run is
  degraded fallback, not a merge failure); Codex per-agent shortcut register/unregister/list remains an
  unvalidated implementation gap. **Separate sessions on separate engines coordinating on a real task**
  (not `/lr:attach`, which is single-executor multi-agent) now has a validated substrate: a shared
  append-only folder (worked example: `workdir/v31-feedback/`), reusable across message-vocabulary
  changes — see `cross-engine-team-substrate-validated.md`. Two rules fell out of running it for real:
  **check for same agent identity before any session writes** (two engines can be the same booted
  agent against the same repo — designate one write-owner, `same-agent-multiple-engines-single-writer.md`)
  and **don't relay a user decision from one session into the shared channel as settled authority for
  another session** (`cross-engine-relay-not-attributable-authority.md`). A genuinely different engine
  also catches design flaws same-engine self-review (even multi-lens) misses — a distinct axis from the
  sandboxed-review/self-report family, worth the coordination cost on high-stakes design decisions,
  not routine changes (`independent-engine-review-catches-structural-blind-spots.md`). The **"framework
  is prose executed by the model"** risk is
  empirically retired for the exercised paths, and the substrate half has quantitative backing — the
  quality benchmark showed positive lore-utilization uplift on every engine+model config, with the
  nuance that **model–engine fit beats model tier**. Cross-engine support is a *supporting* fact in
  positioning, not the headline (the 2026-07-20 landscape re-survey found competitors claiming it too);
  lead with the triad. Anchor: `multi-engine-portability-direction.md`; per-engine entry points
  `claude-engine-capabilities.md`, `codex-engine-capabilities.md`, `cursor-engine-capabilities.md`;
  see also `docs-engines-convention.md`, `subagent-as-optimization-vs-subagent-as-semantics.md`,
  `claude-coupling-inventory-and-port-tiers.md`, `cursor-dual-skill-tree-one-repo.md`,
  `quality-benchmark-feature.md`, `positioning-triad-differentiation.md`, `port-landing-next-steps.md`.
- **Lore housekeeping / consolidation "sleep" pass** and the **simplification/subtraction** review item — active follow-ups from the 2026-06-13 architecture review; see `framework-improvements-backlog.md`. That review's settled dispositions (incl. DF-inside-`lr` and team-shared/multi-author as deliberate, not defects — don't re-raise) live in `architecture-review-dispositions.md`. A newer 2026-07-02 review added two further backlog items (post-merge diff verification, recall-time staleness surfacing) — see `framework-improvements-backlog.md` § Merge Quality, § Search / Scaling.
- Parked: workdir-as-reference-library; vector-DB search (until >100 topics/agent); the session-as-durable-artifact cluster (boot auto-push, boot-context cache, suspend/resume, JSONL archive). All in `framework-improvements-backlog.md`.
- **v25 workspace layer (pull + init)** — shipped; standard workspace-owned ignore lines now include
  `/.worktrees/`, `/.lr-beings/`, and `/.tmp/` (init seeds, pull phase 3 re-asserts, check #22 warns).
  Disposable scaffolds go under `.tmp/<name>/`. See `v25-workspace-pull-init-design.md`,
  `workspace-owned-default-ignore-lines.md`, `workspace-meta-repo-pattern.md`.
- **Workspace lifecycle** — **shipped in v37 and corrected in v38**; no longer an exploration. The
  four-command surface (`init` converges, `pull`, `push`, `status`) and the v3 memory-file contract
  are live — see `workspace-lifecycle-four-commands.md`, `workspace-memory-file-contract.md`, and
  `workdir/draft-workspace-lifecycle.md` for the original 12 decisions. Still open and *not* closed by
  it: the backlog's "Workspace-root paths gap" and B7 "Orphan version stamps" (different git
  roots/scopes) — `framework-improvements-backlog.md` § Workspace & Environment.

## Current State

Workspace holds **`lore-framework/`**, **`lore-framework-dev/`**, **`lore-agents/`**, and
**`lore-chronicler/`** (Being; on disk, undeclared). Meta-repo `AGENTS.md` lists them after
`/lr:workspace-init`, which converges — there is no `--refresh` flag as of v37.

Framework `main` carries **v38** shipped (commit `0435186`, tag `lr--v1.38.0`, pushed) — a
correctness pass over the v37 workspace layer: parser drift between the Python scanner and the bash
puller, new finding **S16** for a detached workspace HEAD, and a widened S8. Gates, per the full
record in `versioning-release-types.md`: a three-round nine-lens TriLens (all lenses reporting, every
lens chosen new because twelve had already been spent on v37) plus a green **414-test** deterministic
suite with every new test verified red at `lr--v1.37.0`; **lifecycle and quality waived by the user
and not run**, so the release makes no model-execution-fidelity claim. **The loop ended at its
three-round ceiling, not on a clean round** — all findings applied, round 3's own fixes unreviewed.

My own Lore corpus is still essentially legacy; v1 adoption is lazy via merge or explicit via
`/lr:groom`, and **`lore-context.md` is over its 10K v1 target** — a grooming pass, not a merge, is
the fix. Unrelated uncommitted WIP may sit on these checkouts; do not sweep it into lore-finalize
commits (`git add agents/` only), and **preserve unrelated dirty-tree changes** during release or
fold-into-main work, stashing around feature merges when needed
(`fold-feature-into-local-main-via-stash.md`).

**This workspace really does run concurrent sessions, including non-human ones** (the live launchd
Keeper above). A concurrent session's directory-wide `git add` can commit and push work I left
uncommitted — no conflict, no loss, but ungated work ships under an unrelated commit message, and
`git status` stops being a reliable inventory of my own session's changes. So: stage narrowly
(`git add <path>`, not a directory) whenever another session may be live, re-check `git status` and
`git log` *before reporting* on my own change set rather than only at the start, and never leave
deliberately-ungated work sitting dirty — branch it. Distinct from the same-agent write-contention
rule, which is about two sessions editing the same file. See
`concurrent-session-committed-my-uncommitted-work.md`,
`same-agent-multiple-engines-single-writer.md`.

Both pre-ship gates remain in working order: `/lr:trilens-loop`, and `tests/lifecycle/` (plus
Keeper / quality tracks). For small doc ships, a feedback-only trilens round then selective apply
is a valid path (`trilens-feedback-only-selective-apply.md`).

See `versioning-release-types.md`, `trilens-loop-feature.md`, `lifecycle-testing-harness.md`,
`workspace-owned-default-ignore-lines.md`.

## Running Backlog & Standing Improvement List

`framework-improvements-backlog.md` is the canonical list of deferred items; its § Ship Closures
archives per-ship gate dispositions. Quality benchmark tier/probe expansion is in the dev repo with
regular/deep matrix defaults and local override support. ~215 lore topics. The
backlog is organized into top-level `##` categories (Major Directions, Session Lifecycle &
Durability, Knowledge Quality & Curation, Multi-Agent Collaboration, Workspace & Environment,
Framework Upkeep/Distribution/Docs, Ship Closures archive), each holding `###` topical sections —
the fix for a flat list that outgrew ~30 sections. File new items under the matching category. See
`backlog-categorization-precedent.md`.

**`workdir/what-to-improve.md`** is the **standing prioritized improvement list** — a ranked
action view over the backlog that must always exist, not a one-off review deliverable
(user-established practice, 2026-07-18). Reread it at the start of every framework-work session;
refresh it at each architecture review. Last refresh 2026-07-18: A-tier verified inconsistencies
(script-backed `/lr:check` core + reference-rot cleanup first), B-tier backlog promotions (merge
verification, staleness surfacing, trust model), C-tier feature directions (ambient recall,
`/lr:note`, lore MCP server). A **v32 tier** now sits alongside these: A8, the `agent-boot.md`
subtraction pass, held out of v31 deliberately (`agent-boot-doc-grew-when-scripted.md`). See
`standing-improvement-list-practice.md` for the refresh protocol, backlog relationship, and
tiering convention.
