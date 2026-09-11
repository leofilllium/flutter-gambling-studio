# Context-based generation refactor

The framework now derives visual leads and store composition from the game rather than requiring
a character on every first slide and gameplay in every middle slide.

## Decisions

- `.claude/docs/visual-context.md` owns the shared concept/asset/store rules.
- `.claude/docs/game-concept-examples.md` maps the supplied Plinko, crown and Joker previews to
  original concept seeds, with additional Zeus/chicken examples. New classic slots default to
  3×3; explicit and existing variants retain their topology.
- Character-led games retain a prominent opening character; object/mechanic-led games need no
  invented mascot. Joker direction is mischievous and slightly vicious, playful rather than
  elegant or frightening. Config-supported x5/x10 coins are preferred where appropriate.
- The compositor supports explicit lead kinds, noncharacter lead bounds, repeatable critical
  region bounds, freely placed/spanning boards and free or left-heavy feature layouts. Measured
  subjects/gameplay are excluded from background-only detail checks, with real background still
  required. A separate mascot framing mode supports compact chickens without humanoid proportions. Existing
  character calls retain their default; the runbook always supplies the actual lead kind.
- The long store runbook is replaced with a context-driven workflow and a focused supporting
  reference for runtime-branding/background preservation. Identity, capture, math, compliance,
  visual verification and archive requirements remain.
- `/auto-learn` records evidence, deduplicates observations, prepares isolated worktrees, binds
  checks to final content and pushes bounded `learning/*` proposals. The owner alone merges.
  Session hooks display pending observations; active agents process findings under the standing
  authorization. No background daemon, automatic PR, external message or auto-merge is installed.

## Verification

- 165 Python tests passed, including 140 compositor tests and 15 real-Git learner integration
  tests. Learner tests use temporary bare local remotes and preserve their default branches.
- Ten documented compositor command variants parsed successfully. Forward walkthroughs covered
  no-mascot Plinko, Joker with right-side gameplay, and an existing 5×3 crown slot.
- The M1 reference template now has three visible rows and its existing single payline in the
  middle row. Payouts/weights are unchanged: exact enumeration of 262,144 outcomes gives 96.00%
  RTP and 34.31% hit rate, both passing.
- Shell syntax and Git whitespace checks passed. Auto-learn passes the skill-creator validator.
  Existing dual-platform skills retain Claude's `argument-hint` and `user-invocable` metadata;
  the Codex-only validator rejects those pre-existing extension keys. YAML/core fields and local
  reference targets were checked separately with the known Claude extensions allowed.

## Practical limits

Rerun Python checks in an environment with Pillow and NumPy:
`python3 -B -m unittest discover -s tools/tests -v`. Skill metadata validation also uses PyYAML.

No game assets were regenerated or store kit published during this framework refactor. Geometry
tests cannot prove artistic quality, exact lettering, or correct visual payline identity; future
runs still require visual and real-runtime checks. Wide-board width is a fit limit, so height
and aspect ratio can constrain the actual span; inspect it rather than stretching gameplay.

The affected local Codex skill links and slash-command prompts were updated to this checkout,
including auto-learn, without changing security settings. Restart the client to reload skill
discovery. Learner publication requires an authenticated configured Git remote; a failed push
keeps its evidence and recoverable local proposal.
