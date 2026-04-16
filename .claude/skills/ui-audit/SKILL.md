---
name: ui-audit
description: "Глубокий аудит UI/UX кода на anti-slop качество, краш-уязвимости, layout overflow, state ошибки, навигацию, отзывчивость и визуальные проблемы. 60+ проверок с автоматическим исправлением. Ловит реальные баги, а не только стилистику."
argument-hint: "[--fix | --report-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# UI Audit — Глубокий Аудит и Исправление UI/UX

Сканирует весь код в `lib/screens/`, `lib/widgets/`, `lib/theme/`, `lib/components/`,
`lib/app.dart`, `lib/main.dart` и находит **реальные баги**, краш-уязвимости и
визуальные проблемы.

**Это НЕ линтер. Это глубокий аудит, который ловит ошибки, вызывающие краши и плохой UX.**

**Режимы:**
- По умолчанию: найти и исправить
- `--report-only`: только отчёт, без изменений
- `--fix`: исправить всё без подтверждения

---

## Фаза 1 — Сбор данных

1. Прочитать `.claude/rules/anti-slop-design.md`
2. Прочитать `.claude/rules/ui-code.md`
3. `glob lib/screens/**/*.dart` — найти все экраны
4. `glob lib/widgets/**/*.dart` — найти все виджеты
5. `glob lib/theme/**/*.dart` — найти тему и анимации
6. `glob lib/components/**/*.dart` — найти Flame компоненты
7. Прочитать КАЖДЫЙ найденный файл полностью
8. Прочитать `lib/app.dart` и `lib/main.dart`
9. Прочитать `pubspec.yaml` (секция assets и fonts)
10. `glob assets/**/*` — найти все реальные ассеты на диске

---

## Фаза 2 — Аудит (60+ проверок, 7 категорий)

### Категория A: КРАШ-УЯЗВИМОСТИ (Critical — приложение падает)

> Эти ошибки ГАРАНТИРОВАННО крашат приложение. Исправлять ПЕРВЫМИ.

| # | Проверка | Как найти | Почему крашит | Автофикс |
|---|---------|-----------|---------------|----------|
| A1 | **RenderFlex overflow**: Column/Row без ограничения высоты/ширины | Найти `Column(` или `Row(` внутри другого `Column`/`Row`/`ListView` без `Expanded`/`Flexible`/`SizedBox` обёртки | "A RenderFlex overflowed by N pixels" — красно-жёлтые полосы | Обернуть в `Expanded` или `Flexible` |
| A2 | **ListView в Column без bounds** | `grep -n 'ListView'` внутри `Column` без `Expanded` wrapper | "Vertical viewport was given unbounded height" | Обернуть ListView в `Expanded` |
| A3 | **setState after dispose** | StatefulWidget с `setState` но без `if (!mounted) return;` проверки перед каждым `setState`, особенно в callbacks, Futures, Timers | "setState() called after dispose()" | Добавить `if (!mounted) return;` перед каждым `setState` в async контексте |
| A4 | **AnimationController без dispose** | StatefulWidget с `AnimationController` но без `controller.dispose()` в `dispose()` | Memory leak → eventual crash | Добавить `dispose()` |
| A5 | **Timer/StreamSubscription без cancel** | `Timer.periodic` или `.listen(` без `cancel()` в `dispose()` | Callback вызывается на disposed widget | Добавить `cancel()` в `dispose()` |
| A6 | **Navigator.pop на пустом стеке** | `Navigator.pop(context)` без проверки `Navigator.canPop(context)` | "Navigator cannot pop — route stack is empty" | Добавить `if (Navigator.canPop(context))` |
| A7 | **Отсутствующий ассет** | Сравнить пути в коде (`'assets/...'`) с реальными файлами в `assets/` | "Unable to load asset" — белый экран или crash | Создать отсутствующий файл или исправить путь |
| A8 | **Шрифт не зарегистрирован** | fontFamily в коде vs fonts в `pubspec.yaml` | Шрифт не загружается, fallback на системный | Добавить в pubspec.yaml или использовать GoogleFonts |
| A9 | **Infinite size**: Unconstrained widget | `MediaQuery.of(context).size` используется для задания constraints внутри `build` до layout | "BoxConstraints forces an infinite width/height" | Использовать `LayoutBuilder` вместо `MediaQuery` для constraints |
| A10 | **Missing Key на анимированных списках** | `ListView.builder` или `AnimatedList` без `key:` на children | Неправильная анимация, мерцание, потенциальный краш при удалении | Добавить `ValueKey` на каждый child |

### Категория B: LAYOUT ОШИБКИ (High — визуальные баги, не краш)

> Приложение работает, но выглядит сломанным на некоторых устройствах.

| # | Проверка | Как найти | Симптом | Автофикс |
|---|---------|-----------|---------|----------|
| B1 | **Нет SafeArea** | Корневой виджет экрана (Scaffold body) без `SafeArea` | Контент уходит под notch/status bar/navigation bar | Обернуть в `SafeArea` |
| B2 | **Фиксированные пиксели** | `height: [число]` или `width: [число]` без `MediaQuery` рядом (исключая иконки <48 и padding) | На маленьком экране — overflow, на большом — пустота | Заменить на `MediaQuery.of(context).size.height * fraction` или `LayoutBuilder` |
| B3 | **Текст overflow** | `Text(` без `overflow:`, `maxLines:`, `FittedBox` или `Flexible` родителя | Текст выходит за экран, жёлтые полосы | Добавить `overflow: TextOverflow.ellipsis, maxLines: 1` или обернуть в `FittedBox` |
| B4 | **Клавиатура перекрывает ввод** | `TextField`/`TextFormField` не внутри `SingleChildScrollView` или `resizeToAvoidBottomInset: true` не установлен | Поле ввода скрыто за клавиатурой | Обернуть в `SingleChildScrollView` + `resizeToAvoidBottomInset: true` |
| B5 | **Отсутствует Scaffold** | Экран возвращает виджет без `Scaffold` wrapper | Нет фона, нет appbar, нет safe area handling | Обернуть в `Scaffold(body: ...)` |
| B6 | **Padding внутри Padding** | Вложенные `Padding` виджеты — двойные отступы | Слишком большие отступы, потеря пространства | Объединить в один Padding |
| B7 | **SingleChildScrollView с Column** | `SingleChildScrollView` → `Column` с `Expanded` children | Expanded не работает в unbounded scroll — crash или unexpected behavior | Убрать `Expanded` внутри `SingleChildScrollView`, использовать фиксированные или intrinsic размеры |
| B8 | **Image без размеров** | `Image.asset(` / `SvgPicture.asset(` без `width:`, `height:` или `fit:` | Изображение может растянуться или сжаться непредсказуемо | Добавить `width`, `height`, `fit: BoxFit.contain` |
| B9 | **Stack без Positioned** | `Stack` с children без `Positioned` или `Align` — элементы наложены друг на друга | Элементы в углу друг на друге | Добавить `Positioned` или `Align` |
| B10 | **Обрезание контента на маленьких экранах** | Контент высотой > 600px без scroll | На iPhone SE / маленьких телефонах — overflow | Обернуть в `SingleChildScrollView` или использовать `LayoutBuilder` для адаптации |

### Категория C: НАВИГАЦИЯ И СОСТОЯНИЕ (High — приложение работает неправильно)

| # | Проверка | Как найти | Симптом | Автофикс |
|---|---------|-----------|---------|----------|
| C1 | **Маршрут не определён** | `pushNamed('/...')` в коде vs `routes:` в `MaterialApp` | "Could not find route" — чёрный экран или exception | Добавить маршрут в `app.dart` |
| C2 | **Нет Back button handling** | Экраны без `PopScope` (Flutter 3.12+) или `WillPopScope` | Кнопка "Назад" закрывает приложение вместо возврата на предыдущий экран | Добавить `PopScope(canPop: false, onPopInvokedWithResult: ...)` |
| C3 | **Game overlay не закрывается** | Flame `overlays.add('win')` без соответствующего `overlays.remove('win')` по таймеру или тапу | Оверлей висит навсегда, блокирует игру | Добавить auto-dismiss Timer + tap-to-dismiss |
| C4 | **Settings не сохраняются** | Settings экран без `SharedPreferences` вызовов | Настройки сбрасываются при перезапуске | Добавить SharedPreferences load/save |
| C5 | **Settings не применяются** | Sound toggle не проверяется перед воспроизведением | Звук играет даже если выключен | Добавить проверку `isSoundEnabled` перед `FlameAudio.play` |
| C6 | **Daily Bonus даёт бесконечно** | Нет проверки даты последнего получения | Игрок может получать бонус неограниченно | Добавить `SharedPreferences` с датой + проверку |
| C7 | **Leaderboard не обновляется** | Нет записи результата после игры | Leaderboard всегда пустой | Добавить запись результата при Game Over / новом high score |
| C8 | **Profile не сохраняет** | Nickname/avatar не записываются в SharedPreferences | Данные теряются при перезапуске | Добавить persistence |
| C9 | **Splash не переходит** | Splash screen без `Timer` или `Future.delayed` для авто-навигации | Приложение застревает на splash | Добавить `Future.delayed(Duration(seconds: 2), () => Navigator.pushReplacementNamed(context, '/menu'))` |
| C10 | **Множественный push без replacement** | `Navigator.pushNamed` вместо `pushReplacementNamed` для splash→menu | Стек навигации растёт, кнопка "назад" ведёт обратно на splash | Использовать `pushReplacementNamed` для splash→menu |

### Категория D: КНОПКИ И ВЗАИМОДЕЙСТВИЕ (High — UX баги)

| # | Проверка | Как найти | Симптом | Автофикс |
|---|---------|-----------|---------|----------|
| D1 | **Двойной клик на кнопке действия** | Кнопка Spin/Play без `isSpinning`/`isPlaying` check | Два спина/действия одновременно, баланс списывается дважды | Добавить `if (isPlaying) return;` + debounce 300ms |
| D2 | **Bet изменяется во время действия** | Кнопки Bet+/Bet- без disabled state при `isSpinning` | Ставка меняется между списанием и начислением выигрыша | Добавить `IgnorePointer(ignoring: isSpinning)` или disabled state |
| D3 | **Кнопка без обратной связи** | `GestureDetector(onTap:)` без анимации при нажатии | Пользователь не понимает, нажал ли он | Добавить `AnimatedScale` (0.95 при нажатии) или `InkWell` с splash |
| D4 | **Tap target < 48px** | Кнопки/иконки с `width` или `height` < 48 | Сложно нажать на мобильном | Обернуть в `SizedBox(width: 48, height: 48)` или добавить padding |
| D5 | **Invisible tap blocker** | `Opacity(opacity: 0)` или `Container(color: Colors.transparent)` с `GestureDetector` поверх контента | Пользователь нажимает — ничего не происходит, хотя кнопка видна | Убрать невидимый blocker или добавить `IgnorePointer` |
| D6 | **Scroll внутри scroll** | `ListView` внутри `ListView` без `shrinkWrap: true` + `NeverScrollableScrollPhysics` | Конфликт жестов, невозможно прокрутить | Добавить `shrinkWrap: true, physics: NeverScrollableScrollPhysics()` на внутренний |
| D7 | **Нет обработки пустого состояния** | `ListView.builder(itemCount: items.length)` без проверки `items.isEmpty` | Пустой экран без объяснения | Добавить `if (items.isEmpty) return EmptyStateWidget(...)` |
| D8 | **GestureDetector перехватывает скролл** | `GestureDetector` с `onVerticalDragUpdate` внутри `ListView` | Скролл не работает | Использовать `onTap` или `Listener` вместо drag gestures |
| D9 | **Кнопка действия не показывает disabled** | Кнопка "SPIN" / "PLAY" визуально одинакова в enabled и disabled | Пользователь нажимает — ничего не происходит — фрустрация | Добавить визуальное различие: тусклый цвет, пониженная opacity, другая иконка |
| D10 | **Нет Insufficient Funds обработки** | При `balance < bet` нет проверки перед действием | Баланс уходит в минус ИЛИ ничего не происходит при нажатии | Добавить проверку + показ InsufficientFundsDialog |

### Категория E: DESIGN INTENT (Medium — контекстуальный дизайн)

> Не проверяем "есть ли neon glow." Проверяем: "есть ли НАМЕРЕНИЕ за каждым решением."
> Прочитай `.claude/rules/anti-slop-design.md` для понимания принципа.
> Также прочитай `design/gdd/game-concept.md` (Design DNA) чтобы понять контекст ЭТОЙ игры.

| # | Проверка | Как проверить | Автофикс |
|---|---------|--------------|----------|
| E1 | **Нет default framework widgets без кастомизации** | `ThemeData.dark()`, `ThemeData.light()` без модификации | → Кастомная тема из Design DNA |
| E2 | **Нет generic loading** | `CircularProgressIndicator`, `LinearProgressIndicator` | → Тематический загрузчик (из контекста игры) |
| E3 | **Нет generic dialogs** | `AlertDialog(` без стилизации | → Стилизованный диалог (стиль из Design DNA) |
| E4 | **Нет generic transitions** | `MaterialPageRoute` | → Тематический `PageRouteBuilder` |
| E5 | **Нет print()** | `print(` | → `debugPrint` или удалить |
| E6 | **Есть animations.dart** | `lib/theme/animations.dart` не существует | Создать файл |
| E7 | **Нет хардкоженных Duration в screens** | `Duration(milliseconds:` вне animations.dart | → `AnimationConfig.xxx` |
| E8 | **Design DNA существует и используется** | Прочитать `design/gdd/game-concept.md` — есть ли Design DNA? Используются ли цвета из DNA в `game_theme.dart`? | Если нет DNA — создать. Если есть но не используется — связать. |
| E9 | **Цвета обоснованы контекстом** | Прочитать game_theme.dart — цвета соответствуют теме игры? (лес = зелёный OK, казино = золотой OK, произвольный фиолетовый = НЕТ) | Скорректировать палитру |
| E10 | **Шрифты соответствуют настроению** | Шрифт подходит миру игры? (ретро-аркада = пиксельный, элегантное казино = serif, детская = rounded) | Заменить на подходящий |
| E11 | **Кнопки имеют форму из Design DNA** | Все primary кнопки используют одну форму, secondary — другую | Привести к единому стилю из DNA |
| E12 | **Визуальная консистентность** | Все экраны используют одну палитру, одни шрифты, один стиль кнопок | Привести к единству |

### Категория F: ОТСУТСТВУЮЩИЕ ЭКРАНЫ (Medium)

| # | Проверка | Как проверить |
|---|---------|--------------|
| F1 | Splash Screen | `glob lib/screens/splash*` |
| F2 | Main Menu | `glob lib/screens/main_menu*` |
| F3 | Game Screen | `glob lib/screens/game_screen*` |
| F4 | HUD Widget | `glob lib/screens/hud*` |
| F5 | Paytable / Rules | `glob lib/screens/paytable*` |
| F6 | Settings | `glob lib/screens/settings*` |
| F7 | Help | `glob lib/screens/help*` |
| F8 | Win Overlay | `glob lib/screens/win_overlay*` |
| F9 | Insufficient Funds | `grep 'insufficient\|InsufficientFunds'` в screens |
| F10 | Game Theme | `glob lib/theme/game_theme*` |
| F11 | Daily Bonus | `glob lib/screens/daily_bonus*` |
| F12 | Leaderboard | `glob lib/screens/leaderboard*` |
| F13 | Profile | `glob lib/screens/profile*` |

### Категория G: UX POLISH (Low — но делает разницу между "работает" и "хочется играть")

| # | Проверка | Как проверить | Автофикс |
|---|---------|--------------|----------|
| G1 | 2+ шрифта подключены (display + body) | `grep 'fontFamily\|GoogleFonts'` | Добавить подходящую пару для контекста игры |
| G2 | Кнопка действия: idle + press + disabled визуально различимы | Прочитать код кнопки | Добавить feedback (характер — из Design DNA) |
| G3 | Числа анимируются при изменении | `grep 'TweenAnimationBuilder\|AnimatedCount'` | Обернуть в TweenAnimationBuilder |
| G4 | Interactive elements имеют visual feedback | `grep 'onTapDown\|AnimatedScale\|ScaleTransition'` | Добавить feedback на все GestureDetector |
| G5 | Win overlay масштабируется по размеру выигрыша | Прочитать win_overlay — есть ли small/big/mega | Добавить switch по multiplier |
| G6 | Контраст текста к фону >= 4.5:1 | Проверить цвета в theme | Скорректировать |
| G7 | Game screen: основное действие доминирует (60%+) | Прочитать layout | Скорректировать proportions |
| G8 | Пустые состояния стилизованы | `grep 'empty\|EmptyState\|no data'` | Добавить placeholder с текстом и иллюстрацией |
| G9 | Loading state стилизован под игру | `grep 'Loading\|loading'` в screens | Заменить generic → тематический |
| G10 | **Transferability test** | Мысленно перенести UI на другую игру — выглядит ли неуместно? | Если UI generic (подходит к любой игре) — усилить тематическую привязку |

---

## Фаза 3 — Автоисправление

### Порядок исправлений (СТРОГО)

**Этап 1 — Краш-уязвимости (A1-A10):**
Исправить ВСЕ потенциальные краши. Каждое исправление — прочитать файл → понять контекст → точечный Edit.

**Типовые фиксы для категории A:**

```dart
// A1: RenderFlex overflow — Column в Column
// БЫЛО:
Column(children: [
  Column(children: [Widget1(), Widget2(), Widget3()])
])
// СТАЛО:
Column(children: [
  Expanded(child: Column(children: [Widget1(), Widget2(), Widget3()]))
])

// A2: ListView в Column
// БЫЛО:
Column(children: [Header(), ListView.builder(...)])
// СТАЛО:
Column(children: [Header(), Expanded(child: ListView.builder(...))])

// A3: setState after dispose
// БЫЛО:
Future.delayed(Duration(seconds: 2), () {
  setState(() { _showOverlay = false; });
});
// СТАЛО:
Future.delayed(Duration(seconds: 2), () {
  if (!mounted) return;
  setState(() { _showOverlay = false; });
});

// A4: AnimationController без dispose
// БЫЛО:
class _MyState extends State<My> with SingleTickerProviderStateMixin {
  late final _ctrl = AnimationController(vsync: this, duration: ...);
}
// СТАЛО:
class _MyState extends State<My> with SingleTickerProviderStateMixin {
  late final _ctrl = AnimationController(vsync: this, duration: ...);
  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }
}

// A5: Timer without cancel
// БЫЛО:
Timer.periodic(Duration(seconds: 1), (t) { ... });
// СТАЛО:
late final Timer _timer;
@override
void initState() {
  super.initState();
  _timer = Timer.periodic(Duration(seconds: 1), (t) { ... });
}
@override
void dispose() {
  _timer.cancel();
  super.dispose();
}
```

**Этап 2 — Layout ошибки (B1-B10):**
Исправить все layout проблемы. Особое внимание: SafeArea, overflow, responsive.

**Этап 3 — Навигация и состояние (C1-C10):**
Проверить все маршруты, все persistence, все overlay lifecycle.

**Этап 4 — Кнопки и взаимодействие (D1-D10):**
Обеспечить что каждая кнопка имеет обратную связь, защиту от двойного клика, disabled state.

**Этап 5 — Anti-Slop (E1-E12):**
Заменить все запрещённые паттерны на кастомные.

**Этап 6 — Недостающие экраны (F1-F13):**
Создать недостающие экраны через Agent (ui-programmer).

**Этап 7 — Визуальное качество (G1-G10):**
Polish — шрифты, анимации, glow, micro-interactions.

---

## Фаза 4 — Верификация (ОБЯЗАТЕЛЬНАЯ)

```bash
dart analyze lib/
```

Если появились ошибки от автофиксов → исправить (до 5 попыток).

Затем проверить что автофиксы не сломали функциональность:
```bash
flutter test
```

Если тесты падают → исправить (до 3 попыток). Если тест правильный — исправить код, не тест.

---

## Фаза 5 — Отчёт

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 UI/UX AUDIT COMPLETE — DEEP SCAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Экраны: [N] найдено / [M] создано
🧩 Виджеты: [N] найдено

💥 A: Краш-уязвимости (Critical):
   [✅|❌] A1: RenderFlex overflow — [статус]
   [✅|❌] A2: ListView в Column — [статус]
   [✅|❌] A3: setState after dispose — [статус]
   [✅|❌] A4: AnimationController dispose — [статус]
   [✅|❌] A5: Timer/Stream cancel — [статус]
   [✅|❌] A6: Navigator.pop safety — [статус]
   [✅|❌] A7: Asset existence — [статус]
   [✅|❌] A8: Font registration — [статус]
   [✅|❌] A9: Infinite constraints — [статус]
   [✅|❌] A10: Missing Keys — [статус]
   Итого: [X]/10

📐 B: Layout ошибки (High):
   [✅|❌] B1-B10: [краткий статус]
   Итого: [X]/10

🧭 C: Навигация и состояние (High):
   [✅|❌] C1-C10: [краткий статус]
   Итого: [X]/10

👆 D: Кнопки и взаимодействие (High):
   [✅|❌] D1-D10: [краткий статус]
   Итого: [X]/10

🎨 E: Anti-Slop (Medium):
   [✅|❌] E1-E12: [краткий статус]
   Итого: [X]/12

📱 F: Экраны (Medium):
   [✅|❌] F1-F13: [краткий статус]
   Итого: [X]/13

✨ G: Визуальное качество (Low):
   [✅|❌] G1-G10: [краткий статус]
   Итого: [X]/10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ОБЩИЙ РЕЗУЛЬТАТ: [PASS ✅ | NEEDS FIX ⚠️ | BLOCKED ❌]

   Найдено проблем: [X]
   Автоисправлено: [Y]
   Требуют ручного вмешательства: [Z]

   Критических (crash): [N]  ← ДОЛЖНО БЫТЬ 0
   Layout (visual bug): [N]  ← ДОЛЖНО БЫТЬ 0
   Навигация/состояние: [N] ← ДОЛЖНО БЫТЬ 0
   UX (interaction): [N]     ← ДОЛЖНО БЫТЬ 0
   Anti-Slop: [N]
   Экраны: [N]
   Visual quality: [N]

   Вердикт: PASS = 0 Critical + 0 High
            NEEDS FIX = любые High незакрытые
            BLOCKED = любые Critical незакрытые
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
