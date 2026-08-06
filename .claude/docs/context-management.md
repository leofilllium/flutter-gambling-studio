# Context management — Flutter Game Studio

Context is a critical resource in a session. Manage it actively.

## File-backed state (the main strategy)

**The file is the memory, not the conversation.** Conversations are ephemeral and will be
compacted or lost. Files on disk survive compaction and restarts.

### The session state file

Keep `production/session-state/active.md` as a living checkpoint.
Update it after every meaningful step.

```markdown
<!-- STATUS -->
Epic: Neon Spin Slot
Feature: Payline System
Task: Implement 5-line evaluator
<!-- /STATUS -->

## Current task
[What we are doing]

## Progress
- [x] GDD written
- [x] rtp-config.json → RTP 96.1%
- [ ] Payline evaluator — in progress
- [ ] Payline tests
- [ ] Win animation

## Key decisions
- Using a sealed class GameState (ADR-001)
- RNG: Random.secure() through a WeightedRNG singleton
- 5 paylines (horizontal + diagonal)

## Files in flight
- lib/systems/payline_evaluator.dart
- test/systems/payline_evaluator_test.dart
- design/gdd/payline-system.md

## Open questions
- Should Wild count on the diagonal lines?

## Last compaction
[date and time — updated automatically by the hook]
```

### Writing documents incrementally

When creating a GDD or an ADR (multi-section documents):
1. Create the file immediately with all the headings (empty)
2. Discuss and write one section at a time
3. Write each section to the file once it is approved
4. Update `active.md` after every section
5. Earlier discussion of finished sections can safely be compacted — the decisions are in the file

### After any failure (compaction, crash)

1. The `session-start.sh` hook automatically shows `active.md`
2. Read the full state file to restore context
3. Read the files that were in flight
4. Continue from the unfinished task

## Proactive compaction

- Compact proactively at around 60–70% context usage
- Use `/clear` between unrelated tasks
- Natural compaction points: after writing a section to a file, after a commit, after
  finishing a task

```
/compact Focus on [current task] — sections 1-3 are written to the file, we are on section 4
```

## Context budgets by task type

| Task | Budget | Notes |
|------|--------|-------|
| Reading/reviewing a GDD | ~3k tokens | A quick read |
| Implementing one component | ~8k tokens | Read the files + write |
| Refactoring several files | ~15k tokens | Analysis + changes |
| A full /autocreate pipeline | ~40k tokens | Many parallel tasks |

## Delegating to sub-agents

Use sub-agents to protect the main context:
- Research across many files → an Explore sub-agent
- Deep analysis → a Plan sub-agent
- Code review → `/code-review` (which uses several agents)
- Sub-agents receive full context in the prompt — they do not inherit the conversation history

## Game-specific strategy

### Balancing — fast cycles

Balance iterations (parameters → simulation → adjustment) repeat many times. Each cycle saves
context:

The cycle is the same in every category — only the config and the model change:

```bash
# edit the numbers in JSON → run → read the verdict
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json --trials 100000
```

| Category | What `game-mathematician` turns | Model |
|----------|--------------------------------|-------|
| C1 | Symbol weights, payouts in `rtp-config.json` | M1 |
| C2 | House edge, the multiplier formula, the cap | M2 |
| C3 | Spin event weights, unlock prices, energy regen | M3 |
| C4 | Base rates, soft/hard pity | M4 |
| C5 | Round thresholds, modifier strength, income | M5 |
| C6 | Bucket multipliers, board geometry | M6 |

Do NOT keep all the mathematics in the conversation. It lives in files — the config and the
report survive compaction.

### After /balance-check

The simulation/analysis result is written to `design/balance/simulation-report.md`.
Compact the context afterwards — every decision is in the file.

## What to preserve when compacting

Save this to `active.md` before compacting:
- A pointer to `active.md` (read it to restore)
- The list of changed files and what each is for
- Architectural decisions and their rationale
- The current task and the next step
- Open questions awaiting a user answer
- Test status (green/red)
- The game's category (C1–C6), its math model (M1–M6) and the latest run verdict
