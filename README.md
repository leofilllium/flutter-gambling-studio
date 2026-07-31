<p align="center">
  <h1 align="center">Flutter Gambling Studio</h1>
  <p align="center">
    Студия гемблинг-мини-игр на Flutter + Flame.<br/>
    От концепта до релиза — правильная архитектура, верифицируемая математика, «сочный» UI.
    <br /><br />
    <strong>14 агентов · 32 навыка · 8 хуков · 8 правил · 32 архетипа · 6 категорий</strong>
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/агенты-14-blueviolet" alt="14 агентов">
  <img src="https://img.shields.io/badge/навыки-32-green" alt="32 навыка">
  <img src="https://img.shields.io/badge/архетипы-32-orange" alt="32 архетипа">
  <img src="https://img.shields.io/badge/категории-6-yellow" alt="6 категорий">
  <img src="https://img.shields.io/badge/Flutter-3.27+-blue?logo=flutter" alt="Flutter 3.27+">
  <img src="https://img.shields.io/badge/Flame-1.18+-red" alt="Flame 1.18+">
  <a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/совместимо-Claude%20Code-f5f5f5?logo=anthropic" alt="Claude Code Compatible"></a>
  <img src="https://img.shields.io/badge/совместимо-OpenAI%20Codex-111111" alt="OpenAI Codex Compatible">
</p>

---

## Зачем это нужно

Гемблинг-игры сложнее, чем кажутся — и ошибка здесь стоит дороже, чем в обычной мини-игре:

- **Неправильные веса** = нечестный RTP, который никто не заметит до релиза
- **`math.Random()`** вместо `Random.secure()` = предсказуемый исход
- **Исход, вычисленный во время анимации** = RTP невозможно верифицировать, cash-out некорректен
- **Кап множителя или округление выплаты** = тихая утечка процентов
- **Pity-счётчик, не переживающий перезапуск** = pity превращается в фикцию
- **Отсутствие age-gate и дисклеймера** = стор отклонит игру
- **Плюс общее**: аллокации в `update()` = джанк; слабый UI = игра выглядит дёшево

**Flutter Gambling Studio** решает всё это через систему специализированных агентов —
математик владеет моделью и верифицирует её прогоном, дизайнер пишет GDD, программист
механик реализует логику, художник VFX добавляет «сочность», release-manager проверяет
compliance. Хуки защищают от нарушений правил при коммите. Ворота качества не пустят
плохой код на следующий этап.

Математика не «на глаз»: у каждой игры ровно одна объявленная модель (M1–M6), один
JSON-конфиг и один прогон, который либо проходит порог, либо блокирует релиз:

```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json
# exit 0 = PASS · 1 = CONCERNS · 2 = FAIL
```

Репозиторий теперь настроен в dual-mode:

- `CLAUDE.md` и `.claude/` остаются каноническим источником студийных правил
- `AGENTS.md` и `.codex/` дают Codex-совместимый слой исполнения тех же skills, ролей и hooks

Вы контролируете стратегию. Команда реализует.

---

## Шесть категорий гемблинга

Студия делает **только** гемблинг-игры. Пазлы, раннеры, шутеры и кликеры — вне области.

| ID | Категория | Примеры | Модель баланса |
|----|-----------|---------|----------------|
| **C1** 🎰 | Social Casino | Слоты, видео-покер, блэкджек, рулетка, бинго | **M1**: RTP 95–97%, hit rate 20–35% |
| **C2** ⚡ | Casino Originals | Crash, mines, dice, hi-lo, tower, keno, скретч | **M2**: RTP 96–99%, кап множителя |
| **C3** 🏰 | Spin-to-Progress | Build-and-raid, board-dice, prize wheel, альбом | **M3**: source/sink 0.90–1.15 |
| **C4** 🎁 | Gacha & Loot-Box | Баннеры, паки карт, кейсы, гашапон | **M4**: rates 0.5–2%, pity 50–90 |
| **C5** 🃏 | Casino Roguelike | Poker deckbuilder, reel roguelike, dice-builder | **M5**: run win-rate 25–40% |
| **C6** ⚙️ | Coin Pusher & Plinko | Дозер, плинко, пачинко | **M6**: эмпирический RTP 95–97% |

Полный справочник: [`.claude/docs/gambling-categories.md`](.claude/docs/gambling-categories.md).
Пороги верификации: [`.claude/docs/math-models.md`](.claude/docs/math-models.md).

> **Всегда виртуально.** Ни одна игра не принимает и не выплачивает реальные деньги.
> Compliance-слой (age-gate, дисклеймер, responsible-play, раскрытие шансов) — release-блокер:
> [`.claude/rules/responsible-gaming.md`](.claude/rules/responsible-gaming.md).

---

## Codex Quick Start

Если вы работаете в OpenAI Codex:

1. Откройте `AGENTS.md`.
2. Затем прочитайте `.codex/README.md`.
3. Любую slash-команду (`/brainstorm`, `/autocreate`, `/team-dev`) выполняйте через маппинг в `.codex/commands.md`.
4. Для ручного запуска hook-скриптов используйте `bash tools/codex-hooks.sh <hook-name>`.

Это позволяет пользоваться теми же agents/skills/workflows, что и в Claude Code, но без скрытой Claude-специфичной магии.

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
| `game-mathematician` | Владелец матмодели | RTP, house edge, pity, экономика, run win-rate — и их верификация |
| `game-designer` | Геймдизайнер | GDD: раунд, ставки, бонусы, прогрессия, compliance-экраны |
| `mechanics-programmer` | Программист механик | RNG, физика, коллизии, match detection, spawning |
| `juice-artist` | Художник VFX | Anticipation, near-miss, win-celebration, партикли |
| `art-director` | Арт-директор | Vision-ревью набора ассетов на визуальную целостность |
| `meta-systems-programmer` | Мета-системы | Save, экономика, прогрессия, достижения, ads/iap абстракции |
| `lead-programmer` | Ведущий программист | Архитектура, ревью кода, Flame 1.18.x стандарты |
| `performance-analyst` | Аналитик производительности | FPS, память, SpriteBatch, утечки текстур |
| `ui-programmer` | Flutter UI | Экраны, HUD, Win оверлеи, anti-slop дизайн |
| `sound-designer` | Звуковой дизайнер | Ставка, вращение, остановка, cash-out, reveal, pitch scaling |
| `qa-tester` | QA инженер | Тест-кейсы, edge cases, RNG дистрибуция, state leakage |
| `release-manager` | Менеджер релизов | Финальная проверка перед деплоем + compliance-аудит |

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
| `/gate-check concept` | Готов ли концепт к дизайну? | Нет GDD, нет блока Классификация (категория + модель + compliance) |
| `/gate-check design` | Готов ли GDD к имплементации? | Нет 8 секций, нет balance config |
| `/gate-check code` | Готов ли код к QA? | `math.Random()`, захардкоженные вероятности, исход внутри анимации |
| `/gate-check qa` | Готов ли к релизу? | Матмодель вне окна, нет compliance-экранов, нет edge case тестов |

---

## Все команды

### Создание игры

| Команда | Описание |
|---------|----------|
| `/start` | Онбординг и маршрутизация — с чего начать |
| `/brainstorm [хинт]` | Интерактивный концепт гемблинг-игры |
| `/auto-idea` | Автономный концепт из 32 архетипов без вопросов |
| `/auto-idea --list` | Показать все 32 архетипа (A–AF) по категориям |
| `/auto-idea --archetype [A-AF]` | Развернуть конкретный архетип |
| `/auto-idea --category [C1-C6]` | Случайный архетип внутри категории |
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
| `/generate-asset [тип] [имя]` | SVG по умолчанию; PNG только по явному запросу |
| `/generate-png-asset [описание]` | PNG через GPT Image 2: built-in tool или `tools/gpt_image.py` в headless Codex CLI; фон простых ассетов вырезается локально |
| `/svg-to-png [путь]` | Конвертация SVG → PNG через Codex GPT Images 2.0 |

### Ревью и ворота

| Команда | Описание |
|---------|----------|
| `/code-review` | Полное ревью: RNG, Stateless Outcomes, Flame API, State, тесты |
| `/design-review` | Ревью GDD: 8 секций, математика, edge cases |
| `/ui-audit` | Автоматический аудит UI на anti-slop качество |
| `/gate-check [этап]` | Ворота перехода с вердиктом PASS / CONCERNS / FAIL |

### Баланс и математика

| Команда | Описание |
|---------|----------|
| `/balance-check` | Верификация матмодели M1–M6 через `tools/simulate_math.py` (1М испытаний, full-curve) |

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

## Архетипы гемблинг-игр (A–AF)

### 🎰 C1 — Social Casino (A–H) · модель M1

| ID | Название | Механика | Уникальная фича |
|----|----------|----------|-----------------|
| A | Неоновый Спин | Классический слот 3×3 | Near Miss система, каскадная остановка |
| B | Фруктовая Буря | Видео-слот 5×3 + Free Spins | Avalanche: каскадные символы, растущий множитель |
| C | Сахарный Взрыв | Scatter-pays / cluster слот | Выплата за количество символов, tumble-множители |
| D | Золотая Связь | Hold & Spin (Link & Win) | Залипающие монеты, 3 тира джекпота |
| E | Покер Экспресс | Видео-покер | 5 карт, Hold, Double-up на масти |
| F | Стол 21 | Блэкджек | Hit/Stand/Double/Split, подсказка базовой стратегии |
| G | Кибер Спин | Европейская рулетка | Физически достоверный отскок шарика |
| H | Бинго Блиц | Социальное бинго 75 шаров | Power-ups, коллекционные карточки, XP комнат |

### ⚡ C2 — Casino Originals (I–P) · модель M2

| ID | Название | Механика | Уникальная фича |
|----|----------|----------|-----------------|
| I | Космический Взлёт | Crash | Кривая ускорения, particle-хвост, история раундов |
| J | Минное Поле | Mines | Геометрический рост множителя, тишина перед раскрытием |
| K | Квантовые Кости | Dice roll-under | Честная 2D-физика броска, живой слайдер порога |
| L | Выше-Ниже | Hi-Lo | Streak множителей, риск-метр, cash-out в любой момент |
| M | Башня Дракона | Tower Climb | Risk/Reward, выбор 1 из N ячеек на этаж |
| N | Лотерея Чисел | Keno | Выбор чисел + тираж с физикой шариков |
| O | Делюкс Золото | Скретч-карты | Партикли стирающейся фольги, тактильное стирание |
| P | Сундуки Фортуны | Bonus Pick | Dramatic reveal с задержкой |

### 🏰 C3 — Spin-to-Progress (Q–U) · модель M3

| ID | Название | Механика | Уникальная фича |
|----|----------|----------|-----------------|
| Q | Королевство Монет | Build-and-Raid слот | Набег с раскопкой 1 из 4 точек |
| R | Бросок Судьбы | Board-move dice | Доска-сезон: круг открывает новую доску |
| S | Колесо Удачи | Prize-wheel энергохаб | Сектор-джекпот с прогресс-баром между спинами |
| T | Альбом Коллекционера | Стикеры из паков | Дубликаты → обменная валюта, награда за набор |
| U | Щит и Меч | Raid & Shield ладдер | Месть: окно ответа тем, кто напал |

### 🎁 C4 — Gacha & Loot-Box (V–Y) · модель M4

| ID | Название | Механика | Уникальная фича |
|----|----------|----------|-----------------|
| V | Призыв Легенд | Banner pull | Видимый pity-счётчик, гарант на 10-м пулле |
| W | Колода Чемпионов | Mystery card packs | Дубликаты повышают уровень карты |
| X | Кейс-Рулетка | Case opener | Тормозящий спиннер с near-miss на редком |
| Y | Капсульный Автомат | Гашапон | Двухступенчатое раскрытие: капсула → содержимое |

### 🃏 C5 — Casino Roguelike (Z–AC) · модель M5

| ID | Название | Механика | Уникальная фича |
|----|----------|----------|-----------------|
| Z | Джокер | Poker deckbuilder | Джокеры меняют сами правила подсчёта рук |
| AA | Свой Барабан | Slot-reel roguelike | Синергии символов: соседство меняет выплату |
| AB | Кузница Костей | Dice-builder | Перековка: замена грани на эффект |
| AC | Мешок Алхимика | Push-your-luck bag | Порог bust виден, состав мешка меняется |

### ⚙️ C6 — Coin Pusher & Plinko (AD–AF) · модель M6

| ID | Название | Механика | Уникальная фича |
|----|----------|----------|-----------------|
| AD | Золотой Бульдозер | Coin Pusher | Накопление «навеса» у края — обещание лавины |
| AE | Неоновый Каскад | Plinko | Выбор рискового профиля (ряды + раскладка корзин) |
| AF | Серебряный Дождь | Пачинко | Гейт джекпота запускает отдельный слот-раунд |

```bash
/auto-idea --archetype A    # Неоновый Спин (слот, C1)
/auto-idea --archetype I    # Космический Взлёт (crash, C2)
/auto-idea --archetype V    # Призыв Легенд (гача, C4)
/auto-idea --category C5    # Случайный казино-рогалик
/auto-idea --list           # Показать все 32 архетипа по категориям
/auto-idea                  # Случайная уникальная гемблинг-механика
```

> Архетип = МЕХАНИКА. Чтобы игры одного архетипа не повторялись, поверх него прокручиваются
> **Layout Archetype L1–L6** (композиция экранов) и **Design DNA** (палитра/шрифты/формы).
> «Гемблинг» ≠ «тёмный неон и золото»: бинго может быть тёплым и бумажным, гашапон —
> пастельным, рогалик — строгим типографским.

---

## Критические правила игры

Применяются ко всем шести категориям **безусловно** — нет «категорий, к которым они не относятся».

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

// ✅ GameState — sealed class обязателен
sealed class GameState {}
class IdleState extends GameState {}
class ResolvingState extends GameState { final RoundOutcome outcome; }
class WinState extends GameState { final int payout; final WinTier tier; }
class OutOfFundsState extends GameState {}

// ✅ Все параметры в GameConfig; числа модели — из JSON, не дублируются
class GameConfig {
  static const int minBet = 1;
  static const int maxBet = 100;
  static const Duration roundAnimation = Duration(milliseconds: 2000);
}

// ❌ Запрещено — magic numbers
if (win > 1000) triggerJackpot(); // Откуда взялось 1000?
```

**Единственное исключение из `Random.secure()`** — seeded-детерминизм забега в казино-рогаликах
(C5): забег обязан воспроизводиться по seed. Требует ADR.

**Верификация модели обязательна** перед `/gate-check qa`:

```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json --trials 1000000
python3 tools/simulate_math.py --selftest   # эталонные конфиги всех шести моделей
```

### Compliance — release-блокер

Age-gate при первом запуске · дисклеймер на splash и в правилах · responsible-play в настройках ·
раскрытие шансов (C4 и платные спины C3) · никаких символов реальной валюты у игрового баланса ·
никаких обещаний выигрыша. Полностью: [`.claude/rules/responsible-gaming.md`](.claude/rules/responsible-gaming.md).

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
│   │   ├── game-mathematician.md      # владелец матмодели M1–M6 + верификация
│   │   ├── game-designer.md           # GDD: раунд, ставки, бонусы, compliance
│   │   ├── mechanics-programmer.md    # RNG, Stateless Outcomes, cash-out, pity, физика
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
- OpenAI Codex с поддержкой `AGENTS.md`
- Python 3 (для симуляции баланса)

### Установка

```bash
git clone https://github.com/leofillium/flutter-gambling-studio.git
cd flutter-gambling-studio
claude
```

### Пути

**Хочу игру прямо сейчас (любая из шести категорий):**
```
/autocreate
```
Автономный конвейер: концепт + матмодель → ассеты → Flutter код → верификация баланса
→ `pubspec.yaml`. Без вопросов.

**Хочу контролировать каждый шаг:**
```
/brainstorm          # Выбрать категорию C1–C6 и создать концепт вместе
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
