---
name: svg-to-png
description: "Конвертация SVG-ассетов в PNG. Простая пиксельная конвертация выполняется локально; если нужен новый материальный PNG-ассет, в Codex основной путь — GPT Images 2.0, fallback — GPT Images/default Codex image generation только при техническом сбое."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[путь_к_svg] [--bulk папка] [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `svg-to-png` — Конвертер SVG → PNG

Агент анализирует SVG, формирует промпт из его содержимого и генерирует качественный PNG.

---

## Выбор режима

### Codex default

Сначала определить цель. Если нужен только PNG того же SVG без нового материала, света или
детализации, это локальная конвертация и не требует image generation. Если нужен новый
материальный игровой ассет, в Codex использовать **GPT Image 2** через встроенную image
generation возможность, а при отсутствии этого tool в headless Codex CLI — через
`python3 tools/gpt_image.py generate ...`. Отсутствие built-in tool не считается провалом
модели. Если оба транспорта GPT Image 2 технически не сработали или не дали валидный PNG,
повторить тот же prompt через **GPT Images / default Codex image generation**.

- Не спрашивать ключи Google/Pollinations/remove.bg.
- Перед semantic-апгрейдом прочитать `design/asset-manifest.md`: валидное совпадение SHA-256
  prompt переиспользовать, а вызов разрешён только классу `generate` в его общем бюджете.
- Один SVG → один вызов image generation → один PNG только для semantic-апгрейда; не
  применять GPT Images 2.0 как дорогостоящий растровый конвертер UI и уже готовых иконок.
- Для `sprite`, `symbol`, `icon`, `wild`, `scatter`, `tile`, `item` просить плоский ключевой фон (`flat solid pure magenta #FF00FF background`, либо `pure green #00FF00`, если в палитре есть пурпур) без теней, градиентов и сцены.
- Для `background`, `ui_panel`, полноэкранной сцены фон не вырезать.
- Если у простого ассета фон всё же появился, вырезать его через `python3 tools/cutout.py <файл> --type sprite`.

#### Пиксельная конвертация без image generation

Если форма SVG не меняется, использовать уже доступный локальный SVG-рендерер. Например,
при наличии `rsvg-convert`:

```bash
rsvg-convert assets/images/sprites/sprite_cherry.svg -o assets/images/sprites/sprite_cherry.png
```

Если локального рендерера нет, остановиться и сообщить об этом; не заменять техническую
конвертацию дополнительным вызовом GPT Images 2.0. Семантический апгрейд остаётся отдельным
режимом `generate` и работает по манифесту/бюджету выше.

### Legacy flags:
- `--cheap POLL_API_TOKEN` → Pollinations.ai (только если пользователь явно просит legacy fallback)
- `--free REMOVE_BG_TOKEN` → remove.bg только если пользователь явно передал ключ и попросил этот сервис
- Без флагов в Codex → не спрашивать: для пиксельной конвертации использовать локальный
  рендерер, для semantic-апгрейда — GPT Images 2.0; GPT Images/default только после
  технического сбоя.

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
  SVG до мультяшного объёмного 2.5D ассета того же объекта, достоверного концепту.

**2. Сформировать промпт** на английском (concept-grounded cartoon 2.5D — НЕ дешёвый значок):

Сначала из SVG+концепта выведи: **Subject** (что это за объект в мире игры),
**Material/texture** (металл/стекло/камень/дерево/неон/ткань), **Lighting** (единый для набора,
напр. key верх-слева + rim), **Render style** из DNA.

```
Polished cartoon 2.5D game asset of [SUBJECT identity], single hero object centered,
bold rounded and slightly exaggerated silhouette, [MATERIAL/TEXTURE] simplified into
smooth modeled gradients, clean edging, glossy highlights and restrained star glints,
soft [LIGHTING] light, rich [DNA PALETTE] colors,
crisp clean silhouette, sharp focus, faithful to the original shape/colors,
isolated on flat solid single-colour [KEY COLOUR] background, no gradient, no scene, no ground shadow, no text,
no photorealism, no product photography, no flat vector clipart, transparent-ready, 1024x1024.
```

> Объект на PNG должен совпадать по форме/композиции с исходным SVG (это конвертация, не
> новая идея), но быть объёмным и материальным, а не плоской заливкой.

**3. Генерация PNG:**

### Режим 1: Codex GPT Images 2.0 → GPT Images fallback

В Codex использовать GPT Images 2.0 первым. При техническом сбое (ошибка, нет файла или
невалидный PNG) повторить тот же prompt через GPT Images / default Codex image generation.

1. Передать prompt из шага 2 во встроенную image generation возможность Codex. Если её нет
   в tool list, сохранить prompt в UTF-8 файл и выполнить:

```bash
python3 tools/gpt_image.py generate \
  --prompt-file design/prompts/<logical_id>.txt \
  --out assets/images/pngs/<logical_id>.png \
  --size 1024x1024 \
  --quality high
```
2. Сохранить результат рядом с исходником или в `assets/images/pngs/`.
3. Если тип ассета простой и PNG содержит фон — вырезать его через `tools/cutout.py`
   (ручной `magick -fuzz` и голый `rembg i` запрещены: см. `generate-png-asset/SKILL.md`):

```bash
python3 tools/cutout.py assets/images/sprites/cherry.png --type sprite
```

Ненулевой код возврата = сначала проверить исходник и ключевой цвет, затем применить один
разрешённый recovery-вызов через GPT Images 2.0. GPT Images/default использовать только при
технической ошибке GPT Images 2.0, а не из-за визуального брака или ошибки cutout.

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
python3 tools/cutout.py "${OUTPUT_DIR}/${ASSET_NAME}.png" --type sprite

FINAL_SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Готово: ${OUTPUT_DIR}/${ASSET_NAME}.png (${FINAL_SIZE})"
```

### Режим 3: Legacy fallback Google Imagen API

```bash
API_KEY="[ключ от пользователя]"
ASSET_NAME="cherry"
PROMPT="Professional game asset: cherry. Single isolated object on flat solid pure magenta #FF00FF background, no gradient, 2D game sprite, vibrant style, no scene, no ground shadow, 512x512."
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
3. Для каждого файла сначала выбирает локальную конвертацию или semantic-апгрейд и проверяет
   `design/asset-manifest.md`; совпадающий валидный SHA-256 переиспользует.
4. В Codex использовать GPT Images 2.0 только для уникального semantic-апгрейда класса
   `generate`; GPT Images/default разрешён лишь после технического сбоя.
5. Для legacy Pollinations: пауза 3 сек между запросами.
6. Для legacy Google Imagen: пауза 4 сек (лимит Free tier: 15 RPM).
7. Сохраняет PNG в `assets/images/pngs/` или рядом с исходниками

### Bulk через Codex GPT Images 2.0 → GPT Images fallback:

Агент делает отдельный image-generation call только для каждого уникального semantic-апгрейда,
используя шаблон из Режима 1. Простые копии формы рендерит локально, а `reuse` не вызывает
модель. Не объединять разные игровые предметы в один запрос.

---

## Вариант В: Ручной режим (без API)

Если пользователь не хочет использовать API:

### Шаг 1: Анализ SVG
Агент читает SVG и составляет детализированный промпт на английском.

### Шаг 2: Промпт для внешнего генератора
```
Professional game asset: [название].
Single isolated object, clean edges, vibrant colors.
2D game sprite style, flat solid pure magenta #FF00FF background, no gradient, no scene, no ground shadow, 1024x1024 pixels.
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

1. В Codex использовать GPT Images 2.0 первым только для semantic-апгрейда; GPT Images/default
   доступен исключительно после технического сбоя GPT Images 2.0.
2. **Один image-generation call = один уникальный source asset** — не объединять разные
   игровые объекты в один запрос.
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
| `cutout.py` вернул FAIL | Фон не плоский, или ключ совпал с палитрой объекта | Проверить исходник/ключ и перевырезать; при непригодном источнике использовать один GPT Images 2.0 recovery, не fallback по качеству |
| `cutout.py: requires numpy + Pillow` | Нет зависимостей | `apt-get install -y python3-numpy python3-pil` (или `pip install numpy pillow`) |
