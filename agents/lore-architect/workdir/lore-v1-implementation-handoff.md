# Lore v1 Implementation Handoff

Status: **shipped**. v36 was released 2026-08-09 as framework commit `e5e097b` on `main`,
tag `lr--v1.36.0`, pushed. Three doc-only fixes from a final independent architect review were
amended onto the earlier candidate `1cda4cd`; the deterministic suite was re-run green against the
final tree. Real-engine lifecycle tests were explicitly waived by the user at ship time (recorded
in `versioning-release-types.md`).

## Working Trees

- Framework: `/Users/yaroslav/Documents/agent-workspace/.worktrees/lore-framework/lore-v1-implementation`
  - branch: `codex/lore-v1-implementation`
  - base commit: `9d4c3b9`
  - local v36 candidate: `1cda4cd` (`Release v36 Lore structure and grooming`)
- Development tests: `/Users/yaroslav/Documents/agent-workspace/.worktrees/lore-framework-dev/lore-v1-implementation`
  - branch: `codex/lore-v1-implementation`
  - base commit: `5fc9cef`

The top-level production checkouts were not used for implementation. Existing unrelated changes
there remain untouched.

## Delivered

- Lore v1 frontmatter with `context`, recursive `area`, and leaf `topic` nodes.
- Recursive discovery, taxonomy validation, coverage accounting, formal links, conservative
  references, Git dates/status, token estimates, and exact source hashes.
- Compact `lore-map --view boot` and complete/scoped `--view detailed` YAML maps.
- Deterministic `lore-workset` selection with a 30,000-token default budget, read-only halo,
  snapshots, rotation cursor, and future-version protection.
- Boot, search, merge, check, agent-creation, migration, grooming, and release integration.
- One standard three-line boot report with ceiling-rounded Lore and footprint statistics, plus an
  attach report showing each guest's added role, Lore context, and map footprint.
- Best-effort publication after explicit or boot-time framework updates: narrow update-owned commit,
  existing-upstream push, safe retry, and visible partial outcomes.
- A modest `lr-core` split: the stable 28-line `scripts/lr-core` entry point delegates to focused
  modules under `scripts/lr_core/`. The fallback-bearing preflight and scan modules stay below
  roughly 10K estimated tokens each, so a failed command no longer forces an agent to load the
  entire ~31K-token implementation.
- `/lr:groom`, including iterative and approval-gated Whole-Lore modes.
- Framework version 36 and plugin manifest version `1.36.0`.
- Deterministic coverage and lifecycle scenarios in the development repo. The lifecycle scenarios
  remain unexecuted for this local candidate by explicit user direction.

## Third-Party Review Fixes Applied

- Detailed mapped nodes now expose conservative `legacy_references`, so inline filename mentions
  cannot disappear from rename/merge/delete safety scans.
- Invalid UTF-8 no longer disables maps. Coverage emits no per-file corruption list, only
  `coverage.uncovered.invalid_utf8`; affected files never enter a workset or halo. Structural path
  changes and Whole-Lore mode stop while the count is nonzero.
- Malformed summaries now produce one `invalid_summary` finding.
- Harmless trailing spaces after frontmatter scalars are accepted.
- Detailed mapped and uncovered records expose `uncommitted`; grooming rechecks Git cleanliness
  before applying destructive changes.

## TriLens Release Review

Three independent lenses reviewed the full candidate for three rounds. All reported findings were
applied, including:

- dirty-target no-clobber and a fresh exact-commit/sole-ahead gate for framework-update pushes;
- actual Codex `spawn_agent` schema, engine propagation for attach, and a direct-tool-evidence
  Codex boot override for worktrees;
- corrected boot/attach branching, compact-map coverage wording, and the legacy 50K context check;
- normal Markdown links with optional titles in the formal graph parser;
- removal of false attach upgrade claims after a deferred or failed reconcile.

Round three found two medium issues; both were fixed and covered deterministically. The procedure's
three-round cap prevented a fourth cold-review attestation, so the honest status is “all known
findings applied,” not “a final reviewer returned clean.” The requested lifecycle-test expansion
was declined for this preparation because lifecycle work was explicitly excluded.

## Suggested Review Order

1. `docs/lore-structure.md` — data model and compatibility contract.
2. `scripts/lr-core` and `scripts/lr_core/` — verify the stable wrapper, then review
   `preflight.py`, `scan.py`, `lore_graph.py`, `lore_map.py`, and `lore_workset.py` by
   responsibility.
3. `docs/groom.md` and `skills/groom/SKILL.md` — semantic and destructive-change procedure.
4. `docs/agent-boot.md`, `docs/lore-search.md`, and `docs/process-merge.md` — lifecycle adoption.
5. `tests/test_lr_core_lore_v1.py` and `tests/lifecycle/test_lore_v1.py` — executable contracts.
6. `migrations/36.md` and `release-notes/36.md` — no-write adoption and ship claims.

## Verification Evidence

- Explicit non-real-engine development suite: 315/315 passed; no module below `tests/lifecycle/`
  was invoked.
- `tests.test_lr_core` plus `tests.test_lr_core_lore_v1`: 109/109 passed.
- Focused Lore v1 module: 46/46 passed.
- Framework scripts and development tests compile; all five shell scripts pass `bash -n`.
- Cursor wrappers are synchronized; manifests are valid JSON at `1.36.0`; version/migration and
  declared-write-path checks pass; both worktrees pass `git diff --check`.
- Real Lore Architect corpus: 220 files, 282,342 estimated tokens, no invalid UTF-8.
- Compact boot map: 857 bytes, 215 estimated tokens; context estimate 10,798 tokens; role estimate
  3,685 tokens; system-prompt estimate 7,525 tokens; total boot footprint estimate 22,223 tokens
  for Codex.
- Workset: 29,946 / 30,000 estimated tokens.
- Boot, detailed, and workset YAML parse successfully.
- Five Cursor `composer-2.5` Lore v1 lifecycle scenarios passed before the review fixes.
- Canonical regular quality matrix `matrix-20260809T045314Z-regular`: usable `partial` result;
  Claude/Haiku +50.0-point behavior uplift (36/36 scored), Cursor/Composer 2.5 +66.7 (36/36),
  Codex/gpt-5.4-mini +66.3 (35/36). Codex timed out only on
  `P10-parametric-gotcha/treatment`; there were no judge failures. Durable artifacts are under
  `tests/quality/results/matrix-20260809T045314Z-regular/` and the generated block is in
  `release-notes/36.md`.
- Candidate-identity limitation: the matrix ran against the frozen v36 worktrees before the local
  candidate commits were created, but `summary.json` records only their base `HEAD` values
  (`9d4c3b9` / `5fc9cef`). Those SHA fields do not identify the tested dirty state. The runtime
  files were frozen for the canonical run; the final candidate commits are recorded above. Future
  harness output should add dirty status, a diff fingerprint, and changed paths.

## Remaining Release Gate

Real-engine lifecycle was the only intentionally omitted release-gate layer; the user explicitly
waived it at ship time (2026-08-09), so this gate is closed by waiver, not by execution. The earlier Cursor run used
`LR_SKIP_PLUGIN_IDENTITY=1`, so it remains historical smoke evidence only. The one quality timeout
can be rerun with the exact command in `release-notes/36.md`; the quality policy permits a useful
partial result when technical failures are explicit. No real Lore Architect topics were migrated
or groomed; v36 adoption intentionally performs no bulk rewrite.
