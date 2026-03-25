---
name: ui-audit
description: "Автоматический аудит UI/UX кода на anti-slop качество, UX ошибки и визуальные проблемы. Сканирует все экраны, находит проблемы и автоматически исправляет их."
argument-hint: "[--fix | --report-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# UI Audit — Автоматический Аудит и Исправление UI/UX

Сканирует весь код в `lib/screens/`, `lib/widgets/`, `lib/theme/` и автоматически
находит и исправляет UI/UX проблемы.

**Режимы:**
- По умолчанию: найти и исправить
- `--report-only`: только отчёт, без изменений
- `--fix`: исправить всё без подтверждения

---

## Фаза 1 — Сбор данных

1. Прочитать `.claude/rules/anti-slop-design.md` для понимания стандартов
2. Выполнить `find lib/screens -name "*.dart" | wc -l` — подсчитать экраны
3. Выполнить `find lib/widgets -name "*.dart" | wc -l` — подсчитать виджеты
4. Прочитать ВСЕ файлы в `lib/screens/` и `lib/widgets/`
5. Прочитать `lib/theme/` если существует
6. Прочитать `lib/app.dart` и `lib/main.dart`

---

## Фаза 2 — Anti-Slop Аудит (30 проверок)

### Категория A: Запрещённые паттерны (Critical — блокирует релиз)

| # | Проверка | Grep-паттерн | Автофикс |
|---|---------|-------------|----------|
| A1 | Нет голого `ThemeData.dark()` | `ThemeData.dark()` | Заменить на `GameTheme.themeData` |
| A2 | Нет голого `ThemeData.light()` | `ThemeData.light()` | Заменить на `GameTheme.themeData` |
| A3 | Нет `CircularProgressIndicator` без обёртки | `CircularProgressIndicator` | Заменить на `GameLoadingIndicator()` |
| A4 | Нет `LinearProgressIndicator` без обёртки | `LinearProgressIndicator` | Заменить на кастомный виджет |
| A5 | Нет голого `AlertDialog` | `AlertDialog(` | Заменить на стилизованный диалог |
| A6 | Нет `MaterialPageRoute` | `MaterialPageRoute` | Заменить на `PageRouteBuilder` |
| A7 | Нет `Colors.purple` / `Colors.deepPurple` как основная тема | `Colors.purple\|Colors.deepPurple` | Заменить на тематический цвет |
| A8 | Нет `print()` в UI коде | `print(` | Заменить на `Logger` |
| A9 | Обязателен `BackdropFilter` или кастомные шейдеры | Проверить отсутствие продвинутого рендеринга слоёв | Внедрить эффект Glassmorphism |

### Категория B: Отсутствующие экраны (Major)

| # | Проверка | Как проверить | Автофикс |
|---|---------|--------------|----------|
| B1 | Splash Screen существует | `glob lib/screens/splash*` | Создать шаблон |
| B2 | Main Menu существует | `glob lib/screens/main_menu*` | Создать шаблон |
| B3 | Game Screen существует | `glob lib/screens/game_screen*` | — (критическая ошибка) |
| B4 | HUD Widget существует | `glob lib/screens/hud*` | Создать шаблон |
| B5 | Paytable Screen существует | `glob lib/screens/paytable*` | Создать шаблон |
| B6 | Settings Screen существует | `glob lib/screens/settings*` | Создать шаблон |
| B7 | Help Screen существует | `glob lib/screens/help*` | Создать шаблон |
| B8 | Win Overlay существует | `glob lib/screens/win_overlay*` | Создать шаблон |
| B9 | Insufficient Funds обрабатывается | `grep 'insufficient\|InsufficientFunds\|no_funds'` | Создать диалог |
| B10 | Game Theme файл существует | `glob lib/theme/game_theme*` | Создать тему |
| B11 | Daily Bonus Screen существует | `glob lib/screens/daily_bonus*` | Создать шаблон |
| B12 | Leaderboard Screen существует | `glob lib/screens/leaderboard*` | Создать шаблон |
| B13 | Profile Screen существует | `glob lib/screens/profile*` | Создать шаблон |
| B14 | Animations config файл существует | `glob lib/theme/animations.dart` | Создать конфиг |

### Категория C: Визуальное качество (Medium)

| # | Проверка | Как проверить | Автофикс |
|---|---------|--------------|----------|
| C1 | Минимум 2 шрифта подключены | `grep 'fontFamily\|GoogleFonts'` в screens | Добавить шрифты |
| C2 | Кнопка Spin имеет disabled state | Прочитать spin button code | Добавить `isSpinning` check |
| C3 | Числа анимируются | `grep 'AnimatedCounter\|TweenAnimationBuilder\|CountUp'` | Обернуть в AnimatedCounter |
| C4 | Кастомные переходы между экранами | `grep 'PageRouteBuilder\|CustomTransition'` | Добавить переходы |
| C5 | Glow/shadow эффекты на кнопках | `grep 'BoxShadow\|glow\|Shadow'` в widget файлах | Добавить glow |
| C6 | Micro-interactions на интерактивных элементах | `grep 'GestureDetector\|InkWell'` + наличие анимации | Добавить scale/opacity анимацию |
| C7 | Idle-анимации определены | `grep 'idle\|breathing\|pulsate\|PulsatingWidget'` | Добавить idle пульсацию |
| C8 | Текст не обрезается | `grep 'TextOverflow\|FittedBox\|Flexible'` рядом с Text | Добавить overflow handling |

### Категория D: UX проблемы (Medium)

| # | Проверка | Как проверить | Автофикс |
|---|---------|--------------|----------|
| D1 | Двойной клик Spin защищён | Debounce или `isSpinning` check в spin handler | Добавить защиту |
| D2 | Bet блокирован во время спина | `isSpinning` check в bet handlers | Добавить блокировку |
| D3 | SafeArea на корневых экранах | `grep 'SafeArea'` | Обернуть в SafeArea |
| D4 | Back button обрабатывается | `grep 'PopScope\|WillPopScope'` | Добавить PopScope |
| D5 | Responsive layout | `grep 'LayoutBuilder\|MediaQuery\|FractionallySizedBox'` | Обернуть в LayoutBuilder |
| D6 | Staggered entrance анимации | `grep 'stagger\|AnimationController\|SlideTransition'` в menu | Добавить staggered entrance |

---

## Фаза 3 — Автоисправление

Для каждой найденной проблемы:

1. **Прочитать файл полностью** — понять контекст
2. **Определить минимальное исправление** — не переписывать весь файл
3. **Применить Edit** — точечное исправление
4. **Если файл отсутствует** — создать из шаблона (Agent: ui-programmer)

### Шаблоны для создания недостающих экранов

Если экран отсутствует, запустить **Agent (ui-programmer)** с промптом:
```
Создай [экран] для гемблинг-игры. Прочитай lib/theme/game_theme.dart для цветов,
lib/game/slot_config.dart для констант. Следуй правилам из .claude/rules/anti-slop-design.md.
```

### Порядок исправлений

1. Сначала создать `GameTheme` если отсутствует (от неё зависит всё)
2. Затем исправить Critical (A1-A8)
3. Затем создать недостающие экраны (B1-B10)
4. Затем исправить визуальное качество (C1-C8)
5. Затем исправить UX (D1-D6)

---

## Фаза 4 — Верификация

```bash
dart analyze lib/
```

Если есть ошибки после фиксов — исправить (до 3 попыток).

---

## Фаза 5 — Отчёт

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 UI/UX AUDIT COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Экраны: [N] найдено / [M] создано
🧩 Виджеты: [N] найдено / [M] создано

🚨 Critical (Anti-Slop):
   [✅|❌] A1: ThemeData.dark() — [статус]
   [✅|❌] A2: CircularProgressIndicator — [статус]
   ...

⚠️ Major (Missing Screens):
   [✅|❌] B1: Splash Screen — [статус]
   ...

🎨 Visual Quality:
   [✅|❌] C1: 2 шрифта — [статус]
   ...

🔧 UX Issues:
   [✅|❌] D1: Двойной клик Spin — [статус]
   ...

📊 Итого:
   Найдено проблем: [X]
   Исправлено: [Y]
   Требуют ручного вмешательства: [Z]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
