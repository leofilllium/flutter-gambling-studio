# Концепт Гемблинг Игры: [Название]

**Архетип**: [Классический Слот 3x3 / Видео-слот 5x3 / Рулетка / Карты]
**RTP Цель**: [от 90% до 98%, например 95.5%]
**Волатильность**: [Низкая / Средняя / Высокая]

## 1. Elevator Pitch
Какую главную эмоцию дает эта игра? В чем ее "крючок"?

## 2. Математический Профиль (Заполняет game-mathematician)
- **Базовый RTP**: [XX]%
- **Максимальный Множитель**: [x100? x1000?]
- **Частота Выиграшей (Hit Rate)**: [XX]%

## 3. Базовая Механика (Заполняет game-designer)
- **Структура**: [Количество барабанов / линий / ячеек]
- **Особые символы**: [Wild, Scatter, Bonus]
- **Бонусный раунд**: [Описание фичи]

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

## 8. Карта экранов (минимум 10+, композиция по выбранному Layout Archetype)
- Splash, Main Menu, Game+HUD, Paytable/Rules, Settings, Help, Win Overlays (3 уровня),
  Insufficient/Game Over, Daily Bonus, Leaderboard, Profile, Loading.
