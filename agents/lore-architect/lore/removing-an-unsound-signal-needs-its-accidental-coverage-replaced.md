# Removing an Unsound Signal Needs Its Accidental Coverage Replaced

Deleting the "`~/.codex/` exists → codex" rung from engine detection was correct — it fired for
every session on any machine with Codex installed
(`engine-profile-must-be-observed-not-believed.md`). But a cold reviewer found what the deletion
cost, and the cost was not obvious from the rung itself.

## What the bad rung was quietly covering

Codex's two remaining signals **fail together**:

- Its sandbox blocks `ps`, so process-ancestry detection reads nothing at all.
- Framework-root containment only matches when `<framework-root>` sits under `~/.codex/`.

So a Codex session run against a worktree or a dev checkout — which is exactly how this framework's
own contributors run it, per `docs/worktrees.md` — matches **nothing**, and silently falls back to
the claude profile. That means the wrong memory file, the wrong subagent mechanism, and Claude's
`/lr:<skill>` invocation syntax that falls through to the shell and fails under `codex exec`.

The unsound rung had been covering that case by accident.

## The rule

The lesson is **not** "keep the bad heuristic." A signal that is wrong in general cannot be retained
for the sake of the cases it accidentally gets right; that trades a loud correct answer for a quiet
wrong one everywhere else.

The lesson is that **removing it is only half the change: enumerate what the removed signal was
catching, and handle those cases deliberately.** A cleanup that improves the rule and regresses the
outcomes is not a cleanup.

## How it was handled here

Not by restoring the rung, and not by inventing a new heuristic — by making the no-signal branch
**legible instead of silent**:

- `data.engine.detail` distinguishes "ancestry ran and matched nothing" from "`ps` could not be read
  at all" — the second is the routine Codex case and says so.
- `confidence: "assumed"` marks the fallback as a substitution rather than a finding, and the
  warning names `--engine <claude|codex|cursor>` as the remedy. The user is the one who knows which
  engine they launched; the only useful move is to tell them they are the authority here.
- `docs/engines/codex.md` carries a **§ Detection blind spot** telling Codex users to pass
  `--engine codex` when running off anything but a native install.

## Generalizes

**When a fallback exists, ask which real configuration lands on it, and whether that configuration
can tell.** A fallback that is silently correct for most callers and silently wrong for one
identifiable class is worse than one that announces its uncertainty — the affected class is usually
the one least able to notice.

## See Also

- `engine-profile-must-be-observed-not-believed.md` — the change this rule was learned during.
- `graduated-verification-confidence.md` — confidence as a reported value rather than a boolean;
  `assumed` vs `confident` is that principle at the detection layer.
- `docs-engines-convention.md` — where the per-engine remedy lives at point of use.
- `codex-git-sandbox-blocks-dotgit.md`, `codex-engine-capabilities.md` — the Codex sandbox
  constraints that make its two remaining signals correlated rather than independent.
