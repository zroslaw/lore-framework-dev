# Kill-tree ordering: enumerate descendants before signaling any ancestor

General principle for **any** process-supervisor code that reaps a tree by walking ancestry
(ppid chain) rather than by process group/session: snapshot the full descendant list **before**
sending a signal to any ancestor in that tree. Never enumerate-then-kill in the other order.

## Why

Killing an ancestor first can let the OS reparent a still-alive descendant to PID 1 (init/launchd)
before the enumeration runs — silently erasing the very ppid link the walk depends on. The walk
then finds nothing, and the descendant is missed entirely, even though the enumeration logic itself
is correct in isolation. This is a race between the kernel's reparenting and your own code's reads,
not a logic bug you can spot by reading the walk function alone.

## Where this bit us

First surfaced in the Being Keeper's `_kill`/`_descendant_pids` (`scripts/lrb.py`), added to close
the cursor `setsid`-escape gap (a sandboxed shell tool's spawned commands land in a new process
group that `killpg` can't reach — see `cursor-agent-real-invocation-contract.md` §
"Sandboxed shell tool escapes process-group kill", `engine-kinds-design-decision.md`). The
regression test `test_kill_reaches_a_grandchild_that_escaped_into_a_new_session` (`test_lrb.py`)
failed on the first version of the fix — not because the ppid-walk logic was wrong (a standalone
check of `_descendant_pids` proved it was correct), but because the direct child died and was
reaped before the walk ran. The fix was purely reordering: enumerate first, kill second. See
`lore-beings-mvp-takeover-review.md` § Fifth pass for the full incident.

## Operational recommendation

Any future Keeper-like or process-supervisor code in this framework that reaps a tree by ancestry
(rather than by process group) must follow this same discipline: enumerate the full descendant set,
*then* signal, working from leaves/descendants toward the ancestor if signaling in stages. Treat
this as a correctness invariant to check for in review whenever new kill-tree/process-cleanup code
is added, not just something to test for after the fact.

## See Also

- `cursor-agent-real-invocation-contract.md` — the concrete cursor `setsid`-escape bug this ordering
  fix was closing
- `engine-kinds-design-decision.md` — the per-engine-kind design context
- `lore-beings-mvp-takeover-review.md` § Fifth pass — the full incident narrative
- `testing-simulate-process-escape-without-setsid-binary.md` — how the regression test that caught
  this reproduces the process-tree shape without a real `setsid` binary
- `hot-path-latency-can-expose-latent-test-timing-races.md` — a second-order consequence of this
  same fix: the `ps`-based descendant walk added real latency to `_kill`'s previously-instant hot
  path, which broke unrelated tests relying on that speed as an implicit sync primitive
