Before implementing workspace v25 slice: run **three-lens parallel review** — (1) framework
architecture & lore consistency, (2) operational UX & team adoption, (3) implementation safety &
harness coverage. Iterate drafts until all lenses approve.

Round 1 typically surfaces: step-order bugs, gitignore scope gaps, dirty-tree guards, cross-ref
sweeps. Keep UX review artifacts in `workdir/` when produced.

**Subagent model:** user preference Composer 2.5 (regular, not fast) for review subagents — not
Sonnet 4.6 High (`feedback-composer-25-subagent-reviews.md`).

## See Also

- `parallel-reviewer-fanout-pattern.md`
- `v25-workspace-pull-init-design.md`
