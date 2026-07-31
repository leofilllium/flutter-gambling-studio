---
name: autocreate
description: "Фабрика производства ПОЛНЫХ гемблинг-игр Zero-to-Production (категории C1-C6). Концепт + Production Plan, реалистичные PNG-ассеты в Codex через GPT Images 2.0 с fallback на GPT Images/default Codex image generation (SVG только fallback вне Codex), РЕАЛЬНОЕ синтезированное аудио (.wav), полный код на Flutter/Flame 1.18.x со ВСЕМИ экранами (15+), ВСЯ игровая логика + мета-системы (save/economy/progression/achievements + analytics/ads/iap/remote-config abstractions), КОНТЕНТ (bet-tiers/стейджи/баннеры/режимы), тесты, UI/UX аудит (compliance), верификация матмодели M1-M6, runtime+soak верификация, release-engineering (иконки/splash/AAB/store-metadata). Результат — полная, публикуемая 2D-игра без крашей, а не мини-демо."
argument-hint: "[--from-concept | --idea-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# AutoCreate — Zero-to-Production Complete Game Factory

Выполняет ПОЛНЫЙ цикл разработки мини-игры до production-ready состояния.
**Результат: полностью рабочее приложение (первичная платформа — Chrome/Web, Android APK — опционально), которое компилируется, запускается и НЕ КРАШИТСЯ.**

**ЗАПРЕЩАЕТСЯ задавать вопросы.**

**CODEX ASSET DEFAULT:** в Codex `/autocreate` всегда создаёт **PNG через GPT Image 2**.
В Codex app используется built-in image generation tool; в headless Codex CLI, где tool не
экспонирован, та же модель `gpt-image-2` вызывается через `python3 tools/gpt_image.py`.
Отсутствие built-in tool не является причиной fallback. Если оба транспорта GPT Image 2
технически не сработали, повторить генерацию через **GPT Images / default Codex image
generation** с тем же prompt. SVG допустим только если среда НЕ Codex, пользователь явно передал
`--svg`, либо после зафиксированного провала всех PNG-путей и явного решения пользователя.
Дефолтный визуальный профиль PNG —
realistic/material-grounded game assets: правдоподобные материалы, единый свет, чистый силуэт,
простые ассеты на плоском chroma-key фоне для локального вырезания, без flat clipart.

**CODEX ASSET BUDGET:** `/autocreate` использует `design/asset-manifest.md`: максимум 12
уникальных PNG-источников и 2 технических recovery-вызова. GPT Images 2.0 создаёт только
уникальные игровые силуэты и сцены; UI, типографика, иконки, VFX и безопасные варианты
создаются кодом, локально выводятся из источника или переиспользуются. GPT Images/default
не является вторым эстетическим кандидатом и используется только после технического сбоя
GPT Images 2.0.

---

## 🚨 MANDATORY EXECUTION CONTRACT (читать до начала работы)

`/autocreate` — это **полный конвейер Zero-to-Production**, разбитый на **ТРИ
context-сессии** во избежание истощения токенов (полная игра тяжелее, чем мини-демо):

- **Сессия 1 — Pre-production (ЭТА conversation, Фазы 1 → 3.7)** — концепт+Production Plan,
  bootstrap проекта, ассеты, синтез аудио, генерация ДАННЫХ контента/экономики. Лёгкая по
  контексту: дизайн-выход + конфиги, без массового кода. В конце — spawn Сессии 2.
- **Сессия 2 — Implementation (свежий subagent, Фазы 4 → 10)** — 5 агентов пишут код + мета-
  системы, wiring контента, интеграция, build, feel-pass, тесты, UI-аудит, баланс, crash. Тяжёлые
  фазы делегируются СУБ-АГЕНТАМ (оркестратор не читает весь код сам). Skill: `autocreate-implement`.
  В конце — spawn Сессии 3.
- **Сессия 3 — Finalize & release-ready (свежий subagent, Фазы 10.5 → 12)** — runtime+soak
  верификация, session-state, **release-eng PREP** (иконки/splash/версия/store-metadata — БЕЗ
  сборки AAB/APK), финальный отчёт. Оставляет проект ГОТОВЫМ к `/release-package`.
  Skill: `autocreate-finalize`.

```
Сессия 1 (autocreate)        Сессия 2 (autocreate-implement)     Сессия 3 (autocreate-finalize)
Фазы 1–3.7                   Фазы 4–10                            Фазы 10.5–12
концепт/ассеты/аудио/данные →[Agent]→ код/тесты/аудит/баланс →[Agent]→ runtime/prep/отчёт
        handoff-1.md                      autocreate-handoff.md
```

**Каждая сессия ОБЯЗАНА передать управление следующей через Agent tool в конце.**
Subagent вызывается БЕЗ `subagent_type`/`model`/`reasoning_effort` (full-history fork).

> **🤖 CODEX / среда без Agent tool:** если Agent tool НЕдоступен (OpenAI Codex CLI,
> Gemini CLI), конвейер НЕ останавливается. Вместо spawn: записать handoff-файл как обычно,
> затем **продолжить в этой же сессии** — прочитать SKILL.md следующей сессии и выполнять его.
> «5 параллельных агентов» Фазы 4 выполняются ПОСЛЕДОВАТЕЛЬНО (A→B→C→D→E) как persona-проходы.
> Полные правила адаптации — в `AGENTS.md` (корень репо), раздел «Execution Model».

**Тестирование: Chrome/Web (первичная платформа, не требует эмулятора).** Android/iOS — fallback.
**Сборка AAB/APK НЕ выполняется в конвейере** — финализация лишь делает проект release-ready
(иконки/splash/метаданные); артефакты собирает `/release-package` или `/release-engineering`.

### Что ОБЯЗАНО произойти в Сессии 1 (эта сессия, Фазы 1 → 3.7):

1. ✅ **Flutter-проект создан с нуля** (`flutter create --platforms web,android,ios`)
2. ✅ **Структура + Layout Archetype выбраны** (`design/structure.md`, `design/art-direction.md`)
3. ✅ **Все ассеты подготовлены** (Codex → до 12 unique PNG-источников GPT Images 2.0,
   `derive`/`code`/`reuse` без вызовов, максимум 2 technical recovery; chroma-key cutout через
   `tools/cutout.py`; не-Codex → SVG fallback; формат записан в `design/asset-format.md`,
   промпты и стиль набора — в `design/asset-prompts.md`)
4. ✅ **Реальное аудио синтезировано** (Фаза 3.5: `tools/synth_sfx.py` → `.wav` SFX + BGM)
5. ✅ **Asset Cohesion Review пройден** (Фаза 3.6: art-director, vision-ревью AR1–AR10,
   перегенерация бракованных → `design/asset-review.md`)
6. ✅ **ДАННЫЕ контента/экономики сгенерированы** (Фаза 3.7: `assets/data/*.json`, N>1 уровней)
7. ✅ **Handoff-1 записан** + **Сессия 2 запущена через Agent tool** (`autocreate-implement`)

### Что выполняют последующие сессии (резюме — детали в их skill-файлах):

- **Сессия 2** (`autocreate-implement`, Фазы 4–10): 5 агентов (A/B/C/D/E), wiring контента,
  интеграция, `dart analyze` 0 errors, feel-pass, тесты зелёные, UI-аудит (compliance), баланс
  по всей кривой, crash-prevention. Затем spawn Сессии 3.
- **Сессия 3** (`autocreate-finalize`, Фазы 10.5–12): runtime+soak верификация (Chrome CDP,
  auto-fix), **playtest** (Фаза 10.6 — реальная игровая сессия, проверки P1–P10),
  `active.md`, release-eng PREP (БЕЗ сборки AAB/APK), финальный отчёт.

### Запрещено в Сессии 1:

- ❌ Писать игровой код, экраны, сервисы — это Сессия 2 (5 агентов)
- ❌ Вызывать `flutter run/build/test`, `dart analyze`, `adb`, `emulator` — это задачи Сессий 2/3
- ❌ Делать stub-файлы или TODO-комментарии
- ❌ Отчитываться "игра готова" — написан только дизайн+ассеты+данные
- ✅ В конце ОБЯЗАТЕЛЬНО вызвать Agent tool для Сессии 2 — без этого конвейер НЕ завершён

### Финальный критерий успеха всего конвейера (после Сессии 3):

`ls production/runtime-screenshots/<ts>/` — ≥5 `.png` + `REPORT.md`;
`production/session-state/active.md` — актуальный runtime-verdict;
проект release-ready (иконки/splash/store-metadata готовы).
Для сборки/упаковки артефактов — `/release-package` (AAB+APK+архив) или `/release-engineering`
(signed AAB) отдельным явным запуском.

---

> **ANTI-SLOP**: Каждый экран и виджет — craft-level дизайн.
> Прочитайте `.claude/rules/anti-slop-design.md` перед началом работы.

> **QUALITY BAR**: эталон «профессионального уровня» — `.claude/docs/quality-bar.md`.
> Главный тест: «поставил бы игрок 4+ звезды, не зная, что игру сделал ИИ?»
> Конкретные пороги (TTF ≤ 10 с, отклик ≤ 100 мс, живое поле, масштабированный фидбек,
> 60 fps на win-celebration) проверяются фазами 3.6 / 6.5 / 8 / 10.6 — не на глаз.

> **КЛЮЧЕВОЕ ОТЛИЧИЕ ОТ MVP**: Это НЕ прототип. Это полная игра:
> - ВСЯ игровая логика работает (спины крутятся, очки считаются, уровни переключаются)
> - ВСЕ экраны связаны навигацией и данными
> - ВСЕ ассеты подключены и отображаются
> - ВСЕ кнопки реагируют на нажатия с правильными состояниями
> - ВСЕ анимации проигрываются — и в МЕНЮ/HUD, и ВНУТРИ геймплея: игровые элементы на поле
>   живые (появление, idle-дыхание, реакция на действие, смена состояния, anticipation→release)
> - Приложение НЕ крашится ни при каком сценарии использования
> - Тесты написаны и проходят

---

## Фаза 1 — Идея (Auto-Concept) [~2 мин]

Вызов логики `/auto-idea` для генерации концепции (пропустить если `--from-concept`).
Сохранение в `design/gdd/game-concept.md`.

**ВАЖНО**: Концепт ОБЯЗАН включать:
- **Reference Bar** — 2–3 НАЗВАННЫХ реальных хита этой категории (например для слота:
  Coin Master, Slotomania; для merge: 2048, Triple Town) и КОНКРЕТНО что мы заимствуем у
  каждой В ОЩУЩЕНИИ (тайминг остановки барабанов, вес каскада, ритм наград) — не в контенте.
  Это калибрует планку: игра соревнуется с настоящими играми, а не с другими демками.
  Плюс одна строка: чем НАША игра отличается от референсов (hook).
- **Design DNA** — визуальная идентичность ЭТОЙ игры (палитра/шрифты/shape/motion), обоснованная темой
- **Layout & Composition Direction** — выбранный Layout Archetype (L1–L6) и как он применён к экранам
- **Screen Map** — минимум 12 экранов с ПОЛНЫМ описанием каждого
- **Data Flow** — как данные перетекают между экранами (ValueNotifiers, callbacks)
- **Complete Game Loop** — полный цикл игры от старта до конца
- **All Edge Cases** — что происходит при нулевом балансе, макс выигрыше, паузе, и т.д.

---

## Фаза 2 — Flutter Project Bootstrap [~1 мин]

**Целевая платформа — Web/Chrome (primary).** Android и iOS — опциональные.

```bash
# Web должен быть первым в списке платформ
flutter create . --project-name game_app --platforms web,android,ios --org com.gamestudio

# Проверка что web-директория создана
if [[ ! -f web/index.html ]]; then
  echo "❌ Web-проект не создан — критическая ошибка, прекращаем"
  exit 1
fi

# Патч Android если директория существует (опциональный — не блокирует при отсутствии NDK)
if [[ -d android/app ]]; then
  python3 - <<'PY'
import re, pathlib

bg = pathlib.Path("android/app/build.gradle")
src = bg.read_text()

# ndkVersion — insert after "android {" if not already present
if "ndkVersion" not in src:
    src = src.replace("android {", 'android {\n    ndkVersion "27.0.12077973"', 1)

# minSdkVersion — bump to 21 if lower
src = re.sub(r'minSdkVersion\s+\d+', 'minSdkVersion 21', src)

bg.write_text(src)
print("✅ android/app/build.gradle: ndkVersion + minSdkVersion patched")
PY

  # Verify NDK is installed; install if sdkmanager is available (non-blocking)
  if command -v sdkmanager &>/dev/null; then
    sdkmanager --list_installed 2>/dev/null | grep -q "ndk;27" || \
      sdkmanager "ndk;27.0.12077973" 2>/dev/null && echo "✅ NDK 27 confirmed" || \
      echo "⚠️ NDK не установлен — Android APK будет пропущен, web build продолжается"
  fi
fi
```

Обновление `pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  flame: ^1.18.0
  flame_audio: ^2.1.0
  flame_svg: ^1.10.0    # Используется в SVG-режиме; в PNG-режиме (Codex) оставить в pubspec как fallback
  google_fonts: ^6.1.0
  shared_preferences: ^2.2.0
  # Примечание: в PNG-режиме (Codex) ассеты загружаются через Image.asset(), не flame_svg.
  # flame_svg остаётся в pubspec для совместимости, но Agent B читает design/asset-format.md
  # и выбирает Image.asset() (png) или SvgPicture.asset() (svg) соответственно.

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0

flutter:
  assets:
    - assets/images/sprites/
    - assets/images/ui/
    - assets/images/backgrounds/
    - assets/audio/sfx/
    - assets/audio/bgm/
    - assets/data/          # level/difficulty/economy configs (генерируются в Фазе 4.5)
  # ⚠️ НЕ хардкодить шрифты здесь. Шрифты выбираются в Design DNA каждой игры и
  # подключаются через пакет google_fonts (любой Google Font, без бандла .ttf).
  # ui-programmer вызывает GoogleFonts.<displayFont>() / GoogleFonts.<bodyFont>()
  # с конкретными шрифтами из секции Design DNA концепта.
```

> **АНТИ-SLOP (шрифты):** Orbitron/Rajdhani — НЕ дефолт студии. Display+body шрифты
> берутся из Design DNA концепта (`design/gdd/game-concept.md`) и различаются от игры
> к игре (уютная — Fredoka/Nunito; ретро — Press Start 2P; элегантная — Playfair/Lora;
> sci-fi — Orbitron; и т.д.). `google_fonts` уже в зависимостях — бандлить .ttf не нужно.

Создать базовые директории ассетов и дизайна:
```bash
mkdir -p assets/images/sprites assets/images/ui assets/images/backgrounds assets/audio/sfx assets/audio/bgm assets/data assets/branding design/gdd design/balance production/session-state
```

### 2.1 — Выбор архитектурной структуры проекта

Выбрать один из 5 вариантов структуры **до** создания lib-директорий. Вариант выбирается псевдослучайно по времени — каждая игра получает уникальную организацию кода. Затем создать `design/structure.md` с полным маппингом путей.

```bash
python3 - <<'PYEOF'
import time, pathlib

variant = (int(time.time()) % 5) + 1

variants = {
    1: dict(
        name="V1 — Layer Architecture",
        app="lib/app.dart",
        assets_constants="lib/assets.dart",
        game_dir="lib/game/",
        config="lib/game/game_config.dart",
        game_state="lib/models/game_state.dart",
        models_dir="lib/models/",
        systems_dir="lib/systems/",
        components_dir="lib/components/",
        screens_dir="lib/screens/",
        widgets_dir="lib/widgets/",
        audio_service="lib/audio/audio_service.dart",
        game_theme="lib/theme/game_theme.dart",
        animations="lib/theme/animations.dart",
        lib_dirs="lib/game lib/components lib/systems lib/models lib/screens lib/widgets lib/audio lib/theme",
    ),
    2: dict(
        name="V2 — Feature Slice",
        app="lib/core/app.dart",
        assets_constants="lib/assets.dart",
        game_dir="lib/gameplay/",
        config="lib/domain/game_config.dart",
        game_state="lib/domain/game_state.dart",
        models_dir="lib/domain/",
        systems_dir="lib/gameplay/systems/",
        components_dir="lib/gameplay/components/",
        screens_dir="lib/ui/screens/",
        widgets_dir="lib/ui/widgets/",
        audio_service="lib/services/audio_service.dart",
        game_theme="lib/core/theme/game_theme.dart",
        animations="lib/core/theme/animations.dart",
        lib_dirs="lib/core/theme lib/gameplay/components lib/gameplay/systems lib/ui/screens lib/ui/widgets lib/domain lib/services",
    ),
    3: dict(
        name="V3 — Presentation-Domain-Data",
        app="lib/app.dart",
        assets_constants="lib/assets.dart",
        game_dir="lib/domain/game/",
        config="lib/data/config/game_config.dart",
        game_state="lib/domain/models/game_state.dart",
        models_dir="lib/domain/models/",
        systems_dir="lib/domain/systems/",
        components_dir="lib/components/",
        screens_dir="lib/presentation/screens/",
        widgets_dir="lib/presentation/widgets/",
        audio_service="lib/data/services/audio_service.dart",
        game_theme="lib/presentation/theme/game_theme.dart",
        animations="lib/presentation/theme/animations.dart",
        lib_dirs="lib/presentation/screens lib/presentation/widgets lib/presentation/theme lib/domain/game lib/domain/systems lib/domain/models lib/data/config lib/data/services lib/components",
    ),
    4: dict(
        name="V4 — Module Architecture",
        app="lib/app.dart",
        assets_constants="lib/assets.dart",
        game_dir="lib/engine/",
        config="lib/engine/game_config.dart",
        game_state="lib/mechanics/models/game_state.dart",
        models_dir="lib/mechanics/models/",
        systems_dir="lib/mechanics/systems/",
        components_dir="lib/visuals/components/",
        screens_dir="lib/interface/screens/",
        widgets_dir="lib/interface/widgets/",
        audio_service="lib/infrastructure/audio/audio_service.dart",
        game_theme="lib/visuals/theme/game_theme.dart",
        animations="lib/visuals/theme/animations.dart",
        lib_dirs="lib/engine lib/mechanics/systems lib/mechanics/models lib/visuals/components lib/visuals/theme lib/interface/screens lib/interface/widgets lib/infrastructure/audio",
    ),
    5: dict(
        name="V5 — Vertical Slice",
        app="lib/bootstrap/app.dart",
        assets_constants="lib/bootstrap/assets.dart",
        game_dir="lib/arena/",
        config="lib/rules/config/game_config.dart",
        game_state="lib/rules/models/game_state.dart",
        models_dir="lib/rules/models/",
        systems_dir="lib/rules/systems/",
        components_dir="lib/arena/components/",
        screens_dir="lib/menus/",
        widgets_dir="lib/foundation/widgets/",
        audio_service="lib/foundation/audio/audio_service.dart",
        game_theme="lib/foundation/theme/game_theme.dart",
        animations="lib/foundation/theme/animations.dart",
        lib_dirs="lib/bootstrap lib/arena/components lib/rules/systems lib/rules/models lib/rules/config lib/hud lib/menus lib/foundation/audio lib/foundation/theme lib/foundation/widgets",
    ),
}

v = variants[variant]
content = f"""# Project Structure — Выбранный вариант

## Variant: {v['name']}

## Path Map

### App Bootstrap
- app: {v['app']}
- assets_constants: {v['assets_constants']}
- main: lib/main.dart

### Game Engine (Flame)
- game_dir: {v['game_dir']}
- config: {v['config']}

### State & Models
- game_state: {v['game_state']}
- models_dir: {v['models_dir']}

### Systems (Logic)
- systems_dir: {v['systems_dir']}

### Flame Components
- components_dir: {v['components_dir']}

### Flutter Screens
- screens_dir: {v['screens_dir']}

### Flutter Widgets
- widgets_dir: {v['widgets_dir']}

### Audio
- audio_service: {v['audio_service']}

### Theme
- game_theme: {v['game_theme']}
- animations: {v['animations']}

## Directories to Create
{v['lib_dirs']}
"""
pathlib.Path("design/structure.md").write_text(content)
print(f"✅ Structure variant {variant} ({v['name']}) → design/structure.md")
print(f"LIB_DIRS={v['lib_dirs']}")
PYEOF
```

Прочитать `design/structure.md` и создать lib-директории согласно выбранному варианту:

```bash
LIB_DIRS=$(python3 -c "
import re
txt = open('design/structure.md').read()
m = re.search(r'## Directories to Create\n(.+)', txt, re.DOTALL)
print(m.group(1).strip().split('\n')[0] if m else '')
")
mkdir -p $LIB_DIRS
echo "✅ lib/ директории созданы для выбранного варианта структуры"
```

**ОБЯЗАТЕЛЬНО**: после `flutter pub get` убедиться что нет ошибок зависимостей.

### 2.2 — Выбор Layout Archetype (композиция экранов)

Структура (2.1) меняет, ГДЕ лежат файлы. Layout Archetype меняет, КАК ВЫГЛЯДИТ компоновка
экранов (HUD сверху / нижняя консоль / плавающие углы / боковая рейка / сплит / карточки).
Это вторая ось разнообразия: вместе со структурой и Design DNA она гарантирует, что
игровые экраны НЕ выглядят одинаково от игры к игре.

Каталог: `.claude/docs/layout-archetypes.md` (L1–L6).

При `--from-concept` — взять архетип из секции **Layout & Composition Direction** концепта.
Иначе — выбрать псевдослучайно и записать в `design/art-direction.md`:

```bash
python3 - <<'PYEOF'
import time, pathlib

archetypes = {
    "L1": "Classic Stack — верхний HUD-бар, поле в центре, управление+действие снизу",
    "L2": "Bottom Command Deck — поле edge-to-edge сверху, плотная нижняя консоль с HUD+действием",
    "L3": "Floating Corners — full-bleed поле, плавающие чипы по углам, плавающая кнопка действия",
    "L4": "Side Rail — вертикальная рейка управления/HUD сбоку, поле занимает остальное",
    "L5": "Split Panel — две явные зоны (≈60% поле / ≈40% инфо-панель с отдельной поверхностью)",
    "L6": "Card / Sheet Stack — контент на скруглённых карточках/листах, тонкая пилюля HUD",
}
keys = list(archetypes)
layout = keys[(int(time.time() // 7)) % len(keys)]

content = f"""# Art Direction — выбранное направление

## Layout Archetype: {layout}
{archetypes[layout]}

Полное описание композиции (меню, игровой экран, размещение действия, оверлеи, переходы):
см. `.claude/docs/layout-archetypes.md` → раздел {layout}.

## Как применять
- **Layout Archetype ({layout})** определяет КОМПОЗИЦИЮ всех экранов.
- **Design DNA** (из `design/gdd/game-concept.md`) определяет ВИД (палитра/шрифты/формы/motion).
- ui-programmer реализует пересечение: компоновка по {layout}, одетая в DNA игры.
- Инварианты UX (досягаемость большого пальца, 48×48, SafeArea, фокус на поле) соблюдаются
  в любом архетипе.

> Не применяй один и тот же art-стиль (неон/стекло/тёмная тема) ко всем играм — стиль из DNA.
"""
pathlib.Path("design/art-direction.md").write_text(content)
print(f"✅ Layout archetype {layout} → design/art-direction.md")
PYEOF
```

Прочитать `design/art-direction.md` и передать выбранный архетип в контракт Agent B (Фаза 4).

---

## Фаза 3 — Asset Generation & Validation [~5 мин]

### Формат ассетов — автоматический выбор (без вопросов)

Формат определяется автоматически по среде выполнения. Никакого ввода от пользователя не требуется.

```bash
# Определение среды: Codex → PNG (GPT Image 2 tool/API → fallback), иначе → SVG fallback
IS_CODEX=0
if [[ -n "${CODEX:-}" ]] || [[ -n "${CODEX_ENV:-}" ]] || [[ "${AGENT_PLATFORM:-}" == "codex" ]] || \
   [[ -d ".codex" ]] || [[ "${IMAGE_GENERATION_AVAILABLE:-}" == "1" ]]; then
  IS_CODEX=1
fi

if [[ "$IS_CODEX" == "1" ]]; then
  ASSET_FORMAT="png"
  ASSET_GENERATOR="gpt-image-2:built-in-or-tools/gpt_image.py"
  ASSET_RENDER_PROFILE="realistic material-grounded 3D/product render"
  echo "🎨 Codex detected → PNG mode (GPT Image 2 tool/API bridge)"
else
  ASSET_FORMAT="svg"
  ASSET_GENERATOR="svg-code"
  ASSET_RENDER_PROFILE="design-dna svg fallback"
  echo "🎨 Non-Codex environment → SVG fallback mode"
fi
```

> **Правила переключения:**
> - **Codex app** → PNG через built-in GPT Image 2.
> - **Headless Codex CLI** → PNG через `tools/gpt_image.py` (`gpt-image-2`);
>   `OPENAI_API_KEY` в web-service инжектируется автоматически. Отсутствие built-in tool
>   не считается сбоем и не разрешает SVG.
> - **GPT Images/default** → только после документированного технического провала GPT Image 2.
> - **Не-Codex** (Claude Code, CLI, другое) → SVG (ручная генерация кодом, без внешних API)
> - Явный `--png` всегда форсирует PNG, `--svg` всегда форсирует SVG, regardless of environment
> - Записать выбранный формат в `design/asset-format.md` для Session 2

```bash
mkdir -p design
cat > design/asset-format.md << EOF
# Asset Format — автоматически выбран

format: ${ASSET_FORMAT}
is_codex: ${IS_CODEX}
generator: ${ASSET_GENERATOR}
default_render_profile: ${ASSET_RENDER_PROFILE}
timestamp: $(date -Iseconds)

## Что это значит для Session 2
- Если format=png: ассеты в assets/images/sprites/*.png, ui/*.png, backgrounds/*.png
  Agent B использует Image.asset() / деко через Image, НЕ flame_svg
- Если format=svg: ассеты в assets/images/sprites/*.svg, ui/*.svg, backgrounds/*.svg
  Agent B использует SvgPicture / flame_svg
EOF
echo "✅ Asset format → design/asset-format.md"
```

В PNG-режиме создать бюджетный манифест до первого вызова. Он запрещает дубли prompt-ов и
фиксирует источник каждого производного ассета:

```bash
cat > design/asset-manifest.md << 'EOF'
# Asset Manifest — Budgeted GPT Images 2.0

budget: unique_sources=12, technical_recovery_calls=2

| logical_id | class | target_path | prompt_sha256 | source_id | attempts | validation | status |
|------------|-------|-------------|---------------|-----------|----------|------------|--------|
EOF
```

---

### PNG Генерация (режим по умолчанию в Codex)

Когда `ASSET_FORMAT=png`, все ассеты генерируются через **GPT Image 2**. Сначала использовать
built-in image generation Codex, если tool действительно доступен. В headless `codex exec`
без такого tool немедленно использовать `python3 tools/gpt_image.py`; это основной транспорт,
а не fallback. Если GPT Image 2 через доступный транспорт не сработал или не дал валидный PNG,
зафиксировать ошибку и только затем рассматривать **GPT Images / default Codex image
generation**. Следовать логике `/generate-png-asset --from-concept`.

Перед первой дорогой генерацией в headless CLI выполнить дешёвый access probe:

```bash
python3 tools/gpt_image.py probe
```

Для каждого `generate`-источника сохранить полный prompt в отдельный UTF-8 файл и выполнить:

```bash
python3 tools/gpt_image.py generate \
  --prompt-file design/prompts/<logical_id>.txt \
  --out assets/images/sprites/<logical_id>.png \
  --size 1024x1024 \
  --quality high
```

**КРИТИЧЕСКИ**: Качество PNG = реалистичность + достоверность концепту. НЕ генерировать
абстрактные плоские значки.

#### Codex GPT Images 2.0 default profile (ОБЯЗАТЕЛЬНО)

- **Генератор:** built-in image generation Codex / GPT Image 2; если tool не экспонирован —
  `tools/gpt_image.py` с жёстко заданной моделью `gpt-image-2`. Fallback — GPT Images /
  default Codex image generation с тем же prompt только при документированной
  API/validation ошибке. Не использовать SVG, Pollinations, Gemini,
  Google API, remove.bg API или запросы ключей в Codex-пути, пока не провалились оба Codex-пути.
- **Один источник класса `generate` = один image-generation вызов.** Не просить sprite sheet, atlas, сетку из
  нескольких предметов или набор объектов в одном изображении.
- **Сначала манифест и кэш:** нормализовать prompt и записать SHA-256. Если совпадающий
  валидный `generate` уже есть, использовать его как `reuse`; UI/VFX/варианты сначала
  классифицировать как `code` или `derive`, а не отправлять в image generation.
- **Дефолтный стиль:** realistic/material-grounded 3D или product-render для игровых ассетов:
  реальные материалы, правдоподобные отражения/roughness, единый key light сверху-слева,
  лёгкий rim light, чистый силуэт. Flat/pixel/lineart разрешены только если Design DNA явно
  требует именно этот стиль; даже тогда должны быть единые свет, палитра и читаемость.
- **Запрещённый результат:** flat vector icon, emoji/sticker, logo, generic casino/neon,
  text baked into image, sprite sheet, random scene behind a simple object, inconsistent light,
  ground shadow that мешает вырезанию. Сначала исправить локально всё, что не является
  дефектом исходной генерации; для дефекта источника доступен один recovery GPT Images 2.0
  на `logical_id` и не более двух по игре.
- **Ledger:** создать `design/asset-prompts.md` и записывать для каждого ассета:
  `name`, `type`, `path`, `subject identity`, `material`, `lighting anchor`, `render style`,
  полный prompt, выбранный key colour, post-processing (`cutout.py`), validation verdict.

```bash
cat > design/asset-prompts.md << 'EOF'
# Asset Prompts — GPT Images 2.0 → GPT Images fallback

| name | type | path | subject identity | material | lighting anchor | render style | prompt | post-processing | verdict |
|------|------|------|------------------|----------|-----------------|--------------|--------|-----------------|---------|
EOF
```

Базовый prompt для каждого простого ассета:

```text
Highly detailed realistic mobile game asset of [SUBJECT IDENTITY FROM CONCEPT],
single hero object centered, [MATERIAL/TEXTURE] with believable reflections,
roughness and small surface imperfections, [RENDER STYLE FROM DNA OR DEFAULT REALISTIC 3D]
render, shared soft top-left key light and subtle rim light, rich [DNA PALETTE] colors,
crisp clean silhouette readable at 64 px, sharp focus, premium studio product shot,
flat solid single-colour [KEY COLOUR] background, no gradient, no vignette, subject fully
inside frame, transparent-ready cutout, no scene, no ground shadow, no shadow on the
background, no text, no border, no logo, no sprite sheet, 1024x1024 PNG.
[TYPE_DETAILS]
```

Fallback, если GPT Images 2.0 не сработал:

```text
Только при технической ошибке, отсутствии файла или невалидном PNG.
Повторить тот же prompt через GPT Images / default Codex image generation.
Не менять ключевой фон на прозрачный: плоский ключевой цвет нужен для стабильного cutout.
```

#### Промпт-инжиниринг (обязательно для КАЖДОГО ассета)

Для КАЖДОГО ассета вывести из концепта (`design/gdd/game-concept.md`) + Design DNA:
1. **Subject identity** — что конкретно за объект в мире игры
2. **Material/texture** — металл/стекло/камень/дерево/неон
3. **Lighting** — единый для ВСЕГО набора источник
4. **Render style** из DNA — фотореалистичный 3D / glossy 2.5D / рисованный / pixel
   (один стиль для ВСЕГО набора — консистентность важнее красоты одного ассета)

См. раздел «Realism & concept fidelity» в `generate-png-asset/SKILL.md`, но для
`/autocreate` профиль выше имеет приоритет: realistic PNG через GPT Images 2.0 по умолчанию.

#### Спрайты PNG (`assets/images/sprites/`)
- Минимум 5-8 игровых элементов (символы барабана, карты, фишки, шары, мины, капсулы)
- Каждый: 1024x1024 PNG, затем при необходимости resize до 256x256 для runtime
- **Генерация**: каждый действительно уникальный игровой силуэт — класс `generate` и один
  вызов GPT Images 2.0; совпадающий валидный SHA-256 — `reuse`. Цвет, кадрирование и idle-
  варианты — только `derive`, если это не меняет смысл исхода
- **Фон**: просить плоский ключевой цвет (chroma key, по умолчанию `pure magenta #FF00FF`;
  если в палитре есть пурпур/розовый — `pure green #00FF00`), без теней/градиентов/сцены,
  затем `tools/cutout.py`. Белый фон использовать НЕЛЬЗЯ, если у объекта есть белые или
  светлые области — они сольются с фоном и получатся дыры
- Стиль рендера и детализация — из Design DNA, единый для всего набора

#### UI Elements (`assets/images/ui/` и Flutter)
- Кнопки, рамки, панели, разделители, системные иконки, тени, glow и VFX — класс `code`:
  реализовать Flutter/SVG и темой из Design DNA, без image-generation вызовов.
- Растровый UI допустим только для действительно уникальной иллюстративной детали, которая
  не воспроизводится кодом; она занимает отдельный `generate` budget slot.
- Текст никогда не запекать в изображение.

#### Фоны PNG (`assets/images/backgrounds/`)
- По умолчанию один полноэкранный источник `background_game.png`; меню получает отдельную
  композицию из него через overlay/crop/параллакс (`reuse`/`code`).
- `background_menu.png` генерировать только если меню требует другого мира или композиции,
  а не просто другого цветового тона; это второй и последний полноэкранный source slot.

#### Удаление фона (ОБЯЗАТЕЛЬНО для sprites/icons/symbols)

Применяется ТОЛЬКО к: `symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`.
НЕ применяется к: `background_*`, `ui_panel`, полноэкранным сценам.

> **Единственный способ вырезания — `python3 tools/cutout.py`.** Ручной
> `magick -fuzz ... -transparent white` ЗАПРЕЩЁН: это глобальный матч по цвету, он
> пробивает дыры в белых бликах/глазах/хроме, даёт бинарную (рваную) альфу и оставляет
> белый ореол. cutout.py заливает фон от границы кадра (внутренние светлые пиксели не
> трогает), считает дробную альфу на краю, снимает цвет фона с полупрозрачных пикселей,
> убирает despill, обрезает по контенту и нормализует кадр. `rembg`, если установлен,
> используется им как ассист.

```bash
# Функция вырезания фона — вызывать после генерации каждого sprite/icon/symbol PNG
remove_bg_if_needed() {
  local INPUT_PNG="$1"
  local ASSET_TYPE="${2:-sprite}"  # sprite|symbol|icon|wild|scatter|tile|item|ui|background|ui_panel
  python3 tools/cutout.py "${INPUT_PNG}" --type "${ASSET_TYPE}"
}
```

Ненулевой код возврата = проверить исходник и выбранный ключ, затем перевырезать из
исходника/нормализовать кадр. Если источник действительно непригоден, потратить один
recovery-slot на тот же `logical_id` через GPT Images 2.0; не использовать fallback только
из-за ошибки cutout.

Проверить весь набор одной командой в конце Фазы 3:

```bash
python3 tools/cutout.py --dir assets/images/sprites --check
python3 tools/cutout.py --dir assets/images/ui --check
```

#### Post-Generation Validation (PNG)

**ОБЯЗАТЕЛЬНО** после генерации всех PNG:
1. Проверить что каждый файл валидный PNG (`file *.png | grep "PNG image"`)
2. Проверить что sprites/icons имеют альфа-канал (прозрачный фон)
3. Проверить что каждый простой ассет НЕ выглядит как flat/emoji/clipart/logo; сначала
   исправить локально/переклассифицировать, а дефект исходника исправить одним GPT Images 2.0
   recovery. GPT Images/default допускается лишь при техническом сбое GPT Images 2.0
4. Проверить что `design/asset-prompts.md` содержит prompt+style ledger для каждого PNG
5. Проверить что `design/asset-manifest.md` содержит класс, SHA-256, попытки и validation
   для каждого `generate`/`derive`/`reuse` элемента
6. Проверить что все файлы, указанные в коде (`lib/assets.dart`), физически существуют
7. Проверить что Codex PNG-режим НЕ создал `.svg` в `assets/images/**`. SVG здесь означает
   ошибочный fallback; удалить из манифеста/кода и перегенерировать нужный PNG напрямую через
   GPT Images 2.0 в пределах recovery; GPT Images/default допустим лишь при техническом сбое.
8. Запустить `flutter pub get` для валидации путей ассетов

```bash
# Валидация PNG-ассетов
echo "━━━ Валидация PNG ассетов ━━━"
ERRORS=0
for png in assets/images/sprites/*.png assets/images/ui/*.png assets/images/backgrounds/*.png; do
  [ -f "$png" ] || continue
  if ! file "$png" | grep -q "PNG image"; then
    echo "✗ Невалидный PNG: $png"
    ERRORS=$((ERRORS + 1))
  else
    SIZE=$(ls -lh "$png" | awk '{print $5}')
    echo "✓ $png ($SIZE)"
  fi
done
if find assets/images -name "*.svg" -print -quit | grep -q .; then
  echo "✗ PNG-режим, но найдены SVG в assets/images/**. Не использовать SVG→PNG как путь autocreate."
  ERRORS=$((ERRORS + 1))
fi
[ "$ERRORS" -eq 0 ] && echo "✅ Все PNG валидны" || echo "❌ $ERRORS невалидных файлов"
```

---

### SVG Генерация (fallback для не-Codex среды)

Используется когда `ASSET_FORMAT=svg` (не-Codex среда, или явный `--svg`).

**КРИТИЧЕСКИ**: Каждый SVG ОБЯЗАН быть валидным и отрисовываемым.

#### Спрайты (`assets/images/sprites/`)
- Минимум 5-8 игровых элементов (символы барабана, карты, фишки, шары, мины, капсулы)
- Каждый: 96x96 SVG с `viewBox="0 0 96 96"`
- **Стиль рендера — из Design DNA**: объёмный (градиенты + блики) ИЛИ плоский/flat ИЛИ
  outline/lineart — что подходит миру игры. Дзен/минимал может быть намеренно плоским.
- **Главное — консистентность набора**: один стиль освещения и один уровень детализации
  во ВСЕХ спрайтах. Нельзя мешать flat и фотореалистичные в одном сете.

#### UI Elements (`assets/images/ui/`)
- `ui_action_button.svg` — основное действие; форма из shape language DNA (НЕ обязательно трапеция/скос)
- `ui_frame.svg` — рамка игрового поля
- `ui_panel.svg` — панель управления / ставок
- `ui_separator.svg` — декоративный разделитель
- `ui_icon_sound.svg` — иконка звука
- `ui_icon_settings.svg` — иконка настроек
- `ui_icon_info.svg` — иконка помощи
- Иконки — в едином стиле и одной толщине обводки (Craft Fundamentals)

#### Фоны (`assets/images/backgrounds/`)
- `background_menu.svg` — фон меню (паттерн/градиент/сцена — из DNA; яркость тоже из DNA, не «всегда тёмный»)
- `background_game.svg` — фон игрового экрана (не отвлекает от поля; контраст к элементам HUD)

### Post-Generation Validation (SVG)

**ОБЯЗАТЕЛЬНО** после генерации всех SVG:
1. Проверить что каждый файл начинается с `<svg` и содержит `</svg>`
2. Проверить что `viewBox` определён в каждом файле
3. Проверить что все файлы, указанные в коде (`lib/assets.dart`), физически существуют
4. Запустить `flutter pub get` для валидации путей ассетов

---

## Фаза 3.5 — Real Audio Synthesis [~30 сек]

> **Зачем.** Раньше `AudioService` «graceful-fail» на отсутствующих файлах — игра выходила
> БЕЗ ЗВУКА. Полная игра обязана звучать. `tools/synth_sfx.py` синтезирует НАСТОЯЩИЕ
> playable `.wav` (16-bit/44.1kHz, только stdlib — без внешних API/ffmpeg) для каждого события
> Sound Design Map. Mood берётся из Design DNA (Emotional Core).

```bash
# Mood выводится из концепта (напряжённое/уютное/эпичное/...). Если не определить — bright.
python3 tools/synth_sfx.py --from-concept \
  --sfx-dir assets/audio/sfx --bgm-dir assets/audio/bgm 2>&1 | tail -12

# Валидация: 9 файлов созданы и непустые
ls -1 assets/audio/sfx/*.wav assets/audio/bgm/*.wav 2>/dev/null | wc -l
```

Генерируемые файлы (используй ровно эти имена в `audio_assets`):
`sfx_button, sfx_navigate, sfx_action, sfx_coin, sfx_error, sfx_win_small, sfx_win_big,
sfx_win_mega` (в `assets/audio/sfx/`) + `bgm_main` (в `assets/audio/bgm/`).

> **Контракт для Agent D (Фаза 4):** `audio_assets.dart` ссылается на `.wav` по этим путям;
> `AudioService` всё равно оборачивает воспроизведение в try-catch (на случай платформенных
> ограничений), но файлы РЕАЛЬНО существуют. Если нужен другой mood — перезапусти с `--mood`.

---

## Фаза 3.6 — Asset Cohesion Review (art-director) [~4 мин]

> **Зачем.** Генерация «один промпт = один ассет» неизбежно даёт разнобой: разный свет,
> разная детализация, чужие хюи, нечитаемые в 64 px силуэты, белые ореолы после вырезания.
> Игрок видит это за 3 секунды. Эта фаза — vision-ревью ВСЕГО набора как ЕДИНОГО целого
> и перегенерация только бракованных.

Выполнить runbook `.claude/skills/asset-review/SKILL.md` (роль: `art-director`,
`.claude/agents/art-director.md`):

1. Контактные листы (montage) + **обязательный 64px-лист** (как видит игрок).
2. Vision-оценка по критериям **AR1–AR10** (единый стиль/свет/детализация, палитра из DNA,
   читаемость в 64 px, чистая альфа, единый стиль иконок, фон уступает полю, предмет
   опознаётся, нет AI-артефактов).
3. `design/asset-review.md` — вердикт по каждому ассету.
4. Сначала локальная коррекция ТОЛЬКО FAIL-ассетов. Для дефекта источника допустим один
   recovery через GPT Images 2.0 на `logical_id`, не более двух по игре; GPT Images/default
   доступен только при техническом сбое. SVG править кодом.

**Критерий выхода:** `design/asset-review.md` существует с вердиктом PASS (или REGENERATE
с выполненной перегенерацией); все спрайты/иконки с подтверждённой альфой.

---

## Фаза 3.7 — Content & Economy Data (DATA only) [~3 мин]

> **Сессия 1.** Контент полной игры — это ДАННЫЕ, и они генерируются здесь, ДО кода: агенты
> Сессии 2 будут строить логику против уже готовых конфигов. Объём — из **Production Plan**
> концепта (`design/gdd/game-concept.md` → Секция 2.5). Это дизайн-выход, кода не требует.

Создать в `assets/data/` (зеркало для ревью — в `design/balance/`):

Состав зависит от категории игры (блок **Классификация** концепта):

- **ВСЕГДА** → конфиг математической модели в `design/balance/` по категории:
  `rtp-config.json` (C1/C2) | `economy-config.json` (C3) | `gacha-config.json` (C4) |
  `run-config.json` (C5) | `physics-config.json` (C6).
  Эталоны, проходящие прогон «из коробки»: `.claude/docs/templates/math-configs/`.
- **C1/C2** → `assets/data/bet-tiers.json` — уровни ставок, лимиты, параметры бонус-режимов.
- **C3** → `assets/data/stage-config.json` — лестница анлоков/сезонов доски, **N > 1** записей:
  `id`, цена, награда, что открывает.
- **C4** → `assets/data/banners.json` — баннеры (**N > 1**), их пулы предметов и ротация.
- **C5** → `assets/data/run-config.json` — пороги раундов, каталог модификаторов (≥3), цены магазина.
- **C6** → `assets/data/board-config.json` — раскладки поля/корзин (**N > 1** рисковых профилей).
- **economy** → `assets/data/economy-config.json` — стартовый баланс валюты, цены каталога
  магазина (скины/темы/бустеры/наборы/remove-ads), награды за уровни/дейли/достижения.
- **modes** → отразить в концепте/handoff список 2–3 режимов (Classic + Endless/Time-Attack/Daily).

Валидация:
```bash
for f in assets/data/level-config.json assets/data/economy-config.json; do
  [ -f "$f" ] && python3 -c "import json,sys; d=json.load(open('$f')); print('$f OK', (len(d) if isinstance(d,list) else 'obj'))" \
    || echo "⚠️ нет $f (если категория того требует — создать)"
done
```

> Числа держим в JSON (контент) — один источник правды; `GameConfig` (Сессия 2) их загружает,
> не дублирует. Кривую при желании просчитывает `game-mathematician`, но в Сессии 1 достаточно
> разумных значений из Production Plan; полная балансировка — Фаза 9 (Сессия 2).

---

## Фаза 3.8 — Session 1 Handoff & Spawn Session 2 [~1 мин]

**ЭТО ПОСЛЕДНЯЯ ФАЗА СЕССИИ 1.** Реализация (Фазы 4–10) идёт в Сессии 2 (subagent с чистым
контекстом), НЕ здесь.

### 3.8.1 — Записать handoff-1

Создать `production/session-state/autocreate-handoff-1.md`:

```markdown
# AutoCreate Handoff 1 — Pre-production завершена (Сессия 1)

**Время**: [ISO timestamp]
**Следующий шаг**: subagent выполняет `.claude/skills/autocreate-implement/SKILL.md` (Сессия 2)

## Метаданные игры
- Название / Категория (C1–C6) / Архетип (A–AF) / Матмодель (M1–M6): [...]
- Структура: [V1–V5 из design/structure.md] | Layout: [L1–L6 из design/art-direction.md]
- Audio mood: [mood] (9 .wav в assets/audio/)
- Package: com.gamestudio.[name]

## Готово в Сессии 1
- [x] Концепт + Production Plan: design/gdd/game-concept.md
- [x] Bootstrap: flutter create (web,android,ios), pubspec, директории
- [x] Структура+Layout: design/structure.md, design/art-direction.md
- [x] Ассеты: [N] [PNG/SVG] в assets/images/** (формат: [png/svg], см. design/asset-format.md)
- [x] [Если PNG] Фон удалён для sprites/icons через `tools/cutout.py`, `--check` по всем папкам чист
- [x] Аудио: 9 .wav (assets/audio/sfx + bgm)
- [x] Asset Cohesion Review: design/asset-review.md — вердикт [PASS / N перегенерировано]
- [x] Контент-данные: assets/data/*.json — [N] уровней, режимы [список], economy

## Задачи Сессии 2 (autocreate-implement, Фазы 4–10)
- [ ] 4: 5 агентов (A/B/C/D/E) пишут код + мета-системы
- [ ] 4.5: wiring контента (level/mode select ↔ data) | 5: интеграция (18 связей)
- [ ] 6: dart analyze 0 errors | 6.5: feel-pass | 7: тесты зелёные
- [ ] 8: UI-аудит (compliance) | 9: баланс по кривой | 10: crash-prevention
- [ ] 10.7: spawn Сессии 3 (autocreate-finalize)

## Ссылки
- Спецификации Фаз 4–10: `.claude/skills/autocreate/SKILL.md` (этот файл, ниже)
- Драйвер Сессии 2: `.claude/skills/autocreate-implement/SKILL.md`
```

### 3.8.2 — Spawn Сессии 2 через Agent tool

**ОБЯЗАТЕЛЬНО** (без `subagent_type`/`model`/`reasoning_effort`):

```
Agent(
  description="AutoCreate Session 2: implementation (phases 4–10)",
  prompt="""
Ты — Сессия 2 конвейера /autocreate (чистый контекст). Pre-production (Сессия 1) завершена.

ПЕРВЫМИ ДЕЙСТВИЯМИ прочитай:
1. production/session-state/autocreate-handoff-1.md — что уже готово
2. .claude/skills/autocreate-implement/SKILL.md — твой план Сессии 2 (выполняй его)
3. design/structure.md, design/art-direction.md, design/gdd/game-concept.md

ТВОЯ ЗАДАЧА: выполнить Фазы 4 → 10 (как описано в .claude/skills/autocreate/SKILL.md),
ДЕЛЕГИРУЯ тяжёлые фазы суб-агентам (см. autocreate-implement) чтобы не истощить контекст.
КРИТЕРИЙ: dart analyze 0 errors, flutter test зелёные, UI-аудит пройден, баланс ок,
crash-prevention 20/20. В конце (Фаза 10.7) — записать autocreate-handoff.md и
запустить Сессию 3 (autocreate-finalize) через Agent tool.

НЕ переписывай концепт/ассеты/аудио/данные Сессии 1 — они зафиксированы (можно только
дополнять GameConfig значениями из assets/data/*.json).
"""
)
```

После возврата subagent-а Сессии 2 — вернуть пользователю его итог (который, в свою очередь,
содержит итог Сессии 3). Если упал — сообщить причину и команду ручного перезапуска:
`/autocreate-implement` (в новой conversation).

---

> **Фазы 4–10 ниже ВЫПОЛНЯЮТСЯ В СЕССИИ 2** (`autocreate-implement`), а не в этой conversation.
> Они оставлены здесь как канонические спецификации, на которые ссылается драйвер Сессии 2.

---

## Фаза 4 — Complete Game Implementation (FIVE parallel agents) [~15 мин]

> **КЛЮЧЕВОЕ ПРАВИЛО**: Каждый агент получает ПОЛНЫЙ концепт из `design/gdd/game-concept.md`
> и ПОЛНЫЙ список ассетов. Агенты ОБЯЗАНЫ использовать ОДИНАКОВЫЕ имена классов, типы и интерфейсы.

> **Конвейер использует 6 агентских проходов:** 5 параллельных здесь (A mechanics, B ui,
> C juice, D sound, **E meta-systems**) + 1 выделенный **Gameplay Feel Pass** (Фаза 6.5,
> juice-artist), который оживляет сами игровые компоненты на поле уже на чистом,
> компилирующемся коде. Это разделение намеренное: параллельные агенты строят каркас,
> feel-pass добавляет «жизнь» в геймплей без коллизий при параллельной записи.
>
> **Чтобы 5 агентов не писали в одни файлы:** у каждого — свои директории (A: game/systems/
> components/models; B: screens/widgets/theme/app/assets; C: components/vfx; D: audio;
> E: services/save/economy/progression). Пересечения (game_config.dart, contracts) — только
> ЧИТАЮТСЯ агентами B/C/D/E, ПИШЕТ их Agent A. Мета-сервисы Agent E подключаются к игре в
> Фазе 5 (wiring), а не правкой файлов Agent A.

> **⚠️ СОВМЕСТИМОСТЬ АГЕНТОВ**: При вызове `Agent(...)` НЕ указывай `subagent_type`, `model`
> или `reasoning_effort` — эти параметры несовместимы с full-history fork и вызовут ошибку.
> Используй только `description` и `prompt`.

> **⚠️ СТРУКТУРНО-ЗАВИСИМЫЕ ПУТИ**: Прочитать `design/structure.md` ПЕРЕД формированием
> промптов для агентов. Пути файлов в описаниях агентов ниже — это примеры для V1 (Layer).
> **В промпты агентов подставить ФАКТИЧЕСКИЕ пути** из `design/structure.md`:
>
> | Категория      | Ключ в structure.md | Агент |
> |----------------|---------------------|-------|
> | FlameGame файл | game_dir            | A     |
> | GameConfig     | config              | A     |
> | GameState      | game_state          | A     |
> | Systems        | systems_dir         | A     |
> | Components     | components_dir      | A, C  |
> | Screens        | screens_dir         | B     |
> | Widgets        | widgets_dir         | B     |
> | App/routes     | app                 | B     |
> | Assets consts  | assets_constants    | B     |
> | Theme          | game_theme          | B     |
> | Animations     | animations          | B     |
> | AudioService   | audio_service       | D     |
> | Services (save/economy/progression/achievements/analytics/ads/iap/remote-config) | директория рядом с `audio_service` (`services/`/`data/`/`infrastructure`/`foundation` по варианту) | E |
>
> Агенты получают `lib/contracts.md` с заполненными путями и читают его первым действием.

### Контракт между агентами (определить ДО запуска)

**ПЕРВЫМ ДЕЙСТВИЕМ** прочитать `design/structure.md` — там хранится выбранный в Фазе 2 вариант структуры и точные пути ко всем файлам. Затем создать файл контракта `lib/contracts.md` (временный, удалить в конце), подставив пути из `design/structure.md`:

```markdown
## Shared Types
- GameState sealed class: IdleState, PlayingState, AnimatingState, WinState, GameOverState, PausedState
- ValueNotifiers: balance (int), bet (int), isSpinning/isPlaying (bool), score (int), currentState (GameState)
  + мета: coins (int), currentLevel (int), currentMode (enum), achievementUnlocked (callback/notifier)
- Game class name: [GameName]Game extends FlameGame
- World class name: [GameName]World extends World with HasCollisionDetection
- Config class name: GameConfig (static constants)

## Meta-Services (Agent E) — интерфейсы, которые ЧИТАЮТ Agent A/B
- SaveService    — единый persistence (versioned schema + migration), try-catch
- EconomyService — coins, shop, isUnlocked/purchase (цены из GameConfig)
- ProgressionService — открытые уровни, звёзды, recordResult
- AchievementService — разблокировка по событиям, награда через Economy
- AnalyticsService (abstract) + NoOp/Debug; AdService (abstract) + NoOp;
  IapService (abstract) + NoOp; RemoteConfigService (abstract) + Local(defaults из GameConfig)
- Точки вызова этих сервисов в геймплее/навигации расставляются в Фазе 5 (wiring)

## Structure Variant
[Вставить: Variant из design/structure.md, например "V3 — Presentation-Domain-Data"]

## Layout Archetype
[Вставить: L1–L6 из design/art-direction.md, например "L2 — Bottom Command Deck".
Agent B компонует ВСЕ экраны по этому архетипу — см. .claude/docs/layout-archetypes.md]

## Asset Format
[Вставить из design/asset-format.md: format=png|svg, generator, render profile]
- format=png: использовать Image.asset и .png пути; не использовать SvgPicture/flame_svg в коде.
- format=svg: использовать SvgPicture/flame_svg fallback.
- В Codex `/autocreate` PNG создаются напрямую через GPT Images 2.0 / GPT Images fallback из концепта, НЕ через
  промежуточный SVG→PNG.

## File Paths (EXACT) — из design/structure.md
- App: [app из structure.md]
- Assets constants: [assets_constants из structure.md]
- Main: lib/main.dart
- Game: [game_dir из structure.md][name]_game.dart
- World: [game_dir из structure.md][name]_world.dart
- Config: [config из structure.md]
- State: [game_state из structure.md]
- Models dir: [models_dir из structure.md]
- Systems dir: [systems_dir из structure.md]
- Components dir: [components_dir из structure.md]
- Screens dir: [screens_dir из structure.md]
- Widgets dir: [widgets_dir из structure.md]
- Audio service: [audio_service из structure.md]
- Theme: [game_theme из structure.md]
- Animations: [animations из structure.md]
```

**КРИТИЧЕСКИ**: все агенты ОБЯЗАНЫ читать `lib/contracts.md` ПЕРВЫМ действием и создавать все файлы по УКАЗАННЫМ путям — не по путям из памяти или примерам из других документов.

### Agent A — mechanics-programmer (Core Game Logic):

**Prompt ОБЯЗАН включать**: Полный концепт, контракт типов, список ассетов.

Создаёт ВСЮ рабочую игровую логику:

- `lib/game/[name]_game.dart` — FlameGame с ПОЛНОЙ инициализацией
  - Создаёт World, Camera, все ValueNotifiers
  - Методы: startGame(), performAction() (spin/move/tap), pause(), resume()
  - Обработка всех GameState переходов
  - Подключение к overlays для Flutter UI
- `lib/game/[name]_world.dart` — World с HasCollisionDetection
  - Все игровые компоненты добавляются здесь
  - Метод reset() для перезапуска
- `lib/game/game_config.dart` — ВСЕ константы без исключения
  - Размеры, скорости, множители, тайминги, лимиты
  - Пороги для Small/Big/Mega Win
  - Минимальная/максимальная ставка
  - Начальный баланс
- `lib/systems/` — логика по категории (во ВСЕХ: `weighted_rng.dart` на `Random.secure()`
  + резолвер исхода, вычисляющий результат ДО анимации):
  - **C1**: `weighted_rng.dart`, `payline_evaluator.dart`, `spin_resolver.dart`
  - **C2**: `round_resolver.dart` (seed+nonce), `multiplier_curve.dart`, `cashout_controller.dart`
  - **C3**: `spin_event_table.dart`, `energy_service.dart`, `raid_resolver.dart`
  - **C4**: `banner_resolver.dart`, `pity_counter.dart` (персистентный), `duplicate_converter.dart`
  - **C5**: `run_rng.dart` (`Random(seed)` — ADR!), `hand_evaluator.dart`, `modifier_registry.dart`
  - **C6**: `physics_world.dart` (fixed timestep), `launch_resolver.dart`, `bucket_detector.dart`
- `lib/models/game_state.dart` — sealed class со ВСЕМИ состояниями
- `lib/models/` — все модели данных (символы, тайлы, враги, и т.д.)
- `lib/components/` — ВСЕ Flame компоненты:
  - Основной игровой компонент (ReelComponent / TableComponent / MinefieldComponent /
    MultiplierCurveComponent / BannerComponent / PegBoardComponent)
  - Элементы (SymbolComponent / CardComponent / ChipComponent / BallComponent / CapsuleComponent)
  - Управление (touch/tap handlers)
  - Все компоненты ОБЯЗАНЫ иметь onLoad(), update(dt), и правильную очистку в onRemove()
  - **Animation hooks (для Gameplay Feel Pass):** каждый игровой компонент ОБЯЗАН объявить
    публичные методы-хуки для анимаций — `playEntrance()`, `playImpact()`/`playReaction()`,
    `playStateChange()` (и категорийные: `stopAt()`, `playReveal()`, `playCashout()` и т.п.). В Фазе 4
    они могут содержать минимальную рабочую реализацию без TODO-комментариев — **Фаза 6.5
    их наполнит**. ГЛАВНОЕ: в логике игры (game/world/systems) РАСставить ВЫЗОВЫ этих хуков в
    нужных точках цикла (появился элемент → `playEntrance()`; засчитан выигрыш/удар → `playImpact()`;
    сменилось состояние объекта → `playStateChange()`). Без вызовов хуки мертвы.

**КРИТИЧЕСКИ для Agent A**:
- Результат действия вычисляется ДО анимации (Stateless Outcomes)
- GameState transitions ОБЯЗАНЫ быть полными (нельзя застрять в состоянии)
- update() и render() — ТОЛЬКО синхронные, нет await
- Нет аллокаций в update() — прединициализация Vector2, Paint, Rect
- Gambling: ТОЛЬКО Random.secure(), никаких захардкоженных вероятностей
- Все параметры берутся из GameConfig
- Игровые компоненты выставляют animation-хуки И ВЫЗЫВАЮТ их из логики (см. выше) — даже если
  тела хуков пока минимальны; Фаза 6.5 (juice-artist) наполнит их живыми анимациями

### Agent B — ui-programmer (Complete UI):

**Prompt ОБЯЗАН включать**: Полный концепт с Screen Map, **Design DNA**, **Layout Archetype
(L1–L6) из `design/art-direction.md`**, контракт типов, ПОЛНЫЙ список ассетов.

> **АНТИ-SLOP для Agent B (две оси):**
> - **Композиция** — строго по выбранному Layout Archetype (см. `.claude/docs/layout-archetypes.md`).
>   Не лепи дефолтную раскладку «HUD сверху + кнопка снизу по центру» в каждую игру.
> - **Вид** — строго из Design DNA: палитра, шрифты (через `google_fonts`), shape language,
>   brightness (light/dark равноправны), depth-стратегия. НЕ хардкодь неон/Orbitron/тёмную тему/
>   glassmorphism, если это не в DNA. Тип-шкала (4–6 размеров) и базовый шаг отступов (4/8) — обязательны.
>
> **Два режима UI (читать `ui-programmer.md` → разделы «Signature Menu Centerpiece» и
> «In-Game UI Restraint & Alignment»):**
> - **Меню — концептуальное, смелое.** Главное меню НЕ «фон + лого + столбик кнопок». Обязателен
>   фирменный **centerpiece** — тематический живой визуал в центре композиции (из мира игры),
>   многослойная глубина/параллакс, интегрированная типографика, staggered entrance. Меню должно
>   быть узнаваемо «про эту игру», не переносимо в другую сменой цвета.
> - **Игровой экран — сдержанный, геймплей в приоритете.** HUD/кнопки/лейблы стилизованы из DNA,
>   но компактные, прижаты к краям (по Layout Archetype), не наезжают на поле (поле ≈60%+, фокус).
>   Без тяжёлых эффектов на HUD, крадущих внимание у поля. Только основное действие доминирует.
> - **Выравнивание (везде, особенно в HUD):** общие линии выравнивания, равные оптические отступы
>   от краёв, все гэпы/паддинги кратны базовому шагу (4/8). Никаких случайных `padding: 7/13/22`.

Создаёт ВСЕ экраны и виджеты (ПОЛНОСТЬЮ РАБОЧИЕ, не заглушки):

**Обязательные файлы:**

**Тема и утилиты:**
- `lib/theme/game_theme.dart` — ПОЛНАЯ кастомная тема
  - Палитра из 5 цветов (из Design DNA), brightness из DNA (light/dark равноправны)
  - TextTheme: 2 шрифта из Design DNA через `google_fonts` (НЕ хардкод Orbitron) + тип-шкала (4–6 размеров)
  - Базовый шаг отступов (4/8); формы кнопок из shape language DNA
  - CardTheme, DialogTheme, AppBarTheme
- `lib/theme/animations.dart` — ВСЕ тайминги централизованы
  - Durations: fast (150ms), medium (300ms), slow (600ms), screenTransition (400ms)
  - Curves: для кнопок, для экранов, для чисел, для партиклей
- `lib/assets.dart` — типизированные пути к КАЖДОМУ ассету

**Экраны (КАЖДЫЙ полностью реализован, не stub):**
- `lib/screens/splash_screen.dart` — анимированный логотип → авто-переход на меню
- `lib/screens/main_menu.dart` — **концептуальное меню**: фирменный тематический centerpiece
  (живой визуал из мира игры, не просто лого), многослойный фон с параллаксом/частицами,
  интегрированная типографика названия, staggered entrance; кнопка ИГРАТЬ — доминирующий фокус
  с idle-пульсацией; вторичные входы (Settings, Help, Daily Bonus, Leaderboard, Profile) — тише,
  размещены по Layout Archetype (не обязательно одинаковым столбиком)
- `lib/screens/game_screen.dart` — GameWidget обёртка + **сдержанный** HUD overlay (компактный,
  у краёв, не наезжает на поле; поле ≈60%+ — фокус) + Win overlays + Game Over overlay
- `lib/screens/hud_widget.dart` — ValueListenableBuilder для баланса (animated counter), ставки,
  кнопки действия (с блокировкой); строгое выравнивание (общие линии, отступы кратны 4/8),
  минимум хрома, без отвлекающих эффектов
- `lib/screens/paytable_screen.dart` — символы из `design/asset-format.md` (PNG через Image.asset
  в Codex, SVG только fallback) с описанием выплат / правилами (скролл или PageView)
- `lib/screens/settings_screen.dart` — Sound on/off, SFX on/off, Vibration toggle (SharedPreferences)
- `lib/screens/help_screen.dart` — пошаговое руководство с иллюстрациями
- `lib/screens/daily_bonus_screen.dart` — механика ежедневного бонуса (мини-рулетка или сундуки, SharedPreferences для even tracking)
- `lib/screens/leaderboard_screen.dart` — список лучших результатов (SharedPreferences)
- `lib/screens/profile_screen.dart` — аватар (выбор из 6+), никнейм (TextField), статистика
- `lib/screens/win_overlay.dart` — 3 уровня с разными эффектами:
  - Small: toast снизу + animated counter + auto-dismiss 2s
  - Big: полу-экранный + конфетти + 3s
  - Mega: fullscreen + explosion + camera shake + 4s
- `lib/screens/insufficient_funds_dialog.dart` — стилизованный модал (НЕ AlertDialog); depth-стратегия из DNA (карточка/стекло/бумага/плоско)
- `lib/screens/bonus_overlay.dart` — оверлей бонусного режима (Free Spins / Special Mode)

**Виджеты (КАЖДЫЙ с анимациями и состояниями; назначение фиксировано, ВИД — из DNA):**
- `lib/widgets/animated_counter.dart` — плавное изменение чисел (Tween)
- `lib/widgets/primary_action_button.dart` — основное действие, 3 состояния (idle/press/disabled); форма+эффект из DNA
- `lib/widgets/secondary_button.dart` — вторичные действия, визуально тише primary
- `lib/widgets/display_text.dart` — акцентный текст (титулы/числа); эффект (glow/тень/нет) из DNA
- `lib/widgets/idle_pulse.dart` — idle-анимация для любого child (характер из DNA)
- `lib/widgets/game_loading.dart` — тематический загрузчик (НЕ CircularProgressIndicator)
- `lib/widgets/themed_panel.dart` — поверхность-контейнер; depth-стратегия из DNA (карточка/стекло/бумага/плоско)

> Имена нейтральны намеренно. НЕ создавай `NeonText`/`SkewedButton`/`GlowButton` в игре, где
> нет неона/скоса/glow в DNA — это house-style slop. Вид виджета вытекает из Design DNA.

**Маршрутизация:**
- `lib/app.dart` — MaterialApp с именованными routes:
  ```
  /splash → /menu → /game → (overlays через Flame)
                   → /settings
                   → /help
                   → /paytable
                   → /daily-bonus
                   → /leaderboard
                   → /profile
  ```
- `lib/main.dart` — runApp(const GameApp())

**КРИТИЧЕСКИ для Agent B — CRASH PREVENTION (читай `.claude/rules/ui-code.md`):**

**Layout safety (предотвращение RenderFlex overflow):**
- КАЖДЫЙ ListView/GridView внутри Column ОБЯЗАН быть в `Expanded`
- НЕТ `Expanded` внутри `SingleChildScrollView` (не работает!)
- КАЖДЫЙ динамический Text с `overflow: TextOverflow.ellipsis, maxLines: 1` или в FittedBox
- КАЖДЫЙ Image/SvgPicture с явными width + height
- КАЖДЫЙ экран обёрнут в SafeArea (кроме GameScreen)

**Widget lifecycle (предотвращение setState after dispose):**
- КАЖДЫЙ setState в Future/Timer/callback — `if (!mounted) return;` ПЕРЕД setState
- КАЖДЫЙ AnimationController — `dispose()` в `dispose()`
- КАЖДЫЙ Timer — `cancel()` в `dispose()`
- КАЖДЫЙ ScrollController, TextEditingController — `dispose()` в `dispose()`

**Navigation (предотвращение route crashes):**
- ВСЕ pushNamed маршруты определены в routes: map в app.dart
- Splash → Menu через `pushReplacementNamed` (не push!)
- Navigator.pop — только с `if (Navigator.canPop(context))`
- PopScope на КАЖДОМ экране для Back button
- `onUnknownRoute` определён в MaterialApp как fallback

**Interaction (предотвращение UX багов):**
- Кнопка действия: debounce 300ms + isPlaying check + 3 визуальных состояния
- Ставка блокируется во время действия (IgnorePointer)
- КАЖДАЯ кнопка с visual feedback (AnimatedScale при нажатии)
- Tap target >= 48x48 на все кнопки
- Insufficient Funds проверяется перед действием

**Functional completeness (НЕТ заглушек):**
- Если экран существует — он ПОЛНОСТЬЮ реализован
- Settings: SharedPreferences load + save (try-catch)
- Daily Bonus: DateTime check через SharedPreferences
- Leaderboard: реальные данные из SharedPreferences
- Profile: nickname + avatar сохраняются
- Win overlay: 3 уровня (small/big/mega) с auto-dismiss

### Agent C — juice-artist (VFX & Celebration Layer):

> Agent C в Фазе 4 строит **слой реакций и празднования** (отдельные VFX-компоненты) и общий
> тулкит эффектов. **Глубокая анимация самих игровых элементов на поле** (entrance / idle /
> impact / state-transition / anticipation) — задача **Фазы 6.5 (Gameplay Feel Pass)**, которая
> идёт после чистого build и наполняет animation-хуки из Agent A. Здесь — окружение и кульминации.

Создаёт ВСЕ визуальные эффекты (рабочие, подключённые):

- `lib/components/win_animation.dart` — ParticleSystemComponent для 3 уровней выигрыша
- `lib/components/action_vfx.dart` — эффекты основного действия (spin trail, cascade glow, и т.д.)
- `lib/components/payline_overlay.dart` — визуализация выигрышных линий (gambling)
- `lib/components/ambient_particles.dart` — фоновые частицы (звёзды, искры, пыль)
- `lib/components/screen_shake.dart` — camera shake для mega win
- Анимации кнопки действия: press scale 0.92 → release scale 1.0 + glow flash
- Idle-анимации: символы медленно покачиваются, glow пульсирует

**КРИТИЧЕСКИ для Agent C:**
- Все VFX ОБЯЗАНЫ быть подключены к реальным игровым событиям
- Particle count НЕ превышает GameConfig.maxParticles (200)
- Нет аллокаций в update() — прединициализация
- lifespan частиц конечен — нет утечек
- Эффекты служат цели (restraint): на игровом экране VFX — для игровых событий, а не для
  постоянного оформления HUD

### Agent D — sound-designer (Audio Events):

Создаёт аудио-систему:

- `lib/audio/audio_service.dart` — полный сервис:
  - BGM: loop фоновой музыки (с fade in/out)
  - SFX: действие (spin start, spin stop, tap, match, collision)
  - Win: 3 уровня (small ding, big fanfare, mega explosion)
  - UI: button tap, navigation swish, error buzz
  - Проверка Settings (sound on/off) перед каждым воспроизведением
  - Максимум 3 параллельных звука
- `lib/audio/audio_assets.dart` — константы путей аудио (**`.wav`**, файлы РЕАЛЬНО созданы
  в Фазе 3.5: `assets/audio/sfx/sfx_*.wav` + `assets/audio/bgm/bgm_main.wav`)

**Примечание**: Файлы аудио синтезированы (Фаза 3.5) и существуют. Тем не менее AudioService
ОБЯЗАН оборачивать воспроизведение в try-catch (платформенные ограничения web/codecs) и не
крашить. Логирование через Logger, не print(). Уважать Settings (sound/sfx/bgm on/off).

### Agent E — meta-systems-programmer (Save / Economy / Progression / Telemetry):

**Prompt ОБЯЗАН включать**: Полный концепт с **Production Plan** (Content/Economy/Progression/
Monetization/Telemetry/Compliance), контракт типов, пути из `design/structure.md`.

> Полная спецификация ролей и правил — в `.claude/agents/meta-systems-programmer.md`.
> Читать её ПЕРВЫМ действием вместе с `lib/contracts.md` и `design/structure.md`.

Создаёт мета-системы (всё, что превращает один цикл в ПОЛНУЮ игру):

- **SaveService** — единый persistence: settings, profile, progression, economy, leaderboard,
  achievements, dailyBonus, (опц.) resume-snapshot. Версионированная схема + миграция.
  try-catch вокруг КАЖДОГО доступа к диску, безопасный fallback.
- **EconomyService** — coins/валюта, каталог магазина (скины/темы/бустеры/наборы/remove-ads),
  canAfford/purchase/isUnlocked. Цены — из `GameConfig`/`economy-config.json`, не литералы.
- **ProgressionService** — открытые стейджи/комнаты/баннеры, XP-уровень игрока, лучшие
  результаты, recordResult/unlockNext. Источник кривой — конфиг контента категории (Фаза 4.5).
  **(C4) PityCounter персистентен** — счётчик обязан переживать перезапуск, иначе pity фиктивен.
- **AchievementService** — декларативный список (id/условие/награда), проверка по событиям,
  колбэк в UI + начисление награды через Economy.
- **AnalyticsService** (abstract) + **NoOpAnalytics** (default) + **DebugAnalytics** (Logger).
  Таксономия: app_open, session_*, screen_view, level_start/complete/fail, game_action,
  purchase, ad_*, achievement_unlocked, daily_bonus_claimed.
- **AdService** (abstract) + **NoOpAdService**: rewardedContinue/rewardedDouble/interstitial/banner.
- **IapService** (abstract) + **NoOpIapService**: каталог продуктов, buy() выдаёт товар через Economy.
- **RemoteConfigService** (abstract) + **LocalRemoteConfig** (дефолты из GameConfig).

**КРИТИЧЕСКИ для Agent E:**
- Игра ОБЯЗАНА собираться БЕЗ внешних SDK — никаких `firebase_*`/`google_mobile_ads`/
  `in_app_purchase` в pubspec. Только чистый Dart + `shared_preferences`. Всё «облачное» — абстракции.
- НЕ дублировать игровую логику/RNG/исходы/баланс (это Agent A). Не хардкодить числа.
- Без `dynamic` вне JSON-границ; без `print()` (Logger).
- **Compliance (ОБЯЗАТЕЛЬНО, не опционально):** флаг age-gate (показан ли) в SaveService;
  строки disclaimer/responsible-play — в одной константе `ComplianceCopy`, не в виджетах;
  валюта строго виртуальная, без символов реальной валюты у баланса; для C4 — экран шансов
  читает те же числа, что и резолвер. См. `.claude/rules/responsible-gaming.md`.
- Сервисы testable (инъекция SharedPreferences/времени). Вызовы сервисов расставляются в Фазе 5.

---

## Фаза 4.5 — Content & Modes WIRING (Сессия 2) [~4 мин]

> **Данные уже есть.** `assets/data/*.json` сгенерированы в Фазе 3.7 (Сессия 1). Здесь —
> ПОДКЛЮЧЕНИЕ этих данных к коду: GameConfig загружает их, Game/GameScreen принимают
> `(mode, levelId)`, ProgressionService читает level-config, Level/Mode Select показывает
> реальный список. Контент = данные, поэтому 24 уровня = один GameScreen + конфиг, не 24 экрана.

### 4.5.1 — Проверить и загрузить конфиг контента
Конфиги из Фазы 3.7 в `assets/data/` (состав по категории: `bet-tiers.json` C1/C2 /
`stage-config.json` C3 / `banners.json` C4 / `run-config.json` C5 / `board-config.json` C6,
плюс `economy-config.json`) и конфиг матмодели в `design/balance/`. Убедиться, что они валидны
и **GameConfig их загружает** (не дублирует числа в литералах). Чего не хватает — досоздать здесь.

### 4.5.2 — Режимы (modes)
Реализовать 2–3 режима из Production Plan как enum + ветвление в Game (НЕ как отдельные копии
игры): Classic (основной цикл на выбранном bet-tier/стейдже), плюс один из High-Roller /
Turbo / Survival-серии, плюс опц. Daily Challenge (детерминированный seed по дате → одинаковый
«сегодняшний» расклад, отдельный leaderboard). GameScreen принимает `(mode, stageId)`;
ProgressionService решает доступ.

### 4.5.3 — Лёгкая балансировка кривой (game-mathematician)
Прогнать сгенерированный конфиг через быструю проверку (полная — в Фазе 9):
- **C1/C2**: bet-tiers не ломают RTP-окно; кап множителя объявлен.
- **C3**: лестница анлоков монотонна, шаг цены ≤ 1.6×, нет «стены гринда».
- **C4**: сумма rates = 1.0, hard pity достижим.
- **C5**: пороги раундов растут не более чем ×2.
- **C6**: нет «мёртвых» корзин.
Если кривая кривая — скорректировать JSON (не код).

### 4.5.4 — Критерий выхода Фазы 4.5
- `assets/data/*.json` существуют и валидный JSON (N записей контента, не 1).
- GameScreen/Game умеют принимать `(mode, levelId)`; ProgressionService читает level-config.
- Level/Mode Select экран (Agent B) связан с реальными данными (не хардкод-список из 3 уровней).
- `dart analyze lib/` остаётся 0 errors.

---

## Фаза 5 — Deep Integration & Wiring [~5 мин]

**ЭТО САМАЯ ВАЖНАЯ ФАЗА.** Большинство крашей происходит из-за плохой интеграции.

Прочитать `design/structure.md` в начале фазы для получения актуальных путей к файлам.

### 5.1 — Файл ассетов
Создать / обновить файл констант ассетов по пути `assets_constants` из `design/structure.md` (для V1: `lib/assets.dart`, для V5: `lib/bootstrap/assets.dart` и т.д.).

**КРИТИЧЕСКИ**: расширения файлов берутся из `design/asset-format.md` (`.png` для Codex-режима,
`.svg` для fallback). Все пути ОБЯЗАНЫ совпадать с реально существующими файлами.

```dart
class GameAssets {
  // Sprites (расширение .png или .svg — из design/asset-format.md)
  static const String spriteCherry = 'assets/images/sprites/sprite_cherry.png'; // .png в Codex / .svg иначе
  // ... ВСЕ ассеты с ТОЧНЫМИ путями к существующим файлам

  // Validate all assets exist (вызвать в debug mode)
  static List<String> get all => [spriteCherry, ...];
}
```

### 5.2 — Проверка связей
ОБЯЗАТЕЛЬНО прочитать и проверить:

1. **main.dart → app.dart**: `runApp(const GameApp())` вызывается
2. **app.dart → routes**: ВСЕ именованные routes определены и ведут на реальные экраны
3. **game_screen.dart → Game class**: GameWidget правильно создаёт игру, передаёт overlays
4. **Game class → ValueNotifiers → HUD**: ValueNotifiers создаются в Game, передаются в HUD
5. **Game class → VFX**: win_animation и другие VFX подключены к событиям
6. **Game class → Audio**: AudioService вызывается при правильных событиях
7. **Settings → SharedPreferences**: Настройки сохраняются И загружаются
8. **Win Overlay → Game Screen**: показывается через Flame overlays или Navigator
9. **Insufficient Funds → Game Screen**: вызывается при balance < bet
10. **Daily Bonus → SharedPreferences**: дата проверяется, бонус начисляется
11. **Leaderboard → SharedPreferences**: результаты записываются и читаются
12. **Profile → SharedPreferences**: данные сохраняются

**Мета-системы (Agent E) — подключение к игре и UI:**
13. **SaveService — единый**: экраны/сервисы ходят через SaveService, нет россыпи прямых
    `SharedPreferences.getInstance()` по экранам (консолидировать)
14. **Level/Mode Select → Game**: выбор уровня/режима передаёт параметр в Game; ProgressionService
    отдаёт состояние (открыт/звёзды); по завершении — `recordResult` + `unlockNext`
15. **Economy → Shop**: магазин читает баланс/каталог из EconomyService; покупка списывает coins
    и помечает unlocked; победы/уровни начисляют coins
16. **Achievements → события**: AchievementService подписан на игровые события; разблокировка →
    toast/overlay + награда через Economy
17. **Analytics-вызовы расставлены**: `analytics.log(...)` в навигации (screen_view) и геймплее
    (level_start/complete/fail, game_action, purchase, ad_*, daily_bonus_claimed)
18. **(gambling) Compliance подключён**: age-gate показывается при первом запуске (флаг в Save);
    disclaimer на splash + paytable; responsible-play в settings

### 5.3 — Исправление несоответствий между агентами
Типичные проблемы:
- Agent A назвал класс `SlotGame`, Agent B ожидает `SlotMachineGame` → исправить
- Agent A создал ValueNotifier<int>, Agent B ожидает ValueNotifier<double> → привести к единому типу
- Agent C создал VFX компонент, но Agent A не добавляет его в World → добавить
- Пути ассетов в коде не совпадают с реальными файлами → исправить

### 5.4 — pubspec.yaml финализация
- Все папки с ассетами перечислены в `flutter.assets`
- Все шрифты перечислены в `flutter.fonts`
- Нет дублирующихся зависимостей

---

## Фаза 6 — Build & Fix (Strict Loop) [~5 мин]

**ОБЯЗАТЕЛЬНО выполнить полный цикл `dart analyze` → исправление → повтор.**
Нельзя останавливаться на первой ошибке или считать "в целом зелёно".

```bash
flutter pub get
dart analyze lib/ --fatal-infos
```

### Цикл исправлений (до 10 итераций):

**Итерация N:**
1. `dart analyze lib/` → собрать ВСЕ ошибки
2. Исправить ВСЕ ошибки (не по одной, а ВСЕ сразу)
3. Повторить анализ

**Типичные ошибки после параллельной генерации:**
- Missing imports → добавить
- Undefined class/method → проверить контракт, исправить имя
- Type mismatch → привести к единому типу
- Missing required parameters → добавить
- Unused imports → удалить
- Override method signature mismatch → исправить сигнатуру

**Критерий выхода:** `dart analyze lib/` показывает 0 errors.
Warnings допустимы, но не info about unused variables (удалить их).

---

## Фаза 6.5 — Gameplay Animation & Feel Pass (dedicated agent) [~6 мин]

> **Зачем эта фаза.** После Фазы 6 код компилируется, но геймплей часто статичен: элементы
> на поле стоят, появляются/исчезают мгновенно, не реагируют на действия. Меню и HUD могут
> быть анимированы, а САМА ИГРА — мертва. Эта фаза запускает выделенного агента (роль
> **juice-artist**), который оживляет игровые компоненты НА ПОЛЕ и связывает анимации с
> событиями игрового цикла. Работает на чистом, компилирующемся коде — поэтому видит реальные
> сигнатуры классов, а не догадки.

**Это пятый агентский проход конвейера.** Запускается ПОСЛЕ чистого `dart analyze` (Фаза 6),
ДО генерации тестов (Фаза 7), чтобы тесты покрывали уже финальный код.

### 6.5.1 — Запуск агента Gameplay Feel Pass

Вызвать Agent tool (без `subagent_type`/`model`/`reasoning_effort` — full-history fork):

```
Agent(
  description="Gameplay Feel Pass: оживить игровые компоненты на поле",
  prompt="""
Ты — juice-artist студии. Код игры уже компилируется (dart analyze чист). Твоя задача —
сделать ГЕЙМПЛЕЙ ЖИВЫМ: анимировать сами игровые компоненты на поле и связать анимации с
событиями игрового цикла. НЕ трогай меню/HUD-стиль и НЕ меняй игровую логику/исходы/баланс.

ПЕРВЫМИ ДЕЙСТВИЯМИ прочитай:
1. design/structure.md — точные пути (components_dir, systems_dir, game_dir, animations)
2. design/gdd/game-concept.md — секции Design DNA → Motion Character И Reference Bar
   (референс-игры калибруют ОЩУЩЕНИЕ: тайминги, вес, ритм наград)
3. .claude/agents/juice-artist.md — раздел «0.5 — Анимация ВНУТРИ геймплея» (5 типов движения)
4. .claude/docs/quality-bar.md — §2 (окна отклика ≤100мс), §3 (масштабированный фидбек),
   §4 (живое поле: скриншоты с интервалом 2с ОБЯЗАНЫ различаться)
5. Реальные файлы игровых компонентов и логики (по путям из structure.md)

ЧТО СДЕЛАТЬ (для КАЖДОГО игрового элемента на поле):
- **Entrance**: элемент появляется с анимацией (влетает/выпадает/проявляется), не мгновенно
- **Idle**: живое ожидание в update(dt) — дыхание/покачивание/мерцание (десинхронизируй фазы)
- **Impact/Reaction**: на главное действие — squash&stretch / вспышка / отдача
- **State transition**: смена состояния объекта анимирована (morph/reveal/flip), не щелчком
- **Anticipation→Release**: нагнетание перед результатом (каскад/slow-mo/замах) → разрядка
- Наполни animation-хуки (playEntrance/playImpact/playStateChange/playLand/playMatch/…),
  объявленные Agent A в Фазе 4. Если хук ещё не вызывается из логики — ДОБАВЬ вызов в нужной
  точке цикла (game/world/systems). Анимация без вызова = мёртвый код.
- Характер движения бери из Motion Character (DNA): тяжёлая игра — весомо; казуальная —
  пружинисто; дзен — сдержанно. Не навязывай неон/тряску, если их нет в DNA.

ЖЁСТКИЕ ОГРАНИЧЕНИЯ:
- Используй встроенные Flame-эффекты (ScaleEffect/MoveEffect/RotateEffect/OpacityEffect/
  ColorEffect/SequenceEffect/EffectController) — они самоочищаются, не текут.
- НЕТ аллокаций в update()/render() — прединициализируй Vector2/Paint; idle через накопление фазы.
- update()/render() — только синхронные (нет await).
- ВСЕ Duration/Curve — из файла animations (путь из structure.md), НЕ хардкод. Добавь недостающие
  константы (idleBreathSpeed, entranceDuration, impactDuration, …) в этот файл.
- НЕ меняй: GameConfig игровые параметры, RNG, результаты действий (Stateless Outcomes), баланс.
- Анимации НЕ должны скрывать игровое состояние (видно, где что лежит) и не длиннее 2с для
  основного действия.
- Бюджет: не превышай лимит компонентов/партиклей (GameConfig.maxParticles).

ПОСЛЕ ПРАВОК (обязательно):
1. flutter pub get && dart analyze lib/  → исправь СВОИ ошибки до 0 (до 5 итераций)
2. flutter test  → должны остаться зелёными (если что-то сломал анимацией — почини)
3. Самопроверка чек-листом «живого геймплея» из juice-artist.md (все пункты + grep, что хуки
   реально вызываются из логики)

ВЕРНИ краткий отчёт: какие компоненты оживлены, какие хуки наполнены и где вызываются,
статус dart analyze и flutter test.
"""
)
```

### 6.5.2 — Проверка результата Feel Pass

После возврата агента — проверить в основной conversation:

```bash
# 1. Компиляция и тесты по-прежнему зелёные
dart analyze lib/
flutter test

# 2. Хуки анимации реально вызываются из логики (а не только объявлены)
grep -rn "playEntrance\|playImpact\|playReaction\|playStateChange\|playLand\|playMatch" lib/ \
  | grep -v "void play" | head -40
```

**Критерий выхода Фазы 6.5:**
- `dart analyze lib/` → 0 errors, `flutter test` → зелёные
- У основного игрового элемента есть idle-движение в `update()`
- Хуки анимации (entrance/impact/state) ВЫЗЫВАЮТСЯ из логики (grep непустой, помимо объявлений)
- Нет аллокаций в `update()`/`render()`, тайминги из animations-файла

Если агент не оживил геймплей (поле статично) или сломал build/тесты — повторить запуск
с уточнением (до 2 итераций). Эта фаза — про ЖИВОЙ геймплей, не про меню.

---

## Фаза 7 — Test Suite Generation & Execution [~8 мин]

**НОВАЯ ФАЗА. Тесты ОБЯЗАТЕЛЬНЫ, не опциональны.**

Запустить агент qa-tester для создания полного набора тестов:

### 7.1 — Unit Tests

**`test/systems/`** — тесты логики:

**ВО ВСЕХ категориях (обязательный минимум):**
- `weighted_rng_test.dart` — дистрибуция исходов (100K итераций, ±5% от весов конфига)
- Проверка что используется `Random.secure()` (чтение исходника; исключение — C5 + ADR)
- `outcome_resolver_test.dart` — исход вычислен ДО анимации (Stateless Outcomes)
- `payout_test.dart` — выплата ровно равна ставке × множитель, без утечки в округлении

Для C1 (Social Casino):
- `payline_evaluator_test.dart` — все комбинации выигрышей + Wild/Scatter + edge cases
- Wild заменяет любой символ кроме Scatter; 2 символа без Wild — не выигрыш

Для C2 (Originals):
- `multiplier_curve_test.dart` — множитель на шаге k = (1 - houseEdge) / P(дожить до k)
- `round_resolver_test.dart` — одинаковые (serverSeed, clientSeed, nonce) → одинаковый исход;
  изменение любого компонента меняет исход
- `cashout_test.dart` — cash-out на шаге k платит ровно ставка × multiplier(k)
- Кап максимального множителя соблюдается

Для C3 (Spin-to-Progress):
- `spin_event_table_test.dart` — распределение событий соответствует весам
- `energy_service_test.dart` — реген не превышает кап, трата не уводит в минус

Для C4 (Gacha):
- `pity_counter_test.dart` — на hard pity редкость гарантирована в 100% случаев
- Счётчик pity ПЕРЕЖИВАЕТ перезапуск (персистентность через SaveService)
- Сумма вероятностей редкостей = 1.0; дубликат всегда конвертируется

Для C5 (Roguelike):
- `run_determinism_test.dart` — один seed → идентичный забег (сравнение полного лога событий)
- `modifier_registry_test.dart` — каждый модификатор применяется и снимается корректно

Для C6 (Physics):
- `physics_world_test.dart` — объекты не проваливаются, отскоки корректны
- `determinism_test.dart` — фиксированный timestep + seed → идентичная траектория

### 7.2 — Model Tests

**`test/models/`**:
- `game_state_test.dart` — все переходы между состояниями
- `game_config_test.dart` — все константы имеют разумные значения

### 7.3 — Integration Tests (Game Flow)

**`test/game/`**:
- `game_flow_test.dart`:
  - Игра инициализируется без ошибок
  - Основное действие (spin/move/tap) работает
  - Баланс / счёт обновляется корректно
  - GameState возвращается в Idle после каждого действия
  - 100 последовательных действий без ошибок (state leakage test)
  - Пауза и возобновление работают

### 7.3b — Meta-Systems Tests (Agent E)

**`test/services/`** (инъекция мок-`SharedPreferences`, без реального диска):
- `save_service_test.dart` — round-trip save→load; миграция со старой `save_schema_version`;
  повреждённые/отсутствующие данные → безопасный fallback (не падать)
- `economy_service_test.dart` — начисление, `canAfford`/`purchase` списывает ровно цену,
  `isUnlocked` после покупки, нельзя купить без средств, валюта не уходит в минус
- `progression_service_test.dart` — `recordResult`/`unlockNext`, открытие следующего уровня,
  звёзды сохраняются, лучший счёт не уменьшается
- `analytics_noop_test.dart` — NoOp/Debug не бросают и не зависят от внешних SDK

### 7.4 — Edge Case Tests

**`test/edge_cases/`**:
- Нулевой баланс → действие блокируется
- Быстрый двойной клик → второй игнорируется
- Ставка > баланса → показывает insufficient funds
- Максимальная ставка на минимальном балансе

### 7.5 — Запуск тестов

```bash
flutter test --reporter expanded
```

**Цикл**: если тесты падают → исправить КОД (не тесты, если тесты верны) → перезапустить.
До 5 итераций исправлений.

**Критерий выхода**: ВСЕ тесты зелёные (passed).

---

## Фаза 8 — Deep UI/UX Audit & Auto-Fix [~8 мин]

**ЭТО КРИТИЧЕСКАЯ ФАЗА. Большинство багов — UI/UX ошибки.**

Прочитать `design/structure.md` для определения текущего варианта структуры и путей.
Затем прочитать ВСЕ файлы в директориях `screens_dir`, `widgets_dir`, директории theme, и файл `app` — все пути берутся из `design/structure.md`.
Провести полный аудит по 10 категориям (100+ проверок) из `.claude/skills/ui-audit/SKILL.md`,
включая меню-centerpiece, сдержанность HUD, живой геймплей (категория I) и
**Production Completeness & Compliance (категория J)** — наличие контента/режимов/мета-систем,
расставленные analytics-вызовы, и (для gambling) age-gate/disclaimer/responsible-play.

### 8.1 — КРАШ-УЯЗВИМОСТИ (исправлять ПЕРВЫМИ!)

| # | Проверка | Как найти | Автофикс |
|---|----------|-----------|----------|
| A1 | **RenderFlex overflow** | Column/Row с ListView/GridView без Expanded | Обернуть scroll-виджет в `Expanded` |
| A2 | **ListView в Column** | `ListView` внутри `Column` без `Expanded` | Обернуть в `Expanded` |
| A3 | **setState after dispose** | `setState` в Future/Timer/callback без `if (!mounted) return;` | Добавить mounted check |
| A4 | **AnimationController без dispose** | StatefulWidget с AnimationController, нет dispose() | Добавить `controller.dispose()` в `dispose()` |
| A5 | **Timer без cancel** | `Timer.periodic` без `cancel()` в `dispose()` | Добавить cancel |
| A6 | **Navigator.pop без canPop** | `Navigator.pop(context)` без проверки | Добавить `if (Navigator.canPop(context))` |
| A7 | **Отсутствующий ассет** | Пути в коде vs реальные файлы в `assets/` | Создать файл или исправить путь |
| A8 | **Шрифт не зарегистрирован** | fontFamily в коде vs fonts в pubspec.yaml | Добавить в pubspec |
| A9 | **Expanded в SingleChildScrollView** | `Expanded` внутри `SingleChildScrollView` — не работает | Убрать Expanded, использовать фиксированный/intrinsic размер |
| A10 | **Missing Key на списках** | `ListView.builder` без `key:` на children | Добавить `ValueKey` |

### 8.2 — LAYOUT БЕЗОПАСНОСТЬ

| # | Проверка | Автофикс |
|---|----------|----------|
| B1 | SafeArea на КАЖДОМ экране (кроме GameScreen) | Обернуть в SafeArea |
| B2 | Нет фиксированных px для layout (>100px) | Заменить на MediaQuery / LayoutBuilder |
| B3 | Каждый динамический Text с overflow handling | Добавить `overflow: TextOverflow.ellipsis, maxLines:` |
| B4 | TextField внутри ScrollView (для клавиатуры) | Обернуть в SingleChildScrollView |
| B5 | Scaffold на каждом экране | Обернуть в Scaffold |
| B6 | Image/SVG с width + height | Добавить размеры |
| B7 | Нет вложенных scroll (или shrinkWrap на внутреннем) | Добавить shrinkWrap + NeverScrollableScrollPhysics |
| B8 | Контент адаптируется к маленьким экранам (< 640px height) | Добавить scroll или адаптивный layout |

### 8.3 — НАВИГАЦИЯ И СОСТОЯНИЕ

| # | Проверка | Автофикс |
|---|----------|----------|
| C1 | ВСЕ pushNamed маршруты определены в app.dart routes | Добавить недостающие routes |
| C2 | Back button обработан (PopScope) на каждом экране | Добавить PopScope |
| C3 | Splash → Menu через pushReplacementNamed (не push) | Заменить на pushReplacement |
| C4 | Splash имеет авто-переход (Timer/Future.delayed) | Добавить таймер |
| C5 | Flame overlays закрываются по таймеру + тапу | Добавить auto-dismiss |
| C6 | Settings сохраняются в SharedPreferences | Добавить persistence |
| C7 | Settings применяются (sound toggle → AudioService) | Добавить проверку |
| C8 | Daily Bonus проверяет дату | Добавить date check |
| C9 | Leaderboard обновляется при новом highscore | Добавить запись |
| C10 | Profile сохраняет nickname/avatar | Добавить persistence |
| C11 | onUnknownRoute определён в MaterialApp | Добавить fallback |

### 8.4 — КНОПКИ И ВЗАИМОДЕЙСТВИЕ

| # | Проверка | Автофикс |
|---|----------|----------|
| D1 | Кнопка действия: debounce 300ms + isPlaying check | Добавить защиту |
| D2 | Кнопка действия: 3 визуальных состояния (idle/press/disabled) | Добавить анимацию |
| D3 | Bet блокирован во время действия (IgnorePointer или disabled) | Добавить блокировку |
| D4 | КАЖДАЯ кнопка с visual feedback (scale/opacity при нажатии) | Добавить AnimatedScale |
| D5 | Tap target >= 48x48 на все кнопки | Обернуть в SizedBox(48) |
| D6 | Insufficient Funds проверяется перед действием | Добавить if (balance < bet) |
| D7 | Пустые состояния (empty list) стилизованы | Добавить EmptyStateWidget |
| D8 | Win overlay: 3 уровня (small/big/mega) | Добавить switch по multiplier |
| D9 | Win overlay: auto-dismiss + tap-to-dismiss | Добавить Timer + GestureDetector |
| D10 | Числа (баланс/счёт) анимируются через AnimatedCounter | Обернуть |

### 8.5 — DESIGN INTENT (контекстуальный дизайн)

> Не "всегда neon + trapezoid." А: каждое решение обосновано контекстом ЭТОЙ игры.
> Прочитай Design DNA из `design/gdd/game-concept.md`.

| # | Проверка | Автофикс |
|---|----------|----------|
| E1 | Нет default ThemeData.dark/light без кастомизации | → Кастомная тема из Design DNA |
| E2 | Нет generic CircularProgressIndicator | → Тематический загрузчик (контекст игры) |
| E3 | Нет generic AlertDialog | → Стилизованный диалог (стиль из DNA) |
| E4 | Нет generic MaterialPageRoute | → Тематический PageRouteBuilder |
| E5 | Нет print() | → debugPrint или удалить |
| E6 | Есть animations.dart | Создать если нет |
| E7 | Нет хардкоженных Duration в screens | → AnimationConfig |
| E8 | Цвета из game_theme.dart соответствуют Design DNA | Скорректировать палитру |
| E9 | Шрифты подходят настроению игры | Заменить если generic |
| E10 | Кнопки имеют единый стиль из DNA | Привести к единству |
| E11 | Визуальная консистентность между экранами | Проверить палитру/шрифты/стиль |
| E12 | UI НЕ transferable — уникален для этой игры | Усилить тематическую привязку |
| E13 | **Меню — концептуальное**: есть фирменный тематический centerpiece (не просто лого+столбик) | Добавить живой centerpiece из мира игры + многослойную глубину |
| E14 | **Игровой экран — сдержанный**: HUD компактный, у краёв, не наезжает на поле (поле ≈60%+) | Уменьшить/прижать HUD к краям, убрать центральные панели |
| E15 | **Иерархия на поле**: только основное действие доминирует, HUD визуально тише | Приглушить вторичные элементы HUD (размер/контраст/эффекты) |
| E16 | **Выравнивание**: общие линии, равные отступы от краёв, гэпы кратны 4/8 | Привести к сетке; убрать случайные padding 7/13/22 |

### 8.6 — ЭКРАНЫ (все 12+ существуют и работают)

Проверить что каждый экран из списка Agent B (Фаза 4) существует,
содержит реальный код (не заглушку), подключён к навигации.

### 8.7 — ЖИВОЙ ГЕЙМПЛЕЙ (проверка результата Фазы 6.5)

> Не путать с анимациями меню/HUD. Здесь проверяем, что анимирован САМ геймплей на поле.

| # | Проверка | Как найти | Автофикс |
|---|----------|-----------|----------|
| F1 | Основной игровой элемент имеет idle-движение в `update()` | grep `update(` в components_dir + ScaleEffect/sin | Вернуть Фазу 6.5 — добавить idle |
| F2 | Элементы появляются с entrance-анимацией (не мгновенно) | поиск `playEntrance`/scale-in/move-in при добавлении | Добавить entrance в спавн |
| F3 | На главное действие есть impact/reaction на поле | хук `playImpact`/`playMatch`/squash вызывается из логики | Добавить реакцию + вызов |
| F4 | Смена состояния игрового объекта анимирована | reveal/morph/flip при смене состояния | Анимировать переход |
| F5 | Хуки анимации реально ВЫЗЫВАЮТСЯ из логики (не только объявлены) | `grep -rn "play...(" lib/ \| grep -v "void play"` | Добавить вызовы в game/world/systems |
| F6 | Нет аллокаций в `update()`/`render()` игровых компонентов | поиск `Vector2(`/`Paint()` в update | Прединициализировать |
| F7 | Тайминги анимаций поля — из animations-файла, не хардкод | поиск `Duration(milliseconds:` в components | Вынести в AnimationConfig |

Если поле статично (F1–F4 не выполнены) — это провал «живой игры»: повторить Фазу 6.5.

### Post-Audit (ОБЯЗАТЕЛЬНО)

```bash
dart analyze lib/
flutter test
```

Если автофиксы сломали компиляцию или тесты → исправить (до 5 итераций).
**Критерий**: 0 errors в analyze + все тесты зелёные.

---

## Фаза 9 — Верификация математической модели [~3 мин]

> **Проверять ВЕСЬ контент**, а не одну точку: все bet-tiers / стейджи / баннеры / раскладки
> из Фазы 3.7, а не только дефолт. Детальная проверка — `/balance-check` (full-curve режим).

Инструмент один для всех категорий — `tools/simulate_math.py`. Модель берётся из блока
**Классификация** концепта. Пороги — `.claude/docs/math-models.md`.

```bash
python3 tools/simulate_math.py \
  --model [m1-m6] \
  --config design/balance/[файл].json \
  --trials 100000 \
  --report design/balance/simulation-report.md
```

Код возврата: `0` = PASS, `1` = CONCERNS, `2` = FAIL.

| Категория | Модель | Конфиг | Требование в автогенерации |
|-----------|--------|--------|----------------------------|
| C1 | m1 | `rtp-config.json` | RTP 94–98% (окно чуть шире для скорости), hit rate 15–45% |
| C2 | m2 | `rtp-config.json` | RTP 95–99.5%, кап объявлен, разброс по стратегиям ≈ 0 |
| C3 | m3 | `economy-config.json` | source/sink 0.8–1.3, пейс 1.5–8 сессий на анлок |
| C4 | m4 | `gacha-config.json` | сумма rates = 1.0, 0 пропусков pity, 90-й перцентиль ≤ hard pity |
| C5 | m5 | `run-config.json` | win-rate 15–55%, детерминизм по seed обязателен |
| C6 | m6 | `physics-config.json` | RTP 94–98%, fixed timestep + seed обязательны |

Если вердикт FAIL → корректировать **JSON-конфиг** (не Dart-литералы) и прогонять снова,
до 3 итераций. `GameConfig` читает те же числа из конфига, поэтому правка одного места
чинит и код, и математику.

Отчёт сохраняется в `design/balance/simulation-report.md` автоматически.

> Если конфига ещё нет — взять эталон из `.claude/docs/templates/math-configs/`
> (все шесть проходят прогон «из коробки») и адаптировать под игру.

---

## Фаза 10 — Final Compilation & Crash Prevention [~3 мин]

### 10.1 — Чистая компиляция
```bash
flutter clean
flutter pub get
dart analyze lib/
flutter test
```

ВСЕ команды должны пройти без ошибок.

### 10.2 — Crash Prevention Audit (20 проверок)

Прочитать ключевые файлы и проверить КАЖДЫЙ пункт:

**Dart / Null Safety:**
1. Нет голого `!` без обоснования — все nullable обработаны через `??` или pattern matching
2. Нет `await` в Flame `update()` / `render()` — ТОЛЬКО синхронные

**Widget Lifecycle (САМЫЕ ЧАСТЫЕ КРАШИ):**
3. КАЖДЫЙ `setState` в async контексте имеет `if (!mounted) return;` перед ним
4. КАЖДЫЙ `AnimationController` disposed в `dispose()`
5. КАЖДЫЙ `Timer` / `Timer.periodic` cancelled в `dispose()`
6. КАЖДЫЙ `StreamSubscription` cancelled в `dispose()`
7. КАЖДЫЙ `ScrollController`, `TextEditingController`, `FocusNode` disposed

**Layout (ВТОРОЙ ПО ЧАСТОТЕ):**
8. НЕТ `ListView` / `GridView` внутри `Column` / `Row` без `Expanded`
9. НЕТ `Expanded` / `Flexible` внутри `SingleChildScrollView`
10. КАЖДЫЙ динамический `Text` имеет `overflow:` + `maxLines:` или обёрнут в `FittedBox`/`Flexible`
11. КАЖДЫЙ `Image` / `SvgPicture` имеет `width:` + `height:`
12. SafeArea на каждом экране (кроме fullscreen GameScreen)

**Navigation:**
13. `Navigator.pop` защищён `canPop` проверкой
14. Splash → Menu через `pushReplacementNamed` (не push)
15. ВСЕ маршруты из кода присутствуют в `routes:` map
16. `onUnknownRoute` определён как fallback

**External Resources (try-catch):**
17. SharedPreferences: try-catch вокруг КАЖДОГО вызова (get/set)
18. Audio: try-catch вокруг КАЖДОГО FlameAudio вызова
19. Flame overlay lifecycle: каждый `overlays.add()` имеет соответствующий `overlays.remove()` по таймеру

**Game State:**
20. GameState sealed class не может застрять — каждое состояние имеет transition наружу

Исправить ВСЕ найденные проблемы. Каждый пункт — потенциальный краш.

### 10.3 — Финальная перекомпиляция
```bash
dart analyze lib/
flutter test
```

---

## Фаза 10.7 — Handoff & Subagent Spawn [~1 мин]

**ЭТО ПОСЛЕДНЯЯ ФАЗА СЕССИИ 2** (`autocreate-implement`).
Фазы 10.5 (runtime+soak), 11 (session state), 11.5 (release-eng prep) и 12 (final report)
выполняются в **Сессии 3** (subagent с чистым контекстом, `autocreate-finalize`), не здесь.

### 10.7.1 — Запись handoff-файла

Создать `production/session-state/autocreate-handoff.md` со всем контекстом,
необходимым subagent-у Сессии 3:

```markdown
# AutoCreate Handoff — Сессия 2 (имплементация) завершена

**Время завершения Сессии 2**: [ISO timestamp]
**Следующий шаг**: subagent выполняет `.claude/skills/autocreate-finalize/SKILL.md` (Сессия 3)

## Метаданные игры
- **Название**: [Game Name]
- **Категория**: [C1 Social Casino / C2 Originals / C3 Spin-to-Progress / C4 Gacha / C5 Roguelike / C6 Physics]
- **Архетип**: [A-AF / Unique]
- **Layout Archetype**: [L1–L6 из design/art-direction.md]
- **Package name**: com.gamestudio.[name]
- **Структура**: [V1–V5 из design/structure.md]
- **Пути**:
  - Концепт: `design/gdd/game-concept.md`
  - Структура: `design/structure.md`
  - Баланс: `design/balance/[rtp-config.json или level-config.json]`
  - Главный класс игры: `[game_dir из structure.md][name]_game.dart`
  - Entry point: `lib/main.dart`

## Статус Сессий 1–2 (Фазы 1–10)
- [x] Фаза 1: Концепт + Production Plan сгенерированы (Сессия 1)
- [x] Фаза 2: Flutter проект создан (web,android,ios) (Сессия 1)
- [x] Фаза 3: [N] ассетов сгенерированы ([SVG/PNG]) (Сессия 1)
- [x] Фаза 3.5: Аудио синтезировано — 9 `.wav` (mood: [mood]) (Сессия 1)
- [x] Фаза 3.7: Контент-данные — `assets/data/*.json`, [N] уровней (Сессия 1)
- [x] Фаза 4: 5 агентов завершили имплементацию (A/B/C/D/E)
- [x] Фаза 4.5: Контент — [N] уровней/стейджей + режимы [список]; `assets/data/*.json`
- [x] Фаза 5: Интеграция проверена (18 связей, вкл. мета-сервисы)
- [x] Фаза 6: `dart analyze lib/` → 0 errors
- [x] Фаза 6.5: Gameplay Feel Pass — игровое поле живое (idle/entrance/impact/state)
- [x] Фаза 7: `flutter test` → [N] тестов, все зелёные
- [x] Фаза 8: UI/UX аудит пройден (100+ проверок, вкл. compliance/content)
- [x] Фаза 9: Balance check по всей кривой — [RTP XX.X% / difficulty OK]
- [x] Фаза 10: Crash-prevention аудит — 20/20 + (gambling) age-gate/disclaimer

## Мета-системы (Agent E) — для финального отчёта
- Экономика: [валюта] + магазин ([N] позиций); Прогрессия: [N] уровней/звёзды
- Достижения: [N]; Monetization: rewarded/interstitial/iap — abstractions (no-op)
- Telemetry: AnalyticsService (no-op) с расставленными вызовами

## Задачи для Сессии 3 (subagent выполняет)
- [ ] Фаза 10.5: Runtime verification (скрины + logcat + auto-fix loop) + soak/leak проверка
- [ ] Фаза 10.6: Playtest — реальная игровая сессия (P1–P10, `.claude/skills/playtest/SKILL.md`)
- [ ] Фаза 11: Обновить `production/session-state/active.md`
- [ ] Фаза 11.5 (release-eng PREP): `/release-engineering --prep-only --no-keystore` —
      иконки/splash/версия/store-metadata/CI (БЕЗ сборки AAB/APK)
- [ ] Фаза 12: Финальный отчёт

## Контракт артефактов Сессии 3 (должны существовать ПОСЛЕ)
- `production/runtime-screenshots/<ts>/*.png` (≥5 снимков) + `REPORT.md`
- `production/session-state/active.md` обновлён с verdict
- Иконки/splash/store-metadata готовы (release-ready, БЕЗ сборки артефактов)
- AAB+APK+архив — через отдельный запуск `/release-package`

## Ссылки на документацию
- Skill Сессии 3: `.claude/skills/autocreate-finalize/SKILL.md`
- Runtime verification: `.claude/skills/emulator-test/SKILL.md`
- Release packaging: `.claude/skills/release-package/SKILL.md`
```

### 10.7.2 — Spawn subagent через Agent tool

**ОБЯЗАТЕЛЬНО** вызвать Agent tool ИМЕННО ТАК (после записи handoff-файла):

```
Agent(
  description="AutoCreate finalize: runtime verification + report",
  prompt="""
Ты — Сессия 3 конвейера /autocreate (finalize) с чистым контекстом.

КОНТЕКСТ:
- Сессия 2 (имплементация) завершена (dart analyze чист, flutter test зелёный, UI-аудит пройден)
- Handoff-файл: production/session-state/autocreate-handoff.md — прочитай его ПЕРВЫМ
- Твой skill-план: .claude/skills/autocreate-finalize/SKILL.md — прочитай его ВТОРЫМ и выполняй

ТВОИ ЗАДАЧИ (в порядке):
1. Фаза 10.5 — runtime verification (см. .claude/skills/emulator-test/SKILL.md --quick)
   - auto-fix loop до 3 итераций при CRITICAL проблемах
   - + soak-проба: ~200 авто-действий по CDP, следить за ростом heap/console (утечки)
2. Фаза 10.6 — playtest (см. .claude/skills/playtest/SKILL.md): реальная игровая сессия,
   проверки P1–P10 (числа меняются, win/lose пути, живое поле, прогрессия), verdict PLAYABLE
3. Фаза 11 — обновить production/session-state/active.md с verdict
4. Фаза 11.5 (release-eng prep) — выполнить `/release-engineering --prep-only --no-keystore`
   (иконки, native splash, версия, store-metadata, CI). БЕЗ сборки AAB/APK и БЕЗ keystore —
   проект становится release-ready; артефакты соберёт пользователь через /release-package.
5. Фаза 12 — вернуть финальный отчёт в том формате, что указан в autocreate-finalize/SKILL.md

КРИТЕРИИ УСПЕХА:
- production/runtime-screenshots/<ts>/*.png (≥5 снимков) сохранены
- production/runtime-screenshots/<ts>/REPORT.md содержит verdict PASS/CONCERNS/FAIL
- production/session-state/active.md обновлён
- Иконки/splash сгенерированы, store/ создан (release-eng prep)
- Финальный отчёт Фазы 12 возвращён

ОГРАНИЧЕНИЯ:
- НЕ переписывай игровой код — Сессия 2 уже закончила имплементацию
- Допустимы ТОЛЬКО runtime-автофиксы UI-багов, которые видны на скриншотах
  или в logcat (overflow, setState after dispose, missing asset, null ValueNotifier)
- Не меняй game_config.dart, rtp-config.json, level-config.json — баланс/контент утверждены
- НЕ генерируй release-keystore и НЕ запускай /release-package — это явные действия пользователя
"""
)
```

### 10.7.3 — Вывод в основную conversation

После возврата subagent-а — в основную сессию сразу вернуть пользователю
**только** результат subagent-а (финальный отчёт Фазы 12). Не дублировать
работу. Если subagent упал — сообщить пользователю точную причину и команду
для ручного перезапуска в новой conversation: `/autocreate-finalize`.

---

## Гарантии качества (Quality Gates)

Каждая фаза имеет критерий выхода. Если критерий не выполнен — фаза повторяется.

### Сессия 1 — Pre-production (эта conversation, `autocreate`):

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 2. Bootstrap | `flutter pub get` — 0 errors; структура+layout выбраны | 3 |
| 3. Assets | Codex: ≤12 уникальных PNG-источников GPT Images 2.0, ≤2 technical recovery, кэш+классы в `design/asset-manifest.md`, ключевой фон вырезан через `tools/cutout.py`, `design/asset-prompts.md`; fallback вне Codex: SVG валидны | 2 |
| 3.5. Audio | 9 `.wav` синтезированы и непустые (`tools/synth_sfx.py`) | 2 |
| 3.6. Asset Review | `design/asset-review.md` — PASS, альфа подтверждена | 2 |
| 3.7. Content Data | `assets/data/*.json` валидны, N>1 уровней + economy | 2 |
| 3.8. Handoff & Spawn | `autocreate-handoff-1.md` записан + Agent tool (Сессия 2) вызван | 1 |

### Сессия 2 — Implementation (subagent, `autocreate-implement`):

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 4. Implementation | Все 5 агентов завершены (A/B/C/D/E) | 1 (Фаза 6 исправляет) |
| 4.5. Content wiring | Game принимает (mode,levelId); Level/Mode Select ↔ data | 2 |
| 5. Integration | Все 18 связей проверены (вкл. мета-сервисы) | 3 |
| 6. Build | `dart analyze` — 0 errors | 10 |
| 6.5. Gameplay Feel Pass | Поле живое (F1–F5), analyze+test чисты | 2 |
| 7. Tests | `flutter test` — all passed (вкл. test/services/) | 5 |
| 8. UI Audit | 100+ checks passed (меню/restraint/живой геймплей/compliance) | 3 |
| 9. Balance | RTP/difficulty по ВСЕЙ кривой контента в норме | 3 |
| 10. Crash Prevention | 20/20 + (gambling) age-gate/disclaimer, analyze+test clean | 3 |
| 10.7. Handoff & Spawn | `autocreate-handoff.md` записан + Agent tool (Сессия 3) вызван | 1 |

### Сессия 3 — Finalize (subagent, `autocreate-finalize`):

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|---------------|
| 10.5. Runtime Chrome | 0 CRITICAL visual + 0 FATAL exceptions (+ soak: нет утечки) | 3 (Chrome всегда доступен) |
| 10.6. Playtest | PLAYABLE (P1–P10, см. `/playtest`); 0 CRITICAL | 2 |
| 11. Session State | `active.md` обновлён с verdict | 1 |
| 11.5. Release-eng prep | Иконки/splash/store-metadata готовы (БЕЗ сборки AAB/APK) | 1 |
| 12. Final Report | Отчёт возвращён | 1 |

**АБСОЛЮТНЫЙ МИНИМУМ Сессии 1 (без него нельзя звать Сессию 2)**:
- Концепт+Production Plan, ассеты, 9 `.wav`, `assets/data/*.json` (N>1) созданы
- `autocreate-handoff-1.md` записан и Agent tool (Сессия 2) вызван

**АБСОЛЮТНЫЙ МИНИМУМ Сессии 2 (без него нельзя звать Сессию 3)**:
- `dart analyze lib/` — 0 errors; `flutter test` — all passed
- 15+ экранов, навигация работает, механика + контент (N уровней/режимы) + мета-системы на месте
- `autocreate-handoff.md` записан и Agent tool (Сессия 3) вызван

**АБСОЛЮТНЫЙ МИНИМУМ Сессии 3**:
- **Chrome скриншоты**: ≥5 снимков в `production/runtime-screenshots/<ts>/`
- **REPORT.md**: verdict PASS/CONCERNS/FAIL; **active.md** обновлён
- Release-eng PREP выполнен (иконки/splash/store-metadata; БЕЗ сборки AAB/APK)
- **Финальный отчёт** возвращён
