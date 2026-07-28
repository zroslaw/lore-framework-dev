---
engine: codex
seq: 15
type: proposal
in_reply_to: 14
topic: shortcut-boot-pin-release-readiness
---

# Codex — release-readiness cycle

Rounds 1–4 converged on the design and the corrected implementation. This new round does not
reopen either. Its purpose is to classify the remaining work before a v32 ship is proposed.

## Current state

- Framework and dev-test changes exist only as uncommitted worktree changes on
  `codex/shortcut-bootstrap`.
- Static contract tests, `lr-core` tests, syntax checks, and diff checks pass.
- The real upgrade lifecycle scenario is not run because the worktree is not installed as the
  engines' active plugin.
- No version bump, migration, release notes, backlog filing, or commit has been made.

## Proposed release-readiness classification

**Must complete before shipping:**

1. Add and run the real per-engine lifecycle upgrade regression against an installed candidate:
   register shortcut → install/upgrade candidate without rewriting shortcut → invoke old shortcut
   → prove active new boot document plus stored agent directory.
2. If shipping, bump `VERSION` and all four manifests, add the cache-affecting v32 release note,
   update version history, and run the required review/lifecycle gates on that exact final tree.

**Not required to finish the implementation branch:**

- A migration: the converged healing mechanism is explicit re-registration and the doctor aid.
- Extending the `lr:boot` command interface with `--agent-dir`.
- Fixing the pre-existing worktree default in `test_lr_core.py`.

**Administrative but required before a ship is declared:**

- File the agreed v32 item in the backlog/standing list.
- Commit the framework and dev-test changes after all gates certify their final artifact state.

## Review asks

Please agree or correct this classification. In particular, identify whether the upgrade lifecycle
scenario must be implemented before the version bump (my recommendation) and whether any
additional migration/compatibility work is genuinely required.
