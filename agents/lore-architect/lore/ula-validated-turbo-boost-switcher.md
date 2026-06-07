# ULA Validated on My-Turbo-Boost-Switcher — Single Unit + End-to-End

Operational validation of the ULA BETA on a real repo, in two phases: a single-unit simulation (2026-06-03) and a full end-to-end workflow run after the DF restructure (2026-06-07).

## What happened (2026-06-03 — single unit, six bugs)

Ran a ULA pass on **`My-Turbo-Boost-Switcher`** (a macOS menu-bar Objective-C app that toggles Intel Turbo Boost via a kext). Target file `SystemCommands.m`. We deliberately scoped the test to a **single unit** — `run-task-as-admin` (`+ (BOOL) runTaskAsAdmin:withAuthRef:andArgs:`) — to exercise the dev ULA features cheaply.

**That one unit alone surfaced six potential bugs**, including genuinely valuable findings:

- **`always-returns-yes`** — the method logs auth failures but unconditionally returns `YES`. Root of a **three-layer error-swallowing chain**: `runTaskAsAdmin` → `loadModuleWithPath` (ignores the return) → `AppDelegate` (ignores that too). The unhappy-path skeleton (BOOL returns, NSLog) exists but was never wired up. UI shows "Turbo Boost disabled" while the CPU is still boosting.
- **`deprecated-api`** — `AuthorizationExecuteWithPrivileges` is removed on macOS 14+; the app's core mechanism is silently broken on current hardware (silently, because of the always-YES bug).
- Plus a pipe fd-leak, NULL-authRef / nil-path guards, and a VLA stack-overflow path.

## Why this matters (for the framework)

- **A single-unit pass is already worth running.** You don't need a whole-file or whole-repo sweep to get value — even one well-chosen unit yields real, actionable findings. Good evidence for ULA's per-unit granularity and for cheap exploratory passes. (Mechanics of scoping to one unit: bypass the splitter, see `workflow-args-string-coercion-and-single-unit-scoping` notes folded into `workflow-primitive-operational-notes.md`.)
- It produced exactly the narrative-vs-structured split (see `ula-narrative-vs-structured-output.md`) that motivated the DF repo's `file-lore.md`.

## End-to-end after the DF restructure (2026-06-07)

The **actual `df-ula-file` workflow** (not a Sonnet simulation) ran clean end-to-end on **`CheckUpdatesHelper.m`**, after the two workflow fixes (`args`-parse guard + `$schema`-strip — see `df-module-conventions.md`). The produced artifacts in `My-Turbo-Boost-Switcher-df/` match the locked design exactly:

- Layout `repo-lore/CheckUpdatesHelper.m/ula/{bugs,scenarios,gap}.yaml` — per-file, under `repo-lore/`, **no unit dir** — plus `repo-lore/.gitkeep`, `df.config.yaml`, `README.md` at the root (exactly what `df-repo-init` scaffolds).
- Provenance Header (`source-sha` + `config: { id: default }`) atop each artifact; **`source-sha` == live `git hash-object CheckUpdatesHelper.m`** (provenance honestly identifies the analyzed bytes).
- Grouped `units: []` shape; gap invariants hold per element (e.g. `ulaNotImplemented: 10` == 10 listed).
- 5 units, ~20 substantive Objective-C bugs (nil-delegate silent failure, non-UTF-8 / HTTP-error body misreported as "no update", concurrent shared-ivar corruption, deprecated `NSURLConnection` run-loop hang).

So the feature works post-restructure, and the per-file / `repo-lore/` / provenance / grouped design is **validated against real output**, not just on paper.

**Caveat — re-validate on a file with tests.** `CheckUpdatesHelper.m` has **no existing tests**, so gap Direction B (`ula-missed`) and the clean-room *comparison* path were not stressed — everything came back `not-implemented` with `considered-tests: []`. The "find existing tests no scenario anticipated" half of gap analysis is still unexercised end-to-end.

## How to apply

When demoing or smoke-testing ULA, pick **one important-but-small unit** in a behaviorally-rich file (privileged ops, branching on OS/arch/state) rather than a trivial getter. `run-task-as-admin` was ideal: short, central, multiple failure modes. For a full-pass smoke test, run `df-ula-file` on a whole behaviorally-rich file — but to exercise the *full* gap analysis, pick one that **already has tests**.

Related: `aiqa-ula-feature.md`, `df-per-repo-backbone.md`, `df-module-conventions.md`, `provenance-header-concept.md`, `ula-narrative-vs-structured-output.md`, `workflow-primitive-operational-notes.md`.
