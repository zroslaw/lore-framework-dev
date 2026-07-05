# `/lr:spawn-teammate` — Feature (v10, BETA)

Added in v10. Spawns one or more lore agents as Claude Code Agent Teams teammates. The current session becomes the team lead.

## Implementation files

- `skills/spawn-teammate/SKILL.md` — thin one-line pointer (standard skill pattern)
- `docs/spawn-teammate.md` — multi-step procedure (v15: Step 7 disambiguated, Step 7c verification added, Step 8 surfaces four-state outcome)
- `docs/teammate-conventions.md` — v15: single canonical source for the four standing teammate input-direction RULES, anchored at boot via `agent-boot.md` Step 5
- `release-notes/10.md` — initial release notes (release-notes-only bump, no migration)
- `release-notes/15.md` — v15 fixes: write-aware gate (orthogonal to spawn-teammate), Step 7 disambiguation, Step 7c verification, teammate-conventions anchored at boot
- `VERSION` bumped 9 → 10 (initial); v15 doesn't touch VERSION semantics for spawn-teammate but bundles fixes into VERSION 15
- `README.md` — skills table row with **BETA** marking

## Design decisions

**Spawn prompt format** — always uses `agent-boot.md` directly with absolute agent-dir path. No fallback to `/lr-<name>-agent` shortcut commands (user specified this). Format (post-v10 in-band BETA refinement):
```
Read ${CLAUDE_PLUGIN_ROOT}/docs/agent-boot.md and boot as agent <name> from <abs-path>.

You were spawned primarily as a parallel session for the user to work with you directly. After boot, wait for the user's instructions in this session and respond to them here — not via SendMessage. Use SendMessage to the team lead or other teammates only when the user explicitly asks you to share or coordinate something.
```
`${CLAUDE_PLUGIN_ROOT}` is left literal — the teammate's session resolves it at boot time (teammates load skills from project/user settings per Agent Teams docs).

The post-boot paragraph does two things: it stops the teammate after the boot procedure's "Confirm" step (rather than letting it invent a task), and it frames **the user — in the teammate's own session — as the primary interlocutor**. SendMessage is reserved for explicit user-requested coordination. This is a design **invariant** of spawn-teammate, not a procedural detail.

**Why the reframe** — the v10 initial release used "After boot, await further instructions from the team lead via SendMessage." Real-world usage report: when the user worked directly with a spawned teammate (Shift+Down into its pane in in-process mode, or click into its pane in split-pane mode), the teammate kept defaulting to *reporting progress back to the team lead via SendMessage* instead of responding in its own session. The dominant usage pattern is the inverse — users spawn a teammate to drive it directly from its pane as a parallel session; cross-agent messaging is the exception. The reframe aligns the teammate's default with that dominant pattern. Boot-time stop behavior was preserved unchanged.

**Refinement workflow** — this change was made in-band on the BETA feature: edit `docs/spawn-teammate.md`, leave `release-notes/10.md` historical (it documents the v10 initial release), no `VERSION` bump. The BETA caveat in the release notes ("internal procedure and presentation may evolve based on real-world usage") is the contract that licenses post-release evolution without ceremony. See `versioning-release-types.md` for the general pattern.

**Operational lesson** — for BETA features, the spawn prompt / first-message framing is a high-leverage place to fix default-behavior divergence. A small wording change there reshapes every future session of that feature. When real-usage reports surface unexpected default behavior, look at the prompt before considering procedural changes.

**v15 follow-up — empirical washout of spawn-prompt directives.** The directive paragraph from the post-v10 reframe empirically washed out after a handful of turns: teammates drifted back to lead-as-hub default. Spawn-prompt-only is an insufficient anchor for standing rules. v15 ships the corrective: standing teammate rules now live in a separate doc (`docs/teammate-conventions.md`) loaded at every boot of a spawned teammate via `agent-boot.md` Step 5. The spawn prompt's recap becomes a one-sentence best-effort fallback; if the boot-time load works, all four rules are present as standing context preferred over conflicting later instructions. Detection of spawned-teammate context is `ps -o args= -p $PPID` looking for `--agent-id` (Agent Teams' invocation marker). See `single-canonical-source-discipline.md` for the broader rule that one site carries the body, callers point at it.

## v15 changes (boot/spawn flow)

**Step 7 disambiguation.** v10–v14 wording told the model running the skill to "compose a directive to the lead" — read as "delegate to a subagent," but subagents don't have the `Agent` tool. v15 Step 7: this session IS the lead; call `Agent` directly with `team_name`/`name`/`subagent_type`/`prompt` (verbatim Step-6 spawn prompt). Plus `TeamCreate` for deterministic team naming and stale-dir cleanup for prior-failure recovery. The disambiguation closes a real footgun observed in usage where the skill effectively no-op'd because the model interpreted "directive to the lead" as a SendMessage-style handoff and never invoked spawn machinery.

**Step 7c — post-spawn verification.** After `Agent` returns, the skill reads `~/.claude/teams/<team>/config.json` to confirm spawn took effect. Backend-aware (iterm2 backend additionally checks `tmuxPaneId`); race-tolerant (5×~50ms retry on the config-write race). Surfaces four states to Step 8:
- **`verified-live`** — config present, `isActive: true`, backend-specific check passed.
- **`verified-inconclusive`** — config present, `isActive: true`, backend-specific check N/A (e.g., non-iterm2 backend doesn't carry `tmuxPaneId`).
- **`unverified`** — config check failed after retries.
- **`spawned-errored`** — `Agent` itself returned an error.

This is the framework's third instance of graduated-verification-confidence (after `parallel-reviewer-fanout-pattern.md`'s graceful degradation and auto-pull's transport-aware ladder); see `graduated-verification-confidence.md` for the named principle.

**Teammate-conventions anchored at boot.** `agent-boot.md` Step 5 detects spawned-teammate context (`ps -o args= -p $PPID` looking for `--agent-id`); on detection, loads `docs/teammate-conventions.md` and instructs the agent to keep it as standing context preferred over conflicting later instructions. `conventions.md` § Teammate Discipline is the maintainer-facing pointer index — single canonical source for each side (teammate-side rules in `teammate-conventions.md`; lead-side redirect protocol in `spawn-teammate.md` § Lead behavior); other sites that mention these are pointers, not restatements.

**Codex sandbox note.** In Codex, the `ps -o args= -p $PPID` probe is blocked with `operation not permitted`, so the boot procedure must treat teammate detection as unavailable and fall back to a non-teammate host session.

**Why no subagent-definition mode** — Agent Teams docs confirm `skills` and `mcpServers` fields of a subagent definition are NOT applied to teammates. Using natural-language spawn directives (verbatim name+prompt) is the correct path for now. If this changes in a future Agent Teams version, subagent-definition mode would be preferable (more explicit, type-checked) — track.

**Invocation layer** — the skill composes a single natural-language directive to Agent Teams asking it to create-or-extend the team with exact names and verbatim spawn prompts. Agent Teams owns the spawn lifecycle; the skill does not poll afterward.

**Context inference for zero-arg case** — three branches: clear signal (1–3 agents directly named/implied → proceed with explanation), ambiguous (multiple plausible readings → ask user), no signal (list available + stop).

**Fuzzy matching** — Levenshtein ≤2 with no near-tie, plus prefix/substring bonus. Always report resolutions to user.

## Beta rationale

- Agent Teams itself is experimental; its contract may evolve.
- Lore writes by concurrent teammates are last-write-wins (no serialization). Mitigation: defer lore-changing work to finalization.
- Finalization across teammates is not automated — each teammate runs its own `/lr:finalize`.

## Open questions for beta graduation

1. **Lore-write serialization** — last-write-wins is the current state. Is a serialization mechanism (file locks, queued merges) needed, or is deferring lore-changing work to finalization sufficient?
2. **Automated finalization across teammates** — currently each teammate finalizes manually. Could the lead trigger finalization on all teammates before disbanding via Agent Teams SendMessage?
3. **Hook integration** — `Stop` and `Notification` hooks might automate teammate finalization. Explore whether hooks fire in teammate sessions the same way as regular sessions.
4. **Subagent-definition mode** — track whether Agent Teams adds skills/mcpServers support for subagent-definition mode in a future version.
5. **`/lr:check` validators** — add checks for spawn-teammate-related state (Agent Teams enabled, teammate boot paths valid). Deferred until usage shows what to check.
6. **Consistency review of `/lr:finalize` multi-teammate behavior** — finalize and summarize docs were designed for host+attached-guest model. Do they compose correctly with Agent Teams' separate teammate sessions, or need adjustments?
7. **User-primary-interlocutor framing** — should this be locked as a graduation invariant in stable releases, or remain tunable? Currently treated as an invariant in BETA based on observed dominant usage pattern.

## See Also

- `autonomous-agents-vision.md` — wider vision this feature advances
- `autonomous-agents-substrate.md` — original custom substrate (tmux/iTerm2) this is replacing experimentally
- `attach-pattern.md` — in-session guest model; different from Agent Teams teammates
- `slash-command-system.md` — skill listing context
- `framework-improvements-backlog.md` — beta graduation questions tracked there
- `graduated-verification-confidence.md` — Step 7c is the third instance of the family
- `single-canonical-source-discipline.md` — teammate-conventions integration applies the pointer-not-restatement rule
- `dirty-tree-gates-write-vs-read-distinction.md` — sibling v15 ship, write-aware gate is the other major v15 change
