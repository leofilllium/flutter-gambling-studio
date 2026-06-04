---
name: generate-png-asset
description: "Генерация PNG-ассетов. В Codex основной путь — встроенная image generation через GPT Images 2.0; внешние API только как legacy fallback. Фон простых ассетов удаляется локальной библиотекой при необходимости."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[описание] | [--batch список] | [--from-concept] | [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `generate-png-asset` — PNG ассеты для мини-игр

## Правило по умолчанию

1. Если пользователь не просил PNG/image generation — вернуться к `/generate-asset` и создать **SVG**.
2. Если пользователь явно просил PNG/image generation и агент работает в **Codex** — использовать **GPT Images 2.0**, доступный как встроенная image generation возможность Codex.
3. Не спрашивать ключи Google, Pollinations или remove.bg в Codex-пути.
4. Внешние провайдеры ниже считаются legacy fallback и используются только по явной просьбе пользователя или если Codex image generation недоступна.

## Сервисы генерации

| Сервис | Когда использовать | Требования |
|--------|--------------------|------------|
| **Codex GPT Images 2.0** | Основной PNG/image-generation путь в Codex | Встроенный Codex image generation tool |
| **SVG** | Режим по умолчанию, если PNG не нужен | Ничего |
| **Pollinations.ai / Google Gemini** | Только legacy fallback или явный запрос пользователя | Внешний API ключ / billing |

**Удаление фона:** для простых ассетов использовать локальную библиотеку/CLI (`rembg`) при необходимости. `remove.bg` не является дефолтом; использовать только если пользователь явно дал ключ и попросил этот сервис.

---

## Шаг 0: Определение режима

### Если агент работает в Codex

- Всегда выбрать **Codex GPT Images 2.0**.
- Создавать один PNG за один вызов image generation.
- Сохранять результат в `assets/images/pngs/`, `assets/images/sprites/`, `assets/images/ui/` или `assets/images/backgrounds/` по типу ассета.
- Для `symbol`, `sprite`, `icon`, `wild`, `scatter` просить transparent background / alpha channel.
- Для `background`, `main_menu_bg`, `game_bg`, полноэкранных иллюстраций фон НЕ вырезать.

### Если переданы legacy-флаги:
- `--cheap POLL_API_TOKEN` → Pollinations.ai с ключом (legacy fallback)
- `--cheap POLL_API_TOKEN --free REMOVE_BG_TOKEN` → Pollinations + remove.bg только если пользователь явно просит этот сервис
- Без флагов в Codex → не спрашивать, использовать GPT Images 2.0

### Если флагов нет и агент НЕ работает в Codex — спросить:

> "Как генерировать PNG ассеты?
>
> **1. SVG** — режим по умолчанию, через /generate-asset
> **2. Внешний PNG provider** — Pollinations.ai или Google Gemini, нужен API ключ / billing
> **3. Ручной промпт** — агент подготовит prompt, пользователь генерирует вне студии
>
> Введите 1, 2 или 3:"

---

## Codex-режим: GPT Images 2.0

**Использовать первым в Codex.** Не нужен API ключ.

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
4. **Render style из DNA** — фотореалистичный 3D-render / glossy 2.5D / рисованный / pixel /
   paper-cut. Выбери ОДИН и держи его одинаковым во всём наборе (консистентность набора важнее
   красоты одного ассета).

### Промпт для простого ассета (concept-grounded, realistic)

```
Highly detailed game asset of [SUBJECT IDENTITY from concept], single hero object centered,
realistic [MATERIAL/TEXTURE] with believable [reflections/roughness/subsurface glow],
[RENDER STYLE from DNA] render, dramatic but soft [LIGHTING: key from top-left + subtle rim],
rich [DNA PALETTE] colors, crisp clean silhouette, sharp focus, studio product shot,
isolated on a plain solid pure-white background, NO scene, NO shadow on ground,
NO text, NO border, transparent-ready, 1024x1024 PNG.
[TYPE_DETAILS]
```

> Если Codex поддерживает прозрачность напрямую — проси `transparent background, alpha channel`
> вместо white. Если нет — проси **plain solid pure-white background** (легко вырезать локально
> на Шаге «Удаление фона»). Никогда не проси сложную сцену/тени под объектом у простого ассета —
> это ломает вырезание фона.

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
3. Если это простой ассет и фон не прозрачный — применить локальное удаление фона.
4. Добавить папку в `pubspec.yaml`, если она новая.

### Локальное удаление фона (с проверкой результата)

Только для `symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`.
Не применять к `background`, `ui_panel`, полноэкранным сценам и иллюстрациям.

> **Порядок предпочтения строгий:** `rembg` (нейросетевое вырезание — даёт чистую альфу даже
> на сложных краях) → ImageMagick fuzz **только как последний резерв** (грубый, рвёт мягкие
> края и полупрозрачность). После вырезания **обязательно проверить, что альфа реально
> появилась**; если нет — перегенерировать ассет с чистым белым фоном и повторить.

```bash
INPUT_PNG="assets/images/pngs/cherry.png"
TMP_PNG="${INPUT_PNG%.png}_nobg.png"

removed=0
if command -v rembg >/dev/null 2>&1; then
  rembg i "${INPUT_PNG}" "${TMP_PNG}" && mv "${TMP_PNG}" "${INPUT_PNG}" && removed=1
elif python3 -c "import rembg" >/dev/null 2>&1; then
  python3 -c "from rembg import remove; from pathlib import Path; p=Path('${INPUT_PNG}'); p.write_bytes(remove(p.read_bytes()))" && removed=1
elif command -v magick >/dev/null 2>&1; then
  echo "⚠ rembg не найден — грубый ImageMagick fallback (мягкие края могут пострадать)"
  magick "${INPUT_PNG}" -fuzz 12% -transparent white "${INPUT_PNG}" && removed=1
elif command -v convert >/dev/null 2>&1; then
  echo "⚠ rembg не найден — грубый ImageMagick fallback (мягкие края могут пострадать)"
  convert "${INPUT_PNG}" -fuzz 12% -transparent white "${INPUT_PNG}" && removed=1
else
  echo "Фон не удалён: установи rembg (pip install rembg) или ImageMagick, либо перегенерируй с transparent background"
fi

# Проверка: действительно ли в PNG появились прозрачные пиксели
if [ "${removed}" = "1" ]; then
  python3 - "${INPUT_PNG}" <<'PYEOF'
import sys
try:
    from PIL import Image
    im = Image.open(sys.argv[1]).convert("RGBA")
    amin, amax = im.getchannel("A").getextrema()
    if amin == 255:
        print("⚠ Альфа НЕ появилась (фон не вырезан). Перегенерируй ассет с чистым белым фоном и повтори rembg.")
    else:
        print(f"✓ Прозрачность подтверждена (alpha min={amin})")
except Exception as e:
    print(f"ℹ Проверку альфы пропустил ({e}); установи Pillow (pip install pillow) для авто-проверки")
PYEOF
fi
```

> **Установка rembg, если отсутствует** (лучшее качество вырезания):
> `pip install rembg` или `pip install "rembg[cpu]"`. После установки — повторить вырезание,
> не оставляя грубый ImageMagick-результат для финальных ассетов.

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

Предпочитать локальный `rembg` / ImageMagick. `remove.bg` использовать только если пользователь явно передал `--free REMOVE_BG_TOKEN`.

Не спрашивать ключ remove.bg. Сохрани `REMBG_KEY` только если пользователь уже передал `--free REMOVE_BG_TOKEN`; иначе `REMBG_KEY=""` и используй локальный fallback.

---

### Шаблон одного символа (один Bash call):

Ассеты типа `symbol`, `icon`, `wild`, `scatter` → **фон удаляется автоматически**.
Ассеты типа `background`, `ui_panel` → фон НЕ удаляется.

```bash
POLL_API_KEY="[ключ от --cheap или от пользователя]"
ASSET_NAME="cherry"
ASSET_TYPE="symbol"   # symbol | icon | wild | scatter | background | ui_panel
PROMPT="red glossy cherries fruit, game sprite icon, pure white background, vibrant colors, cartoon style, isolated object"
OUTPUT_DIR="assets/images/pngs"
MODEL="flux"          # legacy: flux | zimage | gptimage | klein
REMBG_KEY=""          # только если пользователь явно передал --free
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
  echo "Удаляю фон..."

  if command -v rembg >/dev/null 2>&1; then
    rembg i "${OUTPUT_DIR}/${ASSET_NAME}.png" "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" &&
      mv "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" "${OUTPUT_DIR}/${ASSET_NAME}.png"
    echo "✓ Фон удалён (rembg)"
  elif python3 -c "import rembg" >/dev/null 2>&1; then
    python3 -c "from rembg import remove; from pathlib import Path; p=Path('${OUTPUT_DIR}/${ASSET_NAME}.png'); p.write_bytes(remove(p.read_bytes()))"
    echo "✓ Фон удалён (rembg python)"
  elif [ -n "${REMBG_KEY}" ]; then
    # remove.bg только по явному ключу пользователя
    curl -s -X POST "https://api.remove.bg/v1.0/removebg" \
      -H "X-Api-Key: ${REMBG_KEY}" \
      -F "image_file=@${OUTPUT_DIR}/${ASSET_NAME}.png" \
      -F "size=auto" \
      -o "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png"

    if [ -s "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" ]; then
      mv "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" "${OUTPUT_DIR}/${ASSET_NAME}.png"
      echo "✓ Фон удалён (remove.bg)"
    else
      echo "⚠ remove.bg не сработал — оставляю оригинал"
    fi
  else
    # ImageMagick fallback для простого белого/светлого фона
    if command -v magick &>/dev/null; then
      magick "${OUTPUT_DIR}/${ASSET_NAME}.png" \
        -fuzz 15% -transparent white \
        -fuzz 10% -transparent "#f0f0f0" \
        "${OUTPUT_DIR}/${ASSET_NAME}.png"
      echo "✓ Фон удалён (ImageMagick)"
    elif command -v convert &>/dev/null; then
      convert "${OUTPUT_DIR}/${ASSET_NAME}.png" \
        -fuzz 15% -transparent white \
        -fuzz 10% -transparent "#f0f0f0" \
        "${OUTPUT_DIR}/${ASSET_NAME}.png"
      echo "✓ Фон удалён (ImageMagick)"
    else
      echo "⚠ ImageMagick не установлен. Установить: brew install imagemagick"
      echo "  Фон не удалён — файл сохранён как есть"
    fi
  fi
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
PROMPT="red glossy cherries fruit, game sprite icon, pure white background"
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
> а НЕ казино/неон по умолчанию. Подставь в промпты: тему/мир, палитру, стиль арта (flat /
> volume / lineart / пиксель) и яркость из DNA. Лесной пазл → листья/жёлуди в тёплых тонах;
> космос → кристаллы/звёзды в холодных; и т.д. Держи единый стиль во всём наборе.

| Символ (пример-слот) | ASSET_TYPE | Промпт (стиль/палитра — подставить из DNA) |
|--------|-----------|--------|
| cherry | symbol | `red glossy cherries fruit, game sprite, pure white background, vibrant cartoon` |
| bar | symbol | `chrome metallic BAR text, slot machine symbol, pure white background, shiny 3D` |
| seven | symbol | `lucky number seven, red with gold outline, bold game icon, pure white background` |
| diamond | symbol | `blue diamond gemstone, crystal faceted, game icon, pure white background, glossy` |
| wild | wild | `golden star wild, glowing rainbow aura, game icon, pure white background` |
| scatter | scatter | `purple hexagon lightning bolt, scatter symbol, game icon, pure white background` |
| main_menu_bg | background | `[DNA theme] background, [DNA palette], atmospheric, no characters` — яркость и мир из DNA, не «всегда тёмное казино» |

### Особенности:
- В Codex просить прозрачный фон сразу через GPT Images 2.0
- Белый фон в legacy-промпте допустим только когда нужен локальный background cutout
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
> умолчанию. `[АРТ-СТИЛЬ]` = один из {flat 2D, glossy 3D with highlights, hand-drawn lineart,
> pixel art, paper cutout, watercolor, photoreal render} — выбери по DNA и держи ЕДИНЫМ для
> всего набора. Сначала выведи **Subject / Material / Lighting** (см. «Realism & concept
> fidelity» выше) — без них получится дешёвый плоский значок.

```
Highly detailed mobile game asset of [SUBJECT IDENTITY из концепта],
single hero object centered, realistic [MATERIAL/TEXTURE: металл/стекло/камень/дерево/неон],
believable [reflections / roughness / subsurface glow], [АРТ-СТИЛЬ из DNA] render,
soft [LIGHTING: key верх-слева + лёгкий rim], rich [ПАЛИТРА из DNA] colors,
crisp clean silhouette, sharp focus, isolated on plain solid pure-white background,
no scene, no ground shadow, no text, transparent-ready, 1024x1024.
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
> Если alpha не получилась, используй локальный `rembg` / ImageMagick на Шаге 5.

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
INPUT_PNG="${OUTPUT_DIR}/${ASSET_NAME}.png"
TMP_PNG="${OUTPUT_DIR}/${ASSET_NAME}_nobg.png"

if command -v rembg >/dev/null 2>&1; then
  rembg i "${INPUT_PNG}" "${TMP_PNG}" && mv "${TMP_PNG}" "${INPUT_PNG}"
  echo "✓ Фон удалён (rembg): ${INPUT_PNG}"
elif python3 -c "import rembg" >/dev/null 2>&1; then
  python3 -c "from rembg import remove; from pathlib import Path; p=Path('${INPUT_PNG}'); p.write_bytes(remove(p.read_bytes()))"
  echo "✓ Фон удалён (rembg python): ${INPUT_PNG}"
elif command -v magick >/dev/null 2>&1; then
  magick "${INPUT_PNG}" -fuzz 10% -transparent white "${INPUT_PNG}"
  echo "✓ Фон удалён (ImageMagick): ${INPUT_PNG}"
elif command -v convert >/dev/null 2>&1; then
  convert "${INPUT_PNG}" -fuzz 10% -transparent white "${INPUT_PNG}"
  echo "✓ Фон удалён (ImageMagick): ${INPUT_PNG}"
else
  echo "Фон не удалён: нет rembg/ImageMagick. Перегенерируй с transparent background."
fi
```

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
- Для Codex GPT Images 2.0: один вызов image generation = один ассет
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
