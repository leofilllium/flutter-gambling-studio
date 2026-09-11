---
name: auto-learn
description: Turn observed studio failures or verified faster approaches into tested framework improvements on isolated learning branches for human review. Invoke after concrete reusable evidence emerges during a studio task, or to process pending learning observations.
---

# Auto-learn

Use the `auto-learner` role in `.claude/agents/auto-learner.md`. This is an event-driven
workflow in the current agent session, not a background daemon. The helper manages evidence,
worktrees, validation, and branch publication; the agent diagnoses and implements the change.
Read [auto-learning.md](../../docs/auto-learning.md) for commands and recovery behavior.

The repository owner has authorized creating and pushing `learning/*` proposals after observed
mistakes or verified improvements. Complete that work when enabled in
`.claude/auto-learning.json`; human approval or merging remains the owner's action. Do not
ask again for an already authorized proposal push. An explicit user pause or narrower request
overrides this standing authorization. Do not merge, enable auto-merge, push another branch,
force-push, publish comments, or create PRs through this workflow.

1. Capture a concrete failure, correction, or verified improvement with sanitized evidence.
   Separate the observation from inference. A preference applies to its actual context; do
   not convert one example into a universal rule. Record each distinct reusable observation
   even if its implementation must wait. Deduplicate by root cause and proposed remedy.
2. Confirm whether existing guidance already fixes it. If so, repair the discovery or invocation
   gap rather than inventing a duplicate skill. Record a genuinely faster route with comparable
   before/after timing, resource use, or avoided work, preserving all quality gates.
3. Record and prepare with `tools/auto_learn.py`. Work only in the returned isolated worktree,
   which starts at the remote base and does not contain the user's unfinished changes.
4. Implement one bounded correction in the right existing rule, skill, persona, or helper.
   Create a new skill or agent only when the responsibility is distinct and reusable. Apply
   `skill-creator` when available for skill work. Do not weaken RNG, math, compliance, layout,
   runtime verification, or user authorization rules to make a task easier. Changes to the
   learning workflow itself remain proposals requiring human merge.
5. Run meaningful checks through `check`: a reproduced failure that now passes, a focused
   regression test, a measured comparison, or a structured manual review for guidance-only
   edits. For guidance, record the actual review findings in a text artifact and use a command
   to verify relevant references/structure. A no-op command is not validation. Avoid commands
   that print credentials or private data; inspect the generated report before publication.
6. Inspect the complete diff and evidence report. Publish once checks pass on the final content.
   Report the branch, change, evidence, tests, and remaining limits to the owner. They review
   and merge. The proposal must not silently modify the active task's rules before merging.

If the remote base lacks a needed unmerged framework change, leave the observation pending
and state the dependency; do not import the user's whole working tree or publish unrelated
commits. If authentication, connectivity, validation, or a branch collision blocks publication,
keep the recoverable state, report the exact blocker, and continue the main task where possible.
Do not repeat the same failing external operation indefinitely. Do not recursively open learning
proposals for the same learner run; queue genuinely new root causes for a later invocation.
