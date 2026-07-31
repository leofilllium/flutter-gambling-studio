---
name: asset-review
description: "Vision-ревью сгенерированных ассетов на профессиональную целостность: единый стиль/свет/детализация набора, соответствие Design DNA, читаемость в игровом размере, чистая альфа, отсутствие AI-артефактов. Сначала исправляет локально, затем расходует ограниченный recovery GPT Images 2.0; fallback — только при техническом сбое. Вызывается автоматически из /autocreate (Фаза 3.6) или вручную для любого проекта."
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
3. Для PNG прочитать `design/asset-manifest.md`: класс, SHA-256 prompt, число попыток и
   оставшийся бюджет recovery. Совпадающий валидный кэш не считать новым ассетом и не
   перегенерировать.
4. Инвентаризация:

```bash
ls -la assets/images/sprites/ assets/images/ui/ assets/images/backgrounds/ 2>/dev/null
```

Если ассетов нет — остановиться: «нечего ревьюить, сначала /generate-asset».

Если это существующий проект без `design/asset-manifest.md`, восстановить его из
`design/asset-prompts.md` и инвентаризации файлов до начала ревью. Отсутствие манифеста
никогда не является причиной повторно генерировать уже существующий ассет.

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
| AR1 | Единый polished cartoon 2.5D стиль; нет photoreal/product-shot/flat clipart | AR6 | Чистая альфа (без ореолов) |
| AR2 | Единый источник света | AR7 | Иконки — один стиль/вес |
| AR3 | Единая детализация | AR8 | Фон уступает фокус полю |
| AR4 | Палитра из Design DNA | AR9 | Предмет опознаётся |
| AR5 | Читаемость в 64 px | AR10 | Нет AI-артефактов |

Техническая проверка альфы для AR6 (PNG, дополняет визуальную) — `tools/cutout.py --check`
измеряет ровно те дефекты, которые глаз плохо ловит на превью 1024 px:

```bash
python3 tools/cutout.py --dir assets/images/sprites --check
python3 tools/cutout.py --dir assets/images/ui --check
```

| Код | Что означает | Действие |
|-----|--------------|----------|
| `NO_ALPHA` | фон вообще не вырезан | Сначала применить `cutout.py`; новый вызов только если исходник технически непригоден |
| `HARD_EDGE` | бинарная альфа: рваный силуэт «лесенкой» | Сначала перевырезать из исходника; новый вызов только если исходника нет или он непригоден |
| `WHITE_FRINGE` | по краю остался светлый ореол от фона | Сначала перевырезать из исходника; новый вызов только при непригодном исходнике |

Дополнительно смотреть `bbox_fill` (`--json`): если по набору он скачет (0.3 у одного
спрайта против 0.9 у другого), спрайты будут разного видимого размера в игре — прогнать
набор через `python3 tools/cutout.py --dir assets/images/sprites` для нормализации кадра.

## Фаза 4 — Отчёт и вердикт [~1 мин]

Записать `design/asset-review.md`: таблица ассет → вердикт (PASS/FAIL) → критерий →
действие (см. шаблон в `art-director.md`). Общий вердикт: **PASS** или **REGENERATE (N)**.

`--report-only`: остановиться здесь, вернуть отчёт.

## Фаза 5 — Экономная коррекция бракованных [~3 мин]

Только FAIL-ассеты (НЕ весь набор):

- **Локально исправимый PNG** — сначала `cutout.py`, нормализация кадра, исправление
  привязки/масштаба в коде или переклассификация в `derive`/`code`; это не расходует budget.
- **PNG (Codex), дефект исходной генерации** — только для класса `generate` и при свободном
  recovery-slot: один повтор через GPT Images 2.0 с исходным prompt, якорем стиля набора и
  конкретной причиной брака. Обновить SHA-256 и счётчик в `design/asset-manifest.md`, затем
  вырезать фон через `python3 tools/cutout.py <файл> --type sprite`.
- **Fallback** — GPT Images/default разрешён лишь при техническом провале вызова GPT Images
  2.0 (ошибка/нет файла/невалидный PNG), но не по результату vision-оценки.
- **SVG** — править код ассета: палитра/градиенты/обводка к общему стилю набора.

Повторить Фазу 3 только для исправленных ассетов. После одного recovery по `logical_id`
повторный расход запрещён: принять прежний ассет можно только при прохождении критичных
AR5/AR6/AR9/AR10, иначе пометить `BUDGET_BLOCKED` в отчёте и не скрывать причину.

## Критерии выхода

- `design/asset-review.md` с вердиктом и таблицей по каждому ассету
- Контактные листы в `production/asset-review/` (если montage доступен)
- 0 ассетов с вердиктом FAIL без локальной коррекции или одного разрешённого recovery;
  `BUDGET_BLOCKED` всегда содержит причину, расход и требуемое решение
- `python3 tools/cutout.py --dir assets/images/sprites --check` — без FAIL и без
  `HARD_EDGE`/`WHITE_FRINGE` (либо явно принятые остаточные риски в отчёте)
