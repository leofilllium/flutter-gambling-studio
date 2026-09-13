# Store interpreter preflight review

This guidance-only proposal is based on remote commit 15445729f6dea385c4a6edb525fd49ffc77bc17b. The remote store runbook is older and longer than the active checkout, but has the same direct-system-Python dependency probe. The correction is independent of unmerged gameplay and composition changes; none were copied into this branch.

## Findings

- The existing store-screenshots skill owns dependency preflight. No new skill or helper is needed.
- Discovery checks actual Pillow/numpy imports in the active environment, the project .venv, then python3. An explicit STORE_PYTHON path takes priority and fails visibly if invalid.
- Quoting protects executable paths with spaces. The discovered absolute executable is recorded by the import probe; instructions require preserving the selection across shells.
- Dependency installation is deferred until existing environments are checked, and uses the chosen interpreter's -m pip rather than a potentially unrelated pip.
- All 14 compositor invocations use the selected interpreter. Cutout and image-bridge examples also retain the same interpreter. Their command arguments are unchanged.
- The frontmatter, discovery description, visual rules, math/compliance gates, capture requirements, runtime-background authorization, and release boundaries are unchanged.

## Validation performed

The exact first Phase 0 bash block was extracted and executed in temporary directories against seven cases: no usable candidate, valid explicit interpreter, invalid explicit interpreter, active environment, project .venv in a directory containing spaces, broken active environment with valid project .venv, and invalid explicit override with valid fallback available. All seven behaved as specified. The fixtures used an unavailable python3 on PATH and the existing working virtual environment; no dependencies were installed.

The selected interpreter successfully ran tools/store_compose.py --help and the boardplate, triptych, showcase, banner, and check subcommand help. This reproduces the originally failing operation using the proposed invocation. No artwork or game files were generated.

The skill-creator quick validator was run. Its schema rejects pre-existing argument-hint and user-invocable frontmatter keys. A baseline comparison confirms the same rejection before and after this proposal and byte-identical frontmatter. These repository-native fields are preserved rather than removed for an unrelated validator. No new validator regression was introduced.

The helper-managed evidence report records actual command outputs. This review does not claim full store composition or app runtime validation; neither changed.
