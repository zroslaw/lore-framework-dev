#!/usr/bin/env python3
"""Codex-shaped stub engine for lrb (Being Keeper) tests.

Mimics the `codex exec --json --skip-git-repo-check -m <model> <prompt>`
contract lrb.py spawns against for engines of kind "codex" — JSONL events on
stdout ending in `turn.completed` (with token usage, NO usd cost) or
`turn.failed` — shapes captured verbatim from a real `codex-cli 0.142.5` run.
Also VERIFIES the argv shape the Keeper used: any drift from the real codex
CLI contract makes the run end with a `turn.failed` naming the mismatch, so a
Keeper regression shows up as a failed session, not a silent pass.

Env controls (read fresh per invocation):
  STUB_CODEX_FAIL           "1" -> emit an error event + turn.failed, exit 1
  STUB_CODEX_SLEEP_SECONDS  seconds to sleep before responding (default "0")
"""
import json
import os
import sys
import time


def emit(obj):
    print(json.dumps(obj))
    sys.stdout.flush()


def main():
    if "--version" in sys.argv:
        print("stub-codex-engine 1.0")
        return 0

    argv = sys.argv[1:]
    problems = []
    if not argv or argv[0] != "exec":
        problems.append("first arg must be 'exec', got %r" % (argv[:1],))
    if "--json" not in argv:
        problems.append("--json missing")
    if "--skip-git-repo-check" not in argv:
        problems.append("--skip-git-repo-check missing")
    model = None
    if "-m" in argv:
        mi = argv.index("-m")
        model = argv[mi + 1] if mi + 1 < len(argv) else None
    if not model:
        problems.append("-m <model> missing")
    prompt = argv[-1] if argv else ""
    if not prompt or prompt.startswith("-"):
        problems.append("prompt must be the last positional arg, got %r" % prompt)

    emit({"type": "thread.started", "thread_id": "stub-thread"})
    emit({"type": "turn.started"})

    sleep_s = float(os.environ.get("STUB_CODEX_SLEEP_SECONDS", "0"))
    if sleep_s:
        time.sleep(sleep_s)

    if problems:
        emit({"type": "turn.failed", "error": {"message": "argv contract violation: %s" % "; ".join(problems)}})
        return 1
    if os.environ.get("STUB_CODEX_FAIL") == "1":
        emit({"type": "error", "message": "stub codex failure"})
        emit({"type": "turn.failed", "error": {"message": "stub codex failure"}})
        return 1

    emit({"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": "stub codex ok"}})
    emit({"type": "turn.completed", "usage": {"input_tokens": 1000, "cached_input_tokens": 100,
                                              "output_tokens": 20, "reasoning_output_tokens": 5}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
