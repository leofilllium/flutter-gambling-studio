---
name: generate-png-asset
description: "Генерация PNG-ассетов. В Codex основной путь — GPT Images 2.0, fallback — GPT Images/default Codex image generation; внешние API только как legacy fallback. Простые ассеты генерируются на плоском ключевом фоне (chroma key) и вырезаются через tools/cutout.py."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[описание] | [--batch список] | [--from-concept] | [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `generate-png-asset` — PNG ассеты для мини-игр

## Правило по умолчанию

1. **Исключение для `/autocreate`:** если вызов идёт из `/autocreate` или `--from-concept`
   полного проекта в Codex, PNG/image generation является дефолтом даже без `--png`; SVG
   запрещён без явного `--svg`.
2. Если пользователь не просил PNG/image generation и это НЕ `/autocreate` — вернуться к
   `/generate-asset` и создать **SVG**.
3. Если пользователь явно просил PNG/image generation и агент работает в **Codex** — использовать **GPT Images 2.0** первым. Если GPT Images 2.0 недоступен, вернул ошибку или не создал файл, повторить тот же prompt через **GPT Images / default Codex image generation**. Только после провала обоих Codex-путей переходить к legacy fallback.
4. Не спрашивать ключи Google, Pollinations или remove.bg в Codex-пути.
5. Внешние провайдеры ниже считаются legacy fallback и используются только по явной просьбе пользователя или если Codex image generation недоступна.

## Сервисы генерации

| Сервис | Когда использовать | Требования |
|--------|--------------------|------------|
| **Codex GPT Images 2.0** | Основной PNG/image-generation путь в Codex | Встроенный Codex image generation tool |
| **Codex GPT Images / default image generation** | Первый fallback, если GPT Images 2.0 не сработал | Встроенный Codex image generation tool |
| **SVG** | Режим по умолчанию, если PNG не нужен | Ничего |
| **Pollinations.ai / Google Gemini** | Только legacy fallback или явный запрос пользователя | Внешний API ключ / billing |

**Удаление фона:** только `python3 tools/cutout.py`. Ручной `magick -fuzz`, голый `rembg i`
и `remove.bg` запрещены (см. «Локальное удаление фона» ниже).

---

## Бюджетный манифест и кэш (ОБЯЗАТЕЛЬНО)

Экономия достигается не упрощением промпта, а исключением повторных и не нужных вызовов.
GPT Images 2.0 остаётся единственным штатным генератором растрового исходника в Codex.

Перед первой генерацией создать `design/asset-manifest.md`; `design/asset-prompts.md`
остаётся подробным художественным ledger. Манифест — это машиночитаемая для агента запись
решения о расходе каждого вызова:

```markdown
# Asset Manifest — Budgeted GPT Images 2.0

budget: unique_sources=12, technical_recovery_calls=2

| logical_id | class | target_path | prompt_sha256 | source_id | attempts | validation | status |
|------------|-------|-------------|---------------|-----------|----------|------------|--------|
```

Классы манифеста:

| Класс | Когда применять | Расход GPT Images 2.0 |
|-------|-----------------|-----------------------|
| `generate` | Уникальный силуэт игрового символа, hero-объект или полноэкранная сцена | 1 успешный источник |
| `derive` | Кадрирование, масштаб, безопасный цветовой вариант или локальная анимационная фаза существующего ассета | 0 |
| `code` | UI, текст, кнопки, панели, иконки, рамки, тени, glow, частицы и VFX | 0 |
| `reuse` | Уже валидированный источник без изменения его игрового смысла | 0 |

Для каждого `generate` до вызова построить нормализованный prompt (включая тип, Design DNA,
ключевой цвет и путь) и записать его SHA-256. Если в манифесте уже есть тот же
`prompt_sha256`, файл существует, валиден и прошёл `cutout.py --check` для простого ассета,
переиспользовать его без нового вызова. Например:

```bash
printf '%s' "$NORMALIZED_PROMPT" | shasum -a 256
```

Стандартный бюджет для `/autocreate` и `--from-concept`: не более **12 уникальных успешных
исходников** и не более **2 технических recovery-вызовов** на игру. Внутри этих 12 по
умолчанию допускаются 5–8 уникальных игровых символов и не более двух полноэкранных сцен.
Выход за лимит не делается молча: для ручной команды нужен явный запрос пользователя, а
автоконвейер обязан сначала переклассифицировать элемент в `derive`, `code` или `reuse`.

Цветовые варианты разрешены только если не меняют распознаваемый результат раунда,
редкость, выплату или вероятность. В противном случае это отдельный `generate`-ассет.

### Fallback без лишнего расхода

GPT Images / default Codex image generation допускается **только** после документированного
технического сбоя GPT Images 2.0: недоступный инструмент, ошибка вызова, отсутствие файла
или невалидный PNG. Записать причину в `attempts`/`status` манифеста и повторить **тот же**
prompt. Визуальный вкус, AR1–AR10, неподходящая композиция или неудачный chroma-key не
являются основанием для fallback: сначала применить локальную обработку, затем при
необходимости использовать один из двух recovery-вызовов снова через GPT Images 2.0.

---

## Ключевой цвет фона (chroma key) — выбирать ДО генерации

Белый фон нельзя вырезать у белого объекта: курица, перо, лёд, стекло, хром, пена, снег
сливаются с фоном, и от них остаются дыры. Поэтому простые ассеты генерируются на
**плоском ключевом цвете, максимально далёком от палитры объекта**.

Правило выбора (выполнять для КАЖДОГО ассета, писать выбор в `design/asset-prompts.md`):

| Палитра объекта (Design DNA) | Ключ | В промпте |
|------------------------------|------|-----------|
| нет пурпурного/розового/фиолетового | **magenta** (по умолчанию) | `flat solid pure magenta #FF00FF background` |
| есть пурпур/розовый/фиолетовый, нет зелёного | **green** | `flat solid pure green #00FF00 background` |
| есть и пурпур, и зелёный | **blue** | `flat solid pure blue #0000FF background` |
| объект яркий, насыщенный, без белого и светлых бликов | white (допустим) | `flat solid pure white background` |

Всегда добавлять в промпт: `flat solid single-colour background, no gradient, no vignette,
no shadow on the background, subject fully inside frame`.

Ключ определяется автоматически при вырезании — но выбрать его правильно всё равно
обязательно: измеренная ошибка вырезания при плохом ключе (фон того же тона, что объект)
в разы выше, чем при правильном.

---

## Шаг 0: Определение режима

### Если агент работает в Codex

- Всегда выбрать Codex image-generation chain: **GPT Images 2.0 → GPT Images/default Codex image generation**.
- Сначала создать/прочитать `design/asset-manifest.md`, проверить SHA-256 prompt и лимиты;
  создавать PNG только для класса `generate` без валидного кэшированного совпадения.
- Создавать один PNG за один вызов image generation.
- Сохранять результат в `assets/images/pngs/`, `assets/images/sprites/`, `assets/images/ui/` или `assets/images/backgrounds/` по типу ассета.
- Для `symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item` просить **плоский ключевой фон** (см. «Ключевой цвет фона» выше) без теней, градиентов и сцены; прозрачность появляется только после `tools/cutout.py`.
- Для `background`, `main_menu_bg`, `game_bg`, полноэкранных иллюстраций фон НЕ вырезать.
- Для `/autocreate` создать/обновить `design/asset-prompts.md`: полный prompt, subject,
  material, lighting, render style, путь файла и post-processing verdict для каждого ассета.

### Если переданы legacy-флаги:
- `--cheap POLL_API_TOKEN` → Pollinations.ai с ключом (legacy fallback)
- `--cheap POLL_API_TOKEN --free REMOVE_BG_TOKEN` → Pollinations + remove.bg только если пользователь явно просит этот сервис
- Без флагов в Codex → не спрашивать, использовать GPT Images 2.0; если он не сработал, GPT Images/default Codex image generation

### Если флагов нет и агент НЕ работает в Codex — спросить:

> "Как генерировать PNG ассеты?
>
> **1. SVG** — режим по умолчанию, через /generate-asset
> **2. Внешний PNG provider** — Pollinations.ai или Google Gemini, нужен API ключ / billing
> **3. Ручной промпт** — агент подготовит prompt, пользователь генерирует вне студии
>
> Введите 1, 2 или 3:"

---

## Codex-режим: GPT Images 2.0 → GPT Images fallback

**Использовать GPT Images 2.0 первым в Codex.** Не нужен API ключ. Если вызов не сработал
или не дал валидный PNG, повторить с тем же prompt через **GPT Images / default Codex image
generation**. Внешние провайдеры разрешены только после провала обоих Codex-путей или по явной
просьбе пользователя.

### Realism & concept fidelity (читать ПЕРЕД построением промпта)

> Цель — НЕ «нарисуй абстрактный значок». Цель — **реалистичный, концептуально-достоверный
> ассет, который выглядит как настоящий объект из мира ЭТОЙ игры**. Дешёвый промпт даёт
> дешёвый ассет. Перед генерацией каждого ассета выведи из концепта (`design/gdd/game-concept.md`)
> и Design DNA четыре вещи и подставь их в промпт:

1. **Subject identity** — что это конкретно за объект в мире игры (не «гем», а «гранёный
   аметист с внутренним свечением»; не «кнопка», а «латунная клавиша с гравировкой»).
2. **Material & texture** — из чего сделан: металл/стекло/дерево/драгоценный камень/неон/ткань;
   реальные блики, шероховатость, отражения, подповерхностное свечение.
3. **Lighting** — единый для ВСЕГО набора источник (например, мягкий верхне-левый key light
   + лёгкий rim). Свет = главный признак «дорогого» ассета.
4. **Render style из DNA** — по умолчанию для `/autocreate`: realistic/material-grounded
   3D product render или glossy 2.5D с реальными материалами. Рисованный / pixel / paper-cut
   выбирать только если Design DNA явно требует именно это. Выбери ОДИН стиль и держи его
   одинаковым во всём наборе (консистентность набора важнее красоты одного ассета).

**Жёсткий quality floor для `/autocreate`:** результат, похожий на flat vector icon,
emoji/sticker, generic logo, дешёвый clipart, случайный neon/casino asset без связи с концептом,
sprite sheet, текст внутри изображения или объект с другой схемой света, считается FAIL.
Сначала устранить локально исправимые дефекты (cutout, нормализация кадра, переклассификация
в `code`/`derive`); для дефекта исходной генерации разрешён один recovery-вызов GPT Images 2.0
на `logical_id`. Нельзя автоматически переключаться на fallback из-за эстетической оценки.

### Промпт для простого ассета (concept-grounded, realistic)

```
Highly detailed realistic mobile game asset of [SUBJECT IDENTITY from concept],
single hero object centered, [MATERIAL/TEXTURE] with believable
[reflections/roughness/subsurface glow/small surface imperfections],
[RENDER STYLE from DNA or default realistic 3D product render], shared soft
[LIGHTING: key from top-left + subtle rim], rich [DNA PALETTE] colors,
crisp clean silhouette readable at 64 px, sharp focus, premium studio product shot,
flat solid single-colour [KEY COLOUR] background, no gradient, no vignette, subject fully
inside frame, transparent-ready cutout, NO scene, NO ground shadow, NO shadow on the
background, NO text, NO border, NO logo, NO sprite sheet, 1024x1024 PNG.
[TYPE_DETAILS]
```

> `[KEY COLOUR]` подставляется по таблице из «Ключевой цвет фона» (по умолчанию
> `pure magenta #FF00FF`). Сразу после генерации — `python3 tools/cutout.py <файл>
> --type sprite`. Никогда не проси сложную сцену, тень под объектом или градиентный
> фон у простого ассета — это ломает вырезание, и cutout.py такой ассет отклонит.

### Промпт для background (без вырезания фона)

```
Cinematic 9:16 mobile game background: [SCENE from concept & DNA].
Full atmospheric scene with depth (foreground / midground / sky layers),
[DNA mood & palette], volumetric light, no foreground characters, no UI, no text,
calm readable empty area in the vertical center for gameplay, high quality PNG.
```

### После генерации

1. Сохранить PNG в целевую папку.
2. Проверить файл через `file path/to/asset.png`.
3. Если это простой ассет — применить локальное удаление белого фона.
4. Добавить папку в `pubspec.yaml`, если она новая.

### Локальное удаление фона — ТОЛЬКО через `tools/cutout.py`

Только для `symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`.
Не применять к `background`, `ui_panel`, полноэкранным сценам и иллюстрациям
(эти типы навык сам пропустит).

> **Запрещено вырезать фон вручную** — ни `magick -fuzz ... -transparent white`,
> ни голый `rembg i`. Глобальный fuzz-матч пробивает дыры в белых бликах, глазах,
> хроме и пене, даёт бинарную (рваную) альфу и оставляет белый ореол по краю.
> `tools/cutout.py` делает то, что делает компоузер: заливка фона от границы кадра
> (внутренние белые пиксели не трогаются), дробная альфа на краю, декантаминация
> (снятие цвета фона с полупрозрачных пикселей), despill, обрезка по контенту и
> нормализация кадра. `rembg`, если установлен, используется как ассист.

```bash
python3 tools/cutout.py assets/images/pngs/cherry.png --type sprite
```

Вывод: `✅ cherry.png 512×512 flood+matte` — фон снят и проверен.
`✗` означает, что ассет непригоден (фон не плоский / ключевой цвет не тот) —
сначала проверить исходник и ключ, затем использовать только разрешённый recovery GPT Images
2.0; не «дожимать» вручную и не переключаться на fallback по качеству.

| Флаг | Зачем |
|------|-------|
| `--type sprite\|icon\|ui\|tile\|background` | пресет холста и полей; `background`/`ui_panel` пропускаются |
| `--key auto\|magenta\|green\|blue\|white\|#RRGGBB` | ключевой цвет; `auto` определяет его по рамке кадра |
| `--dir assets/images/sprites` | пакетно по папке |
| `--check` | только аудит альфы, без записи (используется в `/asset-review`) |
| `--no-trim` | не перекадрировать (когда важна исходная композиция) |
| `--backup` | сохранить оригинал как `*.orig.png` |

Один вызов на ассет сразу после генерации; для всего набора — `--dir` в конце.

---

## Legacy fallback: Pollinations.ai

### Модели изображений (Pollinations)

| Модель | Качество | Цена | Особенности |
|--------|---------|------|-------------|
| `flux` | Хорошее | Дёшево | Быстрая |
| `zimage` | Хорошее + 2x upscale | Дёшево | Fast 6B Flux с апскейлом |
| `gptimage` | Высокое | Платно (pollen) | OpenAI image gen, поддержка прозрачности |
| `gptimage-large` | Очень высокое | Платно | HD, прозрачность |
| `klein` | Среднее | Дёшево | FLUX.2 Klein 4B, быстрая |

### Удаление фона в legacy fallback

Тот же `python3 tools/cutout.py` — он не зависит от провайдера генерации.
`remove.bg` и ручной ImageMagick не используются даже в legacy-пути.

---

### Шаблон одного символа (один Bash call):

Ассеты типа `symbol`, `icon`, `wild`, `scatter` → **фон удаляется автоматически**.
Ассеты типа `background`, `ui_panel` → фон НЕ удаляется.

```bash
POLL_API_KEY="[ключ от --cheap или от пользователя]"
ASSET_NAME="cherry"
ASSET_TYPE="symbol"   # symbol | icon | wild | scatter | background | ui_panel
PROMPT="red glossy cherries fruit, game sprite icon, flat solid pure magenta #FF00FF background, no gradient, vibrant colors, cartoon style, isolated object"
OUTPUT_DIR="assets/images/pngs"
MODEL="flux"          # legacy: flux | zimage | gptimage | klein
mkdir -p "${OUTPUT_DIR}"

echo "━━━ [${ASSET_TYPE}] Генерирую: ${ASSET_NAME} (модель: ${MODEL}) ━━━"

# 1. Генерация через Pollinations.ai (новый API)
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${PROMPT}'))")
curl -s -L "https://gen.pollinations.ai/image/${ENCODED}?width=1024&height=1024&nologo=true&model=${MODEL}&seed=-1" \
  -H "Authorization: Bearer ${POLL_API_KEY}" \
  -o "${OUTPUT_DIR}/${ASSET_NAME}.png"

if [ ! -s "${OUTPUT_DIR}/${ASSET_NAME}.png" ]; then
  echo "✗ Pollinations не вернул изображение"
  exit 1
fi

SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Сгенерирован: ${SIZE}"

# 2. Удаление фона (только для symbol/icon/wild/scatter)
if [[ "${ASSET_TYPE}" == "symbol" || "${ASSET_TYPE}" == "icon" || "${ASSET_TYPE}" == "wild" || "${ASSET_TYPE}" == "scatter" ]]; then
  python3 tools/cutout.py "${OUTPUT_DIR}/${ASSET_NAME}.png" --type sprite
else
  echo "⏭ Тип '${ASSET_TYPE}' — удаление фона пропущено"
fi

FINAL_SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Готово: ${OUTPUT_DIR}/${ASSET_NAME}.png (${FINAL_SIZE})"
```

### Альтернатива: OpenAI-совместимый endpoint (POST)

Для более сложных сценариев (прозрачность, editing):

```bash
POLL_API_KEY="[ключ]"
ASSET_NAME="cherry"
PROMPT="red glossy cherries fruit, game sprite icon, flat solid pure magenta #FF00FF background, no gradient"
OUTPUT_DIR="assets/images/pngs"
mkdir -p "${OUTPUT_DIR}"

# POST /v1/images/generations (OpenAI-compatible)
RESPONSE=$(curl -s -X POST "https://gen.pollinations.ai/v1/images/generations" \
  -H "Authorization: Bearer ${POLL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"${PROMPT}\",\"model\":\"flux\",\"size\":\"1024x1024\",\"response_format\":\"url\"}")

# Извлечь URL и скачать
IMG_URL=$(echo "${RESPONSE}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['url'])")
curl -s -L "${IMG_URL}" -o "${OUTPUT_DIR}/${ASSET_NAME}.png"
echo "✓ ${OUTPUT_DIR}/${ASSET_NAME}.png"
```

---

### Промпты — выводятся из Design DNA (пример ниже — для ОДНОГО конкретного слота)

> ⚠️ Таблица ниже — иллюстрация для классического фруктового слота. **Для ЭТОЙ игры
> символы, палитра и стиль берутся из Design DNA концепта** (`design/gdd/game-concept.md`),
> а НЕ казино/неон по умолчанию. Для `/autocreate` базовый стиль — realistic/material-grounded
> 3D/product render; flat/lineart/pixel разрешены только если это прямо написано в DNA.
> Подставь в промпты тему/мир, палитру, материалы, единый свет и яркость из DNA.
> Египетский слот → скарабеи/анкхи с фактурой золота и лазурита; космос → кристаллы/
> сплавы/звёздная керамика в холодных; и т.д. Держи единый стиль во всём наборе.

| Символ (пример-слот) | ASSET_TYPE | Промпт (стиль/палитра — подставить из DNA) |
|--------|-----------|--------|
| cherry | symbol | `red glossy cherries fruit, game sprite, flat solid [KEY] background, vibrant cartoon` |
| bar | symbol | `chrome metallic BAR text, slot machine symbol, flat solid [KEY] background, shiny 3D` |
| seven | symbol | `lucky number seven, red with gold outline, bold game icon, flat solid [KEY] background` |
| diamond | symbol | `blue diamond gemstone, crystal faceted, game icon, flat solid green #00FF00 background, glossy` |
| wild | wild | `golden star wild, glowing rainbow aura, game icon, flat solid green #00FF00 background` |
| scatter | scatter | `purple hexagon lightning bolt, scatter symbol, game icon, flat solid green #00FF00 background` |
| main_menu_bg | background | `[DNA theme] background, [DNA palette], atmospheric, no characters` — яркость и мир из DNA, не «всегда тёмное казино» |

### Особенности:
- В Codex для простых ассетов просить плоский ключевой фон сразу, затем `tools/cutout.py`
- Прозрачный фон напрямую не является дефолтом: плоский ключ даёт предсказуемо чистую альфу,
  а «transparent background» модели выполняют через раз и часто отдают белый JPEG-подобный фон
- Модели legacy fallback: `flux`, `zimage`, `gptimage`
- Каждый Bash call = один ассет (не объединять в цикл)
- `seed=-1` для случайного результата каждый раз

---

## Legacy fallback: Google Gemini — требует биллинг

### Шаг 1: Проверка ключа (быстрая диагностика)

Запусти перед генерацией — убеждаемся что ключ рабочий:

```bash
API_KEY="[ключ от пользователя]"

PROBE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${API_KEY}" -H "Content-Type: application/json" -d '{"contents":[{"parts":[{"text":"red dot"}]}],"generationConfig":{"responseModalities":["IMAGE"]}}')

echo "HTTP статус: ${PROBE}"

if [ "$PROBE" = "200" ]; then
  echo "✓ Ключ работает, gemini-2.5-flash-image доступна"
elif [ "$PROBE" = "403" ]; then
  echo "✗ 403 — неверный API ключ или Gemini API не включён в AI Studio"
elif [ "$PROBE" = "404" ]; then
  echo "✗ 404 — попробуй альтернативное имя модели (см. Диагностику)"
else
  echo "✗ HTTP ${PROBE} — проверь ключ и подключение"
fi
```

---

## Шаг 2: Контекст игры

Прочитать если есть:
- `design/gdd/game-concept.md` → тема, цвета, стиль
- `design/balance/rtp-config.json` → список символов (gambling)

---

## Шаг 3: Построение промпта

> Стиль, палитра и яркость подставляются из **Design DNA** концепта — НЕ casino/neon по
> умолчанию. Для `/autocreate` `[АРТ-СТИЛЬ]` по умолчанию = realistic/material-grounded
> 3D product render или glossy 2.5D with believable materials; flat/pixel/lineart только по
> явному DNA. Сначала выведи **Subject / Material / Lighting** (см. «Realism & concept
> fidelity» выше) — без них получится дешёвый плоский значок.

```
Highly detailed mobile game asset of [SUBJECT IDENTITY из концепта],
single hero object centered, realistic [MATERIAL/TEXTURE: металл/стекло/камень/дерево/неон],
believable [reflections / roughness / subsurface glow], [АРТ-СТИЛЬ из DNA] render,
soft [LIGHTING: key верх-слева + лёгкий rim], rich [ПАЛИТРА из DNA] colors,
crisp clean silhouette, sharp focus, isolated on flat solid single-colour [KEY COLOUR]
background, no gradient, no scene, no ground shadow, no text, transparent-ready, 1024x1024.
[ТИП-ДЕТАЛИ]
```

### Детали по типу (эффекты — только если они в DNA):
| Тип | Добавить (подставить под DNA) |
|-----|---------|
| `symbol` / `sprite` | стиль из DNA (объём с бликами ИЛИ flat ИЛИ lineart), единый для набора |
| `wild` (gambling) | премиальный акцентный символ; эффект (свечение/блеск/нет) — из DNA |
| `scatter` (gambling) | особый символ-триггер, визуально выделен средствами DNA |
| `ui` кнопка | форма из shape language DNA; эффект (glow/тень/плоско) из DNA, no text |
| `background` | мир и **яркость** из DNA (не «всегда тёмное казино»), не отвлекает от игрового поля |

> **Важно для прозрачного фона:** legacy Imagen/Gemini не всегда генерирует RGBA.
> Если alpha не получилась, вырежи фон через `tools/cutout.py` на Шаге 5.

---

## Шаг 4: Генерация через gemini-2.5-flash-image

**Формат API:** `generateContent` с `responseModalities: ["IMAGE"]`
**Ответ:** `candidates[0].content.parts[n].inlineData.data`
**Разрешение:** 1024×1024

```bash
API_KEY="[ключ]"
ASSET_NAME="[название]"
PROMPT="[промпт из Шага 3]"
OUTPUT_DIR="assets/images/pngs"
mkdir -p "${OUTPUT_DIR}"

# ВАЖНО: URL и -d на ОДНОЙ строке каждый, без переносов внутри
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${API_KEY}" -H "Content-Type: application/json" -d "{\"contents\":[{\"parts\":[{\"text\":\"${PROMPT}\"}]}],\"generationConfig\":{\"responseModalities\":[\"IMAGE\"]}}" -o "/tmp/gemini_resp_${ASSET_NAME}.json"

# Проверка + декодирование (python3 stdlib, без pip)
python3 - <<PYEOF
import json, base64

name = "${ASSET_NAME}"
out_dir = "${OUTPUT_DIR}"

with open(f"/tmp/gemini_resp_{name}.json") as f:
    data = json.load(f)

# Ошибка API
if "error" in data:
    print(f"✗ Ошибка API: {data['error'].get('message', data['error'])}")
    exit(1)

# Найти inlineData
for candidate in data.get("candidates", []):
    for part in candidate.get("content", {}).get("parts", []):
        if "inlineData" in part:
            img_bytes = base64.b64decode(part["inlineData"]["data"])
            out_path = f"{out_dir}/{name}.png"
            with open(out_path, "wb") as out:
                out.write(img_bytes)
            print(f"✓ {out_path} ({len(img_bytes) // 1024} KB)")
            exit(0)

print(f"✗ Нет inlineData в ответе. Ключи: {list(data.keys())}")
PYEOF
```

---

## Шаг 5: Удаление фона для простых ассетов

Не спрашивать отдельный сервис. Применять только к простым ассетам (`symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`). Для `background` / полноэкранной иллюстрации пропустить.

```bash
python3 tools/cutout.py "${OUTPUT_DIR}/${ASSET_NAME}.png" --type sprite
```

Ненулевой код возврата = проверить исходник и ключ, затем перевырезать/нормализовать локально.
Если исходник действительно непригоден, использовать один разрешённый recovery-вызов GPT
Images 2.0 с плоским ключевым фоном; не переключаться на fallback из-за ошибки cutout.

---

## Генерация: СТРОГО ОДИН АССЕТ ЗА РАЗ

### КРИТИЧЕСКОЕ ПРАВИЛО ДЛЯ АГЕНТА

**ЗАПРЕЩЕНО:**
- Запускать несколько Bash calls подряд без ожидания
- Делать следующий API запрос до того как предыдущий bash полностью завершился
- Использовать фоновые процессы (`&`) или параллельные вызовы

**ОБЯЗАТЕЛЬНО:**
- Один Bash tool call = один ассет
- Для Gemini: `sleep 65` после каждого (rate limit 10 RPM)
- Для Pollinations: `sleep 3` после каждого (быстрее)
- Для Codex GPT Images 2.0 / GPT Images fallback: один вызов image generation = один ассет
- Следующий Bash tool call только ПОСЛЕ того как предыдущий вернул результат

---

### Legacy шаблон одного ассета — Gemini (копировать и менять ASSET_NAME + PROMPT):

```bash
API_KEY="[ключ]"
ASSET_NAME="cherry"
PROMPT="Red glossy cherries fruit, game sprite icon, white background, vibrant colors, cartoon style, 1024x1024"
OUTPUT_DIR="assets/images/pngs"
mkdir -p "${OUTPUT_DIR}"

echo "━━━ Генерирую: ${ASSET_NAME} ━━━"

curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${API_KEY}" -H "Content-Type: application/json" -d "{\"contents\":[{\"parts\":[{\"text\":\"${PROMPT}\"}]}],\"generationConfig\":{\"responseModalities\":[\"IMAGE\"]}}" -o "/tmp/g_${ASSET_NAME}.json"

python3 - <<PYEOF
import json, base64, sys
name = "${ASSET_NAME}"
out_dir = "${OUTPUT_DIR}"
with open(f"/tmp/g_{name}.json") as f:
    data = json.load(f)
if "error" in data:
    print(f"✗ {data['error'].get('message', str(data['error']))}")
    sys.exit(1)
for c in data.get("candidates", []):
    for p in c.get("content", {}).get("parts", []):
        if "inlineData" in p:
            img = base64.b64decode(p["inlineData"]["data"])
            path = f"{out_dir}/{name}.png"
            open(path, "wb").write(img)
            print(f"✓ {path} ({len(img)//1024} KB)")
            sys.exit(0)
print(f"✗ Нет inlineData. Ключи: {list(data.keys())}")
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
  echo "⏳ Ждём 65 сек (rate limit)..."
  sleep 65
  echo "Готово. Можно генерировать следующий."
else
  echo "✗ Ошибка. Полный ответ:"
  cat "/tmp/g_${ASSET_NAME}.json"
  echo "НЕ ПРОДОЛЖАТЬ — сообщить пользователю об ошибке."
fi
```

---

### Последовательность для 6 символов (агент делает 6 отдельных Bash calls):

**Call 1:** cherry → ждёт завершения → сообщает "✓ cherry готов (1/6)"
**Call 2:** bar → ждёт завершения → "✓ bar готов (2/6)"
**Call 3:** seven → ждёт завершения → "✓ seven готов (3/6)"
**Call 4:** diamond → ждёт завершения → "✓ diamond готов (4/6)"
**Call 5:** wild → ждёт завершения → "✓ wild готов (5/6)"
**Call 6:** scatter → "✓ scatter готов (6/6)"

При ошибке — остановиться, показать ответ, спросить пользователя.

---

## --from-concept: из rtp-config.json автоматически

1. Читаем `design/balance/rtp-config.json` → список `symbols[].name`
2. Читаем `design/gdd/game-concept.md` → тема и цвета
3. Строим `ASSETS=()` динамически и запускаем batch-цикл выше

---

## После генерации

Добавить в `pubspec.yaml` если папка новая:
```yaml
flutter:
  assets:
    - assets/images/pngs/
```

---

## Диагностика ошибок

### Pollinations.ai

| Симптом | Причина | Решение |
|---------|---------|---------|
| HTTP 401 | Отсутствует или неверный API ключ | Проверить ключ на https://enter.pollinations.ai |
| HTTP 402 | Недостаточно pollen баланса | Пополнить баланс или переключиться на бесплатную модель (flux, zimage) |
| HTTP 403 | Нет прав (permission denied) | Проверить тип ключа (pk_ vs sk_) и разрешения |
| Пустой файл | Сервер не вернул изображение | Попробовать другую модель или упростить промпт |
| Долгий ответ | Модель gptimage медленнее | Переключиться на flux или zimage для скорости |

### Google Gemini

| Симптом | Причина | Решение |
|---------|---------|---------|
| HTTP 403 | Неверный ключ или Gemini API не активирован | AI Studio → API Keys → убедиться что Gemini API включён |
| HTTP 404 `model not found` | Неверное имя модели | Попробовать `gemini-2.5-flash-preview-image-generation` |
| HTTP 400 `responseModalities` | Модель не поддерживает IMAGE | Добавить `"TEXT"` к списку: `["IMAGE","TEXT"]` |
| HTTP 429 | Превышен лимит 10 RPM | Увеличить sleep до 65+ сек |
| `inlineData` не найден | Gemini вернул только текст | Изменить промпт: начать с "Create an image of..." |
| PNG файл пустой | Ошибка base64 | Показать пользователю полный JSON из `/tmp/g_*.json` |

**Правило:** При ЛЮБОЙ ошибке — показывать пользователю полный ответ API. Никогда не скрывать.
