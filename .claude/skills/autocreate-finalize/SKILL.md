---
name: autocreate-finalize
description: "Сессия 3 конвейера /autocreate (Фазы 10.5 → 10.6 → 11 → 11.5 → 12): runtime+soak верификация (Chrome CDP, auto-fix), playtest (реальная игровая сессия P1–P10), session-state, release-engineering PREP (иконки/splash/версия/store-metadata/CI — БЕЗ сборки AAB/APK и БЕЗ keystore) и финальный отчёт. Оставляет проект release-ready. НЕ собирает артефакты и НЕ вызывает /release-package — это явный запуск пользователя. Запускается автоматически через Agent tool в конце Сессии 2 (autocreate-implement), либо вручную в новой conversation."
argument-hint: "[--skip-emulator | --no-fix]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Finalize — Сессия 3 конвейера

**Назначение**: завершить `/autocreate` после того, как Сессия 2 (`autocreate-implement`)
довела проект до `dart analyze` 0 errors + `flutter test` зелёные. В этой сессии:
- runtime-верификация: Chrome/CDP (скрины + консоль + auto-fix) + soak-проба на утечки;
  Android (`--platform android`) — только Gradle compile-only проверка, без эмулятора/APK
- **playtest** (Фаза 10.6): реальная игровая сессия — проверки P1–P10 из
  `.claude/skills/playtest/SKILL.md` (числа меняются, win/lose пути, живое поле, прогрессия)
- обновление session-state + финальный отчёт
- **release-engineering PREP** (`/release-engineering --prep-only --no-keystore`): иконки, native
  splash, версия, store-metadata, CI — **БЕЗ сборки AAB/APK и БЕЗ keystore**

**Сборка артефактов НЕ входит в этот навык.** AAB/APK + архив собирает `/release-package`
(явный запуск). Для signed-AAB под Google Play — `/release-engineering` без флагов (сминтит
upload-keystore, явное действие пользователя).

**Когда вызывается:**
- Автоматически: Сессия 2 (`autocreate-implement`) в конце Фазы 10.7 вызывает Agent tool
  с прописанным промптом (full-history fork, без subagent_type)
- Вручную: пользователь запускает `/autocreate-finalize` в **новой** conversation,
  если subagent упал, или чтобы повторить runtime-проверку после правок

**Что НЕ делает:**
- НЕ переписывает игровой код, не меняет GDD, не меняет баланс
- НЕ создаёт новые экраны
- НЕ запускает Фазы 1–10 — они уже выполнены Сессией 2

---

## 🚨 MANDATORY CONTRACT

1. ✅ Читает `production/session-state/autocreate-handoff.md` **первым действием**
2. ✅ Валидирует что артефакты Сессии 2 существуют (`pubspec.yaml`, `lib/main.dart`,
   `dart analyze` всё ещё 0 errors)
3. ✅ Выполняет Фазы 10.5 → 11 → 11.5 → 12 в указанном порядке
4. ✅ Возвращает финальный отчёт в родительскую сессию (или печатает пользователю)

**Запрещено:**
- ❌ Менять `lib/game/game_config.dart`, `design/balance/*.json`, `assets/data/*.json` —
  баланс/контент зафиксированы
- ❌ Переписывать целые экраны — допустимы только точечные runtime-автофиксы
  (overflow, setState after dispose, missing asset path, null ValueNotifier)
- ❌ Генерировать release upload-keystore — Фаза 11.5 идёт ТОЛЬКО с `--no-keystore`;
  signed-AAB пользователь делает явным `/release-engineering`
- ❌ Вызывать `/release-package` — упаковка выполняется отдельным явным запуском

---

## Фаза 0 — Preflight & Handoff Read [~30 сек]

```bash
# 1. Handoff должен существовать
test -f production/session-state/autocreate-handoff.md || {
  echo "❌ Нет handoff-файла. Сессия 2 (autocreate-implement) не завершилась?"
  exit 1
}

# 2. Проект должен компилироваться
dart analyze lib/ > /tmp/finalize_preflight_analyze.log 2>&1
if grep -q " error " /tmp/finalize_preflight_analyze.log; then
  echo "❌ dart analyze lib/ показывает errors — Сессия 2 не закончила работу корректно"
  exit 1
fi

# 3. Тесты должны быть зелёными
flutter test > /tmp/finalize_preflight_test.log 2>&1 || {
  echo "⚠️ flutter test красный. Продолжаем, но это стоит исправить."
}
```

Прочитать handoff-файл, извлечь:
- Имя игры → для имени архива
- Категория (C1–C6) и матмодель (M1–M6) → для финального отчёта
- Путь к главному классу игры → для emulator-test навигации

---

## Фаза 10.5 — Runtime Emulator Verification [~8 мин]

Вызвать skill `/emulator-test --quick` (см. `.claude/skills/emulator-test/SKILL.md`).

### 10.5.1 — Preflight (web-first, headless, без дисплея)

> **Дефолт — headless web** через `flutter run -d web-server` + headless Chrome по CDP
> (`tools/web_verify.mjs`). Это НЕ требует ни эмулятора, ни KVM, ни графического дисплея,
> ни `xdotool`/`osascript`. Android (`--platform android`) — явный запрос, и он **не поднимает
> эмулятор/AVD**: это чистая **Gradle compile-only верификация** (`flutter build apk --debug`,
> APK не сохраняется и никуда не паковается), без runtime-тура, скриншотов и `adb logcat`.
> Это устраняет две главные причины зависаний Фазы 10.5: «не могу открыть/кликнуть Chrome»
> и «не могу поднять AVD/KVM в headless-окружении».

```bash
# Что нужно для web-пути: node (для CDP-драйвера) + бинарь Chrome (для headless-снимков).
HAVE_NODE=0; command -v node >/dev/null 2>&1 && HAVE_NODE=1
CHROME_BIN="${CHROME_EXECUTABLE:-}"
for c in google-chrome google-chrome-stable chromium chromium-browser; do
  [ -z "$CHROME_BIN" ] && command -v "$c" >/dev/null 2>&1 && CHROME_BIN="$(command -v "$c")"
done
export CHROME_EXECUTABLE="$CHROME_BIN"

if [[ "${AUTOCREATE_SKIP_EMULATOR:-0}" == "1" ]]; then
  echo "⏭️ AUTOCREATE_SKIP_EMULATOR=1 — Фаза 10.5 SKIPPED по запросу."
  export SKIP_SCREENSHOTS=1
elif [[ "${PLATFORM:-web}" == "android" ]]; then
  # Явный запрос Android (--platform android). НЕ поднимаем эмулятор/AVD/KVM —
  # это только компиляционная верификация Gradle-сборки, см. 10.5.2c.
  echo "🤖 PLATFORM=android → Gradle compile-only verification (без эмулятора/скриншотов)."
fi

# Web-путь (дефолт): нужен node + Chrome. Если их нет — единственный честный SKIP.
if [[ "${SKIP_SCREENSHOTS:-0}" != "1" && "${PLATFORM:-web}" == "web" ]]; then
  if [[ $HAVE_NODE -eq 1 && -n "$CHROME_BIN" ]]; then
    echo "🌐 Web-путь: node=$(node -v) chrome=$CHROME_BIN"; export PLATFORM=web
  else
    echo "⚠️ Нет node ($HAVE_NODE) или Chrome ('$CHROME_BIN') — web-верификация невозможна. SKIPPED."
    export SKIP_SCREENSHOTS=1
  fi
fi

# NDK pre-flight — ТОЛЬКО для Android compile-only верификации (web не собирает Gradle).
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

**Критерий перехода:**
- Если `SKIP_SCREENSHOTS=1` (явный opt-out, либо нет node/Chrome для web) —
  **НЕ запускать** 10.5.2, сразу перейти к Фазе 11 с verdict **SKIPPED**. Это штатный путь —
  НЕ ошибка, конвейер считается успешным (игра уже собрана и протестирована в Сессии 2).
- Иначе (`PLATFORM=web` с node+Chrome, либо `PLATFORM=android` — устройство/эмулятор
  для последнего НЕ нужны, это compile-only) — продолжить с 10.5.2.

### 10.5.2 — Runtime tour / Compile verification (только если НЕ SKIP_SCREENSHOTS)

**Web-путь (дефолт)** — самодостаточные команды (детали см. в `emulator-test/SKILL.md`):

```bash
mkdir -p .claude/runtime-logs
WEB_PORT=8099

# 1) headless dev-server (не открывает браузер)
nohup flutter run -d web-server --web-port "$WEB_PORT" --web-hostname 127.0.0.1 \
  > .claude/runtime-logs/flutter-run.log 2>&1 &
echo $! > .claude/runtime-logs/flutter.pid

# 2) ждём URL, с ранним выходом при ошибке сборки (без зависания)
WEB_URL=""
for i in $(seq 1 120); do
  WEB_URL=$(grep -oE "http://127\.0\.0\.1:[0-9]+" .claude/runtime-logs/flutter-run.log 2>/dev/null | head -1)
  [ -n "$WEB_URL" ] && break
  grep -qE "Failed to compile|Target dart2js failed|Compilation failed|^Error: " .claude/runtime-logs/flutter-run.log 2>/dev/null && break
  sleep 2
done

TS=$(date +%Y%m%d-%H%M%S); SHOT_DIR="production/runtime-screenshots/$TS"; mkdir -p "$SHOT_DIR"

if [ -n "$WEB_URL" ]; then
  # 3) ВЕСЬ тур по экранам + снимки + консоль/исключения одним самозавершающимся вызовом.
  #    Внешний timeout — страховка над внутренним --budget.
  timeout 220 node tools/web_verify.mjs --url "$WEB_URL" --out "$SHOT_DIR" --budget 180 --quick \
    2>&1 | tee "$SHOT_DIR/web_verify.log"
else
  echo "❌ web-server не поднялся — сборка сломана. Лог: .claude/runtime-logs/flutter-run.log" \
    | tee "$SHOT_DIR/web_verify.log"
fi

# 4) cleanup сервера (скрипт сам убивает свой headless Chrome)
kill "$(cat .claude/runtime-logs/flutter.pid 2>/dev/null)" 2>/dev/null || true
```

Затем:
- **Визуальный анализ** каждого `$SHOT_DIR/*.png` через Read (vision) по чеклисту V1–V12.
- **Парсинг ошибок**: `jq '.consoleErrors' "$SHOT_DIR/manifest.json"`, `$SHOT_DIR/webconsole.log`,
  и `.claude/runtime-logs/flutter-run.log` (EXCEPTION CAUGHT, RenderFlex overflowed, Unable to load asset).

### 10.5.2c — Android compile verification (только если `PLATFORM=android`)

Android здесь — **НЕ** runtime-тур. Никакого эмулятора/AVD, никаких скриншотов, никакого
`adb logcat`. Единственная цель — подтвердить, что Gradle-проект действительно компилируется
(в т.ч. что NDK/minSdk патчи из 10.5.1 сработали). Полноценная runtime-верификация игры уже
идёт через web (Chrome/CDP) выше; Android-путь отвечает только на вопрос «компилируется ли»,
а не «работает ли на устройстве» — для этого не нужны эмулятор/KVM/устройство.

```bash
mkdir -p .claude/runtime-logs
timeout 600 flutter build apk --debug 2>&1 | tee .claude/runtime-logs/android-build.log
ANDROID_BUILD_EXIT=${PIPESTATUS[0]}

if [[ "$ANDROID_BUILD_EXIT" == "0" ]]; then
  echo "✅ Android Gradle compile OK — приложение собирается."
else
  echo "❌ Android Gradle compile FAILED — см. .claude/runtime-logs/android-build.log"
fi

# Это верификация, не релизный артефакт — APK не сохраняется и никуда не паковается.
rm -f build/app/outputs/flutter-apk/app-debug.apk 2>/dev/null || true
```

Ошибки компиляции (Gradle/Kotlin/NDK/Dart-платформенный код) разбираются так же, как
`dart analyze` ошибки в Фазе 6 `autocreate-implement`: направляются
mechanics-programmer/ui-programmer, разрешено до 2 итераций правки и повторного
`flutter build apk --debug`. Упаковка (`flutter build apk --release`, AAB, подпись,
архивация) сюда не входит — это отдельный явный `/release-package` по запросу пользователя.

### 10.5.2b — Soak / Leak probe (web, опционально но рекомендуется)

Полная игра должна выдерживать длинную сессию без роста памяти/исключений. Если web-путь
активен, прогнать короткий soak: ~150–200 авто-действий (повтор основного игрового действия +
переходы между экранами) и сравнить heap в начале/конце + накопление console-ошибок.

```bash
# web_verify.mjs --soak N выполняет N циклов действие→ожидание и пишет heapUsedStart/End
# (если флаг не поддержан в текущей версии — пропустить, это не блокер).
timeout 180 node tools/web_verify.mjs --url "$WEB_URL" --out "$SHOT_DIR" --soak 150 \
  2>&1 | tee -a "$SHOT_DIR/web_verify.log" || echo "soak skipped"
```

Признак утечки: монотонный рост `JSHeapUsedSize` без плато после GC, или растущее число
повторяющихся console-исключений. Найденное — в REPORT.md как HIGH (не CRITICAL, если игра
играбельна); точечный фикс (un-disposed controller/timer/particle leak) разрешён.

### 10.5.3 — Auto-Fix Loop (до 3 итераций)

Консолидировать проблемы, разметить severity (CRITICAL/HIGH/MEDIUM), назначить агентов:
- V2/V3/V5/V7/V8/V9/V10/V11 → **ui-programmer**
- V4/V12 → **mechanics-programmer**
- VFX не виден → **juice-artist**
- Logcat asset errors → проверить `lib/assets.dart` vs реальные файлы

**Разрешённые автофиксы:**

| Симптом | Причина | Автофикс |
|---------|---------|----------|
| Пустой чёрный прямоугольник вместо игрового поля | Компоненты не добавлены в World.onLoad() | `await world.addAll([...])` |
| HUD показывает null/NaN | ValueNotifier не проинициализирован | Проинициализировать в Game constructor |
| Splash чёрный и не переходит | Нет Timer для навигации | `Future.delayed → pushReplacementNamed` |
| Белый экран после PLAY | Route не зарегистрирован | Добавить в `routes:` map в app.dart |
| Жёлтые overflow полосы | ListView без Expanded | Обернуть в Expanded |
| Красный экран exception | Null check/type error из stacktrace | Исправить по file:line из лога |
| "Unable to load asset" | Несоответствие путей в `lib/assets.dart` | Исправить путь или создать файл |

**Запрещённые "автофиксы":**
- Менять `game_config.dart` (баланс зафиксирован)
- Менять `rtp-config.json` / `level-config.json`
- Переписывать целые экраны — только точечные правки
- Менять GDD

### 10.5.4 — Критерий выхода Фазы 10.5

**Web-путь (дефолт):**
- **Успех**: 0 CRITICAL визуальных проблем + 0 FATAL exceptions в консоли
- **Частичный успех**: CRITICAL устранены, остались MEDIUM — идём в Фазу 11
- **Неудача**: после 3 итераций CRITICAL остались — сохранить
  `production/runtime-screenshots/<ts>/REPORT.md`, отчитаться с verdict FAIL,
  Фаза 11 всё равно выполняется (active.md обновляется с verdict FAIL)

**Android-путь (`PLATFORM=android`, compile-only):**
- **Успех**: `flutter build apk --debug` завершается с exit code 0 (`ANDROID_BUILD_EXIT=0`)
- **Неудача**: после 2 итераций автофикса ошибки компиляции остались — verdict FAIL с
  причиной из `.claude/runtime-logs/android-build.log`, Фаза 11 всё равно выполняется
- Здесь нет понятий CRITICAL/MEDIUM визуальных проблем — это не runtime-тур

### 10.5.5 — Артефакты

**Web-путь:**
- `production/runtime-screenshots/<ts>/*.png` — снимки
- `production/runtime-screenshots/<ts>/REPORT.md` — verdict PASS/CONCERNS/FAIL
- `.claude/runtime-logs/flutter-run.log`

**Android-путь (compile-only):**
- `.claude/runtime-logs/android-build.log` — лог `flutter build apk --debug`
- Никаких скриншотов/logcat/APK-файлов — эта верификация ничего не сохраняет как артефакт

Cleanup: остановить `flutter run` по PID из `.claude/runtime-logs/*.pid` (web-путь).

---

## Фаза 10.6 — Playtest (реальная игровая сессия) [~6 мин]

> Фаза 10.5 проверила «экраны открываются и не падают». Эта фаза проверяет «в это
> ИГРАЕТСЯ»: действия дают результат, числа меняются, победы празднуются, поле живое.
> Эталон — `.claude/docs/quality-bar.md` (§2–§4, §6, §7).

Выполнить runbook `.claude/skills/playtest/SKILL.md` (если web-путь был SKIPPED в 10.5,
или если 10.5 шла по Android compile-only пути — эта фаза тоже честно SKIPPED, не ошибка:
playtest требует реально работающий инстанс через CDP, а compile-only ничего не запускает):

- Тур + игровая нагрузка (`web_verify.mjs --soak 60`) → проверки **P1–P10**
  (vision-сравнение кадров: действие меняет поле, HUD-числа меняются, win-фидбек виден,
  idle-анимация есть; manifest: 0 consoleErrors, suspectLeak=false).
- Verdict: **PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED** →
  `production/playtest/<ts>/PLAYTEST-REPORT.md`.
- При CRITICAL (P1/P2/P8) — автофикс-цикл до 2 итераций по той же таблице разрешённых
  фиксов, что в 10.5.3 (только точечные правки wiring; НЕ баланс, НЕ переписывание экранов).

**Критерий выхода:** PLAYTEST-REPORT.md существует; verdict ≠ NOT-PLAYABLE (или 2 итерации
исчерпаны — тогда verdict честно фиксируется и попадает в финальный отчёт как FAIL-причина).

---

## Фаза 11 — Session State Update [~1 мин]

Обновить `production/session-state/active.md`:

```markdown
<!-- STATUS -->
Epic: [Game Name]
Feature: Complete Game
Task: Production-ready
<!-- /STATUS -->

## Статус
Игра полностью реализована и верифицирована. Для получения APK и архива запустите /release-package.

## Runtime verification
- Verdict: [PASS / CONCERNS / FAIL / SKIPPED]
- Скриншоты: production/runtime-screenshots/<ts>/
- Report: production/runtime-screenshots/<ts>/REPORT.md

## Тесты Сессии 2
- Unit: [N] зелёные
- Integration: [N] зелёные
- Edge cases: [N] зелёные

## Баланс
[Вердикт прогона матмодели из Сессии 2: модель, метрика, PASS/CONCERNS/FAIL]
```

Также отметить handoff-файл завершённым: дописать в
`production/session-state/autocreate-handoff.md` финальную секцию
`## Сессия 3 завершена` с ISO-timestamp и verdict.

---

## Фаза 11.5 — Release Engineering Prep (БЕЗ сборки) [~3 мин]

Запустить `/release-engineering --prep-only --no-keystore`
(см. `.claude/skills/release-engineering/SKILL.md`). **Сборка AAB/APK здесь НЕ выполняется** —
цель: оставить проект ГОТОВЫМ к `/release-package`, не тратя время на тяжёлый Gradle-build:
- App-иконки (Android adaptive + iOS + web) и native splash из Design DNA.
- Версия/build number, launcher label.
- `store/` — заготовки листинга, privacy-policy, data-safety, age-rating (gambling — disclaimer).
- `.github/workflows/build.yml` (CI).
- **НЕ** генерирует upload-keystore и **НЕ** собирает AAB/APK.

```bash
# Безопасный prep: не создаёт keystore, не публикует наружу, не собирает артефакты.
flutter pub get >/dev/null 2>&1 || true
# Если release-engineering недоступен как skill — выполнить вручную только prep-шаги:
#   dart run flutter_launcher_icons ; dart run flutter_native_splash:create
#   (НЕ запускать flutter build appbundle/apk здесь — это делает /release-package)
```

> Если иконка-источник `assets/branding/app_icon.png` отсутствует — сгенерировать её из
> фирменного логотипа/спрайта (rasterize SVG в 1024×1024) перед запуском launcher_icons.

**Критерий выхода:** иконки и splash сгенерированы, `store/` создан. Артефакты (AAB/APK) НЕ
собираются — их соберёт `/release-package`. Для подписанного Play-AAB пользователь запускает
`/release-engineering` (без флагов) — он сминтит keystore и соберёт signed AAB.

---

## Фаза 12 — Final Report

Вывести пользователю (а если вызван как subagent — вернуть в родительскую сессию):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 AUTOCREATE COMPLETE — PRODUCTION READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Экраны (12+):
   ✅ Splash, Main Menu, Game Screen + HUD
   ✅ Paytable, Settings, Help, Daily Bonus
   ✅ Leaderboard, Profile, Win Overlays (3 tiers)
   ✅ Insufficient Funds, Bonus Mode Overlay

🎮 Gameplay:
   ✅ Core game loop works end-to-end
   ✅ [Категория]: [RNG / резолвер исхода / cash-out / pity / физика] fully functional
   ✅ Stateless Outcomes, GameState sealed class
   ✅ All constants in GameConfig, double-click protection

🗂 Контент и режимы (Фаза 4.5):
   ✅ [N] уровней/стейджей (assets/data/*.json) | Режимы: [Classic + Endless/Time-Attack/Daily]
   ✅ Level/Mode Select связан с реальными данными

🧩 Мета-системы (Agent E):
   ✅ SaveService (versioned), Economy (валюта+магазин), Progression (звёзды), Achievements
   ✅ Analytics/Ads/IAP/RemoteConfig — abstractions (no-op, без внешних SDK)
   [Gambling: age-gate + disclaimer 18+ + responsible-play]

🔊 Audio (Фаза 3.5):
   ✅ 9 реальных .wav синтезированы (mood: [mood]) — SFX + BGM, не заглушки

🧪 Tests (Сессия 2):
   ✅ Unit: [N] passed | Integration: [N] passed | Edge: [N] passed

🌐 Runtime verification (Chrome, Фаза 10.5):
   [PASS / CONCERNS / FAIL / SKIPPED] — [N] CRITICAL, [N] HIGH issues
   Скриншоты: production/runtime-screenshots/<ts>/
   Report: production/runtime-screenshots/<ts>/REPORT.md

🕹 Playtest (Фаза 10.6 — реальная игровая сессия):
   [PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED]
   P1–P10: [кратко — например «P1–P8 PASS, P9 leak-suspect, P10 PASS»]
   Report: production/playtest/<ts>/PLAYTEST-REPORT.md

⚖️ Balance (Сессия 2):
   [Gambling: RTP XX.X% (target 95-97%)]
   [Матмодель M1–M6: метрика в целевом окне, отчёт в design/balance/simulation-report.md]

🚀 Release-ready (Фаза 11.5, PREP — без сборки):
   ✅ Иконки (Android adaptive + iOS + web) + native splash (цвет из DNA)
   ✅ Версия [name]+[build], store/ (listing+privacy+data-safety+age-rating)
   ⚙️ .github/workflows/build.yml (CI)
   ℹ️ AAB/APK НЕ собирались — проект готов к упаковке

📦 Сборка артефактов / публикация (явный запуск пользователя):
   /release-package                 — собрать AAB+APK + скриншоты + исходники → один .zip
   /release-engineering             — сминтить upload-keystore → SIGNED .aab для Google Play

🔧 Команды запуска:
   flutter run -d chrome        — запустить в Chrome
   flutter run                  — запустить на доступном устройстве
   flutter test                 — запустить тесты
   adb install project_zip/[name]-[ts]/apk/*.apk — установить APK (если есть)

📋 Рекомендованные перезапуски:
   /emulator-test               — ПОВТОРНАЯ runtime-верификация
   /release-package             — ПОВТОРНАЯ упаковка релиза
   /autocreate-finalize         — перезапустить Сессию 3 целиком

📋 Опциональные следующие шаги:
   /add-feature [фича]          — добавить механику
   /code-review                 — полное ревью кода
   /balance-check               — детальная проверка баланса (1М итераций)
   /perf-profile                — профилирование производительности
   /release-checklist           — финальный GO/NO-GO чеклист перед стор-релизом
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Гарантии качества (Quality Gates)

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 0. Preflight | Handoff есть + `dart analyze` 0 errors | 1 (fail-fast) |
| 10.5. Runtime Chrome / Android compile | Web: 0 CRITICAL visual + 0 FATAL в flutter-run.log (+ soak: нет утечки). Android (`--platform android`): `flutter build apk --debug` exit 0 | 3 (Chrome всегда доступен) / 2 (Android compile) |
| 10.6. Playtest | PLAYTEST-REPORT.md, verdict ≠ NOT-PLAYABLE (P1–P10) | 2 |
| 11. Session State | `active.md` обновлён | 1 |
| 11.5. Release-eng prep | Иконки/splash сгенерированы, `store/` создан (AAB best-effort) | 1 |
| 12. Final Report | Отчёт напечатан / возвращён | 1 |

**АБСОЛЮТНЫЙ МИНИМУМ для завершения Сессии 3:**
- `production/session-state/active.md` обновлён
- Финальный отчёт напечатан с verdict runtime-верификации

---

## Восстановление после сбоев

**Если subagent упал посреди Сессии 3** — пользователь запускает
`/autocreate-finalize` в новой conversation. Skill:
1. Читает `autocreate-handoff.md` и `active.md`
2. Определяет, с какой фазы продолжить (по наличию артефактов):
   - Нет `production/runtime-screenshots/<ts>/` и нет `.claude/runtime-logs/android-build.log` → начать с 10.5
   - Есть скрины (или, для Android-пути, `android-build.log` с exit 0), но нет
     `production/playtest/<ts>/PLAYTEST-REPORT.md` → начать с 10.6 (для Android-пути этот
     шаг честно SKIPPED — сразу к 11)
   - Есть playtest-report (или Android-путь дошёл до SKIPPED-плейтеста), но `active.md`
     не обновлён → начать с 11
3. Продолжает с нужной фазы, не переделывая сделанное

**Если web-верификация невозможна** (нет `node` или бинаря Chrome): `web_verify.mjs` не запустить —
Фаза 10.5 штатно SKIPPED, идём в Фазу 11 с verdict SKIPPED (игра уже собрана и протестирована
в Сессии 2). Чтобы включить web-верификацию: установить `node` (≥21, нужен встроенный WebSocket)
и Chrome/Chromium (`google-chrome`/`chromium`), либо указать путь в `$CHROME_EXECUTABLE`.
Это НЕ блокирует завершение Сессии 3.

**Если зависает на Фазе 10.5** — этого не должно происходить: `web_verify.mjs` самозавершается
по `--budget`, поверх него стоит `timeout`, а `flutter run -d web-server` имеет ранний выход при
ошибке сборки. Если всё же завис — убить `$(cat .claude/runtime-logs/flutter.pid)` и осиротевшие
`google-chrome --headless` процессы, пометить verdict SKIPPED и перейти к Фазе 11.
В `RELEASE_INFO.md` пометка `CHROME_SKIPPED: true`.
