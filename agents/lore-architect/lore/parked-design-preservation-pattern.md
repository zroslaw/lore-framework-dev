# Parked-Design Preservation Pattern

When the user pulls the brake on a design mid-draft ("looks complicated, let's postpone"), the right move is a **three-part preserve-and-revert drill**, not a lossy "ok, dropped":

1. **Revert in-flight working-tree changes** to whatever doc was being edited (`git checkout -- <doc>`; verify clean tree). The framework stays at the committed state — no half-shipped procedure that future readers might mistake for current.
2. **Save the full design as a draft in `workdir/`** (`workdir/draft-<feature>.md`) — motivating failure mode, the procedural shape we'd reached, all open seams flagged before parking, and a pointer to the doc that *would* have been edited. Future-you (or another contributor) can resume from the draft without rebuilding the design.
3. **Add a backlog entry** in `framework-improvements-backlog.md` that summarizes the proposal in one paragraph and points at the workdir draft. The backlog is the discoverable surface; the draft is the durable detail.

## Today's instance (2026-06-05)

The boot-time auto-commit + auto-push of upgrades design (motivated by the `activities-lore-agents` orphan `stamp version 13` / `stamp version 15` commits — local upgrades that never propagated). The design reached near-final shape including the **content-equality reconciliation** insight (Step 5b: fetch + compare remote write-set bytes against ours; on byte-for-byte match `reset --soft HEAD~1` + `checkout origin/<branch> -- <write-set>`; on divergence keep local commit + warn). User judged the surface area too large to ship next to in-flight DF/ULA work. Reverted `docs/version-check.md`; saved `workdir/draft-auto-push-after-upgrade.md`; backlog entry under a new top-level section.

## Distinguishing from the don't-defer rule

This is the legitimate-defer companion to `feedback-don-t-defer-completable-scope.md`. The anti-pattern there: deferring **bounded mechanical sweeps** that fit in the current ship. The legitimate pattern here: deferring **open-ended design surface that genuinely needs a separate ship slot**.

The smell that distinguishes them: *bounded mechanical* fits inside an already-ongoing ship; *parked-design* would be its own ship with its own version, release notes, review rounds, and migration write-set declaration. When in doubt: **"if I do this now, am I bundling it onto something already shipping, or am I starting a new ship?"** Starting-a-new-ship → use the drill, don't try to slip it in.

## Side benefit

The workdir draft becomes a candidate for `/lr:consult`-style retrieval if a future session needs the design. The backlog entry is the index; the draft is the body — same shape as `shared-procedure-doc-pattern.md` applied to design-state-in-flight.

## Side-insight to watch (don't promote unless it recurs)

**Content-equality as a reconciliation primitive.** When two parallel processes deterministically produce the same artifact (idempotent migrations producing the same write-set bytes), byte-for-byte comparison is a cheap "we converged" signal — strictly cheaper than rebase/merge and strictly safer than force-push. Surfaced in the auto-push draft; watch for the shape in future designs (idempotent fan-out, dedup, distributed-but-deterministic computation).

## See Also

- `feedback-don-t-defer-completable-scope.md` — the inverse anti-pattern (deferring what should ship now). Today's drill is the legitimate-defer companion.
- `feedback-confirm-before-writing-lore.md` — adjacent corrective ("take a note" ≠ commit to lore mid-session). The parked-design drill is what to do *when* mid-session work is correctly held back.
- `workflow-primitive-operational-notes.md` — content-equality reconciliation as a primitive may surface again in workflow design.
- `shared-procedure-doc-pattern.md` — backlog entry + workdir draft mirror its index-vs-body split.
- `framework-improvements-backlog.md` § Boot-Time Auto-Commit + Auto-Push of Upgrades — the cataloged instance.
- `session-as-durable-artifact-cluster.md` — the drill produced one of four cluster members this session.
