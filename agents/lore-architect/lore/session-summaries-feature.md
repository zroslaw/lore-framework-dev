---
lore: 1
type: topic
summary: "Canonical host and guest session-summary design, including the per-agent Learning audit, review gate, privacy boundary, and finalization integration."
parent: lore-context.md
---

# Session Summaries (v7+, Learning audit v40)

Introduced in v7 as the third phase of finalization — capturing session narrative alongside lore's capture of session learnings. Expanded in v8 with short guest summaries.

## What it is

A model-composed markdown file written at finalization, committed to the host agent's repo. Lore
records durable knowledge; summaries record what happened and audit what the learning phases did
without duplicating the resulting Lore.

**Host summary file layout:** `<lore-agent-repo>/agents/<host-agent>/sessions/<YYYY>/<MM>/<YYYY-MM-DD>-<short-uuid>.md`. Year/month nesting prevents single-directory bloat. Short UUID (8 hex chars) in filename; full UUIDv4 in frontmatter.

**Host frontmatter:** `uuid`, `start`, `end`, `host_agent`, `host_repo`, `participants`, `username`, `full_name`, `topics` (free-form kebab-case tags for later analysis), `artifacts` (list of `{path, kind}` entries), `consulted`.

**Body:** a 3–7 paragraph narrative in past tense, third person, covering context → what happened → plot twists → where it landed → next steps. The process doc contains the exact narrative prompt.

## Canonical Learning audit (v40)

Every canonical host summary carries a mandatory `## Learning` section with one subsection per
active agent. Each subsection has four compact fields: `What mattered`, `Lore changes`, `Not
merged`, and `Issues`. `What mattered` preserves the concrete durable fact, decision, or lesson and
its useful reason; `Lore changes` names destination paths and the semantic operation, including
consolidation or simplification. The other fields keep residual topics and confidence problems
visible. This is an audit of the learning process, not a second copy of Lore.

The audit has an explicit evidence chain:

1. Finalize retains each per-agent Reflection outcome, including its paths and one-line themes, a
   completed-zero result, or a failed/unavailable state.
2. Merge receives the known current-session paths and returns a structured handoff covering what
   mattered, Lore changes, unmerged inputs, and anomalies.
3. Summarize retains both phase outputs and renders them into the canonical host summary.

Only a completed Reflection set makes every unlisted reflection provably carried over. A failed
outcome supports current-session attribution only for its known partial paths; an unavailable
outcome makes origins unknown. Carried-over material may be integrated, but it must not appear
under `What mattered` as learning from this session. Missing phase evidence is reported as
unavailable, never silently converted into “nothing learned.” These states describe provenance and
evidence availability, not the verification-confidence ladder in
`graduated-verification-confidence.md`.

The audit is derived from retained phase outputs. It does not make ordinary session-summary
composition transcript-backed; transcript-backed summaries remain outside the bounded design in
`transcript-backed-finalization-mvp.md`.

## Guest summaries (v8)

When one or more guests are attached via `/lr:attach` and a guest has **lore updates in phase 2**, v8 writes a short record into that guest's own repo at `agents/<guest>/sessions/YYYY/MM/<date>-<short-uuid>.md`. Guests attached but with no lore updates get nothing. Consultants (`/lr:consult`) never get a summary — they remain ephemeral, recorded only in the host summary's `consulted` frontmatter.

**Guest summary shape:**

- **Same session UUID as the host summary.** One grep finds host summary + every guest summary + the private Claude Code JSONL.
- **Slim frontmatter:** `uuid`, `date`, `role: guest`, `host_agent`, `host_summary_repo`, `host_summary_path`, `lore_changes`. The `host_summary_repo` / `host_summary_path` split (review outcome) keeps the path robust across checkout layouts — path is repo-relative, not domain-relative.
- **Short body:** one participation sentence, one contribution sentence, bulleted lore updates with one-line reasons, back-reference to the host summary. No plot-twists, no next-steps — those live in the canonical host narrative.
- **Composed by the host inline in phase 3**, from (a) the host summary just composed, (b) session memory of what the guest contributed, and (c) the merge subagent's return for that guest. No additional subagents are spawned for summarization.
- **Closed action kinds remain unchanged:** merge actions `updated`, `consolidated`, and
  `simplified` map to guest-frontmatter kind `modified`; the body keeps the precise semantic action
  in prose.

**Privacy:** guest repos may have different visibility than the host's. The review gate (phase 3) shows every summary for approval; the approver must consider each guest summary against its destination repo specifically, not uniformly. Individual guest summaries can be dropped at review without blocking the host or other guests.

The design chose pointer-preferring minimalism over full narrative duplication across repos — consistent with the `/lr:consult` precedent where handover is by pointers, not content copies.

## Key design decisions

**Session-wide narrative, per-repo pointer records.** Host summary is the one canonical narrative of the session. Guest summaries are thin pointers back to it, existing so each guest's own repo carries evidence that the guest participated.

**Host summary lives in the host's repo.** The host agent "owns" the session narrative. v8's guest-summary addition resolves the previous v7 limitation where cross-repo guests left no trace in their own repos.

**UUID correlation across host + guests + private JSONL.** The summary's UUIDv4 is echoed in the agent's user-visible output during summarize. That echo lands in the Claude Code session JSONL naturally. A single UUID now correlates (a) the host summary, (b) every guest summary in each guest's own repo, and (c) the private JSONL on the user's machine. See `jsonl-session-files-investigation.md`.

**Mandatory review gate.** The composed summary(ies) are shown to the user before any file is written. Consistent with the show-before-persist principle. No automated privacy scrubbing — judgment + review is the defence.

**Additive and non-blocking.** Summarize runs after reflect + merge. Its failure never rolls back reflect or merge. Disk errors, model errors, user aborts → report and continue. In v8, if summarize fails, phase 4 still commits reflect+merge output alone.

**No migration required for the feature.** `sessions/` directories are created on demand. Both v7 and v8 extensions of this feature are additive — no schema changes to existing repos.

## Automatic full-session archives (v28–v34)

v28 introduced automatic full transcript export as compressed `.jsonl.gz`; v29 replaced it with
committed Markdown under `<lore-agent-repo>/agents/<agent>/archive/<YYYY>/<MM>/`. **v34 retires that
automatic behavior.** `/lr:summarize` and `/lr:finalize` now write summaries and optional aggregate
`usage:` metadata only: they must not create an `archive/` directory, copy native engine logs into an
agent repo, or add `archive:` frontmatter.

Historical committed archives and their historical summary frontmatter remain unchanged. The
`session-takeover archive` command is retained as a dormant manual primitive, not a lifecycle step;
any future automatic archive design must be chosen explicitly, with a new privacy and retention
boundary, rather than reconnecting that command incidentally.

## Why we didn't parse the JSONL

The initial proposal was to parse Claude Code's internal session JSONL files, filter technical noise, and use the result for both reflection and archive. Investigation (captured in `jsonl-session-files-investigation.md`) showed real obstacles: format is proprietary, `~/.claude/sessions/<pid>.json` goes stale after `/clear`, cwd encoding is lossy, filtering decisions are non-obvious, and any archive becomes a long-lived copy of sensitive material.

The pivot to model-composed markdown sidesteps all of these. The cost is that summaries reflect the model's in-context memory of the session (lossy on long sessions due to compaction), tracked as improvement rather than blocker.

**Partially revisited since.** `/lr:takeover` (v24) *does* read engine-native session logs — but as a one-shot conversion into a digest for continuing interrupted work, not as the durable record (`takeover-feature.md`, `engine-session-log-formats.md`). v29 also temporarily kept a full log authored as Markdown rather than parsed from a proprietary format; v34 retires its automatic export. The original objections still hold: native logs remain local by default, and a future archive would require an explicit design decision.

## Integration with finalize

`/lr:finalize` runs reflect → merge → summarize → commit+push. Its retained Reflection outcomes and
Merge handoffs are the evidence source for the Learning audit. `/lr:summarize` standalone still
works for mid-session checkpoints or sessions without lore changes worth recording; when phase
evidence is unavailable, it says so. Standalone summarize does not commit — the user commits what
they want to keep. See `finalization-process.md`.

## Known limitations (tracked in workdir/framework-improvements.md)

1. **Compaction-aware narrative quality.** Long sessions may have earlier turns compressed out of the model's context. The prompt instructs the model to say so plainly rather than confabulate.
2. **Reliable start-time capture.** Start time is best-effort from the model's session memory, rounded to nearest 5 minutes. End time is exact.

(The former "cross-repo guest participation" limitation is **resolved in v8** by guest summaries.)

## Files

- `skills/summarize/SKILL.md` — thin skill pointer (skill-doc-pattern)
- `docs/summarize.md` — authoritative process, frontmatter schemas (host + guest), narrative prompt, failure modes
- `docs/finalize.md` — phase 3 reference point; v8 orchestration home
- `docs/conventions.md` — `sessions/` directory in the agent-repo tree
- `release-notes/7.md` — v7 user-facing description (introduction)
- `release-notes/8.md` — v8 user-facing description (guest summaries, four-phase finalize)
- `release-notes/40.md` — v40 Learning-audit contract and scoped validation record
