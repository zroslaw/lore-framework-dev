# Codex Sandbox Blocks `.git/` Writes

Operational finding, Codex `workspace-write` sandbox (`codex exec --full-auto`), 2026-07-05. This
is the **sole remaining gap** in the otherwise end-to-end-validated Codex port (see
`codex-port-validated-end-to-end.md`).

Even with the repo inside the writable cwd, Codex **blocks writes under `.git/`**:
`Operation not permitted` on `.git/index.lock`, `.git/FETCH_HEAD`, etc. Consequences for the
framework:

- **auto-pull** (boot) fails its `git pull` — harmless; boot already degrades on pull failure.
- **finalize's commit** and any framework `git commit` / `git pull` cannot run under the default
  sandbox.

Handling (documented in `docs/engines/codex.md` — see `docs-engines-convention.md`): to allow git,
run Codex with `.git` writable (`--sandbox danger-full-access` for a trusted local run, or add
`.git` to `sandbox_workspace_write.writable_roots`); otherwise leave the merged changes
**uncommitted for the user to commit by hand**, and report it as a sandbox gate — **not** a merge
failure. Merge work completes on disk regardless.

Open question for the port: whether interactive Codex (with approvals) lets git through more
gracefully than headless `--full-auto`. Untested.

## See Also

- `codex-port-validated-end-to-end.md` — where this is the one gap in an otherwise-passing run.
- `docs-engines-convention.md` — the codex profile that documents the sandbox gate + handling.
- `multi-engine-portability-direction.md` — the anchor direction.
