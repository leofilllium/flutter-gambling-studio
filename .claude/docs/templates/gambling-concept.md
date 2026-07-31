# Концепт Гемблинг Игры: [Название]

## 0. Классификация (ОБЯЗАТЕЛЬНО — без неё `/gate-check concept` даёт FAIL)

- **Категория**: [C1 Social Casino | C2 Originals | C3 Spin-to-Progress | C4 Gacha | C5 Roguelike | C6 Physics]
- **Архетип**: [A–AF | UNIQUE] — [название]
- **Математическая модель**: [M1 Paytable RTP | M2 Instant-Win | M3 Economy | M4 Gacha | M5 Run Win-Rate | M6 Physics RTP]
- **Целевая метрика**: [например «RTP 96.0% ±1%» / «hard pity 70, SSR 1.2%» / «run win-rate 32%»]
- **Конфиг модели**: `design/balance/[файл].json`
- **Compliance-профиль**: [полный (age-gate + дисклеймер + 18+) | ослабленный C5 — обоснование]

## 1. Elevator Pitch
Какую главную эмоцию дает эта игра? В чем ее "крючок"?

## 2. Математический Профиль (Заполняет game-mathematician)

Заполняется по модели из §0 — см. `.claude/docs/math-models.md`:

- **M1/M2/M6**: базовый RTP, hit rate, волатильность, максимальный множитель
- **M3**: реген энергии, source/sink, пейс прогресса, таблица событий спина
- **M4**: base rates по редкостям, soft/hard pity, E[пуллов], конвертация дубликатов
- **M5**: пороги раундов, run win-rate, экономика забега, seed-детерминизм

## 3. Базовая Механика (Заполняет game-designer)
- **Структура раунда**: [барабаны/линии | ячейки и мины | кривая множителя | баннер и пулл | доска | поле pegs]
- **Ставка / стоимость входа**: [диапазон, шаг, что тратится]
- **Особые элементы**: [Wild, Scatter, Bonus | cash-out | pity | джокеры | спец-корзины]
- **Бонусный раунд**: [Описание фичи]
- **Условие остановки**: [конец анимации | cash-out игрока | bust | конец забега]

## 4. Сочность (Juiciness)
Какое главное визуальное событие? (Взрыв? Тряска экрана? Золотой Водопад?)
Что видит игрок при "Big Win"?

## 5. Полный список Ассетов
- `sprite_...`
- `ui_...`
- `background_...`

## 6. Design DNA (визуальная идентичность — НЕ дефолтный неон)
> Каждое решение обосновано темой ЭТОЙ игры. См. `.claude/rules/anti-slop-design.md`.
- **Emotional Core**: [что игрок чувствует]
- **Visual World**: [мир: подводный / космос / Египет / уют / …]
- **Palette (5 цветов с причинами)**: background / surface / primary / win / loss
- **Brightness**: [light / dark / сумеречная — по теме]
- **Typography (через google_fonts)**: display + body — [конкретные шрифты + почему]
- **Shape language**: [форма кнопок/панелей — почему]
- **Motion Character**: [feedback / win celebration / transitions]
- **Depth strategy**: [стекло / карточка / бумага / плоско — что подходит]

## 7. Layout & Composition Direction
> См. `.claude/docs/layout-archetypes.md` (L1–L6).
- **Layout Archetype**: [L1–L6] — [почему подходит]
- Применение к Main Menu / Game Screen+HUD / Overlays / Transitions.

## 8. Карта экранов (минимум 12+, композиция по выбранному Layout Archetype)
- Splash, Main Menu, Game+HUD, Paytable/Rules, Settings, Help, Win Overlays (3 уровня),
  Insufficient/Out of Chips, Daily Bonus, Leaderboard, Profile, Loading.
- **Compliance-слой** (`.claude/rules/responsible-gaming.md`): Age Gate, дисклеймер на splash
  и в правилах, Responsible Play в настройках, Odds Disclosure (обязателен для C4 и платных
  спинов в C3).
