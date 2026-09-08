# v45 unified check — implementation record

2026-09-08. Framework branch: `v45-boot-announcements` (base `e8e82d3`).
Tests/dev branch: `codex/v45-check-tests` (base `642900b`). The framework candidate was
committed and pushed on its dedicated branch as `3917ca0`; this record still describes an
unpublished release. Release preparation sets VERSION to 45 and all four version-bearing
manifests to 1.45.0.

## Implemented

- `lr-core check`: plugin/repos/workspace state, location hints, scoped scans, structured
  findings and summary counts, explicit coverage and semantic-review status.
- Plugin version and cache inventory, bounded upstream tag check, manifest consistency,
  migration declaration validation, Cursor parity using the existing generator.
- R1–R15 mechanical repo checks, including normalized shortcut-name matching and reuse of
  the canonical engine bootstrap sentence. Both sides of a renamed Lore path remain visible.
- S19 per-repo freshness: more than 24h since a verified successful framework pull, or unknown
  evidence. Reuse `lr-last-pull`; successful boot/workspace pulls and clones write it atomically.
  Failed/skipped pulls do not advance it. Manual Git operations may not update this marker.
- Unified procedure and findings catalog; old doctor/workspace-status skills removed.
  All three manual diagnosis docs retained as `fix-*`. Active references and historical
  repair-document links updated. `.agents/skills` adoption remains out of scope.

## Verification

336 deterministic tests passed:

| Suite | Tests |
|---|---:|
| test_lr_core_check.py | 24 |
| test_shortcut_bootstrap_contract.py | 8 |
| test_lr_core.py | 68 |
| test_workspace_scan.py | 73 |
| test_workspace_refresh.py | 71 |
| test_plugin_config.py | 46 |
| test_lr_core_lore_v1.py | 46 |

Run each from this dev checkout with `LR_FRAMEWORK_DIR` set to the v45 framework checkout.
Python compilation, `bash -n scripts/workspace-pull`, Cursor `sync-cursor-skills --check`,
and `git diff --check` passed. Active Markdown file links resolve; all P1–P7/R1–R15/S1–S19
have catalog entries.

The upstream probe returned published version 44 from the real remote. Read-only dogfooding
on the development workspace completed in about 10 seconds, with three Lore repos. It found
existing problems, including an incomplete agent directory whose Lore cannot be validated;
that is surfaced as incomplete coverage, never a clean scan. No workspace repairs were applied.

## Implementation refinements

- Mechanical Lore validation remains enabled in the default scan. Measured total runtime is
  about 10 seconds on this workspace, rather than hiding reference checks behind `--full`.
  `--full` expands reporting and requests AI summary-accuracy review; finding counts are
  computed for all completed mechanical checks on every default run.
- Unresolved legacy references are informational cautions, separately categorized from definite
  structural errors. Legacy/future-format coverage is visible without pretending every legacy
  topic is corrupt. Invalid UTF-8 is an error.
- An unsafe enclosing Git repo or malformed plugin settings stay visible even without a
  workspace descriptor; only routine missing setup collapses into the initialization suggestion.
- Cursor-without-plugin diagnosis stays in its own retained repair doc linked by the install guide.
- Boot/attach operation notices are included. Release preparation moves the attach upgrade
  notice into the host before dispatch. No local plugins were refreshed and nothing was merged,
  installed, merged to main, tagged, or published.

Real-engine lifecycle: **did not run** (not requested for this implementation).
Implementation TriLens: **did not run** (the earlier design review is not a code review).

## Release consistency preparation — 2026-09-08

- VERSION 45 and all four version-bearing manifests 1.45.0 are aligned.
- `release-notes/45.md` covers both unified check and operation notices, with the required
  cache notice immediately after Summary and explicit upgrade instructions.
- No new repo migration: no agent/Lore format or shortcut-template changes. Existing workspaces
  refresh their generated command list through `workspace-init`, separately from repo stamping.
- Older executable migrations 25 and 44 and active docs now use current finding IDs; migration
  44 verification no longer invokes the removed workspace-status command.
- Static checks passed: active Markdown links, v2–v45 release/migration coverage (v1 is the baseline), manifest
  alignment, cache-notice placement, Cursor wrapper parity, and diff whitespace.
- Plugin-only offline check reported no P4/P6/P7 problems. It reported only an existing local
  Codex v32 temporary marketplace copy (P5); no cache changes were made.

The 336 deterministic tests above predate this metadata/documentation preparation and were
not rerun for this pass. Lifecycle tests, quality evaluations, and implementation TriLens
remain unrun, as requested. Release preparation is complete; release validation and publishing
remain separate work. The framework candidate is committed and pushed only to its dedicated
release branch; it is not tagged, installed, merged, or published.


## Careful implementation review — 2026-09-08

Requested in place of lifecycle and quality evaluation. Reviewed the unified scan, plugin and
repo checks, freshness writer and pull integration, command routing, migration references,
release packaging, and boot/attach operation notices.

Fixed:

- Cursor shortcut targeting the workspace root could index an empty relative path and abort
  the entire scan. It now produces a scope-format finding.
- Wrapper parity missed empty stale directories, non-prefixed orphan directories, and the
  legacy `skills/cursor` tree; it now mirrors the generator's directory checks.
- Missing optional context on a new agent is informational, consistently with supported boot
  behavior. A context path that exists but is not a file remains an error.
- Invalid/unreadable framework VERSION no longer creates invented repo skew. Version comparison
  is explicitly unavailable and scan completeness reflects that.
- Restored the upstream issue reference `openai/codex#18115`, accidentally changed during the
  preceding check-ID replacement. Corrected the fallback classification to identify `check`
  as an implementation with no manual reconstruction.
- Upgrade notice describes the safety check and conditional publication attempt, rather than
  guaranteeing writes/commit/push before checking whether they can proceed.

Verification: 28 unified-check tests passed, plus 8 shortcut-contract tests. The final optional
context and unknown-version refinements passed their two focused regression cases after the
initial 28-test run. Python compilation, shell syntax, diff whitespace, 45 active Markdown
links, release/migration coverage v2–v45, and plugin P4/P6/P7 checks passed. The existing local
P5 cache finding remains untouched. Release notes include this evidence separately from the
historical 336-test result.

No unresolved release blocker found in this review. Real-engine lifecycle tests, quality
suites, and implementation TriLens remain unrun. The candidate commit is unmerged and unpublished.
