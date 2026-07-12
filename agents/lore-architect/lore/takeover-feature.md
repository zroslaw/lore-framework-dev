# Session Takeover Feature (`/lr:takeover`, BETA, v24)

Cross-engine session continuation: when a session dies (rate limit, crash, engine switch), its engine-native log is converted into a markdown **takeover digest** that a new session on any engine loads as prior context and continues. Origin: the user's Codex hit its token limit mid-work; the sessions were restored and continued on Claude Code.

## Design decisions

- **The digest consumer is an LLM, not a program** — so the portable format is plain markdown (session metadata, `## User`/`## Assistant` turns, tool calls collapsed to one-line bullets, explicit "session ends here" footer), not a rich interchange schema. No standard exists for agent-session transcripts; each vendor's log is proprietary (see `engine-session-log-formats.md` for the per-engine ground truth).
- **Internal intermediate uses the de facto API message shape** `{role, content}` / `{tool, args, result}` — adding an engine only needs a new `parse_<engine>()` + `list_<engine>()` in `scripts/session-takeover`.
- **Skill shape:** thin `skills/takeover/SKILL.md` → `docs/takeover.md` (orchestration: discover→ask, or direct takeover; boot the digest's lore agent before acting; verify on-disk state; confirm per step 5) → script does the mechanical work. Script is python3 stdlib-only — the second sanctioned python component after `lr-wait` (see `plugin-mcp-server-convention.md` § non-shell runtimes precedent).
- **Bare invocation must ask, not pick** — recency is not intent.
- **Boundaries:** read-only on source logs; takeover is a continuation, not a finalization trigger; trust on-disk state over the digest — a dying session's tail may claim unfinished work (the RC glider session's last act was rewriting a generator it never ran). **Extend the same rule to any secondary summary of a session, including our own lore:** trust the raw log tail over prose that summarizes it. In the v24 production takeover the digest's last line was `exit 1: FAIL` (the Codex quality run), but a hand-written rescued-state lore topic had softened it to "interrupted when the session died." When a topic is written to capture a dying session's final state, its prose can drift from the raw tail — trust the tail and verify on-disk before acting.

## Validation (2026-07-08)

Two haiku subagents (the ambiguity-detector tier, `haiku-ambiguity-detector.md`) executed `docs/takeover.md` cold: the bare flow produced the table+question correctly; the direct flow converted a Codex session, booted `health-advisor`, verified disk state, and gave a faithful step-5 confirmation. Cross-engine (Codex→Claude) and cross-model (gpt-5.4→haiku) both proven. A ~50KB digest ≈ 15k tokens for a 75-turn session — loads comfortably.

## Production use (2026-07-08)

First real (non-test) use for its actual purpose: a Claude Code session took over the dying Codex `lore-architect` session `019f3ed9` and continued its work to completion — **it shipped v24**. This is production validation on top of the ad-hoc haiku runs above.

- Bare `/lr:takeover` → `session-takeover --list` produced the compact cross-engine table; the user picked the Codex "Boot lore architect" session by partial id.
- Direct convert → 82-turn / 207-tool-call digest, fit comfortably in context.
- The digest showed the recorded session had booted `lore-architect` — already active in the taking-over session, so the "boot the digest's agent first" step was a designed no-op.
- Step-4 on-disk verification paid off: confirmed v24 was uncommitted in the tree, HEAD still at v23, and the session's `init` `AGENTS.md` fix had survived on disk. Continuation resumed from the exact stop point.

## Cross-engine continuation use (2026-07-12)

The skill also worked for a Claude session handoff into Codex during v25 work. Operational lessons
reinforced the design:

- Bare `/lr:takeover` must list sessions and ask; do not choose by recency.
- Direct takeover with an id should convert to a digest, read it fully, then boot the digest's
  recorded lore agent identity before acting when one is present.
- After digest load, verify on-disk repo state before trusting the final assistant turn. In the v25
  handoff, the digest said the workspace slice had been committed and the repo was clean, but disk
  verification found dirty `assets/logo.svg` in `lore-framework`.
- On Codex, boot auto-pull may need network escalation; still attempt it because boot requires it.
- Takeover is continuation, not finalization. The receiving session's finalization preserves the
  recovered session's learning.

## Known gaps / follow-ups

- **Cursor conversion unsupported**: `~/.cursor/chats/<ws-hash>/<uuid>/store.db` is a content-addressed SQLite blob store (ids = SHA-256 of data, no ordering); messages are JSON blobs in API shape but assistant turns sit in binary records. Listed but not convertible until someone reverse-engineers ordering.
- Discovery's temp-dir filter (`--all` to include) hides lifecycle/quality fixtures, but evaluator sessions run *in project dirs* still appear in the Claude list — cosmetic, unfixed.
- No lifecycle-harness scenario for takeover yet; validated only by the ad-hoc haiku runs above.

Tracked in `framework-improvements-backlog.md` § Takeover.

## Relation to the session-durability family

Takeover is the first *shipped* feature (in v24) in the session-as-durable-artifact territory (`session-as-durable-artifact-cluster.md`): it reads the raw engine-native transcript (cluster member #4's substrate) and delivers a working resume path (member #3's goal) — but by on-demand conversion, not archiving. Raw logs stay local and untouched; the digest is a derived, portable artifact.

## See Also

- `engine-session-log-formats.md` — empirical per-engine log-format ground truth this feature is built on.
- `session-as-durable-artifact-cluster.md` — the parked cluster this partially delivers.
- `jsonl-session-files-investigation.md` — the earlier "don't parse the JSONL" decision; takeover is the sanctioned read-only, on-demand exception (no archiving, no stability dependency for correctness).
- `versioning-release-types.md` — v24 history entry (the release that shipped this feature).
- `haiku-ambiguity-detector.md` — the validation tier used.
