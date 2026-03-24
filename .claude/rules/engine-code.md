---
description: Flame 1.18.x specific patterns — component lifecycle, world setup, camera, forbidden APIs
globs: ["lib/game/**/*.dart", "lib/components/**/*.dart", "lib/systems/**/*.dart"]
---

# Engine Code Rules — Flame 1.18.x

## КРИТИЧЕСКИЕ API Flame 1.18.x

### HasCollisionDetection — на World, не на FlameGame
```dart
// ✅ ПРАВИЛЬНО (Flame 1.18+)
class SlotMachineWorld extends World with HasCollisionDetection {
  // collision detection здесь
}

// ❌ ЗАПРЕЩЕНО (устарело в 1.17, удалено в 1.18)
class SlotMachineGame extends FlameGame with HasCollisionDetection { }
```

### CameraComponent — только новый API
```dart
// ✅ ПРАВИЛЬНО
late final CameraComponent camera;
late final SlotMachineWorld world;

@override
Future<void> onLoad() async {
  world = SlotMachineWorld();
  camera = CameraComponent(world: world);
  await addAll([world, camera]);
}

// ❌ ЗАПРЕЩЕНО (старый Camera API)
camera = Camera(); // Не существует в Flame 1.18!
```

### FlameGame.world и FlameGame.camera — первоклассные поля
```dart
// Flame 1.18: game.world и game.camera — встроенные поля
// Не создавай свои поля с именами world/camera — они зарезервированы

class SlotMachineGame extends FlameGame {
  // this.world — уже есть (World)
  // this.camera — уже есть (CameraComponent)
  // Создавай типизированные геттеры:
  SlotMachineWorld get slotWorld => world as SlotMachineWorld;
}
```

### SpawnComponent (Flame 1.15+)
```dart
// ✅ Используй для периодического спауна символов/эффектов
add(SpawnComponent(
  factory: (i) => CoinParticle(),
  period: 0.1,
  area: Rectangle.fromLTWH(0, 0, size.x, size.y),
));
```

### HasTimeScale (Flame 1.16+) — замедление/ускорение
```dart
// Для slow-motion эффекта при Big Win
class ReelComponent extends PositionComponent with HasTimeScale {
  void slowMotion() => timeScale = 0.3;
  void normalSpeed() => timeScale = 1.0;
}
```

## Запрещённые паттерны Flame

1. **`game.isPaused = true`** — используй `GameState` enum + `pauseEngine()`/`resumeEngine()`
2. **`Flame.images.load()` в `update()`** — только в `onLoad()`
3. **`ComponentSet` прямые операции** — используй `game.children.toList()` (Flame 1.18)
4. **`onGameResize` без `isMounted` проверки** — компонент может получить resize до загрузки
5. **Глубина наследования > 3 уровней** — используй композицию (add child components)
6. **Hot reload для игровых файлов** — используй Hot Restart (Shift+R)

## Обязательные паттерны

### Компонент барабана
```dart
class ReelComponent extends PositionComponent with HasGameRef<SlotMachineGame> {
  // Прединициализация для update() — нет аллокации в горячем пути
  final _tempVector = Vector2.zero();

  late final List<SymbolComponent> _symbols;

  @override
  Future<void> onLoad() async {
    // Загрузка ассетов ТОЛЬКО в onLoad
    _symbols = await _createSymbols();
    await addAll(_symbols);
  }

  @override
  void update(double dt) {
    // СИНХРОННО! Нет await!
    if (!_isSpinning) return;
    _tempVector.setFrom(position);
    _updateScrollPosition(dt); // Без аллокации
  }
}
```

### ParticleSystemComponent — лимиты
```dart
// Для выигрышей > 20x ставки
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

### Audio — максимум 3 параллельных звука
```dart
class AudioService {
  // Только 3 слота: BGM + Spin + Effect
  static const int maxConcurrentSounds = 3;

  Future<void> playWin(int multiplier) async {
    await FlameAudio.play('sfx_win_${_winTier(multiplier)}.ogg');
  }

  // Coin counting с нарастанием pitch
  Future<void> playCoinCount(int coins) async {
    final rate = 1.0 + (coins / 100).clamp(0.0, 0.5);
    await FlameAudio.play('sfx_coins.ogg', volume: 1.0);
    // playbackRate управляется через AudioPlayer instance
  }
}
```

## Производительность

- Нет аллокации в `update()` или `render()` — прединициализируй Vector2, Rect, Paint
- `SpriteBatch` для > 20 одинаковых спрайтов (символы на барабанах!)
- `debugMode = true` только в debug builds
- `FpsTextComponent` только в debug builds
- Максимум 200 активных партиклей одновременно (SlotConfig.maxParticles)
