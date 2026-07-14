#!/usr/bin/env python3
"""Lifecycle scenario: Cursor session takeover via /lr:takeover.

Run:  LR_LIFECYCLE=1 LR_ENGINE=claude LR_TEST_MODEL=haiku \\
        python3 tests/lifecycle/test_takeover.py -v
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
from harness import (
    BUILD_TOOL_FACT,
    SKIP_REASON,
    TAKEOVER_CURSOR_FACT,
    build_cursor_takeover_paths,
    build_fixture,
    run_engine,
    takeover_cursor_prompt,
)


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class TakeoverScenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-takeover-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.fx = build_fixture(tmp)
        self.cursor_home, self.jsonl_path, self.digest_path = (
            build_cursor_takeover_paths(tmp, self.fx.workspace)
        )
        os.environ["CURSOR_HOME"] = self.cursor_home
        self.addCleanup(lambda: os.environ.pop("CURSOR_HOME", None))

    def test_01_cursor_takeover_direct_haiku(self):
        """Haiku reads takeover.md, converts Cursor JSONL fixture, reports facts."""
        prompt = takeover_cursor_prompt(self.jsonl_path, self.digest_path)
        r = run_engine(self.fx.workspace, prompt)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-800:]}")
        self.assertIn("TAKEOVER-OK", r.text, f"takeover not confirmed:\n{r.text[-2000:]}")
        self.assertIn(
            TAKEOVER_CURSOR_FACT,
            r.text,
            f"recall fact missing (expected {TAKEOVER_CURSOR_FACT}):\n{r.text[-2000:]}",
        )
        self.assertIn("3/3", r.text, f"tool pairing line missing:\n{r.text[-2000:]}")
        self.assertTrue(
            os.path.isfile(self.digest_path),
            "session-takeover digest file was not written",
        )
        with open(self.digest_path) as fh:
            digest = fh.read()
        self.assertIn(BUILD_TOOL_FACT, digest)
        self.assertIn("tool_results_paired", digest)


if __name__ == "__main__":
    unittest.main()
