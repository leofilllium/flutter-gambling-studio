---
name: emulator-test
description: "Runtime verification of a finished mini-game. Primary platform - Chrome/Web (does not require an emulator). Fallback: Android ADB → iOS. Launches the application, navigates through screens, takes screenshots, visually analyzes via vision, parses flutter-run.log/logcat for exceptions, automatically fixes found bugs. Integrated into /autocreate after dart analyze."
argument-hint: "[--device deviceId | --platform web|android|ios | --no-fix | --quick]  (default: web/chrome)"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Emulator Test - Runtime verification (Chrome/Web-first)

**Problem**: `dart analyze` + `flutter test` **do not see** runtime problems that appear
only at startup: empty game screen (black rectangle instead of reels), RenderFlex
overflow (yellow-black stripes), Flutter "red screen of death" (raw exception),
layout curve at a specific resolution, `setState() called after dispose`, missing asset, etc.

**This is an insurance skill**: launches the phone game in **Chrome** (default, without an emulator),
navigates through all screens, takes screenshots, **visually analyzes them through vision**
and **parses flutter-run.log** for exceptions. Found - automatically repairs.

Chrome is only a portrait-phone preview harness. Read `.claude/docs/mobile-phone-contract.md`;
never treat the browser as a desktop/tablet target or approve a wide reflow.

**Platforms by priority:**
1. **Chrome/Web (default)** - headless `flutter run -d web-server` + headless Chrome via CDP
   (`tools/web_verify.mjs`). No emulator/display/`xdotool` needed. All you need is `node` and the Chrome binary.
2. Android ADB - fallback at `--platform android` or if the web path is not possible
3. iOS Simulator - only with explicit `--platform ios` (macOS)

**Modes:**
- Default: full cycle (find → visually analyze → fix → restart)
- `--no-fix`: only report without changes
- `--quick`: main screens only (splash/menu/game), without daily-bonus/leaderboard/profile
- `--device <id>`: use specific device (aka Chrome auto-select)
- `--platform web|android|ios`: Force platform selection (**default: web**).

---

## Phase 0 - Environment Preflight [~15 sec]

**Default platform - Chrome web** (headless `web-server` + CDP). Does not require an emulator/display.
Auto-selection order: web → Android (ADB) → iOS.
The forced choice is `--platform android|web|ios`.

```bash
# Flutter check
flutter --version || { echo "❌ Flutter not found in PATH"; exit 1; }

# All available devices
flutter devices

# Android (ADB)
adb version 2>/dev/null || echo "⚠️ adb not found"
adb devices -l 2>/dev/null

# Chrome / web
flutter devices 2>/dev/null | grep -iE "Chrome|web" && echo "✅ Chrome web available"

# iOS (macOS only)
xcrun simctl list devices booted 2>/dev/null
```

### Platform selection algorithm

```bash
# 1. Android: already running emulator or connected device
RUNNING_ANDROID=$(adb devices 2>/dev/null | grep -E "device$" | grep -v "^List" | head -1 | awk '{print $1}')

#2. Chrome web: always available if Flutter recognizes Chrome
CHROME_DEV=$(flutter devices 2>/dev/null | grep -iE "Chrome|web-server" | head -1 | awk -F'•' '{print $2}' | xargs)

# 3. iOS: running simulator (macOS only)
IOS_DEV=$(xcrun simctl list devices booted 2>/dev/null | grep "Booted" | head -1)

# Chrome - first priority (does not require an emulator)
if [[ -n "$CHROME_DEV" ]]; then
  PLATFORM=${PLATFORM:-web}
  echo "🌐 Chrome web: $CHROME_DEV (default)"
elif [[ -n "$RUNNING_ANDROID" ]]; then
  PLATFORM=${PLATFORM:-android}
  echo "✅ Android fallback: $RUNNING_ANDROID"
elif [[ -n "$IOS_DEV" ]]; then
  PLATFORM=${PLATFORM:-ios}
  echo "✅ iOS simulator fallback"
else
  echo "🌐 No native devices → headless web (web-server + CDP)."
  PLATFORM=${PLATFORM:-web}
fi
```

### If there is no device - auto-start

**Chrome web (priority 1 - default):**
You don't need an emulator or an open browser window. The game is distributed headless via
`flutter run -d web-server`, and headless Chrome takes pictures/taps via CDP (`tools/web_verify.mjs`).
It is enough for the system to have `node` and the Chrome binary (`google-chrome`/`chromium`, or
`$CHROME_EXECUTABLE`). Display/`xdotool`/`osascript` are NOT required.

**Android AVD (priority 2 - fallback):**
```bash
# Only if KVM is available and with hard timeouts for each step - otherwise headless hang
# (unlimited adb wait-for-device - the main source of “stuck on the emulator”).
AVD=$(emulator -list-avds 2>/dev/null | head -1)
if [[ -n "$AVD" && -e /dev/kvm ]]; then
  emulator -avd "$AVD" -no-window -no-snapshot-save -no-boot-anim -gpu swiftshader_indirect -no-audio &
  EMU_PID=$!
  if timeout 90 adb wait-for-device 2>/dev/null && \
     timeout 180 bash -c 'until [ "$(adb shell getprop sys.boot_completed 2>/dev/null|tr -d "\r")" = "1" ]; do sleep 2; done'; then
    PLATFORM=android
  else
    echo "⚠️ AVD did not load on time - skip Android."
    kill "$EMU_PID" 2>/dev/null || true
  fi
elif [[ -n "$AVD" ]]; then
  echo "⚠️ AVD is there, but /dev/kvm is not - launching a fresh emulator is skipped (it would freeze)."
fi
```

**iOS (priority 3, macOS only):**
```bash
xcrun simctl boot "iPhone 15" 2>/dev/null
open -a Simulator 2>/dev/null
PLATFORM=ios
```

**Phase 0 exit criterion**: `PLATFORM` set (android / web / ios).

---

## Phase 1 - Build & Install [~2 min]

```bash
flutter pub get
dart analyze lib/ | tail -5
mkdir -p .claude/runtime-logs
```

### Android (PLATFORM=android)

```bash
IMPELLER_FLAG=""
[[ "$NO_IMPELLER" == "1" ]] && IMPELLER_FLAG="--no-enable-impeller"
flutter run -d "$RUNNING_ANDROID" --verbose $IMPELLER_FLAG \
  > .claude/runtime-logs/flutter-run.log 2>&1 &
FLUTTER_PID=$!
echo $FLUTTER_PID > .claude/runtime-logs/flutter.pid

for i in $(seq 1 120); do
  grep -q "Syncing files to device\|Flutter run key commands" \
    .claude/runtime-logs/flutter-run.log 2>/dev/null && { echo "✅ Running (Android)"; break; }
  sleep 1
done

# Parallel to logcat
adb logcat -c
adb logcat -v time flutter:V *:E > .claude/runtime-logs/logcat.log 2>&1 &
LOGCAT_PID=$!
echo $LOGCAT_PID > .claude/runtime-logs/logcat.pid
```

### Chrome / Web (PLATFORM=web) - does not require an emulator and **does not require a display**

> **Why `web-server` and not `-d chrome`:** `flutter run -d chrome` opens a GUI window,
> which then has to be controlled via `xdotool`/`osascript` - and they are unavailable or
> unreliable in headless/Wayland sessions. Plus `flutter screenshot` **does not support web**.
> So we bring up the game headless via `web-server` and shoot/navigate **headless Chrome
> via Chrome DevTools Protocol** (`tools/web_verify.mjs`). This works without a display, gives
> real PNGs with CanvasKit canvases and real taps.

```bash
mkdir -p .claude/runtime-logs
WEB_PORT="${WEB_PORT:-8099}"

# Headless dev-server: compiles and distributes the game without opening the browser.
nohup flutter run -d web-server --web-port "$WEB_PORT" --web-hostname 127.0.0.1 \
  > .claude/runtime-logs/flutter-run.log 2>&1 &
echo $! > .claude/runtime-logs/flutter.pid

# We are waiting for the line "is being served at http://127.0.0.1:PORT" - but with a hard limit and
# exit early if there is a compilation error (otherwise the phase hangs on a broken assembly).
WEB_URL=""
for i in $(seq 1 120); do
  WEB_URL=$(grep -oE "http://127\.0\.0\.1:[0-9]+" .claude/runtime-logs/flutter-run.log 2>/dev/null | head -1)
  [ -n "$WEB_URL" ] && { echo "✅ web-server: $WEB_URL"; break; }
  if grep -qE "Failed to compile|Target dart2js failed|^Error: |Compilation failed" .claude/runtime-logs/flutter-run.log 2>/dev/null; then
    echo "❌ web build failed - see flutter-run.log (Phase 'If build failed')"; break
  fi
  sleep 2
done
[ -z "$WEB_URL" ] && WEB_URL="http://127.0.0.1:$WEB_PORT"  # fallback
```

**Logcat for web**: adb logcat is not available. Instead, runtime exceptions are collected from
**two** sources: `.claude/runtime-logs/flutter-run.log` (Flutter/VM stdout) **and**
`<SHOT_DIR>/webconsole.log`—browser console output and uncaught exceptions that
`web_verify.mjs` captures via CDP (`Runtime.consoleAPICalled`, `Runtime.exceptionThrown`,
and `Log.entryAdded`).

### If build is down

Read `.claude/runtime-logs/flutter-run.log`, extract Gradle/CocoaPods/Dart compilation errors,
correct and repeat. Maximum 3 iterations. If it fails, finish with a report.

---

## Phase 2 - Screenshot Tour [~3 min]

**Strategy**: navigate the game on the selected platform, wait 1–2 seconds after every
screen animation, and capture a screenshot. Chrome/Web is the default. Android uses ADB
input events; iOS uses `xcrun simctl io booted screenshot`.

### Chrome / Web screenshots (PLATFORM=web) - headless CDP phone matrix

`flutter screenshot` **does not support web** (only `device`/`skia` for native devices),
and `xdotool`/`osascript` are unavailable/unreliable headless. Therefore, the canonical tour and
three compact geometry tours use `tools/web_verify.mjs`: it picks up headless Chrome itself, shoots footage via CDP,
taps on the canvas (on the semantic mark, otherwise on the thumb-zone), writes console/exceptions and
always completes within `--budget` and cannot hang the pipeline.

```bash
TS=$(date +%Y%m%d-%H%M%S)
SHOT_DIR="production/runtime-screenshots/$TS"
mkdir -p "$SHOT_DIR"

# --budget — internal script deadline; external `timeout` - insurance from above.
# --quick - only splash→menu→game→action (for /autocreate).
# Canonical phone tour. In full mode this is the all-screen capture.
timeout 220 node tools/web_verify.mjs \
  --url "$WEB_URL" --out "$SHOT_DIR" --size 390x844 --budget 180 ${QUICK_FLAG:-} \
  2>&1 | tee "$SHOT_DIR/web_verify.log"

# Required portrait-phone geometry matrix. These are quick gameplay tours.
for PHONE_SIZE in 360x640 360x800 430x932; do
  PHONE_DIR="$SHOT_DIR/$PHONE_SIZE"
  mkdir -p "$PHONE_DIR"
  timeout 140 node tools/web_verify.mjs \
    --url "$WEB_URL" --out "$PHONE_DIR" --size "$PHONE_SIZE" --budget 120 --quick \
    2>&1 | tee "$PHONE_DIR/web_verify.log"
done
```

The canonical script places in `$SHOT_DIR`: `01-splash.png … 05-game-after-action.png` (+ additional screens without
`--quick`), `webconsole.log` (console+browser exceptions) and `manifest.json`. The other required
phone sizes use subdirectories named after the viewport, with the same quick-tour files
(`{ steps, semanticLabels, consoleErrors, shots }`).

**Navigation:** the script first tries to find the action button by `aria-label`
(Flutter semantics - studio requires `Semantics(label: …)` on the main button: `play/spin/
play/start/spin`), and only if there is no mark - taps the thumb zone (center of the lower 60%). This covers
all layout archetypes L1–L6 without guessing window coordinates.

**Parsing Chrome errors**: grep on `manifest.json` (`consoleErrors`) and `webconsole.log`
(EXCEPTION, RenderFlex overflowed, Unable to load asset) **plus** `flutter-run.log`
(compilation errors). A separate logcat is not needed.

---

### ⚠️ Impeller caveat (root cause of “invalid image”)

On Android, Flutter uses Impeller by default. `adb exec-out screencap -p` **doesn't see
Impeller surface** on a number of devices and returns either a black frame or a broken PNG
color space, which vision analysis rejects as “invalid image”.

**Therefore, the primary withdrawal method is `flutter screenshot`** (read from the Flutter side, Impeller-safe).
`adb exec-out screencap -p` is used only as a fallback. After each photo we **validate
PNG signature** (`89 50 4E 47`). If the file is not PNG, retry using an alternative method.

### Coordinates for navigation

Since we don't know the exact button coordinates for each game, we use a heuristic:
1. Get device permission: `adb shell wm size` → for example `1080x2400`
2. Center tap - in the center: `adb shell input tap 540 1200`
3. Bottom action tap - lower third: `adb shell input tap 540 2000` (Play/Spin button is usually here)
4. Back: `adb shell input keyevent KEYCODE_BACK`

### Sequence of screenshots

Create a directory `production/runtime-screenshots/<timestamp>/` and shoot into it.

```bash
TS=$(date +%Y%m%d-%H%M%S)
SHOT_DIR="production/runtime-screenshots/$TS"
mkdir -p "$SHOT_DIR"

# Platform fixed: web/chrome (default). Overridden by --platform android|ios.
PLATFORM="${PLATFORM:-web}"
DEVICE_ID="${DEVICE_ID:-}" # if empty, flutter will take the first device

# PNG check: first 8 bytes must be 89 50 4E 47 0D 0A 1A 0A
is_valid_png() {
  local f=$1
  [[ -s "$f" ]] || return 1
  local sig
  sig=$(xxd -l 8 -p "$f" 2>/dev/null)
  [[ "$sig" == "89504e470d0a1a0a" ]]
}

# One shot with triple fallback + validation
shoot() {
  local name=$1
  local out="$SHOT_DIR/$name.png"
  local tmp="$SHOT_DIR/.$name.tmp"

  if [[ "$PLATFORM" == "ios" ]]; then
    xcrun simctl io booted screenshot "$out" 2>/dev/null
    is_valid_png "$out" && { echo "✅ $name (ios simctl)"; return 0; }
    echo "❌ $name - simctl did not return a valid PNG"
    return 1
  fi

  if [[ "$PLATFORM" == "web" || "$PLATFORM" == "chrome" ]]; then
    # web does NOT use this function - the whole tour is done by tools/web_verify.mjs via CDP
    # (`flutter screenshot` does not support web). This branch is just a safety net.
    echo "ℹ️ $name - for web use tools/web_verify.mjs (see “Chrome / Web screenshots”)"
    return 1
  fi

  # ANDROID (default)

  # Attempt 1: flutter screenshot - Impeller-safe, shoots from the Flutter side
  local dev_arg=""
  [[ -n "$DEVICE_ID" ]] && dev_arg="-d $DEVICE_ID"
  flutter screenshot $dev_arg --type=device -o "$out" >/dev/null 2>&1 || true
  if is_valid_png "$out"; then
    echo "✅ $name (flutter screenshot)"
    return 0
  fi

  # Attempt 2: adb exec-out screencap -p (classic)
  # IMPORTANT: exactly exec-out, not `adb shell` - otherwise LF→CRLF will break the PNG
  adb ${DEVICE_ID:+-s $DEVICE_ID} exec-out screencap -p > "$tmp" 2>/dev/null
  if is_valid_png "$tmp"; then
    mv "$tmp" "$out"
    echo "✅ $name (adb screencap)"
    return 0
  fi

  # Attempt 3: screencap on device → pull (bypasses stdout corruption)
  adb ${DEVICE_ID:+-s $DEVICE_ID} shell screencap -p /sdcard/_shot.png 2>/dev/null
  adb ${DEVICE_ID:+-s $DEVICE_ID} pull /sdcard/_shot.png "$out" >/dev/null 2>&1
  adb ${DEVICE_ID:+-s $DEVICE_ID} shell rm /sdcard/_shot.png 2>/dev/null
  if is_valid_png "$out"; then
    echo "✅ $name (adb pull)"
    return 0
  fi

  # Complete failure - leave the file for diagnostics, but mark
  mv "$tmp" "$out.INVALID" 2>/dev/null || true
  echo "❌ $name - all 3 methods returned an invalid PNG. Check:"
  echo " - Impeller: restart with --no-enable-impeller"
  echo "Is your device screen unlocked?"
  echo " - file \"$out.INVALID\" (must be PNG image data, not ASCII)"
  return 1
}

# Navigation assist (Android ADB tap or Chrome/macOS click)
nav_tap() {
  # Android/iOS only. For web, navigation is done by tools/web_verify.mjs via CDP.
  local x=${1:-540} y=${2:-2000}
  [[ "$PLATFORM" == "android" ]] && adb ${DEVICE_ID:+-s $DEVICE_ID} shell input tap "$x" "$y"
}
nav_back() {
  [[ "$PLATFORM" == "android" ]] && adb ${DEVICE_ID:+-s $DEVICE_ID} shell input keyevent KEYCODE_BACK
}

# 1. Splash
sleep 3 && shoot 01-splash

# 2. Main menu (splash auto-advances)
sleep 3 && shoot 02-menu

# 3. Game screen (tap on the PLAY button)
nav_tap 540 2000
sleep 2 && shoot 03-game-idle

#4. After the main action (spin/play/tap)
nav_tap 540 2000
sleep 3 && shoot 04-game-action
sleep 3 && shoot 05-game-after-action

# 5. Back → menu
nav_back
sleep 1 && shoot 06-back-menu

#6. Additional screens (if not --quick)
#   Settings, Help, Paytable, Daily Bonus, Leaderboard, Profile
# Navigation by taps on the coordinates of menu buttons
# ...
```

**IMPORTANT**: if `--quick`, limit yourself to images 01–05.

After each screenshot, save the correspondence: what screen was expected vs what was captured.

### If all three methods produce an invalid PNG

1. Make sure that the device screen is **unlocked** (adb screencap on lock screen sometimes returns garbage).
2. Restart Flutter with Impeller disabled:
   ```bash
   flutter run -d "$DEVICE_ID" --no-enable-impeller > .claude/runtime-logs/flutter-run.log 2>&1 &
   ```
3. On Android 14+ it happens that `screencap` requires permission from `READ_FRAME_BUFFER` via
   `adb shell settings put global hidden_api_policy 1` - do it only in a personal dev environment.
4. Diagnostics: `file "$SHOT_DIR/*.INVALID"` - if `ASCII text` is there, an error has entered the pipe
   adb (unauthorized / offline / device not found).

---

## Phase 3 - Visual Analysis [~2 min]

**CRITICAL phase.** Here we use Read's ability to look at PNG as
image (multimodal vision).

For EACH screenshot, call the Read tool:

```
Read file_path=production/runtime-screenshots/<ts>/01-splash.png
```

And visually check using the checklist:

### Checklist of visual problems (Severity Scale)

| # | Problem | What does it look like | Severity | Responsible Agent |
|---|----------|--------------|----------|---------------------|
| V1 | **Flutter red screen of death** | Red background with exception and stacktrace text | CRITICAL | parsing logcat → mechanics-programmer or ui-programmer |
| V2 | **Completely black screen** | Entirely black or dark, no content | CRITICAL | ui-programmer(check onLoad, Scaffold, main.dart) |
| V3 | **Completely white screen** | All white, no content | CRITICAL | ui-programmer (usually Navigator stuck or missing route) |
| V4 | **Blank game screen** | There is a HUD, but the game area (reels/grid/field) is empty | CRITICAL | mechanics-programmer (components not added to World) |
| V5 | **RenderFlex overflow** | Yellow and black diagonal stripes on edges | HIGH | ui-programmer (Expanded/Flexible, Text overflow) |
| V6 | **Missing asset placeholder** | Gray rectangle with cross or empty SVG slot | HIGH | ui-programmer or generate-asset |
| V7 | **Overlapping UI** | Text/buttons overlap each other | HIGH | ui-programmer (layout constraints) |
| V8 | **Text overflow without ellipsis** | The text is cut off at the edge without the "..." | MEDIUM | ui-programmer |
| V9 | **Button invisible/off screen** | No visible action button in game_screen | HIGH | ui-programmer |
| V10 | **Low Contrast** | The text blends into the background, unreadable | MEDIUM | ui-programmer (Design DNA palette) |
| V11 | **All graphics are default Material** | Blue AppBar, white buttons, generic look | MEDIUM | ui-programmer (no custom theme) |
| V12 | **Balance/account not displayed** | HUD is empty or shows NaN/null | HIGH | mechanics-programmer (ValueNotifier not connected) |
| V13 | **Gameplay field is a thumbnail** | Live field occupies <55% of usable portrait area or is conspicuously narrow without a documented mechanic reason | HIGH | ui-programmer (full-viewport recomposition) |
| V14 | **Nested game window** | Field looks like a phone/browser/card inside the actual game screen, with large dead margins or a second unrelated panel | HIGH | ui-programmer (remove outer frame and integrate field/HUD/controls) |
| V15 | **Core loop below the fold** | Player must vertically scroll to see the primary action, stake/risk control, or essential result | HIGH | ui-programmer (fixed-viewport core composition) |
| V16 | **Poorly adjusted controls** | Buttons are cramped, uneven, clipped, undersized, ambiguously disabled, or visually disconnected from gameplay | HIGH | ui-programmer (responsive control deck and state pass) |
| V17 | **Non-phone layout or targeting** | A tablet/desktop/landscape branch appears, wide Web stretches/reflows the game, or portrait/iPhone-only configuration is missing | HIGH | ui-programmer + release-engineering (enforce mobile-phone contract) |

For every game-idle and active screenshot, also apply
`.claude/docs/mobile-phone-contract.md` and `.claude/docs/gameplay-screen-contract.md`.
V13–V17 are release blockers, not subjective polish. Run the screenshot tour across 360×640,
360×800, 390×844 and 430×932; do not add a tablet viewport.

### Create an entry for each screenshot

```markdown
### 03-game-idle.png
- Expected: full-viewport integrated game screen with a dominant field, compact HUD and a visible,
  properly sized primary action; no nested window and no core-loop scrolling
- Observed: [what is actually visible]
- Issues:
  - V4 - The reel area is empty (black rectangle 800x600 in the center)
  - V8 — Balance text is cut off: “100...” instead of “1000”
- Severity: CRITICAL
- Suspected cause: ReelComponent not added to world.onLoad() or SymbolComponent
  doesn't load SVG assets
- File to investigate: lib/game/[name]_world.dart
```

---

## Phase 4 - Logcat Analysis [~30 sec]

**Android**: Read both `logcat.log` and `flutter-run.log`.
**Chrome/web**: read `flutter-run.log` (compilation/VM errors) **and** `<SHOT_DIR>/webconsole.log`
+ `<SHOT_DIR>/manifest.json` → `consoleErrors[]` (runtime exceptions and console.error from the browser,
taken using CDP). Quick check: `jq '.consoleErrors' "$SHOT_DIR/manifest.json"`.
Retrieve all runtime-exceptions.

### Patterns for grep

```bash
# ── Gradle / NDK build errors (checked FIRST — these prevent the app from starting) ──
grep -B 2 -A 10 "FAILURE: Build failed" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5  "No toolchains found\|NDK.*not installed\|NDK.*not configured" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5  "Execution failed for task.*CompileDebug\|Execution failed for task.*Link" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5  "ndkVersion is not set\|Install NDK" .claude/runtime-logs/flutter-run.log

# If any Gradle/NDK error is found, apply the NDK auto-fix before continuing:
# python3 -c "
#   import re, pathlib
#   bg = pathlib.Path('android/app/build.gradle')
#   src = bg.read_text()
#   if 'ndkVersion' not in src:
#       src = src.replace('android {', 'android {\n    ndkVersion \"27.0.12077973\"', 1)
#   src = re.sub(r'minSdkVersion\s+\d+', 'minSdkVersion 21', src)
#   bg.write_text(src)
# "
# command -v sdkmanager &>/dev/null && sdkmanager "ndk;27.0.12077973" 2>/dev/null || true

# ── Flutter runtime exceptions ──
grep -A 20 "EXCEPTION CAUGHT" .claude/runtime-logs/flutter-run.log
grep -A 10 "Another exception was thrown" .claude/runtime-logs/flutter-run.log

# Layout errors
grep -B 2 -A 5 "A RenderFlex overflowed" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "unbounded height\|unbounded width" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "BoxConstraints forces an infinite" .claude/runtime-logs/flutter-run.log

# State lifecycle errors
grep -B 2 -A 5 "setState() called after dispose" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "called on a disposed" .claude/runtime-logs/flutter-run.log

# Asset errors
grep -B 2 -A 3 "Unable to load asset" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 3 "Could not find asset" .claude/runtime-logs/flutter-run.log

# Navigation errors
grep -B 2 -A 3 "Could not find a generator for route" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 3 "Navigator operation requested" .claude/runtime-logs/flutter-run.log

# Null/type errors
grep -B 2 -A 5 "Null check operator" .claude/runtime-logs/flutter-run.log
grep -B 2 -A 5 "type '.*' is not a subtype" .claude/runtime-logs/flutter-run.log

# Flame errors
grep -B 2 -A 5 "FlameGame\|PositionComponent" .claude/runtime-logs/flutter-run.log | grep -i "error\|exception"
```

### Error classification

Mark each caught error:
- **file:line** - where it happened (from stacktrace)
- **category** — layout / lifecycle / asset / navigation / null / flame / other
- **fix_owner** - who does the repairs (ui-programmer / mechanics-programmer / juice-artist)

---

## Phase 5 - Auto-Fix Loop [~5 min, up to 3 iterations]

Consolidate findings from Phase 3 (visual) and Phase 4 (logcat) into a single list of issues.
Sort by severity: CRITICAL → HIGH → MEDIUM.

### Correction strategy

1. **Stop the running application** (otherwise hot reload will create noise):
   ```bash
   kill $(cat .claude/runtime-logs/flutter.pid) 2>/dev/null
   kill $(cat .claude/runtime-logs/logcat.pid) 2>/dev/null
   ```

2. **Group problems by responsible agent.**

3. **Run agents in parallel** (each gets its own list):

   **ui-programmer**:
   - V2/V3 (black/white screen): check main.dart → runApp, app.dart → routes, SafeArea
   - V5/V7/V8/V9 (layout): add Expanded, overflow: ellipsis, FittedBox
   - V10/V11 (design): apply palette from Design DNA, replace Material defaults
   - V13/V14/V15/V16 (gameplay composition): apply `gameplay-screen-contract.md`; expand and
     integrate the field, remove nested framing/core scrolling, and rebuild the responsive control
     deck. If this needs a whole-screen recomposition, route it through `/ui-audit --fix`.

   **mechanics-programmer**:
   - V4 (blank game screen): check [name]_world.dart - onLoad adds components,
     components have the correct position/size, load assets
   - V12 (HUD not updated): check that ValueNotifiers are created in FlameGame and
     inserted into the HUD via GameWidget overlayBuilderMap

   **juice-artist** (if VFX is mentioned):
   - Particle systems are not visible: check that ParticleSystemComponent is added to World

   **ui-audit skill** (auxiliary):
   - If the logcat shows a lot of layout errors, run `/ui-audit --fix`

4. **After corrections**:
   ```bash
   dart analyze lib/
   flutter test
   ```
   If this breaks compilation or tests, roll back non-critical edits and leave only those
   that they fix CRITICAL/HIGH.

5. **Re-run cycle** (from Phase 1): restart the game, take screenshots, compare.
   If the number of CRITICAL problems has decreased, we continue. If there is no progress 2 iterations
   in a row - stop and report to the user.

### Phase 5 Exit Criteria

**Success**: 0 CRITICAL and 0 HIGH; MEDIUM are acceptable with a CONCERNS note.
**Partial success**: CRITICAL/HIGH eliminated but MEDIUM remained - report CONCERNS.
**Failure**: any CRITICAL/HIGH remained after 3 iterations - detailed report + manual escalation.

---

## Phase 6 - Report & Artifacts

Create `production/runtime-screenshots/<timestamp>/REPORT.md`:

```markdown
# Runtime Verification Report - [date]

## Device
- Platform: Android / iOS
- Device: [model / emulator name]
- Resolution: [WxH]
- Flutter: [version]

## Screens Tested
- [x] Splash → Menu transition
- [x] Main Menu
- [x] Game Screen (idle)
- [x] Game Screen (action in progress)
- [x] Game Screen (after action)
- [ ] Settings (--quick mode: skipped)
- ...

## Issues Found

### Initial run (iteration 1)
- CRITICAL (2):
  - V4 on 03-game-idle.png — reels area is black rectangle. Root cause: ReelComponent not
    added in SlotMachineWorld.onLoad(). Fixed by mechanics-programmer: lib/game/slot_world.dart
  - V2 on 01-splash.png — all-black splash. Root cause: splash_screen.dart did not wrap
    content in Scaffold. Fixed by ui-programmer.
- HIGH (1):
  - V5 on 02-menu.png — RenderFlex overflow bottom 42px. Fixed: wrapped ListView in Expanded.

### Final run (iteration 2) — VERIFIED
- CRITICAL: 0
- HIGH: 0
- MEDIUM: 1 (V11 — menu uses default AppBar color, consider theming)

## Logcat Summary
- Exceptions: 3 (iteration 1) → 0 (iteration 2)
- Warnings: 5 (acceptable)

## Screenshots
- production/runtime-screenshots/<ts>/01-splash.png
- ...

## Verdict
✅ PASS — game runs end-to-end without crashes, all CRITICAL/HIGH issues resolved.
```

Also update `production/session-state/active.md`:
```markdown
## Runtime verified
- Date: [date]
- Device: [device]
- Issues fixed: [N]
- Verdict: PASS / CONCERNS / FAIL
- Report: production/runtime-screenshots/<ts>/REPORT.md
```

---

## Phase 7 - Cleanup

```bash
# Stop the application
kill $(cat .claude/runtime-logs/flutter.pid) 2>/dev/null || true
kill $(cat .claude/runtime-logs/logcat.pid) 2>/dev/null || true

# Do NOT delete logs (may be needed for debugging)
# Do NOT delete screenshots (verification artifact)

# Optional: remove old wounds (keep the last 5)
ls -1t production/runtime-screenshots/ | tail -n +6 | xargs -I{} rm -rf "production/runtime-screenshots/{}"
```

---

## Integration in /autocreate

This skill automatically starts from `/autocreate` in **Phase 10.5** - immediately after
`Phase 10 Crash Prevention` and up to `Phase 11 Session State Update`.

`/autocreate` uses **`--quick`** mode (main screens only) to fit
in the time budget. If there are critical problems, the full mode starts.

---

## Quality Gates

| Phase | Exit Criteria | Max. iterations |
|------|----------------|---------------|
| 0.Preflight | Device available | 1 (aka abort) |
| 1.Build | `flutter run` does not crash, the application is running | 3 |
| 2. Screenshots | Minimum 5 pictures taken | 2 |
| 3. Visual Analysis | All images analyzed | 1 |
| 4. Logcat | Log read, errors classified | 1 |
| 5. Auto-Fix | 0 CRITICAL | 3 |
| 6.Report | REPORT.md created | 1 |
| 7. Cleanup | Processes stopped | 1 |

---

## Prohibited in this skill

1. Change `pubspec.yaml` dependencies during auto-fix (this is the task of the main pipeline)
2. Launch the emulator with `-wipe-data` - the user may lose the state of other applications
3. Using `adb root` or `adb shell su` is unnecessary and unsafe
4. Delete screenshots or logs before the end of the report
5. Do git commit automatically - only the user decides

---

## Arguments

- `--device <id>` - specific `flutter devices` ID (default: Chrome auto-select)
- `--platform web|android|ios` - force the platform.
  - **Default: `web`** - headless `web-server` + CDP (`tools/web_verify.mjs`), no emulator/display needed
  - `android` - ADB + `flutter screenshot`, requires a running device/emulator
- `--no-fix` - analysis and report only, no corrections
- `--quick` - shortened tour (splash → menu → game → action). Forwarded to `web_verify.mjs --quick`.
- `--skip-logcat` - skip logcat parsing (for web logcat is not needed - everything is in webconsole.log/flutter-run.log)
- `--no-impeller` - launch `flutter run` from `--no-enable-impeller` (Android only).
  Use if the first pass yielded `.INVALID` PNG.
