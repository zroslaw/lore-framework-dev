---
lore: 1
type: topic
summary: "Never use --autostash in the framework: on a real content collision it exits 0, writes conflict markers into the file, and reports success — the general ban is on any automatic path that resolves a conflict by overwriting."
parent: lore-context.md
---

# Never `--autostash`: It Reports Success While Corrupting

**No framework path may use `--autostash`.** `git pull --ff-only --autostash` meeting a real content
collision **exits 0**, prints `Applying autostash resulted in conflicts. Your changes are safe in the
stash.`, and leaves the file in `UU` state with literal conflict markers written into it. Reproduced
independently three times in one session.

It converts a safe, loud refusal into a silent corruption that reports success — in **lore files**,
which are then read back as knowledge. The exit code is the trap: any caller checking `rc` sees a
pass, and every automatic caller here checks `rc`.

## The general rule

The ban is not really about autostash. It is about the shape: **an operation that "resolves" a
conflict by discarding or overwriting, and reports success, must not exist in any automatic path** —
no `stash`, no `--force`, no `reset --hard`. A refusal is an acceptable outcome; a silent overwrite
is not. What `--ff-only` refuses is precisely what must stay refused
([git-ff-only-is-file-granular.md](git-ff-only-is-file-granular.md)).

Worth remembering the asymmetry, so the rule is not mis-generalized: `git pull --rebase --autostash`
*does* cleanly resolve divergence and preserve unrelated dirty files. The danger is specific to
autostash meeting a real content collision — which is exactly the case a lore repo produces.

## Where the guardrail lives

In `conventions.md` § Tooling: Git Safety, at the point of use — not only here. A trap recorded only
as lore protects nobody
([point-of-use-guardrails-beat-recorded-lore.md](point-of-use-guardrails-beat-recorded-lore.md));
shipping that section is C7 in
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).

Sibling in evidence discipline:
[a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md) — here the
*success report* is the self-report that must not be trusted.
