# Codex Sandbox Blocks `.git/` Writes

Operational finding, Codex `workspace-write` sandbox (`codex exec --full-auto`), 2026-07-05. This
is a launch/configuration requirement around the otherwise end-to-end-validated Codex port (see
`codex-port-validated-end-to-end.md`), not a behavior the plugin can change itself.

Even with the repo inside the writable cwd, Codex **blocks writes under `.git/`**:
`Operation not permitted` on `.git/index.lock`, `.git/FETCH_HEAD`, etc. Consequences for the
framework:

- **auto-pull** (boot) fails its `git pull` — harmless; boot already degrades on pull failure.
- **finalize's commit** and any framework `git commit` / `git pull` cannot run under the default
  sandbox.

Product decision (documented in `docs/engines/codex.md` — see `docs-engines-convention.md`):
Lore's supported Codex finalization path requires `.git` to be writable. Run a trusted local
session with `--sandbox danger-full-access`, or add the repository's `.git` directory to
`sandbox_workspace_write.writable_roots`. The plugin cannot widen the sandbox, so this permission
must come from Codex launch/configuration.

The default sandbox can still let reflect and merge write lore files before blocking commit.
Treat that state as a degraded fallback, not the intended handoff and not a merge failure. Manual
user commit is recovery from the sandbox gate, not a co-equal supported finalization path.

## See Also

- `codex-port-validated-end-to-end.md` — where this is the one gap in an otherwise-passing run.
- `docs-engines-convention.md` — the codex profile that documents the sandbox gate + handling.
- `multi-engine-portability-direction.md` — the anchor direction.
