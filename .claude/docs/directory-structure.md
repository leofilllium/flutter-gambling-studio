# Game Studio directories

The studio supports **5 variants of project architecture**.
On every `/autocreate` run one variant is chosen automatically and recorded in `design/structure.md`.
This creates variety between games — each one gets its own code organisation.

---

## V1 — Layer Architecture

The classic MVC-like organisation: every layer in its own folder.

```text
lib/
├── main.dart
├── app.dart                          # MaterialApp, named routes
├── assets.dart                       # Path constants for every asset
├── game/
│   ├── [name]_game.dart              # FlameGame
│   ├── [name]_world.dart             # World with HasCollisionDetection
│   └── game_config.dart              # Every game constant
├── components/
│   ├── [main_component].dart
│   ├── [element_component].dart
│   ├── win_animation.dart
│   ├── ambient_particles.dart
│   └── screen_shake.dart
├── systems/
│   ├── [game_logic].dart             # RNG / match_detector / spawn_manager
│   └── [evaluator].dart              # The pure result-scoring function
├── models/
│   ├── game_state.dart               # The sealed state class
│   └── [game_element].dart
├── screens/
│   ├── splash_screen.dart
│   ├── main_menu.dart
│   ├── game_screen.dart
│   ├── hud_widget.dart
│   └── [others].dart                 # 12+ screens
├── widgets/
│   └── [shared_widgets].dart
├── audio/
│   └── audio_service.dart
└── theme/
    ├── game_theme.dart
    └── animations.dart
```

---

## V2 — Feature Slice

Gameplay (Flame) is separated from UI (Flutter) and services — each feature in its own folder.

```text
lib/
├── main.dart
├── assets.dart
├── core/
│   ├── app.dart                      # MaterialApp, routes
│   └── theme/
│       ├── game_theme.dart
│       └── animations.dart
├── gameplay/                         # Everything Flame: game + components + logic
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   ├── components/
│   │   ├── [main_component].dart
│   │   ├── win_animation.dart
│   │   └── ambient_particles.dart
│   └── systems/
│       ├── [game_logic].dart
│       └── [evaluator].dart
├── ui/                               # Everything Flutter: screens + widgets
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── main_menu.dart
│   │   ├── game_screen.dart
│   │   ├── hud_widget.dart
│   │   └── [others].dart
│   └── widgets/
│       └── [shared_widgets].dart
├── domain/                           # Models + states + config
│   ├── game_config.dart
│   ├── game_state.dart
│   └── [game_element].dart
└── services/                         # External services
    └── audio_service.dart
```

---

## V3 — Presentation-Domain-Data (PDD)

A clean separation: presentation (Flutter UI), domain (business logic + Flame), data (configs).

```text
lib/
├── main.dart
├── app.dart
├── assets.dart
├── presentation/                     # The Flutter UI layer
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── main_menu.dart
│   │   ├── game_screen.dart
│   │   ├── hud_widget.dart
│   │   └── [others].dart
│   ├── widgets/
│   │   └── [shared_widgets].dart
│   └── theme/
│       ├── game_theme.dart
│       └── animations.dart
├── domain/                           # Business logic + Flame
│   ├── game/
│   │   ├── [name]_game.dart
│   │   └── [name]_world.dart
│   ├── systems/
│   │   ├── [game_logic].dart
│   │   └── [evaluator].dart
│   └── models/
│       ├── game_state.dart
│       └── [game_element].dart
├── data/                             # Configs and services
│   ├── config/
│   │   └── game_config.dart
│   └── services/
│       └── audio_service.dart
└── components/                       # Flame visual components
    ├── [main_component].dart
    ├── win_animation.dart
    └── ambient_particles.dart
```

---

## V4 — Module Architecture

By functional module: engine, mechanics, visuals, interface, infrastructure.

```text
lib/
├── main.dart
├── app.dart
├── assets.dart
├── engine/                           # The Flame core
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   └── game_config.dart
├── mechanics/                        # Game logic
│   ├── systems/
│   │   ├── [game_logic].dart
│   │   └── [evaluator].dart
│   └── models/
│       ├── game_state.dart
│       └── [game_element].dart
├── visuals/                          # The visual layer (Flame components + theme)
│   ├── components/
│   │   ├── [main_component].dart
│   │   ├── win_animation.dart
│   │   └── ambient_particles.dart
│   └── theme/
│       ├── game_theme.dart
│       └── animations.dart
├── interface/                        # Flutter UI
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── main_menu.dart
│   │   ├── game_screen.dart
│   │   ├── hud_widget.dart
│   │   └── [others].dart
│   └── widgets/
│       └── [shared_widgets].dart
└── infrastructure/                   # External dependencies
    └── audio/
        └── audio_service.dart
```

---

## V5 — Vertical Slice

Organised by game area: bootstrap, arena, rules, hud, menus, foundation.

```text
lib/
├── main.dart
├── bootstrap/                        # The application entry point
│   ├── app.dart
│   └── assets.dart
├── arena/                            # The play field (Flame)
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   └── components/
│       ├── [main_component].dart
│       ├── win_animation.dart
│       └── ambient_particles.dart
├── rules/                            # Rules and mechanics
│   ├── systems/
│   │   ├── [game_logic].dart
│   │   └── [evaluator].dart
│   ├── models/
│   │   ├── game_state.dart
│   │   └── [game_element].dart
│   └── config/
│       └── game_config.dart
├── hud/                              # HUD and in-game overlays
│   ├── hud_widget.dart
│   ├── win_overlay.dart
│   └── bonus_overlay.dart
├── menus/                            # Menu screens
│   ├── splash_screen.dart
│   ├── main_menu.dart
│   ├── game_screen.dart
│   └── [others].dart
└── foundation/                       # The shared base
    ├── audio/
    │   └── audio_service.dart
    ├── theme/
    │   ├── game_theme.dart
    │   └── animations.dart
    └── widgets/
        └── [shared_widgets].dart
```

---

## How the variant is chosen

In Phase 2 of `/autocreate` a Python snippet writes the chosen variant to `design/structure.md`:

```python
import time
variant = (int(time.time()) % 5) + 1  # uniformly 1–5
```

`design/structure.md` contains the full path mapping for every file category.
The Phase 4 agents read this file through `lib/contracts.md` and create every file at the
paths it specifies.

---

## Invariants (identical in ALL variants)

- `lib/main.dart` — the entry point, always at the root of `lib/`
- `assets/` — the assets folder, always at the project root
- `design/` — GDD and balance docs, always at the root
- `GameConfig` contains ONLY constants, no logic
- `GameState` — a sealed class, present in every variant
- `AudioService` — at most 3 concurrent sounds
- Asset paths are registered in `pubspec.yaml` under the same `assets/` directories

---

## Key file examples by gambling category (V1 paths)

Every category shares the same skeleton — a source of randomness, a pure outcome evaluator and
the math model's config. Only what fills them changes.

```
lib/systems/weighted_rng.dart       # Random.secure() — the ONLY source of randomness
lib/systems/[outcome]_resolver.dart # Pure function: the round outcome BEFORE the animation
design/balance/[model]-config.json  # The math model's numbers (read by simulate_math.py)
```

### C1 — Social Casino (a slot)
```
lib/systems/weighted_rng.dart
lib/systems/payline_evaluator.dart  # Scoring wins by line
lib/components/reel_component.dart  # A spinning reel
lib/components/symbol_component.dart
design/balance/rtp-config.json      # model M1
```

### C2 — Casino Originals (crash / mines / dice)
```
lib/systems/round_resolver.dart     # serverSeed+clientSeed+nonce → the round outcome
lib/systems/multiplier_curve.dart   # The multiplier formula from the house edge
lib/components/multiplier_display.dart
lib/components/cashout_button.dart
design/balance/rtp-config.json      # model M2
```

### C3 — Spin-to-Progress (build-and-raid)
```
lib/systems/weighted_rng.dart
lib/systems/spin_event_table.dart   # Spin event weights
lib/systems/energy_service.dart     # Regeneration, cap, spending
lib/components/village_component.dart
design/balance/economy-config.json  # model M3
```

### C4 — Gacha (banner pull)
```
lib/systems/weighted_rng.dart
lib/systems/pity_counter.dart       # soft/hard pity — persisted between sessions
lib/systems/banner_resolver.dart    # Rarity → a specific item
lib/components/pull_reveal.dart
design/balance/gacha-config.json    # model M4
```

### C5 — Casino Roguelike (poker deckbuilder)
```
lib/systems/run_rng.dart            # EXCEPTION: Random(seed) — the run is reproducible (ADR!)
lib/systems/hand_evaluator.dart     # A poker hand → points
lib/systems/modifier_registry.dart  # Jokers/symbols and their effects
lib/models/run_state.dart
design/balance/run-config.json      # model M5
```

### C6 — Physics (plinko / coin pusher)
```
lib/systems/physics_world.dart      # Forge2D, a FIXED timestep
lib/systems/launch_resolver.dart    # Starting conditions from Random.secure()
lib/components/ball_component.dart
lib/components/peg_component.dart
design/balance/physics-config.json  # model M6
```
