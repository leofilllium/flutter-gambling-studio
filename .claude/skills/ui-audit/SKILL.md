---
name: ui-audit
description: "Deep audit of UI/UX code for anti-slop quality, crash vulnerabilities, layout overflow, state errors, navigation, responsiveness, craft composition, live gameplay, production completeness/compliance and visual problems. 100+ checks (10 categories) with automatic correction. Checks INTENT and CRAFT, without imposing house-style. Catches real bugs, not just stylistics."
argument-hint: "[--fix | --report-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# UI Audit - Deep Audit and Correction of UI/UX

Scans all code in `lib/screens/`, `lib/widgets/`, `lib/theme/`, `lib/components/`,
`lib/app.dart`, `lib/main.dart` and finds **real bugs**, crash vulnerabilities and
visual problems.

**This is NOT a linter. This is an in-depth audit that catches bugs that cause crashes and poor UX.**

**Modes:**
- Default: find and fix
- `--report-only`: report only, no changes
- `--fix`: fix everything without confirmation

---

## Phase 1 - Data Collection

1. Read `.claude/rules/anti-slop-design.md` (Game UI Read, Design Signature, state map,
   anti-repeat gate, craft floor, audit guard)
2. Read `.claude/rules/ui-code.md`
2a. Read `design/gdd/game-concept.md` → **Game UI Read and Design Signature**
2b. Read `design/art-direction.md` → state composition map, F/C/H/M/O/R recipes, Similarity
    Check, and viewport proofs
2c. Read `.claude/docs/quality-bar.md` → professional level thresholds
    (§1 first 30 sec: TTP ≤ 3 taps; §2 response ≤ 100 ms; §3 scaled feedback;
    §7 completeness; §8 visual integrity) - the audit measures BY THEM, not “by eye”
2d. Read `.claude/docs/gameplay-screen-contract.md` → full-viewport field, integrated controls,
    stable measurement keys, no core-loop scrolling, and the full verification matrix
2e. Read `.claude/docs/mobile-first-contract.md` → touch-first phone baseline, intentional
    landscape/tablet/desktop/Web reflow, full-host canvas, and platform targeting guidance
3. `glob lib/screens/**/*.dart` - find all screens
4. `glob lib/widgets/**/*.dart` - find all widgets
5. `glob lib/theme/**/*.dart` - find theme and animations
6. `glob lib/components/**/*.dart` - find Flame components
7. Read EVERY file found completely
8. Read `lib/app.dart` and `lib/main.dart`
9. Read `pubspec.yaml` (assets and fonts section)
10. `glob assets/**/*` - find all real assets on disk

---

## Phase 2 - Audit (100+ audits, 10 categories)

### Category A: CRASH VULNERABILITIES (Critical - application crashes)

> These errors are GUARANTEED to crash the application. Fix it FIRST.

| # | Check | How to find | Why does it crash | Autofix |
|---|---------|-----------|---------------|----------|
| A1 | **RenderFlex overflow**: Column/Row without height/width limitation | Find `Column(` or `Row(` inside another `Column`/`Row`/`ListView` without `Expanded`/`Flexible`/`SizedBox` wrapper | "A RenderFlex overflowed by N pixels" - red and yellow stripes | Wrap in `Expanded` or `Flexible` |
| A2 | **ListView in Column without bounds** | `grep -n 'ListView'` inside `Column` without `Expanded` wrapper | "Vertical viewport was given unbounded height" | Wrap ListView in `Expanded` |
| A3 | **setState after dispose** | StatefulWidget with `setState` but without `if (!mounted) return;` checking before each `setState`, especially in callbacks, Futures, Timers | "setState() called after dispose()" | Add `if (!mounted) return;` before every `setState` in async context |
| A4 | **AnimationController without dispose** | StatefulWidget with `AnimationController` but without `controller.dispose()` in `dispose()` | Memory leak → eventual crash | Add `dispose()` |
| A5 | **Timer/StreamSubscription without cancel** | `Timer.periodic` or `.listen(` without `cancel()` in `dispose()` | Callback is called on disposed widget | Add `cancel()` to `dispose()` |
| A6 | **Navigator.pop on empty stack** | `Navigator.pop(context)` without check `Navigator.canPop(context)` | "Navigator cannot pop - route stack is empty" | Add `if (Navigator.canPop(context))` |
| A7 | **Missing or silently substituted asset** | Compare every configured visual item ID with the runtime asset map, `pubspec.yaml`, and a real file. Do not filter null/blank paths before checking completeness. If text/shape fallback is intentional, require explicit art direction and runtime proof; otherwise treat letters, emoji, debug labels, or generic shapes in place of promised art as missing assets. | An outcome can render a placeholder while ordinary file-existence checks still pass | Restore one-to-one configured-ID coverage, remove unintended fallback, and fail startup/tests on incomplete mapping |
| A8 | **Font not registered** | fontFamily in code vs fonts in `pubspec.yaml` | The font does not load, it falls back to the system one | Add to pubspec.yaml or use GoogleFonts |
| A9 | **Infinite size**: Unconstrained widget | `MediaQuery.of(context).size` is used to set the constraints inside `build` to layout | "BoxConstraints forces an infinite width/height" | Use `LayoutBuilder` instead of `MediaQuery` for constraints |
| A10 | **Missing Key on Animated Lists** | `ListView.builder` or `AnimatedList` without `key:` on children | Incorrect animation, flickering, potential crash when deleted | Add `ValueKey` to each child |

### Category B: LAYOUT BUGS (High - visual bugs, no crash)

> The app works but appears broken on some devices.

| # | Check | How to find | Symptom | Autofix |
|---|---------|-----------|---------|----------|
| B1 | **No SafeArea** | Root screen widget (Scaffold body) without `SafeArea` | Content goes under notch/status bar/navigation bar | Wrap in `SafeArea` |
| B2 | **Fixed pixels** | `height: [number]` or `width: [number]` without `MediaQuery` next to it (excluding icons <48 and padding) | On a small screen - overflow, on a large screen - emptiness | Replace with `MediaQuery.of(context).size.height * fraction` or `LayoutBuilder` |
| B3 | **Text overflow** | `Text(` without `overflow:`, `maxLines:`, `FittedBox` or `Flexible` parent | Text goes off screen, yellow stripes | Add `overflow: TextOverflow.ellipsis, maxLines: 1` or wrap in `FittedBox` |
| B4 | **Keyboard blocking input** | `TextField`/`TextFormField` not inside `SingleChildScrollView` or `resizeToAvoidBottomInset: true` not installed | The input field is hidden behind the keyboard | Wrap in `SingleChildScrollView` + `resizeToAvoidBottomInset: true` |
| B5 | **Missing Scaffold** | Screen returns widget without `Scaffold` wrapper | No background, no appbar, no safe area handling | Wrap in `Scaffold(body: ...)` |
| B6 | **Padding inside Padding** | Nested `Padding` widgets - double indentation | Too much padding, wasted space | Combine into one Padding |
| B7 | **SingleChildScrollView with Column** | `SingleChildScrollView` → `Column` with `Expanded` children | Expanded does not work in unbounded scroll - crash or unexpected behavior | Remove `Expanded` inside `SingleChildScrollView`, use fixed or intrinsic sizes |
| B8 | **Image without dimensions** | `Image.asset(` / `SvgPicture.asset(` without `width:`, `height:` or `fit:` | The image may stretch or shrink unpredictably | Add `width`, `height`, `fit: BoxFit.contain` |
| B9 | **Stack without Positioned** | `Stack` with children without `Positioned` or `Align` - elements superimposed on each other | Elements in corner on top of each other | Add `Positioned` or `Align` |
| B10 | **Cutting content on small screens** | Content height > 600px without scroll | On iPhone SE/small phones - overflow | Wrap in `SingleChildScrollView` or use `LayoutBuilder` to adapt |
| B11 | **Gameplay field is too small** | Measure `Key('gameplaySurface')` at 360×640, 360×800, 390×844 and 430×932; compare with the contract | The mechanic reads as a thumbnail and loses focus | Recompose with `Expanded`/`Stack`/`AspectRatio`; field ≥55% usable portrait area and normally ≥88% width |
| B12 | **Nested or displaced game field** | Inspect game-idle and active screenshots for a phone/browser/card-like frame, large unexplained dead margins, or a field pinned to one edge without concept-driven use of the remaining region. On compact portrait, compare the usable gaps between HUD→field and field→controls; large imbalance needs an explicit composition reason. | A game appears embedded, bottom-dumped, or visually absent from the viewport's focal region | Remove outer framing/padding and unintended edge alignment; keep only a tight mechanic-driven rim and place the field according to the selected composition |
| B13 | **Core loop requires scrolling** | Find a vertical `Scrollable` ancestor of `gameplaySurface` or `primaryAction`; verify first viewport | Field or action/control deck falls below the fold | Recompose the fixed viewport; move rules/history/secondary content to a sheet or screen |
| B14 | **Disconnected controls** | Compare field, C recipe, materials, geometry, spacing and depth | Controls look like an unrelated generic panel | Integrate them according to the recorded attached/dock/rail/distributed/direct/contextual recipe |
| B15 | **Poor control proportions** | Measure transformed hit and semantic bounds plus labels at 1.0×/1.3× text scale; compare enabled/disabled states and idle/press animation extrema, not only untransformed widget sizes | Buttons are cramped, uneven, clipped, ambiguous, or shrink below their minimum during feedback | Enforce ≥48×48 targets and a primary action ≥56 logical pixels high throughout animation; keep interaction bounds stable while animating decoration, with shared baselines/heights and responsive label fitting |
| B16 | **Broken mobile-first responsiveness or targeting** | Inspect phone + expanded screenshots, layout branches, `main.dart`, Android manifest, and iOS plist/project | Phone hierarchy breaks; expanded hosts show a capped phone strip, fake frame, dead margins, blind scaling, pointer-only controls, or an undocumented native restriction | Enforce the mobile-first contract; use the full host canvas and intentional responsive reflow |

### Category C: NAVIGATION AND STATUS (High - the application is not working properly)

| # | Check | How to find | Symptom | Autofix |
|---|---------|-----------|---------|----------|
| C1 | **Route not defined** | Compare pushed routes with the loaded app router; reload a non-root Web/platform route through bootstrap loading, error/retry and ready states, with consent accepted and unaccepted | Initial-route errors can occur in a temporary loading app even when the final router is correct | Keep bootstrap navigation-free or explicitly resolve its incoming routes until services are ready; verify platform route precedence rather than assuming `initialRoute` overrides it, and retain consent guards |
| C2 | **No Back button handling** | Screens without `PopScope` (Flutter 3.12+) or `WillPopScope` | Back button closes app instead of returning to previous screen | Add `PopScope(canPop: false, onPopInvokedWithResult: ...)` |
| C3 | **Game overlay does not close** | Flame `overlays.add('win')` without corresponding `overlays.remove('win')` by timer or tap | Overlay hangs forever, blocks the game | Add auto-dismiss Timer + tap-to-dismiss |
| C4 | **Settings are not saved** | Settings screen without `SharedPreferences` calls | Settings are reset on restart | Add SharedPreferences load/save |
| C5 | **Settings not applied** | Sound toggle is not checked before playback | The sound plays even if it is turned off | Add check `isSoundEnabled` before `FlameAudio.play` |
| C6 | **Daily Bonus gives endlessly** | No last received date check | The player can receive the bonus unlimitedly | Add `SharedPreferences` with date + check |
| C7 | **Leaderboard not updating** | No record of result after game | Leaderboard is always empty | Add score entry for Game Over / new high score |
| C8 | **Profile does not save** | Nickname/avatar is not recorded in SharedPreferences | Data is lost on restart | Add persistence |
| C9 | **Splash does not transition** | Splash screen without `Timer` or `Future.delayed` for auto-navigation | Application gets stuck on splash | Add `Future.delayed(Duration(seconds: 2), () => Navigator.pushReplacementNamed(context, '/menu'))` |
| C10 | **Multiple push without replacement** | `Navigator.pushNamed` instead of `pushReplacementNamed` for splash→menu | The navigation stack grows, the back button leads back to splash | Use `pushReplacementNamed` for splash→menu |

### Category D: BUTTONS AND INTERACTION (High - UX bugs)

| # | Check | How to find | Symptom | Autofix |
|---|---------|-----------|---------|----------|
| D1 | **Double click on action button** | Spin/Play button without `isSpinning`/`isPlaying` check | Two spins/actions at the same time, the balance is debited twice | Add `if (isPlaying) return;` + debounce 300ms |
| D2 | **Bet changes during action** | Bet+/Bet- buttons without disabled state at `isSpinning` | The bet changes between debiting and accruing winnings | Add `IgnorePointer(ignoring: isSpinning)` or disabled state |
| D3 | **Button without feedback** | `GestureDetector(onTap:)` without animation when pressed | The user does not understand whether he clicked | Add `AnimatedScale` (0.95 when pressed) or `InkWell` with splash |
| D4 | **Tap target < 48px** | Buttons/icons with `width` or `height` < 48 | Difficult to click on mobile | Wrap in `SizedBox(width: 48, height: 48)` or add padding |
| D5 | **Invisible tap blocker** | `Opacity(opacity: 0)` or `Container(color: Colors.transparent)` with `GestureDetector` over content | The user clicks - nothing happens, although the button is visible | Remove invisible blocker or add `IgnorePointer` |
| D6 | **Scroll inside scroll** | `ListView` inside `ListView` without `shrinkWrap: true` + `NeverScrollableScrollPhysics` | Gesture conflict, unable to scroll | Add `shrinkWrap: true, physics: NeverScrollableScrollPhysics()` to internal |
| D7 | **No handling of empty state** | `ListView.builder(itemCount: items.length)` without check `items.isEmpty` | Blank screen with no explanation | Add `if (items.isEmpty) return EmptyStateWidget(...)` |
| D8 | **GestureDetector intercepts scrolling** | `GestureDetector` with `onVerticalDragUpdate` inside `ListView` | Scroll doesn't work | Use `onTap` or `Listener` instead of drag gestures |
| D9 | **Action button doesn't show disabled** | The "SPIN" / "PLAY" button is visually the same in enabled and disabled | User clicks - nothing happens - frustration | Add visual difference: dull color, lower opacity, different icon |
| D10 | **No Insufficient Funds Processing** | With `balance < bet` there is no check before action | The balance goes into minus OR nothing happens when you press | Add check + show InsufficientFundsDialog |

### Category E: DESIGN INTENT (Medium - contextual design)

> We do not check “whether there is neon glow.” We check: “is there INTENTION behind every decision.”
> Read `.claude/rules/anti-slop-design.md` to understand the principle.
> Also read the game's UI Read, Design Signature, state map, recipes, and Similarity Check.
>
> 🛑 **AUDIT GUARD - do not change one slop for another.** This audit checks the INTENT,
> CONSISTENCY and CRAFT are NEVER a specific style. DO NOT "fix" the screen by adding
> neon, glassmorphism, beveled buttons or dark theme if they are not in the Design Signature. A
> bright, cozy screen or restrained standard control can pass. Any autofix must move the UI toward
> the recorded signature and state job, not toward a studio house style.

| # | Check | How to check | Autofix |
|---|---------|--------------|----------|
| E1 | **Semantic theme is applied** | Default theme values make hierarchy/states inconsistent with the signature | Define only the missing semantic roles; do not restyle for novelty |
| E2 | **Loading/committed state fits the job** | Loader obscures state, lacks progress/meaning, or conflicts with the signature | Choose a standard or thematic indicator that communicates the actual wait |
| E3 | **Blocking surfaces are appropriate** | Dialog/sheet/screen choice mismatches interruption level or content length | Use the recorded O recipe and restore focus on close |
| E4 | **Transitions have a reason** | Motion exists only as decoration or continuity is unclear | Simplify or implement the recorded transition reason; standard/direct is allowed |
| E5 | **No print()** | `print(` | → `debugPrint` or delete |
| E6 | **There are animations.dart** | `lib/theme/animations.dart` does not exist | Create file |
| E7 | **No hard-skinned Duration in screens** | `Duration(milliseconds:` outside animations.dart | → `AnimationConfig.xxx` |
| E8 | **Design Signature exists and is in use** | Are field/controls/HUD/material/type/color/motion decisions reflected in implementation? | Create missing signature/state documentation or align the implementation |
| E9 | **Colors based on context** | Read game_theme.dart - do the colors match the theme of the game? (forest = green OK, casino = gold OK, random purple = NO) | Adjust palette |
| E10 | **Fonts match the mood** | Does the font suit the game world? (retro slot machine = pixelated, elegant casino = serif, cozy bingo = rounded) | Replace with a suitable one |
| E11 | **Control roles are distinct** | Primary, secondary, dangerous, disabled, and contextual actions communicate their roles | Align with the signature without forcing one shape on every control |
| E12 | **Coherent, not cloned** | Semantic roles persist across screens while screen jobs may use different recipes | Repair unexplained drift or inappropriate structural repetition |
| E13 | **Menu recipe and memorable idea** | Menu implements its M/O/R recipe and is not merely the studio's recurring shell | Recompose to the recorded job; do not automatically add a centerpiece/layers |
| E14 | **State-aware game UI** | Field meets contract; C/H recipes and attention order hold in setup, anticipation, and result | Fix the failing state instead of forcing every HUD to the edges |

### Category F: MISSING SCREENS (Medium)

| # | Check | How to check |
|---|---------|--------------|
| F1 | Splash Screen | `glob lib/screens/splash*` |
| F2 | Main Menu | `glob lib/screens/main_menu*` |
| F3 | Game Screen | `glob lib/screens/game_screen*` |
| F4 | HUD Widget | `glob lib/screens/hud*` |
| F5 | Paytable / Rules | `glob lib/screens/paytable*` |
| F6 | Settings | `glob lib/screens/settings*` |
| F7 | Help | `glob lib/screens/help*` |
| F8 | Win Overlay | `glob lib/screens/win_overlay*` |
| F9 | Insufficient Funds | `grep 'insufficient\|InsufficientFunds'` in screens |
| F10 | Game Theme | `glob lib/theme/game_theme*` |
| F11 | Daily Bonus | `glob lib/screens/daily_bonus*` |
| F12 | Leaderboard | `glob lib/screens/leaderboard*` |
| F13 | Profile | `glob lib/screens/profile*` |

### Category G: UX POLISH (Low - but makes the difference between “works” and “want to play”)

| # | Check | How to check | Autofix |
|---|---------|--------------|----------|
| G1 | Semantic type roles are implemented | Inspect display/readout/action/body/legal roles and readability | Add or consolidate roles; one family may be correct |
| G2 | Action button: idle + press + disabled visually distinguishable | Read button code | Add feedback from the Design Signature |
| G3 | Meaningful value changes communicate magnitude | Observe balance/win/risk/progression changes | Animate only changes that matter; stable utility values may update directly |
| G4 | Interactive elements acknowledge input | Inspect code and runtime for immediate, role-appropriate pressed/committed feedback | Add the feedback behavior recorded by the signature; scaling is only one option |
| G5 | Result tiers are distinguishable | Compare routine/notable/major outcomes against the state map | Differentiate locally or globally as documented; a win overlay is optional |
| G6 | Text to background contrast >= 4.5:1 | Check colors in theme | Adjust |
| G7 | Game screen: mechanic dominates and the next action is clear | Measure the field and inspect hierarchy against `gameplay-screen-contract.md` | Expand/integrate the field; clarify the recorded action or direct-manipulation affordance |
| G8 | Empty states are useful and in voice | `grep 'empty\|EmptyState\|no data'`; verify explanation and next step | Add concise copy and an action; illustration is optional |
| G9 | Loading/committed state is clear and accessible | Inspect waiting states and interruption/retry behavior | Use the simplest indicator that fits the job/signature |
| G10 | **Wireframe distinction test** | Does field/control/HUD/menu structure remain specific in grayscale without art? | Rework interaction/composition; palette/mascot swaps do not count |
| G11 | **Gameplay field alignment is intentional** | `python3 tools/check_gameplay_center.py` plus screenshots: centered by default, or the recipe records a concrete offset reason | Remove unexplained offsets or document and verify the recipe's reason |

### Category H: CRAFT & COMPOSITION (Low is what distinguishes a “designer” screen from a generated one)

> This is not about style, but about craft. Applicable to every Design Signature. See
> "Craft floor without a house style" in `anti-slop-design.md`.

| # | Check | How to find | Autofix |
|---|---------|-----------|----------|
| H1 | **Semantic type system** | Named roles are reused; no unexplained one-off sizes; roles remain readable | Consolidate or add a justified role, without a fixed role count |
| H2 | **Spacing rhythm** | Named spacing/grouping tokens express relationship and touch ergonomics | Replace arbitrary gaps with project tokens; no universal 4/8 mandate |
| H3 | **Color-role discipline** | Every hue/value has a semantic or material role; critical meaning is redundant | Remove roleless colors or fix semantic mapping; no universal accent cap |
| H4 | **Attention order by state** | Setup, anticipation, result, and recovery match their recorded first/second/third reads | Repair hierarchy for that state; dual focus is allowed when documented |
| H5 | **Role-based geometry** | Shape differences follow control/surface/material roles | Fix unexplained mixing; do not force one radius everywhere |
| H6 | **Intentional alignment and balance** | Shared edges or object-relative placement look chosen and safe-area aware | Fix near-misses while preserving documented asymmetry |
| H7 | **Restraint effects** | There is no “soup” of weak shadows/gradients; the effects are meaningful | Remove unnecessary effects |
| H8 | **Unified iconography** | Icons in the same style and stroke thickness | Bring to one style |
| H9 | **Recipe and anti-repeat matching** | Screens follow recorded F/C/H/M/O/R recipes and the Similarity Check is honest | Recompose the mismatched screen or update the rationale with evidence |

### Category I: LIVE GAMEPLAY FEEDBACK (Medium - state change inside the field, not menu decoration)

> Inspect `lib/components/` and the live round. A still setup state can be deliberate. Failure means
> commitment, anticipation, result, or recovery is unreadable because field state snaps or only the
> surrounding HUD reacts. Apply `juice-artist.md` §0.5 and the recorded state map.

| # | Check | How to find | Autofix |
|---|---------|-----------|----------|
| I1 | **Idle behavior matches the signature** | Runtime observation plus reduced-motion path | Keep deliberate stillness or add only the documented contextual loop |
| I2 | **Commitment is acknowledged on the field** | Compare the pre-action and immediate post-input frames | Add a mechanic-specific cue; entrance travel is optional |
| I3 | **Anticipation/reveal remains readable** | Observe what changes before and at the predetermined result | Add only the feedback roles needed to explain the transition |
| I4 | **Result and recovery are distinct** | Compare field states, not only HUD/overlay pixels | Make the outcome and return-to-play state unambiguous; direct changes may be valid |
| I5 | **Selected hooks are actually called** from logic | Trace each feedback hook from state transition to component | Wire the missing selected hooks; do not create unused animation APIs |
| I6 | **No allocations** in `update()`/`render()` components | `Vector2(`/`Paint()`/`Rect.` inside update | Preinitialize fields |
| I7 | **Timing roles are centralized** | Compare used timings with `AnimationConfig` and reduced-motion values | Centralize repeated/semantic timings without forcing one cadence on all events |

> ⚠️ If autofix requires significant work (to revive the entire gameplay) - delegate it to an agent
> **juice-artist** via Agent tool (Gameplay Feel Pass role), as in Phase 6.5 `/autocreate`.

### Category J: PRODUCTION COMPLETENESS & COMPLIANCE (Medium - “full game”, not demo)

> The difference between the full game and the mini-demo: the amount of content, the meta-loop and the compliance layer.
> We check the presence of subsystems and integration points, and not just one game loop. Category - from
> `design/gdd/game-concept.md` (Production Plan section). If the game is intentionally one-level
> (e.g. pure endless without meta) - mark N/A with justification, do not force content for the sake of content.

| # | Check | How to find | Autofix |
|---|---------|-----------|----------|
| J1 | **Content = data, not one point** | There is a category content config and >1 entries (`bet-tiers.json` C1/C2, `stage-config.json` C3, `banners.json` C4, `run-config.json` C5, `board-config.json` C6) | Generate content config (Phase 3.7 autocreate) |
| J2 | **Level/Mode Select linked to data** | the screen reads the real list of levels/modes, not hardcode 3 buttons | Link to ProgressionService/config |
| J3 | **Modes implemented** | enum modes + branching in Game (Classic + ≥1 more) | Add mode parameter to GameScreen |
| J4 | **SaveService single** | no scattering of straight lines `SharedPreferences.getInstance()` across the screens | Consolidate to SaveService |
| J5 | **Economy connected** | EconomyService + Shop read/spend currency; victories are awarded | Connect your store to Economy |
| J6 | **Progression preserved** | open levels/stars/best scores written and read | Add recordResult/unlock |
| J7 | **Achievements working** | list + event check + reward | Subscribe to events |
| J8 | **Analytics calls arranged** | `grep -rn "analytics\.\(log\|logEvent\)" lib/` non-empty (screen_view + level_* + game_action) | Add calls (no-op service) |
| J9 | **No external SDKs by default** | `firebase_`/`google_mobile_ads`/`in_app_purchase` NOT in pubspec | Replace with abstraction + no-op |
| J11 | **Disclaimer** | “Playing with virtual chips...Success does not mean success in gambling for real money” on splash + in the rules | Add a line to `ComplianceCopy` and print |
| J12 | **Responsible-play** | Block in settings: session reminder, “take a break”, help contacts | Add block to settings |
| J13 | **Odds disclosure** | The Odds screen is available BEFORE spending currency (required for C4 and C3 paid spins) | Add screen, read numbers from model config |
| J14 | **No real currency on balance** | `grep -rnE '\$\{?balance\|USD\|€\|₽' lib/` empty (except IAP screen) | Remove real currency symbols |
| J15 | **No promises to win** | `grep -rniE 'real money\|real money\|win money\|payout\|earn' lib/ store/` empty | Rewrite texts |
| J16 | **Shown = config** | The numbers in the paytable/odds screen match the JSON config of the mathematical model | Link UI to config, do not duplicate |

> J10–J12 — **compliance release blockers** (without them the store will reject). Mandatory for everyone
> categories; weakening is only possible for C5 without purchases - see `.claude/rules/responsible-gaming.md`.
> J1–J9 - about “completeness”: if they are not there, the game is functional, but a mini-demo remains. Mark as
> Medium and repair where the Production Plan of the concept provides for it.

---

## Phase 3 - Auto-correction

### Order of corrections (STRICTLY)

**Stage 1 - Crash Vulnerabilities (A1-A10):**
Fix ALL potential crashes. Each correction - read the file → understand the context → spot Edit.

**Typical fixes for category A:**

```dart
// A1: RenderFlex overflow - Column in Column
// WAS:
Column(children: [
  Column(children: [Widget1(), Widget2(), Widget3()])
])
// NOW:
Column(children: [
  Expanded(child: Column(children: [Widget1(), Widget2(), Widget3()]))
])

// A2: ListView in Column
// WAS:
Column(children: [Header(), ListView.builder(...)])
// NOW:
Column(children: [Header(), Expanded(child: ListView.builder(...))])

// A3: setState after dispose
// WAS:
Future.delayed(Duration(seconds: 2), () {
  setState(() { _showOverlay = false; });
});
// NOW:
Future.delayed(Duration(seconds: 2), () {
  if (!mounted) return;
  setState(() { _showOverlay = false; });
});

// A4: AnimationController without dispose
// WAS:
class _MyState extends State<My> with SingleTickerProviderStateMixin {
  late final _ctrl = AnimationController(vsync: this, duration: ...);
}
// NOW:
class _MyState extends State<My> with SingleTickerProviderStateMixin {
  late final _ctrl = AnimationController(vsync: this, duration: ...);
  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }
}

// A5: Timer without cancel
// WAS:
Timer.periodic(Duration(seconds: 1), (t) { ... });
// NOW:
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

**Stage 2 - Layout errors (B1-B16):**
Fix all layout problems. Special attention: SafeArea, overflow, mobile-first responsive
constraints, full-viewport gameplay composition, platform targeting, and control proportions.
Do not “fix” B11–B16 by wrapping the whole game screen in a scroll view.

**Stage 3 - Navigation and Status (C1-C10):**
Check all routes, all persistence, all overlay lifecycle.

**Stage 4 - Buttons and Interactions (D1-D10):**
Ensure that each button has feedback, double-click protection, and a disabled state.

**Stage 5 - Anti-Slop (E1-E14):**
Fix unsupported defaults and contradictions with the recorded Design Signature. Make the menu's
M/O/R recipe legible (E13) and make the HUD's H recipe and state behavior legible (E14). A custom
widget is not automatically better than a standard control, and a centerpiece is not mandatory.

**Step 6 - Missing Screens (F1-F13):**
Create missing screens using Agent (ui-programmer).

**Stage 7 - Visual quality + craft (G1-G11, H1-H9):**
Polish - fonts, animations, micro-interactions, type-scale, indents, alignment.

**Stage 8 - Live Gameplay (I1-I7):**
Animate game components on the field (idle/entrance/impact/state) and associate hooks with events.
For large volumes, delegate juice-artist (“Gameplay Feel Pass”) to the agent via the Agent tool.

---

## Phase 4 - Verification (MANDATORY)

```bash
dart analyze lib/
```

If errors from autofixes appear → correct (up to 5 attempts).

Then check that autofixes do not break functionality:
```bash
flutter test
```

If tests fail → fix (up to 3 attempts). If the test is correct, fix the code, not the test.

### Integrated runtime proof

Static analysis and widget tests cannot approve visual composition or prove that configured
assets actually render. Before a final `PASS`, run the game and capture at minimum:

- idle gameplay and one active/resolved action at the phone baseline; and
- idle gameplay at one expanded viewport from the mobile-first matrix.

Use the runtime screenshots to verify B11–B16 and A7 directly. Record the field bounds or
usable gaps, confirm there is no unexplained dead region or edge-pinned mechanic, and compare
every configured visual item with what appears in the live outcome set. Inspect console/runtime
errors and reject captures whose renderer failed to paint raster layers.

If the project cannot be executed, the audit may report source and test findings, but its
overall result is `RUNTIME PENDING`, never `PASS`. Do not describe runtime review as deferred
inside a PASS report.

---

## Phase 5 - Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 UI/UX AUDIT COMPLETE — DEEP SCAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Screens: [N] found / [M] created
🧩 Widgets: [N] found

💥 A: Crash vulnerabilities (Critical):
   [✅|❌] A1: RenderFlex overflow - [status]
   [✅|❌] A2: ListView in Column - [status]
   [✅|❌] A3: setState after dispose - [status]
   [✅|❌] A4: AnimationController dispose - [status]
   [✅|❌] A5: Timer/Stream cancel — [status]
   [✅|❌] A6: Navigator.pop safety - [status]
   [✅|❌] A7: Asset existence - [status]
   [✅|❌] A8: Font registration - [status]
   [✅|❌] A9: Infinite constraints - [status]
   [✅|❌] A10: Missing Keys - [status]
   Total: [X]/10

📐 B: Layout errors (High):
   [✅|❌] B1-B10: [responsive/safe layout status]
   [✅|❌] B11-B15: [field dominance, no nested window/scroll, integrated usable controls]
   [✅|❌] B16: [mobile-first full-viewport responsiveness and platform configuration]
   Total: [X]/16

🧭 C: Navigation and Status (High):
   [✅|❌] C1-C10: [short status]
   Total: [X]/10

👆 D: Buttons and interactions (High):
   [✅|❌] D1-D10: [short status]
   Total: [X]/10

🎨 E: Anti-Slop + menu/HUD (Medium):
   [✅|❌] E1-E14: [short status, on. E13 concept menu, E14 discreet HUD]
   Total: [X]/14

📱 F: Screens (Medium):
   [✅|❌] F1-F13: [short status]
   Total: [X]/13

✨ G: Visual quality (Low):
   [✅|❌] G1-G11: [short status]
   Total: [X]/10

🎯 H: Craft & Composition (Low):
   [✅|❌] H1-H9: [short status - type-scale, indents, palette, focus, shapes, alignment, effects, icons, layout]
   Total: [X]/9

🕹 I: Live gameplay (Medium):
   [✅|❌] I1-I7: [idle, entrance, impact, state-transition, hook calls, allocations, timings]
   Total: [X]/7

🏗 J: Production completeness & compliance (Medium):
   [✅|❌] J1-J9: [content-data, level/mode select, modes, SaveService, economy, progression,
          achievements, analytics calls, no external SDK]
   [✅|❌] J10-J12 (gambling): [disclaimer, responsible-play] - release blockers
   Total: [X]/16 (J10-J16 = compliance blockers; N/A only for C5 without purchases)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 OVERALL RESULT: [PASS ✅ | RUNTIME PENDING ⏳ | NEEDS FIX ⚠️ | BLOCKED ❌]

   Issues found: [X]
   Autocorrected: [Y]
   Require manual intervention: [Z]

   Critical (crash): [N] ← MUST BE 0
   Layout (visual bug): [N] ← MUST BE 0
   Navigation/State: [N] ← MUST BE 0
   UX (interaction): [N] ← MUST BE 0
   Anti-Slop: [N]
   Screens: [N]
   Visual quality: [N]
   Craft & composition: [N]

   Verdict: PASS = 0 Critical + 0 High + integrated runtime proof complete
            RUNTIME PENDING = source/test review complete but required runtime proof unavailable
            NEEDS FIX = any High unclosed
            BLOCKED = any Critical unblocked
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
