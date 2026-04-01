---
name: autocreate
description: "Фабрика производства гемблинг-игр Zero-to-Playable. Создает концепт, рисует SVG ассеты, пишет код на Flutter/Flame 1.18.x с полным набором экранов (7+), настраивает pubspec.yaml, проводит UI/UX аудит и исправляет проблемы. Всё автономно."
argument-hint: "[--from-concept | --idea-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# AutoCreate — Zero-to-Playable Gambling Game Factory

Выполняет полный цикл разработки мини-игр без участия пользователя.
**ЗАПРЕЩАЕТСЯ задавать вопросы (кроме критических багов).**

> **ANTI-SLOP**: Каждый экран и виджет должен выглядеть как craft-level дизайн.
> Прочитайте `.claude/rules/anti-slop-design.md` перед началом работы.

---

## Фаза 1 — Идея (Auto-Concept)

Вызов логики `/auto-idea` для генерации концепции (пропустить если `--from-concept`).
Сохранение в `design/gdd/gambling-concept.md`.

**ВАЖНО**: Концепт ОБЯЗАН включать **Screen Map** — список всех экранов MVP с описанием
и UX-потока между ними (минимум 10 экранов, включая Daily Bonus, Leaderboard, Profile).

---

## Фаза 2 — Flutter Project Bootstrap

`flutter create . --project-name gambling_app --platforms android,ios,web`

Обновление `pubspec.yaml`:
```yaml
dependencies:
  flame: ^1.18.0
  flame_audio: ^2.1.0
  flame_svg: ^1.10.0
  google_fonts: ^6.1.0

flutter:
  fonts:
    - family: Orbitron
      fonts:
        - asset: assets/fonts/Orbitron-Regular.ttf
        - asset: assets/fonts/Orbitron-Bold.ttf
          weight: 700
    - family: Rajdhani
      fonts:
        - asset: assets/fonts/Rajdhani-Regular.ttf
        - asset: assets/fonts/Rajdhani-Bold.ttf
          weight: 700
```

Скачать Google Fonts в `assets/fonts/` через команду:
```bash
mkdir -p assets/fonts
# Используй curl для загрузки шрифтов из Google Fonts CDN
```

---

## Фаза 3 — Asset Mode Selection & Generation

### Выбор формата ассетов (ОБЯЗАТЕЛЬНО спросить пользователя)

> "Выберите формат игровых ассетов:
>
> **1. SVG** (по умолчанию) — векторный, встраивается в код через flame_svg, генерируется мгновенно
> **2. PNG** — растровый, генерируется через Google AI Studio (Imagen API)
>    Требует: API ключ от https://aistudio.google.com/app/apikey
>    Плюс: реалистичные текстуры, AI-качество
>    Минус: нужен ключ, ~4 сек на ассет
>
> Введите 1 или 2 (Enter = SVG):"

**Если выбран SVG** → генерировать по разделу «SVG Генерация» ниже.
**Если выбран PNG** → запросить API ключ и следовать логике `/generate-png-asset --from-concept`.

---

### SVG Генерация (режим по умолчанию)

Автоматическая генерация SVG ассетов:

### Символы (`assets/images/sprites/`)
- Минимум 5 символов для слота (или эквивалент для другого жанра)
- Каждый символ: 96x96 SVG с градиентами и деталями
- НЕ плоские иконки — объём через градиенты и тени

### UI Elements (`assets/images/ui/`)
- Кнопка Spin (кастомная форма — трапеция или скошенный прямоугольник)
- Рамка барабана/игрового поля
- Фон панели ставок
- Декоративные разделители
- Иконки для настроек (звук, вибрация)

### Фоны (`assets/images/backgrounds/`)
- Main menu фон (тёмный с паттерном или ambient эффектом)
- Game screen фон (текстурированный, не просто сплошной цвет)

---

### PNG Генерация (если выбран режим PNG)

1. Запросить Google AI Studio API ключ у пользователя (не сохранять в файлы)
2. Прочитать символы из концепта (`design/gdd/gambling-concept.md`)
3. Для каждого ассета: вызвать Google Imagen REST API через `curl`
4. Декодировать base64 → сохранить PNG в `assets/images/pngs/`
5. Опционально: убрать фон через remove.bg API (спросить пользователя)
6. Обновить `pubspec.yaml` — добавить `assets/images/pngs/`

Следовать полной инструкции из скилла `generate-png-asset`.

---

## Фаза 4 — Parallel Game Implementation (THREE agents)

Запуск ТРЁХ агентов ПАРАЛЛЕЛЬНО:

### Agent A (slot-programmer):
- `lib/game/slot_machine_game.dart` — FlameGame наследник
- `lib/game/slot_machine_world.dart` — World с HasCollisionDetection
- `lib/game/slot_config.dart` — ВСЕ игровые константы
- `lib/systems/weighted_rng.dart` — строго `Random.secure()`
- `lib/systems/payline_evaluator.dart` — чистая функция подсчёта выигрышей
- `lib/models/game_state.dart` — sealed class
- `lib/models/slot_symbol.dart` — модель символа
- `lib/components/reel_component.dart` — механика вращения
- `lib/components/symbol_component.dart` — отображение символа

### Agent B (ui-programmer):
Создаёт ВСЕ экраны по спецификации из `.claude/agents/ui-programmer.md`:

**Обязательные файлы (минимум):**
- `lib/theme/game_theme.dart` — полная кастомная тема (anti-slop)
- `lib/theme/animations.dart` — ОБЯЗАТЕЛЬНО: централизованные Duration и Curve
- `lib/screens/splash_screen.dart` — анимированный splash
- `lib/screens/main_menu.dart` — атмосферное меню с staggered entrance и partcles/живым фоном
- `lib/screens/game_screen.dart` — обёртка GameWidget + overlays
- `lib/screens/hud_widget.dart` — HUD с ValueNotifiers (баланс, ставка, spin)
- `lib/screens/paytable_screen.dart` — таблица выплат с символами
- `lib/screens/settings_screen.dart` — звук, вибрация, auto-spin
- `lib/screens/help_screen.dart` — правила игры пошагово
- `lib/screens/daily_bonus_screen.dart` — ежедневная награда (сундуки/колесо)
- `lib/screens/leaderboard_screen.dart` — статистика и топ игроков
- `lib/screens/profile_screen.dart` — профиль с аватаром
- `lib/screens/win_overlay.dart` — 3 уровня (small/big/mega)
- `lib/screens/insufficient_funds_dialog.dart` — стилизованный диалог (Glassmorphism)
- `lib/screens/free_spins_overlay.dart` — оверлей бонусных спинов
- `lib/widgets/animated_counter.dart` — плавный счётчик
- `lib/widgets/glow_button.dart` — кнопка с glow эффектом
- `lib/widgets/skewed_button.dart` — кнопка с ClipPath
- `lib/widgets/neon_text.dart` — текст с неоновым свечением
- `lib/widgets/pulsating_widget.dart` — idle пульсация
- `lib/widgets/game_loading.dart` — тематический загрузчик
- `lib/app.dart` — MaterialApp с routing и кастомной темой
- `lib/main.dart` — точка входа

**Навигация**: GoRouter или именованные маршруты:
```
/splash → /menu → /game
                → /settings
                → /help
                → /paytable
                → /daily_bonus
                → /leaderboard
                → /profile
```

### Agent C (juice-artist):
- `lib/components/win_animation.dart` — VFX для выигрышей (particles)
- `lib/components/payline_overlay.dart` — визуализация линий
- Анимация кнопки Spin (press/release/disabled)
- Idle-анимации (breathing symbols, pulsing glow)

---

## Фаза 5 — Интеграция и Склейка

После завершения всех агентов:

1. Создать `lib/assets.dart` с типизированными SVG константами
2. Обновить все пути ассетов в `pubspec.yaml`
3. Проверить что `main.dart` → `app.dart` → routing → все экраны связаны
4. Убедиться что `GameScreen` правильно создаёт `SlotMachineGame` и передаёт ValueNotifiers в HUD
5. Проверить что theme подключена в `MaterialApp`

---

## Фаза 6 — Build & Fix

```bash
flutter pub get
dart analyze lib/
```

Исправить ошибки компиляции (до 5 попыток).
Типичные ошибки после параллельной генерации:
- Несовпадение имён классов между агентами
- Отсутствующие импорты
- Несовпадение типов ValueNotifier
- Неправильные пути ассетов

---

## Фаза 7 — UI/UX Аудит и Автоисправление (НОВАЯ)

После успешной компиляции запустить автоматический UI/UX аудит.
Прочитать ВСЕ файлы в `lib/screens/` и `lib/widgets/` и проверить:

### Проверка Anti-Slop

| Проверка | Как проверить | Автофикс |
|----------|--------------|----------|
| Нет `ThemeData.dark()` без кастомизации | `grep 'ThemeData.dark'` | Заменить на `GameTheme.themeData` |
| Нет `CircularProgressIndicator` | `grep 'CircularProgressIndicator'` | Заменить на `GameLoadingIndicator` |
| Нет `AlertDialog` без стилизации | `grep 'AlertDialog'` | Заменить на стилизованный диалог |
| Нет `MaterialPageRoute` | `grep 'MaterialPageRoute'` | Заменить на `PageRouteBuilder` с анимацией |
| Есть минимум 2 шрифта | Проверить `google_fonts` usage | Добавить если нет |
| Кнопка Spin имеет 3 состояния | Прочитать spin button код | Добавить анимации состояний |
| Числа анимируются | Проверить AnimatedCounter usage | Обернуть в AnimatedCounter |
| Минимум 10 экранов | Подсчитать файлы в screens/ | Создать недостающие |
| Унифицированы анимации | `grep 'lib/theme/animations.dart'` | Создать и использовать конфиг |
| Используется Glassmorphism | `grep 'BackdropFilter'` | Добавить в модальные окна |

### Проверка UX

| Проверка | Критерий | Автофикс |
|----------|---------|----------|
| Двойной клик Spin защищён | `isSpinning` check + debounce | Добавить защиту |
| Bet нельзя менять во время спина | Disabled state в BetSelector | Добавить блокировку |
| Недостаточно средств обрабатывается | InsufficientFundsDialog существует | Создать и подключить |
| Win overlay показывается | WinOverlay подключен к GameScreen | Подключить |
| Навигация работает между экранами | Все routes определены | Исправить routes |
| Settings сохраняются | SharedPreferences используется | Добавить persistence |
| Back button работает | WillPopScope/PopScope | Добавить обработку |

### Проверка визуального качества

| Проверка | Что искать | Автофикс |
|----------|-----------|----------|
| Контрастность текста | Светлый текст на тёмном фоне | Скорректировать цвета |
| Текст не обрезается | `TextOverflow.ellipsis` или `FittedBox` | Добавить |
| Responsive layout | `LayoutBuilder` или `MediaQuery` | Обернуть в LayoutBuilder |
| Отступы консистентны | Единые padding значения | Использовать константы |
| Safe area соблюдается | `SafeArea` на корневых экранах | Обернуть в SafeArea |

Выполнить все автофиксы, затем снова:
```bash
dart analyze lib/
```

---

## Фаза 8 — Финальный Отчёт

Вывести отчёт:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎰 AUTOCREATE COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Экраны MVP:
   ✅ Splash Screen
   ✅ Main Menu
   ✅ Game Screen + HUD
   ✅ Paytable
   ✅ Settings
   ✅ Help / Rules
   ✅ Daily Bonus Screen
   ✅ Leaderboard / Stats
   ✅ Player Profile
   ✅ Win Overlays (small/big/mega)
   ✅ Insufficient Funds Dialog
   ✅ Free Spins Overlay

🎨 Anti-Slop Аудит:
   ✅ Кастомная тема (не ThemeData.dark)
   ✅ 2 шрифта подключены
   ✅ Унифицированные тайминги анимаций
   ✅ Использование Glassmorphism/Parallax
   ✅ Кастомные переходы между экранами
   ✅ Micro-interactions на кнопках
   ✅ Animated counters для чисел
   ✅ Тематический загрузчик

🔧 UX Аудит:
   ✅ Двойной клик Spin защищён
   ✅ Bet блокирован во время спина
   ✅ Недостаточно средств обрабатывается
   ✅ Навигация между всеми экранами

🏗️ Следующие шаги:
   flutter run                  — запустить игру
   /balance-check              — проверить RTP
   /code-review                — gambling-ревью кода
   /ui-audit                   — повторный UI/UX аудит
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
