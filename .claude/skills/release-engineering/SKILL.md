---
name: release-engineering
description: "Ship engineering for a finished game: app icon generation (all densities + adaptive + iOS), a native splash, versioning, a signed Android App Bundle (.aab — the Google Play format), an iOS archive scaffold, build flavors, obfuscation, a CI workflow and store metadata templates. Turns a built project into a GENUINELY publishable artifact. Runs from /autocreate-finalize ahead of /release-package, or manually."
argument-hint: "[--prep-only | --no-keystore | --aab-only | --with-ci]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

# Release Engineering — from "it builds" to "it ships"

`/release-package` packs the sources + screenshots + a **debug-signed APK**. That is not enough
to publish: Google Play accepts a **signed `.aab`**, and you need icons at every density, a
native splash, a version/build number and the listing metadata. This skill closes that gap.

> **The safety principle:** it publishes nothing externally, never overwrites an existing
> keystore, and never commits secrets. The keystore and passwords go into a **gitignored**
> `key.properties`. Destructive steps (generating a key) run only when none exists, and they log
> explicitly where the key was put.

> **`--prep-only`** (used by `/autocreate-finalize`): do ONLY the preparation —
> phases 1 (icons/splash), 2 (versioning), 4 (iOS scaffold), 5 (store metadata), 6 (CI).
> **Skip phase 3 entirely** (no keystore and no AAB/APK build). The project becomes
> release-ready, and the artifacts themselves are built later by `/release-package` or a full
> `/release-engineering`.

---

## Phase 0 — preflight [~20 s]

```bash
test -f pubspec.yaml || { echo "❌ Not a Flutter project (no pubspec.yaml)"; exit 1; }
dart analyze lib/ > /tmp/relng_analyze.log 2>&1
grep -q " error " /tmp/relng_analyze.log && { echo "❌ dart analyze: errors. Fix them first."; exit 1; }
flutter --version | head -1
APP_NAME=$(grep -m1 '^name:' pubspec.yaml | awk '{print $2}')
echo "Project: $APP_NAME"
```

Read from the concept (`design/gdd/game-concept.md`): the human-readable game title (for the
launcher label and the listing), the splash background colour (from the Design DNA → Background),
the category C1–C6 and the compliance profile (for the metadata and the age rating).

---

## Phase 1 — app icon & native splash [~2 min]

### 1.1 — Prepare the source icon (1024×1024 PNG)
The icon MUST be raster 1024×1024 with no alpha channel for iOS. Sources, in order:
1. **If `/store-screenshots` has already run** — `assets/branding/app_icon.png` and
   `assets/branding/app_icon_fg.png` are already assembled by it (and most likely already
   applied). Take them as they are and regenerate nothing.
2. If there is a suitable PNG logo in `assets/`, use it.
3. Otherwise generate the icon art (Codex: GPT Images 2.0 → GPT Images/default fallback),
   or rasterise `assets/images/ui/ui_app_icon.svg`
   (`rsvg-convert`/`inkscape`/`magick -density 384`), then assemble the set in one call:
   ```bash
   python3 tools/store_compose.py icon --src <art>.png [--fg-src <emblem with alpha>.png] \
     --out-dir assets/branding --bg "[DNA Background]"
   ```
   That produces `app_icon.png` (1024, no alpha), `app_icon_fg.png` (an adaptive foreground
   inside the safe zone) and `store_icon_512.png` (the Play listing icon).
4. Android's adaptive icon needs a foreground with a transparent background — if
   `app_icon_fg.png` was not created, remove BOTH `adaptive_icon_*` lines from the config below,
   or Android will crop the artwork.

```bash
mkdir -p assets/branding
# (the agent picks whichever converter is available; the end result is assets/branding/app_icon.png 1024x1024)
test -f assets/branding/app_icon.png || echo "⚠️ no app_icon.png — generate it before continuing"
```

### 1.2 — flutter_launcher_icons
Add it to `dev_dependencies` and configure it:

```yaml
dev_dependencies:
  flutter_launcher_icons: ^0.14.1

flutter_launcher_icons:
  image_path: "assets/branding/app_icon.png"
  android: true
  ios: true
  remove_alpha_ios: true
  web: { generate: true }
  adaptive_icon_background: "#0E1116"   # ← from the Design DNA (Background)
  adaptive_icon_foreground: "assets/branding/app_icon_fg.png"
```

```bash
flutter pub get
dart run flutter_launcher_icons 2>&1 | tail -5
```

### 1.3 — flutter_native_splash
```yaml
dev_dependencies:
  flutter_native_splash: ^2.4.1

flutter_native_splash:
  color: "#0E1116"                       # ← from the Design DNA
  image: "assets/branding/splash_logo.png"   # a mono logo, centred (optional)
  android_12: { color: "#0E1116", image: "assets/branding/splash_logo.png" }
  fullscreen: true
```

```bash
dart run flutter_native_splash:create 2>&1 | tail -5
```

> The splash colour comes from the Design DNA, NOT a default white/black. It is the game's first frame.

---

## Phase 2 — versioning & app identity [~30 s]

```bash
# version: <semver>+<buildNumber>. The build number increases monotonically.
python3 - <<'PY'
import re, pathlib, time
p = pathlib.Path("pubspec.yaml"); s = p.read_text()
m = re.search(r'^version:\s*([0-9]+\.[0-9]+\.[0-9]+)\+([0-9]+)', s, re.M)
if m:
    name, build = m.group(1), int(m.group(2)) + 1
else:
    name, build = "1.0.0", 1
s = re.sub(r'^version:.*$', f'version: {name}+{build}', s, count=1, flags=re.M)
p.write_text(s)
print(f"✅ version: {name}+{build}")
PY
```

The launcher label (the human-readable name) is set in
`android/app/src/main/AndroidManifest.xml` (`android:label`) and `ios/Runner/Info.plist`
(`CFBundleDisplayName`) from the title in the concept — in English, unless the user explicitly
asked for the game in another language.
Application ID / bundle id: `com.gamestudio.<name>` (already set by `flutter create --org`).

---

## Phase 3 — Android signing & App Bundle [~5 min]

**SKIP THE WHOLE OF PHASE 3 when `--prep-only`** — no keystore and no AAB/APK build.
`/release-package` builds the artifacts. (That is how `/autocreate-finalize` calls this phase.)

**Skip only the signing (3.1–3.2) when** `--no-keystore` (the AAB is then debug-signed — it
builds, but Play will not accept it; fine for internal testing).

### 3.1 — The upload keystore (only if there is none yet)
```bash
KS=android/keystore/upload-keystore.jks
if [[ -f "$KS" ]]; then
  echo "✅ keystore already exists: $KS (not overwriting)"
elif [[ "${RELNG_NO_KEYSTORE:-0}" == "1" ]]; then
  echo "⏭️ --no-keystore: skipping key generation"
else
  mkdir -p android/keystore
  STOREPASS=$(openssl rand -base64 18 | tr -d '/+=' | head -c 24)
  keytool -genkey -v -keystore "$KS" -keyalg RSA -keysize 2048 -validity 10000 \
    -alias upload -storepass "$STOREPASS" -keypass "$STOREPASS" \
    -dname "CN=Game Studio, OU=Games, O=GameStudio, L=NA, S=NA, C=US" 2>/dev/null
  cat > android/key.properties <<EOF
storePassword=$STOREPASS
keyPassword=$STOREPASS
keyAlias=upload
storeFile=keystore/upload-keystore.jks
EOF
  echo "✅ keystore + key.properties created."
  echo "🔐 IMPORTANT: keep android/keystore/upload-keystore.jks and android/key.properties"
  echo "    somewhere safe. Losing the key means you can never update the app on Google Play."
fi

# gitignore the secrets (idempotent)
grep -qxF 'android/key.properties'       .gitignore 2>/dev/null || echo 'android/key.properties'       >> .gitignore
grep -qxF 'android/keystore/'            .gitignore 2>/dev/null || echo 'android/keystore/'            >> .gitignore
grep -qxF '**/*.jks'                     .gitignore 2>/dev/null || echo '**/*.jks'                     >> .gitignore
```

### 3.2 — Wire the signingConfig into `android/app/build.gradle`
Only if `key.properties` exists and the block has not been added yet. Add it BEFORE `android {`:
```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```
And inside `android { ... }`:
```gradle
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig keystorePropertiesFile.exists() ? signingConfigs.release : signingConfigs.debug
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
```
Create an empty `android/app/proguard-rules.pro` with Flutter's keep rules (Flutter adds them
itself by default; the file just has to exist so `proguardFiles` does not fail).

### 3.3 — Building the AAB (the Google Play format) + a universal APK
```bash
flutter build appbundle --release --obfuscate --split-debug-info=build/symbols 2>&1 | tee /tmp/relng_aab.log
ls -lh build/app/outputs/bundle/release/app-release.aab 2>/dev/null \
  && echo "✅ AAB ready: build/app/outputs/bundle/release/app-release.aab" \
  || echo "⚠️ the AAB did not build (NDK/Gradle?). See /tmp/relng_aab.log"

# The APK too (for a sideload test)
[[ "${1:-}" != "--aab-only" ]] && flutter build apk --release --obfuscate --split-debug-info=build/symbols 2>&1 | tail -3
```

> The AAB is signed with the upload key (if one was created in 3.1) — that is what gets uploaded
> to the Play Console. `--obfuscate --split-debug-info` reduces the size and protects the code;
> the symbols for de-obfuscating stack traces live in `build/symbols/` (keep them with the release).

---

## Phase 4 — the iOS release scaffold [~1 min, no build on Linux]

An IPA cannot be built on Linux (it needs macOS/Xcode). But the preparation can be done:
- Make sure `ios/Runner/Info.plist` has `CFBundleDisplayName` and correct
  `CFBundleShortVersionString`/`CFBundleVersion` (Flutter fills those from pubspec).
- Set `platform :ios, '13.0'` in `ios/Podfile`.
- Create an `ios/ExportOptions.plist` template (method: app-store) for a later `xcodebuild`.
- Record the mac build command in `RELEASE_INFO`/CI:
  `flutter build ipa --release --export-options-plist=ios/ExportOptions.plist`.

The iOS icons were already generated by flutter_launcher_icons (phase 1.2).

---

## Phase 5 — store metadata templates [~1 min]

Create `store/` with listing stubs (filled in from the concept, in English):
```
store/
├── listing/
│   ├── title.txt                 # ≤30 chars
│   ├── short_description.txt      # ≤80 chars
│   ├── full_description.txt       # ≤4000 chars (from the concept's USP + features)
│   └── keywords.txt
├── privacy-policy.md              # a template (data is / is not collected — mark it)
├── data-safety.md                # the answers for Google Play Data Safety
└── age-rating.md                  # IARC: the age rating + its justification
```

Fill `title/short/full description` from the concept's sections (title, USP, features, modes).
The privacy policy is a real template: what data is collected (by default: none, since analytics
is no-op), how it is stored (locally), and a contact.

> **Compliance (MANDATORY for moderation):** `full_description.txt` and `age-rating.md` must
> state explicitly: "a social-casual game, **for entertainment only, with no real money and no
> real winnings**", the 18+ age rating (or whatever the platform's rules require), and the
> presence of an in-app age gate. Without that, Google/Apple will reject a gambling app.

---

## Phase 6 — the CI/CD scaffold [~1 min] (with `--with-ci`, or from autocreate)

Create `.github/workflows/build.yml`:
```yaml
name: build
on: { push: { branches: [ main ] }, workflow_dispatch: {} }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { channel: stable }
      - run: flutter pub get
      - run: dart analyze lib/
      - run: flutter test
      - run: flutter build web --release
      - run: flutter build appbundle --release   # signing through secrets (see below)
      - uses: actions/upload-artifact@v4
        with: { name: release-bundle, path: build/app/outputs/bundle/release/*.aab }
```
In the README's CI section, note that for a signed build in CI the keystore is passed through
GitHub Secrets (a base64 jks + the passwords) rather than committed. Optionally add a
`fastlane/Fastfile` with an `internal` lane (upload to the Play internal track) as a commented-out
template.

---

## Phase 7 — the final report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 RELEASE ENGINEERING COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 Icons: Android (adaptive) + iOS + web — generated
🌅 Native splash: colour from the DNA, Android 12+ supported
🔢 Version: [name]+[build]
🤖 Android: app-release.aab [signed/debug] ([size]) + app-release.apk
   Symbols: build/symbols/ (for de-obfuscating stack traces)
🍎 iOS: the scaffold is ready (the IPA build happens on macOS)
🏪 Store metadata: store/ (listing + privacy + data-safety + age-rating)
   [Gambling: disclaimer + 18+ + age gate noted]
⚙️ CI: .github/workflows/build.yml [with --with-ci]

Next:
  /release-package   — pack the AAB+APK+sources+screenshots into a .zip
  (Play Console)     — upload app-release.aab to the internal track
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quality gates

| Phase | Exit criterion |
|-------|----------------|
| 1. Icons/Splash | `dart run flutter_launcher_icons` + `native_splash:create` with no errors |
| 2. Versioning | `version: X.Y.Z+N` updated, the label set |
| 3. AAB | `build/app/outputs/bundle/release/app-release.aab` exists (signed if there is a keystore) |
| 5. Metadata | `store/` created and filled in from the concept |
| 6. CI | `.github/workflows/build.yml` is valid (if requested) |

## Forbidden
1. Overwriting an existing keystore.
2. Committing `key.properties`, `*.jks` or passwords (all of it goes in .gitignore).
3. Publishing artifacts to external services without an explicit request from the user.
4. Shipping without a disclaimer / age gate / responsible play / age rating (a release blocker).
   Relaxation is acceptable only for C5 without purchases, and must be recorded in the concept.
5. Store metadata in a language other than English, unless the user explicitly asked otherwise.
