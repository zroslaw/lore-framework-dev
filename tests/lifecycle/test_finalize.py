#!/usr/bin/env python3
"""Lifecycle scenarios 10-13: reflect, merge, summarize, finalize end-to-end
(catalog: workdir/draft-testing-pipeline.md).

Merge is the framework's highest-risk procedure per its own design notes (a
multi-step lore-integration process explicitly flagged as fidelity-unverified
on non-Claude models) — the most valuable scenario in the catalog to test.

Run:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_finalize.py -v
One:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_finalize.py -v -k 10
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import (
    AGENT_NAME, FINALIZE_PROMPT, FINALIZE_TOOL_CANARY, MERGE_PROMPT, MERGE_TOOL_CANARY,
    REFLECT_PROMPT, REFLECT_TOOL_CANARY, SKIP_REASON, SUMMARIZE_PROMPT, build_fixture,
    grep_agent_dir, head, is_clean, lore_snapshot, reflections_dir, run_engine,
    seed_reflection,
)


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class FinalizeScenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.fx = build_fixture(tmp)

    def test_10_reflect(self):
        """Reflect writes the session's new fact into reflections/, and only there."""
        before = head(self.fx.repo)
        before_lore = lore_snapshot(self.fx)

        r = run_engine(self.fx.workspace, REFLECT_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        rdir = reflections_dir(self.fx)
        self.assertTrue(os.path.isdir(rdir), "reflections/ directory was not created")
        files = [f for f in os.listdir(rdir) if f.endswith(".md")]
        self.assertTrue(files, "no reflection topic files were written")

        found = False
        for f in files:
            with open(os.path.join(rdir, f)) as fh:
                if REFLECT_TOOL_CANARY in fh.read():
                    found = True
        self.assertTrue(found, f"reflected fact missing from reflections/ files: {files}")

        self.assertEqual(head(self.fx.repo), before, "reflect must not create commits")
        self.assertEqual(
            lore_snapshot(self.fx), before_lore,
            "reflect must not touch lore/ directly — only reflections/",
        )

    def test_11_merge(self):
        """Merge integrates a pre-seeded reflection into lore/, then cleans up reflections/."""
        seed_reflection(self.fx, "deploy-tool-swap.md", (
            "# Deploy Tool Swap\n\n"
            f"The fixture project's deployment tool is now **{MERGE_TOOL_CANARY}**. "
            "It replaced the previous tool for faster rollback times.\n"
        ))
        before = head(self.fx.repo)

        r = run_engine(self.fx.workspace, MERGE_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        self.assertTrue(
            grep_agent_dir(self.fx, MERGE_TOOL_CANARY),
            "merged fact not found anywhere in lore/ or lore-context.md after merge",
        )

        rdir = reflections_dir(self.fx)
        leftover = os.listdir(rdir) if os.path.isdir(rdir) else []
        self.assertFalse(leftover, f"reflections/ was not cleaned up after merge: {leftover}")

        self.assertEqual(head(self.fx.repo), before, "merge must not create commits")

    def test_12_summarize(self):
        """Summarize writes a session record with the required frontmatter fields."""
        r = run_engine(self.fx.workspace, SUMMARIZE_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        sessions_dir = os.path.join(self.fx.agent_dir, "sessions")
        summary_files = []
        for root, _dirs, files in os.walk(sessions_dir):
            summary_files += [os.path.join(root, f) for f in files if f.endswith(".md")]
        self.assertTrue(summary_files, "no session summary file was written")

        with open(summary_files[0]) as f:
            content = f.read()
        self.assertIn("uuid:", content, "summary missing uuid frontmatter")
        self.assertIn(f"host_agent: {AGENT_NAME}", content, "summary missing host_agent frontmatter")

    def test_13_finalize_end_to_end(self):
        """Full reflect->merge->summarize->commit->push pipeline in one run."""
        before = head(self.fx.repo)

        r = run_engine(self.fx.workspace, FINALIZE_PROMPT)
        print(f"\n  [{self.id().split('.')[-1]}] {r.summary()}")
        self.assertEqual(r.exit_code, 0, f"engine run failed: {r.stderr[-500:]}")

        after = head(self.fx.repo)
        self.assertNotEqual(after, before, "finalize must create a commit")
        self.assertEqual(
            after, head(self.fx.origin, "main"),
            "finalize must push the commit to origin",
        )
        self.assertTrue(is_clean(self.fx.repo), "working tree must be clean after finalize")

        self.assertTrue(
            grep_agent_dir(self.fx, FINALIZE_TOOL_CANARY),
            "finalized fact not found in lore/ or lore-context.md",
        )

        rdir = reflections_dir(self.fx)
        leftover = os.listdir(rdir) if os.path.isdir(rdir) else []
        self.assertFalse(leftover, f"reflections/ was not cleaned up: {leftover}")

        sessions_dir = os.path.join(self.fx.agent_dir, "sessions")
        summary_files = []
        for root, _dirs, files in os.walk(sessions_dir):
            summary_files += [os.path.join(root, f) for f in files if f.endswith(".md")]
        self.assertTrue(summary_files, "no session summary was written by finalize")


if __name__ == "__main__":
    unittest.main()
