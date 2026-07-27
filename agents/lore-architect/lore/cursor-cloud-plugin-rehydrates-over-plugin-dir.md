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

## Operational fix that worked

1. Move aside `~/.cursor/plugins/cache/zroslaw-lore-framework` and
   `~/.cursor/plugins/marketplaces/github.com/zroslaw`.
2. Strip the `lr` entry from `~/.cursor/plugins/cache/.cloud-plugin-manifest.json`.
3. Keep `~/.cursor/plugins/local/lore-framework` → worktree (optional but useful).
4. Re-run with `LR_FRAMEWORK_DIR=<worktree>`; A7 identity should then report the worktree
   VERSION/root.

Backup path used: `~/.cursor/plugins-backup-v31-*`. Restore when finished testing a parked
branch so normal IDE/cloud plugin use returns.

## Relation to A7

`lifecycle-harness-plugin-identity-unverified.md`'s probe is what *detects* this; this topic
is the Cursor-specific *remediation*. Do not treat "repoint local symlink" alone as a
complete Cursor prep step for a non-main `LR_FRAMEWORK_DIR`.

## See Also

- `lifecycle-harness-plugin-identity-unverified.md` — harness gate.
- `v31-lr-core-parked-2026-07-25.md` / `v31-lifecycle-rerun-partial-green-2026-07-27.md` —
  the run that required this.
- `cursor-plugin-distribution-update-model.md` — broader Cursor update/propagation model.
