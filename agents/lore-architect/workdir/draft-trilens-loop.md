# Draft — `/lr:trilens-loop`

Design record for the three-lens iterated review skill. Settled in a design dialogue with the
user on 2026-07-25 (plain-language / dialogue / follow-me modes active). Implementation lands in
`lore-architect/trilens-loop` (plugin) + `lore-architect/trilens-loop-dev` (tests).

## 1. What it is

**Review the changes from three independent perspectives, fix what matters, repeat until clean.**

1. Point it at a set of changes (default: everything this session changed).
2. The host session picks the **three lenses** that matter most for *these* changes.
3. It spawns **three subagents**, one per lens. They did not author the changes, so they carry
   none of the session's bias.
4. Each reviews and reports findings.
5. The host **triages** each finding — accept or decline, with a reason. Declining is legitimate.
6. The host fixes what it accepted.
7. New round: fresh reviewers, told what was applied and what was declined and why.
8. Stop when a round finds nothing worth fixing. A round cap bounds the loop.

Output: the improved changes plus a ledger of every finding and its verdict.

## 2. Provenance — this is a promotion, not a new invention

The flow is `parallel-reviewer-fanout-pattern.md`, the architect's own review discipline, hardened
across the v11–v28 ships. The user independently articulated the same flow in the 2026-06-01 lr-dev
design dialogue (`draft-lr-dev.md` §5), where it was captured as a backlog item
(`framework-improvements-backlog.md`: *"Reusable multi-lens review skill"*).

Two changes from the backlog capture:

- **Core, not the DF module.** The backlog filed it as `lr:dev-review` under lr-dev. Wrong layer —
  the pattern is domain-agnostic (used on doc sweeps and lore edits, not just code). Ships as a
  core plugin skill; DF/AIQA becomes a consumer.
- **The loop is first-class.** The backlog treated iteration as "address-then-decide-if-another-round."
  Here the loop, its termination rule, and the dispositions ledger are the specified core.

## 3. Naming

`trilens-loop` — `tri` (three perspectives) + `lens` (the framework's existing word for a review
perspective, from `parallel-reviewer-fanout-pattern.md`) + `loop` (the iteration is the feature).

- Claude Code: `/lr:trilens-loop` · Cursor: `/lr-trilens-loop` · Codex: `/lr:trilens-loop`
- Canonical folder `skills/trilens-loop/`, doc `docs/trilens-loop.md`.
- Distinctive enough to avoid confusion with Claude Code's built-in `/review`, `/code-review`,
  `/security-review`.
- Rejected: `/lr:review` (generic, collides conceptually with engine built-ins), `/lr:trilens`
  (drops the loop), `/lr:review-cycle` (drops the three lenses), `/lr:converge` (names the goal,
  not the mechanism), `/lr:triad` (collides with `positioning-triad-differentiation.md` vocabulary).

## 4. The load-bearing decision: subagent-as-semantics

**In every existing fan-out site — recall, consult, merge — the subagent is an _optimization_:**
parallelism plus context isolation. Serial host-side execution reaches the same answer, just
slower. That is why Cursor's conservative serial override (`docs/engines/cursor.md`) is a lossless
degradation everywhere it currently applies.

**`trilens-loop` is the first skill where the subagent is the _semantics_.** Independence from the
author's bias *is* the deliverable. A host reviewing its own work is not a slow review — it is not
a review. So the usual graceful-degradation-to-serial escape hatch is **unavailable here**.

Consequences:

- The skill requires a **native engine subagent mechanism**. No host-side fallback.
- A headless shell-out (`cursor-agent -p`, `claude -p`, `codex exec`) would also give independence,
  and was considered — the user explicitly rejected workarounds in favour of native subagents.
- On an engine with no verified subagent mechanism, the skill reports that plainly and stops rather
  than pretending. It does **not** silently degrade into self-review.

Candidate lore topic: `subagent-as-optimization-vs-subagent-as-semantics.md` — a new axis on the
engine-degradation question, and the first case where a binding's conservative fallback is
feature-destroying rather than merely slower.

## 5. Per-engine subagent binding

| Engine | Mechanism | Read-only enforcement | Status |
|---|---|---|---|
| Claude Code | `Agent` tool, `subagent_type: general-purpose`, 3 parallel calls in one message | by instruction | verified in practice (v11–v28 ships) |
| Codex | `spawn_agent`, role `explorer`; collect with `wait_agent` | structural (`explorer` is read-only) | verified end-to-end (v19) |
| Cursor | `Task` tool (subagents shipped in Cursor 2.4; editor + CLI + Cloud) | `readonly: true` in an agent definition | **documented, not yet validated by us** |

Hard rules:

- **Never a context-inheriting fork.** On Claude that means never `subagent_type: "fork"` — a fork
  inherits the host's conversation and with it the bias the skill exists to remove.
- **Reviewers are read-only.** They report; they never edit. The host owns all writes. Prefer a
  structurally read-only role where the engine has one; otherwise instruct it.
- Codex `agents.max_depth = 1` and `max_threads ≈ 6` both accommodate three reviewers.

**Where these facts live (settled in round 1 of the self-review):** the shipped `docs/trilens-loop.md`
does **not** carry this table. It points at the engine profile's `subagent-spawn` binding and stops.
Restating per-engine mechanics in the procedure doc is a single-canonical-source violation, and the
copy had already dropped the caveat the canonical source keeps (Cursor's documented-vs-validated
distinction). The table above is a design record, not the runtime contract.

Two Claude-specific traps were pushed **up** into `docs/engines/claude.md`, where the Claude binding
belongs and where every other skill can benefit from them:

- `fork` inherits the caller's context, so it is unusable wherever independence is required. The
  profile previously did not mention `fork` at all.
- **Passing a `name` makes the call an Agent-Teams teammate, and a teammate does not auto-return its
  report to the caller.** Discovered the hard way during this very session: the first fan-out was
  spawned with names, three reviewers went idle without reporting, and the round had to be re-run
  unnamed. `parallel-reviewer-fanout-pattern.md` already recorded this gotcha; the engine profile
  did not, which is why it was available to be re-hit.

### Cursor — what changed and what is still open

The shipped `docs/engines/cursor.md` binding says *"no verified Cursor-native in-session subagent
mechanism is relied on by the framework… do not claim parallel fan-out on Cursor until it is
validated on the real engine."* That is **epistemic conservatism, not a discovered limitation** —
the probe notes (`cursor-agent-cli-probe-findings.md`,
`cursor-cli-and-harness-operational-notes.md`) contain zero mentions of subagents. The question was
never asked, because the serial override was sufficient for every skill that existed at the time
(19/19 lifecycle green at v20).

Established 2026-07-25 from Cursor's own docs:

- Subagents shipped in **Cursor 2.4**, available in *"the editor, CLI, and Cloud Agents."*
- The agent spawns them with a **`Task` tool**; several run in parallel; one extra nesting level.
- Definitions are markdown + YAML frontmatter in `.cursor/agents/` — and Cursor **also reads
  `.claude/agents/` and `.codex/agents/`**.
- Frontmatter carries `name`, `description`, `model`, `readonly`, `is_background`.
- Cursor **2.5** added async subagents and the nesting rule (a subagent may spawn, but its children
  may not) — one point release after the initial 2.4 ship. 2.4 shipped 2026-01-22.
- CLI support was **reportedly broken by a bug** (the `Task` tool was not injected into the CLI
  toolset, so subagents ran serially in one context), reportedly fixed for standard accounts in
  Q1 2026. **Community-sourced only** — forum threads spanning ~Feb–Apr 2026 describe the bug and the
  fix, but no official changelog entry could be located, so the specific date does not survive
  citation. Round 1's verification lens caught an earlier draft asserting "2026-03-02" under the
  banner "established from Cursor's own docs"; corrected to separate confirmed-official facts from
  community reports. Either way our profile was written 2026-07-05, after the reported fix, and was
  simply never rechecked.
- `cursor-agent --help` (2026.07.20-8cc9c0b) shows no spawn flag — expected, since `Task` is a
  model-facing in-session tool, exactly like Codex's `spawn_agent`.

**Open, to be settled by the lifecycle test:** whether Cursor's `Task` tool accepts a **free-text
brief** (like Claude's `Agent`) or only dispatches a **pre-defined agent file by name**. The skill
needs free-text briefs — lenses are chosen per change, so they cannot be pre-declared. If Cursor
turns out to be name-only, the fallback is for the skill to write three throwaway definitions into
`.cursor/agents/` before dispatch and remove them after. Deliberately unresolved in the doc until
measured; the doc marks the Cursor path as unvalidated.

## 6. Interface

```
/lr:trilens-loop [free-text amendments]
```

**No flags.** One optional free-text argument, consistent with `/lr:recall [hint]` and
`/lr:consult <agent> [hint]`. Free text works identically on every engine, where flag parsing does
not, and it lets the user amend anything without the doc having to anticipate it.

```
/lr:trilens-loop
/lr:trilens-loop only one round, no fixes
/lr:trilens-loop use security, performance and API compatibility as the lenses
/lr:trilens-loop review only the changes under tests/
/lr:trilens-loop max 5 rounds
/lr:trilens-loop five lenses instead of three
```

**Free text is genuinely free** (user decision, 2026-07-25): it may override anything, including
the round cap, the lens count, and the independence rule. The one obligation is **visibility** —
when an amendment switches off a default rail, the skill says so out loud in its output rather
than silently complying. Rails that are quietly removed are worse than rails that were never there.

## 7. Default scope

Default = **everything this session changed**, not a git range. The anchor is *what we did here*.

Resolution order:

1. The files the host edited or created this session (the host knows these directly).
2. Cross-check with `git status --porcelain` and `git diff` in each repo those files live in, to
   catch changes the host forgot and to produce reviewable diffs.
3. If the session also committed, include those commits.
4. State the resolved scope before dispatching, so a wrong scope is caught before three agents are
   paid for.

Multi-repo sessions are normal in a lore workspace (plugin + dev repo). Scope may span repos; group
the file list by repo. Free text can narrow or replace the scope entirely.

## 8. Lens selection

The host picks three lenses from the change and the session, not from a fixed list.

Rules (inherited from `parallel-reviewer-fanout-pattern.md`):

- **Mutually exclusive.** If two reviewers would find the same issues, a slot is wasted.
- **Tell each what to skip**, including what the other lenses own.
- **The don't-fan-out test:** *would a single agent looking at all N items produce the same verdicts
  as N separate agents?* If yes, batch instead — a fan-out over items that share a uniform property
  adds cost without adding rejection power.
- Starter catalog (a menu, not a default): correctness, security / adversarial input, UX &
  discoverability, framework architectural consistency, terminology coherence, newcomer experience,
  release readiness, AI-installer literal-execution, filesystem-grounded verification.
- The architecture lens gets pointed at the booted agent's `lore-context.md` as a baseline, so it
  can apply the agent's own stated meta-rules to the change.

## 9. Brief shape — goal, not rationale

Each reviewer brief carries: context (what changed and **what it is for**), the file list with
absolute paths, what to look for under this lens, what to skip, and the output format.

**Deliberate omission: the host's rationale for each choice.** The reviewer gets the *goal* — enough
to judge fitness for purpose — but not the argument for why each decision was made. Rationale
pre-empts the criticism the fan-out is being paid to produce. This is the bias-minimisation rule at
the brief level, the counterpart to not inheriting session context at the spawn level.

Candidate lore topic: `brief-the-goal-not-the-rationale.md`.

Output format required from every reviewer:

- Findings: severity (`BLOCKER` / `HIGH` / `MEDIUM` / `LOW`), `file:line`, the issue, a
  one-sentence fix.
- A closing **verdict line**: `SHIP`, `SHIP-WITH-FIXES`, or `BLOCK`.
- ≤600 words, to keep three reports digestible.

## 10. Round protocol

**Round 1** — breadth. Three reviewers in parallel, lens-isolated.

**Triage** — the host's job, and the one place authorship is an advantage:

- **Verify every `BLOCKER` and `HIGH` against the actual file before acting.** Reviewers
  occasionally hallucinate or work from stale state.
- Accept or decline each finding, each with a one-line reason. Declining is legitimate.
- Cross-check overlap: two lenses hitting one issue from different angles is one fix, noted twice.
- Fix what was accepted.

**Round N+1** — fresh reviewers, because independence is the point. Fresh reviewers have no memory
of the previous round, so each brief **must** open with:

1. A numbered **APPLIED / DECLINED (+reason)** ledger of *that lens's own* prior findings.
2. A short digest of what the *other* lenses' fixes changed in this lens's territory.

Without that ledger, declined findings resurface every round and the loop never converges. With it,
across a validated four-round run, no reviewer re-raised a settled item.

Expect round N's findings to cluster on round N−1's **edits** — fixes create new seams. That is
normal convergence behaviour, not failure.

**Optional final round** — when the loop is already converging, the last round may be a *single*
reviewer with the full diff and filesystem access, rather than three lens-isolated ones. Round 1 and
the final round are different jobs: breadth-parallel-isolated versus depth-sequential-whole. A
single full-diff reviewer catches cross-file drift that per-lens reviewers structurally cannot.

## 11. Termination

Stop when a round produces nothing worth fixing. Convergence by shrinking findings count is the
signal — typical runs converge in 2–3 rounds; large cross-cutting changes have taken 7.

Two guards:

- **Round cap, default 3.** Amendable by free text. Prevents an unattended loop from burning agents.
- **Reviewer-gated stop.** The loop may not terminate while any reviewer's most recent verdict is
  `BLOCK`. The host may still override — it must say so explicitly, with a reason. Without this the
  same session both writes the fixes and grades its own convergence; the guard makes termination
  partly reviewer-owned.

On hitting the cap with findings still open, report what remains rather than declaring success.

## 12. Degradation

- **Partial returns are additive evidence.** A reviewer that returns one finding then stalls has
  done useful work. Do not discard the round; read what came back.
- **Fewer than three returning is still a round** — continue, and say which lens is missing.
- **No native subagent mechanism → stop and report.** Never self-review under the skill's name.

## 13. Boundaries

- Not `/lr:check` (domain content consistency) and not `/lr:doctor` (runtime ailments) — those are
  state-scoped; this is change-scoped.
- Not part of finalization. It **never writes lore**, never reflects, never merges, never commits.
- It *does* edit the files under review — that is the point of the loop. `--report-only` behaviour
  is available through free text ("no fixes").
- No persistence in the MVP: the ledger is printed, not filed. Persisting review records is a
  possible follow-up.

## 14. Cost

Three subagents per round, 2–3 rounds typical. Real but proportionate for a substantive change; not
for a one-line edit. The doc says so, so the skill is not reached for reflexively.

## 15. Ship scope

Plugin (`lore-framework`):

- `skills/trilens-loop/SKILL.md` — thin pointer.
- `docs/trilens-loop.md` — all logic.
- `.cursor-skills/lr-trilens-loop/SKILL.md` — generated by `scripts/sync-cursor-skills`.
- `docs/engines/cursor.md` — subagent-spawn binding updated (stale since 2.4).
- `README.md` — skill table entry.
- **No `VERSION` bump and no manifest bumps** — this increment merges into a bigger release later.
  Cache-clear applies at that release, not here.

Dev (`lore-framework-dev`):

- A lifecycle scenario covering this skill only.
- This draft.
- The release-notes increment, held here until the bigger release absorbs it.

## 16. Open seams

- **Cursor `Task` free-text vs named-definition** (§5) — settled by the lifecycle test.
- **Persisting the ledger** — out of MVP scope; revisit if review records prove worth keeping.
- **Reviewer model tier** — inherits the session default; no knob. Free text can ask for a tier
  where the engine supports it.
- **Interaction with `/lr:spawn-teammate`** — named teammates do not auto-return their reports, so a
  teammate-based variant would need explicit send-back instructions. Out of scope; the skill uses
  plain background subagents.
