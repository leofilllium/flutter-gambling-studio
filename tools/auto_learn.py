#!/usr/bin/env python3
"""Evidence-backed learning proposals; edits belong to an agent, merges to a human.

State and isolated worktrees live in Git's common directory, outside the source
checkout. Run --help for the record/prepare/check/publish/pending workflow.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

CONFIG = ".claude/auto-learning.json"
DEFAULTS = {
    "enabled": True,
    "publish_learning_branches": False,
    "remote": "origin",
    "base_branch": None,
    "max_changed_files": 12,
    "max_changed_lines": 800,
    "check_timeout_seconds": 300,
}
ALLOWED_PREFIXES = (".claude/", ".codex/", "tools/", "docs/")
ALLOWED_FILES = {"AGENTS.md", "agents.md", "CLAUDE.md", "README.md"}


class LearningError(Exception):
    """An action cannot proceed within the learning proposal contract."""


def run(argv, cwd, *, timeout=60):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise LearningError(f"Command failed ({result.returncode}): {argv[0]}: {detail}")
    return result.stdout.decode("utf-8", errors="strict").strip()


def git(repo, *args):
    return run(["git", *args], repo)


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def read_policy(repo):
    policy = dict(DEFAULTS)
    path = repo / CONFIG
    if path.exists():
        policy.update(json.loads(path.read_text()))
    if not policy["enabled"]:
        raise LearningError("Auto-learning is disabled in .claude/auto-learning.json.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", policy["remote"]):
        raise LearningError("The configured remote must be a named Git remote.")
    for key in ("max_changed_files", "max_changed_lines", "check_timeout_seconds"):
        if not isinstance(policy[key], int) or policy[key] < 1:
            raise LearningError(f"{key} must be a positive integer.")
    return policy


@contextmanager
def state_lock(repo):
    common = Path(git(repo, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = repo / common
    state = common.resolve() / "auto-learn"
    state.mkdir(parents=True, exist_ok=True)
    with (state / "lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise LearningError("Another learning command is active; retry after it finishes.") from exc
        yield state


def load_observation(state, observation_id):
    if not re.fullmatch(r"[a-f0-9]{16}", observation_id):
        raise LearningError("Observation IDs contain 16 lowercase hexadecimal characters.")
    path = state / "observations" / f"{observation_id}.json"
    if not path.exists():
        raise LearningError(f"Unknown observation: {observation_id}")
    return path, json.loads(path.read_text())


def record(repo, state, args):
    fields = (args.title, args.problem, args.improvement)
    if any(not value.strip() for value in fields):
        raise LearningError("Title, observed problem, and proposed improvement must be non-empty.")
    normalized = "\n".join(" ".join(value.lower().split()) for value in fields[1:])
    observation_id = hashlib.sha256(normalized.encode()).hexdigest()[:16]
    path = state / "observations" / f"{observation_id}.json"
    evidence = []
    for item in args.evidence:
        source = Path(item).resolve()
        if not source.is_file() or source.stat().st_size > 100_000:
            raise LearningError("Each evidence file must be a text file of at most 100 KB.")
        content = source.read_text(encoding="utf-8")
        if not content.strip():
            raise LearningError("Evidence files cannot be empty.")
        evidence.append({"name": source.name, "sha256": hashlib.sha256(content.encode()).hexdigest(), "text": content})
    if path.exists():
        observation = json.loads(path.read_text())
        observation["occurrences"] += 1
        observation["last_seen"] = now()
        # Keep the reviewed evidence and branch immutable on duplicate observations.
    else:
        observation = {
            "id": observation_id, "title": args.title.strip(), "problem": args.problem.strip(),
            "improvement": args.improvement.strip(), "evidence": evidence,
            "created_at": now(), "last_seen": now(), "occurrences": 1, "status": "recorded",
        }
    save(path, observation)
    return {"id": observation_id, "status": observation["status"], "occurrences": observation["occurrences"]}


def remote_urls(repo, remote):
    fetch = git(repo, "remote", "get-url", "--all", remote).splitlines()
    push = git(repo, "remote", "get-url", "--push", "--all", remote).splitlines()
    if len(fetch) != 1 or len(push) != 1:
        raise LearningError("Learning requires exactly one fetch URL and one push URL.")
    return {"fetch": fetch[0], "push": push[0]}


def report_path(observation):
    return f"docs/learning/{observation['id']}.md"


def write_report(worktree, observation):
    lines = [f"# Learning proposal: {observation['title']}", "", "Status: proposed; human review and merge required.", "",
             "## Observed problem", "", observation["problem"], "", "## Proposed improvement", "", observation["improvement"], "",
             f"Base commit: `{observation['base_sha']}`", "", "## Source evidence", ""]
    for item in observation["evidence"]:
        lines += [f"### {item['name']}", "", f"SHA-256: `{item['sha256']}`", ""]
        # Indentation keeps supplied evidence inert even if it contains Markdown fences.
        lines += [("    " + line.rstrip()) if line.strip() else "" for line in item["text"].splitlines()]
        lines += [""]
    lines += ["## Validation", ""]
    checks = observation.get("checks", [])
    if not checks:
        lines += ["Validation has not run yet.", ""]
    for check in checks:
        lines += [f"- Command: `{json.dumps(check['argv'])}`; exit {check['exit_code']}; {check['finished_at']}",
                  f"  Output SHA-256: `{check['output_sha256']}`"]
        if check.get("output_excerpt"):
            lines += ["", *[("    " + line.rstrip()) if line.strip() else "" for line in check["output_excerpt"].splitlines()], ""]
    relative = report_path(observation)
    parts = PurePosixPath(relative).parts
    if any(worktree.joinpath(*parts[:i]).is_symlink() for i in range(1, len(parts) + 1)):
        raise LearningError("The proposal report and its parent directories may not be symlinks.")
    path = worktree / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise LearningError("The proposal report may not be a symlink.")
    path.write_text("\n".join(lines) + "\n")


def prepare(repo, state, policy, args):
    path, observation = load_observation(state, args.id)
    if observation.get("worktree"):
        return {"id": args.id, "status": observation["status"], "worktree": observation["worktree"], "branch": observation["branch"]}
    remote = policy["remote"]
    urls = remote_urls(repo, remote)
    base = args.base or policy["base_branch"]
    if not base:
        symbolic = git(repo, "ls-remote", "--symref", remote, "HEAD")
        match = re.search(r"^ref: refs/heads/(.+)\tHEAD$", symbolic, re.MULTILINE)
        if not match:
            raise LearningError("Remote HEAD is unavailable; configure base_branch or pass --base main.")
        base = match.group(1)
    git(repo, "check-ref-format", f"refs/heads/{base}")
    git(repo, "fetch", "--no-tags", remote, f"refs/heads/{base}")
    base_sha = git(repo, "rev-parse", "FETCH_HEAD^{commit}")
    slug = re.sub(r"[^a-z0-9]+", "-", observation["title"].lower()).strip("-")[:48] or "improvement"
    branch = f"learning/{args.id}-{slug}"
    worktree = state / "worktrees" / args.id
    git(repo, "worktree", "add", "-b", branch, str(worktree), base_sha)
    observation.update({"status": "prepared", "worktree": str(worktree), "branch": branch,
                        "remote": remote, "remote_urls": urls, "base_branch": base,
                        "base_sha": base_sha, "checks": []})
    save(path, observation)
    write_report(worktree, observation)
    return {"id": args.id, "status": "prepared", "branch": branch, "worktree": str(worktree), "base": base_sha,
            "next": "An agent must implement the improvement in this worktree, then run check and publish."}


def verify_worktree(observation, state):
    expected = state / "worktrees" / observation["id"]
    if Path(observation.get("worktree", "")).resolve() != expected.resolve() or not expected.is_dir():
        raise LearningError("Prepare the observation before validation or publication.")
    if git(expected, "branch", "--show-current") != observation["branch"] or not re.fullmatch(r"learning/[a-f0-9]{16}-[a-z0-9-]+", observation["branch"]):
        raise LearningError("Only the prepared learning/* branch may be published.")
    expected_head = observation.get("commit_sha", observation["base_sha"])
    if git(expected, "rev-parse", "HEAD") != expected_head:
        raise LearningError("Unexpected commits in the worktree; the learner creates its own single reviewed commit.")
    return expected


def changed_paths(worktree, base):
    tracked = git(worktree, "diff", "--name-only", "-z", "--no-renames", base, "--").split("\0")
    untracked = git(worktree, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    return sorted(set(filter(None, tracked + untracked)))


def snapshot(worktree, observation, policy):
    paths = changed_paths(worktree, observation["base_sha"])
    if len(paths) > policy["max_changed_files"]:
        raise LearningError("Proposal exceeds max_changed_files; split the improvement.")
    digest = hashlib.sha256()
    count = 0
    for item in paths:
        parts = PurePosixPath(item).parts
        if not parts or any(part in {"..", ".git"} for part in parts) or PurePosixPath(item).is_absolute():
            raise LearningError(f"Unsafe proposal path: {item}")
        if item not in ALLOWED_FILES and not item.startswith(ALLOWED_PREFIXES):
            raise LearningError(f"Learning proposals may only change studio guidance and tools: {item}")
        target = worktree / item
        if any((worktree.joinpath(*parts[:i])).is_symlink() for i in range(1, len(parts) + 1)):
            raise LearningError(f"Symlinks are not allowed in proposals: {item}")
        payload = target.read_bytes() if target.exists() else b"<deleted>"
        if b"\0" in payload:
            raise LearningError(f"Binary files are not allowed in proposals: {item}")
        payload.decode("utf-8")
        digest.update(item.encode() + b"\0" + payload)
        digest.update(str(target.stat().st_mode if target.exists() else 0).encode())
        # Git reports tracked added/deleted lines; count untracked text separately.
    stats = git(worktree, "diff", "--numstat", "--no-renames", observation["base_sha"], "--")
    for line in stats.splitlines():
        added, deleted, _ = line.split("\t", 2)
        if added == "-" or deleted == "-":
            raise LearningError("Binary patches are not allowed in learning proposals.")
        count += int(added) + int(deleted)
    untracked = set(filter(None, git(worktree, "ls-files", "--others", "--exclude-standard", "-z").split("\0")))
    count += sum(len((worktree / item).read_text().splitlines()) for item in untracked)
    if count > policy["max_changed_lines"]:
        raise LearningError("Proposal exceeds max_changed_lines; split the improvement.")
    return digest.hexdigest(), paths


def check(repo, state, policy, args):
    path, observation = load_observation(state, args.id)
    if observation.get("commit_sha"):
        raise LearningError("Already committed; retry publish for this immutable proposal.")
    worktree = verify_worktree(observation, state)
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    if not argv:
        raise LearningError("Provide a validation command after --.")
    before, _ = snapshot(worktree, observation, policy)
    if observation.get("validated_snapshot") != before:
        observation["checks"] = []
    # A retry replaces the previous result for the same command on this snapshot.
    observation["checks"] = [item for item in observation["checks"] if item["argv"] != argv]
    started = now()
    try:
        result = subprocess.run(argv, cwd=worktree, capture_output=True, timeout=policy["check_timeout_seconds"])
        output = result.stdout + result.stderr
        exit_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"") + (exc.stderr or b"") + b"\nValidation timed out."
        exit_code = 124
    after, _ = snapshot(worktree, observation, policy)
    observation["checks"].append({"argv": argv, "started_at": started, "finished_at": now(), "exit_code": exit_code,
                                  "output_sha256": hashlib.sha256(output).hexdigest(),
                                  "output_excerpt": output.decode("utf-8", errors="replace")[-4000:]})
    if before != after:
        observation["checks"][-1]["exit_code"] = 125
        observation["checks"][-1]["output_excerpt"] += "\nValidation changed proposal files. Rerun after reviewing those changes."
    write_report(worktree, observation)
    observation["validated_snapshot"], _ = snapshot(worktree, observation, policy)
    observation["status"] = "validated" if all(item["exit_code"] == 0 for item in observation["checks"]) else "validation_failed"
    save(path, observation)
    if observation["status"] == "validation_failed":
        raise LearningError("Validation failed; inspect the report, fix the cause, and rerun checks on the changed files.")
    return {"id": args.id, "status": observation["status"], "checks": len(observation["checks"]), "report": report_path(observation)}


def publish(repo, state, policy, args):
    if not policy["publish_learning_branches"]:
        raise LearningError("Branch publication is disabled in .claude/auto-learning.json.")
    path, observation = load_observation(state, args.id)
    worktree = verify_worktree(observation, state)
    if policy["remote"] != observation["remote"] or remote_urls(repo, observation["remote"]) != observation["remote_urls"]:
        raise LearningError("The configured remote changed after preparation; publication stopped.")
    current, paths = snapshot(worktree, observation, policy)
    if observation.get("status") not in {"validated", "committed", "published"} or not observation.get("checks"):
        raise LearningError("A passing check is required before publication.")
    if current != observation.get("validated_snapshot"):
        raise LearningError("Proposal changed after validation; rerun check before publishing.")
    if not any(item != report_path(observation) for item in paths):
        raise LearningError("A report alone is not an implemented improvement.")
    git(worktree, "diff", "--check", observation["base_sha"], "--")
    if not observation.get("commit_sha"):
        # Case-insensitive path matching can omit a tracked case alias on
        # macOS. Match each exact path for this command only; keep repo config.
        for item in paths:
            git(worktree, "-c", "core.ignorecase=false", "add", "--", item)
        staged = set(filter(None, git(worktree, "diff", "--cached", "--name-only", "-z").split("\0")))
        if staged != set(paths):
            raise LearningError("The index contains unexpected changes; publication stopped.")
        git(worktree, "commit", "-m", f"fix(studio): {observation['title']}")
        observation["commit_sha"] = git(worktree, "rev-parse", "HEAD")
        observation["status"] = "committed"
        save(path, observation)
    # Pre-commit hooks must not alter the validated proposal.
    committed_snapshot, _ = snapshot(worktree, observation, policy)
    if committed_snapshot != observation["validated_snapshot"] or git(worktree, "status", "--porcelain"):
        raise LearningError("Commit hooks or another process changed the proposal; no push was attempted.")
    remote = observation["remote"]
    if remote_urls(repo, remote) != observation["remote_urls"]:
        raise LearningError("The remote changed during commit; no push was attempted.")
    ref = f"refs/heads/{observation['branch']}"
    existing = git(repo, "ls-remote", observation["remote_urls"]["push"], ref)
    if existing and existing.split()[0] != observation["commit_sha"]:
        raise LearningError("The remote learning branch already has different work; it will never be overwritten.")
    git(worktree, "-c", f"remote.{remote}.mirror=false", "-c", "push.followTags=false", "push", "--no-follow-tags",
        remote, f"{observation['commit_sha']}:{ref}")
    observation["status"] = "published"
    observation["published_at"] = now()
    save(path, observation)
    return {"id": args.id, "status": "published", "branch": observation["branch"], "commit": observation["commit_sha"],
            "next": "Human review and merge required. No pull request, comment, or merge was created."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Studio checkout (default: current directory).")
    commands = parser.add_subparsers(dest="command", required=True)
    recorder = commands.add_parser("record", help="Deduplicate a concrete observation with sanitized text evidence.")
    recorder.add_argument("--title", required=True)
    recorder.add_argument("--problem", required=True)
    recorder.add_argument("--improvement", required=True)
    recorder.add_argument("--evidence", action="append", required=True, help="Sanitized UTF-8 evidence file; repeatable.")
    preparer = commands.add_parser("prepare", help="Create a learning/* worktree from the remote base; does not implement edits.")
    preparer.add_argument("id")
    preparer.add_argument("--base", help="Remote base branch; default is configured branch or remote HEAD.")
    checker = commands.add_parser("check", help="Run a real command in the worktree and bind its result to the proposal content.")
    checker.add_argument("id")
    checker.add_argument("argv", nargs=argparse.REMAINDER)
    publisher = commands.add_parser("publish", help="Commit exact proposal paths and push only the isolated learning/* branch.")
    publisher.add_argument("id")
    commands.add_parser("pending", help="Read pending observations; no generation, agent spawning, or pushing.")
    args = parser.parse_args(argv)
    try:
        repo = Path(git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel")).resolve()
        policy = read_policy(repo)
        with state_lock(repo) as state:
            if args.command == "record":
                result = record(repo, state, args)
            elif args.command == "pending":
                result = []
                for path in sorted((state / "observations").glob("*.json")):
                    item = json.loads(path.read_text())
                    if item["status"] != "published":
                        result.append({key: item[key] for key in ("id", "title", "status", "occurrences")})
            else:
                result = {"prepare": prepare, "check": check, "publish": publish}[args.command](repo, state, policy, args)
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
        return 0
    except (LearningError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        sys.stderr.write(f"auto-learn: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
