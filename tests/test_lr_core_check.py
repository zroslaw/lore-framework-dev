#!/usr/bin/env python3
"""Unified health checks, using disposable repos and an injected upstream response."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

FRAMEWORK = Path(os.environ.get('LR_FRAMEWORK_DIR', Path(__file__).resolve().parents[2] / 'lore-framework'))
sys.path.insert(0, str(FRAMEWORK / 'scripts'))
from lr_core.check import run_check
from lr_core.freshness import MAX_AGE, read_stamp, repo_freshness, stamp_path, write_stamp
from lr_core.plugin_scan import migration_issues, scan_plugin
from lr_core.repo_scan import bootstrap_template, check_shortcuts, scan_repos
from lr_core.workspace_scan import scan_children


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.ws = self.root / 'workspace'
        self.ws.mkdir()
        self.env = patch.dict(os.environ, {'HOME': str(self.root / 'home'),
            'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_SYSTEM': os.devnull,
            'GIT_AUTHOR_NAME': 'Test', 'GIT_COMMITTER_NAME': 'Test',
            'GIT_AUTHOR_EMAIL': 'test@example.com', 'GIT_COMMITTER_EMAIL': 'test@example.com'})
        self.env.start(); self.addCleanup(self.env.stop)

    def repo(self, name='agents', lore=True):
        path = self.ws / name
        path.mkdir(exist_ok=True)
        git(path, 'init', '-q')
        if lore:
            put(path / 'lore-repo.md', '---\ndescription: Example\nversion: "44"\n---\n')
        return path

    def agent(self, repo=None, name='test-agent'):
        repo = repo or self.repo()
        path = repo / 'agents' / name
        put(path / 'role.md', '---\ndescription: Test role\n---\n# Test Agent\n')
        put(path / 'lore-context.md', '---\nlore: 1\ntype: context\nsummary: Test context\n---\n# Context\n')
        (path / 'lore').mkdir(); (path / 'workdir').mkdir()
        return path

    def shortcut(self, agent, engine='codex', home=False, name='test-agent'):
        target = str(agent) if home else str(agent.relative_to(self.ws))
        body = bootstrap_template(str(FRAMEWORK), engine).replace('<agent-name>', name).replace('<agent-dir-rel>', target).replace('<agent-dir>', target)
        if engine == 'claude':
            path = self.ws / '.claude/commands' / ('lr-%s-agent.md' % name)
            text = body + '\n'
        else:
            base = Path.home() if home else self.ws
            path = base / ('.%s/skills/lr-%s-agent/SKILL.md' % (engine, name))
            text = '---\nname: lr-%s-agent\ndescription: Test\n' % name
            if engine == 'cursor': text += 'disable-model-invocation: true\npaths:\n  - "agents/**"\n'
            text += '---\n\n' + body + '\n'
        put(path, text)
        return path

    def check(self, **kw):
        return run_check(str(self.ws), str(FRAMEWORK), engine='codex', no_network=True, **kw)

    def test_states_and_scope(self):
        self.assertEqual(self.check()[0]['state'], 1)
        self.repo()
        data, _ = self.check()
        self.assertEqual(data['state'], 2)
        self.assertTrue(all(f['collapsed'] for f in data['findings'] if f['id'] == 'S10'))
        put(self.ws / 'lore-workspace.md', '---\ndescription: Workspace\n---\n')
        self.assertEqual(self.check()[0]['state'], 3)
        data, _ = self.check(scope='workspace')
        self.assertIsNone(data['plugin'])
        self.assertFalse(any(f['id'].startswith('P') for f in data['findings']))

    def test_wrong_directory_context_does_not_scan_parent(self):
        agent = self.agent()
        put(self.ws / 'lore-workspace.md', '---\ndescription: Workspace\n---\n')
        data, _ = run_check(str(agent), str(FRAMEWORK), 'codex', True)
        self.assertEqual(data['state'], 1)
        self.assertEqual(data['context']['workspace_root'], str(self.ws))
        self.assertEqual(data['repos'], [])
        data, _ = run_check(str(self.root), str(FRAMEWORK), 'codex', True)
        self.assertEqual(data['context']['case'], '1d')
        self.assertEqual(data['context']['workspace_roots'], [str(self.ws)])

    def test_exact_normalized_and_different_shortcut_names(self):
        agent = self.agent()
        for engine in ('codex', 'cursor', 'claude'):
            self.shortcut(agent, engine)
        findings, warnings = [], []
        check_shortcuts(str(self.ws), str(FRAMEWORK), findings, warnings)
        self.assertEqual(findings, [])
        self.assertEqual(warnings, [])
        put(agent / 'role.md', '---\ndescription: Another\n---\n# Different Name\n')
        check_shortcuts(str(self.ws), str(FRAMEWORK), findings, warnings)
        self.assertEqual(len([f for f in findings if f['id'] == 'R15']), 3)

    def test_home_absolute_target_valid_foreign_ignored(self):
        agent = self.agent()
        self.shortcut(agent, home=True)
        findings, warnings = [], []
        check_shortcuts(str(self.ws), str(FRAMEWORK), findings, warnings)
        self.assertFalse(any(f['id'] == 'R12' for f in findings))
        foreign = self.root / 'foreign'
        foreign.mkdir()
        self.shortcut(foreign, home=True, name='foreign')
        check_shortcuts(str(self.ws), str(FRAMEWORK), findings, warnings)
        self.assertFalse(any('foreign' in str(f) for f in findings))

    def test_workspace_absolute_and_missing_target(self):
        agent = self.agent()
        path = self.shortcut(agent)
        path.write_text(path.read_text().replace(str(agent.relative_to(self.ws)), str(agent)))
        findings, warnings = [], []
        check_shortcuts(str(self.ws), str(FRAMEWORK), findings, warnings)
        self.assertIn('R12', [f['id'] for f in findings])
        path.write_text(path.read_text().replace(str(agent), 'missing/agents/test-agent'))
        findings.clear()
        check_shortcuts(str(self.ws), str(FRAMEWORK), findings, warnings)
        self.assertIn('R11', [f['id'] for f in findings])
        self.assertNotIn('R15', [f['id'] for f in findings])

    def test_duplicate_agent_names_use_target_identity(self):
        first = self.agent(self.repo('first'))
        second = self.agent(self.repo('second'))
        self.shortcut(first)
        data, _ = self.check(scope='repos')
        unregistered = [f['data']['repo'] for f in data['findings'] if f['id'] == 'R10']
        self.assertEqual(unregistered, ['second'])

    def test_missing_role_directory_is_not_silently_skipped(self):
        agent = self.agent()
        (agent / 'role.md').unlink()
        data, _ = self.check(scope='repos')
        rows = [f for f in data['findings'] if f['id'] == 'R5']
        self.assertEqual(rows[0]['data']['missing'], ['role.md'])

    def test_freshness_boundary_unknown_and_future(self):
        repo = self.repo()
        path = Path(stamp_path(str(repo)))
        now = 200000
        for value, status in ((str(now-MAX_AGE), 'recent'), (str(now-MAX_AGE-1), 'stale'),
                              ('nan', 'unknown'), ('inf', 'unknown'), ('broken', 'unknown'),
                              (str(now+1), 'unknown')):
            path.write_text(value)
            self.assertEqual(repo_freshness(str(repo), now)['status'], status)
        path.unlink()
        self.assertEqual(repo_freshness(str(repo), now)['status'], 'unknown')

    def test_freshness_per_repo_no_remote_exempt_and_check_read_only(self):
        stale = self.repo('stale', False)
        recent = self.repo('recent', False)
        self.repo('local')
        for repo in (stale, recent): git(repo, 'remote', 'add', 'origin', str(self.root / 'unused'))
        Path(stamp_path(str(stale))).write_text('1')
        Path(stamp_path(str(recent))).write_text('199999')
        before = Path(stamp_path(str(stale))).read_bytes()
        data, _ = self.check(now=200000, scope='workspace')
        rows = [f for f in data['findings'] if f['id'] == 'S19']
        self.assertEqual([f['data']['repo'] for f in rows], [str(stale)])
        self.assertEqual(Path(stamp_path(str(stale))).read_bytes(), before)

    def test_marker_write_failure_preserves_previous(self):
        repo = self.repo()
        self.assertIsNone(write_stamp(str(repo)))
        previous = read_stamp(str(repo))
        with patch('lr_core.freshness.os.replace', side_effect=OSError('denied')):
            self.assertIn('denied', write_stamp(str(repo)))
        self.assertEqual(read_stamp(str(repo)), previous)

    def test_git_directory_file_in_worktree(self):
        repo = self.repo()
        git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'initial')
        tree = self.root / 'worktree'
        git(repo, 'worktree', 'add', '-qb', 'feature', str(tree))
        self.assertTrue((tree / '.git').is_file())
        self.assertIsNone(write_stamp(str(tree)))
        self.assertEqual(repo_freshness(str(tree))['status'], 'recent')
        self.assertIsNone(read_stamp(str(repo)))

    def test_migration_grammar(self):
        for body in ('(none)', '(none) — no writes', '', '# comment', 'agents/**/*.md # comment'):
            self.assertEqual(migration_issues('## Write Paths\n\n```\n'+body+'\n```\n'), [])
        self.assertEqual(migration_issues('## Write Paths\nplain prose'), ['missing_fence'])
        self.assertEqual(migration_issues('nothing'), ['missing_section'])
        self.assertTrue(migration_issues('## Write Paths\n```\ntwo words\n```'))

    def test_plugin_probe_injected_and_skip(self):
        with patch('lr_core.plugin_scan.run', return_value=(0, 'hash\trefs/tags/lr--v1.999.0\n', '')) as probe:
            data, rows, _ = scan_plugin(str(FRAMEWORK), 'codex', home=str(Path.home()))
            self.assertEqual(data['latest_version'], 999)
            self.assertIn('P1', [f['id'] for f in rows])
            self.assertEqual(probe.call_args.kwargs['timeout'], 15)
        with patch('lr_core.plugin_scan.run') as probe:
            data, _, _ = scan_plugin(str(FRAMEWORK), 'codex', True, str(Path.home()))
            probe.assert_not_called()
            self.assertEqual(data['upstream'], 'skipped')
        with patch('lr_core.plugin_scan.run', return_value=(None, '', 'offline')):
            data, rows, _ = scan_plugin(str(FRAMEWORK), 'codex', home=str(Path.home()))
            self.assertEqual(data['upstream'], 'unknown')
            self.assertNotIn('P1', [f['id'] for f in rows])

    def test_workspace_pull_stamps_success_but_not_failure(self):
        bare = self.root / 'origin.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(bare)], check=True)
        repo = self.repo('good')
        git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'initial')
        git(repo, 'remote', 'add', 'origin', str(bare)); git(repo, 'push', '-qu', 'origin', 'HEAD')
        bad = self.repo('bad', False)
        git(bad, 'remote', 'add', 'origin', str(self.root / 'missing'))
        out = subprocess.run(['bash', str(FRAMEWORK / 'scripts/workspace-pull'), str(self.ws)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
        self.assertIsNotNone(read_stamp(str(repo)))
        self.assertIsNone(read_stamp(str(bad)))

    def test_lore_validator_and_uncommitted_work_are_reported(self):
        agent = self.agent()
        put(agent / 'lore-context.md', '---\nlore: 1\ntype: context\nsummary: Test\n---\n# Context\n[broken](lore/missing.md)\n')
        put(agent / 'lore/topic.md', '---\nlore: 1\ntype: topic\nsummary: Topic\nparent: lore-context.md\n---\n# Topic\n')
        put(agent / 'reflections/pending.md', '# Pending\n')
        data, _ = self.check(scope='repos')
        ids = {f['id'] for f in data['findings']}
        self.assertTrue({'R6', 'R7', 'R8'}.issubset(ids))
        self.assertEqual(data['semantic_review'], 'not_run')
        visible = [f for f in data['findings'] if not f['collapsed']]
        self.assertEqual(sum(row['total'] for row in data['summary'].values()), len(visible))

    def test_newer_topic_is_a_staleness_hint(self):
        repo = self.repo()
        agent = self.agent(repo)
        git(repo, 'add', '.')
        with patch.dict(os.environ, {'GIT_AUTHOR_DATE': '2026-01-01T00:00:00Z',
                                     'GIT_COMMITTER_DATE': '2026-01-01T00:00:00Z'}):
            git(repo, 'commit', '-qm', 'context')
        put(agent / 'lore/topic.md', '# Topic\n')
        git(repo, 'add', '.')
        with patch.dict(os.environ, {'GIT_AUTHOR_DATE': '2026-01-02T00:00:00Z',
                                     'GIT_COMMITTER_DATE': '2026-01-02T00:00:00Z'}):
            git(repo, 'commit', '-qm', 'topic')
        data, _ = self.check(scope='repos')
        self.assertTrue(any(f['id'] == 'R9' for f in data['findings']))

    def test_cache_inventory_requires_plugin_identity(self):
        home = Path.home()
        tree = home / '.codex/plugins/cache/test/lr/1.999.0'
        put(tree / 'VERSION', '999')
        put(tree / '.codex-plugin/plugin.json', '{"name":"other"}')
        _, rows, _ = scan_plugin(str(FRAMEWORK), 'codex', True, str(home))
        self.assertNotIn('P2', [f['id'] for f in rows])
        put(tree / '.codex-plugin/plugin.json', '{"name":"lr"}')
        _, rows, _ = scan_plugin(str(FRAMEWORK), 'codex', True, str(home))
        self.assertIn('P2', [f['id'] for f in rows])
        old = home / '.codex/.tmp/marketplaces/old'
        put(old / 'VERSION', '1')
        put(old / '.codex-plugin/plugin.json', '{"name":"lr"}')
        _, rows, _ = scan_plugin(str(FRAMEWORK), 'codex', True, str(home))
        self.assertIn('P5', [f['id'] for f in rows])

    def test_plugin_manifest_and_wrapper_corruption(self):
        copy = self.root / 'plugin'
        shutil.copytree(FRAMEWORK, copy, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        (copy / '.claude-plugin/marketplace.json').unlink()
        (copy / '.codex-plugin/plugin.json').unlink()
        _, rows, _ = scan_plugin(str(copy), 'codex', True, str(Path.home()))
        self.assertNotIn('P4', [f['id'] for f in rows])
        put(copy / '.cursor-plugin/plugin.json', '{"version":"1.0.0"}')
        (copy / '.cursor-skills/lr-boot/SKILL.md').unlink()
        put(copy / 'migrations/999.md', '## Write Paths\n```\ninvalid prose here\n```')
        _, rows, _ = scan_plugin(str(copy), 'codex', True, str(Path.home()))
        self.assertTrue({'P4','P6','P7'}.issubset({f['id'] for f in rows}))

    def test_clone_and_root_pull_record_success(self):
        origin = self.root / 'origin.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(origin)], check=True)
        source = self.root / 'source'
        source.mkdir(); git(source, 'init', '-q')
        put(source / 'README.md', 'fixture')
        git(source, 'add', '.'); git(source, 'commit', '-qm', 'initial')
        git(source, 'remote', 'add', 'origin', str(origin)); git(source, 'push', '-qu', 'origin', 'HEAD')
        git(self.ws, 'init', '-q')
        put(self.ws / 'lore-workspace.md', '---\ndescription: Test\nrepos:\n  - '+str(origin)+'\n---\n')
        git(self.ws, 'add', '.'); git(self.ws, 'commit', '-qm', 'workspace')
        root_origin = self.root / 'root-origin.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(root_origin)], check=True)
        git(self.ws, 'remote', 'add', 'origin', str(root_origin)); git(self.ws, 'push', '-qu', 'origin', 'HEAD')
        result = subprocess.run(['bash', str(FRAMEWORK / 'scripts/workspace-pull'), str(self.ws)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsNotNone(read_stamp(str(self.ws)))
        self.assertIsNotNone(read_stamp(str(self.ws / 'origin')))

    def test_setup_collapse_preserves_unsafe_git_and_invalid_settings(self):
        git(self.root, 'init', '-q')
        self.repo()
        put(self.ws / '.cursor/settings.json', 'invalid JSON')
        data, _ = self.check(scope='workspace')
        rows = {f['id']: f for f in data['findings']}
        self.assertFalse(rows['S4']['collapsed'])
        self.assertFalse(rows['S18']['collapsed'])

    def test_relative_plugin_root_has_no_false_wrapper_orphans(self):
        relative = os.path.relpath(FRAMEWORK, Path.cwd())
        _, rows, warnings = scan_plugin(relative, 'codex', True, str(Path.home()))
        self.assertNotIn('P7', [f['id'] for f in rows])
        self.assertEqual(warnings, [])

    def test_equivalent_numeric_repo_versions(self):
        repo = self.repo()
        put(repo / 'lore-repo.md', '---\ndescription: Example\nversion: "0'+(FRAMEWORK / 'VERSION').read_text().strip()+'"\n---\n')
        data, _ = self.check(scope='repos')
        self.assertNotIn('R2', [f['id'] for f in data['findings']])

    def test_invalid_utf8_and_legacy_coverage_are_visible(self):
        agent = self.agent()
        put(agent / 'lore/old.md', '# Legacy\n')
        (agent / 'lore/broken.md').write_bytes(b'\xffbroken')
        data, _ = self.check(scope='repos')
        rows = [f for f in data['findings'] if f['id'] == 'R6']
        self.assertTrue(any(f['data'].get('issue') == 'invalid_utf8' and f['severity']=='error' for f in rows))
        self.assertTrue(any(f['data'].get('issue') == 'legacy' and f['severity']=='info' for f in rows))

    def test_topic_renamed_out_of_lore_is_uncommitted_lore(self):
        repo = self.repo()
        agent = self.agent(repo)
        put(agent / 'lore/topic.md', '# Topic\n')
        git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'initial')
        git(repo, 'mv', 'agents/test-agent/lore/topic.md', 'agents/test-agent/workdir/topic.md')
        data, _ = self.check(scope='repos')
        rows = [f for f in data['findings'] if f['id'] == 'R8']
        self.assertIn('agents/test-agent/lore/topic.md', rows[0]['data']['paths'])

    def test_cursor_shortcut_targeting_workspace_root_does_not_abort(self):
        agent = self.agent()
        path = self.shortcut(agent, 'cursor')
        path.write_text(path.read_text().replace(str(agent.relative_to(self.ws)), '.'))
        findings, warnings = [], []
        check_shortcuts(str(self.ws), str(FRAMEWORK), findings, warnings)
        self.assertTrue(any(f['id'] == 'R12' and 'repo_scope' in f['data']['reasons']
                            for f in findings))

    def test_new_agent_missing_context_is_informational(self):
        agent = self.agent()
        (agent / 'lore-context.md').unlink()
        data, _ = self.check(scope='repos')
        rows = [f for f in data['findings'] if f['id'] == 'R5']
        self.assertEqual([(f['severity'], f['data']['reason']) for f in rows],
                         [('info', 'optional_context_absent')])
        self.assertTrue(all(f['severity'] == 'info' for f in data['findings']
                            if f['data'].get('issue') == 'missing_context'))

    def test_unknown_framework_version_does_not_invent_repo_skew(self):
        self.agent()
        with patch('lr_core.check.version_at', return_value=None):
            data, _ = self.check(scope='repos')
        self.assertNotIn('R2', [f['id'] for f in data['findings']])
        self.assertFalse(data['complete'])

    def test_wrapper_inventory_includes_empty_and_legacy_directories(self):
        copy = self.root / 'plugin'
        shutil.copytree(FRAMEWORK, copy, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        (copy / '.cursor-skills/retired-command').mkdir()
        (copy / 'skills/cursor').mkdir()
        _, rows, _ = scan_plugin(str(copy), 'codex', True, str(Path.home()))
        paths = {f['data']['path'] for f in rows if f['id'] == 'P7'}
        self.assertTrue({'.cursor-skills/retired-command', 'skills/cursor'}.issubset(paths))


if __name__ == '__main__':
    unittest.main()
