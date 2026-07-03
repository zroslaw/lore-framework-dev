#!/usr/bin/env python3
"""Lifecycle scenario 7: recall with hint (catalog: workdir/draft-testing-pipeline.md).

Run:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_recall.py -v
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import BUILD_TOOL_FACT, RECALL_PROMPT, SKIP_REASON, build_fixture, run_engine


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class RecallScenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.fx = build_fixture(tmp)

    def test_07_recall_with_hint(self):
        """Recall with hint "build tool" surfaces the known fixture fact, not a hallucination."""
        r = run_engine(self.fx.workspace, RECALL_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertIn(
            BUILD_TOOL_FACT, r.text,
            f"recall did not surface the fixture build-tool fact:\n{r.text}",
        )


if __name__ == "__main__":
    unittest.main()
