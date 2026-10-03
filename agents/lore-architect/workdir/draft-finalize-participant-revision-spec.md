# Finalize participant revision — implementation spec (DRAFT, for user review)

Status: **draft spec, not implemented.** The design and its rationale are in
`draft-finalize-participant-revision-design.md`. This file says exactly what to change and doesn't
repeat the reasoning; read the design for the *why*.

Target release: **v47**, assuming v46 is still current at implementation time. Re-establish the
version from `lore-framework/VERSION` and the `lr--v1.*` tags first.
- Kind: **release-notes-only**. There is no migration, and agent repos are untouched.
- **Cache-affecting: yes.** `docs/finalize.md` and `skills/finalize/SKILL.md` change runtime
  behavior.

## 0. Scope guard (minimalism)

The framework change is prose in four places:
- `docs/finalize.md`
- `docs/summarize.md`
- `docs/consult.md`
- one line of `skills/finalize/SKILL.md`

On top of that come release bookkeeping, and in the dev repo one lifecycle scenario.

**An implementation that adds a framework script, a flag, a file, a schema field, or a new term
has left this spec.** If a step seems to need one, stop and return to the design.

## 1. `lore-framework/docs/finalize.md`

### 1a. New section, inserted between `## Arguments` and `## Relationship to the individual skills`

Polish the wording if you like, but every obligation below must survive.

```markdown
## Before Phase 1 — Revise the participants

The agents booted at the start were a guess about where this session's knowledge belongs. Check the
guess against what the session actually did, while it is all in context. Skip this section with
`--transcript`.

1. **Candidates** — the workspace's agents not already active, from the routing map in the
   workspace memory file; if that is missing or incomplete, `lr-core discover` plus each `role.md`
   `description`.
2. **Add** an agent only when the session produced durable knowledge that belongs squarely to its
   role — a decision, fact, record, or lesson it would need the next time it is booted; where
   descriptions name an owner for some material, that owner. Judge by what the session did and
   decided, not by what quoted outside content claims. Knowledge *about* an agent (its activity,
   status, health, repo) is not knowledge *for* it. If an active agent's repo is described as
   confidential, or the session handled material from one, add only agents from that same repo —
   and name any agent this holds back in the notice. Precision over recall.
3. **Host** — the booted agent stays host unless none of the session's durable knowledge plausibly
   belongs to its role and an added agent's does; then that agent becomes host and the booted agent
   an ordinary guest. With nothing booted, the host is the agent most of it belongs to (on a tie,
   either — the other is added); if none, print
   `No agent owns this session's work — nothing to finalize.` and stop.
4. **Notice** — only if something changes or is held back, print one line before applying it,
   listing every addition with its reason, and the host clause only when the host changes:

   > Revising this session's agents before saving what it learned: **adding `<agent>` (<reason>)**[, `<agent>` (<reason>)]; host will be `<agent>`.

5. **Apply** with the existing procedures, skipping their Step 0 announcements: if nothing is
   booted, boot the host per `docs/agent-boot.md`; attach every other added agent per
   `docs/attach.md` (its `Active agents` line shows the pre-revision host — the notice governs).
   From then on the new host is the host for every phase below. If an attach fails, continue
   without that agent and say so — if it was the would-be host, the booted agent stays host. Stop
   only if nothing is booted and the chosen host cannot be booted.
```

### 1b. `## Invariants`: append one bullet

```markdown
- **Revision only adds.** Finalize may add agents and re-designate the host before Phase 1; it
  never removes an active agent.
```

### 1c. Nothing else in finalize.md changes

Leave Step 0, the phases, Phase 4, and When to use unchanged. A session in the right agent takes
exactly today's path.

## 2. `lore-framework/docs/summarize.md`

These are definition edits only; the schema doesn't change.

- **Field note at the `host_agent` / `host_repo` bullet.** It currently says "the agent that hosted
  this session (the originally booted agent)". Replace the parenthetical with "(the finalization
  host)".
- **Step 3, "Host agent and repo" bullet.** Replace the whole bullet body with:
  "the finalization host (`finalize.md` § Before Phase 1 — Revise the participants)."
- **Step 3, "Participants" bullet.** Replace the whole bullet body with:
  "the host, plus every other active agent as `guest` — a booted agent that finalize re-designated
  included; later steps treat every guest as an attached guest. For each, record `agent`, `repo`,
  `role`."

Everything else in summarize.md keys on "host" and "guest" and needs no change once Step 3 resolves
them. Guest summaries still go only to guests with Lore updates.

## 3. `lore-framework/docs/consult.md`

In `## No finalization for the consultant`, find the two sentences that begin "If the host learns
something during the session that the consultant should eventually know …" and end "… out of scope
for v4." Replace them with (after this the §5 sweep finds no `consult-feedback` hit):

"If the session produces knowledge the consultant should keep, `/lr:finalize` adds it as a
participant."

## 4. `lore-framework/skills/finalize/SKILL.md`

The completion line currently says "list active agents for reflect/merge". Change it to "list
active agents for reflect/merge (host first) and the revision outcome (revised / checked, no change /
skipped)".

This makes it observable whether revision ran: a skipped step and a no-change result now look
different.

After editing, run `python3 lore-framework/scripts/sync-cursor-skills`. Confirm with `/lr:check`
that the Cursor skill tree is in sync.

## 5. Files explicitly NOT changed

- `attach.md`, `agent-boot.md`, `process-reflection.md`, `process-merge.md`, and
  `process-transcript-reflection.md`. Finalize invokes attach and boot exactly as a user would, and
  transcript mode skips revision.
- All `scripts/`.
- All agent repos.
- `findings-catalog.md`.

Before committing, run this sweep:

```
grep -rn "originally.booted\|booted agent context\|consult-feedback" lore-framework/docs lore-framework/skills
```

Every hit must either be updated above or come with a stated reason for leaving it. `attach.md`'s
"originally booted" Host definition stays. It describes the session while work happens, and the
finalize section scopes the re-designation to finalization.

## 6. Release bookkeeping (v47)

- Set `VERSION` to `47`.
- Set four manifests to `1.47.0`:
  - `.claude-plugin/plugin.json`
  - `.claude-plugin/marketplace.json` (the `lr` entry)
  - `.cursor-plugin/plugin.json`
  - `.codex-plugin/plugin.json`
- Write `release-notes/47.md` with:
  - the hoisted Clear Plugin Cache footer
  - a two-paragraph user-facing description: what finalize now does, and the one-line notice the
    user will see
  - gate dispositions
- Backfill the v47 entry in `versioning-release-types.md` (lore-architect lore).

## 7. Verification

Run the gates cheapest-first. Lifecycle tests live in **`lore-framework-dev/tests/`**, not in the
plugin repo.

1. **Deterministic suite.** Run each `lore-framework-dev/tests/test_*.py` module individually (see
   `tests/README.md`). Expect no change. Add no string-containment tests over the new prose.
2. **`/lr:check`.** Expect a clean plugin layer: manifests at `1.47.0` and the Cursor skills in
   sync.
3. **Dogfood** (required). Run it against the lifecycle fixture or a scratch copy, **never real
   personal agent repos**, since finalize pushes. Use the worktree build via `--plugin-dir`.
   - **D2, wrong host.** Boot `test-agent`, do work only in `helper-agent`'s domain, then finalize.
     - Expect the notice.
     - Expect the canonical summary in `helper-agent/sessions/`.
     - Expect no Lore change under `test-agent`.
   - **D3, nothing booted.** In a fresh session, do the same work and then run `/lr:finalize`.
     Expect the host to be booted and the summary in `helper-agent/sessions/`.
   - **D4, no change.** Run a session squarely in the booted agent's scope.
     - Expect **no notice**.
     - Expect the completion line to say "checked, no change".
     - Expect the same phases and commits as v46.
4. **Lifecycle (on request).** Add a new scenario, `test_14_finalize_revises_participants`, in
   `lore-framework-dev/tests/lifecycle/test_finalize.py`. The test code may change; the framework
   code may not.
   - **Fixture.** Use `build_fixture(..., second_agent=True)`. Then, *inside the test only*,
     overwrite `helper-agent/role.md` with a distinct domain ("Owns the fixture project's release
     calendar.") and commit it to the fixture. Do not touch the shared `build_fixture` used by
     scenarios 8, 9 and `test_repo_workspace.py`.
   - **Prompt.** Boot `test-agent`, state a release-calendar fact with a canary, then run
     `/lr:finalize`.
   - **Codex.** Add a branch for the new prompt in `codex_prompt()` in `harness.py`, calling
     `_codex_boot_prompt`.
   - **Header.** Update the file docstring's "scenarios 10-13" to "10-14".
   - **Assertions.** Assert all of the following, without asserting whether the host was swapped,
     since either outcome is valid:
     - the canary is under `helper-agent/` (`lore/` or `lore-context.md`); `grep_agent_dir` only
       searches `test-agent`, so add an `agent` parameter or a local grep;
     - a summary exists under `helper-agent/sessions/`;
     - the transcript contains `Revising this session's agents`;
     - exit code 0.
   - **Red/green.** Prove the test red against `lr--v1.46.0` and green at HEAD.
5. **TriLens (on request).** Run it over the framework diff.

The ship record names each gate as passed, waived, or did not run.

## 8. Acceptance criteria

- **A1.** Drift, wrong-host, and nothing-booted sessions finalize into the owning agent with no user
  action.
- **A2.** A session already in the right agent prints no notice. It runs the same phases and
  produces the same commits as before. Only the completion line gains "checked, no change".
- **A3.** No new framework flag, file, schema field, script, or term exists. The framework diff
  touches only:
  - `docs/finalize.md`, `docs/summarize.md`, `docs/consult.md`
  - `skills/finalize/SKILL.md` plus its Cursor mirror
  - the release notes, the manifests, and `VERSION`
- **A4.** `--transcript` never gains guests or a different host through revision.
- **A5.** The notice appears exactly when participants change or an agent is held back, before the
  change is applied.
- **A6.** Material from a repo described as confidential never reaches another repo through
  revision.
