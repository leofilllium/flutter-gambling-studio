---
name: auto-idea
description: "Автономно генерирует готовую концепцию мини-игры любого жанра (без вопросов пользователю). Выбирает из 24 архетипов A-X (гемблинг, пазл, аркада, физика, казуальные, карточные) или придумывает совершенно уникальную механику. Включает полную карту экранов MVP (10+), UX-поток и anti-slop дизайн-токены."
argument-hint: "[--list] | [--archetype A-X]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write
---

# Auto-Idea — Автогенератор Идей Мини-Игр

Не задавайте вопросов пользователю! Полностью автономно создайте `design/gdd/game-concept.md`.

> **ANTI-SLOP**: Прочитайте `.claude/rules/anti-slop-design.md` перед генерацией.
> Концепт ОБЯЗАН включать уникальную визуальную идентичность, а не generic "тёмная тема с фиолетовым".

## Каталог Архетипов (A-X)

### Гемблинг (A-F)

**A — Слот "Неоновый Спин" (Classic 3x3)**
> Классика 3 барабана в ретро-вейв стиле. Низкая волатильность, частые выигрыши. Фича: контролируемый Near Miss (замедление 3-го барабана).

**B — Слот "Фруктовая Буря" (Video Slot 5x3)**
> 5 барабанов, каскадные выигрыши (Avalanche). Символы взрываются, верхние падают вниз с растущим x-множителем.

**C — Колесо "Счастливый Множитель" (Wheel of Fortune)**
> 1 большое колесо. Игрок делает ставку на цвет или множитель. Фича: фрикционная анимация остановки колеса.

**D — Карты "Покер Экспресс" (Mini Video Poker)**
> Раздача 5 карт. Игрок может "Hold" (заморозить) часть карт для второго драва. RTP считается с учетом оптимальной стратегии.

**E — Скретч "Делюкс Золото" (Scratch Cards)**
> Игрок 'стирает' 9 полей на экране пальцем/мышкой. 3 одинаковых символа дают выигрыш. Фича: партикли стирающейся фольги.

**F — Рулетка "Кибер Спин" (Mini Roulette)**
> 12 номеров + Зеро. Ускоренный геймплей. Фича: физически достоверный отскок шарика от ячеек.

### Crash / Physics Gambling (G-L)

**G — Crash Физика "Космический Взлёт"**
> Краш-игра, где множитель растёт, пока летит объект (ракета/астероид). Flame Particles формируют динамический хвост. Фича: визуализированное физическое ускорение.

**H — Plinko "Неоновый Каскад"**
> Падение шариков через преграды (pegs) с использованием честной физики отскоков (Flame Forge2D) в корзины с множителями.

**I — Coin Pusher "Золотой Бульдозер"**
> 3D-подобная 2D физика толкания монет (rigid bodies). Монеты взаимодействуют друг с другом геометрически.

**J — Mines "Минное Поле"**
> Игрок открывает ячейки, множитель геометрически растёт с каждой безопасной ячейкой. Фича: напряжённые звуковые эффекты наведения.

**K — Dice Physics "Квантовые Кости"**
> Бросок 2-3 костей с честной 2D физикой вращения и отскока от бортов (Flame Forge2D) для определения выигрыша. Зависит от импульса броска пользователя.

**L — Tower Climber "Башня Дракона"**
> Микро-выбор: подъём по этажам, выбор 1 из 3 ячеек. Рост множителя (2 успешные) против немедленного сброса (1 мина).

### Пазл / Match (M-O)

**M — Match-3 "Кристальный Каскад"**
> Классическая сетка match-3 с каскадными взрывами. Flame компоненты для плавных перемещений. Фича: chain-combo счётчик с нарастающими эффектами и специальные кристаллы (бомба, строка, крест).

**N — Тетрис "Неоновый Тетрис"**
> Неоновый тетрис с ghost-piece и hold-механикой. Фича: при каждом cleared line — волна неонового свечения от дна. Hard drop создаёт вибрацию и shake эффект.

**O — Push-puzzle "Пиксельный Сокобан"**
> Пиксельная головоломка с толканием ящиков на цели. Фича: каждый уровень — новая тема (космос, лес, подземелье). Undo с анимацией "перемотки".

### Аркада / Action (P-R)

**P — Endless Runner "Неоновый Раннер"**
> Бесконечный сайд-скроллер: прыжки, уклонения. Процедурная генерация препятствий. Фича: neon trail за персонажем, slow-motion при близком промахе.

**Q — Breakout "Кибер Брейкаут"**
> Arkanoid/Breakout с нарастающей скоростью. Разные типы блоков (обычный, бронированный, взрывной). Фича: power-up шары — мульти-шар, лазер, расширение платформы.

**R — Vertical Shooter "Звёздный Шутер"**
> Вертикальный shoot-em-up с волнами врагов. Flame компоненты для пуль и врагов. Фича: заряженный выстрел (hold = big blast) с уникальной анимацией зарядки.

### Физика / Skill (S-T)

**S — Pinball "Неоновый Пинбол"**
> Полноценный пинбол на Flame Forge2D с флипперами, бамперами и мультиболом. Фича: dynamic lighting — мяч оставляет светящийся след, бамперы вспыхивают при ударе.

**T — Projectile Physics "Катапульта"**
> Angry Birds-подобная механика: прицел, сила броска, физика траектории и разрушения структур. Фича: разные снаряды (камень, взрывчатка, магнит). Разрушение по физике.

### Казуальная / Idle (U-V)

**U — Rhythm Tap "Тап Мастер"**
> Ритм-игра: нажимай в такт музыке на падающие нотки. Flame для синхронизации визуала с аудио. Фича: combo streak меняет цвет и форму нот, background реагирует на ритм.

**V — Idle Clicker "Золотой Кликер"**
> Idle-кликер с автоматизацией и апгрейдами. Петля: клик → монеты → апгрейды → автоклик → пресестиж. Фича: визуальная эволюция мира по мере прогресса, красивые idle анимации.

### Карточная / Настольная (W-X)

**W — Memory "Нейро Память"**
> Классическая игра на память (карточный флип). Пары карточек. Фича: карточки в разных тематиках (животные/космос/символы), эффект голографического переворота, timelimit с визуальным таймером.

**X — Trivia Quiz "Квиз Баттл"**
> Викторина с вопросами и таймером. Streak множитель за правильные ответы подряд. Фича: анимированный таймер в форме круга, wrong answer shake, correct answer confetti.

## Процедурная Уникальная Генерация (Unique Mode)
Если флаг `--archetype` не передан или пользователь явно запросил "уникальную идею", вы **ОБЯЗАНЫ** изобрести **абсолютно новую** механику, не совпадающую с A-X.
Смешивайте жанры, добавляйте физические эффекты (гравитация, магнетизм, физика жидкостей, траектории), Flame партиклы и нестандартные способы взаимодействия (например: "Пинбол-слот с рикошетами", "Аркадный шутер на ставку", "Скретч-карта с физикой разрушения").

## Алгоритм работы

1. Прочитайте флаг (если `--list`, выведите таблицу архетипов A-X).
2. Выберите архетип (по аргументу или случайно, не повторяя прошлый).
3. Определите жанр выбранного архетипа.
4. Создайте детализированный GDD в `design/gdd/game-concept.md`.

## Обязательные секции GDD

### Секция 1: Обзор
- Название, жанр, одно предложение
- Целевая аудитория
- Уникальное торговое предложение (USP)

### Секция 2: Математический / Балансовый профиль

**Для Гемблинг жанра (A-L):**
- Предлагаемый RTP и Волатильность
- Таблица символов с весами
- Hit rate
- Формула выигрыша

**Для других жанров (M-X):**
- Система очков (как начисляются, формула множителя)
- Кривая сложности (как растёт сложность по уровням/времени)
- Прогрессия (что открывается, как долго до следующего этапа)
- Баланс сессии (средняя длина сессии, пиковый момент)

### Секция 3: Design DNA (Contextual Visual Identity)

**Каждое визуальное решение ОБЯЗАНО быть обосновано контекстом ЭТОЙ КОНКРЕТНОЙ игры.**
Не шаблон. Не "всегда неон + трапеция." Дизайн вытекает из темы, настроения и механики.

Прочитай `.claude/rules/anti-slop-design.md` — там объяснён принцип.

```markdown
## Design DNA: [Game Name]

### Emotional Core
[1-2 предложения: что игрок ЧУВСТВУЕТ, играя в ЭТУ КОНКРЕТНУЮ игру?]
[Пример: "Нарастающее напряжение и эйфория при выигрыше" / "Спокойное удовлетворение от решённой головоломки" / "Адреналин от скорости и рефлексов"]

### Visual World
[В каком визуальном мире существует эта игра? Это определяет ВСЁ остальное.]
[Пример: "Подводный мир с мягким свечением медуз" / "Неоновый Токио 2080-х" / "Уютная кофейня с бумажными текстурами"]

### Shape Language (вытекает из Visual World)
- Primary action button: [форма + ПОЧЕМУ для этой игры]
  [Пример для подводной игры: "плавная капля — органическая форма, как медуза"]
  [Пример для механической игры: "рифлёный прямоугольник — как промышленный рычаг"]
  [Пример для уютной игры: "мягкий скруглённый — как подушка"]
- Info panels: [форма + ПОЧЕМУ]
- Decorative elements: [форма + ПОЧЕМУ]

### Color Palette (5 цветов — КАЖДЫЙ обоснован контекстом игры)
- Background: #XXXXXX — [ПОЧЕМУ именно этот цвет для ЭТОЙ игры]
- Surface: #XXXXXX — [ПОЧЕМУ]
- Primary: #XXXXXX — [ПОЧЕМУ — связь с темой/миром игры]
- Win/Success: #XXXXXX — [ПОЧЕМУ]
- Danger/Loss: #XXXXXX — [ПОЧЕМУ]
[Примечание: если игра про лес — зелёная палитра ЛОГИЧНА, а не запрещена.
Если игра про космос — синий ЛОГИЧЕН. Цвет запрещён только если он СЛУЧАЕН.]

### Typography (вытекает из мира и настроения)
- Display font: [конкретный Google Font] — [ПОЧЕМУ этот шрифт подходит этой игре]
  [Пример: "Press Start 2P — ретро-аркадный мир" / "Playfair Display — элегантное казино" / "Nunito — дружелюбная казуальная игра"]
- Body font: [конкретный Google Font] — [ПОЧЕМУ читаемый и подходит настроению]

### Motion Character (вытекает из emotional core)
- Button feedback: [КАКОЙ и ПОЧЕМУ]
  [Тяжёлая механическая игра: глубокое нажатие с задержкой]
  [Лёгкая казуальная: пружинистый отскок]
  [Элегантная: тонкое свечение]
- Win celebration: [ЧТО именно и ПОЧЕМУ соответствует уровню выигрыша]
- Screen transitions: [ЧТО и ПОЧЕМУ — связь с метафорой игры]
  [Карточная игра: переворот карты. Слот: створки. Пазл: рассыпание кусочков.]
  [Или: быстрый cut для быстрой игры. Намеренная простота — тоже дизайн-решение.]
- Idle state: [ЧТО оживляет экран когда игрок не взаимодействует]

### Depth & Effects Strategy
[НЕ "всегда glassmorphism." А: какой приём создания глубины подходит ЭТОЙ игре?]
- [Пример: "Бумажные слои с тенями" для настольной игры]
- [Пример: "Голографические оверлеи" для sci-fi]
- [Пример: "Никакой глубины — плоский минимализм" для дзен-пазла]
- [Пример: "Glassmorphism" для футуристической темы]
- Effects: [какие эффекты используются, зачем, и где НЕ используются]

### What Makes This Design UNIQUE to This Game
[Если перенести этот UI на другую игру — будет ли он выглядеть неуместно? Если да — дизайн удался.]
[1-2 предложения: что НЕВОЗМОЖНО было бы перенести на другую игру]
```

### Секция 4: Карта экранов MVP (Screen Map)

**ОБЯЗАТЕЛЬНО. Минимум 10 экранов с описанием и UX-потоком.**

```markdown
## Screen Map

### Экран 1: Splash Screen
- Что показывает: [анимированный логотип/символ игры]
- Длительность: 1.5-2 сек
- Переход на: Main Menu
- Анимация входа: [конкретный эффект]

### Экран 2: Main Menu
- Элементы: название (с glow), кнопка ИГРАТЬ (пульсирующая), настройки, помощь
- Фон: [описание атмосферного фона]
- Анимация входа: staggered появление элементов
- Переходы: → Game Screen, → Settings, → Help

### Экран 3: Game Screen + HUD
- Игровое поле: [описание специфики жанра]
- HUD элементы: счёт/баланс (animated counter), управление, кнопка действия
- Оверлеи: Win/Score (3 уровня), Game Over, уровень пройден

### Экран 4: Paytable / Таблица правил
- Содержимое: правила, выплаты или комбинации
- Навигация: свайп или табы
- Переход обратно: → Game Screen

### Экран 5: Settings / Настройки
- Элементы: громкость BGM, громкость SFX, вибрация, жанр-специфичные настройки
- Стиль переключателей: [описание кастомных toggles]

### Экран 6: Help / Как играть
- Формат: пошаговое руководство с иллюстрациями

### Экран 7: Win / Score Overlays (3 уровня)
- Small (базовый): toast снизу, animated counter, auto-dismiss 2s
- Big (средний): полу-экранный, конфетти particles, 3s
- Mega (максимальный): полноэкранный, explosion, camera shake

### Экран 8: Game Over / Insufficient Funds
- Стилизованный модал (НЕ AlertDialog)
- Повтор / уменьшить ставку / продолжить

### Экран 9: Bonus / Special Mode (если есть)
- Жанр-специфичный бонусный режим

### Экран 10: Daily Bonus
- Механика удержания игроков
- Переход обратно: → Main Menu

### Экран 11: Leaderboard / Stats
- Топ результатов, прогресс игрока

### Экран 12: Player Profile
- Аватар, никнейм, статистика
```

**UX Flow (навигация):**
```
Splash → Menu → Game ←→ Paytable/Rules
                 ↓  ←→ Settings
                 ↓  ←→ Help
                 ↓
          Win Overlay → Game (auto)
          Bonus Mode → Game (auto)
          Game Over → Menu / Retry

          Menu ←→ Daily Bonus
          Menu ←→ Leaderboard
          Menu ←→ Player Profile
```

### Секция 5: Asset Manifest (ПОЛНЫЙ)
```markdown
## SVG Assets

### Спрайты (assets/images/sprites/)
- sprite_[name].svg — [описание, размер 96x96, стиль]
- ... (минимум 5-8 элементов)

### UI Elements (assets/images/ui/)
- ui_action_button.svg — кнопка действия (кастомная форма)
- ui_frame.svg — рамка игрового поля
- ui_bet_panel.svg — панель управления
- ui_separator.svg — декоративный разделитель
- ui_icon_sound.svg — иконка звука
- ui_icon_settings.svg — иконка настроек
- ui_icon_info.svg — иконка помощи

### Фоны (assets/images/backgrounds/)
- background_menu.svg — фон главного меню
- background_game.svg — фон игрового экрана

### Аудио (assets/audio/sfx/)
- bgm_main.ogg — фоновая музыка
- sfx_action.ogg — основное действие (spin/tap/move)
- sfx_win_small.ogg — малый выигрыш
- sfx_win_big.ogg — большой выигрыш
- sfx_win_mega.ogg — мега выигрыш
- sfx_button.ogg — нажатие кнопки UI
- sfx_navigate.ogg — переход между экранами
```

### Секция 6: Code Architecture (ПОЛНАЯ с Data Flow)
```markdown
## Dart Classes

### Game Core
- [GameName]Game extends FlameGame — точка входа, управляет ValueNotifiers
- [GameName]World extends World with HasCollisionDetection — игровой мир
- GameConfig — ВСЕ числовые константы (ставки, скорости, множители, тайминги)
- GameState (sealed) — Idle, Playing, Animating, Win, GameOver, Paused

### Systems
- [GameLogic] — основная механика (WeightedRNG/MatchDetector/SpawnManager)
- [Evaluator] — чистая функция подсчёта результата

### Components
- [MainComponent] — основной игровой объект
- [ElementComponent] — игровые элементы
- WinAnimationComponent — VFX выигрышей
- AmbientParticles — фоновые частицы

### UI
- GameApp (MaterialApp) → named routes
- SplashScreen → MainMenu → GameScreen (GameWidget + HUD overlay)
- HudWidget — ValueListenableBuilder для баланса/счёта/состояния
- WinOverlay — 3 уровня
- All other screens (12+)

## ValueNotifier Contracts (между Flame Game и Flutter UI)
| Notifier | Type | Writes | Reads |
|----------|------|--------|-------|
| balance | ValueNotifier<int> | Game | HUD, Bet selector, InsufficientFunds |
| bet | ValueNotifier<int> | HUD (Bet+/-) | Game (при действии) |
| isPlaying | ValueNotifier<bool> | Game | HUD (блокировка кнопок) |
| currentState | ValueNotifier<GameState> | Game | HUD, Overlays |
| score | ValueNotifier<int> | Game | HUD, Leaderboard |
| lastWin | ValueNotifier<int> | Game | WinOverlay |

## Complete Game Loop
1. User taps Action button → check isPlaying (false) + check balance >= bet
2. Set isPlaying = true, deduct bet from balance
3. Compute outcome (BEFORE animation)
4. Play action animation (reels spin / tiles move / etc.)
5. Animation complete → evaluate result
6. If win: update balance, show WinOverlay (level based on multiplier), play sound
7. If loss: brief feedback
8. Set isPlaying = false → return to Idle state
9. Update leaderboard if score > highScore

## Edge Cases (ПОЛНЫЙ список)
- Balance = 0 → show InsufficientFunds dialog
- Balance < minBet → show InsufficientFunds
- Double-click Action → second click ignored (isPlaying check)
- App pause during animation → complete animation, return to Idle
- Back button on GameScreen → confirm exit dialog
- Settings changed mid-game → apply immediately (audio volume)
- Daily Bonus already claimed today → show "come back tomorrow"
- First launch → show tutorial/help overlay
```

### Секция 7: Требования к "Сочности" (Juiciness) — ПОЛНЫЕ

```markdown
## Anticipation
- [Описание эффекта ожидания перед результатом]
- [Замедление / задержка / звуковое нарастание]

## Near Miss / Almost Win (если применимо)
- [Описание визуального эффекта при почти-выигрыше]

## Win Celebration (3 уровня)
- Small (1-5x): [описание — toast + confetti + ding]
- Big (5-20x): [описание — полуэкранный + burst particles + fanfare]
- Mega (20x+): [описание — fullscreen + explosion + camera shake + epic music]

## Idle Animations (когда игрок не взаимодействует)
- Основной элемент: [покачивание / блик / пульсация]
- Фон: [движущиеся частицы / ambient glow]
- Кнопка действия: [пульсирующий glow]

## Micro-Interactions
- Каждая кнопка: scale 0.95 при нажатии → 1.0 при отпускании + shadow change
- Числа: AnimatedCounter при изменении (easeOutCubic)
- Навигация: тематический переход (не fade/slide)
- Переключатели: custom toggle с анимацией

## Sound Design Map
| Событие | Звук | Характер |
|---------|------|----------|
| Action start | sfx_action.ogg | Нарастающий |
| Action complete | (тишина 200ms) | Пауза для anticipation |
| Small win | sfx_win_small.ogg | Мелодичный ding |
| Big win | sfx_win_big.ogg | Фанфары |
| Mega win | sfx_win_mega.ogg | Epic orchestra |
| Button tap | sfx_button.ogg | Короткий click |
| Navigation | sfx_navigate.ogg | Swoosh |
| Error/Fail | sfx_error.ogg | Мягкий buzz |
```

### Секция 8: Anti-Slop Checklist + Production Readiness
```markdown
## Anti-Slop
- [ ] Уникальная цветовая палитра (не фиолетово-синий AI default)
- [ ] 2 кастомных шрифта определены
- [ ] Форма кнопок — не стандартный прямоугольник
- [ ] Переходы между экранами тематические
- [ ] Все 12+ экранов описаны с полным содержанием
- [ ] Micro-interactions на каждом интерактивном элементе
- [ ] Idle-анимации определены
- [ ] Загрузка — тематический виджет (не CircularProgressIndicator)
- [ ] Glassmorphism/BackdropFilter для модальных окон
- [ ] Centralized animation timings (animations.dart)

## Production Readiness
- [ ] Complete Game Loop описан (шаг за шагом)
- [ ] ВСЕ edge cases перечислены с решениями
- [ ] Data Flow определён (ValueNotifier контракты)
- [ ] Asset Manifest полный (SVG + Audio)
- [ ] Sound Design Map определён
- [ ] SharedPreferences для: Settings, Profile, Leaderboard, Daily Bonus
```

## Вывод

Выведите сообщение:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTO-IDEA COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Игра: [Название]
Архетип: [A-X | UNIQUE] — [Жанр]
Баланс: [RTP XX% / Кривая сложности / Система очков]
Экранов MVP: [N] экранов
Design DNA: [ключевые визуальные решения]

Сохранено: design/gdd/game-concept.md

Следующий шаг:
  /autocreate --from-concept    — реализовать как игру
  /map-systems                  — декомпозировать на системы
  /design-review                — ревью концепта
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
