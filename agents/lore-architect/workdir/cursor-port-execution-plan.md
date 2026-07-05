# Cursor Port Execution Plan for Lore Framework

Assumption: the requested target engine is **Cursor**. If "Carcer" refers to a different engine, this plan's structure still applies, but the engine-specific bindings and validation steps need to be rewritten from the capability-discovery phase onward.

Status: planning artifact, not yet executed.

## Objective

Add **Tier-1 Lore framework support** for Cursor using the same `docs/engines/` architecture that shipped for Codex in v19, then validate it on the real engine before automating it in the lifecycle harness.

Tier-1 parity means:
- boot
- recall
- consult
- attach
- reflect
- merge
- summarize
- finalize
- check
- update
- init
- workspace-sync
- create-repo / create-agent

The goal is **not** to redesign Lore around Cursor. The goal is to map Cursor cleanly onto the existing five-binding engine adapter model while preserving one shared team knowledge substrate across Claude Code, Codex, and Cursor.

## Non-Goals

The first Cursor port should **not** attempt to solve these unless validation proves they are required for Tier-1:
- `spawn-teammate`
- `lr-wait` / MCP-specific follow-ons beyond basic registration verification
- DF / AIQA / `df-*`
- migration of all Claude-first surfaces outside the core lifecycle
- Cursor-only UX optimization before the baseline lifecycle is stable

## Why Planning First Is Correct

For Lore, the risky part is not file editing. It is getting the **engine behavior contract** correct:
- how skills load
- how the engine invokes them
- how subagents work
- how git/network approvals behave
- how worktrees interact with the framework's top-level-repo invariant
- whether Cursor's default model follows the prose procedures faithfully

Codex became tractable only after the probe and binding design made those contracts explicit. Cursor should follow the same sequence.

## Success Criteria

The Cursor port is "done" for v1 only if all of these are true:

1. `docs/engines/cursor.md` exists and fully specifies the five bindings plus capability gates.
2. Boot Step 0 selects the Cursor profile deterministically in a real Cursor session.
3. A real Cursor session can boot `lore-architect` and complete at least one full Tier-1 lifecycle path.
4. The worktree story is documented clearly enough that users cannot accidentally violate the workspace invariant during parallel-agent use.
5. Cursor is wired into `lore-framework-dev/tests/lifecycle/harness.py`, or there is an explicit documented blocker proving why automation must remain deferred.
6. The shipping docs distinguish verified behavior from hypothesis.

## Core Design Constraint

The existing `docs/engines/` convention is the architectural boundary. Cursor should be expressed through the same five bindings already used by Claude and Codex:
- `framework-root`
- `invocation-syntax`
- `subagent-spawn`
- `memory-file`
- `runtime-bounding`

If Cursor appears to need more than these, first challenge the assumption. That usually means we are mixing engine behavior with feature scope.

## Deliverables

Expected output of the full port:
- [cursor.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/engines/cursor.md)
- updates to [agent-boot.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/agent-boot.md) Step 0 engine selection
- any required updates to shared procedure docs only where the existing engine-note pattern is insufficient
- Cursor install / usage guidance in the framework docs or release notes
- lifecycle harness support in [harness.py](/Users/yaroslav/Documents/git-repos/lore-framework-dev/tests/lifecycle/harness.py)
- fresh lore artifacts recording verified Cursor behavior, blockers, and design decisions

## Execution Phases

### Phase 1: Live Capability Refresh

Purpose: replace the current quota-blocked Cursor draft assumptions with verified current facts.

Inputs:
- [draft-port-cursor.md](/Users/yaroslav/Documents/git-repos/lore-framework-dev/agents/lore-architect/workdir/draft-port-cursor.md)
- [cursor-agent-cli-probe-findings.md](/Users/yaroslav/Documents/git-repos/lore-framework-dev/agents/lore-architect/lore/cursor-agent-cli-probe-findings.md)
- Cursor official docs and the actual local `cursor-agent` binary

Tasks:
1. Verify `cursor-agent` is installed and current enough to target.
2. Re-run the capability probe:
   - `--plugin-dir`
   - headless invocation flags
   - skill loading behavior
   - AGENTS support
   - subagent support
   - approval / trust behavior
3. Verify whether the prior quota block still exists.
4. Identify a deterministic install path for local development:
   - per-invocation `--plugin-dir`
   - symlink under `~/.agents/skills/`
   - Cursor-native install from GitHub repo
5. Determine the strongest engine-detection signal for Step 0:
   - `cursor-agent` process identity
   - `.cursor/` install path
   - env vars
   - plugin root path shape

Deliverables:
- refreshed Cursor probe notes
- yes/no decision on whether implementation can proceed immediately
- exact candidate values for each of the five bindings

Exit gate:
- we can state Cursor facts as verified behavior, not "should work"

### Phase 2: Binding Design Lock

Purpose: translate Cursor facts into the existing engine-profile model before editing the framework.

Tasks:
1. Write the provisional binding table for Cursor:
   - `framework-root`
   - `invocation-syntax`
   - `subagent-spawn`
   - `memory-file`
   - `runtime-bounding`
2. Decide whether Cursor should be treated as:
   - pure `SKILL.md` engine
   - mixed `SKILL.md` + `.cursor/agents/` engine
   - mixed `SKILL.md` + `.cursor/rules` engine
3. Decide the v1 policy for implicit invocation:
   - conservative default: `disable-model-invocation: true` on lifecycle skills
   - explicitly decide whether `recall` and `consult` stay implicit or not
4. Decide whether Cursor declarative subagents are required for v1 or whether an inline fallback is sufficient for first parity.
5. Decide how worktree behavior will be bounded in the first release:
   - allow only single-agent lifecycle initially
   - allow parallel fan-out only after worktree verification

Files likely affected in implementation:
- [agent-boot.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/agent-boot.md)
- [cursor.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/engines/cursor.md)
- possibly [conventions.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/conventions.md)
- possibly selected `skills/*/SKILL.md` files if Cursor-specific frontmatter is needed

Deliverables:
- binding table
- explicit scope line for v1
- list of files to edit

Exit gate:
- no unresolved engine-design questions remain on the critical path to a minimal implementation

### Phase 3: Minimal Cursor Profile Implementation

Purpose: implement only what is necessary for the first real Tier-1 Cursor run.

Tasks:
1. Add [cursor.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/engines/cursor.md).
2. Update [agent-boot.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/agent-boot.md) Step 0 to recognize Cursor.
3. If needed, add or adjust lifecycle-skill frontmatter for Cursor-safe invocation behavior.
4. Update any user-facing install or execution notes needed to make a manual trial reproducible.
5. Keep changes inside the established engine-note pattern where possible; avoid forking shared docs unless Cursor genuinely needs a different procedure.

Design rule:
- do not optimize for Cursor-native elegance yet
- optimize for smallest correct diff that enables the first full run

Deliverables:
- working framework diff for manual Cursor validation

Exit gate:
- a local modified framework copy exists that should be executable by Cursor without hand improvisation

### Phase 4: Manual Lifecycle Validation on Real Cursor

Purpose: prove the port on the real engine before any harness automation work.

Validation order:
1. boot happy path
2. boot unknown agent
3. recall
4. reflect
5. merge
6. finalize
7. consult / attach
8. init / check / update / workspace-sync

Rules:
- validate against a fixture workspace first, not against real lore repos
- capture exact prompts used
- prefer zero-network or local-only fixtures where possible, matching the existing lifecycle harness model
- if the model claims a behavior, verify it structurally from files or git state

Critical checks:
- Boot Step 0 selects Cursor, not Claude fallback.
- `<framework-root>` resolves without `${CLAUDE_PLUGIN_ROOT}` assumptions.
- auto-pull degrades correctly under Cursor approvals / network limits.
- version-check behavior remains "defer is not boot failure."
- merge writes the right files and does not silently skip reflections.
- finalize behavior around git approvals is documented, not guessed.

Deliverables:
- pass/fail record per scenario
- list of real blockers, each tied to a file or engine behavior

Exit gate:
- one complete lifecycle path is proven end-to-end on real Cursor

### Phase 5: Cursor-Specific Orchestration Decisions

Purpose: decide whether Cursor-specific features should be used in v1 or deferred.

Decision areas:
1. Declarative `.cursor/agents/` for merge / recall / consult fan-out.
2. Worktree interplay with Cursor's parallel agents.
3. `paths:` scoping for generated agent shortcuts.
4. `.cursor/rules` use, if any.

Decision rule:
- adopt a Cursor-specific mechanism only if it is clearly better and does not expand the maintenance surface disproportionately
- otherwise keep the shared docs/engines model as the primary portability layer

Specific risk to resolve:
- Cursor auto-managed worktrees may conflict with the framework rule that top-level checkouts remain on default branches and non-default work happens under `.worktrees/<repo>/<slug>/`

Deliverables:
- explicit keep/defer decisions for each Cursor-native feature

Exit gate:
- v1 is either safely conservative or intentionally Cursor-optimized, but not ambiguous

### Phase 6: Lifecycle Harness Automation

Purpose: move Cursor validation from manual proof to repeatable regression coverage.

Target file:
- [harness.py](/Users/yaroslav/Documents/git-repos/lore-framework-dev/tests/lifecycle/harness.py)

Tasks:
1. Add a `cursor` branch to `run_engine()` or equivalent engine dispatch.
2. Encode the right install / invocation model:
   - likely `--plugin-dir` if still supported
   - stdin handling
   - trust / force flags
   - output capture
3. Add any Cursor-specific spawn verification needed if subagents are involved.
4. Run the existing Tier-1 scenario suite incrementally:
   - `test_boot.py`
   - `test_recall.py`
   - `test_finalize.py`
   - `test_consult_attach.py`
   - `test_repo_workspace.py`
5. Record any scenario classes that fail because of engine fidelity rather than framework logic.

Deliverables:
- repeatable Cursor harness path, or a precise blocker note proving why it must remain manual

Exit gate:
- Cursor regressions can be rechecked mechanically after future framework changes

### Phase 7: Shipping, Documentation, and Versioning

Purpose: land the Cursor work in canonical `lore-framework` with the same discipline used for Codex.

Tasks:
1. Decide whether the Cursor port is:
   - release-notes-only
   - migration + release-notes
2. Bump `VERSION` and plugin manifests if the ship is cache-affecting.
3. Add release notes with exact verified scope and any explicit deferrals.
4. Run pre-ship review and the relevant lifecycle scenarios.
5. Update lore topics with what was actually learned, not what was intended.

Deliverables:
- releasable framework change set
- release notes stating the verified Cursor support surface

Exit gate:
- the canonical repo, not a side build, contains the Cursor support

## Binding Hypotheses to Verify

These are planning hypotheses, not final facts.

| Binding | Current hypothesis | What must be verified |
|---|---|---|
| `framework-root` | self-location should work exactly as with Codex | whether Cursor ever sets a useful engine-specific root signal and what Step 0 should key on |
| `invocation-syntax` | user-facing slash or skill-picker invocation likely works; agent-initiated invocation may need direct doc-following or disabled model invocation | whether Cursor honors lifecycle skills as explicit-only when requested |
| `subagent-spawn` | Cursor declarative agents may be the cleanest fan-out mechanism | whether they support the Lore boot-as-target-agent pattern without awkward generation or hidden state |
| `memory-file` | `AGENTS.md` | whether any `.cursor/rules` companion is actually necessary |
| `runtime-bounding` | terminal/approval model, not Claude's Bash timeout | exact timeout and approval semantics in CLI and IDE |

## File-Level Work Map

Files likely to change in the framework repo:
- [agent-boot.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/agent-boot.md)
- [cursor.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/engines/cursor.md)
- [claude.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/engines/claude.md) only if the reference wording needs normalization
- [codex.md](/Users/yaroslav/Documents/git-repos/lore-framework/docs/engines/codex.md) only if shared conventions get clearer through the Cursor work
- selected `skills/*/SKILL.md` files if Cursor-specific frontmatter needs to be added
- release notes and `VERSION` if shipped

Files likely to change in the framework-dev repo:
- [harness.py](/Users/yaroslav/Documents/git-repos/lore-framework-dev/tests/lifecycle/harness.py)
- test fixtures only if Cursor needs extra deterministic assertions
- lore topics capturing verified Cursor behavior
- this plan's follow-up execution notes in `workdir/`

Files that should not be changed early:
- broad shared procedure docs, unless a real Cursor execution failure proves the prose is too Claude-shaped
- `migrations/*`, `df/*`, and other deferred surfaces before the Tier-1 path is working

## Main Risks and Mitigations

### 1. Model fidelity on long prose procedures

Risk:
- Cursor's default models may follow the documents less faithfully than Claude or Codex.

Mitigation:
- use the existing lifecycle scenarios as structural truth
- validate weakest practical model tier first where possible
- simplify prose only in response to real execution evidence

### 2. Worktree collision

Risk:
- Cursor parallel/background agents may create worktrees in ways that violate Lore's workspace invariant.

Mitigation:
- defer parallel subagent claims until verified
- document a single-agent-safe path first
- inspect where Cursor creates worktrees and whether top-level discovery remains stable

### 3. Invocation ambiguity

Risk:
- lifecycle skills may trigger implicitly when they should only run explicitly.

Mitigation:
- default to explicit-only lifecycle invocation in v1
- only relax once the engine's invocation behavior is well characterized

### 4. Approval and git behavior

Risk:
- Cursor may require approvals that break auto-pull/finalize assumptions, or may hide failures behind IDE affordances.

Mitigation:
- document degraded-mode behavior clearly
- validate under both permissive and denied-approval cases if possible

### 5. Overfitting to Cursor-native features too early

Risk:
- the port becomes a second framework implementation rather than another engine profile.

Mitigation:
- ship the minimal adapter first
- treat Cursor-native declarative agents as an optimization phase, not the foundation

## Recommended Execution Order

This is the actual sequence I would run:

1. Refresh the live Cursor probe.
2. Lock the five Cursor bindings.
3. Implement the smallest framework diff needed for a manual Tier-1 run.
4. Prove boot and one full lifecycle path on real Cursor.
5. Expand to the remaining Tier-1 scenarios.
6. Automate Cursor in the lifecycle harness.
7. Only then evaluate Cursor-native subagent optimizations.
8. Ship via the normal versioning/release discipline.

## Immediate Next Step

Phase 1: run the live Cursor capability refresh and convert the current draft from "should work, unconfirmed" into a verified engine profile candidate.
