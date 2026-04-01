---
name: generate-png-asset
description: "Генерация PNG-ассетов через Google AI Studio API (требует биллинг) или альтернативы: Stability AI, Pollinations.ai (бесплатно без ключа). SVG через generate-asset всегда бесплатно."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[описание ассета] | [--batch список_через_запятую] | [--from-concept] | [--free]"
user-invocable: true
---

# `generate-png-asset` — PNG ассеты для гемблинг-игры

## ВАЖНО: Статус бесплатного доступа (актуально)

| Сервис | Бесплатно? | Требования | Качество |
|--------|-----------|------------|---------|
| **Google Gemini 2.5 Flash Image** | ❌ НЕТ — `limit: 0` на free tier | Google Cloud Billing включён | Высокое |
| **Google Gemini 2.0 Flash Exp** | ⚠️ Экспериментально, может не работать | AI Studio ключ | Среднее |
| **Pollinations.ai** | ✅ ДА — полностью бесплатно, без ключа | Ничего | Среднее |
| **Stability AI** | ⚠️ Ограниченный free tier | API ключ с stability.ai | Высокое |
| **SVG через generate-asset** | ✅ ДА — всегда бесплатно | Ничего | Векторное |

**Рекомендация для прототипов:** Pollinations.ai (бесплатно, без регистрации)
**Рекомендация для продакшна:** Google Gemini с включённым биллингом (~$0.003/изображение)

---

## Шаг 0: Выбор режима генерации

Спроси пользователя:

> "Как генерировать PNG ассеты?
>
> **1. Pollinations.ai** — БЕСПЛАТНО, без ключа, без регистрации (рекомендую для старта)
> **2. Google Gemini** — требует Google Cloud Billing (~$0.003/изображение), высокое качество
> **3. SVG** — полностью бесплатно, через /generate-asset (векторные, встраиваются в Flame)
>
> Введите 1, 2 или 3:"

- Выбор 1 → раздел «Pollinations.ai (бесплатно)»
- Выбор 2 → раздел «Google Gemini API»
- Выбор 3 → вызвать логику `/generate-asset` (SVG режим)

---

---

## Режим 1: Pollinations.ai — БЕСПЛАТНО, без ключа

Простой GET-запрос с промптом в URL. Никакой авторизации.
После генерации символа/иконки — **автоматическое удаление фона**.

### Удаление фона: спросить один раз в начале

> "Есть ключ remove.bg для автоудаления фона?
> (50 бесплатных/мес → remove.bg/dashboard)
> Если нет — используем ImageMagick (хуже качество, но бесплатно и без ключа)"

Сохрани выбор: `REMBG_KEY="ключ"` или `REMBG_KEY=""` (пустой = ImageMagick fallback).

---

### Шаблон одного символа (один Bash call):

Ассеты типа `symbol`, `icon`, `wild`, `scatter` → **фон удаляется автоматически**.
Ассеты типа `background`, `ui_panel` → фон НЕ удаляется.

```bash
ASSET_NAME="cherry"
ASSET_TYPE="symbol"   # symbol | icon | wild | scatter | background | ui_panel
PROMPT="red glossy cherries fruit, game sprite icon, pure white background, vibrant colors, cartoon style, isolated object"
OUTPUT_DIR="assets/images/pngs"
REMBG_KEY=""          # вставить ключ remove.bg или оставить пустым
mkdir -p "${OUTPUT_DIR}"

echo "━━━ [symbol] Генерирую: ${ASSET_NAME} ━━━"

# 1. Генерация через Pollinations.ai
ENCODED=$(echo "${PROMPT}" | sed 's/ /+/g; s/,/%2C/g')
curl -s -L "https://image.pollinations.ai/prompt/${ENCODED}?width=1024&height=1024&nologo=true&model=flux" -o "${OUTPUT_DIR}/${ASSET_NAME}.png"

if [ ! -s "${OUTPUT_DIR}/${ASSET_NAME}.png" ]; then
  echo "✗ Pollinations не вернул изображение"
  exit 1
fi

SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Сгенерирован: ${SIZE}"

# 2. Удаление фона (только для symbol/icon/wild/scatter)
if [[ "${ASSET_TYPE}" == "symbol" || "${ASSET_TYPE}" == "icon" || "${ASSET_TYPE}" == "wild" || "${ASSET_TYPE}" == "scatter" ]]; then
  echo "🔲 Удаляю фон..."

  if [ -n "${REMBG_KEY}" ]; then
    # Вариант А: remove.bg (лучшее качество)
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
    # Вариант Б: ImageMagick (базовое качество, бесплатно)
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
echo "⏳ Пауза 10 сек..."
sleep 10
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
- Модели: `flux` (качество), `turbo` (быстрее)
- Каждый Bash call = один ассет (не объединять в цикл)

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
- `design/gdd/gambling-concept.md` → тема, цвета, стиль
- `design/balance/rtp-config.json` → список символов

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
- `sleep 65` ВНУТРИ каждого скрипта ПОСЛЕ успешного сохранения
- Sleep встроен в скрипт — bash call не вернётся пока не выждет паузу
- Следующий Bash tool call только ПОСЛЕ того как предыдущий вернул результат

---

### Шаблон одного ассета (копировать и менять ASSET_NAME + PROMPT):

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

**Call 1:** cherry → ждёт завершения (включая sleep 65) → сообщает "✓ cherry готов (1/6)"
**Call 2:** bar → ждёт завершения → "✓ bar готов (2/6)"
**Call 3:** seven → ждёт завершения → "✓ seven готов (3/6)"
**Call 4:** diamond → ждёт завершения → "✓ diamond готов (4/6)"
**Call 5:** wild → ждёт завершения → "✓ wild готов (5/6)"
**Call 6:** scatter → sleep НЕ НУЖЕН в последнем → "✓ scatter готов (6/6)"

При ошибке — остановиться, показать JSON, спросить пользователя.

---

## --from-concept: из rtp-config.json автоматически

1. Читаем `design/balance/rtp-config.json` → список `symbols[].name`
2. Читаем `design/gdd/gambling-concept.md` → тема и цвета
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

| Симптом | Причина | Решение |
|---------|---------|---------|
| HTTP 403 | Неверный ключ или Gemini API не активирован | AI Studio → API Keys → убедиться что Gemini API включён |
| HTTP 404 `model not found` | Неверное имя модели | Попробовать `gemini-2.5-flash-preview-image-generation` (альтернативное имя) |
| HTTP 400 `responseModalities` | Модель не поддерживает IMAGE | Добавить `"TEXT"` к списку: `["IMAGE","TEXT"]` |
| HTTP 429 | Превышен лимит 10 RPM | Увеличить sleep до 8-10 сек, дождаться сброса квоты |
| `inlineData` не найден | Gemini вернул только текст | Изменить промпт: начать с "Create an image of..." |
| Imagen 403 / 404 | Требует платный биллинг Vertex AI | Не использовать Imagen — только `gemini-2.5-flash-image` |
| PNG файл пустой | Ошибка base64 или пустой ответ | `cat /tmp/gemini_resp_[name].json` — показать пользователю полный JSON |
| Ошибка содержимого (safety) | Промпт заблокирован фильтром | Убрать слова gambling/casino из промпта, заменить на "game symbol" |

**Правило:** При ЛЮБОЙ ошибке — показывать пользователю полный JSON из `/tmp/gemini_resp_*.json`. Никогда не скрывать ответ API.
