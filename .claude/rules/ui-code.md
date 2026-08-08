---
description: Flutter UI rules — crash prevention, layout safety, state management, navigation, interaction patterns
globs: ["lib/screens/**/*.dart", "lib/widgets/**/*.dart", "lib/ui/**/*.dart", "lib/theme/**/*.dart", "lib/app.dart"]
---

# UI Code Rules — Flutter Screens, Widgets & HUD

## 1. Separating UI state from game state

- **NEVER** store game state (balance, bet, the current spin) in Flutter widgets
- The Flutter UI only **reads** state, through a `ValueNotifier` or a `Stream`
- Game logic lives in Flame components; the UI only displays it

```dart
// ✅ CORRECT — the HUD reads through a ValueNotifier
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

// ❌ FORBIDDEN — the HUD manages the balance itself
class HudWidget extends StatefulWidget {
  int _balance = 1000; // Not allowed!
  void _onWin(int amount) => setState(() => _balance += amount); // Not allowed!
}
```

---

## 2. CRASH SAFETY (critical — a violation means a guaranteed crash)

### 2.1 RenderFlex overflow — THE MOST COMMON ERROR

```dart
// ❌ CRASH: "A RenderFlex overflowed by 42 pixels on the bottom"
Column(
  children: [
    Text('Header'),
    ListView.builder(itemCount: 100, itemBuilder: ...), // Unbounded height!
  ],
)

// ✅ SAFE: the ListView is bounded by Expanded
Column(
  children: [
    Text('Header'),
    Expanded(
      child: ListView.builder(itemCount: 100, itemBuilder: ...),
    ),
  ],
)
```

**Rule**: every scrolling widget (`ListView`, `GridView`, `SingleChildScrollView`) inside a
`Column` or `Row` MUST be wrapped in `Expanded` or `Flexible`.

### 2.2 setState after dispose

```dart
// ❌ CRASH: "setState() called after dispose()"
class _MyState extends State<MyWidget> {
  void _onDataLoaded(data) {
    setState(() { _data = data; }); // The widget may already be disposed!
  }
}

// ✅ SAFE: check mounted
class _MyState extends State<MyWidget> {
  void _onDataLoaded(data) {
    if (!mounted) return; // MANDATORY before every setState in a callback/Future/Timer
    setState(() { _data = data; });
  }
}
```

**Rule**: EVERY `setState` inside `Future.then()`, `Timer`, `StreamSubscription.listen()`,
`.whenComplete()` or any async callback MUST be preceded by `if (!mounted) return;`.

### 2.3 Dispose every resource

```dart
// ❌ MEMORY LEAK + CRASH:
class _MyState extends State<MyWidget> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl = AnimationController(vsync: this, duration: Duration(seconds: 1));
  late final Timer _timer = Timer.periodic(Duration(seconds: 1), (_) { ... });
  late final StreamSubscription _sub = someStream.listen((_) { ... });
  final _scrollCtrl = ScrollController();
  final _textCtrl = TextEditingController();
  // No dispose()! → memory leak → crash when touching a disposed controller
}

// ✅ SAFE: everything is released
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

**Rule**: every `AnimationController`, `Timer`, `StreamSubscription`, `ScrollController`,
`TextEditingController` and `FocusNode` MUST be disposed or cancelled in `dispose()`.
Use nullable types (`Timer?`) for safety.

### 2.4 Missing assets

```dart
// ❌ CRASH: "Unable to load asset: assets/images/sprites/missing.svg"
SvgPicture.asset('assets/images/sprites/missing.svg')

// ✅ SAFE: the path comes from constants and the file is guaranteed to exist
SvgPicture.asset(
  GameAssets.spriteCherry, // From lib/assets.dart — verified at build time
  width: 64,
  height: 64,
  placeholderBuilder: (_) => SizedBox(width: 64, height: 64), // fallback
)
```

**Rule**: all asset paths go through constants in `lib/assets.dart`.
For SVG/Image: always specify `width` and `height`.
For optional assets: use `placeholderBuilder` or `errorBuilder`.

### 2.5 Navigator safety

```dart
// ❌ CRASH: "Navigator.pop called on empty stack"
Navigator.pop(context);

// ✅ SAFE
if (Navigator.canPop(context)) {
  Navigator.pop(context);
} else {
  Navigator.pushReplacementNamed(context, '/menu');
}

// ❌ CRASH: "Could not find a generator for route /unknown"
Navigator.pushNamed(context, '/unknown');

// ✅ SAFE: every route is declared in app.dart
// And, for safety, add onUnknownRoute:
MaterialApp(
  routes: { '/menu': (_) => MainMenu(), '/game': (_) => GameScreen(), ... },
  onUnknownRoute: (settings) => MaterialPageRoute(builder: (_) => MainMenu()),
)
```

---

## 3. LAYOUT SAFETY (high — a violation means a visual bug)

### 3.1 SafeArea on EVERY root screen

```dart
// ❌ Content slides under the notch / status bar
@override
Widget build(BuildContext context) {
  return Scaffold(
    body: Column(children: [...]),
  );
}

// ✅ SafeArea protects against the notch / status bar / navigation bar
@override
Widget build(BuildContext context) {
  return Scaffold(
    body: SafeArea(
      child: Column(children: [...]),
    ),
  );
}
```

**Exception**: the game screen with the Flame GameWidget — SafeArea is NOT needed there
(the game is fullscreen).

### 3.2 Text ALWAYS handles overflow

```dart
// ❌ The text runs off the screen — yellow overflow stripes
Text(longPlayerName)

// ✅ The text is clipped or scaled
Text(longPlayerName, overflow: TextOverflow.ellipsis, maxLines: 1)
// or
FittedBox(fit: BoxFit.scaleDown, child: Text(longPlayerName))
// or
Flexible(child: Text(longPlayerName, overflow: TextOverflow.ellipsis))
```

**Rule**: every `Text` with dynamic content (not a hardcoded string) MUST have `overflow:`
plus `maxLines:`, or sit inside a `FittedBox`, or inside a `Flexible`/`Expanded`.

### 3.3 Responsive design — no fixed pixels for layout

```dart
// ❌ Overflow on a small screen, empty space on a large one
Container(width: 400, height: 600, child: ...)

// ✅ Adaptive layout
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

// ✅ Or MediaQuery for percentage sizes
final size = MediaQuery.of(context).size;
Container(width: size.width * 0.9, height: size.height * 0.7)
```

**Rule**: fixed pixels are acceptable ONLY for:
- Icons and buttons (32–64px)
- Padding (8–24px)
- Border/shadow (1–4px)
- Font size (12–48sp)

Everything else goes through `MediaQuery`, `LayoutBuilder`, `Expanded`, `Flexible` or
`FractionallySizedBox`.

### 3.4 SingleChildScrollView + Column (the correct pattern)

```dart
// ❌ CRASH: Expanded inside an unbounded scroll view
SingleChildScrollView(
  child: Column(
    children: [
      Expanded(child: Widget()), // Expanded does not work inside a scroll!
    ],
  ),
)

// ✅ SAFE: no Expanded inside the scroll
SingleChildScrollView(
  child: Column(
    children: [
      SizedBox(height: 200, child: Widget()), // Fixed or intrinsic size
      Widget(), // Intrinsic size
    ],
  ),
)
```

### 3.5 Image / SVG with dimensions

```dart
// ❌ The image stretches across the whole screen
Image.asset('assets/images/ui/button.png')
SvgPicture.asset('assets/images/sprites/cherry.svg')

// ✅ Dimensions are given
Image.asset('assets/images/ui/button.png', width: 120, height: 48, fit: BoxFit.contain)
SvgPicture.asset('assets/images/sprites/cherry.svg', width: 64, height: 64)
```

---

## 4. NAVIGATION

### 4.1 Splash → Menu: pushReplacement, not push

```dart
// ❌ The splash stays on the stack — "back" returns to the splash
Navigator.pushNamed(context, '/menu');

// ✅ The splash is replaced
Navigator.pushReplacementNamed(context, '/menu');
```

### 4.2 A back action on every screen

```dart
// ❌ "Back" closes the app
@override
Widget build(BuildContext context) {
  return Scaffold(body: ...);
}

// ✅ "Back" returns to the previous screen (or asks for confirmation)
@override
Widget build(BuildContext context) {
  return PopScope(
    canPop: false,
    onPopInvokedWithResult: (didPop, _) {
      if (didPop) return;
      // For the game screen: show "Quit the game?"
      // For the others: Navigator.pop(context)
      if (Navigator.canPop(context)) {
        Navigator.pop(context);
      }
    },
    child: Scaffold(body: ...),
  );
}
```

### 4.3 Every route is declared

In `app.dart`, EVERY route used MUST be in the `routes:` map.
Add `onUnknownRoute:` as a fallback.

### 4.4 Flame overlay lifecycle

```dart
// ❌ The overlay hangs around forever
game.overlays.add('win');

// ✅ The overlay closes itself
game.overlays.add('win');
Future.delayed(Duration(seconds: 3), () {
  if (game.overlays.isActive('win')) {
    game.overlays.remove('win');
  }
});
```

---

## 5. BUTTONS AND INTERACTION

### 5.1 The action button (Spin / Play) — THE COMPLETE PATTERN

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
          opacity: isPlaying ? 0.5 : 1.0, // Visual disabled state
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

**Rule**: the action button MUST have:
1. A 300 ms debounce
2. An isPlaying check
3. A visual disabled state (opacity / colour change)
4. A press animation (scale / glow)
5. A ValueListenableBuilder for reactivity

### 5.2 Bet +/- — locked while the round runs

```dart
// ❌ The bet can be changed mid-spin
ElevatedButton(onPressed: () => bet.value++, child: Text('+'))

// ✅ The bet is locked
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

### 5.3 Tap targets at least 48x48

```dart
// ❌ Too small a button — 24x24
Icon(Icons.settings, size: 24)

// ✅ A 48x48 tap target with a 24x24 icon
SizedBox(
  width: 48, height: 48,
  child: IconButton(
    icon: Icon(Icons.settings, size: 24),
    onPressed: () => Navigator.pushNamed(context, '/settings'),
  ),
)
```

### 5.4 Every button gives feedback

```dart
// ❌ A "dead" button — no visual reaction
GestureDetector(
  onTap: doSomething,
  child: Container(child: Text('TAP')),
)

// ✅ A button with press feedback
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

## 6. WIN OVERLAYS

- The win overlay appears AFTER the animation finishes
- Duration: small 2 s, big 3 s, mega 4 s
- Auto-dismiss on a timer, plus tap-to-dismiss
- 3 tiers:
  - Small: < 5x the bet — a toast at the bottom, AnimatedCounter, confetti
  - Big: 5–20x the bet — half-screen, burst particles, fanfare
  - Mega: > 20x the bet — fullscreen, explosion, camera shake, an epic win stinger (`sfx_win_mega`)
- The balance updates with an AnimatedCounter (never a jump)
- The overlay does NOT block the back action

---

## 7. PERSISTENCE (SharedPreferences)

Must be saved:
- Settings: sound on/off, sfx on/off, vibration on/off
- Profile: nickname, avatar index
- Leaderboard: top 10 scores
- Daily bonus: the date it was last claimed
- High score: the best result

**Pattern**: a try-catch around EVERY SharedPreferences call:
```dart
Future<int> getHighScore() async {
  try {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('high_score') ?? 0;
  } catch (_) {
    return 0; // Safe fallback
  }
}
```

---

## 8. ACCESSIBILITY

- The action button: `Semantics(label: 'Start the game')`
- Balance/score: `Semantics(value: '$balance coins')`
- Text at least 14sp on mobile
- Text contrast against the background at least 4.5:1
- Every interactive element at least 48x48

---

## 9. FORBIDDEN PATTERNS

1. **`setState()`** for updating game state — use `ValueNotifier` only
2. **`setState` without a `mounted` check** in an async context — a guaranteed crash
3. **`BuildContext` in Flame components** — pass a callback at initialisation
4. **UI animations longer than 500 ms** — they slow down the perception of the result
5. **Fixed sizes without `MediaQuery`** for layout — use `LayoutBuilder`
6. **`ListView` inside `Column` without `Expanded`** — an "unbounded height" crash
7. **`Expanded` inside `SingleChildScrollView`** — Expanded does not work in a scroll
8. **`Navigator.pop` without a `canPop` check** — a crash on an empty stack
9. **An AnimationController without `dispose()`** — a memory leak
10. **A Timer without `cancel()` in `dispose()`** — a callback on a disposed widget
11. **Image/SVG without width/height** — unpredictable sizing
12. **Text without overflow handling** on dynamic content
13. **A GestureDetector without visual feedback** — a "dead" button
14. **`print()` in production** — use `debugPrint` or `Logger`
15. **Player-facing strings in a language other than English**, unless the user explicitly
    asked for a different language — see CLAUDE.md → Language
