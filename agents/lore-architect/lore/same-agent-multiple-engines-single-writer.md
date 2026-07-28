# Same Agent, Multiple Engines — Single Writer

Discovered mid cross-engine collaboration (v32 shortcut-bootstrap design): Cursor and Codex were
**both also booted as lore-architect** against this same `lore-framework-dev` repo — not three
different agents coordinating, one agent identity running on three engines at once. Caught before
anyone wrote, but it generalizes: if two or more sessions of the *same* agent identity independently
run reflect → merge → commit against the same `lore/` + `lore-context.md`, that is a real git
conflict on shared prose — not the harmless filename-owned sequence collision that a coordination
message log (see `cross-engine-team-substrate-validated.md`) tolerates. Distinct engines do not
imply distinct write scopes.

## Resolution that held for the rest of the session

Exactly one engine session declares itself the **finalize write-side owner** — in this case Claude,
the engine the user was directly steering. The others explicitly hold off on reflect/merge/commit/
push against the shared repo and contribute only through the shared coordination thread, which the
writer folds in during its own reflect/merge pass. All three engines agreed to this without friction
once the ambiguity was named out loud.

## Operational rule

**Before any engine starts a write-side finalize in a multi-engine session, confirm none of the
other participating sessions share the same agent identity against the same repo.** If they do,
designate a single writer explicitly (don't assume it by default) and have the others route their
contributions through the coordination channel instead of their own finalize.

This is a corollary of `finalization-process.md`'s existing single-repo-conflict handling
(`push-conflict-resolution.md`) — that mechanism resolves a *detected* concurrent-write conflict
after the fact; this rule is about *avoiding* the conflict in the first place when the concurrency
is foreseeable (multiple engines, same agent, same session-scale task).

## The wide-staging variant (2026-07-28)

Write-ownership is necessary but not sufficient. A concurrent session can sweep your uncommitted
work into *its* commit without ever touching your content, purely through a directory-wide
`git add`. Same shared-workspace hazard, different mechanism — no conflict, no loss, but ungated
work ships under someone else's commit message. See
`concurrent-session-committed-my-uncommitted-work.md`.

## See Also

- `concurrent-session-committed-my-uncommitted-work.md` — the staging-scope variant of this hazard;
  read alongside, since designating a single writer does not protect files the writer never meant to
  stage.
- `cross-engine-team-substrate-validated.md` — the shared-folder coordination substrate this
  collaboration used; the write-ownership rule is the missing piece that makes it safe for tasks
  that end in a real commit.
- `cross-engine-relay-not-attributable-authority.md` — a companion trust rule from the same session:
  even the designated writer can't act on another session's paraphrase of a user decision.
- `finalization-process.md`, `push-conflict-resolution.md` — the existing single-engine finalize
  and conflict-resolution machinery this rule sits upstream of.
- `attach-pattern.md` — a different multi-agent shape (one executor, multiple agent identities
  loaded); this rule is the inverse (one agent identity, multiple executors/engines).
