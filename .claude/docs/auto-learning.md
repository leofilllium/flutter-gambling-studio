# Evidence-driven studio learning

The studio records reusable mistakes and verified improvements during normal work. An agent
then implements one bounded framework correction in a separate worktree, validates it, and
pushes a `learning/*` branch for the owner to review and merge. A suggestion alone is not a
learned correction, and an unmerged proposal is not a new production rule.

This is session-driven automation. The skill and persona guide an available Codex or Claude
agent; `tools/auto_learn.py` does not call a model, invent fixes, schedule jobs, run between
sessions, or merge branches. Session hooks may display the pending queue. The active agent
must invoke `/auto-learn` on a concrete reusable finding and process pending items when useful.

## When to trigger

- A failed build, asset review, runtime check, math verification, or store composition review
  exposes a reusable framework gap after the immediate task has been corrected.
- A user correction reveals a wrong default, conflicting guidance, or a missing contextual rule.
- A measured alternative produces the same or better result faster or with fewer retries.

Record every distinct supported finding. Repeated occurrences of the same normalized problem
and remedy increment its count; they do not create more branches. Keep one root cause per
proposal. Do not invent lessons from hypothetical failures, add rules for every harmless
variation, or turn a one-game preference into a studio-wide restriction. Prioritize current
work and preserve a pending observation if its independent fix cannot yet be verified.

## Authorization and configuration

`.claude/auto-learning.json` enables the workflow and automatic proposal publication for this
repository, following the owner's request. `publish_learning_branches: false` retains local
recording, preparation, and checking but disables pushes; `enabled: false` disables the helper.
An absent configuration defaults to publication disabled.

`remote` names one configured Git remote. `base_branch: null` discovers its default branch;
set a branch name when remote HEAD is unavailable. The helper fetches that remote branch and
creates the worktree from the fetched commit, excluding local unpublished commits and dirty
files. Publication requires the same pinned fetch and push destinations as preparation.

Default bounds are 12 changed files and 800 added/deleted lines, including the evidence
report. Allowed changes are `.claude/`, `.codex/`, `tools/`, `docs/`, `AGENTS.md`, `CLAUDE.md`,
`agents.md` (the existing lowercase alias), and `README.md`. Both tracked guideline aliases
are accepted together, including on case-insensitive filesystems. This targets the framework
rather than generated apps, media, credentials, or balance configs. Text-only changes and ordinary files are required. Split a large remedy
into independently validated proposals; do not inflate limits just to bypass reviewability.

The helper never merges, force-pushes, pushes the default branch, stages the active checkout,
or sends external messages/comments. It creates no pull request. The final assistant response
provides the branch name and evidence for the owner's normal review process. A manual PR can
be created by the owner; future automation requires explicit authorization.

## Commands

Run commands from the studio root, or provide `--repo /absolute/studio` before the subcommand.
Use a sanitized UTF-8 evidence file containing the actual observation and reproduction or
measurements. Each input file is limited to 100 KB and copied into the proposal report; never
supply credentials, private user content, complete raw service logs, or unrelated app data.
The helper does not promise automatic secret redaction.

```bash
python3 tools/auto_learn.py record \
  --title "Correct the shared asset review invocation" \
  --problem "The generation run called review with an obsolete flag and failed." \
  --improvement "Update the canonical call and verify the supported CLI invocation." \
  --evidence /tmp/asset-review-evidence.txt
python3 tools/auto_learn.py pending
python3 tools/auto_learn.py prepare OBSERVATION_ID
```

`record` returns a 16-character ID. `prepare` returns an absolute worktree path and branch
`learning/<id>-<title>`. It writes the evidence report at `docs/learning/<id>.md` but does not
implement the remedy. The active agent or auto-learner edits files inside that worktree.
Keep the original checkout path for invoking the helper, especially before this framework
version has been merged into the remote base.

```bash
python3 tools/auto_learn.py check OBSERVATION_ID -- \
  python3 -B -m unittest discover -s tools/tests -p 'test_relevant_helper.py'
python3 tools/auto_learn.py publish OBSERVATION_ID
```

Replace the example test pattern with real tests relevant to the actual proposal. The helper
runs the command as an argument vector in the isolated worktree without shell evaluation.
For multiple commands, invoke `check` separately. A check must terminate within
`check_timeout_seconds` (300 by default). A failure or timeout blocks publication. Commands
must not mutate proposal files; format first, then check. Avoid generated untracked artifacts;
Python's `-B` suppresses bytecode writes. A structured review of a documentation-only change
can be evidence, but a command that merely returns zero is not a meaningful review.

The report contains the observation, sanitized source evidence, base commit, command results,
output excerpts, and output hashes. Review it and the complete diff before `publish`. Check
results are bound to final file content and modes; changing the proposal requires rerunning
checks. The helper controls the report; do not hand-edit it. Publication stages exactly the
bounded proposal paths, creates one conventional commit, and pushes an explicit
`refs/heads/learning/...` destination. It never adds the active source checkout to the index.

## State and recovery

Queue state, locks, and worktrees live in `<git-common-dir>/auto-learn/`, outside tracked
source files. A nonblocking lock prevents concurrent helper commands from racing. They are
local machine state, not a cloud queue or a durable cross-clone learner database. Merged
`docs/learning/` reports retain the shared lessons; consult those reports before recording a
new finding in a fresh clone.

- Repeating `prepare` returns the existing worktree. A missing/deleted worktree requires
  deliberate local recovery; it is not silently recreated over another branch.
- Fix validation failures in the worktree and rerun checks. Content changes discard old check
  results; repeating the same command replaces its previous result on unchanged content.
- A failed push retains the exact local commit. Retry `publish` after authentication or
  connectivity is restored. Already published identical commits are safe to retry.
- A remote learning branch with a different commit is never overwritten. Reconcile it through
  human review; the helper does not force-push or silently switch destinations.
- Unexpected commits or branch switches stop publication. Do not commit manually in the
  worktree; the helper binds checks to the prepared base and creates the single proposal commit.
- If the remote base lacks a required unmerged change, leave the observation pending until
  that dependency is merged. Do not copy all current changes into a learning proposal.
- Report an external blocker after a bounded attempt. Continue the original task when it is
  independent; a failed proposal push does not erase the evidence or justify an infinite retry.

After the owner merges or rejects the branch, they may remove its worktree with ordinary
`git worktree remove` and optionally delete its local or remote branch. The helper does not
automatically delete human review artifacts or infer approval from elapsed time.

## Verification

```bash
python3 -B -m unittest tools.tests.test_auto_learn -v
```

The integration suite uses temporary repositories and bare local remotes. It checks real Git
publication and rejects stale/failed checks, branch switches, remote changes, report-only
proposals, oversized changes, binary files, symlinks, generated-app changes, and collisions.
It also verifies that source checkout staging, unpublished commits, and the remote default
branch remain untouched. No test contacts the production remote.
