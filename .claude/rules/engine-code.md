---
description: Flame 1.18.x specific patterns — component lifecycle, world setup, camera, forbidden APIs
globs: ["lib/game/**/*.dart", "lib/components/**/*.dart", "lib/systems/**/*.dart"]
---

# Engine Code Rules — Flame 1.18.x

## CRITICAL Flame 1.18.x APIs

### HasCollisionDetection — on World, not on FlameGame
```dart
// ✅ CORRECT (Flame 1.18+)
class SlotMachineWorld extends World with HasCollisionDetection {
  // collision detection goes here
}

// ❌ FORBIDDEN (deprecated in 1.17, removed in 1.18)
class SlotMachineGame extends FlameGame with HasCollisionDetection { }
```

### CameraComponent — the new API only
```dart
// ✅ CORRECT
late final CameraComponent camera;
late final SlotMachineWorld world;

@override
Future<void> onLoad() async {
  world = SlotMachineWorld();
  camera = CameraComponent(world: world);
  await addAll([world, camera]);
}

// ❌ FORBIDDEN (the old Camera API)
camera = Camera(); // Does not exist in Flame 1.18!
```

### FlameGame.world and FlameGame.camera — first-class fields
```dart
// Flame 1.18: game.world and game.camera are built-in fields.
// Do not create your own fields named world/camera — those names are reserved.

class SlotMachineGame extends FlameGame {
  // this.world — already exists (World)
  // this.camera — already exists (CameraComponent)
  // Create typed getters instead:
  SlotMachineWorld get slotWorld => world as SlotMachineWorld;
}
```

### SpawnComponent (Flame 1.15+)
```dart
// ✅ Use it for periodic spawning of symbols/effects
add(SpawnComponent(
  factory: (i) => CoinParticle(),
  period: 0.1,
  area: Rectangle.fromLTWH(0, 0, size.x, size.y),
));
```

### HasTimeScale (Flame 1.16+) — slow down / speed up
```dart
// For a slow-motion effect on a big win
class ReelComponent extends PositionComponent with HasTimeScale {
  void slowMotion() => timeScale = 0.3;
  void normalSpeed() => timeScale = 1.0;
}
```

## Forbidden Flame patterns

1. **`game.isPaused = true`** — use a `GameState` enum + `pauseEngine()`/`resumeEngine()`
2. **`Flame.images.load()` inside `update()`** — only in `onLoad()`
3. **Direct `ComponentSet` operations** — use `game.children.toList()` (Flame 1.18)
4. **`onGameResize` without an `isMounted` check** — a component can receive a resize before it loads
5. **Inheritance deeper than 3 levels** — use composition instead (add child components)
6. **Hot reload for game files** — use Hot Restart (Shift+R)

## Required patterns

### The reel component
```dart
class ReelComponent extends PositionComponent with HasGameRef<SlotMachineGame> {
  // Pre-initialised for update() — no allocation in the hot path
  final _tempVector = Vector2.zero();

  late final List<SymbolComponent> _symbols;

  @override
  Future<void> onLoad() async {
    // Load assets ONLY in onLoad
    _symbols = await _createSymbols();
    await addAll(_symbols);
  }

  @override
  void update(double dt) {
    // SYNCHRONOUS! No await!
    if (!_isSpinning) return;
    _tempVector.setFrom(position);
    _updateScrollPosition(dt); // No allocation
  }
}
```

### ParticleSystemComponent — limits
```dart
// For wins above 20x the bet
void _spawnWinParticles(int multiplier) {
  final count = (multiplier * 5).clamp(20, SlotConfig.maxParticles);
  add(ParticleSystemComponent(
    particle: Particle.generate(
      count: count,
      lifespan: 1.5,
      generator: (i) => AcceleratedParticle(
        acceleration: Vector2(0, 98),
        speed: Vector2(
          (gameRng.nextDouble() - 0.5) * 200,
          -gameRng.nextDouble() * 300,
        ),
        child: CircleParticle(radius: 3, paint: Paint()..color = Colors.amber),
      ),
    ),
  ));
}
```

### Audio — at most 3 concurrent sounds
```dart
class AudioService {
  // Only 3 slots: BGM + Spin + Effect
  static const int maxConcurrentSounds = 3;

  Future<void> playWin(int multiplier) async {
    await FlameAudio.play('sfx_win_${_winTier(multiplier)}.ogg');
  }

  // Coin counting with rising pitch
  Future<void> playCoinCount(int coins) async {
    final rate = 1.0 + (coins / 100).clamp(0.0, 0.5);
    await FlameAudio.play('sfx_coins.ogg', volume: 1.0);
    // playbackRate is controlled through the AudioPlayer instance
  }
}
```

## Performance

- No allocation in `update()` or `render()` — pre-initialise Vector2, Rect, Paint
- `SpriteBatch` for more than 20 identical sprites (the symbols on the reels!)
- `debugMode = true` only in debug builds
- `FpsTextComponent` only in debug builds
- At most 200 active particles at once (SlotConfig.maxParticles)
