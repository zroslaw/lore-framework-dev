# Framework-defined role + thin-role-pointer pattern

A framework pattern surfaced designing the lr-dev **context agent** (2026-06-01): a *role* whose standardized behavior is owned by the plugin, and whose per-instance `role.md` is a **thin pointer** to it. This is the thin-pointer pattern — already used for skills (`skill-doc-pattern.md`) and for boot commands (`/lr-<name>-agent` → `agent-boot.md`) — applied to a **role** for the first time. Sibling of `shared-procedure-doc-pattern.md`: one plugin doc, authored once, referenced from many sites/instances.

## Problem it solves

When a role *recurs across many instances* (every source repo gets a context agent) and must be **standardized yet centrally updatable**, baking the standard into each instance's `role.md` freezes it — later improvements don't propagate, and you'd have to hand-edit N agents to roll a change out.

## Mechanism

- Standardized behavior lives in **one versioned plugin doc** (e.g. `lore-framework/docs/context-agent.md`), stamped on `lore-framework/VERSION`, distributed via the marketplace.
- Each instance's `role.md` is **thin**: instance-specific identity + a pointer — *"operate per `${CLAUDE_PLUGIN_ROOT}/docs/<role>.md`."* Resolves at boot exactly as `agent-boot.md` references its sibling docs.
- **Updates ride plugin distribution:** edit the doc, bump VERSION (+ cache-clear footer if cache-affecting, per `cache-clear-footer-convention.md`), and every instance picks up the current version at *next boot*. **Zero per-instance churn; no migration for behavior changes** — the instance only ever held a pointer.

## role vs lore-context split

`role.md` = pointer to central behavior + instance identity; `lore-context.md` = content only, conforming to the standard structure the plugin doc defines.

**Discipline: behavior + structure central, content local.** Never let behavioral instructions leak into instance lore — that re-freezes the standard locally and defeats the pattern. Genuine deviations go into a small "instance-specific overrides" section in the thin role (≈99% inherited / 1% local).

## Reproducibility

Instances are *generated from a template* (e.g. a flag on `/lr:create-agent`, or a dedicated generator skill), the same way `/lr:register-repo` emits boot commands from `agent-boot.md`. Template + thin-pointer = reproducible *and* updatable — the two properties that otherwise feel in tension (a baked-in template is reproducible but frozen; a hand-written role is flexible but unrepeatable).

## When to reach for it

A role qualifies when **(a)** it recurs across many instances, **(b)** its behavior should be standardized, and **(c)** that behavior should stay centrally updatable. A one-off agent role does not qualify — write its `role.md` directly. The pattern earns its keep only when the propagate-a-change-to-N-instances problem is real.

First application: the lr-dev context agent (see `lr-dev-direction.md`). Generalize further if other recurring framework-defined roles emerge.

## See Also

- `skill-doc-pattern.md` — the broader thin-pointer pattern this applies to a role (SKILL.md → doc; generated commands → `agent-boot.md`).
- `shared-procedure-doc-pattern.md` — sibling: one plugin doc referenced from many call sites, authored once. Same "central body, thin callers" shape, applied to procedures rather than roles.
- `slash-command-system.md` — thin generated artifacts (`/lr-<name>-agent` delegations) as precedent.
- `lr-dev-direction.md` — the context agent, this pattern's first application.
- `framework-scope-vs-agent-scope.md` — central behavior is the universal core; instance identity/overrides are the agent-specific remainder.
- `placeholder-vocabulary.md` — `${CLAUDE_PLUGIN_ROOT}` resolution that makes the thin pointer work at boot.
- `cache-clear-footer-convention.md` — the cache-clear discipline a behavior-doc bump must observe.
