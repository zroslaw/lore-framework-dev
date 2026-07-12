# v25 Implementation Review — Lessons (2026-07-10)

Three in-session lore-architect review rounds on the v25 implementation converged after doc-only
fixes — no script changes after round 1.

## Round 1 (SHOULD-FIX)

- **Stale-skill routing:** `INSTALL-CURSOR.md` must not point stale-content symptoms at
  `doctor-cursor-session-without-plugin` (atomic root cause: plugin never loaded). Route stale →
  refresh + new session; Claude → `doctor-stale-plugin-cache`.
- **Canonical-copy discipline:** mid-session fallback procedure lives **only** in
  `docs/engines/cursor.md`; INSTALL/README pointer-only.
- **Binding consistency:** `cursor.md` invocation-syntax row must not suggest `docs/<skill>.md`
  guesswork — contradicts § Mid-session fallback name mapping (`lr-merge` → `process-merge.md`).

## Round 2 (SHOULD-FIX)

- **Release-notes order:** `conventions.md` expects Summary → Clear Plugin Cache → What's New (v25
  draft had cache-first).
- **Section placement:** stale-content remediation belongs under Refresh, not Mid-session fallback.

## Round 3

**APPROVE** — zero blocking, zero should-fix.

## Operational takeaway

Implementation review on operator/docs ships benefits from the same multi-round convergence
discipline as design review — especially cross-doc routing (doctor ailments, canonical vs pointer
copies, release-note section order).

## See Also

- `v25-cursor-ops-parity-design.md`
- `parallel-reviewer-fanout-pattern.md`
- `single-canonical-source-discipline.md`
- `ailment-catalog-pattern.md`
