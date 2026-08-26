---
lore: 1
type: topic
summary: "When a diagnostic and its remedy answer the same predicate, derive both from one code path — a checker that drifts from the doer routes users to a fix that can never succeed."
parent: lore-context.md
---

# Two Functions Answering One Question Must Derive From One Code Path

v43 shipped a checker (`check_plugin_config`, feeding `workspace-status` finding S18) and a doer
(`apply_plugin_config`, called by `workspace-init`) that both answered *is this file configured?* —
by separate logic. Two independent reviewers found the same divergence.

A settings file holding one of our own keys at the wrong type (`"enabledPlugins": "not-a-dict"`) is
valid JSON, so it never lands in the unreadable bucket. The checker's `isinstance` guard fell
through to `None` and bucketed it **`missing`**. The doer's merge refused it as a structural
conflict and left it alone.

**The result is a diagnostic that routes the user to a fix that cannot succeed, forever.** S18 says
"run `workspace-init`"; `workspace-init` errors; the file stays broken; the next scan says the same
thing. That is worse than emitting no finding at all — a silent gap invites investigation, while
confident wrong advice ends it.

Fix: the checker now *asks the merger*, on a deep copy, and classifies from what it does. Agreement
is guaranteed by construction rather than by two implementations being kept in sync by hand.

## The rule

When a diagnostic and a remedy both answer the same predicate, derive both from **one** code path.
This is [single-canonical-source-discipline.md](single-canonical-source-discipline.md) applied to
**code** rather than prose, and the failure mode is sharper: prose that drifts confuses a reader,
but a checker that drifts sends a user into a loop.

**Corollary for finding vocabularies:** a finding's buckets must be able to express *"this needs a
human, not the automated fix."* Missing / unresolvable / disabled — three routes, three different
remedies, and only one of them is the skill.

## See Also

- [single-canonical-source-discipline.md](single-canonical-source-discipline.md) — the prose form,
  and its § *Fixing a duplicated rule in code can recreate it in prose*.
- [a-reported-error-is-not-proof-the-file-survived.md](a-reported-error-is-not-proof-the-file-survived.md)
- [short-circuit-on-the-condition-not-a-proxy.md](short-circuit-on-the-condition-not-a-proxy.md)
- [project-scope-plugin-config-feature.md](project-scope-plugin-config-feature.md)
