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

## A. Verified inconsistencies — fix now (bounded, "v28 hygiene ship" tier)

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

### A6. `docs/engines/claude.md` ↔ `CLAUDE.md` case-collision on macOS — OPEN (low)
Observed live 2026-07-18: on case-insensitive APFS, Claude Code auto-injects
`docs/engines/claude.md` as *directory memory* whenever any file under `docs/engines/` is
read (filename matches `CLAUDE.md` case-insensitively). Harmless today (duplicate
context), but an unintended semantic. **Do:** rename the profile file (touches boot
Step 0's `<engine>` → filename mapping) or document the quirk. Low priority.

---

## B. Known gaps to promote from the backlog (fresh justification attached)

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

## Provenance

2026-07-18 architecture review, lore-architect (session on Claude Code / Fable 5, max
effort). Method: prior-dispositions load (`architecture-review-dispositions.md`,
`framework-improvements-backlog.md`) → mechanical consistency sweep of `lore-framework/`
(versions, manifests, cursor parity, skill-doc conformance, deterministic reference sweep
across plugin tree and lore graph) → doc/catalog deep-read (`check.md`, skills, README
funnel) → synthesis. Settled dispositions were respected and not re-raised
(DF-inside-`lr`, team-shared framing — see `architecture-review-dispositions.md`).
