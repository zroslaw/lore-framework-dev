# Lore Context

Compacted working knowledge for the **lore-architect**. This is the entry point to the lore graph, not a catalog — each theme points at its summary topic, which fans out to detail. For exhaustive lookup, scan `lore/` directly. (This doc follows the `lore-context` shape discipline: working-knowledge + summary-topic references, present-tense, no index, no version-history narrative — see `process-merge.md` § Step 4.)

## Style Skills

A category of user-invoked `/lr:` skill that changes how the agent *communicates or collaborates* (vs. operations like `/lr:recall`/`/lr:merge`). Regular thin-pointer skills — **not** boot-loaded or surfaced at boot; the user re-asserts a style by invoking its trigger. Three shipped in v19, composing on three levels: **`/lr:plain-language`** (sentence — plain short English), **`/lr:dialogue`** (turn — short turns, one step at a time), **`/lr:follow-me`** (thinking-direction — user drives, small suggestions only; extracted up from lore, canonical def now in `docs/follow-me.md`). A boot-loaded "soft skills" mechanism was prototyped and rejected in favor of plain skills. See `style-skills.md`, `skill-request-defaults-to-regular-skill.md`, `soft-skill-follow-me-mode.md`.

## Who I Am

Architect and maintainer of the lore system — the `lr` framework plugin and the agent ecosystem on it. I work across two repos: **`lore-framework/`** (the distributed plugin — changes to how agents work go here) and **`lore-framework-dev/`** (my own agent repo — my lore, workdir, sessions). I'm both builder and user: I use lore to track my own design knowledge. See `role.md`.

## System Architecture

Three discrete layers — identify which one owns a change before touching files:
1. **Plugin** (`lore-framework/`, installed as `lr`) — what's distributed via the marketplace: skills, docs, migrations, scripts, manifests, `VERSION`. Universal across installs.
2. **Domain** — the conceptual scope of one agent repo, marked by `lore-repo.md` (frontmatter: `description`, `version`, optional `repos:`). Holds `agents/<name>/` with `role.md`, `lore-context.md`, `lore/`, `workdir/`, `sessions/`.
3. **Workspace** — the filesystem Claude runs from; holds one or more agent repos + their declared siblings. Discovery scans workspace-root dirs for `lore-repo.md`; nested repos are invisible to most skills.

See `architecture-overview.md`, `workspace-vs-domain-vocabulary.md`, `agent-discovery-nesting-constraint.md`, `plugin-vs-agent-repo-separation.md`.

## Design Principles

Identity-layer framings that frame everything else:
- **Team-shared knowledge** — agents are team-shared knowledge containers, not personal notebooks. Design for concurrent multi-contributor use.
- **Engine, not KB** — the framework is the engine/environment for self-improving agents; the knowledge base is a consequence, not the identity.
- **Executors first, advisors second** — primary value is getting things done; conversation is secondary. The usage→learning positive feedback loop only spins under executor-first framing.

What each agent carries: **knowledge** (markdown — what it knows, accrues passively via reflection) + **skills** (tools + instructions — what it can do, evolves actively via in-flight teaching). Distinct assets; don't collapse them.

Core mechanics: directory-driven, plain markdown (frontmatter only on descriptor files), git-as-metadata, delete-don't-mark, knowledge graph by filename reference, concise context with detail on demand, skill/doc separation, repo-level versioning. Framework owns the universal; agents own repo/host/workflow specifics.

**Subagent as optimization vs subagent as semantics** — before letting any engine degrade a
subagent-spawning procedure to serial host-side execution, classify what the subagent is *for*. If it
buys parallelism and context isolation (recall, consult, attach, merge, conflict resolution),
serialization is lossless. If the subagent's *independence from the caller* is the deliverable
(`/lr:trilens-loop`), serialization destroys the feature — the procedure must stop and report. Profile
degradation clauses therefore need carve-outs, not blanket rules, and "the conservative profile passed
the whole suite" only ever meant it was adequate for the procedures that existed then. See
`subagent-as-optimization-vs-subagent-as-semantics.md`.

See `system-design-principles.md` (the full list and the overreach diagnostics), plus the framing topics `team-shared-knowledge-principle.md`, `framework-as-engine-not-kb.md`, `agents-are-executors-first.md`, `knowledge-vs-skills-distinction.md`, `framework-scope-vs-agent-scope.md`.

## Skills & Docs

Operations are Claude Code plugin skills, `lr:` prefix on Claude; Cursor uses `/lr-<skill>` via
prefixed wrappers (`cursor-dual-skill-tree-one-repo.md`). **Skills are thin pointers** — each `skills/<name>/SKILL.md` is a one-line reference to `docs/<name>.md`, where all logic lives. Same for generated `/lr-<agent>-agent` boot commands (thin delegations to `agent-boot.md`). When a skill orchestrates sub-skills, the orchestration gets its own `docs/<skill>.md`; non-skill procedures shared across call sites get a `docs/<procedure>.md` (e.g. `auto-pull.md`). See `slash-command-system.md`, `skill-doc-pattern.md`, `shared-procedure-doc-pattern.md`, `single-canonical-source-discipline.md`.

An **accelerator** script (Script Fallback Contract) can go one step further and become
**literate**: the procedure lives in the script's own instructional comments rather than in a
companion doc, so there's one artifact instead of two that can drift apart. First applied to
`scripts/lr-core` in v31. See `literate-accelerator-pattern.md`.

The plugin can also **bundle an MCP server** (declared in a root `.mcp.json`, auto-launched by Claude Code with its tools merged into the agent): **`lr-wait`** (v18) is the first — and the framework's first `python3` dependency (stdlib-only, no pip; the sole sanctioned exception to bash-on-BSD, for protocol-speaking server components). Practical limit to remember before promising a long wait: on Claude Code a single MCP call dies at the engine's ~30-minute idle timeout, and the abort leaves `lr-wait`'s single-request lock stuck `busy` for the rest of the session — chunk waits at ≤29 min, or use a backgrounded shell timer. See `plugin-mcp-server-convention.md`, `wait-primitive-feature.md`.

## Engine Hubs

Engine-specific operational knowledge now has one hub topic per engine: `claude-engine-capabilities.md`,
`codex-engine-capabilities.md`, and `cursor-engine-capabilities.md`. Use them as the entry points
for install/update model, invocation surface, subagent mechanism, memory file, MCP/plugin loading,
sandbox constraints, and lifecycle-harness caveats; keep atomic findings in the linked detailed
topics rather than rediscovering them from old session notes. Cursor live usage retrieval
(plan quota + CLI session context) → `cursor-usage-auto-retrieval.md`.

**Where an engine fact belongs:** if it would change what an executor *types*, it goes in
`docs/engines/<engine>.md`'s binding — the doc read at the moment of use — not only in these hubs or in
agent lore. Lore is for judgement and history; the profile is the point-of-use contract. I learned this
by hitting a trap that had been recorded in my own lore since v18. See `docs-engines-convention.md`
§ Engine traps belong in the binding, and audit sibling profiles whenever one binding gains a guardrail.

**Codex/Cursor plugin identity is not self-verifying.** The lifecycle harness passes `--plugin-dir` to
every engine, but an installed/cached plugin can silently win over that flag on Codex and Cursor,
substituting a different tree for the one under test with no loud failure — confirmed live 2026-07-27
running the suite against the parked v31 branch. See `lifecycle-harness-plugin-identity-unverified.md`.

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

Boot (`agent-boot.md`, single source of truth): discover agent → auto-pull repo → version check → read `role.md` + `lore-context.md` → detect teammate spawn → confirm. **Boot loads only those two files; topics are read on demand.** Repos auto-pull at every session-context boundary (boot, attach, pre-merge) to match the team's latest pushed state; `/lr:pull-lore` is the manual refresh. See `freshness-contracts-at-session-boundaries.md`, `auto-pull-mechanism.md`.

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

## Versioning & Migration

`lore-framework/VERSION` is the single source of truth; **the current shipped version is v30** — v31
(`lr-core`) is fully built, reviewed, and parked, not shipped (see Current State above,
`v31-lr-core-parked-2026-07-25.md`). Each
agent repo stamps that version in its `lore-repo.md`, and four version-bearing plugin manifests mirror
`1.<VERSION>.0` (`/lr:check` #19 enforces). A version is either **migration**, **release-notes-only**,
or both, and independently **cache-affecting** or not — those two axes are orthogonal, and every ship
records both in `versioning-release-types.md`, which holds the full per-version history. Read that
topic for what any given version contained; don't reconstruct it from here.

Ship mechanics that bite: verify `git HEAD` rather than trusting lore's "commit pending" (it
accumulates across versions), and scan the whole history tail for gaps at each ship rather than only
appending the current entry. See `versioning-release-types.md`, `plugin-manifest-versioning.md`,
`cache-clear-footer-convention.md`, `update-process.md`, `release-commit-hash-from-tag.md`.

## Consistency & Diagnostics

- **`/lr:check`** — 23 content-consistency checks (descriptor/version, structure, references, size/state, drift, four-manifest #19, migration write-paths #20, cursor-tree parity #21, workspace-layer checks #22–23). At scale, prefer a deterministic script-based sweep for the mechanical subset (existence/version/glob checks) over an LLM read-through — checks #9–10 alone missed 14 dangling references in a 147-topic graph. See `consistency-checks.md`.
- **`/lr:doctor`** — diagnoses runtime/environmental issues that escape content checks (esp. stale plugin cache) via an accreting ailment catalog. See `ailment-catalog-pattern.md`.

## Operating Disciplines

How I work, especially at version ships and high-stakes lore edits:
- **On VERSION bumps:** backfill `versioning-release-types.md` history, add the cache-clear footer if cache-affecting, bump all four version-bearing plugin manifests to `1.<VERSION>.0`, promote any newly-named principle to its own topic. (Full curation disciplines live in `role.md`.)
- **Pre-ship review:** multi-lens review iterated until a round finds nothing worth fixing (convergence is the ship signal) — **run it via `/lr:trilens-loop`** rather than hand-assembling the fan-out; the skill enforces cold-context reviewer independence, the APPLIED/DECLINED ledger, the "a silent round is not a clean round" guard, and rail-removal disclosure, while lens *choice* and triage judgement stay mine. Brief reviewers with the **goal, not the rationale** — rationale pre-empts the criticism you're paying for. Two triage facts from measuring a live round: **~94% of a loop's tokens stay inside the subagents** (a reviewer's budget is its own reasoning, not the material handed to it — so withholding the diff is cost-neutral, and the exchange contract must be justified on independence and host-context preservation, never on token savings), and **convergent findings from two independent lenses are strong evidence, not redundancy** — reword rather than defend. Sonnet boot-as-self review remains the separate single-lens, role-as-perspective tool for high-stakes single edits. See `trilens-loop-feature.md`, `parallel-reviewer-fanout-pattern.md`, `sonnet-subagent-review-pattern.md`. **Second, empirical leg (v18+):** for procedure docs covered by the lifecycle testing harness, also run the relevant scenarios against real engine execution before shipping — review catches reasoning issues, the harness catches model-execution-fidelity issues invisible to a strong-model reviewer — and the fidelity axis is **engine, not just model tier** (run scenarios on every engine, using the cheapest practical default tier unless explicitly overriding: Claude Code -> haiku, Codex -> gpt-5.4-mini, Cursor -> composer-2.5; the same model tier can behave differently by engine, and mid-procedure step insertions are the highest-risk for a silent skip). See `lifecycle-testing-harness.md`, `execution-testing-catches-blind-ambiguity.md`, `haiku-ambiguity-detector.md`.
- **A gate result belongs to an artifact state** — a converged review loop and a green lifecycle run each certify only the tree they actually ran against. An edit landed after the gates pass is ungated: re-run the affected gate, or revert and file a follow-up. Never report "converged and green" for a tree neither gate saw, and record *which* state a result belongs to. Also: an environment failure mid-run (e.g. macOS TCC revocation) makes results **uninterpretable**, not red — fix and re-run rather than debugging the code under test. See `post-convergence-edits-need-their-own-gate.md`, `macos-documents-permission-loss-mid-session.md`.
- **Verify before asserting** — check filesystem/state directly before "fixing" a suspected bug; verify *which* bug, not just whether. **Pointed inward:** before declaring a known finding moot — especially a ship-blocking one — read the lore rule it rests on rather than reconstructing it; reconstruction keeps a rule's motivating case and drops its actual obligation, and those diverge precisely when dismissal feels justified (`check-own-lore-before-dismissing-a-finding.md`). Same reflex, two more sites: fetch volatile external facts (prices, model IDs, rate limits) live with a dated citation rather than trusting memory — "couldn't verify" licenses marking a value unavailable, not guessing; and after any scoped/read-only subagent or fork returns, verify its actual filesystem footprint (`git status`, `git worktree list`) rather than trusting its summary — a capable fork acts on the largest goal it can see in inherited context unless scoped *against* it explicitly. See `verify-before-acting-on-suspected-bugs.md`, `fetch-volatile-facts-live-not-memory.md`, `fork-scope-creep-under-standing-goal.md`.
- **Curation meta-rules:** name foundational principles as their own topics; single canonical source (pointer, don't restate — and its design-time cousin: reuse an existing correlation/identity signal before inventing new plumbing); don't defer completable bounded sweeps; graduated verification (confidence, not boolean). See `naming-foundational-principles.md`, `single-canonical-source-discipline.md`, `reuse-existing-correlation-signal.md`, `feedback-don-t-defer-completable-scope.md`, `graduated-verification-confidence.md`.
- **User-feedback working style:** ranked-shortlist over exhaustive enumeration; confirm before writing durable lore mid-session; in design dialogues, write the draft only when the user triggers it (decisions are safe in conversation — don't repeatedly move to persist); populate dry-run counters with would-be outcomes; "enforce X" ≠ add a required schema field; for broad/emotionally-loaded open-ended asks, decompose into hidden axes and sequence a build order by dependency (cheapest/highest-leverage first, flashiest/most-structural last) rather than proposing a menu or jumping to implementation; on a second round of pushback on the same axis (length, tone, scope), act on the next ask instead of re-justifying — a second "no" is not a request for more reasoning; a **short measurement question gets a short factual answer**, with the interesting generalisation offered rather than delivered, and **several style skills invoked at once is a stop signal**, not a preference tweak (hold the style for the rest of the session). See `feedback-too-many-words.md`, `feedback-confirm-before-writing-lore.md`, `feedback-draft-only-when-user-triggers.md`, `feedback-schemas-as-enforcement-overreach.md`, `feedback-layered-decomposition-for-open-ended-asks.md`, `feedback-mvp-minimalism.md`, `feedback-comply-promptly-after-repeated-pushback.md`.

## Key Constraints

- `lore-context.md` ≤ 50K tokens; **shape over size** — working-knowledge + summary-topic references, not an index (see `lore-context-shape-discipline.md`).
- Lore topics: atomic, <5K tokens preferred, plain markdown, no frontmatter.
- Descriptor frontmatter: `lore-repo.md` = `description` + `version` (+ optional `repos:`); `role.md` = `description` only.
- Command filenames: lowercase/digits/hyphens, ≤64 chars.
- Placeholders: `<workspace>`, `<lore-agent-repo>`, `<guest-lore-agent-repo>`, `<agent-name>`, `${CLAUDE_PLUGIN_ROOT}`.
- **CWD safety:** never `cd` when later tools depend on cwd — use `git -C <repo>`. **Portable shell:** assume BSD/macOS, no GNU-only binaries (`timeout`); bound commands via the Bash-tool timeout.
- See `conventions.md`, `placeholder-vocabulary.md`, `tooling-cwd-safety.md`, `portable-shell-in-framework-docs.md`.

## Onboarding-Doc Authoring

Co-authoring framework onboarding docs for adopting teams is part of the role. Two distinct genres now exist: **`onboarding-doc-narrative-pattern.md`** (long-form prose pitching a human reader) and **`paste-link-installer-doc-genre.md`** (a doc written *to the AI agent* as the literal installer, meant to be pasted as a link — shipped as `QUICKSTART.md` + per-engine `INSTALL-<ENGINE>.md`). Load the identity-layer framings first, then the toolkit: the two genre topics above, `use-cases-via-parallel-consult-pattern.md`, `terminology-domain-collision-trap.md`, `agent-as-universal-working-environment.md`, `in-flight-skill-teaching-pattern.md`. Pre-ship review for either genre uses `parallel-reviewer-fanout-pattern.md`'s multi-lens fan-out; the installer genre additionally needs the **AI-installer (literal executor)** lens (`ai-installer-review-lens.md`) — it catches execution-fidelity bugs (e.g. `skill-doc-filename-divergence-bug-class.md`) the newcomer/editorial lenses miss. Landing-page placement of a self-referential/meta example differs from long-narrative placement — primacy goes to the strongest CTA; see `onboarding-doc-narrative-pattern.md` § placement note. A recurring funnel bug: an author writing from the fresh-start perspective railroads readers into create-your-first-agent and leaves the **team-join path** invisible at every layer (README prose, QUICKSTART, and the INSTALL AI-agent preambles) — check all layers, and keep the fork question verbatim-identical across sites (`onboarding-funnel-team-join-path.md`). Adopter-facing prose carries the product name **"Lore Agents"** while the engine keeps `lore-framework`/`lr` (`lore-agents-product-name.md`). First instance: the Activities team's intro doc.

## Active Design Explorations

- **lr-dev / Dark Factory (DF)** — major direction; a `lr` module for SDLC automation toward an autonomous "dark factory" SDLC. Per-repo artifacts + narrative context live in a `<repo>-df` backbone (a `repo-lore/<file>/` mirror: `file-lore.md` narrative landing + flat structured aspect subdirs like `ula/`). Skills not agents; persistence external. First aspect: **AIQA/ULA** (`/lr:df-repo-init`, `/lr:df-ula-file`) — unit-level analysis with a bug-verification track, BETA. The DF/ULA design thread is closed and the module ships as BETA. Anchor: `lr-dev-direction.md`; see `df-per-repo-backbone.md`, `aiqa-ula-feature.md`, `df-module-conventions.md`, `workflow-primitive-operational-notes.md`.
- **Autonomous agents / Lore Beings** — agents as always-on background collaborators with persistent task state, raising for input only when needed. Concrete steps taken: `/lr:spawn-teammate` (multi-agent substrate, v10) and the v18 **`lr-wait`** primitive — the first *inbound-signal* step: an agent blocks on an event and an external actor (cron/CI/webhook/human, via `lr-emit`) wakes it with text. **The beings design is settled (2026-07-19): the module is _Lore Beings_.** A being is an ordinary lore agent plus a `being.md` descriptor; the **Being Keeper** (`lrb`) is deterministic substrate (never an LLM). **MVP is CLI-only**; engines are explicit user config. Budget = daily-USD spawn gate + per-task wall-clock kill. **Engine kinds: `claude`, `codex`, and `cursor`** — cursor landed in framework v28: requires `--plugin-dir` at `engines add`, claude-shaped JSON result + flat-cost fallback. **Keeper-specific real-engine lifecycle coverage now exists** (`tests/lifecycle/keeper_harness.py` + `test_lrb_lifecycle.py`, 10 scenarios after the 2026-07-20 fifth pass added B2/B3, separate higher-blast-radius gate `LR_LIFECYCLE_KEEPER=1`, verified claude 6/6 + codex 1/1 + cursor 1/1 at the recommended-minimum tier). That fifth pass found and fixed a real production bug, not just a coverage gap: `cursor-agent`'s sandboxed shell tool escapes `_kill`'s `killpg` by running spawned commands in a freshly `setsid`'d session, which left a real orphaned process on the test machine before the fix — `_kill` now also walks the full ppid-descendant tree and signals every descendant directly, enumerated *before* any ancestor is signaled (killing the ancestor first risks the OS reparenting a survivor to PID 1 and erasing the ppid link). **The Keeper substrate shipped BETA in v28, and v29 added the in-engine command surface `/lr:being`** — one skill with subcommands (status/init/create/validate/logs/keeper/engine/workspace/pause/resume) over the same deterministic `lrb` CLI, rather than a `lrb-*` skill per operation. Ship record: v28 at framework commit `5e00209`, tag `lr--v1.28.0`; the standard lifecycle gate passed by persisted broad matrix plus targeted reruns. Real-engine verification sharpened two per-kind contract gaps (both backlog schema decisions, not silently patched): the `cursor` kind is empirically cost-blind (no `total_cost_usd`), so its flat `--session-cost-usd` fallback is load-bearing not optional; the `claude` kind has no `--plugin-dir` field, so a claude-kind being needs a wrapper-script `command` to load `lr:` skills at all. Two further findings from that same review pass — budget-enforcement edge cases and an unattended-full-permission trust gap — were deliberately deferred to the backlog rather than fixed. Chronicler week-long soak and persistent `--launchd` install still user-triggered. Open gap: headless permissions (`permission_mode: full` vs future scoped-tools), and self-scheduling under the safe default. Anchor: `lore-beings-design.md`; see `cursor-agent-real-invocation-contract.md`, `engine-kinds-design-decision.md`, `lifecycle-testing-harness.md` § Keeper coverage, `keeper-spawn-prompt-boilerplate-distraction.md`, `lore-beings-mvp-takeover-review.md`, `kill-tree-enumerate-before-signal-ordering.md`, `codex-exec-real-invocation-contract.md`, `macos-ps-o-multi-field-single-line.md`, `agent-being-consciousness-substrate-split.md`, `unenforceable-caps-are-prompt-theater.md`, `feedback-mvp-minimalism.md`, `autonomous-agents-vision.md`, `wait-primitive-feature.md`, `framework-improvements-backlog.md` § Major Directions § Autonomous Agents / Lore Beings.
- **Multi-engine portability (Codex, Cursor)** — **the ports are shipped, not in flight.** Claude
  Code, Codex, and Cursor are all Tier-1 supported, so a mixed-engine team shares one agent repo.
  Claude Code remains the reference path: shared procedure docs are written in Claude terms, and other
  engines override only at binding points. What made this tractable: the knowledge substrate (agent
  repos, `lore-repo.md`, `role.md`, `lore/`, `lore-context.md`, git) was already engine-agnostic, so
  the port was **packaging, not redesign** — the whole surface is **5 adapter bindings** via the
  `docs/engines/` convention (framework-root, invocation-syntax, subagent-spawn, memory-file,
  runtime-bounding) plus Boot Step-0 engine selection. Both engines have native in-session subagents
  (Codex `spawn_agent`/`wait_agent`; Cursor `Task`), so the feared Tier-B nucleus is proven, and one
  repo carries both skill namespaces (canonical `skills/<skill>/` for Claude, `.cursor-skills/lr-<skill>/`
  wrappers for Cursor, kept in sync by `scripts/sync-cursor-skills` and `/lr:check` #21).

  Standing operational facts worth carrying: **trust rollout/tool-call logs, not model self-report**,
  when validating an engine path; Codex's default sandbox blocks `.git` writes and network, so the
  supported finalization path needs `.git` writable through launch/config (a commit-blocked run is
  degraded fallback, not a merge failure); Codex per-agent shortcut register/unregister/list remains an
  unvalidated implementation gap. The **"framework is prose executed by the model"** risk is
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
- **v25 workspace layer (pull + init)** — implemented locally in `lore-framework` commit `0311ab6`.
  Hard renames: workspace-sync→workspace-pull, init→workspace-init. Two-level repo declarations
  (`lore-workspace.md` + domain `repos:`), optional workspace-as-git-repo envelope, cursor wrapper
  regeneration, checks #22–23. Full lifecycle remains the pre-push gate. See
  `v25-workspace-pull-init-design.md`, `workspace-meta-repo-pattern.md`.

## Current State

Workspace holds three canonical repos: **`lore-framework/`** (plugin), **`lore-framework-dev/`**
(this repo — lore-architect lore, tests, drafts), and **`lore-agents/`** (personal agents).

`lore-framework/` is **clean and pushed at v30** on `main`. The three newest *shipped* capability
surfaces are all live: **Lore Beings** (Being Keeper substrate + `/lr:being` command surface, BETA),
**Markdown session archives** under `agents/<agent>/archive/YYYY/MM/`, and **`/lr:trilens-loop`**
(iterated three-lens review). Three engines are Tier-1 supported — Claude Code, Codex, Cursor.

**v31 `lr-core` is built, reviewed, but PARKED, not shipped.** Deterministic substrate script +
boot/attach/consult/pull-lore/process-merge/lore-search doc rewiring + the Script Fallback Contract
(whose Accelerator category was redesigned as **literate** — the script's own comments are the
fallback spec, ~9 docs thinned to pointers), plus a reworked `docs/trilens-loop.md`. It lives on
branch `wip/lr-core-v31` in both repos (worktrees at
`<workspace>/.worktrees/{lore-framework,lore-framework-dev}/lr-core-v31/`), **committed there, working
trees clean, not merged to main and not pushed** — parked per explicit user instruction after a rough
2026-07-25 session. Three full-surface trilens rounds have now run over the branch (25 findings, 21
applied, 3 declined, 1 accepted, zero sustained BLOCKERs; round 3 hit the 3-round ceiling with 2 HIGHs
left ungated and disclosed as such), fixing real bugs along the way — a nested-repo `git -C` escape
both in the script (`git-dash-c-needs-toplevel-guard.md`) and, found separately this round, in
`version-check.md`'s parallel prose gate; signal-death/sentinel collisions; encoding/BOM bugs; a
version-comparison bug; boot-procedure and release-notes gaps — plus two mutation-verified regression
tests (`verify-regression-tests-via-mutation.md`), tests 38→51 green. **The lifecycle suite has now
run once (2026-07-27), with a partial result: Claude Code/haiku is green (6/7 modules; the 7th's
flakiness root-caused as a macOS `pwd`-vs-`realpath` ambiguity, `macos-var-symlink-realpath-ambiguity.md`,
and fixed) and is the only trustworthy data point — Codex and Cursor both silently resolved an
*installed* v30 plugin instead of the `--plugin-dir` worktree under test, invalidating both engines'
results (`lifecycle-harness-plugin-identity-unverified.md`).** Repointing those two engines' sources at
the worktree and re-running them is the actual remaining precondition to a valid three-engine green,
still deferred to the user. `main` in both repos is unaffected. Check `v31-lr-core-parked-2026-07-25.md`
before starting related work — its "Resuming" section is current; the in-worktree
`workdir/GOAL-2026-07-25.md` is stale on three points, don't follow it as-is. See also
`trilens-loop-v31-restructured.md`.

Both pre-ship gates are in working order and both are routinely run: the review loop via
`/lr:trilens-loop`, and the real-engine lifecycle suite via `tests/lifecycle/` (plus the separate
higher-blast-radius `LR_LIFECYCLE_KEEPER=1` Keeper track and the `LR_QUALITY=1` benchmark track).
See `trilens-loop-feature.md`, `lifecycle-testing-harness.md`, `lore-beings-design.md`,
`session-summaries-feature.md`.

## Running Backlog & Standing Improvement List

`framework-improvements-backlog.md` is the canonical list of deferred items; its § Ship Closures
archives per-ship gate dispositions. Quality benchmark tier/probe expansion is in the dev repo with
regular/deep matrix defaults and local override support. ~175 lore topics. The
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
`/lr:note`, lore MCP server). See `standing-improvement-list-practice.md` for the refresh
protocol, backlog relationship, and tiering convention.
