#!/usr/bin/env python3
"""Cursor-shaped stub engine for lrb (Being Keeper) tests.

Mimics the `cursor-agent -p <prompt> --output-format json --model <model>
--plugin-dir <dir> --workspace <ws> [--force --sandbox disabled]` contract
lrb.py spawns against for engines of kind "cursor" — a single JSON object on
stdout with result/total_cost_usd/is_error/usage. Also VERIFIES the argv shape
the Keeper used: any drift from the real cursor-agent CLI contract makes the
run end with is_error true, so a Keeper regression shows up as a failed session.

Env controls (read fresh per invocation):
  STUB_COST              total_cost_usd to report (default "0.01"; omit with "none")
  STUB_IS_ERROR          "1" -> is_error true
  STUB_SLEEP_SECONDS     seconds to sleep before responding (default "0")
  STUB_RESULT_TEXT       the "result" text (default "stub cursor ok")
  STUB_CRASH             "1" -> exit(1) with NOTHING on stdout
  STUB_STDERR_NOISE      "1" -> write harmless stderr before JSON stdout
"""
import argparse
import json
import os
import sys
import time


def main():
    if "--version" in sys.argv:
        print("stub-cursor-engine 1.0")
        return 0

    p = argparse.ArgumentParser()
    p.add_argument("-p", "--print", action="store_true")
    p.add_argument("--output-format")
    p.add_argument("--model")
    p.add_argument("--plugin-dir")
    p.add_argument("--workspace")
    p.add_argument("--trust", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--sandbox")
    p.add_argument("prompt", nargs="?")
    args, _ = p.parse_known_args()

    problems = []
    if not args.print and "-p" not in sys.argv:
        problems.append("-p missing")
    if args.output_format != "json":
        problems.append("--output-format json missing")
    if not args.model:
        problems.append("--model missing")
    if not args.plugin_dir:
        problems.append("--plugin-dir missing")
    if not args.workspace:
        problems.append("--workspace missing")
    if "--trust" not in sys.argv:
        problems.append("--trust missing")
    if not args.prompt:
        problems.append("prompt missing")

    if os.environ.get("STUB_STDERR_NOISE") == "1":
        sys.stderr.write("stub-cursor-engine: harmless stderr noise\n")
        sys.stderr.flush()

    sleep_s = float(os.environ.get("STUB_SLEEP_SECONDS", "0"))
    if sleep_s:
        time.sleep(sleep_s)

    if os.environ.get("STUB_CRASH") == "1":
        return 1

    if problems:
        payload = {
            "type": "result",
            "subtype": "error",
            "is_error": True,
            "result": "argv contract violation: %s" % "; ".join(problems),
            "session_id": "stub-cursor-session",
        }
        print(json.dumps(payload))
        return 1

    cost_env = os.environ.get("STUB_COST", "0.01")
    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": os.environ.get("STUB_IS_ERROR") == "1",
        "result": os.environ.get("STUB_RESULT_TEXT", "stub cursor ok"),
        "session_id": "stub-cursor-session",
        "usage": {"input_tokens": 500, "output_tokens": 12},
    }
    if cost_env != "none":
        payload["total_cost_usd"] = float(cost_env)
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
