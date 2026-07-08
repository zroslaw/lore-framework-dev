# Session Takeover Feature (`/lr:takeover`, BETA, v24)

Cross-engine session continuation: when a session dies (rate limit, crash, engine switch), its engine-native log is converted into a markdown **takeover digest** that a new session on any engine loads as prior context and continues. Origin: the user's Codex hit its token limit mid-work; the sessions were restored and continued on Claude Code.

## Design decisions

- **The digest consumer is an LLM, not a program** — so the portable format is plain markdown (session metadata, `## User`/`## Assistant` turns, tool calls collapsed to one-line bullets, explicit "session ends here" footer), not a rich interchange schema. No standard exists for agent-session transcripts; each vendor's log is proprietary (see `engine-session-log-formats.md` for the per-engine ground truth).
- **Internal intermediate uses the de facto API message shape** `{role, content}` / `{tool, args, result}` — adding an engine only needs a new `parse_<engine>()` + `list_<engine>()` in `scripts/session-takeover`.
- **Skill shape:** thin `skills/takeover/SKILL.md` → `docs/takeover.md` (orchestration: discover→ask, or direct takeover; boot the digest's lore agent before acting; verify on-disk state; confirm per step 5) → script does the mechanical work. Script is python3 stdlib-only — the second sanctioned python component after `lr-wait` (see `plugin-mcp-server-convention.md` § non-shell runtimes precedent).
- **Bare invocation must ask, not pick** — recency is not intent.
- **Boundaries:** read-only on source logs; takeover is a continuation, not a finalization trigger; trust on-disk state over the digest — a dying session's tail may claim unfinished work (the RC glider session's last act was rewriting a generator it never ran).

## Validation (2026-07-08)

Two haiku subagents (the ambiguity-detector tier, `haiku-ambiguity-detector.md`) executed `docs/takeover.md` cold: the bare flow produced the table+question correctly; the direct flow converted a Codex session, booted `health-advisor`, verified disk state, and gave a faithful step-5 confirmation. Cross-engine (Codex→Claude) and cross-model (gpt-5.4→haiku) both proven. A ~50KB digest ≈ 15k tokens for a 75-turn session — loads comfortably.

## Known gaps / follow-ups

- **Cursor conversion unsupported**: `~/.cursor/chats/<ws-hash>/<uuid>/store.db` is a content-addressed SQLite blob store (ids = SHA-256 of data, no ordering); messages are JSON blobs in API shape but assistant turns sit in binary records. Listed but not convertible until someone reverse-engineers ordering.
- Discovery's temp-dir filter (`--all` to include) hides lifecycle/quality fixtures, but evaluator sessions run *in project dirs* still appear in the Claude list — cosmetic, unfixed.
- No lifecycle-harness scenario for takeover yet; validated only by the ad-hoc haiku runs above.

Tracked in `framework-improvements-backlog.md` § Takeover.

## Relation to the session-durability family

Takeover is the first *built* feature (ship pending with v24 — see `v24-ship-status.md`) in the session-as-durable-artifact territory (`session-as-durable-artifact-cluster.md`): it reads the raw engine-native transcript (cluster member #4's substrate) and delivers a working resume path (member #3's goal) — but by on-demand conversion, not archiving. Raw logs stay local and untouched; the digest is a derived, portable artifact.

## See Also

- `engine-session-log-formats.md` — empirical per-engine log-format ground truth this feature is built on.
- `session-as-durable-artifact-cluster.md` — the parked cluster this partially delivers.
- `jsonl-session-files-investigation.md` — the earlier "don't parse the JSONL" decision; takeover is the sanctioned read-only, on-demand exception (no archiving, no stability dependency for correctness).
- `v24-ship-status.md` — ship state of the release carrying this feature.
- `haiku-ambiguity-detector.md` — the validation tier used.
