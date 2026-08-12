---
name: autocreate-finalize
description: "Session 3 of the /autocreate pipeline (Phases 10.5 → 10.6 → 11 → 11.5 → 12): runtime + soak verification (Chrome CDP, auto-fix), playtest (a real gameplay session, P1–P10), session state, release-engineering PREP (icons/splash/version/store-metadata/CI — WITHOUT building the AAB/APK and without a keystore) and the final report. Leaves the project release-ready. It does NOT build artifacts and does NOT call /release-package — that is an explicit user action. Started automatically through the Agent tool at the end of Session 2 (autocreate-implement), or manually in a new conversation."
argument-hint: "[--skip-emulator | --no-fix]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Finalize — Session 3 of the pipeline

**Purpose**: finish `/autocreate` after Session 2 (`autocreate-implement`) has brought the
project to `dart analyze` 0 errors + `flutter test` green. In this session:
- runtime verification: Chrome/CDP (screenshots + console + auto-fix) plus a soak probe for leaks;
  Android (`--platform android`) is a Gradle compile-only check, with no emulator and no APK
- **playtest** (Phase 10.6): a real gameplay session — the P1–P10 checks from
  `.claude/skills/playtest/SKILL.md` (numbers change, win/lose paths, a living board, progression)
- updating the session state + the final report
- **release-engineering PREP** (`/release-engineering --prep-only --no-keystore`): icons, native
  splash, versioning, store metadata, CI — **WITHOUT building the AAB/APK and without a keystore**

**Building the artifacts is NOT part of this skill.** The AAB/APK and the archive are built by
`/release-package` (an explicit run). For a signed AAB for Google Play, use
`/release-engineering` with no flags (it mints the upload keystore — an explicit user action).

**When it is called:**
- Automatically: Session 2 (`autocreate-implement`) calls the Agent tool at the end of Phase 10.7
  with a prepared prompt (a full-history fork, no subagent_type)
- Manually: the user runs `/autocreate-finalize` in a **new** conversation, if the sub-agent
  crashed, or to repeat the runtime check after edits

**What it does NOT do:**
- It does NOT rewrite the game code, change the GDD or change the balance
- It does NOT create new screens
- It does NOT run Phases 1–10 — Session 2 already did those

---

## 🚨 MANDATORY CONTRACT

1. ✅ Reads `production/session-state/autocreate-handoff.md` **as its first action**
2. ✅ Validates that Session 2's artifacts exist (`pubspec.yaml`, `lib/main.dart`,
   `dart analyze` still 0 errors)
3. ✅ Reads `.claude/docs/gameplay-screen-contract.md` before runtime capture and treats every
   V13–V16 defect as a HIGH release blocker
4. ✅ Runs Phases 10.5 → 11 → 11.5 → 12 in that order
5. ✅ Returns the final report to the parent session (or prints it for the user)

**Forbidden:**
- ❌ Changing `lib/game/game_config.dart`, `design/balance/*.json` or `assets/data/*.json` —
  the balance and content are frozen
- ❌ Rewriting whole screens — only targeted runtime auto-fixes are allowed
  (overflow, setState after dispose, a missing asset path, a null ValueNotifier)
- ❌ Generating a release upload keystore — Phase 11.5 runs ONLY with `--no-keystore`;
  a signed AAB is the user's explicit `/release-engineering`
- ❌ Calling `/release-package` — packaging is a separate, explicit run

---

## Phase 0 — preflight & handoff read [~30 s]

```bash
# 1. The handoff must exist
test -f production/session-state/autocreate-handoff.md || {
  echo "❌ No handoff file. Did Session 2 (autocreate-implement) not finish?"
  exit 1
}

# 2. The project must compile
dart analyze lib/ > /tmp/finalize_preflight_analyze.log 2>&1
if grep -q " error " /tmp/finalize_preflight_analyze.log; then
  echo "❌ dart analyze lib/ reports errors — Session 2 did not finish its work correctly"
  exit 1
fi

# 3. The tests must be green
flutter test > /tmp/finalize_preflight_test.log 2>&1 || {
  echo "⚠️ flutter test is red. We continue, but this is worth fixing."
}
```

Read the handoff file and extract:
- The game's name → for the archive's name
- The category (C1–C6) and the math model (M1–M6) → for the final report
- The path to the main game class → for emulator-test navigation

---

## Phase 10.5 — runtime emulator verification [~8 min]

Call the `/emulator-test --quick` skill (see `.claude/skills/emulator-test/SKILL.md`).

### 10.5.1 — preflight (web-first, headless, no display)

> **The default is headless web** through `flutter run -d web-server` + headless Chrome over CDP
> (`tools/web_verify.mjs`). That needs no emulator, no KVM, no graphical display and no
> `xdotool`/`osascript`. Android (`--platform android`) is an explicit request, and it **does not
> start an emulator/AVD**: it is a pure **Gradle compile-only verification**
> (`flutter build apk --debug`; the APK is neither kept nor packaged), with no runtime tour, no
> screenshots and no `adb logcat`. That removes the two main causes of Phase 10.5 hanging:
> "I cannot open/click Chrome" and "I cannot start an AVD/KVM in a headless environment".

```bash
# What the web path needs: node (for the CDP driver) + a Chrome binary (for headless shots).
HAVE_NODE=0; command -v node >/dev/null 2>&1 && HAVE_NODE=1
CHROME_BIN="${CHROME_EXECUTABLE:-}"
for c in google-chrome google-chrome-stable chromium chromium-browser; do
  [ -z "$CHROME_BIN" ] && command -v "$c" >/dev/null 2>&1 && CHROME_BIN="$(command -v "$c")"
done
export CHROME_EXECUTABLE="$CHROME_BIN"

if [[ "${AUTOCREATE_SKIP_EMULATOR:-0}" == "1" ]]; then
  echo "⏭️ AUTOCREATE_SKIP_EMULATOR=1 — Phase 10.5 SKIPPED on request."
  export SKIP_SCREENSHOTS=1
elif [[ "${PLATFORM:-web}" == "android" ]]; then
  # An explicit Android request (--platform android). We do NOT start an emulator/AVD/KVM —
  # this is only a compile verification of the Gradle build; see 10.5.2c.
  echo "🤖 PLATFORM=android → Gradle compile-only verification (no emulator, no screenshots)."
fi

# The web path (the default): needs node + Chrome. Without them, the only honest answer is SKIP.
if [[ "${SKIP_SCREENSHOTS:-0}" != "1" && "${PLATFORM:-web}" == "web" ]]; then
  if [[ $HAVE_NODE -eq 1 && -n "$CHROME_BIN" ]]; then
    echo "🌐 Web path: node=$(node -v) chrome=$CHROME_BIN"; export PLATFORM=web
  else
    echo "⚠️ No node ($HAVE_NODE) or Chrome ('$CHROME_BIN') — web verification is impossible. SKIPPED."
    export SKIP_SCREENSHOTS=1
  fi
fi

# NDK pre-flight — ONLY for the Android compile-only verification (web does not build Gradle).
if [[ "${PLATFORM:-web}" == "android" ]]; then
  command -v sdkmanager &>/dev/null && { sdkmanager --list_installed 2>/dev/null | grep -q "ndk;27" || \
    sdkmanager "ndk;27.0.12077973" 2>/dev/null || echo "⚠️ NDK install failed"; }
  if [[ -f android/app/build.gradle ]] && ! grep -q "ndkVersion" android/app/build.gradle; then
    python3 - <<'PY'
import re, pathlib
bg = pathlib.Path("android/app/build.gradle"); src = bg.read_text()
src = src.replace("android {", 'android {\n    ndkVersion "27.0.12077973"', 1)
src = re.sub(r'minSdkVersion\s+\d+', 'minSdkVersion 21', src); bg.write_text(src)
print("✅ Patched build.gradle: ndkVersion + minSdkVersion 21")
PY
  fi
fi
```

**The transition criterion:**
- If `SKIP_SCREENSHOTS=1` (an explicit opt-out, or no node/Chrome for web) —
  **do NOT run** 10.5.2; go straight to Phase 11 with the verdict **SKIPPED**. That is a normal
  path, NOT an error: the pipeline counts as successful (the game was already built and tested in
  Session 2).
- Otherwise (`PLATFORM=web` with node+Chrome, or `PLATFORM=android` — no device or emulator is
  needed for the latter, it is compile-only) — continue with 10.5.2.

### 10.5.2 — runtime tour / compile verification (only when NOT SKIP_SCREENSHOTS)

**The web path (the default)** — self-contained commands (details in `emulator-test/SKILL.md`):

```bash
mkdir -p .claude/runtime-logs
WEB_PORT=8099

# 1) A headless dev server (it does not open a browser)
nohup flutter run -d web-server --web-port "$WEB_PORT" --web-hostname 127.0.0.1 \
  > .claude/runtime-logs/flutter-run.log 2>&1 &
echo $! > .claude/runtime-logs/flutter.pid

# 2) Wait for the URL, with an early exit on a build error (so it cannot hang)
WEB_URL=""
for i in $(seq 1 120); do
  WEB_URL=$(grep -oE "http://127\.0\.0\.1:[0-9]+" .claude/runtime-logs/flutter-run.log 2>/dev/null | head -1)
  [ -n "$WEB_URL" ] && break
  grep -qE "Failed to compile|Target dart2js failed|Compilation failed|^Error: " .claude/runtime-logs/flutter-run.log 2>/dev/null && break
  sleep 2
done

TS=$(date +%Y%m%d-%H%M%S); SHOT_DIR="production/runtime-screenshots/$TS"; mkdir -p "$SHOT_DIR"

if [ -n "$WEB_URL" ]; then
  # 3) The WHOLE screen tour + shots + console/exceptions in one self-terminating call.
  #    The outer timeout is a backstop over the internal --budget.
  timeout 220 node tools/web_verify.mjs --url "$WEB_URL" --out "$SHOT_DIR" --budget 180 --quick \
    2>&1 | tee "$SHOT_DIR/web_verify.log"
else
  echo "❌ the web server did not come up — the build is broken. Log: .claude/runtime-logs/flutter-run.log" \
    | tee "$SHOT_DIR/web_verify.log"
fi

# 4) Server cleanup (the script kills its own headless Chrome)
kill "$(cat .claude/runtime-logs/flutter.pid 2>/dev/null)" 2>/dev/null || true
```

Then:
- **Visual analysis** of each `$SHOT_DIR/*.png` through Read (vision) against the V1–V16 checklist
  and `.claude/docs/gameplay-screen-contract.md`. Inspect idle and active gameplay at 390×844 and
  add a 430×932 capture when the tour does not already include one.
- **Error parsing**: `jq '.consoleErrors' "$SHOT_DIR/manifest.json"`, `$SHOT_DIR/webconsole.log`,
  and `.claude/runtime-logs/flutter-run.log` (EXCEPTION CAUGHT, RenderFlex overflowed, Unable to load asset).

### 10.5.2c — Android compile verification (only when `PLATFORM=android`)

Android here is **NOT** a runtime tour. No emulator/AVD, no screenshots, no `adb logcat`. The
only goal is to confirm that the Gradle project really compiles (including that the NDK/minSdk
patches from 10.5.1 worked). Full runtime verification of the game already happens through web
(Chrome/CDP) above; the Android path answers only "does it compile", not "does it work on a
device" — and for that you need no emulator, KVM or hardware.

```bash
mkdir -p .claude/runtime-logs
timeout 600 flutter build apk --debug 2>&1 | tee .claude/runtime-logs/android-build.log
ANDROID_BUILD_EXIT=${PIPESTATUS[0]}

if [[ "$ANDROID_BUILD_EXIT" == "0" ]]; then
  echo "✅ Android Gradle compile OK — the app builds."
else
  echo "❌ Android Gradle compile FAILED — see .claude/runtime-logs/android-build.log"
fi

# This is a verification, not a release artifact — the APK is not kept or packaged.
rm -f build/app/outputs/flutter-apk/app-debug.apk 2>/dev/null || true
```

Compile errors (Gradle/Kotlin/NDK/platform Dart code) are handled the same way as the
`dart analyze` errors in Phase 6 of `autocreate-implement`: routed to
mechanics-programmer/ui-programmer, with up to 2 iterations of editing and re-running
`flutter build apk --debug`. Packaging (`flutter build apk --release`, the AAB, signing,
archiving) is not part of this — that is a separate, explicit `/release-package` on request.

### 10.5.2b — soak / leak probe (web, optional but recommended)

A complete game must survive a long session without memory growth or exceptions. If the web path
is active, run a short soak: ~150–200 automated actions (repeating the main game action plus
screen transitions) and compare the heap at the start and the end, plus the accumulation of
console errors.

```bash
# web_verify.mjs --soak N runs N action→wait cycles and records heapUsedStart/End
# (if the flag is not supported in the current version, skip it — this is not a blocker).
timeout 180 node tools/web_verify.mjs --url "$WEB_URL" --out "$SHOT_DIR" --soak 150 \
  2>&1 | tee -a "$SHOT_DIR/web_verify.log" || echo "soak skipped"
```

The sign of a leak: monotonic growth in `JSHeapUsedSize` with no plateau after GC, or a growing
number of repeated console exceptions. Whatever is found goes into REPORT.md as HIGH (not
CRITICAL, if the game is playable); a targeted fix (an un-disposed controller/timer/particle
leak) is permitted.

### 10.5.3 — the auto-fix loop (up to 3 iterations)

Consolidate the problems, mark their severity (CRITICAL/HIGH/MEDIUM) and assign agents:
- V2/V3/V5/V7/V8/V9/V10/V11/V13/V14/V15/V16 → **ui-programmer**
- V4/V12 → **mechanics-programmer**
- VFX not visible → **juice-artist**
- Logcat asset errors → check `lib/assets.dart` against the real files

**Permitted auto-fixes:**

| Symptom | Cause | Auto-fix |
|---------|-------|----------|
| An empty black rectangle instead of the play field | The components were not added in World.onLoad() | `await world.addAll([...])` |
| The HUD shows null/NaN | The ValueNotifier was never initialised | Initialise it in the Game constructor |
| The splash is black and never advances | There is no Timer for navigation | `Future.delayed → pushReplacementNamed` |
| A white screen after PLAY | The route is not registered | Add it to the `routes:` map in app.dart |
| Yellow overflow stripes | A ListView with no Expanded | Wrap it in Expanded |
| A red screen exception | A null check/type error from the stack trace | Fix it at the file:line from the log |
| "Unable to load asset" | A path mismatch in `lib/assets.dart` | Fix the path, or create the file |
| Slight field/control constraint miss | An avoidable wrapper, padding, or incorrect flex | Make a targeted constraint edit and re-capture both idle and active states |

**Forbidden "auto-fixes":**
- Changing `game_config.dart` (the balance is frozen)
- Changing `rtp-config.json` / `level-config.json`
- Rewriting whole screens — targeted edits only
- Changing the GDD

If V13–V16 require structural recomposition rather than a targeted constraint edit, do not hide
or downgrade the defect. Mark finalization FAIL and route it back to `/ui-audit --fix` or
`/autocreate-implement --resume`; Session 2 owns whole-screen composition.

### 10.5.4 — Phase 10.5's exit criterion

**The web path (the default):**
- **Success**: 0 CRITICAL + 0 HIGH visual problems, 0 FATAL exceptions, and the gameplay-screen
  contract passes in idle and active states
- **Partial success**: CRITICAL/HIGH are cleared but MEDIUMs remain — go on to Phase 11 with CONCERNS
- **Failure**: after 3 iterations any CRITICAL/HIGH remains — save
  `production/runtime-screenshots/<ts>/REPORT.md`, report with the verdict FAIL;
  Phase 11 runs anyway (active.md is updated with the FAIL verdict)

**The Android path (`PLATFORM=android`, compile-only):**
- **Success**: `flutter build apk --debug` finishes with exit code 0 (`ANDROID_BUILD_EXIT=0`)
- **Failure**: after 2 auto-fix iterations the compile errors remain — the verdict is FAIL, with
  the reason from `.claude/runtime-logs/android-build.log`; Phase 11 runs anyway
- There is no notion of CRITICAL/MEDIUM visual problems here — this is not a runtime tour

### 10.5.5 — artifacts

**The web path:**
- `production/runtime-screenshots/<ts>/*.png` — the shots
- `production/runtime-screenshots/<ts>/REPORT.md` — the verdict PASS/CONCERNS/FAIL
- `.claude/runtime-logs/flutter-run.log`

**The Android path (compile-only):**
- `.claude/runtime-logs/android-build.log` — the `flutter build apk --debug` log
- No screenshots/logcat/APK files — this verification saves nothing as an artifact

Cleanup: stop `flutter run` using the PID in `.claude/runtime-logs/*.pid` (the web path).

---

## Phase 10.6 — playtest (a real gameplay session) [~6 min]

> Phase 10.5 checked that "the screens open and do not crash". This phase checks that "it is
> actually PLAYABLE": actions produce results, numbers change, wins are celebrated, the board
> is alive. The benchmark is `.claude/docs/quality-bar.md` (§2–§4, §6, §7).

Run the `.claude/skills/playtest/SKILL.md` runbook (if the web path was SKIPPED in 10.5, or if
10.5 went down the Android compile-only path, this phase is honestly SKIPPED too — that is not an
error: playtest needs a genuinely running instance over CDP, and compile-only launches nothing):

- The tour + gameplay load (`web_verify.mjs --soak 60`) → the **P1–P10** checks
  (vision comparison of frames: the action changes the field, the HUD numbers change, win
  feedback is visible, the idle animation exists; manifest: 0 consoleErrors, suspectLeak=false).
- Verdict: **PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED** →
  `production/playtest/<ts>/PLAYTEST-REPORT.md`.
- On a CRITICAL (P1/P2/P8), run an auto-fix loop of up to 2 iterations against the same table of
  permitted fixes as in 10.5.3 (targeted wiring edits only; NOT balance, NOT rewriting screens).

**Exit criterion:** PLAYTEST-REPORT.md exists; the verdict is ≠ NOT-PLAYABLE (or the 2 iterations
are exhausted — then the verdict is recorded honestly and reaches the final report as the FAIL
reason).

---

## Phase 11 — session state update [~1 min]

Update `production/session-state/active.md`:

```markdown
<!-- STATUS -->
Epic: [Game Name]
Feature: Complete Game
Task: Production-ready
<!-- /STATUS -->

## Status
[If runtime/playtest/layout pass: The game is fully implemented and verified. To get the APK and
the archive, run /release-package.]
[If any CRITICAL/HIGH or NOT-PLAYABLE remains: RELEASE BLOCKED. Return to /ui-audit --fix or
/autocreate-implement --resume; do not run /release-package yet.]

## Runtime verification
- Verdict: [PASS / CONCERNS / FAIL / SKIPPED]
- Screenshots: production/runtime-screenshots/<ts>/
- Report: production/runtime-screenshots/<ts>/REPORT.md

## Session 2's tests
- Unit: [N] green
- Integration: [N] green
- Edge cases: [N] green

## Balance
[The math model run's verdict from Session 2: the model, the metric, PASS/CONCERNS/FAIL]
```

Also mark the handoff file as finished: append a final
`## Session 3 finished` section to `production/session-state/autocreate-handoff.md`, with an
ISO timestamp and the verdict.

---

## Phase 11.5 — release engineering prep (NO build) [~3 min]

Run `/release-engineering --prep-only --no-keystore`
(see `.claude/skills/release-engineering/SKILL.md`). **The AAB/APK build does NOT happen here** —
the goal is to leave the project READY for `/release-package` without spending time on a heavy
Gradle build:
- App icons (Android adaptive + iOS + web) and a native splash from the Design DNA.
- The version/build number and the launcher label.
- `store/` — the listing stubs, privacy policy, data safety, age rating (gambling — the disclaimer).
- `.github/workflows/build.yml` (CI).
- It does **NOT** generate an upload keystore and does **NOT** build the AAB/APK.

```bash
# A safe prep: it creates no keystore, publishes nothing externally and builds no artifacts.
flutter pub get >/dev/null 2>&1 || true
# If release-engineering is unavailable as a skill, do only the prep steps by hand:
#   dart run flutter_launcher_icons ; dart run flutter_native_splash:create
#   (do NOT run flutter build appbundle/apk here — that is /release-package's job)
```

> If the source icon `assets/branding/app_icon.png` is missing, generate it from the branded
> logo/sprite (rasterise the SVG at 1024×1024) before running launcher_icons.

**Exit criterion:** the icons and splash are generated and `store/` exists. The artifacts
(AAB/APK) are NOT built — `/release-package` builds those. For a signed Play AAB, the user runs
`/release-engineering` (with no flags), which mints the keystore and builds the signed AAB.

---

## Phase 12 — the final report

Print to the user (or, when invoked as a sub-agent, return it to the parent session). Use
`AUTOCREATE COMPLETE — PRODUCTION READY` only when runtime has 0 CRITICAL/HIGH issues, the
gameplay-screen contract passes, and playtest is not NOT-PLAYABLE. Otherwise use
`AUTOCREATE BLOCKED — UI/GAMEPLAY REWORK REQUIRED` and put the blocking rerun command first.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 AUTOCREATE COMPLETE — PRODUCTION READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Screens (12+):
   ✅ Splash, Main Menu, Game Screen + HUD
   ✅ Paytable, Settings, Help, Daily Bonus
   ✅ Leaderboard, Profile, Win Overlays (3 tiers)
   ✅ Insufficient Funds, Bonus Mode Overlay

🎮 Gameplay:
   ✅ Core game loop works end-to-end
   ✅ [Category]: [RNG / outcome resolver / cash-out / pity / physics] fully functional
   ✅ Stateless Outcomes, GameState sealed class
   ✅ All constants in GameConfig, double-click protection

🗂 Content and modes (Phase 4.5):
   ✅ [N] levels/stages (assets/data/*.json) | Modes: [Classic + Endless/Time-Attack/Daily]
   ✅ Level/Mode Select is wired to the real data

🧩 Meta systems (Agent E):
   ✅ SaveService (versioned), Economy (currency + shop), Progression (stars), Achievements
   ✅ Analytics/Ads/IAP/RemoteConfig — abstractions (no-op, no external SDKs)
   [Gambling: age gate + 18+ disclaimer + responsible play]

🔊 Audio (Phase 3.5):
   ✅ 8 real .wav sound effects synthesised (mood: [mood]) — not placeholders
   ℹ️ No background music by design (SFX-only); not a gap, do not list it as one

🧪 Tests (Session 2):
   ✅ Unit: [N] passed | Integration: [N] passed | Edge: [N] passed

🌐 Runtime verification (Chrome, Phase 10.5):
   [PASS / CONCERNS / FAIL / SKIPPED] — [N] CRITICAL, [N] HIGH issues
   Gameplay composition: [PASS / FAIL / UNVERIFIED] — full-viewport field + integrated controls
   Screenshots: production/runtime-screenshots/<ts>/
   Report: production/runtime-screenshots/<ts>/REPORT.md

🕹 Playtest (Phase 10.6 — a real gameplay session):
   [PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED]
   P1–P10: [briefly — e.g. "P1–P8 PASS, P9 leak-suspect, P10 PASS"]
   Report: production/playtest/<ts>/PLAYTEST-REPORT.md

⚖️ Balance (Session 2):
   [Gambling: RTP XX.X% (target 95-97%)]
   [Math model M1–M6: the metric is inside its window, the report is in design/balance/simulation-report.md]

🚀 Release-ready (Phase 11.5, PREP — no build):
   ✅ Icons (Android adaptive + iOS + web) + a native splash (colour from the DNA)
   ✅ Version [name]+[build], store/ (listing + privacy + data-safety + age-rating)
   ⚙️ .github/workflows/build.yml (CI)
   ℹ️ The AAB/APK were NOT built — the project is ready to be packaged

📦 Building artifacts / publishing (an explicit user action):
   /release-package                 — build the AAB+APK + screenshots + sources → one .zip
   /release-engineering             — mint the upload keystore → a SIGNED .aab for Google Play

🔧 Commands to run it:
   flutter run -d chrome        — run in Chrome
   flutter run                  — run on an available device
   flutter test                 — run the tests
   adb install project_zip/[name]-[ts]/apk/*.apk — install the APK (if there is one)

📋 Recommended re-runs:
   /emulator-test               — REPEAT the runtime verification
   /release-package             — REPEAT the release packaging
   /autocreate-finalize         — re-run the whole of Session 3

📋 Optional next steps:
   /add-feature [feature]       — add a mechanic
   /code-review                 — a full code review
   /balance-check               — a detailed balance check (1M iterations)
   /perf-profile                — performance profiling
   /release-checklist           — the final GO/NO-GO checklist before a store release
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quality gates

| Phase | Exit criterion | Max iterations |
|-------|----------------|----------------|
| 0. Preflight | The handoff exists + `dart analyze` 0 errors | 1 (fail-fast) |
| 10.5. Runtime Chrome / Android compile | Web: 0 CRITICAL/HIGH visual, gameplay-screen contract PASS, 0 FATAL in flutter-run.log (+ soak: no leak). Android (`--platform android`): `flutter build apk --debug` exit 0 | 3 (Chrome is always available) / 2 (Android compile) |
| 10.6. Playtest | PLAYTEST-REPORT.md, verdict ≠ NOT-PLAYABLE (P1–P10) | 2 |
| 11. Session state | `active.md` updated | 1 |
| 11.5. Release-eng prep | Icons/splash generated, `store/` created (AAB best-effort) | 1 |
| 12. Final report | The report was printed / returned | 1 |

**THE ABSOLUTE MINIMUM to finish Session 3:**
- `production/session-state/active.md` is updated
- The final report is printed, with the runtime verification verdict

This minimum permits an honest blocked report; it does not permit a production-ready claim. Any
remaining V13–V16/HIGH defect or a failed gameplay-screen contract keeps the project blocked.

---

## Recovery after a failure

**If the sub-agent crashed mid-Session 3**, the user runs `/autocreate-finalize` in a new
conversation. The skill:
1. Reads `autocreate-handoff.md` and `active.md`
2. Works out which phase to continue from (by which artifacts exist):
   - No `production/runtime-screenshots/<ts>/` and no `.claude/runtime-logs/android-build.log` → start at 10.5
   - There are shots (or, on the Android path, an `android-build.log` with exit 0) but no
     `production/playtest/<ts>/PLAYTEST-REPORT.md` → start at 10.6 (on the Android path this step
     is honestly SKIPPED — go straight to 11)
   - There is a playtest report (or the Android path reached the SKIPPED playtest) but `active.md`
     has not been updated → start at 11
3. Continues from that phase without redoing what is done

**If web verification is impossible** (no `node` or no Chrome binary): `web_verify.mjs` cannot
run — Phase 10.5 is SKIPPED as normal and we go to Phase 11 with the verdict SKIPPED (the game
was already built and tested in Session 2). To enable web verification: install `node` (≥21, for
the built-in WebSocket) and Chrome/Chromium (`google-chrome`/`chromium`), or point
`$CHROME_EXECUTABLE` at the binary. This does NOT block Session 3 from finishing.

**If it hangs on Phase 10.5** — it should not: `web_verify.mjs` terminates itself on `--budget`,
there is a `timeout` on top of it, and `flutter run -d web-server` exits early on a build error.
If it does hang anyway, kill `$(cat .claude/runtime-logs/flutter.pid)` and any orphaned
`google-chrome --headless` processes, mark the verdict SKIPPED and move to Phase 11.
Note `CHROME_SKIPPED: true` in `RELEASE_INFO.md`.
