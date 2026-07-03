#!/usr/bin/env python3
"""Lifecycle scenarios 8-9: consult, attach (catalog: workdir/draft-testing-pipeline.md).

Both use a fixture with a second agent ("helper-agent") in the same repo so the
host has somewhere to reach across to.

Run:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_consult_attach.py -v
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import ATTACH_PROMPT, CONSULT_PROMPT, HELPER_FACT, SKIP_REASON, build_fixture, run_engine


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class ConsultAttachScenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.fx = build_fixture(tmp, second_agent=True)

    def test_08_consult(self):
        """Consult gets a focused answer from an unloaded agent's lore."""
        r = run_engine(self.fx.workspace, CONSULT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertIn(
            HELPER_FACT, r.text,
            f"consult did not surface helper-agent's fact:\n{r.text}",
        )

    def test_09_attach(self):
        """Attach loads a guest; recall afterwards covers both agents' lore."""
        r = run_engine(self.fx.workspace, ATTACH_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")
        self.assertIn(
            HELPER_FACT, r.text,
            f"recall after attach did not surface the guest's fact:\n{r.text}",
        )


if __name__ == "__main__":
    unittest.main()
