# Session-as-Durable-Artifact — Backlog Cluster

Four backlog entries landed in the 2026-06-05 session, none coincidental — they form a coherent **session-as-first-class-durable-artifact** cluster. Worth naming as a cluster (not as a foundational principle topic yet — no immediate design pulls on it — but worth flagging so the next time one of these resumes, the others surface alongside).

## The four cluster members (all parked 2026-06-05)

1. **Boot-Time Auto-Commit + Auto-Push of Upgrades** — solves: locally-upgraded-but-unpushed orphan commits. Frame: the *upgrade event* should propagate to the team automatically because boot is unattended. Full draft preserved at `workdir/draft-auto-push-after-upgrade.md`; see `parked-design-preservation-pattern.md`.
2. **Agent Boot-Context Caching** — solves: paying full re-load cost on every boot. Frame: the *boot context* should be a precomputed durable artifact, invalidated by content-hash of its inputs.
3. **Call-It-a-Day Suspend & Resume** — solves: end-of-day binary between forced-finalize and lost-context. Frame: the *in-flight session* should be a durable artifact even when not at a finalize boundary.
4. **Preserve Claude Code Session JSONLs** — solves: full session transcript is richer than our composed summary, but lives outside the agent repo and rotates without our control. Frame: the *raw session record* should be a durable artifact, searchable and attachable.

## Common thread

**Session-shaped state today is volatile** — only the *summary* is durable, and only at finalize time. Each entry takes a different volatile aspect (the upgrade-just-applied, the boot-context-just-loaded, the in-flight conversation, the raw transcript) and asks "what if this were durable?"

The first real Codex session turned this from an archival concern into a
correctness concern: compaction removed a successful guest attachment from the
model-visible history while the raw JSONL retained it. Transcript-backed
lifecycle recovery should therefore extract a small normalized state capsule
for active agents and finalize checkpoints. This is distinct from committing a
full transcript archive: raw logs remain local by default, and automatically
disabling auto-compaction is only a risk-reduction measure. See
`codex-first-real-session-lifecycle-findings.md`.

## How they compose

- **Suspend (#3) and JSONL-archive (#4) are tightly coupled.** The suspend doc could be a thin pointer at the JSONL plus prose highlights, rather than a hand-composed seed. Solving #4 reshapes #3.
- **Boot-context caching (#2) and JSONL-archive (#4) share an invalidation-keying problem.** Both need a content-hash discipline so cache/archive entries are addressable across versions.
- **Boot auto-push (#1) is the slightly different shape** — it's about *team propagation* rather than *individual durability*. But it's still "boot-time event becomes durable artifact" (the commit + push *are* the durability).

## Why not promoting to a foundational-principle topic yet

The pattern is emergent from the backlog, not driving any current ship. Promote to a principle when one of these becomes active and the others get pulled in alongside (e.g., designing suspend without pinning down archive policy doesn't work). **Trigger:** at least two of the four shipping or designing simultaneously, or a fifth entry joining the cluster.

## Adjacent

- `autonomous-agents-vision.md` is the *autonomous* sibling — what happens when sessions never end. This cluster is the *interactive* sibling — what happens between deliberately-ending sessions. They share the durability vocabulary.

## See Also

- `framework-improvements-backlog.md` § Boot-Time Auto-Commit + Auto-Push of Upgrades, § Agent Boot-Context Caching, § Call-It-a-Day, § Preserve Claude Code Session JSONLs — the four cluster members.
- `autonomous-agents-vision.md` — the autonomous sibling family.
- `session-summaries-feature.md` — current state of session durability (composed summary at finalize only).
- `jsonl-session-files-investigation.md` — prior work on the raw-transcript side; starting point for #4.
- `codex-first-real-session-lifecycle-findings.md` — real compaction failure and
  the engine-neutral state-capsule direction.
- `parked-design-preservation-pattern.md` — methodology for capturing #1's design without shipping (the drill itself was a session output).
