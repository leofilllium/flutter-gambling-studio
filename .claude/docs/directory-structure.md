# Директории Игровой Студии

Типовая структура проекта мини-игры в нашей студии:

```text
/
├── CLAUDE.md                    # Конфиг студии
├── pubspec.yaml                 # Зависимости Flame (1.18.x)
├── .claude/                     # Агенты и Навыки
├── lib/
│   ├── main.dart                # Точка входа
│   ├── app.dart                 # MaterialApp / GameWidget
│   ├── game/
│   │   ├── [game_name]_game.dart   # Наследник FlameGame
│   │   ├── [game_name]_world.dart  # Наследник World, хранит игровые компоненты
│   │   └── game_config.dart        # ТОЛЬКО константы (параметры баланса, скорости, размеры)
│   ├── components/
│   │   ├── [game_specific].dart    # Основные игровые компоненты (барабаны, сетка, ракетка, и т.д.)
│   │   ├── [element].dart          # Игровые элементы (символы, блоки, мячи, и т.д.)
│   │   ├── win_animation.dart      # VFX эффект (ParticleBurst)
│   │   └── [overlay].dart          # Визуальные оверлеи
│   ├── systems/
│   │   ├── [game_logic].dart       # Основная логика (RNG для gambling, match detector для puzzle, и т.д.)
│   │   └── [evaluator].dart        # Оценка результата (payline для gambling, score для arcade, и т.д.)
│   ├── models/
│   │   ├── [game_element].dart     # Модель игрового элемента
│   │   └── game_state.dart         # Sealed class состояний
│   ├── audio/
│   │   └── audio_service.dart      # Пул звуков
│   ├── screens/                    # Flutter виджеты
│   │   ├── main_menu.dart          # Меню с кнопкой Play
│   │   ├── game_screen.dart        # Обертка GameWidget
│   │   └── hud_widget.dart         # UI (ValueNotifiers: действие, счёт, состояние)
│   └── assets.dart                 # Константы путей SVG файлов
├── assets/
│   ├── images/
│   │   ├── sprites/                # SVG: игровые элементы
│   │   └── ui/                     # SVG: кнопки, панели
│   └── audio/
│       └── sfx/                    # OGG: эффекты, музыка
├── design/
│   ├── gdd/                        # Геймдизайн (концепты, системы)
│   └── balance/                    # Отчёты математики / баланса
├── tools/
│   └── simulate_balance.py         # Скрипт проверки баланса (RTP для gambling, difficulty для puzzle)
└── prototypes/                     # Sandboxes для /prototype
```

## Примеры структуры по жанрам

### Gambling (слот)
```
lib/systems/weighted_rng.dart       # Random.secure() — ЕДИНСТВЕННЫЙ RNG
lib/systems/payline_evaluator.dart  # Подсчёт выигрышей
lib/components/reel_component.dart  # Вращающийся барабан
lib/components/symbol_component.dart # Символ на барабане
design/balance/rtp-config.json      # Веса и выплаты
```

### Puzzle (match-3)
```
lib/systems/match_detector.dart     # Поиск совпадений на сетке
lib/systems/cascade_system.dart     # Каскадное заполнение
lib/components/grid_component.dart  # Игровая сетка
lib/components/tile_component.dart  # Элемент сетки
design/balance/level-config.json    # Конфигурация уровней
```

### Action (runner/shooter)
```
lib/systems/spawn_manager.dart      # Генерация препятствий/врагов
lib/systems/collision_system.dart   # Обработка столкновений
lib/components/player_component.dart # Игрок
lib/components/obstacle_component.dart # Препятствие
design/balance/difficulty-curve.json # Кривая сложности
```

### Physics (pinball/plinko)
```
lib/systems/physics_world.dart      # Forge2D мир
lib/components/ball_component.dart  # Шарик
lib/components/bumper_component.dart # Бампер/преграда
lib/components/flipper_component.dart # Флиппер (пинбол)
design/balance/physics-config.json  # Физические параметры
```
