# Testing technique: simulate a `setsid`-escaped process on macOS without the `setsid` binary

macOS does not ship a `setsid` binary by default (it's a Linux util-linux tool), so a test that
needs to reproduce a process escaping into a new session/process-group — e.g. to reproduce a
"`killpg` can't reach it" bug — cannot shell out to `setsid sh -c '...'` the way it might on Linux
CI.

## Technique

Spawn the "grandchild" from **within** a direct-child Python process, via a nested
`subprocess.Popen([...], start_new_session=True)` call:

1. Parent spawns a direct child normally (no special session flag).
2. That direct child, once running, itself calls `subprocess.Popen([...], start_new_session=True)`
   to spawn the grandchild. `start_new_session=True` gives the grandchild its own session/pgid
   distinct from its parent's — exactly mirroring how a real sandboxed CLI tool (e.g.
   `cursor-agent`'s shell tool) detaches its spawned commands into a fresh session.
3. The direct child writes the grandchild's PID to a marker file so the test can read it back and
   assert on it.

This produces the exact process-tree shape under test (parent → direct child → session-escaped
grandchild) as a fast, deterministic, real-process unit test — no real `cursor-agent` invocation,
network call, or CI-only binary required.

## Where this was used

Built `test_kill_reaches_a_grandchild_that_escaped_into_a_new_session` in
`lore-framework-dev/tests/test_lrb.py` (2026-07-20) to regression-test the Being Keeper's
`_kill`/`_descendant_pids` fix for the cursor `setsid`-escape gap — see
`kill-tree-enumerate-before-signal-ordering.md` and `cursor-agent-real-invocation-contract.md` §
"Sandboxed shell tool escapes process-group kill" for the bug this test locks in.

## Operational recommendation

Prefer this nested-`Popen`-with-`start_new_session` pattern over any real-engine call whenever a
test only needs to reproduce a **process-tree shape** (new session/pgid, specific ppid chain), not
the engine's actual behavior. It's macOS-portable (no GNU-only binary dependency — see
`portable-shell-in-framework-docs.md`), doesn't require network or API cost, and runs in
milliseconds versus the real-engine lifecycle harness's cost/time budget
(`lifecycle-testing-harness.md`). Reserve real-engine invocation for scenarios that need to verify
the engine's *actual* observed behavior (e.g. the A3/B3 Lore Beings lifecycle scenarios), not just the
shape a bug fix needs to handle.

## See Also

- `kill-tree-enumerate-before-signal-ordering.md` — the bug/fix this test was built to lock in
- `cursor-agent-real-invocation-contract.md` — the real-engine finding this synthetic test mirrors
- `macos-ps-o-multi-field-single-line.md`, `macos-case-insensitive-filename-collision-with-memory-files.md` — sibling macOS-portability quirks caught the same way (empirical, not assumed)
- `lifecycle-testing-harness.md` — where real-engine process-tree scenarios (B1/B2/B3) live, as the complementary heavier-weight tier
