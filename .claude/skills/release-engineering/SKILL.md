---
name: release-engineering
description: "Ship-engineering для готовой игры: генерация app-иконок (все плотности + adaptive + iOS), нативный splash, версионирование, signed Android App Bundle (.aab — формат Google Play), iOS-архив-каркас, build-флейворы, обфускация, CI-workflow и шаблоны метаданных стора. Превращает собранный проект в РЕАЛЬНО публикуемый артефакт. Запускается из /autocreate-finalize перед /release-package, либо вручную."
argument-hint: "[--prep-only | --no-keystore | --aab-only | --with-ci]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

# Release Engineering — от «собирается» к «публикуется»

`/release-package` пакует исходники + скриншоты + **debug-подписанный APK**. Этого
недостаточно для публикации: Google Play принимает **подписанный `.aab`**, нужны иконки всех
плотностей, нативный splash, версия/build number, и метаданные листинга. Этот навык закрывает
эту дистанцию.

> **Принцип безопасности:** ничего не публикует наружу, не перезаписывает существующий
> keystore, не коммитит секреты. Keystore и пароли кладутся в **gitignored** `key.properties`.
> Деструктивные шаги (генерация ключа) выполняются только при отсутствии существующего и с
> явным логированием, где лежит ключ.

> **`--prep-only`** (используется из `/autocreate-finalize`): выполнить ТОЛЬКО подготовку —
> Фазы 1 (иконки/splash), 2 (версия), 4 (iOS scaffold), 5 (store-metadata), 6 (CI). **Пропустить
> Фазу 3 целиком** (никакого keystore и никакой сборки AAB/APK). Проект становится release-ready,
> а сами артефакты позже собирает `/release-package` или полный `/release-engineering`.

---

## Фаза 0 — Preflight [~20 сек]

```bash
test -f pubspec.yaml || { echo "❌ Не Flutter-проект (нет pubspec.yaml)"; exit 1; }
dart analyze lib/ > /tmp/relng_analyze.log 2>&1
grep -q " error " /tmp/relng_analyze.log && { echo "❌ dart analyze: errors. Сначала почини."; exit 1; }
flutter --version | head -1
APP_NAME=$(grep -m1 '^name:' pubspec.yaml | awk '{print $2}')
echo "Проект: $APP_NAME"
```

Прочитать из концепта (`design/gdd/game-concept.md`): человекочитаемое название игры (для
launcher label и листинга), цвет фона splash (из Design DNA → Background), жанр (для compliance).

---

## Фаза 1 — App Icon & Native Splash [~2 мин]

### 1.1 — Подготовить иконку-источник (1024×1024 PNG)
Иконка ОБЯЗАНА быть растровой 1024×1024 без альфа-канала для iOS. Источник:
1. Если есть подходящий PNG-логотип в `assets/` — взять его.
2. Иначе — растрировать `assets/images/ui/ui_app_icon.svg` (если есть) или фирменный sprite/лого
   в 1024×1024. Конвертация: `rsvg-convert`/`inkscape`/ImageMagick (`magick -density 384`),
   либо в Codex — GPT Images 2.0 (см. `/svg-to-png`). Положить в `assets/branding/app_icon.png`.
3. Для adaptive-иконки Android — отдельный foreground (прозрачный фон) `app_icon_fg.png` +
   цвет фона из Design DNA.

```bash
mkdir -p assets/branding
# (агент сам выбирает доступный конвертер; финал — assets/branding/app_icon.png 1024x1024)
test -f assets/branding/app_icon.png || echo "⚠️ нет app_icon.png — сгенерировать перед продолжением"
```

### 1.2 — flutter_launcher_icons
Добавить в `dev_dependencies` и сконфигурировать:

```yaml
dev_dependencies:
  flutter_launcher_icons: ^0.14.1

flutter_launcher_icons:
  image_path: "assets/branding/app_icon.png"
  android: true
  ios: true
  remove_alpha_ios: true
  web: { generate: true }
  adaptive_icon_background: "#0E1116"   # ← из Design DNA (Background)
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
  color: "#0E1116"                       # ← из Design DNA
  image: "assets/branding/splash_logo.png"   # моно-лого по центру (опц.)
  android_12: { color: "#0E1116", image: "assets/branding/splash_logo.png" }
  fullscreen: true
```

```bash
dart run flutter_native_splash:create 2>&1 | tail -5
```

> Цвет splash берётся из Design DNA, НЕ дефолтный белый/чёрный. Это первый кадр игры.

---

## Фаза 2 — Versioning & App Identity [~30 сек]

```bash
# version: <semver>+<buildNumber>. Buildnumber монотонно растёт.
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

Launcher label (человекочитаемое имя) — проставить в `android/app/src/main/AndroidManifest.xml`
(`android:label`) и `ios/Runner/Info.plist` (`CFBundleDisplayName`) из названия в концепте.
ApplicationId / bundle id: `com.gamestudio.<name>` (уже задан при `flutter create --org`).

---

## Фаза 3 — Android Signing & App Bundle [~5 мин]

**ПРОПУСТИТЬ ВСЮ ФАЗУ 3 если `--prep-only`** — никакого keystore и никакой сборки AAB/APK.
Артефакты соберёт `/release-package`. (Так эту фазу вызывает `/autocreate-finalize`.)

**Пропустить только подпись (3.1–3.2) если** `--no-keystore` (тогда AAB будет debug-signed —
собирается, но в Play не загрузится; годится для внутреннего теста).

### 3.1 — Upload keystore (только если ещё нет)
```bash
KS=android/keystore/upload-keystore.jks
if [[ -f "$KS" ]]; then
  echo "✅ keystore уже есть: $KS (не перезаписываю)"
elif [[ "${RELNG_NO_KEYSTORE:-0}" == "1" ]]; then
  echo "⏭️ --no-keystore: пропускаю генерацию ключа"
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
  echo "✅ keystore + key.properties созданы."
  echo "🔐 ВАЖНО: сохрани android/keystore/upload-keystore.jks и android/key.properties в надёжном"
  echo "    месте. Потеря ключа = невозможность обновить приложение в Google Play."
fi

# gitignore секретов (идемпотентно)
grep -qxF 'android/key.properties'       .gitignore 2>/dev/null || echo 'android/key.properties'       >> .gitignore
grep -qxF 'android/keystore/'            .gitignore 2>/dev/null || echo 'android/keystore/'            >> .gitignore
grep -qxF '**/*.jks'                     .gitignore 2>/dev/null || echo '**/*.jks'                     >> .gitignore
```

### 3.2 — Wire signingConfig в `android/app/build.gradle`
Только если есть `key.properties` и блок ещё не добавлен. Добавить ПЕРЕД `android {`:
```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```
И внутри `android { ... }`:
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
Создать пустой `android/app/proguard-rules.pro` с keep-правилами Flutter (по умолчанию Flutter
сам их добавляет; файл нужен, чтобы `proguardFiles` не падал).

### 3.3 — Сборка AAB (формат Google Play) + universal APK
```bash
flutter build appbundle --release --obfuscate --split-debug-info=build/symbols 2>&1 | tee /tmp/relng_aab.log
ls -lh build/app/outputs/bundle/release/app-release.aab 2>/dev/null \
  && echo "✅ AAB готов: build/app/outputs/bundle/release/app-release.aab" \
  || echo "⚠️ AAB не собрался (NDK/Gradle?). См. /tmp/relng_aab.log"

# APK тоже (для sideload-теста)
[[ "${1:-}" != "--aab-only" ]] && flutter build apk --release --obfuscate --split-debug-info=build/symbols 2>&1 | tail -3
```

> AAB подписан upload-ключом (если он создан в 3.1) — это то, что грузится в Play Console.
> `--obfuscate --split-debug-info` уменьшает размер и защищает код; символы для деобфускации
> стектрейсов лежат в `build/symbols/` (сохранить вместе с релизом).

---

## Фаза 4 — iOS Release Scaffold [~1 мин, без сборки на Linux]

На Linux IPA не собрать (нужен macOS/Xcode). Но подготовить можно:
- Убедиться, что `ios/Runner/Info.plist` содержит `CFBundleDisplayName`, корректный
  `CFBundleShortVersionString`/`CFBundleVersion` (Flutter подставляет из pubspec).
- Прописать в `ios/Podfile` `platform :ios, '13.0'`.
- Создать `ios/ExportOptions.plist` шаблон (method: app-store) для последующего `xcodebuild`.
- Зафиксировать в `RELEASE_INFO`/CI команду сборки на mac:
  `flutter build ipa --release --export-options-plist=ios/ExportOptions.plist`.

Иконки iOS уже сгенерированы flutter_launcher_icons (Фаза 1.2).

---

## Фаза 5 — Store Metadata Templates [~1 мин]

Создать `store/` с заготовками листинга (заполняются из концепта):
```
store/
├── listing/
│   ├── title.txt                 # ≤30 симв
│   ├── short_description.txt      # ≤80 симв
│   ├── full_description.txt       # ≤4000 симв (из USP + фич концепта)
│   └── keywords.txt
├── privacy-policy.md              # шаблон (данные не собираются / собираются — отметить)
├── data-safety.md                # ответы на Google Play Data Safety
└── age-rating.md                  # IARC: возрастной рейтинг + обоснование
```

Заполнить `title/short/full description` из секций концепта (название, USP, фичи, режимы).
Privacy policy — реальный шаблон: какие данные собираются (по умолчанию: никакие, т.к. analytics
no-op), как хранятся (локально), контакт.

> **Gambling-жанр (ОБЯЗАТЕЛЬНО для модерации):** в `full_description.txt` и `age-rating.md`
> явно указать: «социально-казуальная игра, **только для развлечения, без реальных денег и
> реальных выигрышей**», возрастной рейтинг 18+ (или по правилам платформы), наличие
> in-app age-gate. Без этого Google/Apple отклонят гемблинг-приложение.

---

## Фаза 6 — CI/CD Scaffold [~1 мин] (если `--with-ci` или из autocreate)

Создать `.github/workflows/build.yml`:
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
      - run: flutter build appbundle --release   # подпись через secrets (см. ниже)
      - uses: actions/upload-artifact@v4
        with: { name: release-bundle, path: build/app/outputs/bundle/release/*.aab }
```
В README CI-секции отметить, что для подписанной сборки в CI keystore передаётся через
GitHub Secrets (base64 jks + пароли), а не коммитится. Опционально — `fastlane/Fastfile`
с lane `internal` (upload to Play internal track) как закомментированный шаблон.

---

## Фаза 7 — Final Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 RELEASE ENGINEERING COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 Иконки: Android (adaptive) + iOS + web — сгенерированы
🌅 Native splash: цвет из DNA, Android 12+ поддержан
🔢 Версия: [name]+[build]
🤖 Android: app-release.aab [signed/debug] ([size]) + app-release.apk
   Symbols: build/symbols/ (деобфускация стектрейсов)
🍎 iOS: каркас готов (сборка IPA — на macOS)
🏪 Store metadata: store/ (listing + privacy + data-safety + age-rating)
   [Gambling: disclaimer + 18+ + age-gate отмечены]
⚙️ CI: .github/workflows/build.yml [если --with-ci]

Следующее:
  /release-package   — упаковать AAB+APK+исходники+скриншоты в .zip
  (Play Console)     — загрузить app-release.aab во внутренний трек
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quality Gates

| Фаза | Критерий выхода |
|------|----------------|
| 1. Icons/Splash | `dart run flutter_launcher_icons` + `native_splash:create` без ошибок |
| 2. Versioning | `version: X.Y.Z+N` обновлён, label проставлен |
| 3. AAB | `build/app/outputs/bundle/release/app-release.aab` существует (signed если есть keystore) |
| 5. Metadata | `store/` создан и заполнен из концепта |
| 6. CI | `.github/workflows/build.yml` валиден (если запрошен) |

## Запрещено
1. Перезаписывать существующий keystore.
2. Коммитить `key.properties`, `*.jks`, пароли (всё в .gitignore).
3. Публиковать артефакты во внешние сервисы без явного запроса пользователя.
4. Для gambling — выпускать без disclaimer/age-gate/18+ (release-блокер).
