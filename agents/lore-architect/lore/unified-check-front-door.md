---
lore: 1
type: topic
summary: "Unreleased v45 unified health check: mechanical versus semantic ownership, network and freshness boundaries, and continuation evidence."
parent: lore-context.md
---

# Unified Check Front Door — v45 Candidate

The v45 candidate makes `/lr:check` the health front door across plugin, repo, and workspace layers. It removes the doctor and workspace-status skills while retaining the manual repair documents under `fix-*.md` names. This is **unreleased**: v44 remains the shipped version. The implementation is isolated on framework branch `v45-boot-announcements` and paired dev branch `codex/v45-check-tests`.

## Ownership and side effects

Mechanical checks own exact counts, structural validation, and exact normalized shortcut-name matching. AI owns context-summary meaning review and interpretation of intentional aliases. `--full` requests that semantic review; default mechanical validation always runs. A read-only scan on this development workspace took about 10 seconds; this is an environment-specific measurement, not a performance guarantee.

The scan performs no silent repairs or repo fetches. Its only network probe is a bounded upstream release-tag query, skippable with `--no-network`. Reuse canonical generators and engine bootstrap templates; validate edge cases such as empty retired wrapper directories, not only ordinary generated files. An absent optional context on a new agent is informational, matching supported boot.

## Repo freshness is pull evidence

Freshness means the last recorded successful framework pull, not commit age or behind count. More than 24 hours is stale. Absent, corrupt, nonfinite, or future timestamps mean unknown. The `lr-last-pull` marker belongs to each checkout's Git directory; successful clones and no-change pulls count, while failed or skipped pulls preserve the old evidence. Manual Git operations may leave it unchanged. This diagnostic must not be mistaken for proof of remote synchronization.

## Continuation and release boundary

[Implementation record](../workdir/v45-check-implementation.md) and [approved design](../workdir/draft-lr-check-front-door.md) retain detailed scope and evidence. No new repo migration is needed: generated workspace command lists converge through workspace-init, separately from repo stamping. Keep release preparation, development-branch preservation, and shipping distinct.

The user chose careful implementation review in place of lifecycle and quality suites. The earlier 336 deterministic tests describe an earlier artifact state; later 28 unified-check and 8 shortcut-contract tests, plus two final focused cases, cover review fixes. Do not sum them into a fresh whole-tree certification. Lifecycle, quality evaluation, and implementation TriLens remain unrun; design review is not implementation review. Follow the record for exact state and scope before resuming.

[Consistency checks](consistency-checks.md) preserves the old catalog and rationale. [The backlog](framework-improvements-backlog.md) holds the explicitly postponed shared-skills and manual-Diagnosis decisions.
