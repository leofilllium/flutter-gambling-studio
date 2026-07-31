# Быстрый Старт

Добро пожаловать в **Flutter Gambling Studio** — студию гемблинг-мини-игр:
слоты, покер, рулетка, бинго, crash, mines, plinko, gacha, казино-рогалики,
coin pusher и spin-to-progress гибриды.

Здесь вы выступаете в роли **Директора Студии**, а AI-агенты — ваша команда.
Ваша главная задача — принимать решения, а всю рутину команда возьмет на себя.

> **ВАЖНО**: Всё общение со студией ведется исключительно на **русском языке**.
>
> **Всегда виртуально.** Игры студии не принимают и не выплачивают реальные деньги —
> см. `.claude/rules/responsible-gaming.md`.

## Шесть категорий, в которых работает студия

| ID | Категория | Примеры |
|----|-----------|---------|
| C1 🎰 | Social Casino | слот, видео-покер, блэкджек, рулетка, бинго |
| C2 ⚡ | Casino Originals | crash, mines, dice, hi-lo, tower, keno, скретч |
| C3 🏰 | Spin-to-Progress | build-and-raid слот, board-dice, prize wheel |
| C4 🎁 | Gacha & Loot-Box | banner pull, паки карт, case opener, гашапон |
| C5 🃏 | Casino Roguelike | poker deckbuilder, slot-reel roguelike |
| C6 ⚙️ | Coin Pusher & Plinko | дозер, plinko, пачинко |

Полный справочник — `.claude/docs/gambling-categories.md`.

## 🚀 Как начать новую игру?

У вас есть два пути:

### Путь 1: Автоматический (Я хочу готовую игру)
Просто введите:
```bash
/autocreate
```
Студия сама выберет архетип из 32 (A–AF по шести категориям), объявит математическую
модель, напишет дизайн, нарисует ассеты, создаст код, прогонит баланс и настроит `pubspec.yaml`.

### Путь 2: Ручной (Я хочу создать уникальную игру)

**Шаг 1. Идея и категория**
```bash
/brainstorm
```
Вместе с агентом выберете категорию, архетип, тему и уникальную фичу («сочность»).

**Шаг 2. Разбор на компоненты**
```bash
/map-systems
```
Студия создаст план сборки вашей игры с картой систем.

**Шаг 3. Детальный дизайн механики**
```bash
/design-system rtp-weights        # C1: веса символов и таблица выплат
/design-system multiplier-curve   # C2: формула множителя от house edge
/design-system pity-system        # C4: soft/hard pity и раскрытие шансов
/design-system energy-economy     # C3: реген, кап, source/sink
```
Подключаются `game-mathematician` и `game-designer` — рассчитают модель вашей категории.

**Шаг 4. Написание кода**
```bash
/team-dev "Реализуй ядро игры по нашему концепту"
```
Запустится оркестрация `mechanics-programmer` (логика и RNG) и `juice-artist` (анимации).

---

## 👥 Ваша команда (Агенты)

| Специалист | Кого звать | Что делает |
|------------|------------|------------|
| Математик | `@game-mathematician` | Владелец матмодели: RTP, house edge, pity, экономика, run win-rate |
| Геймдизайнер | `@game-designer` | GDD: раунд, ставки, бонусы, прогрессия, compliance-экраны |
| Программист механик | `@mechanics-programmer` | `Random.secure()`, Stateless Outcomes, paylines, множители, Forge2D |
| Мета-системы | `@meta-systems-programmer` | Save, экономика, прогрессия, достижения, ads/iap абстракции |
| Художник Эффектов | `@juice-artist` | Anticipation, near-miss, win-celebration, партикли |
| UI/UX | `@ui-programmer` | Все экраны Flutter, HUD, панель ставок, anti-slop дизайн |
| Звуковик | `@sound-designer` | Ставка, вращение, остановка, победа, cash-out |

---

## 🛠 Полезные команды в процессе разработки

Генерация ассетов:
```bash
/generate-asset symbol вишня      # символ для барабана
/generate-asset sprite chip-gold  # фишка / шар / капсула
```

Проверить математику игры:
```bash
/balance-check                    # выбирает модель M1–M6 по категории игры
```

Напрямую, если нужно быстро:
```bash
python3 tools/simulate_math.py --model m1 --config design/balance/rtp-config.json
python3 tools/simulate_math.py --selftest   # эталонные конфиги всех шести моделей
```

Добавить фичу в уже готовую игру:
```bash
/add-feature "Добавь Free Spins раунд"        # C1
/add-feature "Добавь авто-ставку с лимитами"  # C2
/add-feature "Добавь гарант на 10-м пулле"    # C4
```

Сделать паузу и продолжить завтра:
```bash
/continue-project
```

Готовы начать? Введите `/start` прямо сейчас.
