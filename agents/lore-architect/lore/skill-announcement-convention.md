---
lore: 1
type: topic
summary: "The Skill Purpose Announcement convention shipped in v44: Step 0 announcements authored per skill as onboarding material, plus the v44 ship record, gate dispositions and open items."
parent: lore-context.md
---

# Skill Purpose Announcement convention (v44)

Every skill prints a short user-facing announcement before its first procedural step, in a
`## Step 0 — Announce` section holding one instruction line and the announcement itself as a
blockquote.

**Status: shipped 2026-08-31** as tag `lr--v1.44.0`, merge commit `26a9dac` on `lore-framework`
main (feature commit `c56eb60`). The v44 entry is in
[versioning-release-types.md](versioning-release-types.md), which carries the full gate record.

## Origin

User observation, 2026-08-30: `/lr:workspace-init` and `/lr:workspace-status` "just silently start to
do smth on the background." Legible to the author, opaque to an adopter. The framing that decided the
shape: announcements are **onboarding material, not status lines** — reading them in sequence teaches
the framework's vocabulary without a separate tutorial.

## Design decisions and why

- **Authored per skill, in that skill's own doc.** My first proposal was a shared rule doc that all
  33 skills point at, justified by `single-canonical-source-discipline.md`. The user rejected it, and
  was right: the *rule* is shared, the *text* is not. The generalized lesson is
  [per-site-authoring-is-not-duplication.md](per-site-authoring-is-not-duplication.md).
- **`## Step 0 — Announce`, before the first procedural step.** Location decides whether an
  instruction runs; Step 0 is the one position a paged doc cannot skip past
  ([instruction-location-beats-emphasis-in-long-docs.md](instruction-location-beats-emphasis-in-long-docs.md)).
- **Framework concepts, never internals.** "I pull its lore agent repo," not the script that does it.
  The reader is an engineer who has not read our source. My first drafts named `lr-core` calls and
  were rejected for it.
- **Bold the one thing a newcomer is most likely to get wrong** — judged per skill. I first proposed
  a mechanical rule (always bold what the skill does to your files); the user rejected it as verbose
  and mis-targeting, because a fixed slot makes several announcements end on a limp "nothing is
  changed" while the genuinely surprising thing goes unmarked. **A formatting rule that fires the
  same way every time stops carrying information.**
- **Say "subagent".** I wrote "a separate helper" for generalization; the user's correction:
  "everyone knows what subagent is... 'helper' brings more confusion then generalization." Do not
  soften engineering vocabulary for an engineering audience.
- **"Lore agent repo", not "repo",** wherever a git repo holding agents is meant — a workspace
  commonly holds both those and the ordinary source repos the agents work on.
- **Explain the basics every time, briefly.** Explain-once-per-session was considered and rejected:
  it is a rule each of 33 docs would have to implement, with no reliable way for a skill to know what
  already ran in the session.

## Shape facts worth keeping

**Count note:** every number below is the v44 state. **v45 removed `doctor` and `workspace-status`, so the convention now covers 31 skills** — re-count before quoting it in release notes
([consistency-checks.md](consistency-checks.md) § When a ship's claim earns a check).

33 skills, but not 33 docs. `list-agents` and `list-repos` have no companion doc and carry Step 0 in
`SKILL.md`; the two `df-*` skills live under `df/`, not `docs/`; and `register-repo.md` backs **four**
skills, so its Step 0 branches on the invoked operation. Editing a Cursor mirror's source
(`skills/*/SKILL.md`) requires re-running `scripts/sync-cursor-skills` — which is **python3, not
bash**, despite carrying no extension.

The convention text lives in `conventions.md` § Skill Purpose Announcement.

## v44 ship record (2026-08-31)

v44 shipped more than the announcement convention: the committed-paths-must-be-relative contract
change (with the `<agent-dir-rel>` placeholder), `preflight --agent-dir`'s upward search,
`/lr:create-agent` registering what it creates
([create-agent-registers-what-it-creates.md](create-agent-registers-what-it-creates.md)), and three
migration fixes. It is a **both** release — `migrations/44.md` plus `release-notes/44.md` — and
cache-affecting, since every skill's procedure changed.

The release notes were **incomplete at ship time**: they carried no Verification section at all, so
the gate dispositions and the known bug were written into them as the last pre-push step
([a-release-record-goes-stale-while-you-fix-it.md](a-release-record-goes-stale-while-you-fix-it.md)).
The `540 tests / 15 modules` figure was **re-measured against the shipped tree** rather than copied
forward from this topic's earlier draft record — the same discipline, applied to a number that
happened to still be right.

**Gate record** (dispositions named explicitly, per
[gate-waiver-is-a-record.md](gate-waiver-is-a-record.md)):

- Deterministic tests — **passed**: 540 tests across 15 modules against the v44 tree.
- `/lr:check` — **passed**, after fixing the one error it found.
- Lifecycle, **Claude** — 8 of 9 modules pass; the one v44-caused failure is fixed and re-verified,
  and the three remaining reds are pre-existing flakes with failing history on the old checkout
  ([triage-a-red-module-against-its-own-history.md](triage-a-red-module-against-its-own-history.md)).
- Lifecycle, **Codex and Cursor** — **did not run** (plugin-identity refusal).
- `/code-review` — four rounds, converged; **round 4's own fixes are unreviewed**.
- Mechanical ship checks, re-run at push time — **passed**: 33/33 skills carry Step 0, every
  migration declares `## Write Paths`, `scripts/sync-cursor-skills` produced no drift, and VERSION
  plus all four manifests agree at 44 / `1.44.0`.

**Fixed here, worth not re-deriving:**

- `migrations/44.md` had no `## Write Paths` section. `/lr:check` #20 calls this an error because
  `version-check.md`'s boot-time upgrade gate then falls back to the blanket-dirty rule for any range
  containing v44 — every user with any unrelated dirty file blocked from upgrading.
- `migrations/33.md` and `check.md` #18 formed a **loop**: the check flagged an absolute target and
  named migration 33 as the remedy, while migration 33 wrote an absolute target.
- `migrations/33`, `37` and `44` defined `<workspace>` as the session cwd while needing the workspace
  root.

**Still open** (also carried in `framework-improvements-backlog.md` and `workdir/what-to-improve.md`,
which are the working lists — this is the ship-state record):

1. No test covers `preflight --agent-dir`'s upward search; hand-verified across five invocation
   shapes, which is not a gate.
2. `run_matrix.py` exits 0 on refusal and on failed module runs
   ([lifecycle-harness-exit-code-is-not-a-verdict.md](lifecycle-harness-exit-code-is-not-a-verdict.md)).
3. `test_05` / `test_08` / `test_12` are structurally flaky.
4. `being.md` and `create-agent.md` step 8 disagree about who decides registration for beings.
   **Shipped knowingly as a known bug** (user decision, 2026-08-31) and recorded in
   `release-notes/44.md` § Known Limits rather than fixed before the tag — Beings are BETA, so the
   blast radius is bounded. A contradiction between two docs is not caught by any check; it will
   resurface as whichever doc the executor happens to page.
5. Codex/Cursor gate coverage needs local install changes — a user decision.

## Known gap

There is **no mechanical enforcement** — no `/lr:check` item verifies Step 0 presence. That is a gap,
not a decision, and it is worth closing when v44 resumes: a convention with no check drifts, and this
one has 33+ sites to drift across
([consistency-checks.md](consistency-checks.md), `point-of-use-guardrails-beat-recorded-lore.md`).

## See Also

- [per-site-authoring-is-not-duplication.md](per-site-authoring-is-not-duplication.md) — the design
  rule this case produced.
- [step-number-cross-references-fail-silently.md](step-number-cross-references-fail-silently.md) —
  inserting this Step 0 into `agent-boot.md` is what surfaced that trap.
- `skill-doc-pattern.md`, `slash-command-system.md` — where skills and their docs are specified.
- `adopter-command-surface-curation.md` — the adjacent newcomer-facing IA work this feeds.
