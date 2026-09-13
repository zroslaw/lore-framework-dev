"""Prove selected tests reject deliberately reintroduced design defects.

Every mutant runs in a disposable copy. No installed framework code is changed.
An import error or crashed runner does not count as detecting a mutation.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
MUTATIONS = [
    ("missing-exact-head-guard",
     'if out(self.repo, "rev-parse", "HEAD") != self.state["head"]:',
     'if False:',
     'Fixture.test_external_session_commit_is_detected_without_undoing_it'),
    ("unrelated-index-changes-accepted",
     'if {p: v for p, v in before.items() if p not in conflicts} != {\n'
     '                    p: v for p, v in current.items() if p not in conflicts}:',
     'if False:',
     'Fixture.test_intruding_private_index_changes_are_refused_without_reset'),
    ("setup-required-cooldown-removed",
     'if state.get("result") == "setup-required" and attempt_age is not None:',
     'if False:',
     'Refresh.test_setup_required_uses_its_own_cooldown_without_success_stamp'),
    ("implicit-push-destination",
     'pushed = git(self.repo, "push", "--porcelain", self.state["url"],\n'
     '                                 self.state["head"] + ":" + self.state["destination"], check=False)',
     'pushed = git(self.repo, "push", "--porcelain", "origin", check=False)',
     'Fixture.test_destination_ignores_push_default_refspec_and_pushurl'),
    ("delete-other-branch-marker",
     'if item.get("status") == "published":',
     'if item.get("branch") != out(repo, "symbolic-ref", "HEAD"):\n'
     '                path.unlink()\n'
     '                continue\n'
     '            if item.get("status") == "published":',
     'Fixture.test_status_is_identical_across_main_and_worktree_branches'),
]


def main():
    original = (ROOT / 'publish.py').read_text()
    results = []
    for name, before, after, test in MUTATIONS:
        if original.count(before) != 1:
            raise RuntimeError('mutation anchor must occur once: ' + name)
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            (dest / 'publish.py').write_text(original.replace(before, after))
            shutil.copy(ROOT / 'test_publish.py', dest)
            run = subprocess.run([sys.executable, str(dest / 'test_publish.py'), test, '-v'],
                                 cwd=dest, capture_output=True, text=True, timeout=60)
            caught = run.returncode == 1 and 'FAIL:' in run.stderr and 'ERROR:' not in run.stderr
            results.append(dict(mutation=name, test=test, detected=caught,
                                exit_code=run.returncode))
            print(name + ': ' + ('detected' if caught else 'NOT DETECTED'))
            if not caught:
                print(run.stderr)
    (ROOT / 'mutation-results.json').write_text(json.dumps(results, indent=2) + '\n')
    return 0 if all(r['detected'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
