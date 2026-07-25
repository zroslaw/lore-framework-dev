#!/usr/bin/env bash
# Unified Cursor CLI usage probe.
#
# Returns:
#   - plan_quota: monthly plan % (live API)
#   - session_context: context window % (statusline snapshot, interactive CLI only)
#
# Usage:
#   ./lr-cursor-usage.sh
#   ./lr-cursor-usage.sh --json

set -euo pipefail
export LR_CURSOR_USAGE_MODE="${1:-}"

python3 <<'PY'
import base64, json, os, sqlite3, sys, urllib.request
from datetime import datetime, timezone

mode = os.environ.get("LR_CURSOR_USAGE_MODE", "")
cache = os.environ.get("LR_CONTEXT_USAGE_CACHE", os.path.expanduser("~/.cursor/context-usage.json"))
state_db = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")

def b64url_decode(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

def read_token():
    if not os.path.exists(state_db):
        return None
    conn = sqlite3.connect(state_db)
    row = conn.execute("SELECT value FROM ItemTable WHERE key='cursorAuth/accessToken'").fetchone()
    conn.close()
    if not row:
        return None
    token = row[0].decode() if isinstance(row[0], bytes) else row[0]
    if isinstance(token, str) and token.startswith('"'):
        token = json.loads(token)
    return token

def fetch_plan_quota(token: str):
    payload = json.loads(b64url_decode(token.split(".")[1]))
    sub = payload.get("sub")
    if not sub:
        raise RuntimeError("JWT missing sub claim")
    cookie = f"WorkosCursorSessionToken={sub}::{token}"
    req = urllib.request.Request(
        "https://cursor.com/api/usage-summary",
        headers={"Cookie": cookie, "Accept": "application/json", "User-Agent": "lr-cursor-usage/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    plan = data.get("individualUsage", {}).get("plan", {})
    return {
        "membership": data.get("membershipType"),
        "billing_cycle": {"start": data.get("billingCycleStart"), "end": data.get("billingCycleEnd")},
        "total_percent_used": plan.get("totalPercentUsed"),
        "auto_percent_used": plan.get("autoPercentUsed"),
        "api_percent_used": plan.get("apiPercentUsed"),
        "used": plan.get("used"),
        "limit": plan.get("limit"),
        "remaining": plan.get("remaining"),
        "on_demand": data.get("individualUsage", {}).get("onDemand"),
    }

def read_session_context():
    if not os.path.exists(cache):
        return {
            "available": False,
            "reason": "no statusline snapshot (needs interactive cursor-agent + statusLine config)",
            "snapshot_path": cache,
        }
    with open(cache, encoding="utf-8") as f:
        snap = json.load(f)
    ctx = snap.get("context", {})
    return {
        "available": ctx.get("used_percent") is not None,
        "snapshot_path": cache,
        "checked_at": snap.get("checked_at"),
        "session_id": snap.get("session_id"),
        "session_name": snap.get("session_name"),
        "model": snap.get("model"),
        "used_percent": ctx.get("used_percent"),
        "remaining_percent": ctx.get("remaining_percent"),
        "input_tokens": ctx.get("input_tokens"),
        "output_tokens": ctx.get("output_tokens"),
        "window_size": ctx.get("window_size"),
        "current_usage": ctx.get("current_usage"),
    }

out = {
    "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "engine": "cursor-cli",
    "plan_quota": None,
    "session_context": read_session_context(),
    "sources": {
        "plan_quota": "GET cursor.com/api/usage-summary (undocumented; cookie sub::jwt)",
        "session_context": "statusline snapshot (interactive CLI only)",
        "per_turn_tokens": "cursor-agent --output-format json -> usage",
    },
}

token = read_token()
if not token:
    out["plan_quota"] = {"available": False, "reason": "not logged into Cursor"}
else:
    try:
        out["plan_quota"] = {"available": True, **fetch_plan_quota(token)}
    except Exception as e:
        out["plan_quota"] = {"available": False, "reason": str(e)}

if mode == "--json":
    print(json.dumps(out, indent=2))
    sys.exit(0)

pq, sc = out["plan_quota"] or {}, out["session_context"] or {}
print(f"Checked: {out['checked_at']}")
if pq.get("available"):
    print(f"Plan ({pq.get('membership')}): total={pq.get('total_percent_used')}% auto={pq.get('auto_percent_used')}% api={pq.get('api_percent_used')}%")
    bc = pq.get("billing_cycle") or {}
    print(f"Billing: {str(bc.get('start','?'))[:10]} -> {str(bc.get('end','?'))[:10]}")
else:
    print(f"Plan: unavailable ({pq.get('reason', 'unknown')})")
if sc.get("available"):
    print(f"Session: {sc.get('used_percent')}% ({sc.get('input_tokens')}/{sc.get('window_size')} tok) model={sc.get('model')}")
else:
    print(f"Session: unavailable ({sc.get('reason', 'unknown')})")
PY
