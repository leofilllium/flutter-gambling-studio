---
name: svg-to-png
description: "Конвертация SVG-ассетов в качественные PNG: через Pollinations.ai (--cheap POLL_KEY) или Google Imagen API. Удаление фона через remove.bg (--free REMBG_KEY)."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[путь_к_svg] [--bulk папка] [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `svg-to-png` — Конвертер SVG → PNG

Агент анализирует SVG, формирует промпт из его содержимого, генерирует качественный PNG через API.

---

## Выбор режима

### Флаги:
- `--cheap POLL_API_TOKEN` → Pollinations.ai (рекомендуемый, дёшево и быстро)
- `--free REMOVE_BG_TOKEN` → автоудаление фона через remove.bg после генерации
- Без флагов → спросить пользователя

### Если флагов нет — спросить:

> "Как конвертировать SVG → PNG?
>
> **1. Pollinations.ai** — дёшево, быстро, нужен API ключ (https://enter.pollinations.ai)
> **2. Google Imagen** — требует Google Cloud Billing
> **3. Ручной режим** — сгенерирую промпт, вы генерируете PNG сами
>
> Введите 1, 2 или 3:"

---

## Вариант А: Одиночный файл

```
/svg-to-png assets/images/sprites/sprite_cherry.svg --cheap pk_xxx --free xxx
```

### Алгоритм (агент выполняет сам):

**1. Прочитать SVG** через Read tool, извлечь:
- Название ассета из имени файла (например `sprite_cherry` → `cherry`)
- Цвета, форму, назначение из содержимого SVG

**2. Сформировать промпт** на английском:
```
Professional game asset: [asset_name].
Single isolated object, clean edges, vibrant style, high detail.
2D game sprite on pure white background, 1024x1024.
Style derived from: [краткое описание из SVG — цвета, форма, до 200 символов]
```

**3. Генерация PNG:**

### Режим 1: Pollinations.ai (--cheap)

```bash
POLL_API_KEY="[ключ от --cheap]"
ASSET_NAME="cherry"
PROMPT="Professional game asset: cherry. Red glossy cherries, single isolated object, clean edges, vibrant cartoon style, 2D game sprite, pure white background, 1024x1024"
OUTPUT_DIR="assets/images/sprites"
REMBG_KEY=""  # от --free, или пустой
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

# Удаление фона (если есть REMBG_KEY)
if [ -n "${REMBG_KEY}" ]; then
  echo "Удаляю фон (remove.bg)..."
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
else
  # ImageMagick fallback
  if command -v convert &>/dev/null; then
    convert "${OUTPUT_DIR}/${ASSET_NAME}.png" \
      -fuzz 15% -transparent white \
      -fuzz 10% -transparent "#f0f0f0" \
      "${OUTPUT_DIR}/${ASSET_NAME}.png"
    echo "✓ Фон удалён (ImageMagick)"
  fi
fi

FINAL_SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Готово: ${OUTPUT_DIR}/${ASSET_NAME}.png (${FINAL_SIZE})"
```

### Режим 2: Google Imagen API

```bash
API_KEY="[ключ от пользователя]"
ASSET_NAME="cherry"
PROMPT="Professional game asset: cherry. Single isolated object on transparent background, 2D game sprite, vibrant style, 512x512."
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
4. Для Pollinations: пауза 3 сек между запросами
5. Для Google Imagen: пауза 4 сек (лимит Free tier: 15 RPM)
6. Сохраняет PNG в `assets/images/pngs/` или рядом с исходниками

### Bulk через Pollinations (рекомендуемый):

Агент делает отдельный Bash call для каждого SVG файла, используя шаблон из Режима 1.
**Не объединять в цикл** — один Bash call = один ассет.

---

## Вариант В: Ручной режим (без API)

Если пользователь не хочет использовать API:

### Шаг 1: Анализ SVG
Агент читает SVG и составляет детализированный промпт на английском.

### Шаг 2: Промпт для внешнего генератора
```
Professional game asset: [название].
Single isolated object, clean edges, vibrant colors.
2D game sprite style, transparent background, 1024x1024 pixels.
[описание цветов и формы из SVG]
```

### Шаг 3: Пользователь генерирует PNG вручную и сохраняет в проект.

---

## Модели Pollinations для конвертации

| Модель | Рекомендация | Почему |
|--------|-------------|--------|
| `flux` | По умолчанию | Хорошее качество, быстро, дёшево |
| `zimage` | Для крупных спрайтов | Встроенный 2x upscale |
| `gptimage` | Для сложных ассетов | Лучшее качество, поддержка прозрачности (`transparent: true`) |

---

## Важные правила

1. **API ключ никогда не записывается в файлы** — только используется внутри Bash-команды
2. **Один Bash call = один ассет** — не объединять в цикл
3. Если API вернул ошибку — показать пользователю полный ответ
4. Готовые PNG сохранять в `assets/images/sprites/` (одиночный) или `assets/images/pngs/` (bulk)
5. После завершения — показать `ls -lh` с результатами

## Диагностика

| Симптом | Причина | Решение |
|---------|---------|---------|
| HTTP 401 (Pollinations) | Неверный API ключ | Проверить ключ на https://enter.pollinations.ai |
| HTTP 402 (Pollinations) | Недостаточно pollen | Пополнить или использовать бесплатную модель (flux) |
| Пустой PNG | Сервер не вернул данные | Попробовать другую модель или промпт |
| Плохое качество | Промпт слишком простой | Добавить детали из SVG (цвета, форма, стиль) |
| remove.bg не работает | Неверный ключ или лимит исчерпан | Проверить на remove.bg/dashboard, использовать ImageMagick |
