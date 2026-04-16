---
name: generate-png-asset
description: "Генерация PNG-ассетов через Pollinations.ai (дёшево с ключом / бесплатные модели) или Google Gemini. Удаление фона через remove.bg. Флаги: --cheap POLL_KEY --free REMBG_KEY."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[описание] | [--batch список] | [--from-concept] | [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `generate-png-asset` — PNG ассеты для мини-игр

## Сервисы генерации

| Сервис | Стоимость | Требования | Качество | Флаг |
|--------|-----------|------------|----------|------|
| **Pollinations.ai** (flux, zimage) | Дёшево с API ключом / бесплатные модели | API ключ (`pk_` или `sk_`) | Среднее-Высокое | `--cheap POLL_API_TOKEN` |
| **Pollinations.ai** (gptimage) | Платно (pollen баланс) | API ключ | Высокое | `--cheap POLL_API_TOKEN` |
| **Google Gemini** | ~$0.003/изображение | Google Cloud Billing | Высокое | (без флага) |
| **SVG** | Бесплатно | Ничего | Векторное | → `/generate-asset` |

**Удаление фона:** remove.bg (50 бесплатных/мес) → флаг `--free REMOVE_BG_TOKEN`

---

## Шаг 0: Определение режима

### Если переданы флаги:
- `--cheap POLL_API_TOKEN` → Pollinations.ai с ключом (Режим 1)
- `--cheap POLL_API_TOKEN --free REMOVE_BG_TOKEN` → Pollinations + auto remove.bg
- Без флагов → спросить пользователя

### Если флагов нет — спросить:

> "Как генерировать PNG ассеты?
>
> **1. Pollinations.ai** — дёшево, быстро, модели flux/zimage/gptimage (нужен API ключ → https://enter.pollinations.ai)
> **2. Google Gemini** — требует Google Cloud Billing (~$0.003/изображение)
> **3. SVG** — бесплатно, через /generate-asset
>
> Введите 1, 2 или 3:"

---

## Режим 1: Pollinations.ai (рекомендуемый)

**API Base:** `https://gen.pollinations.ai`
**Ключи:** `https://enter.pollinations.ai`
**Авторизация:** Header `Authorization: Bearer API_KEY` или query `?key=API_KEY`

### Модели изображений (Pollinations)

| Модель | Качество | Цена | Особенности |
|--------|---------|------|-------------|
| `flux` | Хорошее | Дёшево | Быстрая, по умолчанию |
| `zimage` | Хорошее + 2x upscale | Дёшево | Fast 6B Flux с апскейлом |
| `gptimage` | Высокое | Платно (pollen) | OpenAI image gen, поддержка прозрачности |
| `gptimage-large` | Очень высокое | Платно | HD, прозрачность |
| `klein` | Среднее | Дёшево | FLUX.2 Klein 4B, быстрая |

### Удаление фона: определить в начале

Если передан `--free REMOVE_BG_TOKEN` → использовать remove.bg автоматически.
Иначе спросить:

> "Есть ключ remove.bg для автоудаления фона? (`--free КЛЮЧ`)
> (50 бесплатных/мес → remove.bg/dashboard)
> Если нет — используем ImageMagick (хуже качество, но бесплатно)"

Сохрани: `REMBG_KEY="ключ"` или `REMBG_KEY=""` (пустой = ImageMagick fallback).

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
MODEL="flux"          # flux | zimage | gptimage | klein
REMBG_KEY=""          # вставить ключ remove.bg (--free) или оставить пустым
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

  if [ -n "${REMBG_KEY}" ]; then
    # remove.bg (лучшее качество)
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
    # ImageMagick fallback (бесплатно)
    if command -v convert &>/dev/null; then
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

### Промпты для символов по умолчанию:

| Символ | ASSET_TYPE | Промпт |
|--------|-----------|--------|
| cherry | symbol | `red glossy cherries fruit, game sprite, pure white background, vibrant cartoon` |
| bar | symbol | `chrome metallic BAR text, slot machine symbol, pure white background, shiny 3D` |
| seven | symbol | `lucky number seven, red with gold outline, bold game icon, pure white background` |
| diamond | symbol | `blue diamond gemstone, crystal faceted, game icon, pure white background, glossy` |
| wild | wild | `golden star wild, glowing rainbow aura, game icon, pure white background` |
| scatter | scatter | `purple hexagon lightning bolt, scatter symbol, game icon, pure white background` |
| main_menu_bg | background | `dark cyberpunk casino background, neon lights, atmospheric, no characters` |

### Особенности:
- Белый фон в промпте → ImageMagick/remove.bg убирают его точнее
- Модели: `flux` (по умолчанию), `zimage` (с upscale), `gptimage` (лучшее качество, платно)
- Каждый Bash call = один ассет (не объединять в цикл)
- `seed=-1` для случайного результата каждый раз

---

## Режим 2: Google Gemini — требует биллинг

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

```
Professional 2D casino slot game asset: [НАЗВАНИЕ].
Single isolated object on white background, cartoon glossy style,
vibrant [ЦВЕТА ТЕМЫ] color palette, bold clean outline,
high quality game sprite, 512x512 pixels.
[ТИП-ДЕТАЛИ]
```

### Детали по типу:
| Тип | Добавить |
|-----|---------|
| `symbol` (вишня, бар, 7) | "glossy shiny surface, cartoon with depth and highlights" |
| `wild` | "golden glowing wild symbol, premium casino look, radiant aura" |
| `scatter` | "mystical scatter symbol, glowing particles, magical energy" |
| `ui` кнопка | "neon glowing button, casino UI element, no text" |
| `background` | "dark casino atmospheric pattern, subtle texture, no characters" |

> **Важно для прозрачного фона:** Imagen/Gemini не всегда генерирует RGBA.
> Используй белый фон + remove.bg на Шаге 5. В промпте пиши `"white background"`.

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

## Шаг 5: Удаление фона (опционально)

Спросить пользователя: "Удалить фон через remove.bg? (50 бесплатных/мес, нужен отдельный ключ)"

```bash
REMBG_KEY="[ключ remove.bg — получить на remove.bg/api]"
INPUT_PNG="${OUTPUT_DIR}/${ASSET_NAME}.png"
TMP_PNG="${OUTPUT_DIR}/${ASSET_NAME}_nobg.png"

curl -s -X POST "https://api.remove.bg/v1.0/removebg" \
  -H "X-Api-Key: ${REMBG_KEY}" \
  -F "image_file=@${INPUT_PNG}" \
  -F "size=auto" \
  -o "${TMP_PNG}"

if [ -s "${TMP_PNG}" ]; then
  mv "${TMP_PNG}" "${INPUT_PNG}"
  echo "✓ Фон удалён: ${INPUT_PNG}"
else
  echo "Ошибка remove.bg — оригинал сохранён"
  rm -f "${TMP_PNG}"
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
- Следующий Bash tool call только ПОСЛЕ того как предыдущий вернул результат

---

### Шаблон одного ассета — Gemini (копировать и менять ASSET_NAME + PROMPT):

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
