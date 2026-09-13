# WHAT TO IMPROVE — Standing Improvement List

The standing, prioritized improvement list for the Lore Agents framework. Established
2026-07-18 at the user's request, with the explicit intent that a list of this type
**always exists** — a continuous-improvement instrument for the framework, not a one-off
review artifact. Work it down across sessions; refresh it with each new review.

**Relationship to `framework-improvements-backlog.md` (lore):** the backlog is the
canonical *unranked* store of deferred items, grouped by area, with full detail. This file
is the *ranked action view* — what to do next and why, in priority order. Items here carry
a couple of sentences plus pointers; deep detail stays in the backlog entry or lore topic
they reference. The two must not fork: when an item's detail grows, it goes to the backlog
or a topic, and this file keeps the one-liner + pointer.

## Refresh Protocol

- Reread at the start of every framework-work session; the priorities here frame what to
  pick up next unless the user directs otherwise.
- Full refresh at each periodic architecture review (last: 2026-07-18). A refresh re-ranks
  surviving items, inserts new findings in rank order, and deletes shipped/moot entries
  (git history preserves them — delete-don't-mark).
- When an item ships: mark `✅ done <date>, <version/commit>` inline, delete on the next
  refresh.
- Evidence discipline: items born from a review cite the evidence (what was measured or
  observed), so a later session can re-verify rather than trust a stale claim.

## Verdict of the 2026-07-18 Review

Architecture is coherent and disciplined: the three-layer model is clean, skill→doc
pattern mostly honored, v27 stamps/manifests/cursor-parity all consistent, docs lean
(~4.2K lines). Two structural risks: **(1) mechanical procedures executed as LLM
instructions don't hold at current scale** — a deterministic sweep found 14 unresolved
lore cross-references that `/lr:check` #9–10 nominally cover; **(2) no subtraction force**
— the rot predicted by the consolidation/"sleep" thread is now measured, not hypothetical.
Biggest UX gap: agents only remember when *asked* — ambient recall and friction-free
capture would change how the system feels more than anything else here.

---

## A0. Lore sync hardening (v46) — SPEC READY, TIERED, NOT YET IMPLEMENTED — added 2026-09-13

**Top of the list.** Full spec: `workdir/draft-lore-sync-hardening.md` (§ 14a carries the
implementation order; § 14 the review history).

Problem, established by direct git experiment rather than from docs: lore repos accumulate local
commits that are never pushed, nothing detects it, and once a repo diverges every later boot's
`git pull --ff-only` fails permanently while the agent loads stale lore in degraded mode. The
framework manufactures the state itself — `finalize.md` Phase 4 stages `git add agents/` and pushes
without merging, `resolve-conflicts.md` gives up after three tries leaving a commit, and
`update.md`'s push gate refuses precisely when the branch is already ahead. `repo_scan.py` computes
no ahead/behind for agent repos, so none of it is visible to `/lr:check`.

**Next action — implement Tier A, now amended and cleared:** C5 (refresh TTL keys on
`last-success`, not `last-attempt`, with outcome-keyed backoff), C6 (`workspace-pull` Phase 0 stops
pre-refusing on a dirty tree), C7 (`conventions.md` § Tooling: Git Safety, rules 1-2 plus a Known
gap), and C4 in **bare** form (R16 ahead/behind, severity keyed on `diverged`, no marker). Bare R16
is also the instrument that tells us whether Tiers B and C are worth building.

A round-4 review scoped to **Tier A alone** (2026-09-13) returned 2× SHIP-WITH-FIXES and 1× BLOCK —
six real findings, all amended into the spec. The earlier "no further review needed" was wrong:
nine passes had reviewed the whole spec, never the subset, and two of the six would have shipped a
user-visible regression. Ships as **v46** (release-notes-only, cache-affecting); Tier B becomes v47.

**Then Tier B** (C1/C2/C3/C3a — the `publish-lore.md` procedure) **only after one deep
unconstrained cold reviewer**, per `parallel-reviewer-fanout-pattern.md`'s rule for a loop that hit
the round cap without converging. **Tier C** (marker, C8, conflict classification) is deferred by
design — it produced most of the findings in every round, and Tier A's data should decide whether it
is built at all.

Evidence: three review rounds (3, 4, 3 cold lenses), findings 14 → 16 → 13, five BLOCK/BLOCKER
verdicts total. Not converged at the ceiling. Round 3's only BLOCK was a defect round 2's fix
introduced; the core design was never attacked by any lens.

---

## A. Verified inconsistencies — fix now (bounded, "v28 hygiene ship" tier)

### A0. `lr-core` CLI — script-back the mechanical halves of high-frequency skills — DESIGN DRAFTED
Design + phased execution plan in `workdir/draft-lr-core-cli.md` (2026-07-25 design dialogue;
implementation deferred by the user — resume from the draft). One python3-stdlib CLI
(`scripts/lr-core`: `discover`/`preflight`/`scan`/`finalize-git`/`check`) replacing the prose
choreography of boot/attach/consult/recall/finalize-phase-4, with pull-TTL caching and a new
framework-level **Script Fallback Contract** in `conventions.md` (script fails → engine notifies
user, takes over manually per the canonical prose spec). Subsumes/serves A1, A2, B2, and feeds
B3/B4. Evidence: this boot measured 9 tool calls / ~450 prose lines for ~2 lines of judgment.

### A1. Reference rot + `/lr:check` mechanical-check reliability — OPEN
Deterministic sweep (2026-07-18) flagged 14 unresolved topic-style references in
lore-architect's 147-topic graph; ≥8 are genuine rot from renames/deletions:
`contributions-feature.md` (referenced by 7 topics), `workspace-sync.md` (v25 rename),
`dev-repo-lore.md`, `dev-module-conventions.md` (DF-rename leftovers),
`codex-binding-design.md`, `beta-refinement-workflow.md`,
`codex-multiagent-research.md`, `codex-multiagent-live-capture.md`. Checks #9/#10 promise
exactly this coverage → confirmed reliability gap: an LLM under-extracts at O(topics ×
refs). **Do:** script-back the mechanical subset of `/lr:check` (a `scripts/` helper the
skill invokes for ~#2–3, #9–11, #13–14, #19–21; LLM keeps semantic checks #15–16), and
clean the rotten links in the same pass (completable sweep — don't defer, per
`feedback-don-t-defer-completable-scope.md`). Backlog ref: § Documentation / Meta (the
`contributions-feature.md` bullet, now superseded by this broader item).

### A2. `list-agents` / `list-repos` violate the thin-pointer rule — OPEN
Both carry full procedure logic inline in SKILL.md; the framework's own pattern
(`skill-doc-pattern.md`, `single-canonical-source-discipline.md`) says logic lives in
`docs/`. **Do:** move bodies to `docs/list-agents.md` / `docs/list-repos.md`, thin the
SKILL.md files, re-run `sync-cursor-skills`.

### A3. `sync-cursor-skills` ignores unknown flags and always writes — OPEN
Passing `--check` (2026-07-18) silently rewrote all 30 wrappers (byte-identical, no
damage — but a check invocation that mutates is a footgun, and `/lr:check` #21 would
benefit from a real dry-run). **Do:** add `--check` (exit non-zero on drift, write
nothing), reject unknown args.

### A4. Structured test-run metrics across all suites — OPEN
Today's v28 e2e gate made cost/time reporting too manual: lifecycle results now persist
module durations, but not a unified cross-suite run record; Claude cost is extractable from
stdout, while Codex/Cursor report no USD in the current logs. **Do:** add a structured
test-run metrics layer covering deterministic unit tests, standard lifecycle e2e, Keeper
lifecycle e2e, and quality benchmark runs. At minimum record suite, command, framework/dev
commit SHAs, started/ended timestamps, wall time, per-module/per-test durations, engine,
model, status, result paths, and per-engine/per-test cost where the engine exposes it; mark
cost as unavailable rather than guessing where it does not. Output should be machine-readable
JSON plus a short markdown summary suitable for checked-in release-gate notes. Evidence:
2026-07-22 v28 run required manual reconstruction of total time/cost from lifecycle logs.

### A5. v27 partial test gate has no tracked follow-up — ✅ done 2026-07-22, covered by v28 gate
`release-notes/27.md` honestly records the skipped Claude/Haiku + Codex lifecycle runs,
but nothing schedules them — the next ship would silently inherit an unverified base.
**Do:** run the deferred suites (limits have reset), or the next ship's gate must cover
the union of v27+v28 changes. Covered by the v28 standard lifecycle matrix plus targeted
reruns recorded in `workdir/v28-e2e-gate-2026-07-22.md`; delete on the next refresh.

### A8. `agent-boot.md` doubled in the release that scripted it — OPEN, **v32 tier (explicitly not v31)**
Measured 2026-07-28: the boot procedure went 51 → 108 lines on the v31 branch, in the release
whose purpose was to move it into `scripts/lr-core`. `auto-pull.md` went the other way
(100 → 80), so the literate-accelerator thesis holds there and fails here. Every boot on every
engine pays ~3K tokens for the most-read doc in the framework. Three causes, only one
legitimate: (a) ~a quarter of the file is the standing operating manual, not boot — splitting
it out is pure filing, zero behavior change; (b) Step 2 hand-writes prose routing for JSON
fields the script already computed, where `read_next` already solves the same problem in two
lines for `role.md`/`lore-context.md`; (c) the remainder is load-bearing scar tissue pinned by
lifecycle scenarios — do not trim it blind. **Do:** (a) then (b), each behind the normal
gates. **Deliberately deferred past v31** — reopening the most-read procedure doc while v31 is
four commits from shipping moves the ship further out. Evidence + word-level breakdown:
`agent-boot-doc-grew-when-scripted.md`. Backlog ref: § Framework Upkeep — "no subtraction
force".

### A7. Lifecycle harness doesn't verify which plugin actually loaded — ✅ done (holes closed 2026-07-28, ungated)
Confirmed live 2026-07-27 running the suite against the parked v31 branch: `harness.py`'s
`run_engine()` passes `--plugin-dir <framework_dir>`, but on Codex and Cursor an
installed/cached plugin silently won over that flag — both engines ran the full suite
against an installed v30 plugin while reporting results as if v31 had been tested. Claude
Code was unaffected only because nothing was installed for it globally on that machine,
which is incidental, not structural. A green or red result under this condition is
uninterpretable either way. **Done:** `verify_plugin_identity` probes loaded VERSION (+
FRAMEWORK-ROOT) and asserts against `LR_FRAMEWORK_DIR`; Codex also gets a deterministic
marketplace-source/cache preflight; `run_matrix.py` fails an engine's shard before any
module runs. Opt out only via `LR_SKIP_PLUGIN_IDENTITY=1` (debug).
**Follow-up, 2026-07-28:** the first fix shipped with two structural holes (per-run
`framework_dir` overrides unchecked — and `test_08` is the only scenario handed a different
tree, so the one test needing verification was the one skipping it; and the verdict cached
per process, proving identity at probe time only). Worse, the **Cursor arm was a model
self-report**, which passed while the suite ran on v30. All three closed
(`check_cursor_plugin_sources()` walks `local/`+`marketplaces/`+`cache/` off the filesystem;
override verification; `engine|realpath|VERSION` verdict inheritance, which also removed
`test_takeover`'s 420s timeout). **These fixes are ungated** — no lifecycle run has seen
them. See `lifecycle-harness-plugin-identity-unverified.md`,
`a-gate-cannot-be-a-model-self-report.md`, `tests/test_lifecycle_plugin_identity.py`.

### A9. Lifecycle runner: identity-blocked engines render as failures — OPEN, corrected 2026-08-31
**Corrected after verification — the original entry was wrong on two of its three claims, and
acting on it would have "fixed" already-correct code.** Measured against `run_matrix.py` at
`9f164e9` (unchanged since v36, so the 2026-08-31 observation ran exactly this code):

- ~~refusal exits 0~~ — **false.** `LR_LIFECYCLE` unset returns **2**. Verified by running it.
- ~~failed module runs exit 0~~ — **false.** `summarize()` returns `not failed`; `main()` returns
  `0 if all_ok else 1`. A 9/18 run returned 1.
- identity-blocked engines render as `failed 0.0s` — **true, and still open.** Two blocked engines
  read as ~18 test failures when nothing ran. Confirmed again on 2026-08-31.

**Root cause of the original false-green report: the invocation, not the runner.** Gate runs pipe
the runner (`... 2>&1 | tail`), so `$?` is the *pipe's* last element. Reproduced: same command
piped reports 0 while the runner returns 2. A backgrounded wrapper ending in `echo` does the same —
a task notification said "exit code 0" for a run whose runner returned 1. `--dry-run` also exits 0
and prints a plan that resembles the refusal output, giving a second way to misread the same run.

**Do:** (a) give identity-blocked engines a status distinct from `failed`; (b) write the runner's
exit code into `summary.json` so the verdict survives the pipe — the point-of-use guardrail, since
triage reads the artifact, not the shell (`point-of-use-guardrails-beat-recorded-lore.md`);
(c) close the empty-matrix edge, where zero configs makes `all_ok` true and exits 0. **Do not**
"fix" the refusal or failed-module exit codes; they are correct.
Lore: `lifecycle-harness-exit-code-is-not-a-verdict.md` (corrected in the same pass).
Backlog ref: § Framework Upkeep § Lifecycle Harness Reliability.

### A10. `preflight --agent-dir` upward search has no test — OPEN, added 2026-08-31
v44 replaced the `<workspace>` join with an upward search. I hand-verified it across five invocation
shapes; that is not a gate, and the change is on the boot hot path. **Do:** add a deterministic test
and prove it red against v43 (`prove-a-new-test-red-against-the-previous-tag.md`). Ships with v44.

### A11. Three lifecycle scenarios are structurally flaky — OPEN, added 2026-08-31
`test_05`, `test_08`, `test_12` each assert the end state of a long model-driven chain and fail at
whatever step the model stopped at; `test_05` failed at three different assertions across three runs
(the exact distribution its own source comment documents). A test that moves between runs certifies
nothing and pollutes every triage. `test_08` additionally reads the wrong capture surface
(`transcript-vs-final-message-assertions.md`). **Do:** restructure to per-step assertions, or mark
them explicitly non-gating so a red is not mistaken for a regression. Lore:
`triage-a-red-module-against-its-own-history.md`.

### A12. v44's announcement convention has no gate at either level — IN PROGRESS, added 2026-08-31 (**top of tier A**)
v44 shipped `## Step 0 — Announce` to 33 skills: required literal text a model must print before
doing any work. Nothing verifies it. `/lr:check` has no item for the block's presence (v44's own
Known Limits says so), and the lifecycle suite had **no runtime assertion anywhere** that an
announcement is ever emitted — zero matches for `Announce`, `Booting the agent`, or `First I pull`
across every test module.

That gap sits on a failure mode now measured rather than assumed. The 2026-08-31 two-engine run
produced three instances of *substance right, required literal output wrong*: `test_style` dropped
the mandatory `Style set:` line 2 of 3 runs while correctly applying the style; `test_trilens_loop`
emitted `**LENSES:**` for a prompt that said "print exactly these lines"; and a boot in this very
session printed four status lines Step 2 says to suppress. `docs/style.md` already carries maximum
emphasis on its confirmation — "mandatory", "the skill's only result you can check" — and lost
anyway, which is `the-terminal-step-is-the-step-that-gets-dropped.md` reproducing under test.

**Measured on real transcripts:** Claude/haiku announces on boot 3/3; **Codex/gpt-5.4-mini does not
announce at all** on the boot path, 3/3. So the convention is already half-broken in the field and
nothing was reporting it.

**Do:** (a) `test_09_boot_announces_before_working` in `tests/lifecycle/test_boot.py` — shipped on
`v45-announcement-gate`, red against `lr--v1.43.0` (no Step 0, no anchors) and green against v44;
(b) decide what the Codex miss means — engine-profile guidance, or a doc-structure fix per
`instruction-location-beats-emphasis-in-long-docs.md`, *not* more emphatic prose; (c) a `/lr:check`
item for Step 0 presence across the 33 skills, closing the static half.
Lore: `skill-announcement-convention.md`, `the-terminal-step-is-the-step-that-gets-dropped.md`.

### A6. `docs/engines/claude.md` ↔ `CLAUDE.md` case-collision on macOS — OPEN (low)
Observed live 2026-07-18: on case-insensitive APFS, Claude Code auto-injects
`docs/engines/claude.md` as *directory memory* whenever any file under `docs/engines/` is
read (filename matches `CLAUDE.md` case-insensitively). Harmless today (duplicate
context), but an unintended semantic. **Do:** rename the profile file (touches boot
Step 0's `<engine>` → filename mapping) or document the quirk. Low priority.

---

## B. Known gaps to promote from the backlog (fresh justification attached)

### B0. TriLens fix boundary — OPEN, added 2026-08-11
Two releases running (v37, v38), every round after the first found a defect created by the
previous round's fix, and both loops ended at the ceiling — so both **shipped unreviewed
repairs**. It is arithmetic: N rounds review only N−1 rounds of fixes. This is our own
pre-ship gate leaking, which is why it ranks above the rest of B. **Do:** D3+D4 first, they
are free — state each finding's blast radius (implementations, *statements* of the rule,
container requirements) before editing, and re-read the fix in its container rather than in
the diff, since 7 of 8 observed fix-defects were context errors that a diff cannot show. Then
D1+D2 together: a fix-free final round, plus a fix-audit reviewer that does not consume a
round. Design: `draft-trilens-fix-boundary.md`. Lore: `fix-defects-are-context-errors.md`.
Backlog ref: § Multi-Agent Collaboration § TriLens Fix Boundary.

### B1. Post-merge diff verification — OPEN
Merge remains the highest-risk operation with no safety net (outside review 2026-07-02;
still true). **Do:** ship as opt-in `/lr:finalize --verify-merge` — a second booted-as-self
subagent adversarially reviews the merge diff pre-commit. Backlog ref: § Merge Quality.

### B2. Staleness surfacing at recall — OPEN
One `git log -1` call per surfaced hit; at 147 topics spanning >1 year, age-blindness is a
real quality issue now. **Do:** ship the `lore-search.md` date-annotation as sketched in
the backlog (§ Search / Scaling), soft-flag topics older than ~6 months.

### B3. Consolidation "sleep" pass — report-only first — OPEN
The 2026-07-18 rot findings are exactly what this thread predicts. Full restructuring is
high-blast-radius; a **read-only groom report** is safe: dangling refs, orphan topics,
over-granular clusters, lore-context drift. Composes with A1's script. **Do:** promote to
a design draft; ship `/lr:groom --report` (name TBD) before any applying mode. Backlog
ref: § Lore Housekeeping.

### B4. Semantic search — trigger fired (147 > 100), measure before building — OPEN
Don't jump to Chroma. **Do:** extend the quality benchmark with search-recall probes to
test whether subagent-scan actually degrades at this scale; decide on data. Backlog ref:
§ Search / Scaling; `vector-db-search-parked.md`.

### B5. Trust model for team-shared lore — undocumented — OPEN
Auto-pull lands a teammate's push in everyone's context at next boot; lore is
data-that-becomes-instructions → prompt-injection surface with fleet-wide blast radius
(one careless commit suffices; no malice needed). **Do:** short threat-model doc + a
"review lore diffs like code diffs" convention; disproportionately valuable for
enterprise adoption. New item (no backlog entry yet).

### B6. Claude community marketplace submission — OPEN
Pending since v25. Lowest effort, biggest visibility win on the list. **Do:** `claude
plugin validate --strict`, then the Console form. Backlog ref: § Marketplace Distribution.

### B7. Orphan version stamps — live evidence, ship the commit half — OPEN
Observed 2026-07-18: `lore-framework-dev/lore-repo.md` dirty with an uncommitted v27
stamp; `lore-agents/` still stamped 26. Exactly the failure the parked boot-time
auto-commit item describes. Full design drafted in `workdir/draft-auto-push-after-upgrade.md`.
**Do:** consider shipping just the commit half (no push) as a smaller first step. Backlog
ref: § Boot-Time Auto-Commit + Auto-Push.

### B8. Cursor IDE boot assumes Claude — OPEN (live 2026-07-29)
Booting in Cursor IDE chat (extension-host), not `cursor-agent` CLI, yields
`confidence: assumed` → Claude reference profile. Ancestry sees `Cursor Helper` /
`Cursor.app` only; those are deliberately non-signals so Claude-in-Cursor-terminal
is not mislabeled. Workspace `<framework-root>` also misses `~/.cursor` containment.
**Do:** decide among trusted IDE-only argv signal (with negative test), shortcuts
passing `--engine cursor`, profile doc of the assumed path, and/or prefer
plugin-cache framework-root on Cursor. Backlog ref: § Boot Step-0 Engine Detection
Ordering (2026-07-29 bullet).

### B9. `being.md` vs `create-agent.md` — who decides registration — OPEN, added 2026-08-31
v44 makes `/lr:create-agent` register the agent it creates (an unregistered agent is invisible to
the workspace and lands straight in `workspace-status` S11 — the framework's own skill producing the
state its own diagnostic reports). `docs/being.md` keeps its opt-out, which the user has twice
declined to change, so the coupling now rests on a cross-doc inference and the two docs disagree
about *who decides* (step 8 forbids asking; `being.md` says "unless the user asks"). **Do:** settle
the decision owner in one place when v44 resumes. Lore:
`create-agent-registers-what-it-creates.md`.

### B10. Cross-engine lifecycle coverage is blocked by local installs — USER DECISION, added 2026-08-31
On this machine a worktree-based gate run passes plugin identity on **Claude only**: Codex's
marketplace source in `~/.codex/config.toml` points at the main checkout, and an installed Cursor
v42 tree can outrank `--plugin-dir`. So a default gate run is Claude-only and every ship gated that
way must record Codex and Cursor as *did not run*. **Do (only if cross-engine evidence is wanted):**
repoint Codex's marketplace source at the worktree, move `~/.cursor/plugins` aside, re-verify
identity **after** the move, then re-run. Not to be done silently mid-gate. Lore:
`lifecycle-harness-plugin-identity-unverified.md`.

### B11. Keeper login item reads as `python3.14` with a blank icon — OPEN, added 2026-09-05
Every macOS Lore Beings user sees their Keeper in **Login Items & Extensions → App Background
Activity** as a bare interpreter name with a blank icon, because `lrb install` writes
`ProgramArguments[0] = sys.executable` (`lrb.py:1511`). **Do:** ship a small named + iconed wrapper
from `lrb install`. Cheap, purely cosmetic, and the first thing a prospective adopter sees of the
daemon they just let run at login. Blocker: the working mechanism is verified on Intel only and
must be re-tested on Apple Silicon. Mechanism and constraints:
`keeper-login-item-name-and-icon.md`; action item: backlog § Autonomous Agents / Lore Beings.

---

## C. New feature directions — what would make Lore Agents sexier

### C1. Ambient recall — the biggest available UX leap — OPEN
Knowledge currently surfaces only at boot or on explicit `/lr:recall`. Tier 1 (free): a
boot-doc convention — when the task shifts topic, search lore before proceeding. Tier 2
(Claude-first): a `UserPromptSubmit` hook matching the prompt against topic descriptions,
injecting top-K pointers. "Your agent remembers without being asked" is the demo that
sells the system.

### C2. `/lr:note` micro-capture — OPEN
One-liner mid-session lore capture appended to `reflections/`, integrated by the normal
merge at finalize. Kills the learning-only-at-finalize bottleneck, partially de-risks
crashed sessions, answers the backlog's reflect-merge-ergonomics item. Smallest build on
this list.

### C3. Lore MCP server (`lr-lore`) — OPEN
Expose lore search/read over agent repos as MCP tools → claude.ai web/mobile/Slack can
consult the team's agents without a coding CLI. Substrate is already engine-agnostic
files+git. Extends `agent-as-universal-working-environment.md` beyond terminals — a
surface-federation angle distinct from (and not eroded by) the engine-federation claims
that `similar-projects-landscape.md`'s 2026-07-20 re-survey found competitors now also
make; none of the surveyed CLI-bound tools reach non-CLI surfaces like this today. Medium
build, biggest strategic reach.

### C4. Scheduled autonomous maintenance — OPEN
Nightly routine (Claude Code cron/routines exist now): workspace-pull → script-backed
check (A1) → staleness/groom report (B2/B3) → morning summary. First genuinely shippable
rung of `autonomous-agents-vision.md` on existing engine features.

### C5. OKF (Google Open Knowledge Format) alignment evaluation — OPEN
Added 2026-07-20 from the landscape re-survey. OKF v0.1 (Google, 2026-06-12) standardizes
markdown-in-git knowledge graphs — our substrate space. Evaluate: read the spec, then pick
(a) topic frontmatter adoption, (b) `lore → OKF` export bridge, or (c) watch-and-wait.
Cheap interop win if OKF gets traction; conflicts with our no-frontmatter-on-topics
convention, so don't rush a convention change for a v0.1 spec. Backlog ref: § OKF
Alignment; see `similar-projects-landscape.md`.

### C6. Lore graph visualization — OPEN
Script rendering the topic graph to HTML: nodes = topics, edges = references, color =
staleness, orphans highlighted. Cheap, demo-sexy, doubles as the groom report's visual
surface.

---

## Recommended Sequencing (as of 2026-07-18)

1. **v28 hygiene ship:** A1–A5 + the rot cleanup (A6 optional).
2. **Quality ship:** B1 + B2 (merge safety + staleness).
3. **UX ship:** C1 tier 1 + C2.
4. **Own design sessions:** B5 (trust model), C3 (MCP server), C4 (autonomous
   maintenance).
5. **Continuous:** B6 (marketplace) whenever ready; B3/B4 data-gathering alongside.

**v45 tier (re-ranked 2026-08-31, after the first identity-verified two-engine gate):**
**A12 first** — v44's announcement convention has no gate at either level and the boot half of it
is already failing on one engine. Then A9's surviving third (identity status + exit code in
`summary.json`), then A11, since three flaky scenarios pollute every triage of the above. A10 is
unblocked but no longer urgent: `test_33`, the failure that looked like an `--agent-dir` regression,
was a stale v32 plugin and cleared under verified identity.
B9 stays a design decision to settle. **B10 is closed** — Codex identity was never the marketplace
source; a five-week-old v32 tree in `~/.codex/.tmp/marketplaces/` outranked the v44 cache. Moved
aside 2026-08-31; identity green 5/5 since.

**v32 tier (still open):** A8 (`agent-boot.md` subtraction pass).

## Provenance

2026-07-18 architecture review, lore-architect (session on Claude Code / Fable 5, max
effort). Method: prior-dispositions load (`architecture-review-dispositions.md`,
`framework-improvements-backlog.md`) → mechanical consistency sweep of `lore-framework/`
(versions, manifests, cursor parity, skill-doc conformance, deterministic reference sweep
across plugin tree and lore graph) → doc/catalog deep-read (`check.md`, skills, README
funnel) → synthesis. Settled dispositions were respected and not re-raised
(DF-inside-`lr`, team-shared framing — see `architecture-review-dispositions.md`).
