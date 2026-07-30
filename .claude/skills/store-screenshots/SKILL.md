---
name: store-screenshots
description: "Полный комплект витринных материалов для Google Play / App Store: первые N скринов — ОДНА широкая концепт-иллюстрация игры БЕЗ текста, нарезанная на панели (вместе складываются в общую картину), дальше — реальные кадры игры в рамке телефона с маркетинговой типографикой (шрифт по mood игры или из assets/fonts, градиент в палитре DNA), плюс app-иконка, игровой эмблема-логотип и feature-graphic баннер. Иконка и логотип не только генерируются, но и ПРИМЕНЯЮТСЯ к проекту (flutter_launcher_icons + assets). Арт — через GPT Images 2.0, композитинг — через tools/store_compose.py. Результат — .zip в project_zip/ для скачивания."
argument-hint: "[--count 8] [--panels 3] [--platform play|appstore] [--lang ru|en] [--frame ios|android|none] [--type-mood bold|epic|tech|playful|elegant|retro|clean] [--no-captions] [--no-apply] [--no-wire-logo] [--size WxH]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Store Screenshots — витрина игры для стора

**Цель**: собрать всё, что стор просит показать на карточке приложения:

| # | Что | Откуда |
|---|-----|--------|
| 1…P | **Концепт-триптих** — ОДНА широкая иллюстрация мира игры **без текста**, нарезанная на `P` панелей. Рядом в сторе они читаются как одна общая картина | GPT Images 2.0 → `store_compose.py triptych` |
| P+1…N | **Реальные кадры игры** в рамке телефона на тематическом фоне + маркетинговая подпись | web_verify/эмулятор → `store_compose.py showcase` |
| — | **Feature graphic** 1024×500 (Google Play) — единственное место с именем игры | `store_compose.py banner` |
| — | **App-иконка** (launcher, все плотности + adaptive + iOS) — генерируется И применяется | GPT Images 2.0 → `store_compose.py icon` → `flutter_launcher_icons` |
| — | **Игровая эмблема** (лого игры) — ассет проекта + adaptive-foreground иконки | GPT Images 2.0 → `tools/cutout.py` |

Всё складывается в `.zip` в `project_zip/` — worker веб-сервиса автоматически регистрирует
его как скачиваемый артефакт в чате (как у `/release-package`).

> **Триптих — это НЕ экраны приложения.** Первые панели продают *мир и идею* игры: герой,
> ключевой объект механики, награда. Скриншоты интерфейса начинаются с панели P+1.
> Именно так устроены витрины топовых мобильных игр — сначала постер, потом продукт.

> **Текст и картинка разделены.** Триптих — чистое изображение, без единой буквы.
> Слова живут там, где их не разрежут отбивки стора: подписи на витринных кадрах и
> тайтл на feature graphic. Типографику рисует композитор (шрифт из mood игры или
> из `assets/fonts`, трекинг, градиент в палитре DNA) — у модели буквы никогда не просим.

> Не путать с `/release-package` (сырые кадры + APK для документации) и
> `/release-engineering` (подпись, AAB, метаданные). Здесь — **витрина**.

---

## Универсальность (жёсткое правило)

Навык обслуживает ЛЮБОЙ жанр и ЛЮБУЮ тему студии. Весь арт-дирекшен берётся из
`design/gdd/game-concept.md` (Design DNA) и `design/art-direction.md`.

- ❌ Нельзя по умолчанию рисовать казино/неон/золото/фиолетовый градиент.
- ✅ Лесной пазл → лес. Космический раннер → космос. Уютный кликер → уют.
- Тест: если триптих можно переставить на другую игру студии без изменений — он провален.

@.claude/rules/anti-slop-design.md

---

## Аргументы

| Аргумент | По умолчанию | Смысл |
|----------|--------------|-------|
| `--count N` | `8` | Всего скринов (Play: 2–8, App Store: до 10) |
| `--panels P` | `3` | Панелей в концепт-триптихе (`0` — выключить триптих) |
| `--platform play\|appstore` | `play` | Целевой размер |
| `--size WxH` | из platform | Явное переопределение размера панели |
| `--lang ru\|en` | язык концепта | Язык подписей и тайтла |
| `--frame ios\|android\|none` | `ios` | Рамка устройства на витринных кадрах |
| `--type-mood <mood>` | из DNA | Характер шрифта: `bold`/`epic`/`tech`/`playful`/`elegant`/`retro`/`clean` |
| `--font-dir <path>` | `assets/fonts` если есть | Шрифты самой игры — приоритетнее mood'а |
| `--no-captions` | выкл | Без маркетинговых подписей (чистые кадры) |
| `--no-apply` | выкл | Не трогать проект: только сгенерировать файлы в архив |
| `--no-wire-logo` | выкл | Не подключать эмблему в главное меню |
| `--name <custom>` | из pubspec | Имя архива |

### Размеры

| Платформа | Скриншот | Feature graphic |
|-----------|----------|-----------------|
| `play` | **1080×1920** (ровно 9:16 — проходит все проверки Play) | 1024×500 |
| `appstore` | **1290×2796** (iPhone 6.7"; 6.5" — `--size 1242x2688`) | — |

Если игра альбомная (`design/structure.md` → landscape) — поменять W и H местами
и ставить `--panels 0` (горизонтальный триптих из портретных панелей не читается).

---

## Фаза 0 — Preflight [~20 сек]

### 0.1. Проект и инструменты

```bash
[[ -f pubspec.yaml ]] || { echo "❌ Нет pubspec.yaml — нужен Flutter-проект"; exit 1; }

python3 -c "import PIL, numpy" 2>/dev/null || {
  echo "❌ Нужны Pillow + numpy (их же требует tools/cutout.py)."
  echo "   apt-get install -y python3-pil python3-numpy"
  exit 1
}
[[ -f tools/store_compose.py ]] || { echo "❌ Нет tools/store_compose.py"; exit 1; }

PROJECT_NAME=$(grep -m1 -E "^name:" pubspec.yaml | awk '{print $2}')
[[ -z "$PROJECT_NAME" ]] && PROJECT_NAME="game"

TS=$(date +%Y%m%d-%H%M%S)
STORE_ROOT="project_zip"
STORE_DIR="$STORE_ROOT/$PROJECT_NAME-store-$TS"
RAW_DIR="$STORE_DIR/raw"          # сырые кадры игры
ART_DIR="$STORE_DIR/art"          # сгенерированный бренд-арт
OUT_DIR="$STORE_DIR/store"        # финальные витринные PNG
mkdir -p "$RAW_DIR" "$ART_DIR" "$OUT_DIR" assets/branding
echo "📁 $STORE_DIR"

if [[ -f .gitignore ]] && ! grep -q "^project_zip/" .gitignore; then
  printf '\n# Store/release archives\nproject_zip/\n' >> .gitignore
fi
```

### 0.2. Бренд-бриф из концепта

Прочитать через Read (если есть): `design/gdd/game-concept.md`, `design/art-direction.md`,
`design/structure.md`. Извлечь и **записать в `$STORE_DIR/STORE_BRIEF.md`**:

| Переменная | Что это | Пример (условная игра про лес) |
|-----------|---------|-------------------------------|
| `TITLE` | Человекочитаемое имя игры | «Лесной Шёпот» |
| `TAGLINE` | ≤ 42 симв., одна выгода игрока | «Собирай руны. Буди лес.» |
| `GENRE` | Жанр из CLAUDE.md | puzzle / match-3 |
| `HERO` | Главный герой/субъект мира | древний дух-олень с рунами на рогах |
| `MECHANIC_OBJECT` | Предмет, олицетворяющий механику | светящаяся руна-кристалл |
| `REWARD` | Награда/цель мира | пробуждённое Древо-сердце |
| `PALETTE` | 3–5 цветов из DNA | мшисто-зелёный, янтарь, тёплый белый |
| `MOOD` | Настроение | тёплое, живое, чуть волшебное |
| `RENDER` | Стиль рендера из DNA | material-grounded 3D, мягкий свет |
| `DNA_BG` | HEX фона из DNA (для adaptive-иконки) | `#122015` |
| `TYPE_MOOD` | Характер шрифта: `bold` / `epic` / `tech` / `playful` / `elegant` / `retro` / `clean` | `playful` |
| `TEXT_1` | HEX основного цвета текста (светлый конец) | `#FFF7E6` |
| `TEXT_2` | HEX второго стопа градиента = акцент из DNA | `#E0A63C` |

Если концепта нет — вывести из `pubspec.yaml` (`name`, `description`) + прочитать 2–3
ассета игры через Read (vision) и описать стиль по ним. **Нейтральная тема, не казино.**

`TYPE_MOOD` выбирается по DNA, а не по жанру: `Typography` из Design DNA и `MOOD`
задают характер. Космос/кибер → `tech`; миф/фэнтези → `epic`; уютное/детское →
`playful`; премиум-минимализм → `elegant`; пиксель-аркада → `retro`; сомневаешься →
`bold`. Один и тот же mood на все игры — это slop (см. `anti-slop-design.md`).

`TEXT_1`/`TEXT_2` — вертикальный градиент заливки текста. `TEXT_2` берётся из
**акцентного цвета DNA**, поэтому типографика витрины сразу принадлежит миру игры.
Если акцент тёмный (текст станет нечитаемым) — оставить `TEXT_2` пустым, будет
ровная заливка `TEXT_1`.

### 0.3. Шрифты: что реально доступно

```bash
FONT_DIR_ARG=""
[[ -d assets/fonts ]] && FONT_DIR_ARG="--font-dir assets/fonts"

python3 tools/store_compose.py fonts --mood-only \
  --type-mood "${TYPE_MOOD:-bold}" $FONT_DIR_ARG \
  --sample "$TITLE $TAGLINE"
```

Смысл шага: **проверить покрытие глифов ДО композитинга**. Большинство display-шрифтов
(Bodoni, Didot, Impact, Anton, Orbitron, Press Start 2P) — только латиница, а подписи
здесь русские: такой шрифт нарисует не текст, а ряд пустых прямоугольников. Инструмент
сам исключает шрифты без нужных глифов и печатает, какие семейства пропустил.

| Вывод | Действие |
|-------|----------|
| `✅ <mood> display=<Имя>.ttf` | всё хорошо, идти дальше |
| `⚠️ ... has no characterful face here` | в образе нет display-шрифтов. Если у игры есть свои (`assets/fonts`) — они уже подхватятся через `--font-dir`. Иначе продолжать: тайтл будет набран UI-шрифтом (отметить в отчёте как CONCERNS) |
| `no glyphs for the probe: X, Y` | норма: X/Y не покрывают алфавит и корректно пропущены |

`assets/fonts` игры **приоритетнее** любого mood: витрина, набранная шрифтом игры,
выглядит как один продукт. Иконочные шрифты (`MaterialIcons` и подобные) отбрасываются.

---

## Фаза 1 — Сырые кадры игры [~1–5 мин]

> **Кадр обязан быть в пропорции телефона** — высота/ширина ≈ **2.0–2.2** (390×844 → 2.16).
> Почти квадратный кадр (≈1.5) превращает мокап в приплюснутый планшет, и витрина
> разваливается — никакой композитинг это не чинит. Причина такого кадра: старые версии
> снимали по `--window-size`, который headless Chrome трактует как пожелание.
> Сейчас `web_verify.mjs` жёстко задаёт вьюпорт через `Emulation.setDeviceMetricsOverride`.

### 1.1. Переиспользовать готовые кадры — только если они правильной формы

```bash
FOUND=""
for d in production/runtime-screenshots/*/ .claude/runtime-screenshots/*/ project_zip/*/screenshots; do
  [[ -d "$d" ]] && ls "$d"/*.png >/dev/null 2>&1 && FOUND="$d"
done
if [[ -n "$FOUND" ]]; then
  cp "$FOUND"/*.png "$RAW_DIR/" 2>/dev/null || true
  # Отбраковать всё, что не в пропорции телефона (старые «квадратные» кадры)
  python3 - "$RAW_DIR" <<'PY'
import sys, pathlib
from PIL import Image
bad = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("*.png")):
    with Image.open(p) as im:
        w, h = im.size
    ar = h / w
    if not (1.9 <= ar <= 2.35):
        print(f"🗑  {p.name}: {w}x{h} (h/w={ar:.2f}) — не телефон, удаляю")
        p.unlink(); bad += 1
print(f"отбраковано: {bad}")
PY
fi
RAW_COUNT=$(ls -1 "$RAW_DIR"/*.png 2>/dev/null | wc -l | tr -d ' ')
echo "Пригодных кадров в raw/: $RAW_COUNT"
```

### 1.2. Снять свежий тур, если пригодных кадров нет

**Через Chrome/CDP** (эмулятор не нужен):

```bash
flutter run -d web-server --web-port=0 > .claude/runtime-logs/flutter-run.log 2>&1 &
# дождаться URL, затем:
node tools/web_verify.mjs --url "$WEB_URL" --out "$RAW_DIR" \
  --size 390x844 --dpr 3 --budget 180 --quick
```

| Флаг | Зачем именно здесь |
|------|--------------------|
| `--size 390x844` | пропорция телефона 2.16 — то, во что рисуется мокап |
| `--dpr 3` | кадр 1170×2532: в витринный слот (~890 px) идёт с запасом, без апскейла. По умолчанию `--dpr 2` — этого хватает; `3` берём ради максимальной чёткости, т.к. здесь важна только картинка, а не скорость прогона |

Полная процедура запуска/ожидания — `.claude/skills/autocreate-finalize/SKILL.md` (Фаза 10.5).
Android-fallback (`flutter screenshot` / `adb exec-out screencap`) — `.claude/skills/emulator-test/SKILL.md`.

Нужный минимум «продающих» кадров: главное меню, активный геймплей, момент выигрыша/успеха,
правила/прогресс, любой яркий экран (бонус/лидерборд/профиль).

```bash
RAW_COUNT=$(ls -1 "$RAW_DIR"/*.png 2>/dev/null | wc -l | tr -d ' ')
[[ "$RAW_COUNT" -eq 0 ]] && { echo "❌ Нет кадров игры. Запустите /emulator-test и повторите."; exit 1; }
head -c 400 "$RAW_DIR/manifest.json" 2>/dev/null   # поле "capture" — фактический размер
```

**Обязательно** прочитать отобранные кадры через Read (vision): пустой/чёрный/сломанный
кадр на витрину не идёт. Битые — исключить из отбора.

---

## Фаза 2 — Генерация бренд-арта [~3–5 мин]

**Codex-путь (основной)**: встроенная image generation — **GPT Images 2.0**, fallback
**GPT Images / default**. Ключи не нужны. Правила и fallback-цепочка — `/generate-png-asset`.
**Один вызов image generation = один ассет.** Все промпты дописать в `design/asset-prompts.md`.

### 2.1. Панорама-концепт (самый важный ассет)

Просить **самый широкий landscape**, который отдаёт модель (обычно 1536×1024). Нарезку на
панели делаем мы — модель об этом знать НЕ должна, иначе она нарисует коллаж с рамками.

```
One single seamless ultra-wide landscape key-art illustration for a [GENRE] mobile game — [MOOD] [THEME] world.
Composition: [HERO] as the dominant figure just left of centre; [MECHANIC_OBJECT] glowing in the middle;
[REWARD] rising on the right — three distinct focal points spread evenly across the width, so that ANY
vertical third of this picture is a strong standalone image. Keep faces and key silhouettes AWAY from the
vertical lines at 1/3 and 2/3 of the width. [PALETTE] palette, [RENDER] render, dramatic key light from the
upper left, volumetric depth, believable materials, full-bleed edge-to-edge artwork, poster quality.
NO text, NO words, NO numbers, NO letters, NO logo, NO watermark, NO UI, NO phone, NO device mockup,
NO frame, NO border, NO panels, NO split-screen, NO collage, NO grid, NO diptych, NO triptych divisions.
Widest landscape aspect available, highest resolution.
```

Сохранить в `$ART_DIR/keyart.png`, проверить: `file "$ART_DIR/keyart.png"` → PNG.

> Запреты на текст/панели — не украшение промпта. Без них модель рисует «постер» с
> нечитаемыми буквами и разделительными рамками, и триптих разваливается.

### 2.2. Арт app-иконки

```
Square full-bleed app icon artwork for a [GENRE] mobile game — [THEME].
[MECHANIC_OBJECT or HERO head] as one bold hero object, centred, filling most of the frame,
[RENDER] render, [PALETTE] palette, rich materials, dramatic rim light, atmospheric background
consistent with the game world. Instantly readable as a 48 px launcher icon: ONE clear subject,
strong silhouette, high contrast. NO text, NO words, NO letters, NO logo, NO UI, NO border,
NO rounded-corner mask, NO drop shadow outside the artwork. 1024x1024.
```

Сохранить в `$ART_DIR/icon_art.png`.

### 2.3. Игровая эмблема (лого игры)

Генерируется на **плоском ключевом фоне** и вырезается — правила ключа см.
«Ключевой цвет фона» в `/generate-png-asset` (по умолчанию `pure magenta #FF00FF`;
если в палитре есть пурпур/розовый — `pure green #00FF00`).

```
Single hero emblem for a [GENRE] game — [MECHANIC_OBJECT / crest of THEME], one centred object,
[RENDER] render, [PALETTE] palette, believable materials, soft key light from top-left plus subtle rim,
crisp clean silhouette readable at 64 px, premium studio product shot,
flat solid single-colour [KEY COLOUR] background, no gradient, no vignette, no shadow on the background,
subject fully inside frame, NO text, NO letters, NO border, NO scene, NO sprite sheet. 1024x1024.
```

Сохранить в `$ART_DIR/emblem.png`, затем **обязательно** вырезать фон:

```bash
python3 tools/cutout.py "$ART_DIR/emblem.png" --type icon
```

Вывод `✗` = ассет непригоден (фон не плоский / не тот ключ) → **перегенерировать**,
не «дожимать» вручную.

---

## Фаза 3 — Иконка и эмблема: сборка и ПРИМЕНЕНИЕ [~2 мин]

Пропустить всю фазу при `--no-apply` (тогда файлы только кладутся в архив).

### 3.1. Сборка комплекта иконок

```bash
cp "$ART_DIR/icon_art.png" assets/branding/icon_art.png
cp "$ART_DIR/emblem.png"   assets/branding/emblem.png

python3 tools/store_compose.py icon \
  --src assets/branding/icon_art.png \
  --fg-src assets/branding/emblem.png \
  --out-dir assets/branding \
  --bg "$DNA_BG"
```

Получаем:
- `assets/branding/app_icon.png` — 1024×1024 мастер (без альфы, годится для iOS)
- `assets/branding/app_icon_fg.png` — adaptive foreground (субъект в safe-zone 62%)
- `assets/branding/store_icon_512.png` — иконка листинга Play (512×512)

### 3.2. Применение иконки к проекту

```yaml
# pubspec.yaml
dev_dependencies:
  flutter_launcher_icons: ^0.14.1

flutter_launcher_icons:
  image_path: "assets/branding/app_icon.png"
  android: true
  ios: true
  remove_alpha_ios: true
  web: { generate: true }
  adaptive_icon_background: "[DNA_BG]"
  adaptive_icon_foreground: "assets/branding/app_icon_fg.png"
```

```bash
flutter pub get
dart run flutter_launcher_icons 2>&1 | tail -5
ls android/app/src/main/res/mipmap-xxxhdpi/ | head   # проверка, что иконки реально легли
```

> Если `app_icon_fg.png` не создан (эмблема без альфы) — убрать ОБЕ строки
> `adaptive_icon_*`, иначе Android обрежет артворк по маске.

### 3.3. Эмблема как ассет игры

```bash
mkdir -p assets/images/ui
cp assets/branding/emblem.png assets/images/ui/ui_game_logo.png
grep -q "assets/images/ui/" pubspec.yaml || echo "⚠️ добавить assets/images/ui/ в pubspec assets"
```

Добавить константу в `lib/assets.dart` (или его аналог по `design/structure.md`):

```dart
static const String uiGameLogo = 'assets/images/ui/ui_game_logo.png';
```

### 3.4. Подключение эмблемы в главное меню (пропустить при `--no-wire-logo`)

**Только если** в главном меню сейчас нет брендового изображения (заголовок — голый `Text`).
Если лого уже есть — ничего не трогать, только сообщить.

Вставить над заголовком, с обязательными размерами и fallback (правила `ui-code.md` §2.4):

```dart
Image.asset(
  GameAssets.uiGameLogo,
  width: 128,
  height: 128,
  errorBuilder: (_, __, ___) => const SizedBox(width: 128, height: 128),
),
```

Затем **обязательная проверка и откат при ошибке**:

```bash
dart analyze lib/ 2>&1 | tee /tmp/store_analyze.log
if grep -q " error " /tmp/store_analyze.log; then
  echo "❌ Правка меню сломала анализ — откатываю"
  git checkout -- <изменённый файл>   # или Edit-ом вернуть исходный текст
fi
```

Игровую логику, состояния, конфиги — **не трогать**. Разрешена ровно одна вставка виджета.

---

## Фаза 4 — Концепт-триптих: скрины 1…P [~1 мин]

> **Триптих не содержит текста.** Ни тайтла, ни таглайна, ни логотипа — только
> чистая картинка. Причины: (1) буквы поперёк шва разрезаются отбивками стора;
> (2) лockup внутри одной панели убивает иллюзию единого изображения; (3) панорама
> — это концепт-постер мира игры, слова продают его на витринных кадрах и баннере.
> Флаги `--title/--tagline/--logo` инструмент **отклоняет с ошибкой** — это не забытая
> опция, а осознанное ограничение.

```bash
# Размер панели
case "${PLATFORM:-play}" in
  appstore) SW=1290; SH=2796 ;;
  *)        SW=1080; SH=1920 ;;
esac
# --size WxH переопределяет

python3 tools/store_compose.py triptych \
  --src "$ART_DIR/keyart.png" \
  --out "$OUT_DIR" \
  --panels "${PANELS:-3}" \
  --size "${SW}x${SH}"
```

Даёт `store-01.png … store-0P.png` + `_panorama-preview.png` (склейка со швами).

### Обязательный vision-контроль швов

Прочитать `_panorama-preview.png` через Read и проверить:

| Проверка | Провал → действие |
|----------|-------------------|
| Лицо/голова героя рассечены розовой линией шва | сдвинуть кадрирование (ниже) |
| Панель целиком пустая (небо/фон, нет фокуса) | перегенерировать панораму с акцентом на 3 фокуса |
| В арте появились буквы/цифры/рамки/коллаж | перегенерировать, усилив NO-text/NO-panels |

Сдвиг кадрирования **без перегенерации** (дешёвый фикс, пробовать первым):

```bash
python3 tools/store_compose.py triptych --src "$ART_DIR/keyart.png" --out "$OUT_DIR" \
  --panels 3 --size "${SW}x${SH}" --zoom 1.12 --offset -0.6
```

`--offset` от `-1` (влево) до `1` (вправо); `--zoom > 1` создаёт запас для сдвига.
Максимум **2** итерации, потом принять лучший вариант и отметить в отчёте.

При `--panels 0` фаза пропускается целиком, все скрины — витринные кадры (Фаза 5).

---

## Фаза 5 — Витринные кадры игры: скрины P+1…N [~1 мин]

### 5.1. Отбор и подписи

Выбрать `COUNT - PANELS` лучших кадров из `raw/`. Приоритет: активный геймплей → момент
выигрыша/успеха → главное меню → правила/прогресс → бонус/лидерборд.

Для каждого написать подпись на `--lang` (по умолчанию язык концепта, обычно русский),
**≤ 32 символов**, про выгоду игрока, а не про экран:

- ✅ «Собирай цепочки из 3+» / «Один тап — и буря» / «Открывай новые миры»
- ❌ «Главное меню» / «Экран правил» / «Скриншот 3»

При `--no-captions` подписи не рисуются (чистые кадры, как в референсных витринах).

### 5.2. Композитинг

Фон витринных кадров — **та же панорама**: витрина читается как единый набор.

```bash
i=$((PANELS + 1))
for pair in "02-menu.png|Играй с первого тапа" "04-game-action.png|Собирай цепочки из 3+"; do
  SHOT="${pair%%|*}"; CAP="${pair##*|}"
  python3 tools/store_compose.py showcase \
    --shot "$RAW_DIR/$SHOT" \
    --bg "$ART_DIR/keyart.png" \
    --out "$OUT_DIR/$(printf 'store-%02d.png' "$i")" \
    --size "${SW}x${SH}" \
    --caption "$CAP" \
    --type-mood "${TYPE_MOOD:-bold}" \
    --caption-color "${TEXT_1:-#FFFFFF}" \
    --caption-color2 "${TEXT_2:-}" \
    $FONT_DIR_ARG \
    --frame "${FRAME:-ios}" \
    --bg-treatment soft
  i=$((i + 1))
done
```

Типографика подписи (то, что отличает витрину от скриншота с текстом сверху):

- **шрифт** — из `--type-mood` (или из `assets/fonts` игры через `--font-dir`), с
  автоматическим отсевом шрифтов без нужных глифов;
- **трекинг и регистр** — заданы mood'ом, не одинаковы для всех игр;
- **градиент** `--caption-color` → `--caption-color2` в палитре DNA;
- **тень** — реальный блюр по маске текста, а не жёсткая копия со сдвигом;
- **акцентная черта** над подписью в цвете `--caption-color2` (убрать: `--no-rule`);
- **балансировка строк** — перенос выравнивает длины строк вместо «жадного» переноса,
  который оставляет одинокое слово во второй строке и мельчит кегль.

| Флаг | Когда менять |
|------|--------------|
| `--fit bleed` | Нужен телефон крупнее: он занимает всю ширину, а низ уходит за край кадра. **Осторожно с играми, где управление внизу экрана** — оно обрежется |
| `--frame android` | Игра позиционируется под Android / DNA просит punch-hole |
| `--frame none` | Нужен чистый скруглённый кадр без телефона |
| `--bg-treatment blur` | Кадр теряется на слишком детальном фоне |
| `--scale 0.88` | Телефон кажется мелким, по бокам много пустого фона |
| `--tracking 0.0` | Mood растянул буквы сильнее, чем нужно этой игре |
| `--no-uppercase` | Капс не идёт настроению (уютные/детские игры) |
| `--text-outline 0.03` | Подпись всё ещё теряется: тонкий контур в дополнение к тени |
| `--scrim 0.85` | Верх панорамы слишком светлый под подписью |

По умолчанию `--fit contain`: телефон виден целиком, ничего не обрезается. Полоса подписи
подстраивается под реальную высоту текста (одна строка не съедает столько же, сколько две),
поэтому на короткой подписи телефон автоматически становится крупнее.

Если инструмент печатает `⚠️ ... is 1.5 tall/wide — that is not phone-shaped`, значит в
`raw/` просочился старый квадратный кадр — вернуться к Фазе 1.2 и переснять.

### 5.3. Обязательный vision-контроль типографики

Прочитать **один** готовый витринный кадр через Read и проверить:

| Проверка | Провал → действие |
|----------|-------------------|
| Вместо букв — пустые прямоугольники (▯▯▯) | шрифт без нужных глифов. Вернуться к Фазе 0.3, проверить вывод `fonts`, при `--font`/`--font-regular` — убрать их |
| Подпись не читается на фоне | `--scrim 0.85`, затем `--text-outline 0.03` |
| Вторая строка — одно короткое слово | сократить подпись до ≤ 32 символов |
| Буквы слиплись или разъехались | `--tracking` (0.0 … 0.14) |

---

## Фаза 6 — Feature graphic 1024×500 [~20 сек]

Google Play. Безопасная зона — центральные 924×432; по краям текст не ставить.

```bash
python3 tools/store_compose.py banner \
  --keyart "$ART_DIR/keyart.png" \
  --shot "$RAW_DIR/02-menu.png" \
  --out "$OUT_DIR/feature-graphic-1024x500.png" \
  --title "$TITLE" \
  --tagline "$TAGLINE" \
  --type-mood "${TYPE_MOOD:-bold}" \
  --title-color "${TEXT_1:-#FFFFFF}" \
  --title-color2 "${TEXT_2:-}" \
  $FONT_DIR_ARG \
  --frame "${FRAME:-ios}"
```

Баннер — **единственное место, где стоит имя игры**, поэтому именно здесь важен
характер шрифта. Тайтл набирается display-шрифтом mood'а с градиентом, таглайн —
парным body-шрифтом (другой кегль, другой вес, без капса): разные роли выглядят
по-разному. Между ними — акцентная черта (убрать: `--no-rule`).

`--shot` не обязателен: без него баннер — чистая панорама с тайтлом.
Для App Store feature graphic не нужен — при `--platform appstore` шаг можно пропустить.

---

## Фаза 7 — Верификация [~30 сек]

```bash
python3 tools/store_compose.py check --dir "$OUT_DIR"
```

Проверяет: файлы читаются, стороны 320…3840 px, размер ≤ 8 МБ, единый размер у всех `store-*`.

Плюс **vision-проверка** через Read по каждому финальному PNG:

- [ ] Панели 1…P складываются в одну картину, швы не рвут ключевые объекты
- [ ] **На панелях 1…P нет ни одной буквы** (ни сгенерированной, ни нарисованной)
- [ ] На витринных кадрах виден РЕАЛЬНЫЙ интерфейс игры, не заглушка
- [ ] Подписи читаются (контраст ≥ 4.5:1), не обрезаны, без опечаток
- [ ] **Каждый глиф — буква, а не пустой прямоугольник** (шрифт покрывает алфавит)
- [ ] Шрифт подписей и тайтла один и тот же, и он соответствует миру игры
- [ ] Нигде нет сгенерированных букв-артефактов
- [ ] Иконка узнаваема в 48 px (уменьшить `store_icon_512.png` и посмотреть)
- [ ] Стиль триптиха, кадров, баннера и иконки — один мир

Любой провал → исправить и пересобрать конкретный файл. Не прятать проблему в отчёте.

---

## Фаза 8 — STORE_INFO.md [~10 сек]

```markdown
# Store Kit — [TITLE]

**Сборка**: [TS] • **Платформа**: [play|appstore] • **Скрины**: [SW]×[SH]

## Состав
| Файл | Что |
|------|-----|
| store-01…0P.png | Концепт-триптих — одна панорама, [P] панелей |
| store-0(P+1)…N.png | Кадры игры в рамке телефона |
| feature-graphic-1024x500.png | Feature graphic (Google Play) |
| branding/store_icon_512.png | Иконка листинга 512×512 |
| _panorama-preview.png | Склейка триптиха со швами (проверочная, НЕ загружать) |

## Подписи
| Файл | Заголовок |
|------|-----------|
| … | … |

## Применено к проекту
- App-иконка: `flutter_launcher_icons` → Android (adaptive) + iOS + web — [да/нет]
- Эмблема: `assets/images/ui/ui_game_logo.png` — [зарегистрирована / подключена в меню / нет]

## Порядок загрузки
1. Play Console → Store presence → Main store listing → Phone screenshots →
   `store-01 … store-0N.png` **строго по порядку номеров** (иначе триптих развалится).
2. Feature graphic → `feature-graphic-1024x500.png`
3. App icon → `branding/store_icon_512.png`
4. App Store Connect → тот же порядок в нужном размере дисплея.

> Play: 2–8 скринов, PNG/JPEG, сторона 320–3840 px, ≤ 8 МБ. App Store: до 10.
> `_panorama-preview.png` — служебный файл, в стор его не грузить.
```

---

## Фаза 9 — Упаковка [~30 сек]

```bash
mkdir -p "$STORE_DIR/branding"
cp assets/branding/store_icon_512.png assets/branding/app_icon.png "$STORE_DIR/branding/" 2>/dev/null || true
cp assets/branding/app_icon_fg.png "$STORE_DIR/branding/" 2>/dev/null || true

ARCHIVE_NAME="$PROJECT_NAME-store-$TS.zip"
ARCHIVE_PATH="$STORE_ROOT/$ARCHIVE_NAME"
(cd "$STORE_ROOT" && zip -r "$ARCHIVE_NAME" "$(basename "$STORE_DIR")" -x "*.DS_Store")

[[ -s "$ARCHIVE_PATH" ]] || { echo "❌ zip не создан"; exit 1; }
unzip -t "$ARCHIVE_PATH" >/dev/null 2>&1 || { echo "❌ Архив повреждён"; exit 1; }

STORE_PNG=$(unzip -Z1 "$ARCHIVE_PATH" | grep -c "/store/store-.*\.png$" || true)
[[ "$STORE_PNG" -lt 1 ]] && { echo "❌ В архиве нет витринных PNG"; unzip -Z1 "$ARCHIVE_PATH" | head -20; exit 1; }

if command -v sha256sum >/dev/null 2>&1; then
  ARCHIVE_SHA=$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')
else
  ARCHIVE_SHA=$(shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}')
fi
echo "$ARCHIVE_SHA  $ARCHIVE_NAME" > "$ARCHIVE_PATH.sha256"
echo "✅ $ARCHIVE_PATH ($(du -h "$ARCHIVE_PATH" | awk '{print $1}')), store-PNG: $STORE_PNG"
```

---

## Фаза 10 — Финальный отчёт

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖼️  STORE KIT COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 [TITLE] — [TAGLINE]
📐 [SW]×[SH] • [play|appstore]

🎨 Концепт-триптих: панели 01–0[P] = одна панорама [3*SW]×[SH]
📱 Кадры игры:      панели 0[P+1]–0[N], рамка [ios|android|none]
🏞️  Feature graphic: 1024×500
🎭 Иконка:          применена (Android adaptive + iOS + web) [или: только файлы]
🔰 Эмблема:         assets/images/ui/ui_game_logo.png [подключена в меню / зарегистрирована]

📦 project_zip/[PROJECT_NAME]-store-[TS].zip ([SIZE])
🔒 SHA256: [SHA]

📋 Дальше: скачать архив из чата → загрузить store-*.png ПО ПОРЯДКУ в Play Console.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quality Gates

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|----------------|
| 0. Preflight | pubspec + Pillow/numpy + store_compose.py | 1 (иначе abort) |
| 0.3. Шрифты | `fonts` отработал; выбранный display-шрифт покрывает алфавит подписей | 1 (CONCERNS, не abort) |
| 1. Кадры | ≥ 1 непустой PNG в `raw/`, **все в пропорции телефона h/w 1.9–2.35** | 2 (abort если 0) |
| 2. Арт | keyart + icon_art + emblem сгенерированы, emblem с альфой | 2 на ассет |
| 3. Иконка | `flutter_launcher_icons` отработал, mipmap непустой | 2 |
| 3.4. Меню | `dart analyze` без errors (иначе откат) | 1 |
| 4. Триптих | P панелей **без единой буквы** + швы не рвут ключевые объекты (vision) | 2 |
| 5. Витрина | `COUNT-P` кадров собраны; подписи читаемы и **не пустые прямоугольники** (vision 5.3) | 2 |
| 6. Banner | feature-graphic собран | 1 (non-fatal) |
| 7. Verify | `check` без ошибок + vision-чеклист пройден | 2 |
| 9. Archive | zip создан, `store-*.png` внутри, SHA256 записан | 1 |

---

## Запрещено в этом навыке

1. **Менять игровую логику, состояния, конфиги, баланс.** Разрешены ровно: `assets/branding/*`,
   `assets/images/ui/ui_game_logo.png`, `pubspec.yaml` (иконки/ассеты), константа в `lib/assets.dart`
   и ОДНА вставка `Image.asset` в главном меню.
2. **Коммитить в git** — решает только пользователь.
3. **Удалять `project_zip/`** или существующие ассеты проекта — только добавляем.
4. **Публиковать что-либо в стор** — только локальный артефакт.
5. **Рисовать фейковый UI/цифры** в кадрах — на витрине только реальные кадры игры.
6. **Просить у модели текст, буквы, цифры, рамки или «триптих/панели»** внутри арта —
   нарезку делает `store_compose.py`, буквы рисует композитор.
7. **Применять казино/неон по умолчанию** — арт-дирекшен только из Design DNA игры.
8. **Прятать провалы генерации** — показать причину и fallback.
9. **Оставлять `_panorama-preview.png` в списке «для загрузки»** — это проверочный файл.
10. **Ставить текст на концепт-триптих** — панорама остаётся чистым изображением (Фаза 4).
11. **Использовать один и тот же `--type-mood` для всех игр** — это такой же slop, как
    один и тот же неон на всех: mood выводится из Design DNA конкретной игры.
12. **Отдавать витрину, не посмотрев на подпись глазами (Фаза 5.3)** — шрифт без
    кириллицы рисует пустые прямоугольники, и `check` этого не поймает.
