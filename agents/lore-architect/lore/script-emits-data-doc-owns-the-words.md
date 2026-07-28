# Script Emits Data, Doc Owns the Words

**In a literate accelerator, the script emits data; the doc owns user-facing words.** A script
string that reads like a finished message will be printed as one. If a doc owns the message —
especially an engine-specific one — the script must not emit a competing version, however
convenient it looks in the JSON.

This is `single-canonical-source-discipline.md` applied at the **script/doc boundary**, a newer
seam than the doc/doc boundary that principle was written for.

## The concrete instance (v31, Codex `test_07`)

Codex's `test_07` lifecycle scenario printed

```
version skew: repo=32 framework=31 (repo-ahead) — see version-check.md
```

and stopped, never reaching `version-check.md`'s engine-specific plugin-refresh remedy.

This first reads like the model paraphrasing. It was not — **two instructions competed and the
model took the cheaper one:**

- `lr-core preflight` emitted that string into `warnings`.
- `agent-boot.md` Step 2 says "`warnings` — surface anything material to the user in one line each."
- The *same* Step 2 also routes `repo-ahead` into `version-check.md`, which owns the real remedy.

Printing the warning *looks like* handling the skew. The verdict field and the warning were two
renderings of one fact, and only one of them carried the fix. This is the only genuinely confirmed
v31 model-fidelity defect from the 2026-07-27 lifecycle re-run.

## Applied (v31 branch `b824da5`)

- `lr-core` no longer warns on `repo-behind` / `repo-ahead` / `differs`. `data.version` already
  carries verdict, repo and framework, and both consumers (`agent-boot.md` Step 2, `attach.md`
  Step 2) route on it explicitly — verified before deleting.
- The `unknown` warning **stays**: that is not a skew, silence there would read as "versions
  agree", and it deliberately points nowhere.
- `agent-boot.md` now states that a skew verdict is a **routing signal, not a message**.

## Diagnostic

When reviewing an accelerator's output fields, ask of every human-readable string: *is there a doc
that owns this message?* If yes, the script should emit only the machine-readable fact the doc
routes on. A field that is both a fact and a finished sentence gives the executor a cheaper path
than the one you intended.

## See Also

- `single-canonical-source-discipline.md` — the parent principle.
- `literate-accelerator-pattern.md` — the accelerator shape this rule constrains.
- `skill-doc-pattern.md` — the same one-owner discipline at the skill/doc seam.
- `haiku-ambiguity-detector.md` — why a cheap-tier run is what exposes "model took the cheaper
  path" defects at all.
- `v31-lifecycle-rerun-partial-green-2026-07-27.md` — the run that surfaced it.
