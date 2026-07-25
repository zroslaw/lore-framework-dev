#!/usr/bin/env python3
"""Lifecycle scenarios 28-29: /lr:trilens-loop three-lens review loop.

Both scenarios plant an uncommitted lore topic carrying a dangling cross-reference, then ask the
engine to run one round of trilens-loop over the session's changes. Scenario 28 allows fixes and
asserts the target file was edited; scenario 29 amends the flow to report-only and asserts the file
was left byte-identical — a filesystem check of the free-text rail rather than a self-report.

Both are bounded to a single round on purpose: multi-round convergence on a fixture is expensive
and non-deterministic, while the spine under test (scope resolution -> lens choice -> independent
subagent spawn -> triage -> fix-or-not) is fully exercised by one round.

Run:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_trilens_loop.py -v
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import (
    REVIEW_DEFECT_CANARY,
    SKIP_REASON,
    TRILENS_PROMPT,
    TRILENS_REPORT_ONLY_PROMPT,
    build_fixture,
    plant_reviewable_change,
    run_engine,
)


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class TrilensLoopScenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.fx = build_fixture(tmp)
        self.target = plant_reviewable_change(self.fx)
        with open(self.target) as f:
            self.before = f.read()

    def _target_now(self):
        with open(self.target) as f:
            return f.read()

    def _assert_three_lenses(self, text):
        """The LENSES: line must name three distinct lenses, not one or a placeholder."""
        lines = [ln for ln in text.splitlines() if ln.strip().startswith("LENSES:")]
        self.assertTrue(lines, f"no LENSES: line in output:\n{text}")
        lenses = [p.strip() for p in lines[-1].split(":", 1)[1].split("|") if p.strip()]
        self.assertGreaterEqual(
            len(lenses), 3,
            f"expected three lenses, got {lenses!r} from line {lines[-1]!r}",
        )
        self.assertEqual(
            len(lenses), len(set(l.lower() for l in lenses)),
            f"lenses must be distinct, got {lenses!r}",
        )

    def test_28_trilens_loop_single_round_finds_and_fixes(self):
        """One round with fixes: three lenses chosen, planted dangling ref found, target edited."""
        r = run_engine(self.fx.workspace, TRILENS_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertIn("TRILENS-DONE", r.text, f"skill did not run to completion:\n{r.text}")
        self._assert_three_lenses(r.text)
        self.assertIn(
            REVIEW_DEFECT_CANARY, r.text,
            f"reviewers did not surface the planted dangling reference:\n{r.text}",
        )
        self.assertNotEqual(
            self.before, self._target_now(),
            "fixes were allowed but the review target was never edited",
        )

    def test_29_trilens_loop_report_only_makes_no_edits(self):
        """Report-only amendment: finding still surfaced, but no file is touched."""
        r = run_engine(self.fx.workspace, TRILENS_REPORT_ONLY_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertIn("TRILENS-DONE", r.text, f"skill did not run to completion:\n{r.text}")
        self.assertIn(
            REVIEW_DEFECT_CANARY, r.text,
            f"reviewers did not surface the planted dangling reference:\n{r.text}",
        )
        self.assertEqual(
            self.before, self._target_now(),
            "report-only was requested but the review target was modified",
        )


if __name__ == "__main__":
    unittest.main()
