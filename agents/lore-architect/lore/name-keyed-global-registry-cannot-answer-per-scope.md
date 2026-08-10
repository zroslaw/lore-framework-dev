---
lore: 1
type: topic
summary: "A registry keyed by bare name and stored outside the scope you are asking about cannot answer a per-scope question; compute per scope and state the residual limit."
parent: lore-context.md
---

# A Name-Keyed Global Registry Cannot Answer a Per-Scope Question

## The instance (v37, finding S15)

Codex per-agent shortcuts live in `~/.codex/skills/lr-<agent>-agent/` — **user-global**, not
workspace-scoped, and keyed by the **bare agent name**.

The first implementation asked "does this workspace have any Codex shortcut?" by intersecting all
registered names against all agent names. One shortcut anywhere silenced the finding for every repo
in the workspace. Worse: because agent names collide across repos *by design*
(`register-repo.md` § Collision rule), a shortcut registered in an unrelated workspace for a
same-named agent could silence it too.

Fixed to decide **per repo** — a repo is unserved when none of *its own* agents has a matching
shortcut.

## Two transferable rules

1. **A verdict whose payload is per-item must have a trigger computed per item.** A global trigger
   with a per-item payload is a contract mismatch that only reads as a bug once someone constructs
   the two-item case — which is exactly what the contract-integrity reviewer did, and what neither
   the implementation nor the single-repo dogfood workspace would ever have surfaced.
2. **When a check has an irreducible false-negative window, put the limit in the user-facing
   wording.** The name-collision hole cannot be closed without changing the shortcut key, so the
   S15 row now says to treat its silence as weak evidence, not proof. Silence a user believes means
   "fine" is worse than a check that admits what it cannot see.

## See Also

- [widening-a-source-drops-its-validation.md](widening-a-source-drops-its-validation.md) — the other v37 defect that review caught and design did not.
- [registered-shortcuts-are-framework-owned.md](registered-shortcuts-are-framework-owned.md) — what the registry holds.
- [graduated-verification-confidence.md](graduated-verification-confidence.md) — "weak evidence, not proof" as a first-class reported state.
