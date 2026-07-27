# v31 Lifecycle Re-run After A7 — Partial Green (2026-07-27)

First **valid** Codex/Cursor lifecycle against `lore-framework` `wip/lr-core-v31` @ `cd8ece1`,
after the A7 plugin-identity gate landed on `lore-framework-dev` main and engines were
repointed (Codex marketplace → worktree; Cursor cloud plugin disabled — see
`cursor-cloud-plugin-rehydrates-over-plugin-dir.md`).

Identity passed on both engines before modules ran.

| Engine | Modules | Result dir |
|---|---|---|
| Codex | **6/7** | `tests/lifecycle/results/20260727T140740Z-standard/` |
| Cursor | **4/7** | `tests/lifecycle/results/20260727T140949Z-standard/` |

Passed on both: consult/attach, finalize, recall, trilens. Codex also: repo_workspace, takeover.

## Failures to triage before ship

**Codex `test_boot` (2 scenarios):**
- `test_07` R>F — printed `version skew: repo=32 framework=31 (repo-ahead)` instead of the
  expected “your Codex plugin is older than the repo” remedy string (lr-core / version-check
  wording drift vs harness assertion).
- `test_08` Script Fallback — booted OK but did not name `lr-core` / `preflight` in the reply.

**Cursor:**
- `test_05` — did not stamp `lore-repo.md` 30→31.
- `test_08` — same Script Fallback notify gap; reply also claimed framework **30**.
- `test_21` update dry-run — reported `Framework version: 30` (not 31).
- `test_takeover` — per-module identity probe timed out at 420s (each module subprocess
  re-runs `verify_plugin_identity` on first `run_engine`).

Ship gate remains open until Script Fallback notify fidelity, Codex R>F assertion/doc
alignment, and Cursor mid-suite “sees 30” drift are fixed or explicitly waived.

## See Also

- `v31-lr-core-parked-2026-07-25.md` — parking + earlier invalid Codex/Cursor run.
- `lifecycle-harness-plugin-identity-unverified.md` — A7 gate that made this run valid.
- `cursor-cloud-plugin-rehydrates-over-plugin-dir.md` — Cursor prep required for this run.
