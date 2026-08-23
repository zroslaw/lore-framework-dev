---
lore: 1
type: topic
summary: "A new preflight.py leg that needs workspace_scan.py (or anything else that imports preflight at module level) must import it locally inside the calling function, not at preflight.py's top level, or the module graph cycles at load time."
parent: lore-context.md
---

# A Deferred Import Breaks an `lr_core` Circular-Import Trap

`lr_core`'s module graph has a standing cycle risk at `preflight.py`. `workspace_scan.py` does
`from .preflight import detect_engine, discover_workspace, find_repos` at module level, so any *new*
module that `preflight.py` wants to import at **its own module level**, which itself imports
`workspace_scan`, creates a circular import (`preflight -> new_module -> workspace_scan ->
preflight`) that fails at load time. `workspace_scan`'s `from .preflight import ...` runs while
`preflight` is still mid-initialization — its own top-of-file import statement hasn't returned yet,
so the names `workspace_scan` wants aren't in `preflight`'s namespace.

## The concrete instance (v42 workspace-auto-refresh design, 2026-08-23)

`workspace_refresh.py` needs `run_workspace_scan` (from `workspace_scan.py`) and is itself called
from `preflight.cmd_preflight` — see
[workspace-auto-refresh-design.md](workspace-auto-refresh-design.md). Resolved by importing
`workspace_refresh` **locally, inside `cmd_preflight`** (`from . import workspace_refresh as
_workspace_refresh`, right where it's used) rather than at `preflight.py`'s top level.

By the time any `cmd_*` function actually runs, `cli.py`'s own top-level imports have already fully
loaded every module in `sys.modules`, so the deferred import is safe and `preflight.py`'s own
module-level import graph never grows the cycle.

## How to apply

Any future `preflight.py` leg that needs something from `workspace_scan.py` — or from any other
module that itself imports `preflight` — should use this same local-import-at-call-site pattern
rather than adding a top-level import to `preflight.py`. Check for this cycle before adding a new
top-level import there: does the module I'm about to import (directly or transitively) import
`preflight`? If yes, import it locally inside the function that uses it, not at module scope.

## See Also

- [workspace-auto-refresh-design.md](workspace-auto-refresh-design.md) — the feature whose
  implementation surfaced this.
- [literate-accelerator-pattern.md](literate-accelerator-pattern.md) — `preflight.py`'s docstrings
  are the normative procedure spec; this is a structural constraint on the module that hosts them.
