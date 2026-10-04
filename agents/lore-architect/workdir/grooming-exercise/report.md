# Lore grooming exercise — five consecutive runs (2026-10-04)

Agent: `lore-architect`. Requested by the user: run `/lr:groom` five times in a row, measure after each, and report how the metrics progressed. Files in this directory: `metrics.jsonl` (raw snapshot per run), `table.md`, `measure.py` / `verify.sh` / `cursor.py` / `v1.py` / `run3_restructure.py` (the tooling used), `ws1–4.yaml` (the worksets selected).

All edits are **uncommitted** in `lore-framework-dev` pending session finalization. Validation (orphans, cycles, broken parents, topic-with-children) was empty after every run.

## Metrics tracked after each run

| Metric | Why |
|---|---|
| Mapped files / % and mapped tokens % | Share of the corpus the boot map can route to (v1 frontmatter + reachable parent) — the retrieval-coverage metric |
| Legacy (unmapped) files | Remaining conversion backlog |
| `lore-context.md` tokens | Always-loaded cost; v1 target ≤ 10K |
| Boot map tokens | The taxonomy map loaded at boot; shrinks as hierarchy deepens |
| Boot footprint tokens | Role + lore-context + map + system prompts: what every session pays |
| Root children | Fan-out of `lore-context.md`; flat = hard to navigate |
| Area hubs | Count of structural hubs (depth of taxonomy) |
| Total lore tokens | Corpus size (hubs add routing overhead; grooming here was *not* a deletion exercise) |
| Validation issues | Orphans / cycles / broken links introduced (must stay 0) |

Not measured but recorded per run below: stale facts fixed and links repaired (qualitative; the map cannot see them).

## Results

| Metric | Start of session | Baseline (groom #0, earlier) | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 mid | Run 5 |
|---|---|---|---|---|---|---|---|---|
| Mapped files | 129 | 130 | 133 | 150 | 159 | 159 | 174 | 189 |
| Mapped files % | 42.0 | 42.3 | 42.9 | 48.4 | 50.6 | 50.6 | 55.4 | 60.2 |
| Mapped tokens % | 46.7 | 46.8 | 46.9 | 51.7 | 52.9 | 52.9 | 54.3 | 56.8 |
| Legacy (unmapped) files | 178 | 177 | 177 | 160 | 155 | 155 | 140 | 125 |
| lore-context tokens | 10095 | 9865 | 9865 | 9865 | 7306 | 7306 | 7306 | 7306 |
| Boot map tokens | 7964 | 7964 | 7971 | 7981 | 3938 | 3938 | 4351 | 4998 |
| Boot footprint tokens | 30134 | 29904 | 29911 | 29921 | 23319 | 23319 | 23732 | 24379 |
| Root children | – | 122 | 122 | 139 | 57 | 57 | 63 | 72 |
| Area hubs | – | 4 | 5 | 5 | 10 | 10 | 10 | 10 |
| Total lore tokens | 400144 | 399858 | 400344 | 401651 | 405120 | 405147 | 406269 | 407374 |
| Validation issues | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

"Start of session" and "Baseline" bracket the earlier groom run in this session (a small first pass on five recently-changed files); Runs 1–5 are the requested exercise.

### Net change, start of session → end of Run 5

| | Start | End | Change |
|---|---|---|---|
| Mapped files | 129 (42.0%) | 189 (60.2%) | +60 files, +18.2 pts |
| Mapped tokens | 46.7% | 56.8% | +10.1 pts |
| Legacy files | 178 | 125 | −53 (−30%) |
| `lore-context.md` | 10,095 | 7,306 | −2,789 tokens (−28%) |
| Boot map | 7,964 | 4,998 | −2,966 tokens (−37%) |
| **Boot footprint** | **30,134** | **24,379** | **−5,755 tokens (−19%) per session** |
| Root children | ~122 | 72 | −41% |
| Area hubs | 4 | 10 | +6 |
| Total lore tokens | 400,144 | 407,374 | +1.8% (hub overhead; nothing deleted) |

## What each run did

**Run 1 — split the biggest topic.** `versioning-release-types.md` (21k tokens, with v37–v47 entries stranded after an unrelated section) became an area hub plus three lossless history children (`versioning-history-v01-v20 / v21-v36 / v37-v47`). Text moved verbatim and was verified line-by-line against the original (0 lines missing). Also fixed a stale "doctor" reference, a link to the moved v37 record, and an "two years of latency" error (it was three weeks). *Metric effect:* +3 mapped files, small; the gain is that the next reader loads ~2.5k tokens of rules instead of 21k.

**Run 2 — legacy → v1 conversion, first batch.** 17 legacy topics got v1 frontmatter (type, ≤240-char summary, parent) after being read in full. Stale statements fixed while reading: `architecture-overview` (VERSION "currently 12", doctor, `workspace-sync` script), `autonomous-agents-vision` ("nothing shipped yet" — Lore Beings shipped in v28), `auto-pull-mechanism` (`workspace-sync` vs `workspace-pull` naming), `agent-boot-doc-fidelity-fixes` ("fix staged, not applied" — it landed), `agent-being-consciousness-substrate-split`, plus two link repairs. *Metric effect:* +17 mapped files, mapped files 42.9 → 48.4%.

**Run 3 — taxonomy and boot cost.** The biggest lever. `lore-context.md`'s "Operating Disciplines" section held ~3k tokens of rule bodies that also live in topics. Four new area hubs (`gates-and-review-discipline`, `executable-prose-and-design-checks`, `git-and-state-safety`, `user-feedback-working-style`) received that text **verbatim** and ~85 flat root topics were re-parented under them (lifecycle-harness topics under `lifecycle-testing-harness`, now an area). `lore-context.md` keeps a one-line summary and hub pointer per theme. Five legacy feedback topics were converted in the same run. *Metric effect:* lore-context −2.6k tokens, boot map −4.0k (a 122-child root flattens into a hierarchy), **boot footprint −6.6k tokens (−22%)**, root children 139 → 57.

**Run 4 — correctness repair.** No structural gain by design: stale `workspace-status` / `workspace-status.md` references in `workspace-auto-refresh-design.md` annotated with their v45 successors, two history links repointed. The run mostly confirmed that nine other unreviewed topics carried no stale markers. *Metric effect:* none visible — this is the class of work the structural metrics cannot see, which is itself a finding.

**Run 5 — legacy → v1 conversion, second batch.** The 30 smallest remaining legacy topics (in two halves of 15) were read in full, converted, and parented under the cursor/codex/gates/git/executable-prose hubs where the fit was clear. One stale statement fixed (`workspace-meta-repo-pattern`: "not yet scaffolded"). *Metric effect:* +30 mapped files, mapped files 55.4 → 60.2% at the end; the boot map grew back ~1k tokens as more routable nodes were added.

## Findings about the grooming procedure itself

1. **The default workset stops being useful after one run in an uncommitted tree.** `lore-workset` ranks "recently changed" (any uncommitted file) first, and grooming never commits. By Run 3 the rotation tier (the part that reaches unreviewed Lore) was down to 8 files, and by Run 4 the recent tier alone exceeded the 90,000 budget and rotation returned zero. Consecutive default runs therefore re-review their own previous output. **Suggested fix:** exclude from the recent tier any file whose current SHA is already recorded in `lore-grooming-state.yaml`, or let a run commit to a throwaway ref.
2. **Deviations I made, openly:** I raised the budget to 60,000–90,000 for the unscoped selections (the doc says not to raise it *silently*), and for Runs 2, 4 and 5 chose slices by hand (smallest legacy files, unreviewed root topics) after the tool could not offer them. Run 1 followed the tool's `oversized_topic` pick. No file outside the declared write set was edited except exact link repairs.
3. **A hub is where "excessive detail in `lore-context.md`" should go** — demoting to a hub cost nothing in knowledge and returned the largest boot-cost reduction of any single change.
4. **Total corpus tokens rise slightly** because hubs add member lists and routing text. Token reduction is a boot-cost story here, not a corpus-size story; deleting prose (slop) was rare because the topics were already dense.
5. **Suggested extra metrics for the tooling:** `reviewed_since_last_run`, `stale_references_fixed`, count of topics > 5K tokens (stayed at 5), and average depth of mapped nodes.

## Not done (deliberately deferred)

- `parallel-reviewer-fanout-pattern.md` (9k) and `lifecycle-testing-harness.md` (8.6k): both should be split, but ~14 and ~6 existing `§ Section` citations from other topics (`§ Cost`, `§ Lens choice`, `§ Graceful degradation`…) would have to be repaired in the same change. They were removed from the grooming cursor so the next run reviews them.
- Per-version citations across ~35 topics still say `versioning-release-types.md` for a specific version entry; the hub's routing text resolves them, but they could point at the exact history child.
- `role.md` still says to backfill history "in `versioning-release-types.md`"; it should name `versioning-history-v37-v47.md` (outside the Lore write set).
- 125 legacy files remain (about 176k tokens unmapped); at ~15 files per half-run, roughly eight more runs of Run 5's kind would finish the conversion.
