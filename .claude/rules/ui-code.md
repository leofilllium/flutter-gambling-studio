---
description: Flutter UI rules — crash prevention, layout safety, state management, navigation, interaction patterns
globs: ["lib/screens/**/*.dart", "lib/widgets/**/*.dart", "lib/ui/**/*.dart", "lib/theme/**/*.dart", "lib/app.dart"]
---

# UI Code Rules — Flutter Screens, Widgets & HUD

## 1. Разделение состояния UI и игры

- **НИКОГДА** не хранить игровое состояние (баланс, ставка, текущий спин) в Flutter виджетах
- Flutter UI только **читает** состояние через `ValueNotifier` или `Stream`
- Игровая логика живёт в Flame компонентах, UI — только отображает

```dart
// ✅ ПРАВИЛЬНО — HUD читает через ValueNotifier
class HudWidget extends StatelessWidget {
  final ValueNotifier<int> balance;
  final ValueNotifier<int> bet;
  final ValueNotifier<bool> isSpinning;

  const HudWidget({
    required this.balance,
    required this.bet,
    required this.isSpinning,
    super.key,
  });
}

// ❌ ЗАПРЕЩЕНО — HUD сам управляет балансом
class HudWidget extends StatefulWidget {
  int _balance = 1000; // Нельзя!
  void _onWin(int amount) => setState(() => _balance += amount); // Нельзя!
}
```

---

## 2. КРАШ-БЕЗОПАСНОСТЬ (Critical — нарушение = гарантированный краш)

### 2.1 RenderFlex Overflow — САМАЯ ЧАСТАЯ ОШИБКА

```dart
// ❌ КРАШ: "A RenderFlex overflowed by 42 pixels on the bottom"
Column(
  children: [
    Text('Header'),
    ListView.builder(itemCount: 100, itemBuilder: ...), // Неограниченная высота!
  ],
)

// ✅ БЕЗОПАСНО: ListView ограничен через Expanded
Column(
  children: [
    Text('Header'),
    Expanded(
      child: ListView.builder(itemCount: 100, itemBuilder: ...),
    ),
  ],
)
```

**Правило**: Каждый скролл-виджет (`ListView`, `GridView`, `SingleChildScrollView`)
внутри `Column` или `Row` ОБЯЗАН быть обёрнут в `Expanded` или `Flexible`.

### 2.2 setState после dispose

```dart
// ❌ КРАШ: "setState() called after dispose()"
class _MyState extends State<MyWidget> {
  void _onDataLoaded(data) {
    setState(() { _data = data; }); // Widget может быть уже disposed!
  }
}

// ✅ БЕЗОПАСНО: проверка mounted
class _MyState extends State<MyWidget> {
  void _onDataLoaded(data) {
    if (!mounted) return; // ОБЯЗАТЕЛЬНО перед каждым setState в callback/Future/Timer
    setState(() { _data = data; });
  }
}
```

**Правило**: КАЖДЫЙ `setState` внутри `Future.then()`, `Timer`, `StreamSubscription.listen()`,
`.whenComplete()` или любого async callback ОБЯЗАН иметь `if (!mounted) return;` перед ним.

### 2.3 Dispose всех ресурсов

```dart
// ❌ MEMORY LEAK + CRASH:
class _MyState extends State<MyWidget> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl = AnimationController(vsync: this, duration: Duration(seconds: 1));
  late final Timer _timer = Timer.periodic(Duration(seconds: 1), (_) { ... });
  late final StreamSubscription _sub = someStream.listen((_) { ... });
  final _scrollCtrl = ScrollController();
  final _textCtrl = TextEditingController();
  // Нет dispose()! → memory leak → crash при обращении к disposed controller
}

// ✅ БЕЗОПАСНО: всё освобождается
class _MyState extends State<MyWidget> with SingleTickerProviderStateMixin {
  late final AnimationController _animCtrl;
  Timer? _timer;
  StreamSubscription? _sub;
  final _scrollCtrl = ScrollController();
  final _textCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(vsync: this, duration: Duration(seconds: 1));
    _timer = Timer.periodic(Duration(seconds: 1), (_) { ... });
    _sub = someStream.listen((_) { ... });
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    _timer?.cancel();
    _sub?.cancel();
    _scrollCtrl.dispose();
    _textCtrl.dispose();
    super.dispose();
  }
}
```

**Правило**: Каждый `AnimationController`, `Timer`, `StreamSubscription`, `ScrollController`,
`TextEditingController`, `FocusNode` ОБЯЗАН быть disposed/cancelled в `dispose()`.
Используй nullable типы (`Timer?`) для безопасности.

### 2.4 Отсутствующие ассеты

```dart
// ❌ КРАШ: "Unable to load asset: assets/images/sprites/missing.svg"
SvgPicture.asset('assets/images/sprites/missing.svg')

// ✅ БЕЗОПАСНО: путь из constants + файл гарантированно существует
SvgPicture.asset(
  GameAssets.spriteCherry, // Из lib/assets.dart — проверено при сборке
  width: 64,
  height: 64,
  placeholderBuilder: (_) => SizedBox(width: 64, height: 64), // fallback
)
```

**Правило**: Все пути ассетов — через constants в `lib/assets.dart`.
Для SVG/Image: всегда указывай `width` и `height`.
Для необязательных ассетов: используй `placeholderBuilder` или `errorBuilder`.

### 2.5 Navigator safety

```dart
// ❌ КРАШ: "Navigator.pop called on empty stack"
Navigator.pop(context);

// ✅ БЕЗОПАСНО
if (Navigator.canPop(context)) {
  Navigator.pop(context);
} else {
  Navigator.pushReplacementNamed(context, '/menu');
}

// ❌ КРАШ: "Could not find a generator for route /unknown"
Navigator.pushNamed(context, '/unknown');

// ✅ БЕЗОПАСНО: все маршруты определены в app.dart
// И для безопасности добавить onUnknownRoute:
MaterialApp(
  routes: { '/menu': (_) => MainMenu(), '/game': (_) => GameScreen(), ... },
  onUnknownRoute: (settings) => MaterialPageRoute(builder: (_) => MainMenu()),
)
```

---

## 3. LAYOUT БЕЗОПАСНОСТЬ (High — нарушение = визуальный баг)

### 3.1 SafeArea на КАЖДОМ корневом экране

```dart
// ❌ Контент уходит под notch / status bar
@override
Widget build(BuildContext context) {
  return Scaffold(
    body: Column(children: [...]),
  );
}

// ✅ SafeArea защищает от notch / status bar / navigation bar
@override
Widget build(BuildContext context) {
  return Scaffold(
    body: SafeArea(
      child: Column(children: [...]),
    ),
  );
}
```

**Исключение**: Game Screen с Flame GameWidget — SafeArea НЕ нужна (игра fullscreen).

### 3.2 Текст ВСЕГДА с overflow handling

```dart
// ❌ Текст выходит за экран — жёлтые полосы overflow
Text(longPlayerName)

// ✅ Текст обрезается или масштабируется
Text(longPlayerName, overflow: TextOverflow.ellipsis, maxLines: 1)
// или
FittedBox(fit: BoxFit.scaleDown, child: Text(longPlayerName))
// или
Flexible(child: Text(longPlayerName, overflow: TextOverflow.ellipsis))
```

**Правило**: Каждый `Text` с динамическим содержимым (не hardcoded строка) ОБЯЗАН иметь
`overflow:` + `maxLines:`, или быть внутри `FittedBox`, или внутри `Flexible`/`Expanded`.

### 3.3 Responsive design — нет фиксированных px для layout

```dart
// ❌ На маленьком экране — overflow, на большом — пустота
Container(width: 400, height: 600, child: ...)

// ✅ Адаптивный layout
LayoutBuilder(
  builder: (context, constraints) {
    final width = constraints.maxWidth;
    return Container(
      width: width * 0.9,
      height: constraints.maxHeight * 0.7,
      child: ...
    );
  },
)

// ✅ Или через MediaQuery для процентных размеров
final size = MediaQuery.of(context).size;
Container(width: size.width * 0.9, height: size.height * 0.7)
```

**Правило**: Фиксированные пиксели допустимы ТОЛЬКО для:
- Иконки и кнопки (32-64px)
- Padding (8-24px)
- Border/shadow (1-4px)
- Font size (12-48sp)

Всё остальное — через `MediaQuery`, `LayoutBuilder`, `Expanded`, `Flexible`, `FractionallySizedBox`.

### 3.4 SingleChildScrollView + Column (правильный паттерн)

```dart
// ❌ КРАШ: Expanded внутри unbounded scrollview
SingleChildScrollView(
  child: Column(
    children: [
      Expanded(child: Widget()), // Expanded не работает в scroll!
    ],
  ),
)

// ✅ БЕЗОПАСНО: без Expanded внутри scroll
SingleChildScrollView(
  child: Column(
    children: [
      SizedBox(height: 200, child: Widget()), // Фиксированный или intrinsic размер
      Widget(), // Intrinsic size
    ],
  ),
)
```

### 3.5 Image / SVG с размерами

```dart
// ❌ Изображение растягивается на весь экран
Image.asset('assets/images/ui/button.png')
SvgPicture.asset('assets/images/sprites/cherry.svg')

// ✅ Размеры заданы
Image.asset('assets/images/ui/button.png', width: 120, height: 48, fit: BoxFit.contain)
SvgPicture.asset('assets/images/sprites/cherry.svg', width: 64, height: 64)
```

---

## 4. НАВИГАЦИЯ

### 4.1 Splash → Menu: pushReplacement, не push

```dart
// ❌ Splash остаётся в стеке — кнопка "назад" ведёт на splash
Navigator.pushNamed(context, '/menu');

// ✅ Splash заменяется
Navigator.pushReplacementNamed(context, '/menu');
```

### 4.2 Back button на каждом экране

```dart
// ❌ Кнопка "назад" закрывает приложение
@override
Widget build(BuildContext context) {
  return Scaffold(body: ...);
}

// ✅ Кнопка "назад" возвращает на предыдущий экран (или подтверждение выхода)
@override
Widget build(BuildContext context) {
  return PopScope(
    canPop: false,
    onPopInvokedWithResult: (didPop, _) {
      if (didPop) return;
      // Для Game Screen: показать "Выйти из игры?"
      // Для других: Navigator.pop(context)
      if (Navigator.canPop(context)) {
        Navigator.pop(context);
      }
    },
    child: Scaffold(body: ...),
  );
}
```

### 4.3 Все маршруты определены

В `app.dart` ВСЕ используемые маршруты ОБЯЗАНЫ быть в `routes:` map.
Добавь `onUnknownRoute:` как fallback.

### 4.4 Flame Overlays lifecycle

```dart
// ❌ Оверлей висит навсегда
game.overlays.add('win');

// ✅ Оверлей автоматически закрывается
game.overlays.add('win');
Future.delayed(Duration(seconds: 3), () {
  if (game.overlays.isActive('win')) {
    game.overlays.remove('win');
  }
});
```

---

## 5. КНОПКИ И ВЗАИМОДЕЙСТВИЕ

### 5.1 Кнопка действия (Spin / Play) — ПОЛНЫЙ ПАТТЕРН

```dart
class ActionButton extends StatefulWidget {
  final VoidCallback onAction;
  final ValueNotifier<bool> isPlaying;

  const ActionButton({required this.onAction, required this.isPlaying, super.key});

  @override
  State<ActionButton> createState() => _ActionButtonState();
}

class _ActionButtonState extends State<ActionButton> with SingleTickerProviderStateMixin {
  DateTime? _lastTap;
  late final AnimationController _scaleCtrl;
  late final Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    _scaleCtrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 100));
    _scaleAnim = Tween<double>(begin: 1.0, end: 0.92).animate(
      CurvedAnimation(parent: _scaleCtrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _scaleCtrl.dispose();
    super.dispose();
  }

  void _handleTap() {
    // 1. Debounce 300ms
    final now = DateTime.now();
    if (_lastTap != null && now.difference(_lastTap!) < const Duration(milliseconds: 300)) return;
    _lastTap = now;

    // 2. Check game state
    if (widget.isPlaying.value) return;

    // 3. Animate press
    _scaleCtrl.forward().then((_) => _scaleCtrl.reverse());

    // 4. Execute action
    widget.onAction();
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: widget.isPlaying,
      builder: (_, isPlaying, child) {
        return AnimatedOpacity(
          opacity: isPlaying ? 0.5 : 1.0, // Визуальный disabled
          duration: const Duration(milliseconds: 200),
          child: ScaleTransition(
            scale: _scaleAnim,
            child: GestureDetector(
              onTap: isPlaying ? null : _handleTap,
              child: child,
            ),
          ),
        );
      },
      child: /* button visual */,
    );
  }
}
```

**Правило**: Кнопка действия ОБЯЗАНА иметь:
1. Debounce 300ms
2. isPlaying check
3. Визуальный disabled state (opacity / color change)
4. Press animation (scale / glow)
5. ValueListenableBuilder для реактивности

### 5.2 Bet +/- — блокировка во время действия

```dart
// ❌ Ставку можно менять во время спина
ElevatedButton(onPressed: () => bet.value++, child: Text('+'))

// ✅ Ставка блокируется
ValueListenableBuilder<bool>(
  valueListenable: isSpinning,
  builder: (_, spinning, __) {
    return IgnorePointer(
      ignoring: spinning,
      child: AnimatedOpacity(
        opacity: spinning ? 0.4 : 1.0,
        duration: const Duration(milliseconds: 200),
        child: Row(children: [
          GestureDetector(
            onTap: () { if (bet.value > GameConfig.minBet) bet.value--; },
            child: Text('-'),
          ),
          ValueListenableBuilder<int>(
            valueListenable: bet,
            builder: (_, b, __) => Text('$b'),
          ),
          GestureDetector(
            onTap: () { if (bet.value < GameConfig.maxBet) bet.value++; },
            child: Text('+'),
          ),
        ]),
      ),
    );
  },
)
```

### 5.3 Tap target минимум 48x48

```dart
// ❌ Слишком маленькая кнопка — 24x24
Icon(Icons.settings, size: 24)

// ✅ Tap target 48x48, иконка 24x24
SizedBox(
  width: 48, height: 48,
  child: IconButton(
    icon: Icon(Icons.settings, size: 24),
    onPressed: () => Navigator.pushNamed(context, '/settings'),
  ),
)
```

### 5.4 Каждая кнопка с обратной связью

```dart
// ❌ "Мёртвая" кнопка — нет визуальной реакции
GestureDetector(
  onTap: doSomething,
  child: Container(child: Text('TAP')),
)

// ✅ Кнопка с press feedback
GestureDetector(
  onTapDown: (_) => setState(() => _pressed = true),
  onTapUp: (_) => setState(() => _pressed = false),
  onTapCancel: () => setState(() => _pressed = false),
  onTap: doSomething,
  child: AnimatedScale(
    scale: _pressed ? 0.95 : 1.0,
    duration: const Duration(milliseconds: 100),
    child: Container(child: Text('TAP')),
  ),
)
```

---

## 6. ОВЕРЛЕИ ВЫИГРЫШЕЙ

- Win overlay появляется ПОСЛЕ завершения анимации
- Длительность: Small 2s, Big 3s, Mega 4s
- Auto-dismiss по таймеру + tap-to-dismiss
- 3 уровня:
  - Small: < 5x ставки — toast снизу, AnimatedCounter, confetti
  - Big: 5-20x ставки — полуэкранный, burst particles, fanfare
  - Mega: > 20x ставки — fullscreen, explosion, camera shake, epic music
- Баланс обновляется AnimatedCounter (не прыжком)
- Оверлей НЕ блокирует кнопку "назад"

---

## 7. PERSISTENCE (SharedPreferences)

Обязательно сохранять:
- Settings: sound on/off, sfx on/off, vibration on/off
- Profile: nickname, avatar index
- Leaderboard: top 10 scores
- Daily Bonus: дата последнего получения
- High Score: лучший результат

**Паттерн**: try-catch вокруг КАЖДОГО SharedPreferences вызова:
```dart
Future<int> getHighScore() async {
  try {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('high_score') ?? 0;
  } catch (_) {
    return 0; // Безопасный fallback
  }
}
```

---

## 8. ACCESSIBILITY

- Кнопка действия: `Semantics(label: 'Начать игру')`
- Баланс/счёт: `Semantics(value: '$balance монет')`
- Текст минимум 14sp на мобильных
- Контраст текста к фону минимум 4.5:1
- Все интерактивные элементы минимум 48x48

---

## 9. ЗАПРЕЩЁННЫЕ ПАТТЕРНЫ

1. **`setState()`** для обновления игрового состояния — только `ValueNotifier`
2. **`setState` без `mounted` check** в async контексте — гарантированный краш
3. **`BuildContext` в Flame компонентах** — передай колбэк при инициализации
4. **Анимации UI длиннее 500мс** — замедляют восприятие результата
5. **Фиксированные размеры без `MediaQuery`** для layout — используй `LayoutBuilder`
6. **`ListView` в `Column` без `Expanded`** — краш "unbounded height"
7. **`Expanded` в `SingleChildScrollView`** — Expanded не работает в scroll
8. **`Navigator.pop` без `canPop` check** — краш на пустом стеке
9. **AnimationController без `dispose()`** — memory leak
10. **Timer без `cancel()` в `dispose()`** — callback на disposed widget
11. **Image/SVG без width/height** — непредсказуемый размер
12. **Text без overflow handling** на динамическом содержимом
13. **GestureDetector без visual feedback** — "мёртвая" кнопка
14. **`print()` в production** — использовать `debugPrint` или `Logger`
