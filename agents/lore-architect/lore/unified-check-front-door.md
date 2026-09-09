---
lore: 1
type: topic
summary: "The v45 unified health front door: /lr:check reports plugin, agent repos, and workspace as three layers, replacing doctor and workspace-status — ownership boundaries, freshness semantics, and known open findings."
parent: lore-context.md
---

# Unified Check Front Door

**Shipped in v45** (2026-09-09, tag `lr--v1.45.0`). `/lr:check` is the single health front door
across the plugin, agent-repo, and workspace layers. It **replaced `/lr:doctor` and
`/lr:workspace-status`**, taking the skill count from 33 to 31.

## What the shape is now

- The 24 hand-numbered checks became **script findings under stable prefixes**: `P` (plugin),
  `R` (agent repo), `S` (workspace). Numbers are no longer positional and no longer renumber.
- `docs/workspace-status.md` became the shared **`docs/findings-catalog.md`** — one message/fix
  catalog serving every layer and every caller (boot's `workspace_refresh` findings included).
- The three `doctor-*.md` ailment docs survive as **`docs/fix-*.md`**, reachable from finding rows
  and from the install guides — because a missing or broken command cannot diagnose itself.
- New **S19 per-repo pull freshness**, and new **S10 `stale_command_list`**.

## Ownership and side effects

Mechanical checks own exact counts, structural validation, and exact normalized shortcut-name
matching. AI owns context-summary meaning review and interpretation of intentional aliases.
`--full` requests that semantic review; default mechanical validation always runs. A read-only scan
on this development workspace took about 10 seconds — an environment-specific measurement, not a
performance guarantee.

The scan performs **no silent repairs and no repo fetches**. Its only network probe is a bounded
upstream release-tag query, skippable with `--no-network`. Reuse canonical generators and engine
bootstrap templates; validate edge cases such as empty retired wrapper directories, not only
ordinary generated files. An absent optional context on a new agent is informational, matching
supported boot.

## Repo freshness is pull evidence

Freshness means **the last recorded successful framework pull**, not commit age or behind-count.
More than 24 hours is stale. Absent, corrupt, nonfinite, or future timestamps mean *unknown*. The
`lr-last-pull` marker belongs to each checkout's git directory; successful clones and no-change
pulls count, while failed or skipped pulls preserve the old evidence — so a missing marker reads
*unknown*, never *current*. Manual git operations may leave it unchanged. **This diagnostic must not
be mistaken for proof of remote synchronization.**

## Known open findings, shipped knowingly

Five design findings shipped unfixed and are filed in
[the backlog](framework-improvements-backlog.md) § Framework Upkeep, Distribution & Docs. The three
that belong to `check` itself:

- **The default report drowns in one info category** — 997 repo findings on this workspace, 965 of
  them `R6 reference_cautions`, burying 1 error and 7 warnings.
- **`check` is scanner-first where `doctor` was symptom-first** — a symptom with no mechanical
  finding has no route to the `fix-*.md` docs.
- **Diagnosis lost its literate fallback** — `check` is now filed under *Implementation* ("the
  script is the specification"), so when `lr-core` cannot run there is no hand-executable diagnosis
  path, where v44 had two.

## Verification boundary

The user chose careful implementation review in place of the lifecycle and quality suites. The
shipped tree's number is **345 deterministic tests green across 7 modules**; earlier counts in the
draft record describe earlier artifact states and must not be summed into a fresh whole-tree
certification. Lifecycle, quality evaluation, and implementation TriLens **did not run** — a
[blast-radius audit](blast-radius-audit-when-a-gate-is-waived.md) was performed in their place, and
design review is not implementation review.

## See Also

- [operation-notice-convention.md](operation-notice-convention.md) — the other v45 convention, with
  its own two open findings.
- [consistency-checks.md](consistency-checks.md) — the pre-v45 numbered catalog and its rationale,
  kept for history.
- [findings catalog / implementation record](../workdir/v45-check-implementation.md) and
  [approved design](../workdir/draft-lr-check-front-door.md) — detailed scope and evidence.
- [versioning-release-types.md](versioning-release-types.md) — the v45 ship record.
