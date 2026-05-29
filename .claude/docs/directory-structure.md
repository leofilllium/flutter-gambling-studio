# Директории Игровой Студии

Студия поддерживает **5 вариантов архитектурной структуры проекта**.
При каждом запуске `/autocreate` один вариант выбирается автоматически через `design/structure.md`.
Это обеспечивает разнообразие между играми — каждая получает свою уникальную организацию кода.

---

## V1 — Layer Architecture (Слоевая)

Классическая MVC-подобная организация: каждый слой в отдельной папке.

```text
lib/
├── main.dart
├── app.dart                          # MaterialApp, именованные routes
├── assets.dart                       # Константы путей ко всем ассетам
├── game/
│   ├── [name]_game.dart              # FlameGame
│   ├── [name]_world.dart             # World with HasCollisionDetection
│   └── game_config.dart              # Все игровые константы
├── components/
│   ├── [main_component].dart
│   ├── [element_component].dart
│   ├── win_animation.dart
│   ├── ambient_particles.dart
│   └── screen_shake.dart
├── systems/
│   ├── [game_logic].dart             # RNG / match_detector / spawn_manager
│   └── [evaluator].dart              # Чистая функция подсчёта результата
├── models/
│   ├── game_state.dart               # Sealed class состояний
│   └── [game_element].dart
├── screens/
│   ├── splash_screen.dart
│   ├── main_menu.dart
│   ├── game_screen.dart
│   ├── hud_widget.dart
│   └── [others].dart                 # 12+ экранов
├── widgets/
│   └── [shared_widgets].dart
├── audio/
│   └── audio_service.dart
└── theme/
    ├── game_theme.dart
    └── animations.dart
```

---

## V2 — Feature Slice (По фичам)

Gameplay (Flame) отделён от UI (Flutter) и сервисов — каждая фича в своей папке.

```text
lib/
├── main.dart
├── assets.dart
├── core/
│   ├── app.dart                      # MaterialApp, routes
│   └── theme/
│       ├── game_theme.dart
│       └── animations.dart
├── gameplay/                         # Всё Flame: игра + компоненты + логика
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   ├── components/
│   │   ├── [main_component].dart
│   │   ├── win_animation.dart
│   │   └── ambient_particles.dart
│   └── systems/
│       ├── [game_logic].dart
│       └── [evaluator].dart
├── ui/                               # Всё Flutter: экраны + виджеты
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── main_menu.dart
│   │   ├── game_screen.dart
│   │   ├── hud_widget.dart
│   │   └── [others].dart
│   └── widgets/
│       └── [shared_widgets].dart
├── domain/                           # Модели + состояния + конфиг
│   ├── game_config.dart
│   ├── game_state.dart
│   └── [game_element].dart
└── services/                         # Внешние сервисы
    └── audio_service.dart
```

---

## V3 — Presentation-Domain-Data (PDD)

Чёткое разделение: presentation (Flutter UI), domain (бизнес-логика + Flame), data (конфиги).

```text
lib/
├── main.dart
├── app.dart
├── assets.dart
├── presentation/                     # Flutter UI слой
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
├── domain/                           # Бизнес-логика + Flame
│   ├── game/
│   │   ├── [name]_game.dart
│   │   └── [name]_world.dart
│   ├── systems/
│   │   ├── [game_logic].dart
│   │   └── [evaluator].dart
│   └── models/
│       ├── game_state.dart
│       └── [game_element].dart
├── data/                             # Конфиги и сервисы
│   ├── config/
│   │   └── game_config.dart
│   └── services/
│       └── audio_service.dart
└── components/                       # Flame визуальные компоненты
    ├── [main_component].dart
    ├── win_animation.dart
    └── ambient_particles.dart
```

---

## V4 — Module Architecture (Модульная)

По функциональным модулям: engine, mechanics, visuals, interface, infrastructure.

```text
lib/
├── main.dart
├── app.dart
├── assets.dart
├── engine/                           # Ядро Flame
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   └── game_config.dart
├── mechanics/                        # Игровая логика
│   ├── systems/
│   │   ├── [game_logic].dart
│   │   └── [evaluator].dart
│   └── models/
│       ├── game_state.dart
│       └── [game_element].dart
├── visuals/                          # Визуальный слой (Flame компоненты + тема)
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
└── infrastructure/                   # Внешние зависимости
    └── audio/
        └── audio_service.dart
```

---

## V5 — Vertical Slice (Вертикальные срезы)

Организация по игровым областям: bootstrap, arena, rules, hud, menus, foundation.

```text
lib/
├── main.dart
├── bootstrap/                        # Точка входа приложения
│   ├── app.dart
│   └── assets.dart
├── arena/                            # Игровое поле (Flame)
│   ├── [name]_game.dart
│   ├── [name]_world.dart
│   └── components/
│       ├── [main_component].dart
│       ├── win_animation.dart
│       └── ambient_particles.dart
├── rules/                            # Правила и механики
│   ├── systems/
│   │   ├── [game_logic].dart
│   │   └── [evaluator].dart
│   ├── models/
│   │   ├── game_state.dart
│   │   └── [game_element].dart
│   └── config/
│       └── game_config.dart
├── hud/                              # HUD и игровые оверлеи
│   ├── hud_widget.dart
│   ├── win_overlay.dart
│   └── bonus_overlay.dart
├── menus/                            # Экраны меню
│   ├── splash_screen.dart
│   ├── main_menu.dart
│   ├── game_screen.dart
│   └── [others].dart
└── foundation/                       # Общая база
    ├── audio/
    │   └── audio_service.dart
    ├── theme/
    │   ├── game_theme.dart
    │   └── animations.dart
    └── widgets/
        └── [shared_widgets].dart
```

---

## Как выбирается вариант

В Фазе 2 `/autocreate` Python-скрипт записывает выбранный вариант в `design/structure.md`:

```python
import time
variant = (int(time.time()) % 5) + 1  # равномерно 1–5
```

`design/structure.md` содержит полный маппинг путей для всех категорий файлов.
Агенты Фазы 4 читают этот файл через `lib/contracts.md` и создают все файлы по указанным путям.

---

## Инварианты (одинаковы для ВСЕХ вариантов)

- `lib/main.dart` — точка входа, всегда в корне `lib/`
- `assets/` — папка ассетов, всегда в корне проекта
- `design/` — GDD и balance docs, всегда в корне
- `GameConfig` содержит ТОЛЬКО константы, никакой логики
- `GameState` — sealed class, присутствует в каждом варианте
- `AudioService` — max 3 параллельных звука
- Пути ассетов регистрируются в `pubspec.yaml` по одним и тем же директориям `assets/`

---

## Примеры ключевых файлов по жанрам (V1 paths)

### Gambling (слот)
```
lib/systems/weighted_rng.dart       # Random.secure() — ЕДИНСТВЕННЫЙ RNG
lib/systems/payline_evaluator.dart  # Подсчёт выигрышей
lib/components/reel_component.dart  # Вращающийся барабан
lib/components/symbol_component.dart
design/balance/rtp-config.json
```

### Puzzle (match-3)
```
lib/systems/match_detector.dart
lib/systems/cascade_system.dart
lib/components/grid_component.dart
lib/components/tile_component.dart
design/balance/level-config.json
```

### Action (runner/shooter)
```
lib/systems/spawn_manager.dart
lib/systems/collision_system.dart
lib/components/player_component.dart
lib/components/obstacle_component.dart
design/balance/difficulty-curve.json
```

### Physics (pinball/plinko)
```
lib/systems/physics_world.dart
lib/components/ball_component.dart
lib/components/bumper_component.dart
lib/components/flipper_component.dart
design/balance/physics-config.json
```
