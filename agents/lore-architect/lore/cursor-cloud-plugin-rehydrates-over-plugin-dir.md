# Cursor Cloud Plugin Rehydrates Over `--plugin-dir`

For Cursor lifecycle (or any headless `cursor-agent --plugin-dir <checkout>`) against a
**non-main** lore-framework checkout, pointing `~/.cursor/plugins/local/lore-framework` at
the worktree and passing `--plugin-dir` is **not enough**.

## Mechanism

Cursor's user-marketplace install records something like:

- `marketplaceSlug: zroslaw-lore-framework`
- `gitUrl: https://github.com/zroslaw/lore-framework`
- `resolvedCommitSha` pinned to shipped main (e.g. `11ec0df` = v30)

On `cursor-agent` invocation it **rehydrates**
`~/.cursor/plugins/cache/zroslaw-lore-framework/...` from that GitHub commit — overwriting
symlinks or rsync copies of a worktree — and that cache **wins over `--plugin-dir`**.

Confirmed 2026-07-27 while preparing the valid v31 Codex/Cursor lifecycle re-run: after
symlinking the cache dir to `wip/lr-core-v31`, the next identity probe reported VERSION **30**
and a real (non-symlink) cache directory again.

## Rehydration is seconds fast — move-aside alone is NOT enough

The move-aside procedure below was **applied correctly on 2026-07-27 and still lost.** Timestamps
from the machine (local time is UTC+7):

| Local time | Event |
|---|---|
| 21:07:40 | `~/.cursor/plugins` moved to `plugins-backup-v31-20260727210740` |
| 21:07:40 | `cache/.cloud-plugin-manifest.json` rewritten |
| 21:08:03 | `cache/zroslaw-lore-framework/lr/11ec0df…/` re-downloaded (`VERSION` = 30) |
| 21:09:49 | Cursor lifecycle suite starts (`20260727T140949Z`) |

**Rehydration completed 23 seconds after the move and 1m46s before the suite started.** By the
time the first scenario ran, three lore-framework trees existed: the v31 worktree link in `local/`,
plus v30 in both `cache/` and `marketplaces/` at commit `11ec0df` (the v30 release). The entire
Cursor shard of that run is therefore uninterpretable — see
`v31-lifecycle-rerun-partial-green-2026-07-27.md`.

**Operational rule: re-check after the move, not before.** A move-aside is a point-in-time action
against a process that reinstates itself. The check that matters is "is the tree clean *now*, at
the moment the suite starts" — which is why the deterministic source check belongs **in the
harness**, not in a human prep step (`point-of-use-guardrails-beat-recorded-lore.md`). That check
now exists: `check_cursor_plugin_sources()` walks `local/`, `marketplaces/` and `cache/` and
rejects any tree whose `VERSION` differs from `LR_FRAMEWORK_DIR`, filesystem-only, before any
engine call.

**Diagnostic note worth copying:** this was root-caused entirely from filesystem timestamps plus
the stored stderr logs, with **zero engine calls**. Five live `cursor-agent` probes had been
planned and were unnecessary. Read the artifacts first — a stored failure log plus `stat` on the
plugin directories answered a question that was about to be paid for.

## Operational prep (necessary, not sufficient on its own)

1. Move aside `~/.cursor/plugins/cache/zroslaw-lore-framework` and
   `~/.cursor/plugins/marketplaces/github.com/zroslaw`.
2. Strip the `lr` entry from `~/.cursor/plugins/cache/.cloud-plugin-manifest.json`.
3. Keep `~/.cursor/plugins/local/lore-framework` → worktree (optional but useful).
4. Re-run with `LR_FRAMEWORK_DIR=<worktree>`.
5. **Re-check immediately before the suite starts** — rehydration can complete within ~25s of
   step 1. Rely on the harness's deterministic check for the verdict, not on having done steps 1–3.

Backup path used: `~/.cursor/plugins-backup-v31-*`. Restore when finished testing a parked
branch so normal IDE/cloud plugin use returns.

## Relation to A7

`lifecycle-harness-plugin-identity-unverified.md`'s gate is what *detects* this; this topic is the
Cursor-specific *remediation*. Do not treat "repoint local symlink" — or even the full move-aside
— as a complete Cursor prep step for a non-main `LR_FRAMEWORK_DIR`.

The original Cursor arm of A7 could **not** detect it: it was an engine-side prompt asking the
model which plugin root served its skills, which is unanswerable from inside the model. It reported
`PLUGIN-IDENTITY-OK 31 <worktree>` while the suite ran on v30. See
`a-gate-cannot-be-a-model-self-report.md`.

## See Also

- `lifecycle-harness-plugin-identity-unverified.md` — harness gate.
- `a-gate-cannot-be-a-model-self-report.md` — why the first Cursor gate arm passed while wrong.
- `point-of-use-guardrails-beat-recorded-lore.md` — why the check belongs in the harness rather
  than in a remembered prep step.
- `v31-lr-core-parked-2026-07-25.md` / `v31-lifecycle-rerun-partial-green-2026-07-27.md` —
  the run that required this, and the run it invalidated.
- `cursor-plugin-distribution-update-model.md` — broader Cursor update/propagation model.
- `cursor-engine-capabilities.md` — the durable Cursor hub topic.
