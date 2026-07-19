#!/usr/bin/env python3
"""Real cursor-agent e2e through the Being Keeper tick loop.

Costs API money when cursor-agent is authenticated. Skips cleanly when not
logged in. Run from lore-framework-dev:

  python3 tests/test_lrb_cursor_real_e2e.py

Optional env:
  LR_FRAMEWORK_DIR   lore-framework checkout (default: sibling)
  LRB_CURSOR_MODEL   model name (default: composer-2.5)
  LRB_CURSOR_ENGINE  cursor-agent binary (default: cursor-agent on PATH)
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

FRAMEWORK_DIR = os.environ.get("LR_FRAMEWORK_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "lore-framework")
)
LRB = os.path.join(FRAMEWORK_DIR, "scripts", "lrb.py")
MODEL = os.environ.get("LRB_CURSOR_MODEL", "composer-2.5")
CURSOR_BIN = os.environ.get("LRB_CURSOR_ENGINE", "cursor-agent")


def load_lrb():
    spec = importlib.util.spec_from_file_location("lrb", LRB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cursor_logged_in():
    try:
        r = subprocess.run([CURSOR_BIN, "status"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return False
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode == 0 and "not logged in" not in out.lower()


def main():
    if not cursor_logged_in():
        print("SKIP: cursor-agent not logged in — run 'cursor-agent login' or set CURSOR_API_KEY")
        return 0

    lrb = load_lrb()
    tmp = tempfile.mkdtemp(prefix="lrb-cursor-e2e-")
    home = os.path.join(tmp, "home")
    launchagents = os.path.join(tmp, "launchagents")
    os.environ["LRB_HOME"] = home
    os.environ["LRB_LAUNCHAGENTS_DIR"] = launchagents
    workspace = os.path.join(tmp, "workspace")
    os.makedirs(workspace)

    repo = os.path.join(workspace, "e2erepo")
    agent_dir = os.path.join(repo, "agents", "probe")
    os.makedirs(agent_dir)
    with open(os.path.join(repo, "lore-repo.md"), "w") as f:
        f.write('---\ndescription: e2e\nversion: "1"\n---\n')
    now = __import__("datetime").datetime.now()
    cron = "%d %d * * *" % (now.minute, now.hour)
    with open(os.path.join(agent_dir, "being.md"), "w") as f:
        f.write("""---
description: cursor e2e probe being
engine: cursor
model: %s
daily-usd: 1
existential-tasks:
  - name: e2e-probe
    schedule: "%s"
    prompt: task.md
    timeout-minutes: 5
---

# probe
""" % (MODEL, cron))
    with open(os.path.join(agent_dir, "task.md"), "w") as f:
        f.write("Reply with exactly E2E-CURSOR-KEEPER-OK as your final output message.")

    cfg = {
        "workspaces": [workspace],
        "engines": {
            "cursor": {
                "command": shutil.which(CURSOR_BIN) or CURSOR_BIN,
                "kind": "cursor",
                "permission_mode": "full",
                "plugin_dir": FRAMEWORK_DIR,
            }
        },
    }
    lrb.save_config(cfg)

    being_id = "e2erepo/probe"
    keeper = lrb.Keeper()
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        keeper.tick(cfg)
        state = lrb.load_state(workspace)
        bstate = state["beings"].get(being_id, {})
        if not bstate.get("running") and bstate.get("last_runs"):
            break
        time.sleep(2)

    with open(lrb.ledger_path(workspace, being_id)) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    print(json.dumps(lines, indent=2))
    finished = [l for l in lines if l.get("outcome") in ("ok", "error", "timeout", "unparseable", "crashed")]
    if not finished:
        print("FAIL: no finished session in ledger", file=sys.stderr)
        shutil.rmtree(tmp, ignore_errors=True)
        return 1
    last = finished[-1]
    print("outcome=%s cost_usd=%s" % (last.get("outcome"), last.get("cost_usd")))
    log_path = last.get("log_path")
    if log_path and os.path.exists(log_path):
        with open(log_path) as lf:
            print("log tail:", lf.read()[-500:])
    shutil.rmtree(tmp, ignore_errors=True)
    if last.get("outcome") != "ok":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
