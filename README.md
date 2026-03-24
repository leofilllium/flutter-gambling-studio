<p align="center">
  <h1 align="center">Flutter Gambling Studio</h1>
  <p align="center">
    Специализированная студия для создания мини-гемблинг игр на Flutter + Flame.<br/>
    От концепта до релиза — без ошибок RNG, без проблем с RTP, без сломанной архитектуры.
    <br /><br />
    <strong>12 агентов · 20 навыков · 8 хуков · 6 правил · 1 дорожная карта</strong>
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/агенты-12-blueviolet" alt="12 агентов">
  <img src="https://img.shields.io/badge/навыки-20-green" alt="20 навыков">
  <img src="https://img.shields.io/badge/хуки-8-orange" alt="8 хуков">
  <img src="https://img.shields.io/badge/Flutter-3.27+-blue?logo=flutter" alt="Flutter 3.27+">
  <img src="https://img.shields.io/badge/Flame-1.18+-red" alt="Flame 1.18+">
  <a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/создано%20для-Claude%20Code-f5f5f5?logo=anthropic" alt="Built for Claude Code"></a>
</p>

---

## Зачем это нужно

Гемблинг игры — один из самых технически требовательных жанров:

- **Математика**: неправильные веса символов = RTP вне норм = нечестная игра
- **RNG**: `math.Random()` вместо `Random.secure()` = уязвимость безопасности
- **Состояние**: state leakage между спинами = неправильный баланс игрока
- **Производительность**: аллокации в `update()` = джанк при вращении барабанов
- **Архитектура**: захардкоженные вероятности = невозможность балансировки

**Flutter Gambling Studio** решает всё это через систему специализированных агентов, которые знают gambling-специфику лучше обычного ИИ-ассистента. Математик считает RTP и итерирует веса. Программист слотов пишет только `Random.secure()`. Хуки блокируют коммит с нарушениями. Ворота качества не пустят плохой код в следующий этап.

Вы контролируете стратегию. Команда реализует.

---

## Технологический стек

| Компонент | Технология |
|-----------|-----------|
| **Движок** | Flutter 3.27+ / Flame 1.18+ |
| **Язык** | Dart 3.6+ (null-safe, sealed classes, pattern matching) |
| **Рендеринг** | Impeller (iOS/Android), Skia (десктоп) |
| **Аудио** | flame_audio ^2.1.0 |
| **SVG** | flame_svg ^1.10.0 |
| **RNG** | `Random.secure()` — жёсткое требование |
| **Специализация** | Мини-гемблинг игры (mobile-first) |

---

## Содержание

- [Что включено](#что-включено)
- [Иерархия студии](#иерархия-студии)
- [Дорожная карта разработки](#дорожная-карта-разработки)
- [Все команды](#все-команды)
- [Архетипы мини-игр](#архетипы-мини-игр)
- [Критические gambling-правила](#критические-gambling-правила)
- [Автоматизация и хуки](#автоматизация-и-хуки)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [Кастомизация](#кастомизация)

---

## Что включено

| Категория | Кол-во | Описание |
|-----------|--------|----------|
| **Агенты** | 12 | Специализированные субагенты: директора, математики, дизайнеры, художники, программисты, QA |
| **Навыки (слэш-команды)** | 20 | Полный пайплайн: от концепта до ADR и экстренных фиксов |
| **Хуки автоматизации** | 8 | Автоматическая защита от нарушений gambling-правил при коммите |
| **Правила кода** | 6 | Path-based стандарты, автоматически применяемые по типу файла |
| **Документация** | 6 | Coding standards, context management, coordination rules и др. |
| **Шаблоны** | 2 | GDD концепт и RTP design документы |

---

## Иерархия студии

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1 — Директора (стратегические решения)            │
│    creative-director    technical-director               │
└─────────────────────────────────────────────────────────┘
              ↓                    ↓
┌─────────────────────────────────────────────────────────┐
│  Tier 2 — Специалисты гемблинга (gambling-уникальные)   │
│    rtp-mathematician      gambling-game-designer         │
│    slot-programmer        juice-artist                   │
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
| `rtp-mathematician` | Математик RTP | Веса символов, RTP расчёт, симуляция 1М спинов, волатильность |
| `gambling-game-designer` | Геймдизайнер | GDD документы, механики барабанов, линии выплат, бонусы |
| `slot-programmer` | Программист слотов | Логика вращения, RNG, PaylineEvaluator, GameState machine |
| `juice-artist` | Художник VFX | Партикли, анимации, каскадная остановка, "сочность" |
| `lead-programmer` | Ведущий программист | Архитектура, ревью кода, Flame 1.18.x стандарты |
| `performance-analyst` | Аналитик производительности | FPS, память, SpriteBatch, утечки текстур |
| `ui-programmer` | Flutter UI | Экраны, HUD (баланс/ставка/спин), Win оверлеи |
| `sound-designer` | Звуковой дизайнер | BGM, SFX (спин/выигрыш/Near Miss), pitch scaling |
| `qa-tester` | QA инженер | Тест-кейсы, edge cases, RNG дистрибуция, state leakage |
| `release-manager` | Менеджер релизов | Финальная проверка перед деплоем |

> **Язык**: все агенты общаются на **русском языке**. Исключения: код, пути файлов, CLI команды.

---

## Дорожная карта разработки

Студия обеспечивает полный путь от идеи до релиза с воротами качества на каждом переходе:

```
  ИДЕЯ          КОНЦЕПТ         ДИЗАЙН          КОД           QA          РЕЛИЗ
    │               │               │              │             │             │
/brainstorm    /gate-check    /design-system   /team-       /code-       /release-
/auto-idea      concept       /design-review   gambling     review       checklist
/autocreate                   /map-systems     /gate-check  /balance-
               /gate-check    /balance-check    code        check
                design                         /gate-check  /gate-check
                                                            qa
```

### Ворота качества (`/gate-check`)

Перед каждым переходом между этапами проходи `/gate-check`:

| Команда | Что проверяет | Блокеры |
|---------|--------------|---------|
| `/gate-check concept` | Готов ли концепт к дизайну? | Нет GDD, не определён RTP |
| `/gate-check design` | Готов ли GDD к имплементации? | Нет 8 секций, нет rtp-config.json |
| `/gate-check code` | Готов ли код к QA? | math.Random(), захардкоженные RTP, failing tests |
| `/gate-check qa` | Готов ли к релизу? | RTP вне 95–97%, нет edge case тестов |

---

## Все команды

### Создание игры

| Команда | Описание |
|---------|----------|
| `/start` | Онбординг и маршрутизация — с чего начать |
| `/brainstorm [хинт]` | Интерактивный концепт: RTP-профиль, механики, тема |
| `/auto-idea` | Автономный концепт из 6 архетипов без вопросов |
| `/auto-idea --list` | Показать все 6 архетипов с описанием |
| `/auto-idea --archetype [A-F]` | Развернуть конкретный архетип |
| `/autocreate` | Zero-to-playable: концепт + ассеты + код автономно |
| `/autocreate --from-concept` | Реализовать уже сохранённый концепт |

### Дизайн и архитектура

| Команда | Описание |
|---------|----------|
| `/map-systems` | Декомпозиция концепта на Flame-системы с графом зависимостей |
| `/design-system [система]` | GDD для одной механики (reel/payline/free-spins/bonus) |
| `/prototype [механика]` | Изолированный прототип для тестирования juiciness |
| `/architecture-decision [решение]` | Создать ADR — Architecture Decision Record |

### Ассеты

| Команда | Описание |
|---------|----------|
| `/generate-asset [тип] [имя]` | SVG-ассет: `sprite_cherry`, `ui_spin_button`, `background_neon` |

### Ревью и ворота

| Команда | Описание |
|---------|----------|
| `/code-review` | Полное ревью: RNG, Flame API, State integrity, тесты |
| `/design-review` | Ревью GDD: 8 секций, математика, edge cases |
| `/gate-check [этап]` | Ворота перехода с вердиктом PASS / CONCERNS / FAIL |

### Баланс и математика

| Команда | Описание |
|---------|----------|
| `/balance-check` | Симуляция 1,000,000 спинов, проверка RTP 95–97% |

### Диагностика

| Команда | Описание |
|---------|----------|
| `/perf-profile [область]` | Профилирование FPS / памяти / партиклей / аудио |
| `/tech-debt` | Сканирование и реестр технического долга |
| `/hotfix [описание]` | Экстренное исправление с аудит-следом |

### Командная работа

| Команда | Описание |
|---------|----------|
| `/team-gambling [описание]` | Оркестрация: game-designer → rtp-mathematician → slot-programmer → juice-artist → qa |

### Работа с существующим проектом

| Команда | Описание |
|---------|----------|
| `/continue-project` | Восстановить контекст и продолжить с точки остановки |
| `/add-feature [фича]` | Добавить фичу с пересчётом RTP (Wild, Free Spins, Jackpot) |
| `/release-checklist` | Финальный gambling-специфичный чеклист перед деплоем |

---

## Архетипы мини-игр (A–F)

| ID | Название | Жанр | Уникальная механика |
|----|----------|------|---------------------|
| A | Неоновый Спин | 3-барабанный слот | Near Miss система, каскадная остановка барабанов |
| B | Счастливое Колесо | Колесо фортуны | Сектора с разными выплатами, множители ×2/×5 |
| C | Покер Экспресс | Видео-покер | 5 карт, Hold функция, двойная ставка |
| D | Фруктовая Буря | 5-барабанный слот | Каскадные символы (Avalanche), цепные выигрыши |
| E | Скрэтч Делюкс | Скретч-карты | Мгновенные выигрыши, 3 попытки за раунд |
| F | Рулетка Неон | Мини-рулетка | Европейская рулетка, внешние/внутренние ставки |

```bash
/auto-idea --archetype A   # Неоновый Спин — классика
/auto-idea --archetype D   # Фруктовая Буря — сложная механика
/auto-idea --list           # Показать все 6 с описанием
```

---

## Критические gambling-правила

Студия автоматически применяет и защищает следующие правила. Нарушение любого = блокировка релиза.

### 1. RNG безопасность

```dart
// ✅ ТОЛЬКО ТАК
final _rng = Random.secure();

// ❌ ЗАПРЕЩЕНО — хук validate-commit.sh обнаружит и предупредит
final rng = Random();           // Не secure!
final rng = math.Random();      // Не secure!
```

### 2. Stateless Outcomes

Результат спина вычислен **до** анимации. Анимация только "проигрывает" исход.

```dart
// ✅ Результат известен до вращения
Future<void> spin() async {
  final outcome = _rng.computeOutcome();   // Сначала результат
  await _animateReels(outcome.symbols);    // Потом анимация
}
```

### 3. SlotConfig — единственный источник правды

```dart
// ✅ Все константы в одном месте
class SlotConfig {
  static const List<int> reelWeights = [10, 7, 4, 2, 1];
  static const double targetRtp = 0.96;
  static const int bigWinMultiplier = 10;
}

// ❌ Захардкоженные вероятности — запрещено
if (rng.nextDouble() < 0.15) triggerBonus(); // Откуда 0.15?
```

### 4. RTP диапазон

- Целевой RTP: **95–97%** при 1,000,000 симуляций
- Только `rtp-mathematician` меняет веса символов
- `/balance-check` обязателен перед `/gate-check qa`

### 5. GameState — sealed class

```dart
sealed class GameState {}
final class IdleState extends GameState {}
final class SpinningState extends GameState { final SpinOutcome outcome; }
final class WinState extends GameState { final WinResult result; }
// Нет boolean флагов isSpinning/isWin/isFreeSpins
```

---

## Автоматизация и хуки

Студия запускает 8 скриптов автоматически — без участия пользователя:

| Хук | Когда запускается | Что делает |
|-----|-------------------|-----------|
| `session-start.sh` | Старт сессии | Показывает состояние проекта, GDD, последние коммиты |
| `detect-gaps.sh` | Старт сессии | Ищет `math.Random()`, отсутствующие файлы, нарушения |
| `validate-commit.sh` | Перед `git commit` | Блокирует `math.Random()`, захардкоженные RTP, невалидный JSON |
| `validate-push.sh` | Перед `git push` | Предупреждает при push в main без прохождения ворот |
| `validate-assets.sh` | После Write/Edit | Проверяет именование ассетов (`sprite_X`, `sfx_X`) |
| `pre-compact.sh` | Перед сжатием контекста | Сохраняет чекпоинт в `production/session-state/active.md` |
| `session-stop.sh` | Завершение сессии | Логирует изменения сессии в `production/session-logs/` |
| `log-agent.sh` | Запуск субагента | Аудит-след всех вызовов агентов |

### Правила кода (path-based)

Правила применяются автоматически по пути файла:

| Правило | Применяется к | Содержание |
|---------|--------------|-----------|
| `gambling-code.md` | `lib/**/*.dart` | RNG безопасность, Stateless Outcomes, SlotConfig |
| `engine-code.md` | `lib/game/**/*.dart` | Flame 1.18.x API (World, CameraComponent, HasTimeScale) |
| `ui-code.md` | `lib/screens/**/*.dart` | ValueNotifier, защита двойного клика, Win оверлеи |
| `test-standards.md` | `test/**/*.dart` | AAA структура, дистрибуционные тесты RNG, edge cases |
| `data-files.md` | `design/balance/**/*.json` | Схема rtp-config.json, обязательные поля |
| `design-docs.md` | `design/**/*.md` | 8 обязательных секций GDD, статус документа |

---

## Структура проекта

```
flutter-gambling-studio/
├── CLAUDE.md                          # Главная конфигурация студии
├── .gitignore                         # Flutter + session state
├── .claude/
│   ├── settings.json                  # Права, хуки, statusline
│   ├── statusline.sh                  # Статусная строка Claude Code
│   ├── agents/                        # 12 специализированных агентов
│   │   ├── creative-director.md
│   │   ├── technical-director.md      # NEW
│   │   ├── rtp-mathematician.md
│   │   ├── gambling-game-designer.md
│   │   ├── slot-programmer.md
│   │   ├── juice-artist.md
│   │   ├── lead-programmer.md
│   │   ├── performance-analyst.md     # NEW
│   │   ├── ui-programmer.md
│   │   ├── sound-designer.md
│   │   ├── qa-tester.md
│   │   └── release-manager.md
│   ├── skills/                        # 20 слэш-команд
│   │   ├── start/           brainstorm/      auto-idea/
│   │   ├── autocreate/      map-systems/     design-system/
│   │   ├── prototype/       generate-asset/  team-gambling/
│   │   ├── balance-check/   continue-project/ add-feature/
│   │   ├── release-checklist/
│   │   ├── code-review/               # NEW — gambling ревью кода
│   │   ├── design-review/             # NEW — ревью GDD
│   │   ├── gate-check/                # NEW — ворота качества
│   │   ├── hotfix/                    # NEW — экстренные фиксы
│   │   ├── perf-profile/              # NEW — профилирование
│   │   ├── tech-debt/                 # NEW — реестр долга
│   │   └── architecture-decision/     # NEW — ADR
│   ├── hooks/                         # 8 автоматических скриптов
│   │   ├── session-start.sh
│   │   ├── session-stop.sh
│   │   ├── detect-gaps.sh
│   │   ├── validate-commit.sh
│   │   ├── validate-push.sh
│   │   ├── validate-assets.sh
│   │   ├── pre-compact.sh
│   │   └── log-agent.sh
│   ├── rules/                         # 6 path-based правил
│   │   ├── gambling-code.md
│   │   ├── engine-code.md
│   │   ├── ui-code.md
│   │   ├── test-standards.md
│   │   ├── data-files.md
│   │   └── design-docs.md
│   └── docs/                          # Документация студии
│       ├── technical-preferences.md
│       ├── coding-standards.md        # NEW
│       ├── context-management.md      # NEW
│       ├── coordination-rules.md
│       ├── directory-structure.md
│       ├── quick-start.md
│       └── templates/
│           ├── gambling-concept.md
│           └── rtp-design.md
├── production/
│   ├── session-state/active.md        # Текущий чекпоинт (gitignored)
│   └── session-logs/                  # Аудит-лог (gitignored)
└── [игровые проекты создаются здесь]
    ├── lib/
    ├── assets/
    ├── design/
    └── tools/simulate_rtp.py
```

---

## Быстрый старт

### Требования

- [Flutter SDK](https://docs.flutter.dev/get-started/install) 3.27+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`npm install -g @anthropic-ai/claude-code`)
- Python 3 (для симуляции RTP)

### Установка

```bash
git clone https://github.com/leofilllium/flutter-gambling-studio.git
cd flutter-gambling-studio
claude
```

### Пути

**Хочу игру прямо сейчас:**
```
/autocreate
```
Автономный конвейер: концепт → SVG-ассеты → Flutter код → `pubspec.yaml`. Без вопросов.

**Хочу контролировать каждый шаг:**
```
/brainstorm          # Создать концепт вместе
/gate-check concept  # Проверить готовность концепта
/design-system       # Написать GDD для механик
/gate-check design   # Проверить готовность GDD
/team-gambling       # Передать команде программистов
/code-review         # Проверить написанный код
/balance-check       # Симуляция 1М спинов
/gate-check qa       # Финальные ворота
/release-checklist   # Готово к релизу
```

**Работа над существующим проектом:**
```
/continue-project    # Восстановить контекст
/code-review         # Проверить текущее состояние кода
/tech-debt           # Сканировать технический долг
```

---

## Как это работает

### Протокол сотрудничества

**Управляемое сотрудничество, не автономное выполнение** (кроме `/autocreate` и `/auto-idea`).

Схема: **Вопрос → Варианты → Решение → Черновик → Одобрение**

- Агенты спрашивают «Могу ли я записать это в [путь]?» перед Write/Edit
- Изменения в нескольких файлах требуют явного одобрения всего набора
- Только `/autocreate` и `/auto-idea` работают полностью автономно

### Субординация агентов

- Только `creative-director` меняет концепт и видение игры
- Только `rtp-mathematician` утверждает новые веса символов после `/balance-check`
- Только `technical-director` утверждает ADR и архитектурные решения
- `slot-programmer` читает вероятности из `SlotConfig` — никогда не захардкодирует
- `juice-artist` не делает анимации длиннее 3–4 секунд

### Разрешение конфликтов

- Конфликт кода и GDD → `lead-programmer` + `gambling-game-designer` → GDD обновляется
- RTP вне 95–97% → игра останавливается → `rtp-mathematician` итерирует веса
- Технический конфликт между агентами → `technical-director` принимает решение

### Управление контекстом

Студия использует файл-backed сохранение состояния:

- `production/session-state/active.md` — живой чекпоинт сессии
- `pre-compact.sh` хук автоматически сохраняет прогресс перед сжатием
- После сбоя: `session-start.sh` восстанавливает контекст из файла

---

## Кастомизация

Студия расширяема:

**Добавить новый архетип:**
Отредактируй `.claude/skills/auto-idea/SKILL.md` — добавь архетип G–Z.

**Изменить RTP диапазон:**
Обнови `.claude/hooks/validate-commit.sh` и `.claude/skills/gate-check/SKILL.md`.

**Добавить нового агента:**
Создай `.claude/agents/my-specialist.md` по образцу существующих.

**Настроить правила кода:**
Отредактируй `.claude/rules/gambling-code.md` для своей студии.

**Создать ADR для решения:**
```
/architecture-decision Использовать Riverpod вместо ValueNotifier
```

---

## Лицензия

MIT License. Подробности в [LICENSE](LICENSE).
