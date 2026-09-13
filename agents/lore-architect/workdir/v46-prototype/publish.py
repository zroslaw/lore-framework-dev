"""Executable v46 design prototype, NOT an installed framework command.

POSIX reference implementation. All authoring and merging happens in a private
worktree. No reset, stash, shared-checkout commit, or implicit push destination.
The caller is responsible for routing all session edits to the returned worktree.
"""

from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import fcntl
import json
import math
import os
import re
import signal
import subprocess
import tempfile
import time
import uuid


class Refused(RuntimeError):
    pass


GIT_TIMEOUT = 30


def git(repo, *args, check=True):
    env = os.environ.copy()
    # Do not inherit an index/repository override from the caller's shell.
    for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env.update(GIT_TERMINAL_PROMPT="0",
               GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=10")
    argv = (
        ["git", "-C", str(repo), "-c", "merge.autoStash=false",
         "-c", "rebase.autoStash=false", *args])
    proc = subprocess.Popen(argv, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        # Keep ownership until Git and ordinary descendants (hooks, transport)
        # have been killed/reaped; a timed-out child must not keep writing.
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.communicate()
        raise
    result = subprocess.CompletedProcess(argv, proc.returncode, stdout, stderr)
    if check and result.returncode:
        raise Refused(result.stderr.decode(errors="replace").strip())
    return result


def out(repo, *args):
    return git(repo, *args).stdout.decode().strip()


def common(repo):
    return Path(out(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        # Persist the rename as well as the file content.
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def claim(path):
    """Kernel-owned lock; never unlink it, never guess another owner's expiry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Refused("another command owns this session") from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def names(raw):
    return [os.fsdecode(item) for item in raw.split(b"\0") if item]


def valid_paths(repo, paths):
    if not paths or len(paths) != len(set(paths)):
        raise Refused("an explicit nonempty unique write-set is required")
    for path in paths:
        p = PurePosixPath(path)
        if (not path or str(p) != path or p.is_absolute() or ".." in p.parts
                or ".git" in p.parts or "\0" in path):
            raise Refused("invalid literal path: " + repr(path))
        # Reject directories and symlinked parents; symlink leaves are supported.
        target = Path(repo) / path
        if target.is_dir() and not target.is_symlink():
            raise Refused("directory is not a write-set entry: " + path)
        if any(parent.is_symlink() for parent in target.parents
               if parent != Path(repo) and Path(repo) in parent.parents):
            raise Refused("symlinked parent: " + path)
        tracked = git(repo, "ls-files", "--error-unmatch", "--",
                      ":(literal)" + path, check=False).returncode == 0
        if not tracked and not os.path.lexists(target):
            raise Refused("missing write-set entry: " + path)


def entry_map(repo):
    result = {}
    for line in git(repo, "ls-files", "--stage", "-z").stdout.split(b"\0"):
        if line:
            value, path = line.split(b"\t", 1)
            result.setdefault(os.fsdecode(path), []).append(value.decode())
    return result


def validate_record(item, filename):
    required = ("id", "worktree", "canonical", "branch", "destination", "url", "fetched_ref", "status")
    if (not isinstance(item, dict) or type(item.get("version")) is not int
            or item["version"] != 1
            or any(not isinstance(item.get(k), str) or not item[k] for k in required)):
        raise Refused("invalid or unsupported session record")
    sid = item["id"]
    if (not re.fullmatch("[a-f0-9]{32}", sid) or filename != sid + ".json"
            or item["branch"] != "refs/heads/lore/session/" + sid
            or item["fetched_ref"] != "refs/lore/publish/" + sid
            or item["status"] not in {"active", "starting", "committing", "pending", "publishing",
                                      "merging", "conflict", "unknown", "published"}):
        raise Refused("session identity is invalid")
    if "first_failure" in item and (type(item["first_failure"]) not in (int, float)
                                   or not 0 <= item["first_failure"] < float("inf")):
        raise Refused("invalid failure timestamp")
    if item["status"] not in ("starting", "unknown"):
        if not isinstance(item.get("head"), str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", item["head"]):
            raise Refused("missing or invalid expected commit")
    if item["status"] in ("pending", "publishing", "merging", "conflict", "published"):
        if not isinstance(item.get("payload"), str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", item["payload"]):
            raise Refused("missing or invalid payload commit")


class Session:
    def __init__(self, record):
        self.record = Path(record)
        self.lock = self.record.with_suffix(".lock")
        self.reload()

    def reload(self):
        self.state = json.loads(self.record.read_text())
        validate_record(self.state, self.record.name)
        self.repo = Path(self.state["worktree"])

    def save(self, status=None, reason=None, failure=False):
        if status:
            self.state["status"] = status
        if reason is not None:
            self.state["reason"] = reason
        if failure or status in ("conflict", "unknown"):
            self.state.setdefault("first_failure", time.time())
        atomic_json(self.record, self.state)
        return dict(self.state)

    def identity(self):
        if (self.repo.resolve() == Path(self.state["canonical"]).resolve()
                or Path(out(self.repo, "rev-parse", "--absolute-git-dir")) == common(self.repo)
                or Path(out(self.repo, "rev-parse", "--show-toplevel")).resolve() != self.repo.resolve()):
            raise Refused("publication requires a private session worktree")
        if out(self.repo, "symbolic-ref", "HEAD") != self.state["branch"]:
            raise Refused("session branch changed; preserve work and inspect")
        if out(self.repo, "rev-parse", "HEAD") != self.state["head"]:
            raise Refused("session HEAD changed; preserve work and inspect")
        if common(self.repo) != self.record.parent.parent:
            raise Refused("session repository changed")

    def fetch(self, repo=None):
        repo = repo or self.repo
        git(repo, "fetch", "--no-tags", "--no-write-fetch-head",
            self.state["url"], "+" + self.state["destination"] + ":" + self.state["fetched_ref"])
        self.state["remote_head"] = out(repo, "rev-parse", self.state["fetched_ref"])
        self.state["verified_at"] = time.time()
        return self.state["remote_head"]

    @classmethod
    def begin(cls, canonical, worktree, kind="lore"):
        canonical = Path(canonical).resolve()
        if Path(out(canonical, "rev-parse", "--show-toplevel")).resolve() != canonical:
            raise Refused("not its own repository")
        branch = out(canonical, "symbolic-ref", "--short", "HEAD")
        remote = out(canonical, "config", "--get", "branch." + branch + ".remote")
        destination = out(canonical, "config", "--get", "branch." + branch + ".merge")
        if remote == "." or not destination.startswith("refs/heads/"):
            raise Refused("an existing remote branch destination is required")
        git(canonical, "check-ref-format", destination)
        # Resolve one fetch URL. Never inherit push.default, remote.push or pushurl.
        urls = out(canonical, "remote", "get-url", "--all", remote).splitlines()
        if len(urls) != 1:
            raise Refused("ambiguous upstream URL")
        url = urls[0]
        if ":" in url:
            raise Refused("prototype accepts local fixture remotes only")
        # Relative filesystem remotes are relative to the canonical checkout.
        if ":" not in url and not os.path.isabs(url):
            url = str((canonical / url).resolve())
        if url.startswith("-"):
            raise Refused("invalid upstream URL")
        sid = uuid.uuid4().hex
        directory = common(canonical) / "lr-publish"
        state = dict(version=1, id=sid, worktree=str(Path(worktree).resolve()),
                     canonical=str(canonical), branch="refs/heads/lore/session/" + sid,
                     destination=destination, url=url,
                     fetched_ref="refs/lore/publish/" + sid, status="starting")
        record = directory / (sid + ".json")
        atomic_json(record, state)
        session = cls(record)
        try:
            base = session.fetch(canonical)
            if kind not in ("lore", "update"):
                raise Refused("invalid session kind")
            if kind == "update" and (
                    git(canonical, "status", "--porcelain", "-z").stdout
                    or git(canonical, "merge-base", "--is-ancestor", "HEAD", base, check=False).returncode):
                raise Refused("automatic update deferred: canonical checkout has local work")
            # Base new edits on the actual destination, never unpublished main ancestry.
            git(canonical, "worktree", "add", "-b", state["branch"][11:], str(worktree), base)
            session.state.update(base=base, head=base)
            session.save("active")
        except (Refused, OSError, subprocess.TimeoutExpired) as exc:
            session.save("unknown", str(exc))
            raise
        return session

    def commit(self, paths, message):
        with claim(self.lock):
            self.reload()
            self.identity()
            if self.state["status"] != "active":
                raise Refused("retry the existing publication; do not create another snapshot")
            if git(self.repo, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0:
                raise Refused("unexpected merge in progress")
            gitdir = Path(out(self.repo, "rev-parse", "--absolute-git-dir"))
            if any((gitdir / name).exists() for name in (
                    "rebase-merge", "rebase-apply", "sequencer", "CHERRY_PICK_HEAD", "REVERT_HEAD")):
                raise Refused("another Git operation is in progress")
            if git(self.repo, "diff", "--cached", "--name-only", "-z").stdout:
                raise Refused("unexpected staged work in this private session")
            valid_paths(self.repo, paths)
            specs = [":(literal)" + path for path in paths]
            # Persist intent before any Git mutation; a crash must not look healthy.
            self.state["paths"] = list(paths)
            self.save("committing")
            try:
                git(self.repo, "add", "-A", "--", *specs)
                if not git(self.repo, "diff", "--cached", "--name-only", "-z").stdout:
                    return self.save("active", "nothing to commit")
                git(self.repo, "commit", "-m", message, "--", *specs)
                head = out(self.repo, "rev-parse", "HEAD")
                changed = set(names(git(self.repo, "diff-tree", "--no-commit-id", "--name-only",
                                        "-r", "-z", head).stdout))
                if not changed <= set(paths):
                    raise Refused("unexpected committed paths; no reset or push")
                self.state["head"] = head
                self.state["payload"] = head
                return self.save("pending", "ready to publish")
            except (Refused, OSError, subprocess.TimeoutExpired) as exc:
                return self.save("unknown", str(exc))

    def publish(self, mode="merge-retry", attempts=3):
        if mode not in ("merge-retry", "no-merge") or not 1 <= attempts <= 3:
            raise Refused("invalid publication mode or retry bound")
        with claim(self.lock):
            self.reload()
            self.identity()
            if self.state["status"] not in ("pending", "published"):
                raise Refused("session needs resolution or recovery before publication")
            if self.state["status"] == "published":
                return dict(self.state)
            try:
                # Publish only a frozen snapshot. Additional edits require a later session.
                if git(self.repo, "status", "--porcelain", "-z").stdout:
                    return self.save("pending", "uncommitted work in session; preserve and inspect", failure=True)
                for number in range(attempts):
                    self.save("publishing")
                    pushed = git(self.repo, "push", "--porcelain", self.state["url"],
                                 self.state["head"] + ":" + self.state["destination"], check=False)
                    remote = self.fetch()
                    if git(self.repo, "merge-base", "--is-ancestor", self.state["head"],
                           remote, check=False).returncode == 0:
                        return self.save("published", "verified on destination")
                    if pushed.returncode == 0:
                        return self.save("unknown", "push acknowledged but destination no longer contains snapshot")
                    if mode == "no-merge" or number == attempts - 1:
                        return self.save("pending", "push rejected or retry cap reached", failure=True)
                    # A rejected push with no remote advance is not a merge problem.
                    if git(self.repo, "merge-base", "--is-ancestor", remote,
                           self.state["head"], check=False).returncode == 0:
                        return self.save("pending", pushed.stderr.decode(errors="replace"), failure=True)
                    if git(self.repo, "merge-base", "--is-ancestor", self.state["base"],
                           remote, check=False).returncode:
                        return self.save("pending", "destination history rewritten; human reconciliation required", failure=True)
                    self.state["merge_parent"] = remote
                    self.save("merging")
                    merged = git(self.repo, "merge", "--no-commit", "--no-ff", remote, check=False)
                    conflicts = names(git(self.repo, "diff", "--name-only", "--diff-filter=U", "-z").stdout)
                    if conflicts:
                        self.state["conflicts"] = conflicts
                        self.state["index_baseline"] = entry_map(self.repo)
                        return self.save("conflict", "semantic resolution required")
                    if merged.returncode:
                        return self.save("unknown", merged.stderr.decode(errors="replace"))
                    git(self.repo, "commit", "--no-edit")
                    self.state["head"] = out(self.repo, "rev-parse", "HEAD")
                    self.save("pending", "merged incoming changes")
            except (Refused, OSError, subprocess.TimeoutExpired) as exc:
                return self.save("unknown", str(exc))

    def resume(self):
        """Explicitly reconcile uncertain delivery; never adopt an unexpected tip."""
        with claim(self.lock):
            self.reload()
            self.identity()
            if not self.state.get("payload"):
                raise Refused("no recorded snapshot; inspect the interrupted commit first")
            if git(self.repo, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0:
                raise Refused("merge remains in progress; resolve or inspect it first")
            try:
                remote = self.fetch()
                if git(self.repo, "merge-base", "--is-ancestor", self.state["head"],
                       remote, check=False).returncode == 0:
                    return self.save("published", "verified on destination during resume")
                return self.save("pending", "same recorded snapshot ready to retry")
            except (Refused, OSError, subprocess.TimeoutExpired) as exc:
                return self.save("unknown", str(exc))

    def resolve(self, owner):
        """Caller has edited conflict files using an executor booted as owner.

        This API checks paths, not the LLM's identity. The orchestration contract
        provides the identity binding. Guest resolution is sequential in this prototype.
        """
        with claim(self.lock):
            self.reload()
            self.identity()
            if self.state["status"] != "conflict":
                raise Refused("no recorded conflict")
            conflicts = set(self.state["conflicts"])
            prefix = "agents/" + owner + "/"
            allowed = lambda p: p.startswith(prefix + "lore/") or p in (
                prefix + "role.md", prefix + "lore-context.md")
            if not conflicts <= set(self.state["paths"]) or not all(map(allowed, conflicts)):
                raise Refused("foreign conflict; keep private worktree for owning-agent or human recovery")
            if out(self.repo, "rev-parse", "MERGE_HEAD") != self.state["merge_parent"]:
                raise Refused("merge parent changed")
            before = self.state["index_baseline"]
            current = entry_map(self.repo)
            if {p: v for p, v in before.items() if p not in conflicts} != {
                    p: v for p, v in current.items() if p not in conflicts}:
                raise Refused("unrelated index changes during resolution")
            unstaged = set(names(git(self.repo, "diff", "--name-only", "-z").stdout))
            untracked = names(git(self.repo, "ls-files", "--others", "--exclude-standard", "-z").stdout)
            if unstaged - conflicts or untracked:
                raise Refused("unrelated working-tree changes during resolution")
            git(self.repo, "add", "-A", "--", *[":(literal)" + p for p in sorted(conflicts)])
            if git(self.repo, "diff", "--name-only", "--diff-filter=U", "-z").stdout:
                raise Refused("unresolved paths remain")
            self.save("merging")
            git(self.repo, "commit", "--no-edit")
            self.state["head"] = out(self.repo, "rev-parse", "HEAD")
            return self.save("pending", "semantic merge completed")


def status(repo):
    """Read-only status across all sessions, independent of reader checkout branch.

    No cleanup, no network, no claim that clean main implies delivery. Terminal
    success means previously verified delivery; current remote health is separate.
    """
    result = []
    for path in sorted((common(repo) / "lr-publish").glob("*.json")):
        try:
            item = json.loads(path.read_text())
            validate_record(item, path.name)
            if item.get("status") == "published":
                continue
            if item.get("status") in ("committing", "publishing", "merging", "starting"):
                item["activity"] = "interrupted"
                try:
                    with path.with_suffix(".lock").open("r") as lock:
                        try:
                            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            fcntl.flock(lock, fcntl.LOCK_UN)
                        except BlockingIOError:
                            item["activity"] = "running"
                except FileNotFoundError:
                    pass
            item["age_seconds"] = (max(0, time.time() - item["first_failure"])
                                   if "first_failure" in item else None)
            result.append(item)
        except (Refused, ValueError, TypeError, OSError):
            result.append(dict(status="unknown", record=path.name, reason="unreadable or unsupported record"))
    return result


def refresh_due(state, now, ttl):
    """Reference scheduling model; invalid fields self-heal, arithmetic is bounded.

    Numeric epoch timestamps here keep the prototype independent of the installed
    parser. Production keeps the existing offset-aware ISO timestamp encoding.
    """
    ttl = max(0, ttl)
    def age(key):
        value = state.get(key)
        if (type(value) not in (float, int) or value < 0 or value > now
                or not math.isfinite(value)):
            return None
        return now - value
    success_age, attempt_age = age("last_success"), age("last_attempt")
    if state.get("result") == "setup-required" and attempt_age is not None:
        return attempt_age >= ttl
    if success_age is not None and success_age < ttl:
        return False
    if state.get("result") in ("failed", "partial") and attempt_age is not None:
        try:
            failures = max(0, min(32, int(state.get("consecutive_failures", 0))))
        except (ValueError, TypeError, OverflowError):
            failures = 0
        if failures:
            delay = min(ttl, 900 * (1 << (failures - 1)))
            return attempt_age >= delay
    return True
