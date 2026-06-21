---
name: asset-review
description: "Vision-ревью сгенерированных ассетов на профессиональную целостность: единый стиль/свет/детализация набора, соответствие Design DNA, читаемость в игровом размере, чистая альфа, отсутствие AI-артефактов. Бракует выбивающиеся ассеты и перегенерирует их (Codex: GPT Images 2.0 → GPT Images/default fallback; SVG-режим: правка кода). Вызывается автоматически из /autocreate (Фаза 3.6) или вручную для любого проекта."
argument-hint: "[--sprites-only | --report-only]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Asset Review — Визуальная целостность набора ассетов

Игра выглядит профессионально только если ВСЕ ассеты выглядят сделанными одним художником.
Генерация по одному промпту на ассет неизбежно даёт «разнобой» — этот навык его ловит и чинит.

**Роль**: `art-director` (`.claude/agents/art-director.md`) — прочитать ПЕРВЫМ действием.
В средах без Agent tool (Codex) — принять persona арт-директора и выполнить протокол самому.

---

## Фаза 1 — Контекст и инвентаризация [~1 мин]

1. Прочитать `design/gdd/game-concept.md` → секция **Design DNA** (Visual World, Color
   Palette, Shape Language, Depth & Effects Strategy). Это эталон ревью.
2. Прочитать `design/asset-format.md` → `format: png|svg`.
3. Инвентаризация:

```bash
ls -la assets/images/sprites/ assets/images/ui/ assets/images/backgrounds/ 2>/dev/null
```

Если ассетов нет — остановиться: «нечего ревьюить, сначала /generate-asset».

## Фаза 2 — Контактные листы [~1 мин]

```bash
mkdir -p production/asset-review
EXT=$(grep '^format:' design/asset-format.md 2>/dev/null | awk '{print $2}'); EXT=${EXT:-png}

if command -v montage >/dev/null 2>&1 && [ "$EXT" = "png" ]; then
  montage assets/images/sprites/*.png -tile 4x -geometry 256x256+8+8 -background '#202020' \
    production/asset-review/contact-sprites.png 2>/dev/null
  # Ключевой лист: как игрок РЕАЛЬНО увидит спрайты (64px)
  montage assets/images/sprites/*.png -tile 8x -geometry 64x64+4+4 -background '#202020' \
    production/asset-review/contact-sprites-64px.png 2>/dev/null
  montage assets/images/ui/*.png -tile 4x -geometry 256x256+8+8 -background '#202020' \
    production/asset-review/contact-ui.png 2>/dev/null
  echo "✅ Контактные листы → production/asset-review/"
else
  echo "ℹ️ montage недоступен или SVG-режим — ревью по одному файлу"
fi
```

SVG-режим: отрендерить в PNG для просмотра, если есть конвертер
(`rsvg-convert`/`inkscape`/`flutter`-рендер недоступен — читать SVG-код и оценивать
структуру: единая палитра, стиль градиентов, толщина обводки).

## Фаза 3 — Vision-оценка (10 критериев AR1–AR10) [~3 мин]

Просмотреть через Read (vision): контактные листы (или каждый файл), КАЖДЫЙ фон в полном
размере, и **обязательно** 64px-лист — читаемость в игровом размере важнее красоты в 1024px.

Критерии (детали в `art-director.md`):

| # | Критерий | # | Критерий |
|---|----------|---|----------|
| AR1 | Единый стиль рендера | AR6 | Чистая альфа (без ореолов) |
| AR2 | Единый источник света | AR7 | Иконки — один стиль/вес |
| AR3 | Единая детализация | AR8 | Фон уступает фокус полю |
| AR4 | Палитра из Design DNA | AR9 | Предмет опознаётся |
| AR5 | Читаемость в 64 px | AR10 | Нет AI-артефактов |

Техническая проверка альфы (PNG, дополняет визуальную):

```bash
python3 - <<'PY'
from pathlib import Path
try:
    from PIL import Image
    for p in sorted(Path("assets/images/sprites").glob("*.png")):
        im = Image.open(p).convert("RGBA")
        amin, _ = im.getchannel("A").getextrema()
        print(f"{'✓' if amin < 255 else '✗ НЕТ АЛЬФЫ'} {p.name}")
except ImportError:
    print("ℹ Pillow нет — только визуальная проверка")
PY
```

## Фаза 4 — Отчёт и вердикт [~1 мин]

Записать `design/asset-review.md`: таблица ассет → вердикт (PASS/FAIL) → критерий →
действие (см. шаблон в `art-director.md`). Общий вердикт: **PASS** или **REGENERATE (N)**.

`--report-only`: остановиться здесь, вернуть отчёт.

## Фаза 5 — Перегенерация бракованных [~3 мин, до 2 итераций]

Только FAIL-ассеты (НЕ весь набор):

- **PNG (Codex)** — перегенерировать через GPT Images 2.0 с ИСПРАВЛЕННЫМ промптом;
  если GPT Images 2.0 не сработал, повторить тот же промпт через GPT Images/default fallback:
  исходный промпт + «якорь стиля» набора (стиль рендера, свет, палитра — одной и той же
  фразой для всех) + конкретное исправление причины брака + чистый белый фон для простых
  ассетов. После генерации — вырезание
  фона (rembg) и проверка альфы (как в `/autocreate` Фаза 3).
- **SVG** — править код ассета: палитра/градиенты/обводка к общему стилю набора.

Повторить Фазу 3 ТОЛЬКО для перегенерированных. После 2-й итерации — принять лучшее,
остаточные риски записать в отчёт (не зацикливаться: конвейер важнее идеального ассета).

## Критерии выхода

- `design/asset-review.md` с вердиктом и таблицей по каждому ассету
- Контактные листы в `production/asset-review/` (если montage доступен)
- 0 ассетов с вердиктом FAIL без выполненной перегенерации (либо явная пометка
  «принято после 2 итераций» с причиной)
- Все PNG sprites/icons — с подтверждённой альфой
