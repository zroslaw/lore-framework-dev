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
        # Assert on the transcript, not the final message: attach prints its
        # report when the attach completes — mid-run, before the recall this
        # scenario also asks for — and the final message carries the recall
        # synthesis. Asserting against `text` made a compliant run (which did
        # print the report) indistinguishable from one that skipped it.
        self.assertIn("Attached: helper-agent —", r.transcript)
        self.assertRegex(
            r.transcript,
            r"Added Context: ~[1-9][0-9]*k tokens total "
            r"· ~[1-9][0-9]*k lore context · ~[1-9][0-9]*k lore map "
            r"· ~[1-9][0-9]*k role",
        )
        self.assertIn(
            HELPER_FACT, r.text,
            f"recall after attach did not surface the guest's fact:\n{r.text}",
        )


if __name__ == "__main__":
    unittest.main()
