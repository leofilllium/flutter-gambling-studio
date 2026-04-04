# Технические стандарты Игровой Студии

## Flutter + Flame 1.18.x

### Математика и RNG
- **Для gambling жанра КРИТИЧЕСКИ**: НИКОГДА не используйте `math.Random()`. ТОЛЬКО `Random.secure()` для:
  - Выбора символов на барабанах
  - Раздачи карт в покере
  - Остановки колеса рулетки / фортуны
  - Триггеров бонусных механик
- **Для остальных жанров**: `Random()` допустим для не-критичных элементов (визуальные эффекты, генерация уровней). Для scoring/leaderboard-значимых механик рекомендуется `Random.secure()`.
- **Stateless Outcomes**: Результат действия вычисляется ДО начала анимации. Анимация просто "проигрывает" предопределённый сценарий. Критично для gambling (RTP), полезно для всех жанров (match-3 каскады, физика).
- **Balance Tuning**: Все игровые параметры хранятся в `game_config.dart` или берутся из JSON конфига, сгенерированного `game-mathematician`.

### Flame API (1.18.x)

- Наследуйте главный класс от `FlameGame`.
- Коллизии всегда объявляем на `World`, а не на `FlameGame`:
  `class GameWorld extends World with HasCollisionDetection {}`
- Используйте обновленную `CameraComponent`:
  `camera = CameraComponent(world: _world);`
- Никаких `.isPaused = true`. Используйте `GameState` (sealed class: Idle, Playing, Paused, GameOver).

### Визуализаторы и Партикли

Для сочности мини-игр мы используем эффекты *ParticleSystemComponent*.
- При ключевых событиях (выигрыш, combo, level-up) спавните тематические частицы:
  `ParticleSystemComponent(particle: Particle.generate(count: 50, generator: ...))`
- Настройки эффекта (glow, drop shadow) реализуются через Flutter Overlay поверх Flame, так как во Flame сложные фильтры потребляют много ресурсов.

### Звук
- Используйте пакет `flame_audio` `^2.1.0`.
- Ограничивайте параллельное звучание: максимум 3 накладывающихся звука (например: 1 BGM loop, 1 Action sound loop, 1 Effect Overlay).
- Для нарастающих эффектов используйте pitch scaling: `playbackRate` 1.0 → 1.5.

### Ассеты SVG
- Для графики используется `flame_svg` `^1.10.0`.
- Ассеты генерируются через команду `/generate-asset`.
- Паттерн наименования:
  `background_X` (фоны)
  `sprite_X` (игровые элементы: символы, фигуры, объекты)
  `ui_X` (кнопки, панели)
  `icon_X` (значки, иконки интерфейса)
