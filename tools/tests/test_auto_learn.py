"""End-to-end branch safety tests, exclusively against temporary bare remotes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "auto_learn.py"


class AutoLearnTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "studio"
        self.remote = self.root / "remote.git"
        self.repo.mkdir()
        self.git(self.root, "init", "--bare", str(self.remote))
        self.git(self.repo, "init", "-b", "main")
        self.git(self.repo, "config", "user.name", "Learning Test")
        self.git(self.repo, "config", "user.email", "learner@example.invalid")
        (self.repo / ".claude").mkdir()
        (self.repo / "tools").mkdir()
        (self.repo / "tools" / "rule.py").write_text("VALUE = 1\n")
        (self.repo / ".claude" / "auto-learning.json").write_text(json.dumps({"publish_learning_branches": True}))
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "Initial framework")
        self.git(self.repo, "remote", "add", "origin", str(self.remote))
        self.git(self.repo, "push", "-u", "origin", "main")
        self.git(self.remote, "symbolic-ref", "HEAD", "refs/heads/main")
        self.initial = self.git(self.repo, "rev-parse", "HEAD").strip()
        self.evidence = self.root / "evidence.txt"
        self.evidence.write_text("Observed: expected VALUE=2; actual VALUE=1. Reproduced locally.  \n\nEvidence contains blank lines.\n")

    def git(self, cwd, *args):
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), *args], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stderr

    def record(self):
        return self.cli("record", "--title", "Use validated helper value", "--problem", "Helper value is wrong",
                        "--improvement", "Correct the shared helper value", "--evidence", str(self.evidence))["id"]

    def prepared(self):
        observation_id = self.record()
        prepared = self.cli("prepare", observation_id)
        worktree = Path(prepared["worktree"])
        (worktree / "tools" / "rule.py").write_text("VALUE = 2\n")
        return observation_id, worktree, prepared["branch"]

    def check_value(self, observation_id, value=2):
        return self.cli("check", observation_id, "--", sys.executable, "-B", "-c",
                        f"from tools.rule import VALUE; assert VALUE == {value}")

    def assert_base_untouched(self):
        self.assertEqual(self.git(self.repo, "branch", "--show-current").strip(), "main")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD").strip(), self.initial)
        self.assertEqual(self.git(self.remote, "rev-parse", "refs/heads/main").strip(), self.initial)

    def test_publish_isolates_user_changes_and_deduplicates_observations(self):
        # A staged user file must remain byte-for-byte staged and never enter the branch.
        (self.repo / "user-work.txt").write_text("Unrelated unfinished task\n")
        self.git(self.repo, "add", "user-work.txt")
        index_before = self.git(self.repo, "diff", "--cached", "--binary")
        observation_id, worktree, branch = self.prepared()
        self.assertFalse((worktree / "user-work.txt").exists())
        self.assertEqual(self.record(), observation_id)
        self.check_value(observation_id)
        result = self.cli("publish", observation_id)
        self.assertEqual(result["status"], "published")
        self.assertEqual(self.git(self.remote, "rev-parse", f"refs/heads/{branch}").strip(), result["commit"])
        self.assertEqual(self.git(self.remote, "show", f"{branch}:tools/rule.py"), "VALUE = 2\n")
        self.assertEqual(self.git(self.repo, "diff", "--cached", "--binary"), index_before)
        self.assertEqual(self.cli("pending"), [])
        self.assertEqual(self.cli("publish", observation_id)["commit"], result["commit"])
        self.assert_base_untouched()

    def test_paired_root_guideline_aliases_publish_together(self):
        # Seed the two distinct Git paths through the index: this also works on
        # macOS volumes where the checkout aliases share one filesystem entry.
        upper = self.repo / "AGENTS.md"
        upper.write_text("Original guidelines\n")
        blob = self.git(self.repo, "hash-object", "-w", "AGENTS.md").strip()
        for name in ("AGENTS.md", "agents.md"):
            self.git(self.repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{name}")
        self.git(self.repo, "commit", "-m", "Track root guideline aliases")
        self.git(self.repo, "push", "origin", "main")
        self.initial = self.git(self.repo, "rev-parse", "HEAD").strip()
        observation_id, worktree, branch = self.prepared()
        for name in ("AGENTS.md", "agents.md"):
            (worktree / name).write_text("Corrected shared guidelines\n")
        self.check_value(observation_id)
        result = self.cli("publish", observation_id)
        for name in ("AGENTS.md", "agents.md"):
            self.assertEqual(self.git(self.remote, "show", f"{branch}:{name}"), "Corrected shared guidelines\n")
        changed = self.git(self.remote, "diff-tree", "--no-commit-id", "--name-only", "-r", result["commit"]).splitlines()
        self.assertIn("AGENTS.md", changed)
        self.assertIn("agents.md", changed)
        self.assert_base_untouched()

    def test_dirty_source_commits_are_not_included(self):
        (self.repo / "unpublished.txt").write_text("User commit\n")
        self.git(self.repo, "add", "unpublished.txt")
        self.git(self.repo, "commit", "-m", "User unpublished work")
        _, worktree, _ = self.prepared()
        self.assertFalse((worktree / "unpublished.txt").exists())

    def test_publication_requires_current_passing_validation(self):
        observation_id, worktree, _ = self.prepared()
        self.assertIn("passing check", self.cli("publish", observation_id, ok=False))
        self.check_value(observation_id)
        (worktree / "tools" / "rule.py").write_text("VALUE = 3\n")
        self.assertIn("changed after validation", self.cli("publish", observation_id, ok=False))
        self.check_value(observation_id, 3)
        self.cli("publish", observation_id)
        self.assert_base_untouched()

    def test_failed_check_prevents_publication(self):
        observation_id, _, _ = self.prepared()
        self.assertIn("Validation failed", self.cli("check", observation_id, "--", sys.executable, "-c", "raise SystemExit(2)", ok=False))
        self.assertIn("passing check", self.cli("publish", observation_id, ok=False))
        self.assert_base_untouched()

    def test_check_cannot_mutate_the_proposal_and_pass(self):
        observation_id, _, _ = self.prepared()
        self.assertIn("Validation failed", self.cli("check", observation_id, "--", sys.executable, "-c",
                      "from pathlib import Path; Path('tools/rule.py').write_text('VALUE = 9\\n')", ok=False))
        self.assertIn("passing check", self.cli("publish", observation_id, ok=False))

    def test_branch_switch_is_rejected(self):
        observation_id, worktree, _ = self.prepared()
        self.check_value(observation_id)
        self.git(worktree, "switch", "-c", "unsafe-target")
        self.assertIn("learning/*", self.cli("publish", observation_id, ok=False))
        self.assert_base_untouched()

    def test_binary_symlink_and_game_changes_are_rejected(self):
        observation_id, worktree, _ = self.prepared()
        target = worktree / "tools" / "payload.bin"
        target.write_bytes(b"\0binary")
        self.assertIn("Binary", self.cli("check", observation_id, "--", sys.executable, "-c", "pass", ok=False))
        target.unlink()
        target.symlink_to(self.evidence)
        self.assertIn("Symlinks", self.cli("check", observation_id, "--", sys.executable, "-c", "pass", ok=False))
        target.unlink()
        (worktree / "lib").mkdir()
        (worktree / "lib" / "game.dart").write_text("Game change\n")
        self.assertIn("studio guidance and tools", self.cli("check", observation_id, "--", sys.executable, "-c", "pass", ok=False))

    def test_remote_change_and_disabled_publication_are_rejected(self):
        observation_id, _, _ = self.prepared()
        self.check_value(observation_id)
        self.git(self.repo, "remote", "set-url", "--push", "origin", str(self.root / "other.git"))
        self.assertIn("remote changed", self.cli("publish", observation_id, ok=False))
        (self.repo / ".claude" / "auto-learning.json").write_text(json.dumps({"publish_learning_branches": False}))
        self.assertIn("publication is disabled", self.cli("publish", observation_id, ok=False))
        self.assert_base_untouched()

    def test_existing_remote_branch_is_never_overwritten(self):
        observation_id, _, branch = self.prepared()
        self.check_value(observation_id)
        self.git(self.repo, "push", "origin", f"{self.initial}:refs/heads/{branch}")
        self.assertIn("never be overwritten", self.cli("publish", observation_id, ok=False))
        self.assertEqual(self.git(self.remote, "rev-parse", f"refs/heads/{branch}").strip(), self.initial)
        self.assert_base_untouched()

    def test_report_only_is_not_an_implemented_improvement(self):
        observation_id = self.record()
        self.cli("prepare", observation_id)
        self.cli("check", observation_id, "--", sys.executable, "-c", "pass")
        self.assertIn("report alone", self.cli("publish", observation_id, ok=False))

    def test_failed_push_is_retryable_without_new_commit(self):
        observation_id, worktree, branch = self.prepared()
        self.check_value(observation_id)
        hook = self.remote / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        self.assertIn("Command failed", self.cli("publish", observation_id, ok=False))
        committed = self.git(worktree, "rev-parse", "HEAD").strip()
        hook.unlink()
        self.assertEqual(self.cli("publish", observation_id)["commit"], committed)
        self.assertEqual(self.git(self.remote, "rev-parse", f"refs/heads/{branch}").strip(), committed)
        self.assert_base_untouched()

    def test_repeating_failed_check_replaces_its_result(self):
        observation_id, _, _ = self.prepared()
        flag = self.root / "external-ready"
        command = f"from pathlib import Path; assert Path({str(flag)!r}).exists()"
        self.cli("check", observation_id, "--", sys.executable, "-c", command, ok=False)
        flag.write_text("ready")
        result = self.cli("check", observation_id, "--", sys.executable, "-c", command)
        self.assertEqual(result["checks"], 1)
        self.cli("publish", observation_id)

    def test_report_parent_symlink_cannot_write_outside_worktree(self):
        target = self.root / "outside"
        target.mkdir()
        (self.repo / "docs").symlink_to(target, target_is_directory=True)
        self.git(self.repo, "add", "docs")
        self.git(self.repo, "commit", "-m", "Symlink fixture")
        self.git(self.repo, "push", "origin", "main")
        observation_id = self.record()
        self.assertIn("may not be symlinks", self.cli("prepare", observation_id, ok=False))
        self.assertEqual(list(target.iterdir()), [])

    def test_size_limit_rejects_unbounded_changes(self):
        observation_id, worktree, _ = self.prepared()
        (worktree / "tools" / "oversized.py").write_text("# excess\n" * 801)
        self.assertIn("max_changed_lines", self.cli("check", observation_id, "--", sys.executable, "-c", "pass", ok=False))


if __name__ == "__main__":
    unittest.main()
