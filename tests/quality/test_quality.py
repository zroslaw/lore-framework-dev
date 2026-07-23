#!/usr/bin/env python3
"""Lore-agent quality benchmark runner (PoC).

Run:  LR_QUALITY=1 python3 tests/quality/test_quality.py -v
      LR_QUALITY=1 LR_TEST_MODEL=haiku python3 tests/quality/test_quality.py -v
      LR_QUALITY=1 LR_ENGINE=codex python3 tests/quality/test_quality.py -v
      LR_QUALITY=1 LR_ENGINE=cursor python3 tests/quality/test_quality.py -v

Runs every probe in probes.py in two arms (treatment: lore has the fact;
control: fact removed, repo shape identical), scores stages S1/S2/S3, and
prints a scorecard:

  LUS  (Lore Utilization Score) — % of stage points earned, per arm
  Behavior uplift — S3 pass-rate(treatment) − S3 pass-rate(control);
                    the headline "what did the lore buy us" number

This is a benchmark, not a regression gate: the unittest asserts that runs
and judging completed, and reports the scores. Results are also written as
JSON under tests/quality/results/ for cross-run comparison.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import (
    ENGINE, JOBS, JUDGE_MODEL, MODEL, SKIP_REASON, TRACES_TOOLS,
    build_quality_fixture, collect_workspace_artifacts, judge_s3, run_probe,
    score_s2,
)
from probes import DISTRACTOR_TOPICS, NEEDLE_TOPICS, PROBES, WORKDIR_FILES

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.abspath(os.environ.get(
    "LR_QUALITY_RESULTS_DIR", os.path.join(HERE, "results")
))

ARMS = ["treatment", "control"]


def _csv_env(name):
    value = os.environ.get(name, "")
    return [part.strip() for part in value.split(",") if part.strip()]


def selected_probes_and_arms():
    probe_ids = _csv_env("LR_QUALITY_PROBES")
    arm_names = _csv_env("LR_QUALITY_ARMS")
    probes_by_id = {p["id"]: p for p in PROBES}
    unknown_probes = [p for p in probe_ids if p not in probes_by_id]
    unknown_arms = [a for a in arm_names if a not in ARMS]
    if unknown_probes:
        raise ValueError("unknown LR_QUALITY_PROBES: " + ", ".join(unknown_probes))
    if unknown_arms:
        raise ValueError("unknown LR_QUALITY_ARMS: " + ", ".join(unknown_arms))
    selected_probes = [probes_by_id[p] for p in probe_ids] if probe_ids else list(PROBES)
    selected_arms = arm_names if arm_names else list(ARMS)
    if not selected_probes:
        raise ValueError("no probes selected")
    if not selected_arms:
        raise ValueError("no arms selected")
    return selected_probes, selected_arms


def run_one(probe, arm):
    """Build an isolated fixture and run one probe in one arm. A timed-out
    engine run fails that probe only, never the whole suite."""
    started = time.monotonic()
    tmp = tempfile.mkdtemp(prefix=f"lr-quality-{probe['id']}-{arm}-")
    try:
        workspace = build_quality_fixture(tmp, arm, NEEDLE_TOPICS, DISTRACTOR_TOPICS,
                                          WORKDIR_FILES)
        try:
            run = run_probe(workspace, probe["task"])
        except subprocess.TimeoutExpired:
            return {
                "probe": probe["id"], "category": probe["category"],
                "difficulty": probe.get("difficulty", ""), "arm": arm,
                "exit_code": 124, "text": "", "tool_inputs": [],
                "artifacts": "",
                "cost_usd": None, "duration_ms": None,
                "wall_duration_s": round(time.monotonic() - started, 3),
                "stderr_tail": "engine run timed out",
            }
        return {
            "probe": probe["id"],
            "category": probe["category"],
            "difficulty": probe.get("difficulty", ""),
            "arm": arm,
            "exit_code": run.exit_code,
            "text": run.text,
            "tool_inputs": run.tool_inputs,
            # captured before the throwaway workspace is deleted; judged
            # alongside the final message (S2/S3) so file-writing runs
            # aren't scored "no code shown".
            "artifacts": collect_workspace_artifacts(workspace),
            "cost_usd": run.cost_usd,
            "duration_ms": run.duration_ms,
            "wall_duration_s": round(time.monotonic() - started, 3),
            "stderr_tail": run.stderr[-500:] if run.stderr else "",
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def score_one(probe, result):
    """Attach per-stage scores to a run result. S3 uses the LLM judge.
    S1 is skipped entirely when the engine exposes no tool trace — an
    unscorable stage must not count as a failure."""
    if result["exit_code"] != 0:
        result["technical_failure"] = True
        result["technical_failure_reason"] = result.get("stderr_tail") or (
            f"engine exited {result['exit_code']}"
        )
        result["stages"] = {}
        return result

    stages = {}
    if "S1" in probe["stages"] and TRACES_TOOLS and result["tool_inputs"] is not None:
        stages["S1"] = int(score_s1_from(result, probe["s1_target"]))
    if "S2" in probe["stages"]:
        stages["S2"] = int(score_s2_from(result, probe["s2_check"]))
    if "S3" in probe["stages"]:
        passed, verdict, judge_meta = judge_s3(
            probe["task"], result["text"], probe["s3_rubric"],
            artifacts=result.get("artifacts", ""),
        )
        result["judge_verdict"] = verdict
        result["judge_cost_usd"] = judge_meta["cost_usd"]
        result["judge_duration_ms"] = judge_meta["duration_ms"]
        result["judge_attempts"] = judge_meta["attempts"]
        result["judge_cost_unavailable_attempts"] = (
            judge_meta["cost_unavailable_attempts"]
        )
        if passed is None:
            result["judge_error"] = True  # invalid, not FAIL — excluded from scoring
        else:
            stages["S3"] = int(passed)
    result["stages"] = stages
    return result


def score_s1_from(result, target):
    """target may be a single filename or a list (synthesis probes) —
    a list passes only if EVERY listed file appears in the tool trace."""
    targets = target if isinstance(target, list) else [target]
    return all(
        any(t in ti for ti in result["tool_inputs"]) for t in targets
    )


def score_s2_from(result, s2_check):
    class _R:  # minimal shim so harness.score_s2 works on stored dicts
        pass
    r = _R()
    # Grounding counts wherever the agent delivered it: final message or a
    # written file. Agents don't edit lore topics, so the artifact capture
    # can't echo needle text back and false-positive this.
    r.text = result["text"] + "\n" + result.get("artifacts", "")
    return score_s2(r, s2_check)


def aggregate(results):
    """Compute LUS per arm, per-stage rates, and behavior uplift."""
    agg = {}
    for arm in ARMS:
        arm_results = [r for r in results if r["arm"] == arm]
        technical_failures = [r for r in arm_results if r.get("technical_failure")]
        scored_results = [r for r in arm_results if not r.get("technical_failure")]
        earned = sum(sum(r["stages"].values()) for r in scored_results)
        possible = sum(len(r["stages"]) for r in scored_results)
        s3 = [r["stages"]["S3"] for r in scored_results if "S3" in r["stages"]]
        agg[arm] = {
            "earned": earned,
            "possible": possible,
            "lus_pct": round(100.0 * earned / possible, 1) if possible else None,
            "s3_pass_rate_pct": round(100.0 * sum(s3) / len(s3), 1) if s3 else None,
            "completed_runs": len(scored_results),
            "technical_failures": len(technical_failures),
            "total_runs": len(arm_results),
        }
    def _delta(key):
        t, c = agg["treatment"][key], agg["control"][key]
        return round(t - c, 1) if t is not None and c is not None else None

    agg["behavior_uplift_pct"] = _delta("s3_pass_rate_pct")
    agg["lus_uplift_pct"] = _delta("lus_pct")
    engine_failures = [
        {
            "type": "engine",
            "probe": r["probe"],
            "arm": r["arm"],
            "exit_code": r["exit_code"],
            "reason": r.get("technical_failure_reason") or r.get("stderr_tail"),
        }
        for r in results if r.get("technical_failure")
    ]
    judge_failures = [
        {
            "type": "judge",
            "probe": r["probe"],
            "arm": r["arm"],
            "exit_code": "judge",
            "reason": r.get("judge_verdict") or "judge call failed",
        }
        for r in results if r.get("judge_error")
    ]
    agg["technical_failures"] = {
        "count": len(engine_failures) + len(judge_failures),
        "engine_count": len(engine_failures),
        "judge_count": len(judge_failures),
        "runs": engine_failures + judge_failures,
    }
    agent_costs = [r["cost_usd"] for r in results if r.get("cost_usd") is not None]
    judge_costs = [
        r["judge_cost_usd"] for r in results if r.get("judge_cost_usd") is not None
    ]
    agent_durations = [
        r["duration_ms"] for r in results if r.get("duration_ms") is not None
    ]
    judge_durations = [
        r["judge_duration_ms"] for r in results
        if r.get("judge_duration_ms") is not None
    ]
    agg["cost"] = {
        "agent_known_usd": round(sum(agent_costs), 6),
        "judge_known_usd": round(sum(judge_costs), 6),
        "total_known_usd": round(sum(agent_costs) + sum(judge_costs), 6),
        "agent_unavailable_runs": sum(
            1 for r in results if r.get("cost_usd") is None
        ),
        "judge_unavailable_calls": sum(
            r.get("judge_cost_unavailable_attempts", 0) for r in results
        ),
    }
    agg["duration"] = {
        "agent_reported_ms": sum(agent_durations) if agent_durations else None,
        "judge_reported_ms": sum(judge_durations) if judge_durations else None,
        "probe_wall_s_sum": round(sum(r.get("wall_duration_s", 0) for r in results), 3),
    }
    return agg


def scorecard(results, agg):
    # Wide enough for the longest v2 probe id (P17-abstention-general-knowledge,
    # 32 chars) plus a gap; widen this if a future probe id runs past it.
    probe_w = max(24, max((len(r["probe"]) for r in results), default=24) + 2)
    rule_w = probe_w + 48
    lines = []
    lines.append("")
    lines.append("=" * rule_w)
    lines.append(
        f"  LORE AGENT QUALITY BENCHMARK — engine={ENGINE} model={MODEL} judge={JUDGE_MODEL}"
    )
    lines.append("=" * rule_w)
    lines.append(f"  {'probe':<{probe_w}}{'arm':<12}{'S1':>4}{'S2':>4}{'S3':>4}   judge")
    lines.append("-" * rule_w)
    for r in sorted(results, key=lambda x: (x["probe"], x["arm"])):
        s = r["stages"]
        if r.get("technical_failure"):
            lines.append(
                f"  {r['probe']:<{probe_w}}{r['arm']:<12}{'TF':>4}{'TF':>4}{'TF':>4}   "
                f"TECH FAIL - {r.get('technical_failure_reason', '')[:40]}"
            )
            continue
        def fmt(k):
            return {1: "  1", 0: "  0"}.get(s.get(k), "  -")
        verdict = r.get("judge_verdict", "")[:40]
        lines.append(
            f"  {r['probe']:<{probe_w}}{r['arm']:<12}{fmt('S1'):>4}{fmt('S2'):>4}{fmt('S3'):>4}   {verdict}"
        )
    lines.append("-" * rule_w)
    for arm in ARMS:
        a = agg[arm]
        lus = f"{a['lus_pct']:>5}%" if a["lus_pct"] is not None else "  n/a"
        s3 = f"{a['s3_pass_rate_pct']}%" if a["s3_pass_rate_pct"] is not None else "n/a"
        lines.append(
            f"  {arm:<12} LUS {lus}  ({a['earned']}/{a['possible']} stage points)"
            f"   S3 pass rate {s3}"
            f"   completed {a['completed_runs']}/{a['total_runs']}"
            f"   tech fails {a['technical_failures']}"
        )
    lines.append("-" * rule_w)
    def _pts(v):
        return f"{v:+.1f} pts" if v is not None else "n/a (judge errors)"
    lines.append(f"  LUS UPLIFT (treatment - control):      {_pts(agg['lus_uplift_pct'])}")
    lines.append(f"  BEHAVIOR UPLIFT (S3 delta, headline):  {_pts(agg['behavior_uplift_pct'])}")
    cost = agg.get("cost", {})
    unavailable = (
        cost.get("agent_unavailable_runs", 0) + cost.get("judge_unavailable_calls", 0)
    )
    lines.append(
        "  known cost: "
        f"${cost.get('total_known_usd', 0):.4f} "
        f"(agent ${cost.get('agent_known_usd', 0):.4f}, "
        f"judge ${cost.get('judge_known_usd', 0):.4f}; "
        f"unavailable cost fields: {unavailable})"
    )
    tf = agg.get("technical_failures", {})
    lines.append(
        "  technical failures: "
        f"{tf.get('count', 0)} "
        f"(engine {tf.get('engine_count', 0)}, judge {tf.get('judge_count', 0)})"
    )
    lines.append("=" * rule_w)
    return "\n".join(lines)


def git_state(repo):
    def run(*args):
        try:
            return subprocess.check_output(
                ["git", "-C", repo] + list(args),
                text=True, stderr=subprocess.DEVNULL,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    sha = run("rev-parse", "HEAD")
    status = run("status", "--porcelain")
    return {"path": repo, "sha": sha, "dirty": bool(status)}


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def iso_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_results(payload, engine, model, stamp):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    model_slug = re.sub(r"[^A-Za-z0-9.-]+", "_", model)
    out = os.path.join(RESULTS_DIR, f"quality-{engine}-{model_slug}-{stamp}.json")
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"  results saved: {out}\n")
    return out


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class QualityBenchmark(unittest.TestCase):

    def test_benchmark(self):
        """Run all probes in both arms, score, print scorecard, save JSON."""
        started_at = iso_now()
        stamp = utc_stamp()
        wall_start = time.monotonic()
        selected_probes, selected_arms = selected_probes_and_arms()
        jobs = [(p, arm) for p in selected_probes for arm in selected_arms]
        with ThreadPoolExecutor(max_workers=JOBS) as pool:
            futures = [pool.submit(run_one, p, arm) for p, arm in jobs]
            results = [f.result() for f in futures]

        failed = [r for r in results if r["exit_code"] != 0]
        agg = None
        by_id = {p["id"]: p for p in PROBES}
        results = [score_one(by_id[r["probe"]], r) for r in results]
        agg = aggregate(results)
        status = "partial" if failed else "ok"
        print(scorecard(results, agg))

        judge_errors = [r for r in results if r.get("judge_error")]
        if judge_errors:
            status = "partial"

        duration_s = round(time.monotonic() - wall_start, 3)
        payload = {
            "schema_version": 2,
            "suite": "quality",
            "status": status,
            "started_at": started_at,
            "ended_at": iso_now(),
            "duration_s": duration_s,
            "command": " ".join(sys.argv),
            "cwd": os.getcwd(),
            "framework": git_state(os.path.abspath(os.environ.get(
                "LR_FRAMEWORK_DIR",
                os.path.join(HERE, "..", "..", "..", "lore-framework"),
            ))),
            "dev_repo": git_state(os.path.abspath(os.path.join(HERE, "..", ".."))),
            "engine": ENGINE,
            "model": MODEL,
            "judge_model": JUDGE_MODEL,
            "quality_jobs": JOBS,
            "probe_filter": [p["id"] for p in selected_probes],
            "arm_filter": selected_arms,
            "aggregate": agg,
            "results": results,
        }
        write_results(payload, ENGINE, MODEL, stamp)

        for arm in selected_arms:
            self.assertGreater(
                agg[arm]["completed_runs"],
                0,
                f"no completed runs for {arm}; technical failures: "
                + ", ".join(
                    f"{r['probe']}/{r['arm']} (exit={r['exit_code']}, {r['stderr_tail']})"
                    for r in failed if r["arm"] == arm
                ),
            )


if __name__ == "__main__":
    unittest.main()
