---
name: store-screenshots
description: "Генерация маркетинговых скриншотов для стора (Google Play / App Store): реальные кадры игры помещаются в рамку устройства на тематический фон с заголовком-подписью. Фоны генерируются через GPT Images 2.0 (Codex image generation), композитинг — через ImageMagick. Результат — набор store-ready PNG нужных размеров + feature graphic, упакованный в .zip в project_zip/ для скачивания."
argument-hint: "[--count N] [--lang ru|en] [--platform play|appstore] [--no-frame] [--device <id>]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Store Screenshots — Маркетинговые скрины для стора

**Цель**: подготовить готовые к загрузке в стор скриншоты, которые показывают игру «лицом»:
1. Реальные кадры геймплея (снятые на эмуляторе/устройстве)
2. Помещённые в рамку телефона (device frame) с тенью и скруглением
3. На тематическом фоне, сгенерированном через **GPT Images 2.0**
4. С коротким маркетинговым заголовком (подписью) сверху
5. Плюс Google Play **feature graphic** (1024×500)
6. Всё упаковано в `.zip` в `project_zip/` — этот архив автоматически становится скачиваемым артефактом в чате

> Это НЕ то же самое, что `/release-package`. `release-package` снимает «сырые» кадры экранов для документации.
> `store-screenshots` делает из них **полированные витринные изображения** для публикации в сторе.

**Важно**: навык НЕ меняет исходный код игры. Он только снимает кадры, генерирует фоны и собирает композиты.

---

## Размеры выходных изображений

| Платформа | Что | Размер (px) | Ориентация |
|-----------|-----|-------------|------------|
| Google Play (default) | Phone screenshot | **1080×1920** | портрет |
| Google Play | Feature graphic | **1024×500** | альбом |
| App Store (`--platform appstore`) | iPhone 6.7" | **1290×2796** | портрет |

Если игра альбомная (landscape) — поменять местами ширину/высоту скриншотов (1920×1080).

---

## Аргументы

- `--count N` — сколько витринных скринов сделать (default 5, максимум 8)
- `--lang ru|en` — язык подписей (default: язык концепта, обычно `ru`)
- `--platform play|appstore` — целевой размер (default: `play`)
- `--no-frame` — без рамки телефона (только скруглённая карточка кадра на фоне)
- `--device <id>` — конкретное устройство из `flutter devices`
- `--name <custom>` — переопределить имя архива (иначе из pubspec.yaml)

---

## Фаза 0 — Preflight [~15 сек]

### 0.1. Проверка проекта и извлечение метаданных

```bash
if [[ ! -f pubspec.yaml ]]; then
  echo "❌ pubspec.yaml не найден — store-screenshots требует Flutter-проект"
  exit 1
fi

PROJECT_NAME=$(grep -E "^name:" pubspec.yaml | awk '{print $2}')
[[ -z "$PROJECT_NAME" ]] && PROJECT_NAME="game"

TS=$(date +%Y%m%d-%H%M%S)
STORE_ROOT="project_zip"
STORE_DIR="$STORE_ROOT/$PROJECT_NAME-store-$TS"
RAW_DIR="$STORE_DIR/raw"          # сырые кадры игры
BG_DIR="$STORE_DIR/backgrounds"   # фоны от GPT Images 2.0
OUT_DIR="$STORE_DIR/store"        # финальные витринные PNG
mkdir -p "$STORE_DIR" "$RAW_DIR" "$BG_DIR" "$OUT_DIR"
echo "📁 Store-директория: $STORE_DIR"

# project_zip в .gitignore (архивы не место в git)
if [[ -f .gitignore ]] && ! grep -q "^project_zip/" .gitignore; then
  printf '\n# Store/release archives\nproject_zip/\n' >> .gitignore
fi
```

### 0.2. Проверка ImageMagick (нужен для композитинга)

```bash
if command -v magick >/dev/null 2>&1; then
  IM="magick"
elif command -v convert >/dev/null 2>&1; then
  IM="convert"   # ImageMagick 6
else
  echo "❌ ImageMagick не найден. Установить: apt-get install -y imagemagick"
  echo "   Без него композитинг невозможен."
  exit 1
fi
echo "🖼️  ImageMagick: $IM"
```

### 0.3. Контекст игры для темы и подписей

Прочитать через Read, если есть:
- `design/gdd/game-concept.md` → название игры, жанр, тема, цвета, настроение
- `design/structure.md` → ориентация (portrait/landscape), если указана

Извлечь и запомнить:
- **TITLE** — название игры (для feature graphic и подписей)
- **THEME** — визуальная вселенная (неоновое казино / зачарованный лес / космос / …)
- **COLORS** — палитра (для фона и текста)
- **MOOD** — настроение (электрическое / уютное / минимализм / …)

Если файлов нет — вывести найденное из `pubspec.yaml` (`name`, `description`) и продолжить с нейтральной темой.

---

## Фаза 1 — Базовые кадры игры [~3-5 мин]

Сначала **переиспользовать** уже снятые кадры, если они свежие:

```bash
# Ищем готовые кадры от release-package или emulator-test
FOUND=""
for d in project_zip/*/screenshots production/runtime-screenshots/*/ .claude/runtime-screenshots/*/; do
  [[ -d "$d" ]] || continue
  if ls "$d"/*.png >/dev/null 2>&1; then FOUND="$d"; fi
done

if [[ -n "$FOUND" ]]; then
  echo "♻️  Найдены готовые кадры: $FOUND — копирую в raw/"
  cp "$FOUND"/*.png "$RAW_DIR/" 2>/dev/null || true
fi
RAW_COUNT=$(ls -1 "$RAW_DIR"/*.png 2>/dev/null | wc -l | tr -d ' ')
echo "Кадров в raw/: $RAW_COUNT"
```

Если кадров **нет** (`RAW_COUNT == 0`) — снять свежий тур. Использовать логику захвата из
`.claude/skills/emulator-test/SKILL.md` (Фаза 1) и функцию `shoot()` с тройным fallback
(`flutter screenshot` ↔ `adb exec-out screencap` ↔ `adb pull`) и валидацией PNG-сигнатуры `89 50 4E 47`.

Снять минимально нужный набор «продающих» экранов (этого достаточно для витрины):

| Файл | Экран | Навигация |
|------|-------|-----------|
| 01-main-menu.png | Главное меню | sleep 3 после старта |
| 02-gameplay.png | Активный геймплей | тап PLAY, дождаться действия |
| 03-win.png | Выигрыш / победа / комбо | спровоцировать win overlay |
| 04-paytable.png | Правила / выплаты / прогресс | меню → Paytable/Rules |
| 05-extra.png | Любой яркий экран (бонус/лидерборд/профиль) | по ситуации |

Если устройство недоступно и кадров нет — **остановиться** и сообщить пользователю:
запустить эмулятор или сначала выполнить `/release-package`/`/emulator-test`, затем повторить.

```bash
RAW_COUNT=$(ls -1 "$RAW_DIR"/*.png 2>/dev/null | wc -l | tr -d ' ')
if [[ "$RAW_COUNT" -eq 0 ]]; then
  echo "❌ Нет кадров игры и нет активного устройства."
  echo "   Запустите эмулятор или сначала /emulator-test, затем повторите /store-screenshots."
  exit 1
fi
```

---

## Фаза 2 — Отбор кадров и маркетинговые подписи [~30 сек]

1. Выбрать `COUNT` (default 5) лучших кадров из `raw/` — приоритет: геймплей, выигрыш, главное меню, правила, бонус.
2. Прочитать выбранные кадры через Read (vision) и убедиться, что они не пустые/не сломанные.
3. Для каждого выбранного кадра написать **короткий маркетинговый заголовок** на языке `--lang`
   (default — язык концепта, обычно русский). Заголовки ≤ 32 символов, в духе сторов:

   Примеры (адаптировать под конкретную игру и жанр):
   - «Крути и выигрывай!»
   - «Захватывающий геймплей»
   - «Сорви джекпот»
   - «Прозрачные правила»
   - «Ежедневные бонусы»

Записать соответствие «кадр → заголовок» в переменные для Фазы 4 (массивы `SHOTS` и `CAPTIONS`).

---

## Фаза 3 — Тематические фоны через GPT Images 2.0 [~2-4 мин]

**Codex-путь (основной)**: использовать встроенную image generation Codex (**GPT Images 2.0**) — как в `/generate-png-asset`. Ключи не нужны.

Сгенерировать **один общий брендовый фон** на портретный размер (можно несколько — по одному на кадр, если нужна вариативность). Фон БЕЗ текста, БЕЗ телефонов, БЕЗ UI — только атмосфера, с читаемой/спокойной центральной зоной (туда ляжет рамка с кадром).

Промпт фона (подставить THEME/COLORS/MOOD из Фазы 0):

```
Vertical 9:16 mobile app store marketing background for a [THEME] game.
Rich atmospheric [THEME] scene, [COLORS] color palette, [MOOD] mood,
soft depth, subtle gradient, gentle vignette, empty calm center area
reserved for a phone mockup, NO text, NO words, NO phone, NO UI elements,
NO characters in the center, premium polished poster look, high quality, 1080x1920.
```

- В Codex: один вызов image generation = один фон. Сохранять в `$BG_DIR/bg.png` (или `bg-01.png`, `bg-02.png`…).
- Проверить файл: `file "$BG_DIR/bg.png"` должен показать PNG.
- Если Codex image generation недоступна → **legacy fallback**: Pollinations.ai `gptimage`/`flux` (см. `/generate-png-asset`), либо одноцветный/градиентный фон через ImageMagick:

```bash
# Фолбэк-фон: тематический градиент (если генерация изображений недоступна)
"$IM" -size 1080x1920 gradient:'#0b1026'-'#1b2a6b' "$BG_DIR/bg.png" 2>/dev/null || \
  convert -size 1080x1920 gradient:'#0b1026'-'#1b2a6b' "$BG_DIR/bg.png"
echo "⚠️ Использован градиентный фолбэк-фон (image generation недоступна)"
```

Цвета градиента подбирать под COLORS темы игры.

---

## Фаза 4 — Композитинг витринных скринов [~1-2 мин]

Параметры размера (из `--platform`):

```bash
# Google Play phone (default)
SW=1080; SH=1920
# App Store 6.7": SW=1290; SH=2796   (выставить при --platform appstore)

CAP_H=$(( SH / 6 ))            # высота зоны заголовка сверху
RADIUS=40                      # скругление кадра
BEZEL=28                       # толщина рамки телефона
TEXT_COLOR="#ffffff"           # цвет подписи (подобрать контрастный к фону)
```

### Хелпер: одна витрина из одного кадра

Для каждого выбранного кадра выполнить (подставляя `SHOT`, `CAPTION`, `BG`, `OUT`):

```bash
make_store_shot() {
  local SHOT="$1" CAPTION="$2" BG="$3" OUT="$4"

  # Целевая ширина кадра внутри рамки (с полями по бокам)
  local INNER_W=$(( SW * 78 / 100 ))

  # 1) Подогнать кадр по ширине, сохранив пропорции
  "$IM" "$SHOT" -resize "${INNER_W}x" /tmp/ss_resized.png

  # 2) Скруглить углы кадра (классический IM-рецепт через alpha-маску)
  local W H
  W=$(identify -format "%w" /tmp/ss_resized.png)
  H=$(identify -format "%h" /tmp/ss_resized.png)
  "$IM" /tmp/ss_resized.png \
    \( +clone -alpha extract -draw \
       "fill black polygon 0,0 0,$RADIUS $RADIUS,0 fill white circle $RADIUS,$RADIUS $RADIUS,0" \
       \( +clone -flip \) -compose Multiply -composite \
       \( +clone -flop \) -compose Multiply -composite \) \
    -alpha off -compose CopyOpacity -composite /tmp/ss_rounded.png

  # 3) Рамка телефона: тёмная скруглённая подложка чуть больше кадра
  if [[ "$NO_FRAME" != "1" ]]; then
    local FW=$(( W + BEZEL*2 )) FH=$(( H + BEZEL*2 )) FR=$(( RADIUS + BEZEL/2 ))
    "$IM" -size "${FW}x${FH}" xc:none \
      -fill '#0d0d12' -draw "roundrectangle 0,0 $((FW-1)),$((FH-1)) $FR,$FR" /tmp/ss_frame.png
    "$IM" /tmp/ss_frame.png /tmp/ss_rounded.png -gravity center -compose over -composite /tmp/ss_device.png
  else
    cp /tmp/ss_rounded.png /tmp/ss_device.png
  fi

  # 4) Тень устройства
  "$IM" /tmp/ss_device.png \
    \( +clone -background black -shadow 60x18+0+10 \) \
    +swap -background none -layers merge +repage /tmp/ss_shadow.png

  # 5) Фон → нужный размер
  "$IM" "$BG" -resize "${SW}x${SH}^" -gravity center -extent "${SW}x${SH}" /tmp/ss_bg.png

  # 6) Положить устройство на фон, ниже зоны заголовка
  "$IM" /tmp/ss_bg.png /tmp/ss_shadow.png \
    -gravity north -geometry "+0+${CAP_H}" -compose over -composite /tmp/ss_comp.png

  # 7) Заголовок сверху по центру (caption: автоперенос + масштаб)
  "$IM" /tmp/ss_comp.png \
    \( -background none -fill "$TEXT_COLOR" -gravity center \
       -size "$(( SW * 86 / 100 ))x$(( CAP_H * 70 / 100 ))" \
       caption:"$CAPTION" \) \
    -gravity north -geometry "+0+$(( CAP_H / 5 ))" -compose over -composite \
    "$OUT"

  if [[ -s "$OUT" ]]; then
    echo "✅ $(basename "$OUT")"
  else
    echo "⚠️ Не удалось собрать $(basename "$OUT")"
  fi
}
```

> Для ImageMagick 6 (`convert`) `\( +clone ... \)` синтаксис тот же; `identify` доступен отдельной командой.
> Если рецепт скругления падает — сделать прямые углы (шаг 2 пропустить, использовать `/tmp/ss_resized.png`).

Прогнать `make_store_shot` для всех выбранных кадров (по одному вызову на кадр), нумеруя выход:
`$OUT_DIR/store-01.png`, `store-02.png`, …

---

## Фаза 5 — Feature graphic (Google Play, 1024×500) [~30 сек]

Сделать горизонтальный баннер: тематический фон (можно отдельный GPT-фон 1024×500 или кроп общего) + название игры.

```bash
# Фон 1024x500 (GPT Images 2.0 — промпт landscape, либо кроп существующего bg)
"$IM" "$BG_DIR/bg.png" -resize "1024x500^" -gravity center -extent 1024x500 /tmp/fg_bg.png

# Название игры крупно, по центру
"$IM" /tmp/fg_bg.png \
  \( -background none -fill "$TEXT_COLOR" -gravity center -size 900x360 caption:"$TITLE" \) \
  -gravity center -compose over -composite \
  "$OUT_DIR/feature-graphic-1024x500.png"
echo "✅ feature-graphic-1024x500.png"
```

Для feature graphic предпочтительно сгенерировать отдельный landscape-фон через GPT Images 2.0
(промпт: `Horizontal 1024x500 app store feature banner for a [THEME] game, [COLORS], [MOOD], empty area for title text, no text, high quality`).

---

## Фаза 6 — STORE_INFO.md [~10 сек]

Создать `$STORE_DIR/STORE_INFO.md`:

```markdown
# Store Screenshots — [TITLE]

**Сборка**: [TS]
**Платформа**: [play|appstore]
**Размер скринов**: [SW]×[SH]
**Feature graphic**: 1024×500
**Язык подписей**: [lang]
**Фоны**: GPT Images 2.0 ([N] шт.) | fallback: [да/нет]

## Содержимое
- `store/` — [N] витринных скриншотов + feature graphic
- `raw/` — исходные кадры игры
- `backgrounds/` — сгенерированные фоны
- `STORE_INFO.md` — этот файл

## Подписи
| Файл | Заголовок |
|------|-----------|
| store-01.png | [caption 1] |
| store-02.png | [caption 2] |
| … | … |

## Как использовать
1. Google Play Console → Store presence → Main store listing → Phone screenshots → загрузить `store/store-*.png`
2. Feature graphic → загрузить `store/feature-graphic-1024x500.png`
3. App Store Connect → соответствующий размер дисплея

> Требования Google Play: 2–8 phone screenshots, JPEG/24-bit PNG, 320–3840 px по стороне.
```

---

## Фаза 7 — Упаковка в .zip [~30 сек]

```bash
ARCHIVE_NAME="$PROJECT_NAME-store-$TS.zip"
ARCHIVE_PATH="$STORE_ROOT/$ARCHIVE_NAME"

(cd "$STORE_ROOT" && zip -r "$ARCHIVE_NAME" "$(basename "$STORE_DIR")" \
  -x "*.DS_Store" -x "*/__pycache__/*")

if [[ ! -s "$ARCHIVE_PATH" ]]; then
  echo "❌ zip не создан — критическая ошибка упаковки"
  exit 1
fi

# Целостность
unzip -t "$ARCHIVE_PATH" >/dev/null 2>&1 || { echo "❌ Архив повреждён"; exit 1; }

# КРИТИЧНО: витринные PNG ДОЛЖНЫ быть внутри архива
CONTENTS=$(unzip -Z1 "$ARCHIVE_PATH")
STORE_PNG=$(echo "$CONTENTS" | grep -c "/store/.*\.png$" || true)
if [[ "$STORE_PNG" -lt 1 ]]; then
  echo "❌ В архиве нет витринных PNG (store/*.png)"
  echo "$CONTENTS" | head -20
  exit 1
fi

ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | awk '{print $1}')
if command -v sha256sum >/dev/null 2>&1; then
  ARCHIVE_SHA=$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')
else
  ARCHIVE_SHA=$(shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}')
fi
echo "$ARCHIVE_SHA  $ARCHIVE_NAME" > "$ARCHIVE_PATH.sha256"

echo "✅ Архив готов: $ARCHIVE_PATH ($ARCHIVE_SIZE), внутри store-PNG: $STORE_PNG"
echo "SHA256: $ARCHIVE_SHA"
```

> Архив сохраняется в `project_zip/` — worker веб-сервиса автоматически забирает оттуда
> `.zip` и регистрирует его как скачиваемый артефакт в чате (как у `/release-package`).

---

## Фаза 8 — Финальный отчёт

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖼️  STORE SCREENSHOTS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Игра: [TITLE]
📐 Размер: [SW]×[SH]  •  Платформа: [play|appstore]
🎨 Фоны: GPT Images 2.0 ([N])

📦 Архив: project_zip/[PROJECT_NAME]-store-[TS].zip ([SIZE])
   📂 store/ — [N] витринных PNG + feature-graphic-1024x500.png
   📂 raw/ — исходные кадры
   📂 backgrounds/ — фоны
   📄 STORE_INFO.md

🔒 SHA256: [SHA]

📋 Следующий шаг: скачать архив из чата и загрузить store/*.png в Google Play Console / App Store Connect.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Quality Gates

| Фаза | Критерий выхода | Макс. итераций |
|------|----------------|----------------|
| 0. Preflight | pubspec.yaml + ImageMagick есть | 1 (иначе abort) |
| 1. Кадры | ≥1 валидный PNG в raw/ | 2 (abort если 0 и нет устройства) |
| 2. Отбор/подписи | По заголовку на каждый выбранный кадр | 1 |
| 3. Фоны | ≥1 фон (GPT или fallback) | 2 |
| 4. Композиты | ≥1 store-*.png собран | 2 |
| 5. Feature graphic | feature-graphic-1024x500.png собран | 1 (non-fatal) |
| 6. Metadata | STORE_INFO.md создан | 1 |
| 7. Archive | .zip создан, store/*.png внутри, SHA256 записан | 1 |

---

## Запрещено в этом навыке

1. **Менять исходный код игры** — навык только снимает, генерирует и собирает.
2. **Коммитить в git** — только пользователь решает.
3. **Удалять `project_zip/` или его содержимое** — только добавляем.
4. **Публиковать что-либо в стор автоматически** — только локальный артефакт для скачивания.
5. **Вставлять фейковые UI/цифры** в кадры — на витрине только реальные кадры игры.
6. **Прятать ошибки генерации изображений** — при сбое GPT Images 2.0 показать причину и использовать fallback.
