# Game Studio Coordination Rules

A mini-game succeeds when balance (mathematics/difficulty), code design and juiciness stay in sync.

## Collaboration principles

1. **English**
   All interaction between the user and the agents — answers, questions, logs — is in
   **English**, and so is everything the studio produces: design documents, reports, code and
   the player-facing copy in the game itself. The only exception is an explicit user request
   for the game in another language, which affects the player-facing strings only. See
   `CLAUDE.md` → Language.

2. **A consultative style**
   Agents do not make decisions on their own without the user (except in the `/auto-*` skills).
   The pattern: *Ask a question → offer 2-3 options → the user chooses → write a draft →
   the user approves → save to file*.

3. **Respect the chain of command**
   - Only `creative-director` changes the core gameplay and the vision (pillars).
   - Only `game-mathematician` approves a new balance model after `/balance-check` passes.
   - `mechanics-programmer` MAY NOT hardcode game parameters. They must be read from
     `GameConfig`/the GDD.
   - `mechanics-programmer` does not hardcode a win chance (e.g. `if (Random().nextDouble() < 0.1) win!`)
     and does not substitute anything for `Random.secure()`.
   - `juice-artist` does not make an animation longer than 3–4 seconds, so the game loop does
     not slow down. `game-designer` approves the length.
   - `release-manager` is the only agent who can lift a compliance blocker. No agent
     "simplifies" the age gate or the disclaimer for the sake of speed.

## Conflict resolution

Mistakes are inevitable. If one mechanic contradicts another, pause and bring in the specialist:

**If the code contradicts the GDD:** `lead-programmer` and `game-designer` find common ground.
If a feature is impossible because of Flame's architecture, the GDD is updated.

**If the math model is outside its window** (`tools/simulate_math.py` returns FAIL): production
stops. Bring in `game-mathematician`, who iterates ONLY on the numbers in the model's JSON
config. Only after a green run does `mechanics-programmer` update the code. The thresholds for
models M1–M6 are in `.claude/docs/math-models.md`.

**If "prettier" conflicts with "honest":** honesty wins. A visual near-miss is acceptable only
when it reflects the real outcome; tuning the animation to feel more like a win is a breach of
game integrity, not a juice-artist's clever find.

## Handing off work

When passing a task from the mathematician → designer → programmer → VFX, use the `/team-dev`
skill. Each agent must pass the exact reference to the working documents (for example the GDD
at `design/gdd/[file].md`) to the next agent in the chain.
