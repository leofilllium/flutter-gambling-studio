<p align="center">
  <h1 align="center">Flutter Game Studio</h1>
  <p align="center">
    Универсальная студия для создания мини-игр любого жанра на Flutter + Flame.<br/>
    От концепта до релиза — правильная архитектура, честная математика, «сочный» UI.
    <br /><br />
    <strong>12 агентов · 24 навыка · 8 хуков · 6 правил · 24 архетипа игр</strong>
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/агенты-12-blueviolet" alt="12 агентов">
  <img src="https://img.shields.io/badge/навыки-24-green" alt="24 навыка">
  <img src="https://img.shields.io/badge/архетипы-24-orange" alt="24 архетипа">
  <img src="https://img.shields.io/badge/Flutter-3.27+-blue?logo=flutter" alt="Flutter 3.27+">
  <img src="https://img.shields.io/badge/Flame-1.18+-red" alt="Flame 1.18+">
  <a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/создано%20для-Claude%20Code-f5f5f5?logo=anthropic" alt="Built for Claude Code"></a>
</p>

---

## Зачем это нужно

Мини-игры сложнее, чем кажутся. Каждый жанр имеет свои подводные камни:

- **Gambling**: неправильные веса = нечестный RTP; `math.Random()` = уязвимость безопасности
- **Puzzle**: плохая difficulty curve = игроки бросают; state leakage = неправильный счёт
- **Arcade**: магические числа в спауне = неиграбельная сложность
- **Physics**: неправильные параметры Forge2D = неприятная физика
- **Все жанры**: аллокации в `update()` = джанк; слабый UI = игра выглядит дёшево

**Flutter Game Studio** решает всё это через систему специализированных агентов — математик балансирует игру, дизайнер пишет GDD, программист механик реализует логику, художник VFX добавляет «сочность». Хуки защищают от нарушений правил при коммите. Ворота качества не пустят плохой код на следующий этап.

Вы контролируете стратегию. Команда реализует.

---

## Поддерживаемые жанры

| Жанр | Примеры | Уникальные требования |
|------|---------|----------------------|
| **🎰 Gambling** | Слоты, рулетка, покер, crash, dice | RTP 95–97%, `Random.secure()`, Stateless Outcomes |
| **🧩 Puzzle** | Match-3, Tetris, Sokoban | Difficulty curves, match detection, каскады |
| **🏃 Arcade** | Runner, Shooter, Breakout | Spawning, collision, нарастающая сложность |
| **⚡ Physics** | Pinball, Plinko, Catapult | Forge2D, rigid bodies, реалистичная физика |
| **🎯 Casual** | Clicker, Idle, Rhythm | Прогрессия, retention, BPM синхронизация |
| **🃏 Card/Board** | Memory, Trivia, Solitaire | Колода, таймер, streak бонусы |

---

## Технологический стек

| Компонент | Технология |
|-----------|-----------|
| **Движок** | Flutter 3.27+ / Flame 1.18+ |
| **Язык** | Dart 3.6+ (null-safe, sealed classes, pattern matching) |
| **Рендеринг** | Impeller (iOS/Android), Skia (десктоп) |
| **Аудио** | flame_audio ^2.1.0 |
| **SVG** | flame_svg ^1.10.0 |
| **Physics** | forge2d (pinball, plinko, physics games) |
| **RNG** | `Random.secure()` для gambling; `Random()` для некритичных элементов |

---

## Иерархия студии

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1 — Директора (стратегические решения)            │
│    creative-director    technical-director               │
└─────────────────────────────────────────────────────────┘
              ↓                    ↓
┌─────────────────────────────────────────────────────────┐
│  Tier 2 — Специалисты игровых механик                   │
│    game-mathematician     game-designer                  │
│    mechanics-programmer   juice-artist                   │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  Tier 3 — Базовые специалисты (реализация и качество)   │
│    lead-programmer        performance-analyst            │
│    ui-programmer          sound-designer                 │
│    qa-tester              release-manager                │
└─────────────────────────────────────────────────────────┘
```

### Таблица агентов

| Агент | Роль | Зона ответственности |
|-------|------|---------------------|
| `creative-director` | Творческий директор | Видение игры, концепт, разрешение творческих конфликтов |
| `technical-director` | Технический директор | ADR, архитектурные решения, разрешение технических конфликтов |
| `game-mathematician` | Математик баланса | RTP (gambling), difficulty curves (puzzle), scoring (arcade) |
| `game-designer` | Геймдизайнер | GDD для любого жанра: механики, уровни, бонусы, прогрессия |
| `mechanics-programmer` | Программист механик | RNG, физика, коллизии, match detection, spawning |
| `juice-artist` | Художник VFX | Партикли, анимации, «сочность» для любого жанра |
| `lead-programmer` | Ведущий программист | Архитектура, ревью кода, Flame 1.18.x стандарты |
| `performance-analyst` | Аналитик производительности | FPS, память, SpriteBatch, утечки текстур |
| `ui-programmer` | Flutter UI | Экраны, HUD, Win оверлеи, anti-slop дизайн |
| `sound-designer` | Звуковой дизайнер | BGM, SFX для всех жанров, pitch scaling |
| `qa-tester` | QA инженер | Тест-кейсы, edge cases, RNG дистрибуция, state leakage |
| `release-manager` | Менеджер релизов | Финальная проверка перед деплоем |

> **Язык**: все агенты общаются на **русском языке**. Исключения: код, пути файлов, CLI команды.

---

## Дорожная карта разработки

```
  ИДЕЯ          КОНЦЕПТ         ДИЗАЙН          КОД           QA          РЕЛИЗ
    │               │               │              │             │             │
/brainstorm    /gate-check    /design-system   /team-       /code-       /release-
/auto-idea      concept       /design-review   dev          review       checklist
/autocreate                   /map-systems     /gate-check  /balance-
               /gate-check    /balance-check    code        check
                design                         /gate-check  /gate-check
                                                            qa
```

### Ворота качества (`/gate-check`)

| Команда | Что проверяет | Блокеры |
|---------|--------------|---------|
| `/gate-check concept` | Готов ли концепт к дизайну? | Нет GDD, не определён жанр |
| `/gate-check design` | Готов ли GDD к имплементации? | Нет 8 секций, нет balance config |
| `/gate-check code` | Готов ли код к QA? | math.Random() (gambling), захардкоженные параметры |
| `/gate-check qa` | Готов ли к релизу? | RTP вне 95–97% (gambling), нет edge case тестов |

---

## Все команды

### Создание игры

| Команда | Описание |
|---------|----------|
| `/start` | Онбординг и маршрутизация — с чего начать |
| `/brainstorm [хинт]` | Интерактивный концепт любого жанра |
| `/auto-idea` | Автономный концепт из 24 архетипов без вопросов |
| `/auto-idea --list` | Показать все 24 архетипа (A–X) |
| `/auto-idea --archetype [A-X]` | Развернуть конкретный архетип |
| `/autocreate` | Zero-to-playable: концепт + ассеты + код автономно |
| `/autocreate --from-concept` | Реализовать уже сохранённый концепт |

### Дизайн и архитектура

| Команда | Описание |
|---------|----------|
| `/map-systems` | Декомпозиция концепта на Flame-системы |
| `/design-system [система]` | GDD для одной механики |
| `/prototype [механика]` | Изолированный прототип для тестирования juiciness |
| `/architecture-decision [решение]` | Architecture Decision Record (ADR) |

### Ассеты

| Команда | Описание |
|---------|----------|
| `/generate-asset [тип] [имя]` | SVG или PNG (через Google Imagen API) |
| `/generate-png-asset [описание]` | PNG с удалением фона через Google AI Studio |
| `/svg-to-png [путь]` | Конвертация SVG → PNG |

### Ревью и ворота

| Команда | Описание |
|---------|----------|
| `/code-review` | Полное ревью: RNG (gambling), Flame API, State, тесты |
| `/design-review` | Ревью GDD: 8 секций, математика, edge cases |
| `/ui-audit` | Автоматический аудит UI на anti-slop качество |
| `/gate-check [этап]` | Ворота перехода с вердиктом PASS / CONCERNS / FAIL |

### Баланс и математика

| Команда | Описание |
|---------|----------|
| `/balance-check` | Gambling: симуляция 1М спинов (RTP). Puzzle: difficulty curve. Arcade: spawn balance |

### Диагностика

| Команда | Описание |
|---------|----------|
| `/perf-profile [область]` | Профилирование FPS / памяти / партиклей / аудио |
| `/tech-debt` | Сканирование и реестр технического долга |
| `/hotfix [описание]` | Экстренное исправление с аудит-следом |

### Командная работа

| Команда | Описание |
|---------|----------|
| `/team-dev [описание]` | Оркестрация: game-designer → game-mathematician → mechanics-programmer → juice-artist |

### Работа с существующим проектом

| Команда | Описание |
|---------|----------|
| `/continue-project` | Восстановить контекст и продолжить с точки остановки |
| `/add-feature [фича]` | Добавить фичу в готовую игру (с пересчётом баланса) |
| `/release-checklist` | Финальный чеклист перед деплоем |

---

## Архетипы мини-игр (A–X)

### 🎰 Gambling (A–L)

| ID | Название | Жанр | Уникальная механика |
|----|----------|------|---------------------|
| A | Неоновый Спин | 3-барабанный слот | Near Miss система, каскадная остановка |
| B | Счастливое Колесо | Колесо фортуны | Сектора с выплатами, множители |
| C | Покер Экспресс | Видео-покер | 5 карт, Hold функция, двойная ставка |
| D | Фруктовая Буря | 5-барабанный слот | Каскадные символы (Avalanche), Free Spins |
| E | Скрэтч Делюкс | Скретч-карты | Мгновенные выигрыши, 3 попытки |
| F | Рулетка Неон | Мини-рулетка | Европейская рулетка, внешние/внутренние ставки |
| G | Космический Взлёт | Crash | Flame Physics, кривая ускорения, particle хвост |
| H | Неоновый Каскад | Plinko | Forge2D, физика отскоков, каскады |
| I | Золотой Бульдозер | Coin Pusher | 2D rigid bodies, физическое толкание монет |
| J | Минное Поле | Mines | Геометрический рост множителя |
| K | Квантовые Кости | Dice Physics | Честная 2D физика броска |
| L | Башня Дракона | Tower Climber | Risk/Reward, выбор 1 из 3 ячеек на этаж |

### 🧩 Puzzle (M–O)

| ID | Название | Жанр | Уникальная механика |
|----|----------|------|---------------------|
| M | Кристальный Каскад | Match-3 | Свайп, цепные реакции, бустеры |
| N | Неоновый Тетрис | Tetris-like | Ghost piece, T-spin бонус |
| O | Пиксельный Сокобан | Push-puzzle | 50+ уровней, undo, минимум ходов |

### 🏃 Arcade (P–R)

| ID | Название | Жанр | Уникальная механика |
|----|----------|------|---------------------|
| P | Неоновый Раннер | Endless Runner | Авто-бег, нарастающая скорость, particle trail |
| Q | Кибер Брейкаут | Breakout | Разрушаемые блоки, пауэрапы, мульти-мяч |
| R | Звёздный Шутер | Vertical Shooter | Авто-стрельба, волны врагов, боссы |

### ⚡ Physics (S–T)

| ID | Название | Жанр | Уникальная механика |
|----|----------|------|---------------------|
| S | Неоновый Пинбол | Pinball | Forge2D флипперы, бамперы, мульти-болл |
| T | Катапульта | Projectile | Прицеливание, разрушаемые структуры |

### 🎯 Casual (U–V)

| ID | Название | Жанр | Уникальная механика |
|----|----------|------|---------------------|
| U | Тап Мастер | Rhythm/Tap | Ноты в ритм, combo, нарастающий BPM |
| V | Золотой Кликер | Idle/Clicker | Нажатия → апгрейды → автоматизация, prestige |

### 🃏 Card/Board (W–X)

| ID | Название | Жанр | Уникальная механика |
|----|----------|------|---------------------|
| W | Нейро Память | Memory Card | Переворот пар, таймер, 4×4 → 6×6 |
| X | Квиз Баттл | Trivia Quiz | 4 варианта, streak бонусы, категории |

```bash
/auto-idea --archetype A   # Неоновый Спин (слот)
/auto-idea --archetype M   # Кристальный Каскад (match-3)
/auto-idea --archetype P   # Неоновый Раннер (arcade)
/auto-idea --list           # Показать все 24 архетипа
/auto-idea                  # Случайная уникальная генерация
```

---

## Критические правила игры

### Для всех жанров

```dart
// ✅ GameState — sealed class обязателен
sealed class GameState {}
class IdleState extends GameState {}
class PlayingState extends GameState { final int level; }
class PausedState extends GameState { final GameState prev; }
class GameOverState extends GameState { final int score; }

// ✅ Все параметры в GameConfig
class GameConfig {
  static const double playerSpeed = 200.0;
  static const int gridWidth = 8;
  static const Duration comboTimeout = Duration(seconds: 2);
}

// ❌ Запрещено — magic numbers
if (score > 1000) spawnBoss(); // Откуда взялось 1000?
```

### Дополнительно для Gambling

```dart
// ✅ ТОЛЬКО Random.secure()
class WeightedRNG {
  final _rng = Random.secure(); // Не Random()!
}

// ✅ Stateless Outcomes — результат ДО анимации
Future<void> spin() async {
  final outcome = _rng.computeOutcome(); // Сначала результат
  await _animateReels(outcome.symbols);  // Потом анимация
}

// ❌ Захардкоженные вероятности — запрещено
if (Random().nextDouble() < 0.15) triggerBonus();
```

**RTP диапазон**: 95–97% при 1,000,000 симуляций. `/balance-check` обязателен перед `/gate-check qa`.

---

## Автоматизация и хуки

| Хук | Когда | Что делает |
|-----|-------|-----------|
| `session-start.sh` | Старт сессии | Показывает состояние проекта, GDD, последние коммиты |
| `detect-gaps.sh` | Старт сессии | Ищет нарушения (gambling: `math.Random()`), отсутствующие файлы |
| `validate-commit.sh` | Перед `git commit` | Gambling: блокирует `math.Random()`, захардкоженный RTP. Все: невалидный JSON, `print()` |
| `validate-push.sh` | Перед `git push` | Предупреждает при push в main без ворот |
| `validate-assets.sh` | После Write/Edit | Проверяет именование ассетов (`sprite_X`, `sfx_X`) |
| `pre-compact.sh` | Перед сжатием контекста | Сохраняет чекпоинт в `production/session-state/active.md` |
| `session-stop.sh` | Завершение сессии | Логирует изменения в `production/session-logs/` |
| `log-agent.sh` | Запуск субагента | Аудит-след всех вызовов агентов |

### Правила кода (path-based)

| Правило | Применяется к | Содержание |
|---------|--------------|-----------|
| `game-code.md` | `lib/**/*.dart` | GameConfig, GameState sealed class, защита от двойного клика |
| `engine-code.md` | `lib/game/**/*.dart` | Flame 1.18.x API (World, CameraComponent, HasTimeScale) |
| `ui-code.md` | `lib/screens/**/*.dart` | ValueNotifier, Win оверлеи, anti-slop требования |
| `test-standards.md` | `test/**/*.dart` | AAA структура, RNG дистрибуция (gambling), edge cases |
| `data-files.md` | `design/balance/**/*.json` | Схема rtp-config.json (gambling), balance configs |
| `design-docs.md` | `design/**/*.md` | 8 обязательных секций GDD, статус документа |

---

## Структура проекта

```
flutter-game-studio/
├── CLAUDE.md                          # Главная конфигурация студии
├── .claude/
│   ├── settings.json                  # Права, хуки, statusline
│   ├── agents/                        # 12 специализированных агентов
│   │   ├── creative-director.md
│   │   ├── technical-director.md
│   │   ├── game-mathematician.md      # RTP + difficulty curves + score balance
│   │   ├── game-designer.md           # GDD для всех жанров
│   │   ├── mechanics-programmer.md    # RNG/match/spawn/physics
│   │   ├── juice-artist.md
│   │   ├── lead-programmer.md
│   │   ├── performance-analyst.md
│   │   ├── ui-programmer.md
│   │   ├── sound-designer.md
│   │   ├── qa-tester.md
│   │   └── release-manager.md
│   ├── skills/                        # 24 слэш-команды
│   │   ├── start/  brainstorm/  auto-idea/  autocreate/
│   │   ├── map-systems/  design-system/  prototype/
│   │   ├── generate-asset/  generate-png-asset/  svg-to-png/
│   │   ├── team-dev/  balance-check/  add-feature/
│   │   ├── code-review/  design-review/  ui-audit/
│   │   ├── gate-check/  release-checklist/  continue-project/
│   │   ├── hotfix/  perf-profile/  tech-debt/  architecture-decision/
│   │   └── [team-gambling/ — устарело, заменён team-dev/]
│   ├── hooks/                         # 8 автоматических скриптов
│   ├── rules/                         # 6 path-based правил
│   │   ├── game-code.md  engine-code.md  ui-code.md
│   │   ├── test-standards.md  data-files.md  design-docs.md
│   └── docs/                          # Документация студии
├── production/
│   ├── session-state/active.md        # Текущий чекпоинт (gitignored)
│   └── session-logs/                  # Аудит-лог (gitignored)
└── [игровые проекты создаются здесь]
    ├── lib/game/game_config.dart      # Все игровые константы
    ├── lib/models/game_state.dart     # sealed class состояний
    ├── assets/
    ├── design/gdd/
    ├── design/balance/
    └── tools/simulate_balance.py
```

---

## Быстрый старт

### Требования

- [Flutter SDK](https://docs.flutter.dev/get-started/install) 3.27+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`npm install -g @anthropic-ai/claude-code`)
- Python 3 (для симуляции баланса)

### Установка

```bash
git clone https://github.com/leofillium/flutter-gambling-studio.git
cd flutter-gambling-studio
claude
```

### Пути

**Хочу игру прямо сейчас (любой жанр):**
```
/autocreate
```
Автономный конвейер: концепт → SVG-ассеты → Flutter код → `pubspec.yaml`. Без вопросов.

**Хочу контролировать каждый шаг:**
```
/brainstorm          # Выбрать жанр и создать концепт вместе
/gate-check concept  # Проверить готовность концепта
/design-system       # Написать GDD для механик
/gate-check design   # Проверить готовность GDD
/team-dev            # Передать команде программистов
/code-review         # Проверить написанный код
/balance-check       # Симуляция баланса
/gate-check qa       # Финальные ворота
/release-checklist   # Готово к релизу
```

---

## Лицензия

MIT License. Подробности в [LICENSE](LICENSE).
