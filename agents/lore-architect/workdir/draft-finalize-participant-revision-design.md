# Finalize participant revision — design (DRAFT, for user review)

**Status: draft design, not implemented.**
- Written 2026-10-03 by lore-architect, from a user request. Revised 2026-10-04 (user decisions):
  the host is now the **best-fit agent by role**, the booted agent keeps close calls, additions
  stay uncapped but carry an explicit cost note, and confidentiality stays a short guard. See §9
  rounds 4+.
- The request: finalization should look at what the session actually did, decide which agents
  should learn from it, and include them, even when the user booted the wrong agent or none.
- Companion spec: `draft-finalize-participant-revision-spec.md`.
- The user's governing constraint is **minimalism**: add as few concepts, as little data, code and
  instruction as possible, and leave room to extend.

## 1. Problem

Finalization learns only into the **active agents**: the booted host plus any `/lr:attach` guests.
The user picks that set, usually at the start of the session. Sessions drift and users pick wrong.

The four cases where this goes wrong:

1. **Drift.** The user boots `finance-keeper`, and the session becomes a long thread about a Laguna
   Seashore 1409 bill. The workspace says those records belong to `laguna-seashore-manager`, which
   never learns about it.
2. **Wrong agent.** The user boots `tax-advisor` and does framework work.
   - The only agent able to learn has no use for what was learned.
   - Its repo also receives the canonical summary of a session it took no part in.
3. **No agent.** The user does useful work without booting anything, then runs `/lr:finalize`.
   There is nothing to finalize into, and `docs/finalize.md` does not cover this case.
4. **Consult.** The session consulted agent Y, then learned something Y should know.
   - `docs/consult.md` § No finalization for the consultant says the user can boot Y in a future
     session to capture it.
   - In practice nobody does.

In all four cases, knowledge the framework exists to keep is lost or lands in the wrong place.
The only remedy is one the user had to foresee at boot time.

## 2. How it works today (relevant facts only)

- **Active agents = host + attached guests.** The set lives only in the conversation, through the
  attach confirmations (`docs/attach.md`).
- **`/lr:finalize` runs four phases** (`docs/finalize.md`):
  - **Reflect** runs inline, host-first, once per active agent, through that agent's role lens. An
    agent with nothing in scope completes with zero topics, which is a normal outcome.
  - **Merge** runs one subagent per active agent, each booted as itself.
  - **Summarize** writes one canonical summary into the host's repo. A guest whose Lore changed also
    gets a short guest summary.
  - **Commit and push** happens per touched repo, with no prompts.
- **Attach already does everything needed to bring an agent in.** It runs preflight (discover,
  auto-pull, version comparison), reconciles the version, and loads the role, the lore context and
  the compact map. Once an agent is attached, the rest of finalization handles it with no special
  cases.
- **The host role does three things:** it is the session's **executor**, it **wins conflicts** while
  the work is happening, and it is the **home of the canonical summary**. By finalization, only the
  summary home still matters.
- **`--transcript` reflection is host-only.** It refuses attached guests, and guests cannot be
  detached.
- **The workspace memory file carries an AI routing map.** It lists every agent with its canonical
  one-line description, and every engine loads it at session start. Ownership hints live in those
  descriptions, such as "Laguna Seashore 1409 records belong to laguna-seashore-manager".
- **Lore Beings run unattended in `reflect-only` mode** (`docs/beings.md`), not through
  `/lr:finalize`.

## 3. Key insight

**Finalization is already correct for any set of active agents. Only the set is wrong.** So there
is no new pipeline, data model, or script. The design is one judgement, made at the one moment the
whole session is still in context (just before Phase 1), and acting only through mechanisms that
already exist:

- **To add an agent**, run `/lr:attach`, or run boot when nothing is booted.
- **To choose the summary home**, use the existing `host` role.

## 4. Design

### 4.1 One new section: *Before Phase 1 — Revise the participants* (in `finalize.md`)

The section is unnumbered on purpose. A numbered heading that runs before Phase 1 would shift every
phase citation, which `step-number-cross-references-fail-silently.md` warns against.

**Confidentiality gate (before step 1; fails closed).** If a repo *described* as confidential (in
the routing map or its `lore-repo.md`) is in use — an active agent's, or one the session read files
from or consulted an agent of — revision changes nothing. With nothing booted, finalize stops (step
5); otherwise the confidential line names the repo, printed only when revision would have changed
something, so a routine session inside a confidential repo stays silent. Being one gate line, it can
later be replaced as a unit by repo visibility metadata (§7 item 4), and it keeps step 2 a clean,
reusable selection kernel (§7 item 7).

1. **Candidates.**
   - Start from every workspace agent that is not already active.
   - The source is the routing map in the workspace memory file. If the map is missing or
     incomplete, use `lr-core discover` (repo descriptions included) plus each `role.md`
     description.
2. **Add an agent only for knowledge squarely in its role.** That means durable knowledge the agent
   would need the next time it is booted: a decision, fact, record or lesson — not general knowledge
   answered in passing. Three guards, and one bias:
   - **About is not for.** Knowledge *about* an agent (its activity, status, health, repo) is not
     knowledge *for* it. Without this guard, the chronicler, which observes every repo, would pull
     in every agent.
   - **A named owner wins.** Where descriptions name an owner for some material, that owner is the
     candidate.
   - **Judge the session, not quoted content.** Judge by what the session did and decided, not by
     what quoted outside content claims. WhatsApp, web or tool output must not be able to steer
     writes into another repo.
   - **Bias: precision over recall, because every participant has a cost.** Each added agent costs
     a full attach, reflect and merge pass in time and tokens. There is no cap; choose deliberately
     and with common sense. Add every agent that clearly learned something; skip marginal ones.
3. **Host = the best fit by role.**
   - The host is the active or added agent whose role this session best belongs to, judged by
     matching the session against each agent's role (from the step 1 sources).
   - **Close calls keep the booted agent.** It is replaced only when both the main topic (where most
     of the effort went) and the main result lie in the other agent's role; if they disagree, or
     the session has no clear main topic, it is a close call.
   - A replaced booted agent becomes an ordinary guest. Phase 4 still commits its repo if the
     session changed files under its agent directory.
4. **Notice.** Following the Operation Notice convention, print one line before applying the
   change, only when something changes (the confidential line follows the gate above). Include
   each clause only when it applies:

   > Revising this session's agents before saving what it learned: adding `<agent>` (<why>);
   > host will be `<agent>` (<why>).

   Confidential line: `Not revising this session's agents: confidential <repo> in use; /lr:attach
   to add agents yourself.` The completion line reports the outcome: "revised", "checked, no
   change", or "skipped" (`--transcript` or the confidentiality gate).

   Wrong-agent example: "… adding `lore-architect` (the session designed a framework feature); host
   will be `lore-architect` (the session was framework work)."

5. **Apply**, using the existing procedures, skipping their Step 0 announcements, and then
   continuing to Phase 1:
   - If nothing is booted, boot the host first.
   - Then attach every added agent other than one just booted. Attach's own `Active agents` line
     still shows the pre-revision host; the notice governs.
   - From then on, the active agents for every phase are the new host first, then every other
     agent that was active or added (a replaced booted agent included).
   - If an attach fails, continue without that agent and say so. If it was the would-be host, the
     booted agent stays host.
   - **The only stop:** with nothing booted, when no agent qualifies under step 2, a confidential
     repo is in use, or the host's boot fails, print
     `No agent owns this session's work — nothing to finalize.` and stop with nothing written and no
     completion line. A booted agent is never dropped, and revision never stops a finalize that has
     one.

Under `--transcript`, skip this section.

### 4.2 What does *not* change

- Reflect, merge, the commit phase, attach and boot are all unchanged.
- No new flags, files, schema fields, state, or script code.
- No prompt. Finalize stays end-to-end automatic. Beings are unaffected because they run
  `reflect-only`.
- The standalone `/lr:reflect`, `/lr:merge` and `/lr:summarize` stay manual. The user shapes the set
  with `/lr:attach`.
- Summarize: three definition sentences now say what "host" and "guest" mean at finalization. The
  schema is unchanged.
- The SKILL.md completion line also reports the revision outcome: revised, checked with no change,
  or skipped. A skipped revision step is then distinguishable from a no-change result. This is the
  observable postcondition from `the-terminal-step-is-the-step-that-gets-dropped.md`.

### 4.3 Concept budget

| Added | Count |
|---|---|
| New terms or concepts | **0** |
| New rules | One selection test (three guards plus the cost bias), one host rule with its close-call test, one confidentiality skip, one stop line (new behavior: today a nothing-booted finalize is undefined), the notice and its precedence over attach's `Active agents` line, the `--transcript` skip, and the three-state outcome on the SKILL completion line. Finalize can now boot an agent and push to repos the user did not name. "Close call", "main topic" and "main result" are plain words inside the host rule, not new terms. |
| Redefinitions | **1**: at finalization, "host" means the *finalization host* — the agent the session best belongs to, which is the booted agent unless revision found a clearly better fit. This is honest accounting: it is a real change to a definition, confined to finalize and summarize. |
| New data, schema or state | **0** |
| New framework code | **0** |
| New flags | **0** |
| New prose | One finalize section (~45 lines), one invariant bullet, three short summarize edits, one consult sentence, and one SKILL line. |

## 5. Edge cases and resolutions

| # | Case | Resolution |
|---|---|---|
| E1 | Drift into another agent's domain | The agent is added. It becomes host only if its role holds both the main topic and the main result (§4.1 step 3); otherwise it is an ordinary guest. |
| E2 | Wrong agent booted | The host is re-designated and the booted agent becomes a guest. With zero topics it gets no summary, and its repo is committed only if the session changed files under its agent directory; if it did learn something it gets an ordinary guest summary naming the new host. |
| E2a | An already-attached guest is the best fit | It becomes host with no attach; the notice carries only the host clause. Attaching an agent as a guest is not a host preference. |
| E2b | finance-keeper booted; the session is mostly a Laguna Seashore 1409 bill, partly general finance | Main topic and main result are both the unit's bill, so `laguna-seashore-manager` is added and becomes host; finance-keeper reflects as a guest. A roughly even split is a close call and keeps finance-keeper. |
| E3 | Nothing booted | The host is chosen and booted, and boot selects the engine profile. |
| E4 | Nothing booted and nothing fits | The one stop (§4.1 step 5): one line, nothing written. (Before this change there was no defined behavior.) |
| E5 | A booted agent with no durable knowledge anywhere | No additions; the host changes only per E2a. Otherwise it is today's path, including the summary. |
| E6 | Both the booted agent and an added agent learned something | Both participate, and the clearly better fit is host; a close call keeps the booted agent. Shared topics are allowed. |
| E7 | `--transcript` | Revision is skipped. Transcript mode is host-only by design, and its context-poor premise is the wrong place to make this judgement. Drift under `--transcript` keeps today's behavior. |
| E8 | Chronicler or observer sessions | Excluded by the "about is not for" guard. |
| E9 | Agent consulted earlier in the session | It is an ordinary candidate, judged on new knowledge; consulting by itself creates none. This closes the gap in `consult.md`. |
| E10 | Confidential repo in use | Revision changes nothing, and the confidential line names the repo only when revision would have changed something; with nothing booted, finalize stops. Adding agents inside a confidential repo is left to a manual `/lr:attach`. A public host that already has confidential material or guests is a pre-existing risk, out of scope. |
| E11 | Added repo is dirty, behind, or at a different version | Attach handles it: degraded mode, a warning, and possibly a framework version upgrade of that repo, which version-check commits and pushes itself, exactly as a manual attach or boot would. Phase 4 commits a repo only if phases 1–3 produced something there (its existing "no empty commits" invariant). Its `git add agents/` staging breadth is an existing, separately tracked backlog item that revision makes slightly more reachable. |
| E12 | Over-selection (an added agent learns nothing) | Not free, which is why step 2 states the cost. It costs one attach (~10–30k context tokens, plus a possible version upgrade of that repo), one reflect pass and one merge subagent. With zero topics, its Lore is not changed and it gets no summary or Lore commit. The precision bias keeps this rare. A marginal topic can still land, but the merge subagent booted as that agent is the second filter. |
| E13 | Finalize re-run or interrupted | Re-run simply re-evaluates. Agents actually attached (their `Attached:` confirmation) are already active. Anything only named in a notice is re-judged and re-applied. The same session usually gives the same judgement; a differing re-run prints a fresh notice. The notice is never treated as proof of attachment. |
| E14 | Compaction lost the attach records | Revision works from what the conversation still shows. Re-attaching is idempotent. Compaction-unsafe attach state is an existing, recorded limit (`attach-pattern.md`). |
| E15 | User wants to force or forbid an agent | To force one, `/lr:attach` it before finalize, which works today. Forbidding one is not in v1: the notice and the per-repo commit make a wrong add visible and revertible. See extension point §7. |
| E16 | *(Removed in Round 5; E19 covers an uncloned agent.)* | |
| E17 | Concurrent finalization of the same agent (teammates, another engine session) | This is already possible with attach today. Push conflicts route to `resolve-conflicts.md`. It is an accepted residual risk. |
| E18 | A host candidate tie | With an agent booted, it stays host (close-call rule). With nothing booted, pick either; the other is added as a guest, so both learn, and only the summary home differs. |
| E19 | A routing-map agent whose repo isn't cloned | Attach fails; continue without it and say so. |

## 6. Alternatives considered and rejected

- **A "late participant" role or schema field.** Nothing downstream would consume it, and the notice
  plus the participants list already show what happened.
- **Asking the user to confirm additions.** It breaks finalize's no-prompt invariant. A wrong add is
  visible and revertible, and the precision bias bounds its cost. Kept as an extension point.
- **A script that ranks agents.** Selection is semantic judgement over the session, which only the
  model with that context can make.
- **A subagent per candidate.** It would lack the session context, which is the same reason reflect
  runs inline.
- **Putting revision in `process-reflection.md`.** That would couple a standalone phase to attach
  and boot side effects. Participants are an orchestration concern.
- **Never swapping the host.** That covers drift but not the wrong-agent case, where the canonical
  narrative lands in an unrelated repo. Host choice is needed anyway when nothing is booted.
  (Round-1 minimalism review raised dropping the swap as the cheaper option. It was kept because
  the wrong-agent case is half of the motivating problem, and the cost is one redefinition.)
- **Swapping only when the booted agent has no plausible claim** (the rounds 1–3 rule). Superseded
  by user decision 2026-10-04: the summary home should follow where the session best belongs by
  role. The close-call rule keeps the stability the old rule bought.
- **A hard cap on additions.** User decision 2026-10-04: no cap; an explicit cost note asks for
  deliberate, common-sense selection instead.
- **A machine-checkable repo visibility field with a remote-visibility probe.** It is new data and
  new code. The fail-closed confidentiality gate over existing descriptions covers the known risk.
  Kept as an extension point.
- **A lighter attach** (description only). It would be a second attach mode, and reflection needs
  `lore-context.md` to avoid duplicates.
- **Printing the notice even when nothing changes.** That violates the Operation Notice convention,
  under which a no-op stays silent. The completion line covers observability instead.

## 7. Extension points (deliberately not built)

1. **User steering:** `--no-revise`, `--only <agents>`, `--exclude <agent>`, `--host <agent>`. These
   would go in the Arguments section.
2. **Confirmation mode:** confirm additions interactively, while unattended runs stay automatic.
3. **Hard cap on additions,** only if dogfooding shows the cost note is not enough (the user chose
   uncapped, 2026-10-04).
4. **Repo visibility metadata** (in `lore-repo.md`), replacing the description-based confidentiality
   rule.
5. **Agent `description` in `lr-core discover` output** (repo descriptions are already there),
   making the fallback a single call.
6. **Revision in standalone `/lr:reflect`,** or in transcript mode once it supports guests.
7. **Mid-session suggestions** ("this looks like laguna-seashore-manager's business — attach?").
   This would be a separate feature, sharing §4.1 step 2 as its kernel.

## 8. Risks and how they're bounded

- **Judgement quality (a wrong add or a missed add).** Bounded by:
  - the precision bias and the guards;
  - the merge subagent as a second filter;
  - the visible notice;
  - per-repo commits that can be reverted.

  Measured by dogfooding.
- **The executor drops the section.** It sits right after Arguments and before Phase 1, and the
  completion line must report its outcome.
- **Confidential material that is not *described* as confidential.** The rule is only as good as the
  descriptions. This residual risk is the same one a manual `/lr:attach` carries today. Extension
  point 4 closes it.
- **Pushes to repos the user didn't name.** The notice is printed before any attach, and each
  repo's commit line is printed in Phase 4.

## 9. Review log

**Round 1 (three cold reviewers):** minimalism and extensibility, grounding and executor fidelity,
failure modes and safety. Verdicts: SHIP-WITH-FIXES, SHIP-WITH-FIXES, BLOCK.

*Applied:*
- The vacuous "nothing fits → stop" rule would have dropped a booted agent's normal finalize.
  Revision now never stops when an agent is booted. All three lenses raised this.
- The lifecycle test plan didn't run as written: `grep_agent_dir` covers only `test-agent`, the
  Codex prompt map was missing, the shared fixture was touched, and the paths pointed at the wrong
  repo.
- Summarize host and participants role assignment after re-designation is now explicit.
- The notice prints before applying the change, per "as it happens", and the apply order is
  explicit.
- Failure paths for attach and boot are defined.
- `--transcript` now skips the section entirely, instead of a carve-out that continued into the
  wrong repo.
- The completion line now makes the revision outcome observable.
- The confidentiality rule is concrete and fails closed.
- Selection ignores quoted external content.
- Re-run consistency comes from the notice-as-record rule. *(Superseded in Round 2.)*
- E12's cost statement is now honest.
- The claim about Beings is now accurate.
- The "0 concepts" claim was corrected to one redefinition.
- The `attach.md` edit was dropped as cosmetic.
- The invariant bullet was trimmed.
- Dogfood was trimmed to D2, D3 and D4. *(D5 and D6 added back as optional in spec round 1.)*

*Accepted, not acted on here (now extension points):*
- A machine-checkable visibility field. The BLOCKER was resolved by the fail-closed rule instead.
- A hard cap on additions. *(Declined by the user 2026-10-04: uncapped, with a cost note.)*
- Undo hints in the notice.

*Declined:*
- Cutting the edge-case table. The user asked for the edge cases to be explored.
- Routing-map-only candidates. Without the fallback, workspaces with no routing map would get no
  candidates.
- Swap-free minimal variant (see §6).
- A Step 0 announcement change. The notice already covers it.
- A later `/lr:attach` after a finalize re-designation. The case is too rare to justify prose.

**Round 2 (three fresh cold reviewers):** minimalism, a literal-executor walkthrough of seven
concrete sessions, and a claim audit of the fix round. Verdicts: SHIP-WITH-FIXES ×3, all
fixes small.

*Applied:*
- Dropped the rule "an earlier notice counts as having added its agents". The notice prints before
  apply, so treating it as proof of attachment lost agents on an interrupted run and could wrongly
  stop a nothing-booted re-run. The executor and minimalism reviewers converged on this; the claim
  audit had flagged the host half missing from the spec. A re-run now re-evaluates, and attach
  confirmations are the record.
- Confidentiality wording is now determinate: an active confidential agent counts, and agents that
  are held back are named in the notice. *(Superseded in Round 6: confidentiality is a single
  skip.)*
- "Owns none" became "nothing plausibly belongs to its role", so any plausible claim keeps the host.
  *(Superseded in Round 4 by the best-fit host rule.)*
  The drift example no longer swaps the host. *(Superseded in Round 4: E2b swaps it.)*
- Attach's stale `Active agents` line is now explicitly overridden by the notice, and the new host
  goes first in host-first order.
- The completion line reports three states.
- The notice template is plural, and its host clause is conditional.
- Cut the `--transcript` nothing-booted stop, because the transcript preconditions already stop.
- Cut the redundant "mentioned or consulted" guard, and with it the consult-sentence tail.
- Shortened the summarize edits.
- Fixed the spec claims: `codex_prompt()` rather than a "mapping", the consult edit spans two
  sentences, the test header becomes 10-14, and "health" is aligned.

*Declined:*
- Removing a demoted agent from the host summary's participants (see E2).
- A cloneability check before the notice (see E19).
- Trimming the D3 dogfood. It is cheap and is the only check of the boot path.
- Dropping the invariant bullet. It is the single place that states "never removes".

**Round 3 (final; three fresh cold reviewers):** minimalism, end-to-end data flow across phases
and repos, and a post-fix consistency audit. Verdicts: SHIP, SHIP-WITH-FIXES, SHIP-WITH-FIXES.

*Applied:*
- **Stop rule.** A failed attach of the would-be new host no longer stops finalize. The booted agent
  stays host, and finalize stops only when nothing is booted and the chosen host can't be booted.
  This restores the "never stops because of revision" property. The end-to-end and consistency
  reviewers found it independently.
- **Demoted guest is a full guest.** Summarize Step 3 now says later steps treat every guest,
  including a demoted booted agent, as an attached guest. This means Step 11's guest-summary trigger
  covers it.
- **Tie rule.** The E18 tie rule is now in the spec text.
- **Completion line.** It now lists the host first.
- **E11 corrected.** Phase 4 commits only repos with phase output, and the `git add agents/` breadth
  is a pre-existing item.
- **Trims.** Removed "which is host-only", "usually nothing changes", and the "comes first" clause
  (implied by "host for every phase"). *(The order is stated again in Round 6, as part of the
  active-set sentence.)*
- **Housekeeping.** Marked a superseded round-1 log bullet, and fixed the guard count and line
  wrapping.

*Declined:*
- A Phase 4 rule to commit only separable output when a non-host merge fails. That is a pre-existing
  rule, and changing it is outside this feature.
- A note that a consulted-then-added agent appears in both `consulted` and `participants`. This is
  cosmetic and true.
- Pinning the order of guests after the host. The outcomes are per agent, so the order is harmless.

**Loop outcome:** three rounds, which is the ceiling. Round 3 had no BLOCKER or HIGH findings.
Its two MEDIUMs were one convergent defect, which is fixed above. The other round-3 findings were
LOW and were applied or declined as listed. **The round-3 fixes themselves were not re-reviewed by
a fourth round**, because the ceiling prevents it. They are small, local wording changes, listed
above for the implementer to re-check. *(Superseded: the 2026-10-04 user revision reopened
review; Rounds 4–6.)*

**Round 4 (2026-10-04 revision; user decisions, then three fresh cold reviewers):** the user changed
the host rule to best fit by role (booted agent keeps close calls), kept additions uncapped with an
explicit cost note, and asked that confidentiality stay a short guard. Lenses: minimalism and
extensibility, a literal-executor walkthrough of seven sessions, and a consistency and grounding
audit against the framework files. Verdicts: SHIP-WITH-FIXES ×3.

*Applied:*
- **"Clearly better fit" is now executable:** the booted agent is replaced only when the session's
  main topic and results lie in the other role; no clear main topic is a close call. E2b anchors it.
- **Confidentiality:** the host stays in its repo when the guard applies, so a demoted public agent
  never gets a summary pointing into a confidential repo. The trigger is now "read files from" such
  a repo, and E10 shrank to one sentence. The fallback reads `lore-repo.md` descriptions, where
  confidentiality is stated. *(Superseded in Round 6.)*
- **Apply continues to Phase 1** after boot or attach reports, so the run doesn't stop there.
- **Attach wording:** "every added agent other than one just booted", so a new host that is an
  addition is attached.
- **One notice template** with optional add, host (with reason) and hold-back clauses. *(Superseded
  in Round 6: confidentiality is a single skip.)*
- **Cost note merged into the bias bullet** (the guard count is right again).
- E2 covers a demoted agent that learned something; E2a says an explicit guest attach is not a host
  preference; E5 no longer contradicts E2a.
- `--host <agent>` added to extension point 1; the superseded round-1/2 log entries are marked.
- Spec findings (old host rule in the spec, the standalone `/lr:summarize` host definition) go to
  the spec revision.

*Declined:*
- Re-using an earlier notice's judgement on a re-run. Round 2 removed notice-as-record for good
  reason; the main-topic test makes flips rare, and a second notice is visible.
- Folding E6 and E18 into E1, and the remaining confidentiality sharpening. Marginal; the table
  stays the user-requested edge-case record.

**Round 5 (three fresh cold reviewers):** minimalism, a claim audit of the round-4 fixes against
the framework files, and a literal-executor walkthrough of six new sessions. Verdicts:
SHIP-WITH-FIXES ×3, no BLOCKER or HIGH.

*Applied:*
- **One stop rule**, stated once in step 5 with its literal line; step 3 no longer contradicts
  "never stops". E4 points to it. (Minimalism and executor converged.)
- **Confidentiality as one constraint:** revision stays inside the confidential repo — additions and
  host come only from it, and nothing is added when the host is elsewhere. This closes the leak
  where a public host's summary would carry a confidential guest's learning section, and defines the
  nothing-booted case. (Minimalism and claim audit converged.) *(Superseded in Round 6.)*
- **Cost note no longer under-selects:** "the usual answer is no change" became "add every agent
  that clearly learned something; skip marginal ones".
- **Close call made determinate:** both main topic (most effort) and main result must lie in the
  other role; a disagreement is a close call.
- **Hold-back clause** names the repo in use and the `/lr:attach` override. *(Superseded in Round 6:
  confidentiality is a single skip.)*
- **Honest accounting:** a "New rules" row (close call, held back, revision outcome) and ~50 lines.
  *(Superseded in Round 6.)*
- Cuts: restated no-summary/no-commit rule, "not a count of topics", the profile-selection rationale
  in step 5, the transcript precondition explanation, E16 (contradicted step 1; E19 covers it).
- Fallback cites `lr-core discover`'s existing repo descriptions; extension point 5 narrowed to
  agent descriptions. E13 says "usually"; the round-2 drift-example log line is marked superseded.

*Declined:*
- A separate "booting `<agent>`" notice verb for the nothing-booted case. The host clause already
  says who will host; one template is enough.

**Round 6 (three fresh cold reviewers):** minimalism, end-to-end data flow through the real phase
docs for three host-swap cases, and a post-fix consistency audit. Verdicts: SHIP-WITH-FIXES ×3, no
BLOCKER or HIGH.

*Applied:*
- **Confidentiality reduced to one skip** (all three lenses flagged the round-5 wording: it still
  allowed a cross-repo host swap, and broke with two confidential repos). If a confidential repo is
  in use, revision changes nothing and the notice names it; with nothing booted, finalize stops.
  Drift inside a confidential repo is left to a manual `/lr:attach`. This supersedes the Round 4
  and Round 5 confidentiality wording, and the Round 5 claim that revision closes the
  public-host-with-confidential-guest leak: that is pre-existing and out of scope (E10).
- **Demoted executor's files are committed:** Phase 4 still commits a replaced booted agent's repo
  when the session changed files under its agent directory (E2 corrected).
- **Active set stated once in Apply:** the new host first, then every other agent active or added,
  the replaced booted agent included — downstream docs define active agents as host + attached
  guests, and the demoted agent was never attached.
- **Honest accounting:** the §4.3 "New rules" row now lists every rule and behavior the section
  adds.
- Cut step 3's nothing-booted bullet (the general rule covers it). E1 and E2b use the
  both-main-topic- and-main-result test; §6 no longer calls a wrong add cheap; dangling and
  superseded log references fixed; E16 marked removed.
- Spec findings (old rules still in the spec, the completion line naming the final host) go to the
  spec revision.

*Declined:*
- Moving E2a/E13/E18 rules into §4.1. Each follows from §4.1 as written; the table explains, it does
  not add.
- A privacy note for a host move into a more widely visible repo. Summarize's per-destination
  privacy check already applies to whichever repo receives the summary.
- Reordering step 2 for the mid-session-suggestion extension. The general tests already come first.

**Revision loop outcome:** three rounds (4–6), the ceiling. Round 6 had no BLOCKER or HIGH; its
fixes are local and were not re-reviewed by a further design round. The spec rounds re-read §4.1
as the authority and serve as their check.

**Spec round 1 (three fresh cold reviewers over the spec):** minimalism, spec-to-design fidelity,
and implementability against the real framework and test files. Verdicts: SHIP-WITH-FIXES ×3, no
BLOCKER or HIGH.

*Applied (spec, mirrored here where the design changed):*
- **Confidentiality became a single gate line before step 1**, in both spec and design — one place
  to swap for visibility metadata later, and step 2 stays a reusable kernel.
- Close-call wording completed ("if they disagree or there is no clear main topic"); the Operation
  Notice citation restored; the section intro shortened; step 3's duplicated role sources
  cut.
- Paths use `<framework-root>/docs/...` like the rest of `finalize.md`; the completion-line values
  are quoted.
- A1 and A5 match the current design; A7 added for the host rule.
- Verification: D5 (close call, doubles as drift) and D6 (confidentiality) added as optional
  dogfoods; the lifecycle scenario builds its own `second_agent` fixture, uses harness constants,
  and adds a non-colliding README row; release-notes footer wording noted (reworded in spec round
  2); `attach.md`'s missing Step 0 exemption named as a deliberate non-change.

*Declined:*
- Cutting "Phase 4 still commits its repo…". Checked against `finalize.md`: its "No empty commits"
  invariant skips a repo with no phase 1–3 output, so a demoted executor's workdir files would be
  left uncommitted without it.
- Cutting "there is no cap" and "common sense" from the cost note: they are the user's explicit
  wording for this decision.
- Dropping the three-state completion line: it is the observable postcondition that separates a
  skipped revision from a no-change one.
- Shortening the invariant: it is the one place that states "never removes".

**Spec round 2 (three fresh cold reviewers):** minimalism, a literal executor of the shipped
`finalize.md` text alone across six sessions, and a claim audit of spec round 1. Verdicts:
SHIP-WITH-FIXES ×3, no BLOCKER or HIGH. All six executor walks ended correctly.

*Applied:*
- **Confidentiality gate made determinate:** "described" means the routing map or `lore-repo.md`; a
  consult of its agent counts as use; with nothing booted it stops (no double print); otherwise the
  line prints only when revision would have changed something, so a routine session inside a
  confidential repo stays silent (A2 holds). Step 4's "only if something changes" no longer
  contradicts it. (All three lenses touched this.)
- "Then continue to Phase 1" moved to the end of Apply, so boot and attach come first.
- The three outcome words are stated in the `finalize.md` text, with "skipped" covering
  `--transcript` and the gate.
- A6 scoped to revision. Spec lead-in is now "Insert verbatim". Intro filler cut.
- Design: step 3 no longer names role sources separately (mirrors the spec); §6 cites the gate, not
  the old same-repo rule; a stale log claim reworded. Release-notes bullet matches 46.md's
  structure.

*Declined:*
- Cutting the "if they disagree or there is no clear main topic" clause (minimalism) — the spec
  round 1 fidelity reviewer asked for it, and it settles the executor's hardest case.
- Cutting "a replaced booted agent included" — downstream docs define active agents as host plus
  attached guests, so the explicit inclusion is load-bearing.
- Booting the next-best added agent when the chosen host fails to boot — rare, and the stop is safe.

**Spec round 3 (final; three fresh cold reviewers):** minimalism, a literal executor of the patched
docs across six new sessions (all ran end to end), and a whole-document consistency audit.
Verdicts: SHIP, SHIP-WITH-FIXES ×2, no BLOCKER or HIGH.

*Applied:*
- **When the confidential line prints**, made consistent everywhere: only when revision would have
  changed something and an agent is booted (design step 4, E10, spec A2, A5; D6 now does
  helper-domain work first so there is something to block).
- The design's step 4 states the three outcome words, as the spec does.
- `consult.md`'s new sentence says finalize *may* add the consultant (not while a confidential repo
  is in use).
- The stop prints no completion line; "a fact" excludes general knowledge answered in passing.
- Spec §4 no longer runs `/lr:check` twice (§7 gate 2 covers it).
- Remaining §9 reversals marked superseded; the line estimate is ~45.

*Declined:*
- "It stays active through Phase 4" in place of the Phase 4 commit sentence — re-checked against
  `finalize.md`'s "No empty commits" invariant: a demoted agent with no phase 1–3 output would be
  skipped, so the sentence stays.
- Allowing additions inside the same confidential repo — the round-6 simplification leaves that to a
  manual `/lr:attach`.
- Deduplicating the confidential case between the gate and the stop list — the stop list is meant to
  be complete.
- `--transcript` with nothing booted — pre-existing, out of scope.

**Spec loop outcome:** three rounds, the ceiling. Round 3 had one SHIP and no BLOCKER or HIGH; its
fixes are local wording and were not re-reviewed by a fourth round. The implementer should re-read
§1a once against the patched `finalize.md` before committing.

