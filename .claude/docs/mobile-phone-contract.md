# Mobile Phone Contract — Portrait Only

Every game produced by this studio is a **phone game**, not a desktop, tablet, or iPad app.
This is a product constraint, not a responsive-design preference. It applies to concept work,
Flutter implementation, runtime verification, store assets, and native release configuration.

## Product target

- Ship for **Android phones and iPhone only**.
- Use **portrait-up** orientation throughout the app. Do not create landscape gameplay or an
  orientation-specific alternate layout.
- Do not design tablet, iPad, desktop, or wide-screen navigation, sidebars, multi-column pages,
  expanded dashboards, or pointer/hover-dependent interactions.
- Keep `web` only as the studio's build, preview, and Chrome/CDP verification harness. A web build
  does not make desktop browsers a product target.
- Create Flutter platforms with `--platforms web,android,ios`; do not add macOS, Windows, or Linux.

## Canonical phone canvas

All screens must be fluid **within the supported portrait-phone range**, not across arbitrary
desktop widths. Use a compact vertical composition, one dominant action, touch-first controls,
safe areas, and thumb-reachable primary actions.

Required logical-pixel verification matrix:

| Viewport | Purpose |
|---|---|
| 360×640 | short/compact Android phone |
| 360×800 | tall compact Android phone |
| 390×844 | canonical iPhone/preview target |
| 430×932 | large phone portrait |

The supported product canvas is 320–430 logical pixels wide in portrait. The four required
sizes above are release gates. Tablet widths such as 768 logical pixels are deliberately outside
the product matrix.

If the web preview is opened in a wider browser, preserve the phone composition in a centered,
unframed canvas with `maxWidth: 430`. The surrounding host area may use a neutral extension of
the game background, but it must not contain product UI. Never reflow into a desktop/tablet
layout, add a fake phone bezel, or stretch the game field to the browser width.

Apply the cap once around the `MaterialApp` navigator and expose `Key('phoneViewport')` so tests
can measure the actual product canvas:

```dart
builder: (context, child) => LayoutBuilder(
  builder: (context, constraints) {
    final phoneWidth = constraints.maxWidth.clamp(0.0, 430.0).toDouble();
    return ColoredBox(
      color: GameTheme.background,
      child: Align(
        alignment: Alignment.topCenter,
        child: SizedBox(
          key: const Key('phoneViewport'),
          width: phoneWidth,
          height: constraints.maxHeight,
          child: child ?? const SizedBox.shrink(),
        ),
      ),
    );
  },
),
```

This is a host constraint, not a drawn device frame. Dialogs, routes, and overlays remain inside
the same phone canvas.

## Flutter implementation

Lock orientation before `runApp`:

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);
  runApp(const GameApp());
}
```

Import `package:flutter/services.dart`. Keep layout breakpoints inside the phone range only—for
example, compact-height adjustments or a 360/390 width distinction. `shortestSide >= 600`,
tablet branches, desktop navigation, hover-only affordances, and keyboard-only controls are
forbidden.

Secondary informational screens may scroll vertically on short phones. The gameplay core may
not scroll; follow `gameplay-screen-contract.md`.

## Native release configuration

Release preparation must enforce all of the following:

- Android: the launcher activity has `android:screenOrientation="portrait"`.
- iOS `Info.plist`: `UISupportedInterfaceOrientations` contains only
  `UIInterfaceOrientationPortrait`; remove landscape values and any
  `UISupportedInterfaceOrientations~ipad` block.
- Xcode project: every build configuration uses `TARGETED_DEVICE_FAMILY = 1;` (iPhone only,
  never `"1,2"`).

Any missing orientation lock, iPad family target, landscape declaration, tablet-only branch, or
required phone-matrix failure is a HIGH defect and a release blocker.
