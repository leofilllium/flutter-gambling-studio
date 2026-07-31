---
name: generate-asset
description: "Генерация ассетов для гемблинг-игр (категории C1-C6): SVG по умолчанию; PNG только по явному запросу. В Codex PNG/image generation выполняется через GPT Images 2.0 с fallback на GPT Images/default Codex image generation."
allowed-tools: Write, Read, Bash, AskUserQuestion
argument-hint: "[тип (symbol/ui/background)] [название] [--png]"
user-invocable: true
---

# `generate-asset` — Студия Ассетов (SVG / PNG)

Выполняет запросы на генерацию ассетов для игры.

## Шаг 0: Выбор формата

**SVG — режим по умолчанию для ручного `/generate-asset`.** Если пользователь не указал формат,
не спрашивай и сразу создавай SVG.

**Исключение:** когда ассеты создаются из `/autocreate` в Codex или команда пришла как
`--from-concept` для полного проекта, PNG/image generation — дефолт. В этом случае сразу
использовать GPT Images 2.0 → GPT Images/default fallback и правила `generate-png-asset`;
SVG не выбирать без явного `--svg`.

PNG/image generation включается только если:
- пользователь передал `--png`;
- пользователь явно просит PNG, raster, bitmap, "image generation", "AI image", "сгенерируй картинкой";
- пользователь прямо говорит, что работает в Codex и надо использовать image generation.
- вызов идёт из `/autocreate` в Codex или `--from-concept` для полного проекта.

Если выбран PNG/image generation:
- в **Codex** использовать встроенную image generation возможность Codex: **GPT Images 2.0** первым; если он не сработал, повторить тот же prompt через **GPT Images / default Codex image generation**;
- не спрашивать API ключ для Google/Pollinations/remove.bg;
- следовать логике скилла `generate-png-asset`;
- внешние провайдеры допустимы только если пользователь явно попросил конкретный legacy-provider или оба Codex image-generation пути недоступны.

Для простых ассетов (`symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`) запрашивать плоский ключевой фон (`flat solid pure magenta #FF00FF background`, либо `pure green #00FF00`, если в палитре есть пурпур/розовый) без теней, градиентов и сцены, затем вырезать его через `python3 tools/cutout.py <файл> --type sprite`. Белый фон не использовать у объектов со светлыми областями. Для `background` и полноэкранных сцен фон не удалять.

---

## SVG режим (режим по умолчанию)

1. Узнайте **Design DNA / палитру** (если не передана в аргументе — прочитать из
   `design/gdd/game-concept.md`; если GDD нет — спросить тему/палитру). Стиль ассетов
   выводится из DNA, **а не из казино/неон по умолчанию**.
2. Выберите тип ассета (вид — из Design DNA, не casino/neon):
   - `symbol` / `sprite`: 64x64 или 96x96 игровой элемент (символ барабана, карта, фишка,
     шар, мина, капсула). Стиль рендера — из DNA: объёмный (градиенты + блики) ИЛИ flat ИЛИ
     outline/lineart. Чёткий на телефоне.
   - `ui`: кнопки / панели / рамки / иконки. Форма — из shape language DNA (скруглённый
     прямоугольник нормален). Эффекты (`<feDropShadow>` / glow) — ТОЛЬКО если они есть в DNA;
     для flat/минимал-стиля их нет вовсе.
   - `background`: полноэкранный (9:16 mobile) фон. Тема, паттерн и **яркость — из DNA**
     (тёплый светлый лес / холодный космос / пастельная конфетная — НЕ «всегда тёмное казино»).
     Не должен отвлекать от игрового поля; обеспечь контраст к HUD.

> **UNIFIED SVG STYLE CONSTRAINTS (ОБЯЗАТЕЛЬНО)**:
> Все SVG-ассеты должны быть ИДЕАЛЬНО консистентны между собой.
> - **Style from DNA**: общий стиль (flat / volume / lineart), палитра и яркость берутся из
>   Design DNA — но внутри одного набора он ЕДИНЫЙ.
> - **Unified `<defs>`**: Используйте единую структуру градиентов и эффектов во всех файлах.
> - **Lighting**: Зафиксируйте угол освещения (например, 45 градусов сверху-слева) и строго его придерживайтесь.
> - **Shadows & Strokes**: Используйте одинаковую толщину контуров (stroke-width) и ИДЕНТИЧНЫЕ параметры теней (`<feDropShadow dx="0" dy="4" stdDeviation="4">`) во всех файлах.
> - **Mix & Match**: ЗАПРЕЩАЕТСЯ смешивать элементы flat-дизайна (без объёма) с фотореалистичными (сильно шейдированными) в рамках одного сета. Либо всё flat, либо всё volume.
> - **Иконки**: один стиль (всё outline ИЛИ всё filled) и одна толщина обводки во всём наборе.

3. Сохраните в `assets/images/sprites/` или `assets/images/ui/`. Обязательно добавьте путь в `pubspec.yaml` если папка новая.

> Не забывайте `<svg viewBox="0 0 W H" xmlns="http://www.w3.org/2000/svg">`.
