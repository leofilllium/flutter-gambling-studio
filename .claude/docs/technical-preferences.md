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

### Графические ассеты
- Для `/autocreate` в Codex графика по умолчанию — **PNG через GPT Images 2.0**,
  а если GPT Images 2.0 не сработал — повтор через **GPT Images / default Codex image generation**,
  напрямую из концепта и Design DNA. Нельзя сначала генерировать SVG, а потом конвертировать
  их в PNG: это теряет материал, свет, стиль и привязку к миру игры.
- SVG остаётся fallback-режимом для не-Codex среды или явного `--svg`.
- Выбранный формат фиксируется в `design/asset-format.md`.
- Если `format: png`, UI использует `Image.asset(...)` и реальные `.png` пути.
- Если `format: svg`, UI использует `SvgPicture.asset(...)` / `flame_svg`.
- `/svg-to-png` предназначен только для legacy SVG или явного пользовательского запроса,
  не как нормальный путь `/autocreate`.
- Для простых PNG-ассетов prompt должен просить плоский ключевой фон (chroma key: по умолчанию
  `pure magenta #FF00FF`, либо `pure green #00FF00`, если в палитре есть пурпур/розовый) без
  теней/градиентов/сцены, затем фон вырезается через `python3 tools/cutout.py <файл> --type sprite`.
  Белый фон запрещён у объектов со светлыми/белыми областями — они сливаются с фоном.
  Ручной `magick -fuzz -transparent white` запрещён: рвёт альфу и оставляет ореол.
  Для background-изображений фон не удаляется.
- Паттерн наименования:
  `background_X` (фоны)
  `sprite_X` (игровые элементы: символы, фигуры, объекты)
  `ui_X` (кнопки, панели)
  `icon_X` (значки, иконки интерфейса)
