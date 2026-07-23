# Testing docs root discoverability

Testing strategy docs need a discoverable chain from the root of
`lore-framework-dev`, not only from deep test directories.

The repo now keeps that chain in two places:

- root `README.md` links to `tests/README.md`, `tests/testing-strategy.md`,
  `tests/quality/strategy.md`, and `tests/quality/reporting.md`
- `lore-repo.md` carries a short documentation pointer list

For external-reader-facing testing docs, maintain this route:

`README.md` -> `tests/README.md` -> strategy/reporting docs -> source files.

A doc that only lives under `tests/quality/` or another deep test directory is
effectively invisible to release reviewers and new contributors unless the root
map points at it.

The root map must preserve track boundaries. Standard lifecycle docs point at
`tests/lifecycle/` and `tests/lifecycle/results/`; Lore Beings lifecycle docs
point at `tests/lifecycle_beings/` and `tests/lifecycle_beings/results/`; quality
benchmark docs point at `tests/quality/` and the generated quality report
artifacts (`summary.md`, `release-notes.md`, `summary.json`). Do not make the
quality glossary decode lifecycle artifacts, and do not document Lore Beings as
a `tests/lifecycle/run_matrix.py --suite keeper` mode.

## See Also

- `lifecycle-testing-harness.md` - main procedural-fidelity test track.
- `quality-benchmark-feature.md` - quality benchmark track under
  `tests/quality/`.
- `plugin-vs-agent-repo-separation.md` - why dev-only tests live in
  `lore-framework-dev`, not the distributed plugin.
- `finalization-process.md` - why test code and root docs need separate manual
  commits outside finalize's `agents/` scope.
