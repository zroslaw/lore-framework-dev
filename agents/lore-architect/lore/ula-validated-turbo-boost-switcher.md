# ULA Validated on My-Turbo-Boost-Switcher — Single Unit, Six Bugs

Operational validation of the ULA BETA on a real repo (2026-06-03).

## What happened

Ran a ULA pass on **`My-Turbo-Boost-Switcher`** (a macOS menu-bar Objective-C app that toggles Intel Turbo Boost via a kext). Target file `SystemCommands.m`. We deliberately scoped the test to a **single unit** — `run-task-as-admin` (`+ (BOOL) runTaskAsAdmin:withAuthRef:andArgs:`) — to exercise the dev ULA features cheaply.

**That one unit alone surfaced six potential bugs**, including genuinely valuable findings:

- **`always-returns-yes`** — the method logs auth failures but unconditionally returns `YES`. Root of a **three-layer error-swallowing chain**: `runTaskAsAdmin` → `loadModuleWithPath` (ignores the return) → `AppDelegate` (ignores that too). The unhappy-path skeleton (BOOL returns, NSLog) exists but was never wired up. UI shows "Turbo Boost disabled" while the CPU is still boosting.
- **`deprecated-api`** — `AuthorizationExecuteWithPrivileges` is removed on macOS 14+; the app's core mechanism is silently broken on current hardware (silently, because of the always-YES bug).
- Plus a pipe fd-leak, NULL-authRef / nil-path guards, and a VLA stack-overflow path.

## Why this matters (for the framework)

- **A single-unit pass is already worth running.** You don't need a whole-file or whole-repo sweep to get value — even one well-chosen unit yields real, actionable findings. Good evidence for ULA's per-unit granularity and for cheap exploratory passes. (Mechanics of scoping to one unit: bypass the splitter, see `workflow-args-string-coercion-and-single-unit-scoping` notes folded into `workflow-primitive-operational-notes.md`.)
- It produced exactly the narrative-vs-structured split (see `ula-narrative-vs-structured-output.md`) that motivated the DF repo's `index.md`.

## How to apply

When demoing or smoke-testing ULA, pick **one important-but-small unit** in a behaviorally-rich file (privileged ops, branching on OS/arch/state) rather than a trivial getter. `run-task-as-admin` was ideal: short, central, multiple failure modes.

Related: `aiqa-ula-feature.md`, `df-per-repo-backbone.md`, `ula-narrative-vs-structured-output.md`, `workflow-primitive-operational-notes.md`.
