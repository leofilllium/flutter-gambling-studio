# Директории Гемблинг Студии

Типовая структура проекта слота в нашей студии:

```text
/
├── CLAUDE.md                    # Конфиг студии
├── pubspec.yaml                 # Зависимости Flame (1.18.x)
├── .claude/                     # Агенты и Навыки
├── lib/
│   ├── main.dart                # Точка входа
│   ├── app.dart                 # MaterialApp / GameWidget
│   ├── game/
│   │   ├── slot_machine_game.dart  # Наследник FlameGame
│   │   ├── slot_machine_world.dart # Наследник FlameWorld, хранит барабаны
│   │   └── slot_config.dart        # ТОЛЬКО константы (RTP, множители, скорости)
│   ├── components/
│   │   ├── reel_component.dart     # Вращающийся барабан (бесконечный скролл)
│   │   ├── symbol_component.dart   # Иконка на барабане
│   │   ├── win_animation.dart      # VFX эффект (ParticleBurst)
│   │   └── payline_overlay.dart    # Визуализация линии: \ / -
│   ├── systems/
│   │   ├── weighted_rng.dart       # Строго Random.secure()
│   │   └── payline_evaluator.dart  # Подсчет выигрышей
│   ├── models/
│   │   ├── slot_symbol.dart        # Модель символа [isWild, weight, multiplier]
│   │   └── game_state.dart         # Sealed class [Idle, Spinning, Evaluating, Win]
│   ├── audio/
│   │   └── audio_service.dart      # Пул звуков
│   ├── screens/                    # Flutter виджеты
│   │   ├── main_menu.dart          # Меню с кнопкой Play
│   │   ├── game_screen.dart        # Обертка GameWidget
│   │   └── hud_widget.dart         # UI (ValueNotifiers: Spin, Bet+, Bet-, Balance)
│   └── assets.dart                 # Константы путей SVG файлов
├── assets/
│   ├── images/
│   │   ├── sprites/                # SVG: вишни, бары, семерки
│   │   └── ui/                     # SVG: кнопки, панели
│   └── audio/
│       └── sfx/                    # OGG: спины, монеты, Near Miss
├── design/
│   ├── gdd/                        # Геймдизайн (концепты, системы)
│   └── balance/                    # Отчеты математики (rtp-config.json)
├── tools/
│   └── simulate_rtp.py             # Скрипт проверки вероятностей на 1М спинов
└── prototypes/                     # Sandboxes для /prototype
```
