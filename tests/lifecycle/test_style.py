#!/usr/bin/env python3
"""Lifecycle scenario 30: the unified lr:style selector.

Exercises a replacement transition: all components first, then dialogue + follow only. The final
confirmation is specified by docs/style.md, and the constrained reply checks that the resulting
turn stays short and collaborative rather than producing an article.

Run: LR_LIFECYCLE=1 python3 tests/lifecycle/test_style.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import SKIP_REASON, STYLE_PROMPT, build_empty_workspace, run_engine


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class StyleScenarios(unittest.TestCase):

    def test_30_style_replaces_the_active_component_set(self):
        workspace = build_empty_workspace(self._tmpdir())
        result = run_engine(workspace, STYLE_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {result.summary()}")
        self.assertEqual(result.exit_code, 0, f"engine run failed: {result.stderr[-500:]}")
        self.assertIn("Style set: dialogue and follow.", result.text)
        reply = result.text.split("STYLE-REPLY:", 1)[-1].strip()
        self.assertTrue(reply, f"missing STYLE-REPLY marker:\n{result.text}")
        self.assertLessEqual(len(reply.splitlines()), 2, f"dialogue reply was too long:\n{reply}")
        self.assertIn("?", reply, f"follow component did not leave direction with the user:\n{reply}")

    def _tmpdir(self):
        import shutil
        import tempfile

        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        return tmp


if __name__ == "__main__":
    unittest.main()
