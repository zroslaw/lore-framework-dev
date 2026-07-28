# The `docs/engines/` Engine-Profile Convention — Shipped in v19, Extended in v20

The multi-engine port's adapter layer is **shipped in canonical `lore-framework` as v19** (commit
`72b1b2a`) — folded in from the `lore-framework-codex` sibling build where it was first built and
validated (see `codex-port-validated-end-to-end.md`, `landing-via-working-tree-diff.md`). It is the
concrete realization of the "`docs/engines/` adapter" lever named in
`multi-engine-portability-direction.md` § Architectural levers.

## Shape

- One profile per engine: canonical v20 ships `docs/engines/claude.md` (reference),
  `docs/engines/codex.md`, and `docs/engines/cursor.md`. Every profile fills the **same five
  bindings** — framework-root, invocation-syntax, subagent-spawn, memory-file, runtime-bounding —
  plus capability gates. Only the values differ.
- **Boot Step-0** (new, top of `agent-boot.md`): (1) resolve `<framework-root>` by self-location
  (the dir containing `VERSION`); (2) infer the engine — strongest signal first: non-empty
  `${CLAUDE_PLUGIN_ROOT}` → claude; else `~/.codex/` present or root under it → codex; else
  default claude — then read `docs/engines/<engine>.md` and keep its values as standing session
  context. **Profile wins on conflict** with any later step.
- **Shared procedure docs stay engine-agnostic.** They describe the Claude mechanism; each spawn
  site (merge/recall/lore-search/consult) carries a one-line "Engine note" pointing at the
  profile's subagent-spawn override. Low churn, and the override wins at execution time.

## Cursor binding values (`docs/engines/cursor.md`)

The third profile is now **shipped in canonical `lore-framework` as v20** (commit `5cbb967`,
manifests `1.20.0`). The local sibling build proved the shape before landing:

- **framework-root:** self-location, `${CLAUDE_PLUGIN_ROOT}` empty
- **invocation-syntax:** slash skills work under `cursor-agent --plugin-dir`
- **subagent-spawn:** conservative **serial host-side** override for v1, rather than claiming an
  unverified native Cursor subagent mechanism — **corrected in v30** to a serial *default* plus a
  semantics-class carve-out using Cursor's native `Task`; see § v30 profile corrections below
- **memory-file:** `AGENTS.md`
- **runtime-bounding:** rely on Cursor job controls / approvals, not a Claude-style Bash timeout

That profile, plus targeted doc updates, was enough for the full currently-implemented lifecycle
catalog to pass on the real local Cursor installation (`19/19`). The important design lesson is
that the `docs/engines/` convention is broad enough to host a **conservative serial profile** as
well as a native-fan-out one — "engine profile" does not imply parallel subagents.

## Codex binding values (`docs/engines/codex.md`)

- **framework-root:** `${CLAUDE_PLUGIN_ROOT}` is empty → self-locate; inline the resolved absolute
  path into subagent briefs.
- **invocation-syntax:** skills invoked by **reading `docs/<skill>.md` directly** when
  agent-initiated (the slash form falls through to shell — see `codex-cli-plugin-loading-findings.md`).
- **subagent-spawn:** native `spawn_agent` (`worker` = write, `explorer` = read-only), **in-session
  model action, not a shell command** (see `codex-native-multi-agent-subsystem.md`). For
  host-reads-steps procedures like merge, the **host reads the procedure doc and passes the steps
  inline** to the spawned worker (the worker does not re-read the doc) — validated as designed.
- **memory-file:** `AGENTS.md` (not `CLAUDE.md`).
- **runtime-bounding:** sandbox; no Bash-tool timeout parameter.
- **Capability gate:** the boot-time `ps -o args= -p $PPID` teammate probe is sandbox-blocked
  (`operation not permitted`) → degrade to host-session assumption. `.git/`-writes are also
  sandbox-blocked (see `codex-git-sandbox-blocks-dotgit.md`).
- **Finalization contract:** the supported path requires `.git` writable through Codex
  launch/configuration. The default sandbox may let reflect/merge land before commit is blocked;
  that is a degraded fallback, not a merge failure or the intended handoff.
- **Per-agent shortcut shape:** personal skills under
  `~/.codex/skills/lr-<agent-name>-agent/SKILL.md`, invoked as `$lr-<agent-name>-agent`. The
  register/unregister/list implementation remains unvalidated until lifecycle-tested; see
  `slash-command-system.md`.

## Where it lives

Canonical `lore-framework/docs/engines/{claude,codex}.md` shipped in v19; `cursor.md` joined them
in v20. The Codex profile was first built in the `lore-framework-codex` sibling build (no git
remote) — now **superseded and deletable**, its work folded into canonical v19. The Cursor
profile followed the same pattern: first validated in `lore-framework-cursor/`, now **superseded
and deletable** after the v20 landing. Design record: workdir `codex-binding-design.md`. Still
deferred (carry `${CLAUDE_PLUGIN_ROOT}`, out of core scope): `.mcp.json` / lr-wait,
`migrations/*`, `df`/`aiqa` — see `port-landing-next-steps.md` § Remaining follow-ups.

## v30 profile corrections — the `subagent-spawn` binding on Cursor and Claude

Both corrections came out of shipping `/lr:trilens-loop` (`trilens-loop-feature.md`), and both are
about the same binding.

**Cursor — carve-outs, not a blanket rule.** The v20 binding's conservative "execute host-side,
serially" clause was epistemic caution rather than a discovered limitation, and it had gone stale:
Cursor shipped subagents in **2.4** (2026-01-22; editor, CLI and Cloud Agents), dispatched via a `Task`
tool, with async subagents and the nesting rule following in 2.5. The corrected binding uses `Task` for
**merge** and for procedures where **subagent independence is the semantics** (`trilens-loop.md`), and
keeps serial host-side execution as the validated default for recall, consult, attach version-reconcile,
and conflict resolution until those get their own deliberate upgrade. Merge moved to `Task` on
2026-07-28 once free-text brief shape was validated in-session (`cursor-task-free-text-brief-validated.md`,
`cursor-merge-via-task.md`). See `subagent-as-optimization-vs-subagent-as-semantics.md` — merge is
optimization-class (serialization was lossless but slower); trilens is semantics-class (serialization
destroys the feature).

**§ Native subagents** separates *what Cursor documents* from *what this framework has validated*.
Free-text briefs are validated (2026-07-28); throwaway `.cursor/agents/` definitions are obsolete for
merge and trilens briefs. That separation remains the convention-level lesson — a profile may host a
documented capability before every procedure using it is end-to-end proven; say which is which, and
trust tool-call evidence over model self-report when upgrading.

**Claude — the two traps.** `docs/engines/claude.md`'s `subagent-spawn` binding now names all three
subagent types (`general-purpose`, `Explore`, `fork`) and their two traps: `fork` **inherits the
caller's full conversation context** (unusable wherever independence is required), and passing a
**`name`** makes the call an Agent-Teams teammate, which **does not auto-return its report to the
caller**. Both were previously undocumented in the profile and both are easy to hit.

## Engine traps belong in the binding, not only in agent lore

The Claude correction above exists because of a live failure worth generalizing.

`parallel-reviewer-fanout-pattern.md` had recorded the named-teammate non-return trap since **v18**. I
hit it anyway, live, while dogfooding `/lr:trilens-loop`: three reviewers spawned with `name`s, all
three went idle without reporting, round re-run unnamed. The knowledge failed to protect me because it
lived in **agent lore** — recallable, but only if you think to recall it — instead of in the binding an
executor reads *at the moment of spawning*. It was one lookup away from the exact instruction that
would have avoided it. A reviewer lens independently flagged the same gap from the other side: the
warning in `trilens-loop.md` had no basis in the profile it pointed at.

**Rule: a fact about how an engine's mechanism misbehaves belongs in that engine's profile binding.**
Agent lore is for judgement and history; the profile is the point-of-use contract. The test is
mechanical — *if the fact would change what an executor types, it goes in the profile.*

Two corollaries for procedure docs:

- **Don't restate the mechanism** (`single-canonical-source-discipline.md`) — but *do* tell the
  executor to **read the whole binding before spawning**.
- **State the outcome requirement in engine-neutral terms** — e.g. "the report must actually come back
  to you" — so a trap in *any* engine is caught by the requirement rather than by an engine-specific
  warning that only covers the engine you happened to think about.

This composes with § Cross-profile guardrail audits below: having written a trap into one binding, check
the sibling bindings for the same class of trap.

**Generalized past engine profiles:** the binding is one kind of point-of-use site; so are the script
that performs the operation, the exact command spelled out in a doc, and a regression test. The same
failure recurred on 2026-07-28 with non-engine traps (GNU `timeout` on macOS, `git -C` off a repo
toplevel) — both recorded in lore I wrote myself, both hit anyway. See
`point-of-use-guardrails-beat-recorded-lore.md`.

## Cross-profile guardrail audits

When one engine profile documents a named guardrail against a class of error, check every sibling profile for the same latent bug rather than assuming the guardrail was only ever needed once. Since all three profiles share the same five bindings by design, a fix in one binding's handling on one profile is a strong signal to audit the same binding on the others. Concrete instance: `docs/engines/cursor.md` had long guarded against guessing `docs/<skill>.md` from a skill name (skill-name and doc-filename diverge, e.g. `boot` → `agent-boot.md`), but `docs/engines/codex.md`'s invocation-syntax binding had the identical latent bug, undetected until an AI-installer review pass traced it against real files on disk. See `skill-doc-filename-divergence-bug-class.md`.

## See Also

- `multi-engine-portability-direction.md` — the anchor; § Architectural levers names the five bindings.
- `codex-port-validated-end-to-end.md` — this convention exercised end-to-end on real Codex.
- `cursor-port-validated-end-to-end.md` — the validated local Cursor build on the same convention.
- `codex-native-multi-agent-subsystem.md` — the subagent-spawn binding's underlying mechanism.
- `codex-git-sandbox-blocks-dotgit.md` — the `.git`-write capability gate.
- `framework-root-self-location-validated.md` — the framework-root binding, validated separately.
- `claude-coupling-inventory-and-port-tiers.md` — the five bindings as the whole port surface.
- `port-landing-next-steps.md` — the landing record and remaining Claude-first follow-ups.
- `skill-doc-filename-divergence-bug-class.md` — the concrete cross-profile guardrail bug, caught by an AI-installer review pass.
- `subagent-as-optimization-vs-subagent-as-semantics.md` — the principle behind the v30 Cursor carve-out; classifies a procedure before an engine is allowed to degrade it.
- `trilens-loop-feature.md` — the v30 feature that forced both profile corrections.
- `parallel-reviewer-fanout-pattern.md` — where the named-teammate trap used to live alone.
- `claude-engine-capabilities.md`, `cursor-engine-capabilities.md` — the per-engine hubs these bindings feed.
