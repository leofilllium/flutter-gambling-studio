---
name: svg-to-png
description: "Конвертация SVG-ассетов в качественные PNG: ручной режим через промпты или автоматический bulk-режим через API Google Imagen. Без Python — агент использует curl напрямую."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[путь_к_svg] [--bulk папка_с_svg]"
user-invocable: true
---

# `svg-to-png` — Конвертер SVG → PNG через Google Imagen API

Агент выполняет всю конвертацию самостоятельно через REST API, используя `curl` и стандартные shell-утилиты. Python не требуется.

---

## Как работает агент

### Шаг 0: Запрос API ключа у пользователя

Агент ВСЕГДА запрашивает ключ вручную — не читает `.env`, не ищет переменные окружения:

> **Задай пользователю вопрос:**
> "Введите ваш Google AI Studio API ключ (он не будет сохранён в файлы):
> Получить ключ: https://aistudio.google.com/app/apikey"

Сохрани ключ только в переменную внутри Bash-команды — нигде не записывать его в файлы.

---

## Вариант А: Одиночный файл

```
/svg-to-png assets/images/sprites/sprite_cherry.svg
```

### Алгоритм (агент выполняет сам):

**1. Прочитать SVG** через Read tool, извлечь:
- Название ассета из имени файла (например `sprite_cherry` → `cherry`)
- Цвета, форму, назначение из содержимого SVG

**2. Сформировать промпт** на английском:
```
Professional casino slot game asset: [asset_name].
Single isolated object, clean edges, vibrant casino style, high detail.
2D game sprite on transparent background, 512x512.
Style derived from: [краткое описание из SVG — цвета, форма, до 200 символов]
```

**3. Вызвать Google Imagen API через curl:**
```bash
API_KEY="ключ_от_пользователя"
ASSET_NAME="cherry"
PROMPT="Professional casino slot game asset: cherry. Single isolated object, clean edges, vibrant casino style. 2D game sprite, 512x512."

curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"instances\": [{\"prompt\": \"${PROMPT}\"}],
    \"parameters\": {\"sampleCount\": 1, \"aspectRatio\": \"1:1\"}
  }" \
  -o /tmp/imagen_response.json

echo "HTTP статус: $(cat /tmp/imagen_response.json | python3 -c 'import sys,json; d=json.load(sys.stdin); print("OK" if "predictions" in d else d)' 2>/dev/null || echo 'смотри файл')"
```

**4. Декодировать base64 и сохранить PNG:**
```bash
# Извлечь base64 из JSON и декодировать в PNG
cat /tmp/imagen_response.json | \
  python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
img_b64 = data['predictions'][0]['bytesBase64Encoded']
with open('assets/images/sprites/${ASSET_NAME}.png', 'wb') as f:
    f.write(base64.b64decode(img_b64))
print('Сохранено!')
"
```

> **ВАЖНО:** Если `python3` недоступен — используй альтернативу через `base64` CLI:
> ```bash
> # macOS / Linux
> cat /tmp/imagen_response.json | grep -o '"bytesBase64Encoded":"[^"]*"' | \
>   cut -d'"' -f4 | base64 --decode > assets/images/sprites/${ASSET_NAME}.png
> ```

**5. Проверить результат:**
```bash
ls -lh assets/images/sprites/${ASSET_NAME}.png
file assets/images/sprites/${ASSET_NAME}.png
```

**6. Сообщить пользователю** путь к готовому файлу.

---

## Вариант Б: Bulk-режим (вся папка)

```
/svg-to-png --bulk assets/images/svgs
```

Агент:
1. Находит все `.svg` файлы в папке через Glob
2. Запрашивает API ключ **один раз**
3. Обрабатывает каждый файл последовательно (4 секунды пауза между запросами — лимит Free tier: 15 RPM)
4. Сохраняет PNG рядом с исходниками или в `assets/images/pngs/`

### Bulk curl-цикл (агент запускает через Bash):
```bash
API_KEY="ключ_от_пользователя"
INPUT_DIR="assets/images/svgs"
OUTPUT_DIR="assets/images/pngs"
mkdir -p "${OUTPUT_DIR}"

for svg_file in "${INPUT_DIR}"/*.svg; do
  ASSET_NAME=$(basename "${svg_file}" .svg)
  echo "=== Обработка: ${ASSET_NAME} ==="

  SVG_PREVIEW=$(head -c 500 "${svg_file}" | tr '"' "'" | tr '\n' ' ')
  PROMPT="Professional casino slot game asset: ${ASSET_NAME}. Single isolated object on transparent background, 2D game sprite, vibrant casino style, 512x512."

  curl -s -X POST \
    "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key=${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"instances\": [{\"prompt\": \"${PROMPT}\"}], \"parameters\": {\"sampleCount\": 1}}" \
    -o /tmp/img_response.json

  # Декодировать base64 → PNG
  B64=$(cat /tmp/img_response.json | grep -o '"bytesBase64Encoded":"[^"]*"' | cut -d'"' -f4)
  if [ -n "${B64}" ]; then
    echo "${B64}" | base64 --decode > "${OUTPUT_DIR}/${ASSET_NAME}.png"
    echo "✓ Сохранено: ${OUTPUT_DIR}/${ASSET_NAME}.png"
  else
    echo "✗ Ошибка для ${ASSET_NAME}: $(cat /tmp/img_response.json)"
  fi

  sleep 4  # Лимит Free tier API
done

echo "=== Готово ==="
ls -lh "${OUTPUT_DIR}"
```

---

## Вариант В: Ручной режим (без API)

Если пользователь не хочет использовать API:

### Шаг 1: Анализ SVG
Агент читает SVG и составляет детализированный промпт на английском.

### Шаг 2: Промпт для Nano Banana Pro / Midjourney / другого генератора
```
Professional casino slot game asset: [название].
Single isolated object, clean edges, vibrant colors.
2D game sprite style, transparent background, 512x512 pixels.
Casino/gambling aesthetic, high quality render.
[описание цветов и формы из SVG]
```

### Шаг 3: Пользователь генерирует PNG вручную и сохраняет в проект.

---

## Удаление фона (опционально)

Если сгенерированное изображение имеет белый/цветной фон — используй remove.bg API:

```bash
REMOVE_BG_KEY="ключ_remove_bg"  # Отдельный ключ от remove.bg
INPUT_PNG="assets/images/pngs/cherry.png"
OUTPUT_PNG="assets/images/pngs/cherry_transparent.png"

curl -s -X POST "https://api.remove.bg/v1.0/removebg" \
  -H "X-Api-Key: ${REMOVE_BG_KEY}" \
  -F "image_file=@${INPUT_PNG}" \
  -F "size=auto" \
  -o "${OUTPUT_PNG}"

echo "Фон удалён: ${OUTPUT_PNG}"
```

> Бесплатный tier remove.bg: 50 изображений/месяц.
> Альтернатива: Google Imagen обычно генерирует с прозрачным фоном при правильном промпте ("transparent background").

---

## Важные правила

1. **API ключ никогда не записывается в файлы** — только используется внутри Bash-команды в текущей сессии
2. **Пауза 4 сек** между запросами в bulk-режиме (лимит Google AI Studio Free tier)
3. Если API вернул ошибку — показать пользователю raw JSON из `/tmp/img_response.json`
4. Готовые PNG сохранять в `assets/images/sprites/` (одиночный) или `assets/images/pngs/` (bulk)
5. После завершения — показать `ls -lh` с результатами
