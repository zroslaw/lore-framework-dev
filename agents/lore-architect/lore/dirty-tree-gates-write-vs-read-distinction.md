**Dirty-tree safety gates: gate writes, not reads.** When adding a "skip if working tree is dirty" gate to a framework operation, ask whether the operation *writes* file contents the user could care about. If yes, the gate is appropriate. If no — the operation only advances refs, is naturally idempotent, or git handles the collision cleanly itself — no gate. The gate becomes friction without a safety benefit.

A general principle for safety-gate design, surfaced during v13's auto-pull design but applies anywhere the framework touches a dirty working tree.

## The Concrete Instance

The first draft of `auto-pull.md` had a dirty-tree skip gate copied reflexively from `version-check.md`. A self-review caught the bug:

- **`version-check.md` writes** to `lore-repo.md` (the version stamp), runs migrations that may write more files, then commits. A dirty gate is correct: pulling into dirty + then writing makes the user's edits collide with both the pull and the version stamp. Skip the upgrade if dirty; let the user handle uncommitted changes first.
- **`auto-pull.md` does not write** file contents. `git pull --ff-only` advances `HEAD`, refuses cleanly if it would clobber uncommitted edits, otherwise leaves the working tree untouched. A dirty gate would defeat the most useful invocation site (pre-merge auto-pull, where `reflections/` from phase 1 is intentionally uncommitted).

The dirty-tree gate was correct in one place and wrong in the other. The difference is whether the operation writes.

## The Principle

When adding a safety gate, **name what the gate is protecting against**. "Uncommitted changes" is not a hazard by itself — it's only hazardous if the operation *writes in a way that collides with the user's edits*. Articulate the collision scenario:

- "If we pull into dirty and the pull touches the same files, edits would be lost." → No, `--ff-only` refuses cleanly. No gate needed.
- "If we run migrations into dirty, the migration's writes would mix with the user's uncommitted edits." → Yes, the gate is protecting against a real collision. Apply it.
- "If the user has uncommitted work, our operation might overwrite it." → Articulate which operation, what it writes, what file. If the answer is "git refuses cleanly anyway," the gate is friction without a safety benefit.

If the operation doesn't write file contents at all (just advances refs, queries state, prints output), git's existing semantics handle any conflict. An extra gate is noise.

## Verified Live (v13 review)

Round-2 review constructed two scenarios in `/tmp` to test auto-pull's no-gate decision:

1. **Dirty edits to a *different* file than the pull touches** → fast-forward succeeds, edits preserved on the working tree throughout.
2. **Dirty edits to the *same* file the pull touches** → pull refuses with `error: Your local changes to <file> would be overwritten by merge. Aborting.`. Edits preserved.

Either way, edits are safe. The gate would have prevented case (1) for no benefit, and would not have made case (2) any safer than git already does. Net: friction without safety.

This kind of filesystem-grounded verification is exactly what `parallel-reviewer-fanout-pattern.md`'s correctness lens was designed to catch — the v12 ship's targeted-vs-broader cache-wipe defect was caught the same way.

## v15 refinement — gate on collision with the write-set, not blanket-dirty

The v13 distinction was binary: writes get gates, reads don't. v15 refines the write-side a notch further: even on a write operation, the gate should refuse only on **collisions with what the operation will actually write**, not on every dirty file.

The motivating bug: agent repos routinely carry uncommitted runtime state from other agents (`workdir/*` pulse logs, watch markers). The v14 boot-time auto-upgrade gate refused on *any* dirty file, so it overfired on every boot — friction without benefit, because the dirty files weren't in the migration's write paths.

**The split:** every write operation has a **write-set** — the concrete paths it will touch. The gate's job is `dirty ∩ write-set`:

- **Empty intersection** → proceed. The operation can't collide with anything dirty.
- **Non-empty** → defer with a file-naming actionable message ("would clobber `path/X`; commit, stash, or revert").

For migrations, the write-set is declared in `## Write Paths` in the migration doc (one fenced block per version). For other future write operations, the same shape applies: declare what you'll write, the gate intersects against dirty.

**Operational rules that fall out:**

- **Write-sets must be declared.** Undeclared = unknown = fall back to conservative blanket-dirty for safety. Backward-compatible, but creates real friction; authors are nudged to always declare. `/lr:check` #20 enforces declaration presence + body shape (section / fenced body / sentinel-or-glob), all error-severity.
- **Sentinels matter.** An explicit empty write-set (`(none)`, optionally followed by space/hyphen/em-dash + prose, or an empty fenced block) is meaningfully different from an absent declaration. Same data on disk could mean either; the convention disambiguates by treating absent-section as unknown and present-with-empty-body as explicit-empty.
- **Conflict markers are orthogonal.** They're a structural-inconsistency hard-defer regardless of write-set scope, because git itself can't merge through them safely. Step 1a handles them before the collision check runs.
- **Workspace-root paths are a known gap.** The boot-time gate is per-repo and cannot see workspace-root files (`.claude/commands/lr-*-agent.md`); migrations 2/5/6 don't declare those paths because the declaration would be decorative — the per-repo gate can't intersect against them. Protection there is the in-migration three-way merge (`update.md` § Handling Manual Edits to Generated Files), not the gate. Documented in `conventions.md` § Known gap: workspace-root paths.

## The principle generalized: minimum-blast-radius refusal

Both v13's read-vs-write split AND v15's collision check follow the same shape: **identify what the operation actually does, gate exactly on conflicts with that, accept incidental noise.** The gate's job is *minimum-blast-radius refusal* — refuse exactly when refusal prevents data loss, not preemptively.

- v13 instance — auto-pull is a *read* (advances refs, git refuses cleanly on real collision). No gate; "uncommitted in unrelated files" is incidental noise.
- v15 instance — boot-time auto-upgrade is a *write*, but only against its declared paths. Gate on `dirty ∩ write-set`; "dirty in `workdir/`" is incidental noise.

Both refute reflexive "uncommitted = unsafe" reasoning. The hazard is *collision with the operation's actual effects*, nothing else. Future framework operations should design for the same shape: name the effect set, gate on intersection, accept everything else.

**Open future application:** `/lr:update` is interactive-by-design and currently writes through dirty files unconditionally; bringing the v15 collision-check gate to it would make the principle universal across automatic and user-invoked write paths. Tracked in `framework-improvements-backlog.md`.

## Generalization Beyond Auto-Pull

The principle composes with existing tooling/safety topics:

- **`tooling-cwd-safety.md`** is the same shape: gate the *protocol* (never `cd` in Bash when downstream tools depend on CWD), not the symptom (a stray `cd` that happens to be harmless). Both topics reflect "name what the gate is protecting against."
- **Migrations and finalize phase 4** are write-heavy and gate accordingly.
- **`/lr:check`** is read-only and has no dirty gate — correct.
- **`/lr:recall`** is read-only (search lore) and has no dirty gate — correct.

When adding new framework operations, walk the question: read or write? If write, gate appropriately. If read (or naturally collision-safe), no gate.

## Diagnostic Signals (misframing)

- **Copy-paste safety reflexes.** "Other operations have a dirty gate, so this one should too." → Stop and ask what each gate protects against.
- **"Belt and suspenders" justification.** If the operation doesn't write, an extra gate isn't belt-and-suspenders, it's just friction.
- **Conflating "uncommitted" with "unsafe."** Uncommitted is a normal working-tree state. The pre-merge call site for `auto-pull.md` is *intentionally* dirty — `reflections/` from phase 1 has not been committed yet. A dirty gate there would prevent merge from ever benefitting from auto-pull.

## When the Gate *Is* the Right Choice

Don't take this principle to mean "no dirty gates ever." Apply gates when:

- The operation writes file contents the user could be editing concurrently.
- The operation cannot reliably distinguish "my write" from "user's pre-existing edit" (e.g., commits everything in the working tree as a side effect).
- The operation is destructive or hard to reverse.

The trio of write-heavy framework operations that *do* gate: `version-check.md` (migrations + version stamp), finalize commit phase (autocommit everything in agent subtree), and any operation that runs `git reset` or `git checkout`.

## Operational Guidance

When designing a new framework operation:

1. Articulate explicitly: does this operation **write** file contents?
2. If yes: identify the collision scenario. Add the dirty-tree gate. Document what it protects against in the procedure doc.
3. If no: skip the gate. Document the no-gate decision and the reasoning, so a future reviewer doesn't add the gate reflexively. (`auto-pull.md`'s "Why we don't gate on a dirty working tree" subsection is the worked example.)
4. Test both branches: dirty + matching files (does git refuse cleanly?), dirty + unrelated files (does the operation succeed?). Filesystem verification beats prose review.

## See Also

- `auto-pull-mechanism.md` — the v13 canonical no-gate read operation.
- `update-process.md` and `version-check.md` — the canonical gated-write operations.
- `tooling-cwd-safety.md` — adjacent "name what the gate is protecting against" git-discipline topic.
- `parallel-reviewer-fanout-pattern.md` — the correctness/filesystem-verification lens that catches mis-applied gates.
- `freshness-contracts-at-session-boundaries.md` — adjacent: when the operation *is* a read, the freshness question dominates the gate question.
- `consistency-checks.md` — `/lr:check` #20 enforces write-set declaration shape (section / fenced body / sentinel-or-glob).
- `graduated-verification-confidence.md` — sibling principle covering how gate *outcomes* are reported (binary vs. graduated by confidence/blast-radius).
