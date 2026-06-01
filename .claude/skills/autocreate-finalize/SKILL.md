---
name: autocreate-finalize
description: "Вторая половина конвейера /autocreate (Фазы 10.5 → 11 → 12): runtime emulator verification + финальный отчёт. НЕ вызывает /release-package — упаковка APK и архива выполняется только явным запуском /release-package. Запускается автоматически через Agent tool в конце /autocreate, либо вручную в новой conversation."
argument-hint: "[--skip-emulator | --no-fix]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Finalize — Часть 2 конвейера

**Назначение**: завершить `/autocreate` после того, как Часть 1 довела проект
до `dart analyze` 0 errors + `flutter test` зелёные. В этой части:
- runtime-верификация на эмуляторе (скрины + logcat + auto-fix)
- обновление session-state + финальный отчёт

**Упаковка (APK + архив) НЕ входит в этот навык.** Для получения загружаемого
архива запустите `/release-package` отдельно после финализации.

**Когда вызывается:**
- Автоматически: `/autocreate` в конце Фазы 10 вызывает Agent tool с
  subagent_type="general-purpose" и прописанным промптом
- Вручную: пользователь запускает `/autocreate-finalize` в **новой** conversation,
  если subagent упал, или чтобы повторить runtime-проверку после правок

**Что НЕ делает:**
- НЕ переписывает игровой код, не меняет GDD, не меняет баланс
- НЕ создаёт новые экраны
- НЕ запускает Фазы 1–10 — они уже выполнены Частью 1

---

## 🚨 MANDATORY CONTRACT

1. ✅ Читает `production/session-state/autocreate-handoff.md` **первым действием**
2. ✅ Валидирует что артефакты Части 1 существуют (`pubspec.yaml`, `lib/main.dart`,
   `dart analyze` всё ещё 0 errors)
3. ✅ Выполняет Фазы 10.5 → 11 → 12 в указанном порядке
4. ✅ Возвращает финальный отчёт в родительскую сессию (или печатает пользователю)

**Запрещено:**
- ❌ Менять `lib/game/game_config.dart`, `design/balance/*.json` — баланс зафиксирован
- ❌ Переписывать целые экраны — допустимы только точечные runtime-автофиксы
  (overflow, setState after dispose, missing asset path, null ValueNotifier)
- ❌ Вызывать `/release-package` — упаковка выполняется отдельным явным запуском

---

## Фаза 0 — Preflight & Handoff Read [~30 сек]

```bash
# 1. Handoff должен существовать
test -f production/session-state/autocreate-handoff.md || {
  echo "❌ Нет handoff-файла. Часть 1 /autocreate не завершилась?"
  exit 1
}

# 2. Проект должен компилироваться
dart analyze lib/ > /tmp/finalize_preflight_analyze.log 2>&1
if grep -q " error " /tmp/finalize_preflight_analyze.log; then
  echo "❌ dart analyze lib/ показывает errors — Часть 1 не закончила работу корректно"
  exit 1
fi

# 3. Тесты должны быть зелёными
flutter test > /tmp/finalize_preflight_test.log 2>&1 || {
  echo "⚠️ flutter test красный. Продолжаем, но это стоит исправить."
}
```

Прочитать handoff-файл, извлечь:
- Имя игры → для имени архива
- Жанр → для финального отчёта
- Путь к главному классу игры → для emulator-test навигации

---

## Фаза 10.5 — Runtime Emulator Verification [~8 мин]

Вызвать skill `/emulator-test --quick` (см. `.claude/skills/emulator-test/SKILL.md`).

### 10.5.1 — Preflight (web-first, headless, без дисплея)

> **Дефолт — headless web** через `flutter run -d web-server` + headless Chrome по CDP
> (`tools/web_verify.mjs`). Это НЕ требует ни эмулятора, ни KVM, ни графического дисплея,
> ни `xdotool`/`osascript`. Android AVD — только явный fallback (`--platform android`).
> Это устраняет две главные причины зависаний Фазы 10.5: «не могу открыть/кликнуть Chrome»
> и `flutter screenshot` (он не поддерживает web).

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
  # Явный Android fallback (--platform android). Всё под timeout — не вешаем конвейер.
  RUNNING_EMU=$(adb devices 2>/dev/null | grep -E "emulator-[0-9]+.*device$" | head -1 | awk '{print $1}')
  if [[ -n "$RUNNING_EMU" ]]; then
    echo "✅ Android эмулятор: $RUNNING_EMU"; export PLATFORM=android
    adb -s "$RUNNING_EMU" shell input keyevent 82 2>/dev/null || true
  elif [[ -e /dev/kvm ]] && AVD=$(emulator -list-avds 2>/dev/null | head -1) && [[ -n "$AVD" ]]; then
    echo "🚀 Запуск AVD: $AVD"
    nohup emulator -avd "$AVD" -no-window -no-snapshot-save -no-boot-anim \
          -gpu swiftshader_indirect -no-audio > /tmp/avd.log 2>&1 &
    EMU_PID=$!
    if timeout 90 adb wait-for-device 2>/dev/null && \
       timeout 240 bash -c 'until [ "$(adb shell getprop sys.boot_completed 2>/dev/null|tr -d "\r")" = "1" ]; do sleep 2; done'; then
      sleep 20; echo "✅ AVD прогрет"; export PLATFORM=android
    else
      echo "⚠️ AVD не загрузился вовремя → откат на web."; kill "$EMU_PID" 2>/dev/null || true
      export PLATFORM=web
    fi
  else
    echo "⚠️ Нет эмулятора/KVM/AVD → откат на web."; export PLATFORM=web
  fi
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

# NDK pre-flight — ТОЛЬКО для Android fallback (web не собирает Gradle).
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
- Если `SKIP_SCREENSHOTS=1` (явный opt-out, либо нет node/Chrome для web и нет Android-устройства) —
  **НЕ запускать** 10.5.2, сразу перейти к Фазе 11 с verdict **SKIPPED**. Это штатный путь —
  НЕ ошибка, конвейер считается успешным (игра уже собрана и протестирована в Части 1).
- Иначе (`PLATFORM=web` с node+Chrome, либо `PLATFORM=android` с устройством) — продолжить с 10.5.2.

### 10.5.2 — Runtime tour (только если НЕ SKIP_SCREENSHOTS)

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

**Android fallback** (`PLATFORM=android`): следовать `emulator-test/SKILL.md` (`flutter run` + `adb logcat`
+ `flutter screenshot`/`adb screencap`), режим `--quick`.

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

- **Успех**: 0 CRITICAL визуальных проблем + 0 FATAL exceptions в logcat
- **Частичный успех**: CRITICAL устранены, остались MEDIUM — идём в Фазу 11
- **Неудача**: после 3 итераций CRITICAL остались — сохранить
  `production/runtime-screenshots/<ts>/REPORT.md`, отчитаться с verdict FAIL,
  Фаза 11 всё равно выполняется (active.md обновляется с verdict FAIL)

### 10.5.5 — Артефакты

- `production/runtime-screenshots/<ts>/*.png` — снимки
- `production/runtime-screenshots/<ts>/REPORT.md` — verdict PASS/CONCERNS/FAIL
- `.claude/runtime-logs/flutter-run.log`
- `.claude/runtime-logs/logcat.log`

Cleanup: остановить `flutter run` и `adb logcat` по PID из `.claude/runtime-logs/*.pid`.

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

## Тесты Части 1
- Unit: [N] зелёные
- Integration: [N] зелёные
- Edge cases: [N] зелёные

## Баланс
[RTP / Difficulty curve результаты из Части 1]
```

Также отметить handoff-файл завершённым: дописать в
`production/session-state/autocreate-handoff.md` финальную секцию
`## Часть 2 завершена` с ISO-timestamp и verdict.

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
   ✅ [Genre]: [RNG/matching/spawning/physics] fully functional
   ✅ Stateless Outcomes, GameState sealed class
   ✅ All constants in GameConfig, double-click protection

🧪 Tests (Часть 1):
   ✅ Unit: [N] passed | Integration: [N] passed | Edge: [N] passed

🌐 Runtime verification (Chrome, Фаза 10.5):
   [PASS / CONCERNS / FAIL / SKIPPED] — [N] CRITICAL, [N] HIGH issues
   Скриншоты: production/runtime-screenshots/<ts>/
   Report: production/runtime-screenshots/<ts>/REPORT.md

⚖️ Balance (Часть 1):
   [Gambling: RTP XX.X% (target 95-97%)]
   [Puzzle: Difficulty curve validated]
   [Arcade: Spawn/scoring balanced]

📦 Для получения APK и загружаемого архива:
   /release-package                 — упаковка APK + скриншоты + исходники → один .zip

🔧 Команды запуска:
   flutter run -d chrome        — запустить в Chrome
   flutter run                  — запустить на доступном устройстве
   flutter test                 — запустить тесты
   adb install project_zip/[name]-[ts]/apk/*.apk — установить APK (если есть)

📋 Рекомендованные перезапуски:
   /emulator-test               — ПОВТОРНАЯ runtime-верификация
   /release-package             — ПОВТОРНАЯ упаковка релиза
   /autocreate-finalize         — перезапустить Часть 2 целиком

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
| 10.5. Runtime Chrome | 0 CRITICAL visual + 0 FATAL в flutter-run.log | 3 (Chrome всегда доступен) |
| 11. Session State | `active.md` обновлён | 1 |
| 12. Final Report | Отчёт напечатан / возвращён | 1 |

**АБСОЛЮТНЫЙ МИНИМУМ для завершения Части 2:**
- `production/session-state/active.md` обновлён
- Финальный отчёт напечатан с verdict runtime-верификации

---

## Восстановление после сбоев

**Если subagent упал посреди Части 2** — пользователь запускает
`/autocreate-finalize` в новой conversation. Skill:
1. Читает `autocreate-handoff.md` и `active.md`
2. Определяет, с какой фазы продолжить (по наличию артефактов):
   - Нет `production/runtime-screenshots/<ts>/` → начать с 10.5
   - Есть скрины, но `active.md` не обновлён → начать с 11
3. Продолжает с нужной фазы, не переделывая сделанное

**Если web-верификация невозможна** (нет `node` или бинаря Chrome): `web_verify.mjs` не запустить —
Фаза 10.5 штатно SKIPPED, идём в Фазу 11 с verdict SKIPPED (игра уже собрана и протестирована
в Части 1). Чтобы включить web-верификацию: установить `node` (≥21, нужен встроенный WebSocket)
и Chrome/Chromium (`google-chrome`/`chromium`), либо указать путь в `$CHROME_EXECUTABLE`.
Это НЕ блокирует завершение Части 2.

**Если зависает на Фазе 10.5** — этого не должно происходить: `web_verify.mjs` самозавершается
по `--budget`, поверх него стоит `timeout`, а `flutter run -d web-server` имеет ранний выход при
ошибке сборки. Если всё же завис — убить `$(cat .claude/runtime-logs/flutter.pid)` и осиротевшие
`google-chrome --headless` процессы, пометить verdict SKIPPED и перейти к Фазе 11.
В `RELEASE_INFO.md` пометка `CHROME_SKIPPED: true`.
