# Port Landing — Landed in v19 (retrospective + remaining follow-ups)

The multi-engine (Codex) port **landed in canonical `lore-framework` as v19** (commit `72b1b2a`,
manifests `1.19.0`, pushed 2026-07-05). The "next dedicated session" landing plan this topic used to
hold is **done**. What follows is the completion record plus the follow-ups that remain
Claude-first. Anchor: `multi-engine-portability-direction.md`.

## What landed in v19

- **`docs/engines/` convention** — Boot Step-0 engine selection + `docs/engines/{claude,codex}.md`
  profiles (five bindings each) + per-spawn-site "Engine note" pointers. Folded from the
  `lore-framework-codex` sibling build into the real plugin via the working-tree-diff technique
  (`landing-via-working-tree-diff.md`). Full shape: `docs-engines-convention.md`.
- **framework-root-full** — `${CLAUDE_PLUGIN_ROOT}` → `<framework-root>` (self-location) across
  `docs/` + all 26 `SKILL.md`. See `framework-root-self-location-validated.md`.
- **defer-clarity fix** — authored fresh at landing (it was staged separately, never in the codex
  build): `version-check.md` three defer points + `agent-boot.md` step 3 ("the version check never
  aborts boot"). A genuine robustness win, orthogonal to the port. See `haiku-ambiguity-detector.md`.
- **Style skills** — `/lr:plain-language`, `/lr:dialogue`, `/lr:follow-me` rode along, as planned
  (deliberately pulled out of v18). See `style-skills.md`.
- `auto-pull.md` timeout prose got a one-line Engine note (runtime-bounding), not a rewrite.

## Validation on the shipping artifact

Boot lifecycle suite ran **6/6 on haiku against the real v19 tree** (`LR_LIFECYCLE=1
LR_TEST_MODEL=haiku LR_FRAMEWORK_DIR=<real>`, ~$0.75). test_06 (dirty-tree upgrade gate) — the exact
scenario that originally surfaced the defer-clarity ambiguity — now defers cleanly WITHOUT emitting a
boot-failure sentinel, closing the loop `haiku-ambiguity-detector.md` opened. The Codex path was
proven end-to-end on real `codex exec` earlier the same session (`codex-port-validated-end-to-end.md`).

## The `lore-framework-codex` sibling is now superseded

The no-remote sibling build was the staging ground; its port changes are now in canonical
`lore-framework` v19. The sibling is **deletable** — nothing unique lives there (design record is in
workdir `codex-binding-design.md`).

## Remaining follow-ups (still Claude-first / open)

These are deliberate deferred scope documented in `release-notes/19.md`, not regressions:

1. **`lr-wait` MCP** — `.mcp.json` still uses `${CLAUDE_PLUGIN_ROOT}`; port it to a Codex-aware
   registration when the MCP-on-Codex path is exercised.
2. **DF/AIQA module** and **`migrations/*`** — still Claude-targeted; carry `${CLAUDE_PLUGIN_ROOT}`.
3. **Wire a `codex` driver into `harness.py`'s `run_engine()`** (incl. the one-time
   marketplace/plugin-install setup and the rollout-log-based spawn assertions) so the Codex path is
   in the *automated* suite, not just manual — see `codex-testing-methodology.md`,
   `codex-cli-plugin-loading-findings.md`. Local-install update procedure: `codex-local-plugin-update.md`.
4. **Decide the `.git`-sandbox commit handling** for Codex finalize (run with `.git` writable, or
   document the uncommitted-hand-off gate) — see `codex-git-sandbox-blocks-dotgit.md`.
5. **Cursor** — `--plugin-dir` parity confirmed but quota-blocked, unvalidated end-to-end. See
   `cursor-agent-cli-probe-findings.md`.

## Artifacts produced during the port (in workdir)

- `workdir/first-steps-codex.md` (verified) / `workdir/first-steps-cursor.md` (should-work,
  unconfirmed) — manual trial guides per engine.
- `workdir/claude-specific-inventory.md` — the full coupling inventory behind
  `claude-coupling-inventory-and-port-tiers.md`.
- `workdir/codex-binding-design.md` — the engine-profile design record.

## See Also

- `multi-engine-portability-direction.md` — the anchor direction, now marked shipped.
- `docs-engines-convention.md` — the engine-profile layer, folded into canonical v19.
- `codex-port-validated-end-to-end.md` — the end-to-end Codex validation.
- `landing-via-working-tree-diff.md` — the technique that folded the sibling build in.
- `framework-root-self-location-validated.md`, `haiku-ambiguity-detector.md` — the two Claude-side
  change sets, now applied.
- `codex-git-sandbox-blocks-dotgit.md`, `codex-testing-methodology.md` — the remaining open items.
- `claude-coupling-inventory-and-port-tiers.md` — the tiered work map the landing executed.
