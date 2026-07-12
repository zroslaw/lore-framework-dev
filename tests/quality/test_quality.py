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

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import (
    ENGINE, JOBS, JUDGE_MODEL, MODEL, SKIP_REASON, TRACES_TOOLS,
    build_quality_fixture, collect_workspace_artifacts, judge_s3, run_probe,
    score_s2,
)
from probes import DISTRACTOR_TOPICS, NEEDLE_TOPICS, PROBES, WORKDIR_FILES

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

ARMS = ["treatment", "control"]


def run_one(probe, arm):
    """Build an isolated fixture and run one probe in one arm. A timed-out
    engine run fails that probe only, never the whole suite."""
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
            "stderr_tail": run.stderr[-500:] if run.stderr else "",
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def score_one(probe, result):
    """Attach per-stage scores to a run result. S3 uses the LLM judge.
    S1 is skipped entirely when the engine exposes no tool trace — an
    unscorable stage must not count as a failure."""
    stages = {}
    if "S1" in probe["stages"] and TRACES_TOOLS and result["tool_inputs"] is not None:
        stages["S1"] = int(score_s1_from(result, probe["s1_target"]))
    if "S2" in probe["stages"]:
        stages["S2"] = int(score_s2_from(result, probe["s2_check"]))
    if "S3" in probe["stages"]:
        passed, verdict = judge_s3(probe["task"], result["text"], probe["s3_rubric"],
                                   artifacts=result.get("artifacts", ""))
        result["judge_verdict"] = verdict
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
        earned = sum(sum(r["stages"].values()) for r in arm_results)
        possible = sum(len(r["stages"]) for r in arm_results)
        s3 = [r["stages"]["S3"] for r in arm_results if "S3" in r["stages"]]
        agg[arm] = {
            "earned": earned,
            "possible": possible,
            "lus_pct": round(100.0 * earned / possible, 1) if possible else None,
            "s3_pass_rate_pct": round(100.0 * sum(s3) / len(s3), 1) if s3 else None,
        }
    def _delta(key):
        t, c = agg["treatment"][key], agg["control"][key]
        return round(t - c, 1) if t is not None and c is not None else None

    agg["behavior_uplift_pct"] = _delta("s3_pass_rate_pct")
    agg["lus_uplift_pct"] = _delta("lus_pct")
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
        def fmt(k):
            return {1: "  1", 0: "  0"}.get(s.get(k), "  -")
        verdict = r.get("judge_verdict", "")[:40]
        lines.append(
            f"  {r['probe']:<{probe_w}}{r['arm']:<12}{fmt('S1'):>4}{fmt('S2'):>4}{fmt('S3'):>4}   {verdict}"
        )
    lines.append("-" * rule_w)
    for arm in ARMS:
        a = agg[arm]
        lines.append(
            f"  {arm:<12} LUS {a['lus_pct']:>5}%  ({a['earned']}/{a['possible']} stage points)"
            f"   S3 pass rate {a['s3_pass_rate_pct']}%"
        )
    lines.append("-" * rule_w)
    def _pts(v):
        return f"{v:+.1f} pts" if v is not None else "n/a (judge errors)"
    lines.append(f"  LUS UPLIFT (treatment - control):      {_pts(agg['lus_uplift_pct'])}")
    lines.append(f"  BEHAVIOR UPLIFT (S3 delta, headline):  {_pts(agg['behavior_uplift_pct'])}")
    total_cost = sum(r["cost_usd"] or 0 for r in results)
    lines.append(f"  total engine cost: ${total_cost:.2f}")
    lines.append("=" * rule_w)
    return "\n".join(lines)


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class QualityBenchmark(unittest.TestCase):

    def test_benchmark(self):
        """Run all probes in both arms, score, print scorecard, save JSON."""
        jobs = [(p, arm) for p in PROBES for arm in ARMS]
        with ThreadPoolExecutor(max_workers=JOBS) as pool:
            futures = [pool.submit(run_one, p, arm) for p, arm in jobs]
            results = [f.result() for f in futures]

        failed = [r for r in results if r["exit_code"] != 0]
        self.assertFalse(
            failed,
            "engine runs failed: " + ", ".join(
                f"{r['probe']}/{r['arm']} (exit={r['exit_code']}, {r['stderr_tail']})"
                for r in failed
            ),
        )

        by_id = {p["id"]: p for p in PROBES}
        results = [score_one(by_id[r["probe"]], r) for r in results]
        agg = aggregate(results)
        print(scorecard(results, agg))

        os.makedirs(RESULTS_DIR, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        model_slug = re.sub(r"[^A-Za-z0-9.-]+", "_", MODEL)
        out = os.path.join(RESULTS_DIR, f"quality-{ENGINE}-{model_slug}-{stamp}.json")
        with open(out, "w") as f:
            json.dump(
                {"engine": ENGINE, "model": MODEL, "judge_model": JUDGE_MODEL,
                 "aggregate": agg, "results": results},
                f, indent=2,
            )
        print(f"  results saved: {out}\n")

        self.assertIsNotNone(agg["treatment"]["lus_pct"])
        self.assertIsNotNone(agg["control"]["lus_pct"])

        judge_errors = [r for r in results if r.get("judge_error")]
        self.assertFalse(
            judge_errors,
            "judge calls failed (scores above exclude them, S3 shown as '-'): "
            + ", ".join(f"{r['probe']}/{r['arm']}" for r in judge_errors),
        )


if __name__ == "__main__":
    unittest.main()
