---
lore: 1
type: topic
summary: "A probe against live OS state can cost the user password prompts — an axis cheapest-first gate ordering never prices; rank mechanisms by user cost, validate on a copy, prefer ones touching only a file attribute."
parent: lore-context.md
---

# On Live macOS System State, Validate on a Copy and Prefer File-Attribute Mechanisms

From the Keeper login-item work, 2026-09-05
(`keeper-login-item-name-and-icon.md`).

**Every edit to a LaunchAgent plist makes Background Task Management re-evaluate the login item, and
each re-evaluation raises an admin password prompt to the user.** Reaching the answer took six or
seven `launchctl bootout` / `bootstrap` cycles, and the user got visibly frustrated by the prompts.
The mechanism that finally worked required **zero** reloads.

**The cost was not compute or tokens — it was prompts charged to the human**, an axis my usual
cheapest-first gate ordering does not price at all. A "cheap" probe that interrupts the user six
times is not cheap. Cheapest-first ranks deterministic tests below paid engine runs on money and
minutes; nothing in that ordering notices that a free `launchctl` call can be the most expensive
step in the session.

Operational rules this yields:

- Before iterating against live OS-registered state, ask **what each attempt costs the user**, not
  just what it costs the machine. Enumerate the candidate mechanisms *first* and rank them by that
  cost, rather than trying them in the order they occur to you.
- **Validate on a copy first** — a throwaway label, a scratch plist, a spare file — and touch the
  live registration only once the mechanism is known to work.
- **Prefer a mechanism that touches only a file attribute over one that re-registers with the OS.**
  Same reasoning as preferring a filesystem check over an engine probe in the lifecycle harness:
  fewer moving parts, no re-entry into a system daemon's bookkeeping, no user-visible side effect.

## See Also

- [verify-before-acting-on-suspected-bugs.md](verify-before-acting-on-suspected-bugs.md) — diagnosis
  is cheap and a wrong fix is not; the new axis here is that the *diagnosis itself* was not cheap,
  because it ran against live system state.
- [point-of-use-guardrails-beat-recorded-lore.md](point-of-use-guardrails-beat-recorded-lore.md) —
  the sibling question of where a guardrail lives.
- [macos-documents-permission-loss-mid-session.md](macos-documents-permission-loss-mid-session.md) —
  the other direction of the same coupling: live OS state changing *under* a run.
- [keeper-login-item-name-and-icon.md](keeper-login-item-name-and-icon.md) — the case, and the
  mechanism that needed no reload.
