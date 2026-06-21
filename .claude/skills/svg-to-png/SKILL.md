---
name: svg-to-png
description: "Конвертация SVG-ассетов в PNG. В Codex основной путь — GPT Images 2.0, fallback — GPT Images/default Codex image generation; внешние API только legacy fallback. Простые ассеты генерируются на чистом белом фоне для локального вырезания."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[путь_к_svg] [--bulk папка] [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `svg-to-png` — Конвертер SVG → PNG

Агент анализирует SVG, формирует промпт из его содержимого и генерирует качественный PNG.

---

## Выбор режима

### Codex default

Если агент работает в Codex, всегда использовать **GPT Images 2.0** через встроенную image generation возможность Codex. Если GPT Images 2.0 не сработал или не дал валидный PNG, повторить тот же prompt через **GPT Images / default Codex image generation**.

- Не спрашивать ключи Google/Pollinations/remove.bg.
- Один SVG → один вызов image generation → один PNG.
- Для `sprite`, `symbol`, `icon`, `wild`, `scatter`, `tile`, `item` просить чистый белый фон (`plain solid pure-white background`) без теней, градиентов и сцены.
- Для `background`, `ui_panel`, полноэкранной сцены фон не вырезать.
- Если у простого ассета фон всё же появился, удалить его локальной библиотекой/CLI (`rembg`), fallback на ImageMagick.

### Legacy flags:
- `--cheap POLL_API_TOKEN` → Pollinations.ai (только если пользователь явно просит legacy fallback)
- `--free REMOVE_BG_TOKEN` → remove.bg только если пользователь явно передал ключ и попросил этот сервис
- Без флагов в Codex → не спрашивать, использовать GPT Images 2.0; если он не сработал, GPT Images/default Codex image generation

### Если флагов нет и агент НЕ работает в Codex — спросить:

> "Как конвертировать SVG → PNG?
>
> **1. Codex GPT Images 2.0 → GPT Images fallback** — если доступен в текущем агенте
> **2. Legacy external provider** — Pollinations.ai или Google, нужен API ключ / billing
> **3. Ручной режим** — сгенерирую промпт, вы генерируете PNG сами
>
> Введите 1, 2 или 3:"

---

## Вариант А: Одиночный файл

```
/svg-to-png assets/images/sprites/sprite_cherry.svg --cheap pk_xxx --free xxx
```

### Алгоритм (агент выполняет сам):

**1. Прочитать SVG + концепт** для контекста:
- Название ассета из имени файла (например `sprite_cherry` → `cherry`)
- Цвета, форму, назначение из содержимого SVG
- Если есть `design/gdd/game-concept.md` — прочитать **Design DNA** (мир, материалы,
  палитра, render style). Конвертация — не просто «обводка картинки», а **апгрейд** плоского
  SVG до реалистичного, концептуально-достоверного ассета того же объекта.

**2. Сформировать промпт** на английском (concept-grounded, realistic — НЕ дешёвый значок):

Сначала из SVG+концепта выведи: **Subject** (что это за объект в мире игры),
**Material/texture** (металл/стекло/камень/дерево/неон/ткань), **Lighting** (единый для набора,
напр. key верх-слева + rim), **Render style** из DNA.

```
Highly detailed game asset of [SUBJECT identity], single hero object centered,
realistic [MATERIAL/TEXTURE] with believable [reflections / roughness / subsurface glow],
[RENDER STYLE from DNA] render, soft [LIGHTING] light, rich [DNA PALETTE] colors,
crisp clean silhouette, sharp focus, faithful to the original shape/colors,
isolated on plain solid pure-white background, no scene, no ground shadow, no text,
transparent-ready, 1024x1024.
```

> Объект на PNG должен совпадать по форме/композиции с исходным SVG (это конвертация, не
> новая идея), но быть объёмным и материальным, а не плоской заливкой.

**3. Генерация PNG:**

### Режим 1: Codex GPT Images 2.0 → GPT Images fallback

В Codex использовать GPT Images 2.0 первым. Если он не сработал, повторить тот же prompt через
GPT Images / default Codex image generation.

1. Передать prompt из шага 2 во встроенную image generation возможность Codex.
2. Сохранить результат рядом с исходником или в `assets/images/pngs/`.
3. Если тип ассета простой и PNG содержит фон, применить локальное удаление фона с проверкой
   (rembg — приоритет; ImageMagick — последний резерв; затем проверить, что альфа появилась):

```bash
INPUT_PNG="assets/images/sprites/cherry.png"
TMP_PNG="${INPUT_PNG%.png}_nobg.png"

removed=0
if command -v rembg >/dev/null 2>&1; then
  rembg i "${INPUT_PNG}" "${TMP_PNG}" && mv "${TMP_PNG}" "${INPUT_PNG}" && removed=1
elif python3 -c "import rembg" >/dev/null 2>&1; then
  python3 -c "from rembg import remove; from pathlib import Path; p=Path('${INPUT_PNG}'); p.write_bytes(remove(p.read_bytes()))" && removed=1
elif command -v magick >/dev/null 2>&1; then
  echo "⚠ rembg не найден — грубый ImageMagick fallback"
  magick "${INPUT_PNG}" -fuzz 12% -transparent white "${INPUT_PNG}" && removed=1
elif command -v convert >/dev/null 2>&1; then
  echo "⚠ rembg не найден — грубый ImageMagick fallback"
  convert "${INPUT_PNG}" -fuzz 12% -transparent white "${INPUT_PNG}" && removed=1
else
  echo "Фон не удалён: установи rembg (pip install rembg) или ImageMagick. Перегенерируй с чистым белым фоном."
fi

# Проверка, что прозрачность действительно появилась
if [ "${removed}" = "1" ]; then
  python3 - "${INPUT_PNG}" <<'PYEOF'
import sys
try:
    from PIL import Image
    amin, _ = Image.open(sys.argv[1]).convert("RGBA").getchannel("A").getextrema()
    print("⚠ Альфа НЕ появилась — перегенерируй с белым фоном и повтори rembg." if amin == 255
          else f"✓ Прозрачность подтверждена (alpha min={amin})")
except Exception as e:
    print(f"ℹ Проверку альфы пропустил ({e}); pip install pillow для авто-проверки")
PYEOF
fi
```

### Режим 2: Legacy fallback Pollinations.ai (--cheap)

```bash
POLL_API_KEY="[ключ от --cheap]"
ASSET_NAME="cherry"
PROMPT="Professional game asset: cherry. Red glossy cherries, single isolated object, clean edges, vibrant cartoon style, 2D game sprite, pure white background, 1024x1024"
OUTPUT_DIR="assets/images/sprites"
REMBG_KEY=""  # только если пользователь явно передал --free
MODEL="flux"  # flux | zimage | gptimage

echo "━━━ SVG→PNG: ${ASSET_NAME} (Pollinations, ${MODEL}) ━━━"

# Генерация через Pollinations.ai
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

# Удаление фона для простого ассета
if command -v rembg >/dev/null 2>&1; then
  rembg i "${OUTPUT_DIR}/${ASSET_NAME}.png" "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" &&
    mv "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" "${OUTPUT_DIR}/${ASSET_NAME}.png"
  echo "✓ Фон удалён (rembg)"
elif python3 -c "import rembg" >/dev/null 2>&1; then
  python3 -c "from rembg import remove; from pathlib import Path; p=Path('${OUTPUT_DIR}/${ASSET_NAME}.png'); p.write_bytes(remove(p.read_bytes()))"
  echo "✓ Фон удалён (rembg python)"
elif [ -n "${REMBG_KEY}" ]; then
  echo "Удаляю фон (remove.bg, explicit legacy key)..."
  curl -s -X POST "https://api.remove.bg/v1.0/removebg" \
    -H "X-Api-Key: ${REMBG_KEY}" \
    -F "image_file=@${OUTPUT_DIR}/${ASSET_NAME}.png" \
    -F "size=auto" \
    -o "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png"

  if [ -s "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" ]; then
    mv "${OUTPUT_DIR}/${ASSET_NAME}_nobg.png" "${OUTPUT_DIR}/${ASSET_NAME}.png"
    echo "✓ Фон удалён"
  else
    echo "⚠ remove.bg не сработал — оставляю оригинал"
  fi
elif command -v magick >/dev/null 2>&1; then
  magick "${OUTPUT_DIR}/${ASSET_NAME}.png" \
    -fuzz 15% -transparent white \
    -fuzz 10% -transparent "#f0f0f0" \
    "${OUTPUT_DIR}/${ASSET_NAME}.png"
  echo "✓ Фон удалён (ImageMagick)"
elif command -v convert >/dev/null 2>&1; then
  convert "${OUTPUT_DIR}/${ASSET_NAME}.png" \
    -fuzz 15% -transparent white \
    -fuzz 10% -transparent "#f0f0f0" \
    "${OUTPUT_DIR}/${ASSET_NAME}.png"
  echo "✓ Фон удалён (ImageMagick)"
else
  echo "Фон не удалён: нет rembg/ImageMagick. Перегенерируй с чистым белым фоном."
fi

FINAL_SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Готово: ${OUTPUT_DIR}/${ASSET_NAME}.png (${FINAL_SIZE})"
```

### Режим 3: Legacy fallback Google Imagen API

```bash
API_KEY="[ключ от пользователя]"
ASSET_NAME="cherry"
PROMPT="Professional game asset: cherry. Single isolated object on plain solid pure-white background, 2D game sprite, vibrant style, no scene, no ground shadow, 512x512."
OUTPUT_DIR="assets/images/sprites"
mkdir -p "${OUTPUT_DIR}"

curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"instances\": [{\"prompt\": \"${PROMPT}\"}], \"parameters\": {\"sampleCount\": 1, \"aspectRatio\": \"1:1\"}}" \
  -o /tmp/imagen_response.json

# Декодировать base64 → PNG
python3 -c "
import json, base64, sys
with open('/tmp/imagen_response.json') as f:
    data = json.load(f)
if 'error' in data:
    print(f'✗ {data[\"error\"]}'); sys.exit(1)
img_b64 = data['predictions'][0]['bytesBase64Encoded']
path = '${OUTPUT_DIR}/${ASSET_NAME}.png'
open(path, 'wb').write(base64.b64decode(img_b64))
print(f'✓ {path}')
"
```

**4. Проверить результат:**
```bash
ls -lh ${OUTPUT_DIR}/${ASSET_NAME}.png
file ${OUTPUT_DIR}/${ASSET_NAME}.png
```

**5. Сообщить пользователю** путь к готовому файлу.

---

## Вариант Б: Bulk-режим (вся папка)

```
/svg-to-png --bulk assets/images/svgs --cheap pk_xxx --free xxx
```

Агент:
1. Находит все `.svg` файлы в папке через Glob
2. Определяет API ключи из флагов или запрашивает **один раз**
3. Обрабатывает каждый файл последовательно (один Bash call = один файл)
4. В Codex использовать GPT Images 2.0 для каждого SVG; при сбое повторить через GPT Images/default fallback.
5. Для legacy Pollinations: пауза 3 сек между запросами.
6. Для legacy Google Imagen: пауза 4 сек (лимит Free tier: 15 RPM).
7. Сохраняет PNG в `assets/images/pngs/` или рядом с исходниками

### Bulk через Codex GPT Images 2.0 → GPT Images fallback:

Агент делает отдельный image-generation call для каждого SVG файла, используя шаблон из Режима 1.
**Не объединять в один запрос** — один SVG = один PNG.

---

## Вариант В: Ручной режим (без API)

Если пользователь не хочет использовать API:

### Шаг 1: Анализ SVG
Агент читает SVG и составляет детализированный промпт на английском.

### Шаг 2: Промпт для внешнего генератора
```
Professional game asset: [название].
Single isolated object, clean edges, vibrant colors.
2D game sprite style, plain solid pure-white background, no scene, no ground shadow, 1024x1024 pixels.
[описание цветов и формы из SVG]
```

### Шаг 3: Пользователь генерирует PNG вручную и сохраняет в проект.

---

## Legacy-модели Pollinations для конвертации

| Модель | Рекомендация | Почему |
|--------|-------------|--------|
| `flux` | Legacy fallback | Хорошее качество, быстро, дёшево |
| `zimage` | Для крупных спрайтов | Встроенный 2x upscale |
| `gptimage` | Для сложных ассетов | Лучшее качество, поддержка прозрачности (`transparent: true`) |

---

## Важные правила

1. В Codex использовать GPT Images 2.0 первым; если он не сработал, GPT Images/default fallback.
2. **Один image-generation call = один ассет** — не объединять SVG в один запрос.
3. API ключ legacy-provider никогда не записывается в файлы.
4. Если legacy API вернул ошибку — показать пользователю полный ответ.
5. Готовые PNG сохранять в `assets/images/sprites/` (одиночный) или `assets/images/pngs/` (bulk).
6. После завершения — показать `ls -lh` с результатами.

## Диагностика

| Симптом | Причина | Решение |
|---------|---------|---------|
| HTTP 401 (Pollinations) | Неверный API ключ | Проверить ключ на https://enter.pollinations.ai |
| HTTP 402 (Pollinations) | Недостаточно pollen | Пополнить или использовать бесплатную модель (flux) |
| Пустой PNG | Сервер не вернул данные | Попробовать другую модель или промпт |
| Плохое качество | Промпт слишком простой | Добавить детали из SVG (цвета, форма, стиль) |
| Фон не удалился | Нет `rembg`/ImageMagick или сложный фон | Перегенерировать с чистым белым фоном, затем повторить локальный cutout |
