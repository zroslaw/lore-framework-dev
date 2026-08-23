---
lore: 1
type: topic
summary: "A proxy is chosen because it is convenient to observe and it fails on the cases you did not have in mind — usually deliberate user action; write the real condition in words first, and prefer one an existing component already computes."
parent: lore-context.md
---

# Short-Circuit on the Condition, Not a Proxy for It

Named 2026-08-23 while fixing a day-one bug in the workspace auto-refresh design
([workspace-auto-refresh-design.md](workspace-auto-refresh-design.md)).

**The bug.** A brand-new workspace has no refresh state file, so the refresh would fire on first boot
and try to *clone* every declared repo — blowing its timeout mid-clone and leaving partial checkouts
on the user's very first boot.

**The tempting fix, and why it was wrong.** Short-circuit on "is there a state file." But *deleting
the state file is the documented gesture for forcing a refresh.* Keying on file absence means a user
who deleted the stamp to force a refresh gets told to go run a command instead. The proxy and the real
condition diverge exactly where a user acts deliberately.

**The real question** was never "is this the first run" but **"does this need to clone"** — and the
existing scanner already answers it (finding S6: declared repos absent from disk).

## Why the shape recurs

A proxy is chosen because it is convenient to observe, and it holds for the case you had in mind. It
fails on the cases you did not, and the failure lands on deliberate user action — the worst possible
place, because the user has an explicit intent and gets contradicted.

## How to apply

- **Write the condition down in words first, then ask what you are about to test.** If they are
  different sentences, you are using a proxy.
- **Check what else produces the proxy's value.** A state file is absent when it was never written
  *and* when someone deleted it on purpose.
- **Prefer a condition an existing component already computes** over a new signal — it is usually the
  real one, and it carries its own maintenance.

## See Also

- [guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md)
  — sibling shape from the same design.
- [reuse-existing-correlation-signal.md](reuse-existing-correlation-signal.md) — the positive form of
  the third rule: reuse a signal the system already carries before inventing plumbing.
- [name-keyed-global-registry-cannot-answer-per-scope.md](name-keyed-global-registry-cannot-answer-per-scope.md)
  — adjacent: a stored value that cannot answer the question actually being asked.
- [workspace-auto-refresh-design.md](workspace-auto-refresh-design.md) — the design this was named in.
