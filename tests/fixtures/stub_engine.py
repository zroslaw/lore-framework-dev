#!/usr/bin/env python3
"""Stub engine for lrb (Being Keeper) tests.

Mimics the `claude -p <prompt> --output-format json --model <model>` contract
lrb.py spawns against — a single JSON object on stdout with `result`,
`total_cost_usd`, `is_error` — at zero real cost and zero external calls, so
tests exercise the whole Keeper loop (spawn -> capture -> ledger -> budget)
deterministically. Registered via `lrb engines add stub --command
.../stub_engine.py`.

Controlled via env vars (read fresh per invocation, so a test can vary
behavior across spawns within one process by mutating os.environ):
  STUB_COST             total_cost_usd to report (default "0.01")
  STUB_IS_ERROR          "1" -> is_error true
  STUB_SLEEP_SECONDS     seconds to sleep before responding (default "0")
  STUB_RESULT_TEXT       the "result" text (default "stub ok")
  STUB_CRASH             "1" -> exit(1) with NOTHING on stdout or stderr
                          (simulated hard crash — tests the "crashed" outcome)
  STUB_STDERR_NOISE      "1" -> write a stderr line BEFORE the real stdout
                          JSON (simulates a CLI update notice/warning) —
                          stdout still gets exactly the real JSON, since
                          lrb.py routes stderr to a sibling file
  STUB_IGNORE_SIGTERM    "1" -> install a SIGTERM handler that ignores it, so
                          only SIGKILL actually ends the process (tests the
                          Keeper's SIGTERM-then-SIGKILL-after-grace path)
"""
import argparse
import json
import os
import signal
import sys
import time


def main():
    if "--version" in sys.argv:
        print("stub-engine 1.0")
        return 0

    p = argparse.ArgumentParser()
    p.add_argument("-p", "--print", action="store_true")
    p.add_argument("--output-format")
    p.add_argument("--model")
    p.add_argument("--dangerously-skip-permissions", action="store_true")
    p.add_argument("prompt", nargs="?")
    p.parse_known_args()

    if os.environ.get("STUB_IGNORE_SIGTERM") == "1":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)

    if os.environ.get("STUB_STDERR_NOISE") == "1":
        sys.stderr.write("stub-engine: a CLI update is available (harmless stderr noise)\n")
        sys.stderr.flush()

    sleep_s = float(os.environ.get("STUB_SLEEP_SECONDS", "0"))
    if sleep_s:
        time.sleep(sleep_s)

    if os.environ.get("STUB_CRASH") == "1":
        return 1  # nothing on stdout or stderr: tests the true "crashed" (no output at all) path

    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": os.environ.get("STUB_IS_ERROR") == "1",
        "result": os.environ.get("STUB_RESULT_TEXT", "stub ok"),
        "total_cost_usd": float(os.environ.get("STUB_COST", "0.01")),
        "session_id": "stub-session",
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
