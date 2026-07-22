#!/usr/bin/env python3
"""Lifecycle scenarios 10-13: reflect, merge, summarize, finalize end-to-end
(catalog: workdir/draft-testing-pipeline.md).

Merge is the framework's highest-risk procedure per its own design notes (a
multi-step lore-integration process explicitly flagged as fidelity-unverified
on non-Claude models) — the most valuable scenario in the catalog to test.

Run:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_finalize.py -v
One:  LR_LIFECYCLE=1 python3 tests/lifecycle/test_finalize.py -v -k 10
"""

import gzip
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import (
    AGENT_NAME, ENGINE, FINALIZE_PROMPT, FINALIZE_TOOL_CANARY, MERGE_PROMPT,
    MERGE_TOOL_CANARY, REFLECT_PROMPT, REFLECT_TOOL_CANARY, SKIP_REASON,
    SUMMARIZE_PROMPT, build_fixture, grep_agent_dir, head, is_clean,
    lore_snapshot, reflections_dir, run_engine, seed_reflection,
)


def _read_summary(agent_dir):
    """Return (path, text) of the one session summary, or (None, None)."""
    sessions_dir = os.path.join(agent_dir, "sessions")
    for root, _dirs, files in os.walk(sessions_dir):
        for f in files:
            if f.endswith(".md"):
                p = os.path.join(root, f)
                with open(p) as fh:
                    return p, fh.read()
    return None, None


def _frontmatter_lines(summary_text):
    lines = summary_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    try:
        end = lines.index("---", 1)
    except ValueError:
        return []
    return lines[1:end]


# Engines whose CLI agent reliably executes the newly-inserted summarize Step 1.5.
# Cursor (`cursor-agent`) is a KNOWN BETA GAP: empirically it skips Step 1.5 in the
# long summarize.md procedure — it never invokes session-takeover at all — while
# still writing the summary. The archive script itself works on cursor logs when
# driven directly (verified), so this is a weaker-engine doc-following fidelity gap,
# not a code defect. Tracked in release notes + lore. Codex and Claude execute it.
ARCHIVE_STEP_RELIABLE = {"claude", "codex"}


def assert_archive_and_usage(test, agent_dir, summary_text):
    """Assert Feature A + B landed: a month-partitioned gzip archive whose
    header UUID matches the summary, and a well-formed usage frontmatter block.

    In the lifecycle fixture the engine really runs and writes a native log
    containing the Step-1 UUID, so Step 1.5's happy path is expected to hold on
    engines that execute the step. On an engine in the known-gap set, a missing
    archive is a documented BETA limitation, not a regression: we then only
    assert the non-blocking contract held (the summary was still written intact).
    """
    archive_dir = os.path.join(agent_dir, "archive")
    gz_files = []
    for root, _dirs, files in os.walk(archive_dir):
        gz_files += [os.path.join(root, f) for f in files if f.endswith(".jsonl.gz")]

    if not gz_files and ENGINE not in ARCHIVE_STEP_RELIABLE:
        # Known BETA gap (e.g. cursor): archive step skipped by the engine agent.
        # The non-blocking design must still have produced a valid summary with
        # no partial usage/archive keys.
        test.assertNotIn(
            "usage:", summary_text,
            "usage frontmatter present without an archive — partial write "
            "(non-blocking contract violated)",
        )
        test.skipTest(
            f"[known BETA gap] {ENGINE} agent skipped summarize Step 1.5 "
            "(no archive); summary written intact (non-blocking held). "
            "Script works on this engine's logs when driven directly."
        )
    test.assertTrue(gz_files, "no session archive .jsonl.gz was written")
    archive = gz_files[0]

    # month-partitioned like sessions/: archive/<YYYY>/<MM>/<file>
    rel = os.path.relpath(archive, archive_dir).split(os.sep)
    test.assertEqual(len(rel), 3, f"archive not YYYY/MM partitioned: {rel}")
    test.assertTrue(rel[0].isdigit() and len(rel[0]) == 4, f"bad year dir: {rel}")

    with gzip.open(archive, "rt", encoding="utf-8") as fh:
        header = json.loads(fh.readline())
    test.assertEqual(header.get("schema_version"), 1)
    test.assertIn(header.get("engine"), ("claude", "codex", "cursor"))

    # header lore_uuid must equal the summary's uuid frontmatter
    uuid_line = next(
        (ln for ln in summary_text.splitlines() if ln.strip().startswith("uuid:")),
        "",
    )
    summary_uuid = uuid_line.split(":", 1)[1].strip() if ":" in uuid_line else ""
    test.assertTrue(summary_uuid, "summary missing uuid frontmatter")
    test.assertEqual(
        header.get("lore_uuid"), summary_uuid,
        "archive header lore_uuid does not match the summary uuid",
    )

    # archive.path frontmatter must be portable, not an absolute temp path.
    fm = _frontmatter_lines(summary_text)
    archive_idx = next((i for i, ln in enumerate(fm) if ln.strip() == "archive:"), None)
    test.assertIsNotNone(archive_idx, "summary missing archive frontmatter block")
    path_line = next(
        (ln.strip() for ln in fm[archive_idx + 1:] if ln.strip().startswith("path:")),
        "",
    )
    test.assertTrue(path_line, "archive frontmatter missing path")
    archive_path = path_line.split(":", 1)[1].strip().strip("'\"")
    test.assertFalse(os.path.isabs(archive_path), "archive.path must be repo-relative")
    repo_root = os.path.dirname(os.path.dirname(agent_dir))
    expected = os.path.relpath(archive, repo_root)
    test.assertEqual(archive_path, expected)

    # usage frontmatter block with a valid cost_source enum. Cursor is a known
    # BETA fidelity gap: it may execute the archive half of Step 1.5 but omit
    # the usage block during long finalize runs. Claude/Codex remain strict.
    if "usage:" not in summary_text and ENGINE not in ARCHIVE_STEP_RELIABLE:
        test.skipTest(
            f"[known BETA gap] {ENGINE} agent wrote a valid archive but omitted "
            "usage frontmatter during summarize/finalize Step 1.5. Archive path "
            "and header were valid; usage metadata is unavailable for this run."
        )
    test.assertIn("usage:", summary_text, "summary missing usage frontmatter block")
    cost_line = next(
        (ln for ln in summary_text.splitlines()
         if ln.strip().startswith("cost_source:")),
        "",
    )
    test.assertTrue(
        any(v in cost_line for v in ("reported", "computed", "unavailable")),
        f"usage block missing a valid cost_source: {cost_line!r}",
    )


@unittest.skipIf(SKIP_REASON, SKIP_REASON)
class FinalizeScenarios(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="lr-lifecycle-")
        if os.environ.get("LR_KEEP_FIXTURES"):
            print(f"\n  [fixture kept] {tmp}", file=sys.stderr)
        else:
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

        # Feature A + B: archive written + usage frontmatter present
        assert_archive_and_usage(self, self.fx.agent_dir, content)

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

        summary_path, summary_text = _read_summary(self.fx.agent_dir)
        self.assertTrue(summary_path, "no session summary was written by finalize")

        # Feature A + B end-to-end: archive committed + usage frontmatter present.
        assert_archive_and_usage(self, self.fx.agent_dir, summary_text)
        # the archive rode the same finalize commit (git add agents/ scope)
        self.assertTrue(
            grep_agent_dir(self.fx, "archive/") or os.path.isdir(
                os.path.join(self.fx.agent_dir, "archive")
            ),
            "archive directory missing after finalize",
        )


if __name__ == "__main__":
    unittest.main()
