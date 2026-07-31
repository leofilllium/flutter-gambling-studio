---
name: autocreate-implement
description: "Сессия 2 конвейера /autocreate (Фазы 4 → 10): имплементация. 5 агентов последовательно пишут код + мета-системы, wiring контента, интеграция, build до 0 errors, feel-pass, тесты, UI-аудит (compliance), баланс по кривой, crash-prevention. Тяжёлые фазы ДЕЛЕГИРУЮТСЯ свежим суб-агентам без full-history fork, чтобы оркестратор не истощил контекст и TPM. В конце spawn Сессии 3 (autocreate-finalize). Запускается автоматически Сессией 1 через Agent tool, либо вручную в новой conversation."
argument-hint: "[--resume]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, Skill
---

# AutoCreate Implement — Сессия 2 (Имплементация)

**Назначение**: превратить pre-production Сессии 1 (концепт + ассеты + аудио + данные) в
полностью рабочий, чистый и протестированный код игры — и передать его Сессии 3 на runtime-
верификацию. Это **средняя** из трёх context-сессий `/autocreate`.

```
Сессия 1 (autocreate)  →[handoff-1]→  Сессия 2 (ЭТОТ skill)  →[autocreate-handoff.md]→  Сессия 3
   концепт/данные              Фазы 4–10: код/тесты/аудит/баланс         finalize/release-ready
```

---

## 🚨 MANDATORY CONTRACT

1. ✅ Читает `production/session-state/autocreate-handoff-1.md` **первым действием**
2. ✅ Валидирует артефакты Сессии 1 (pubspec, структура, `assets/data/*.json`, `assets/audio/*`)
3. ✅ Читает `design/asset-format.md` для определения формата ассетов (PNG vs SVG) и передаёт
   агентам (Agent B: `Image.asset()` для PNG, `SvgPicture` для SVG; Agent A: расширения файлов)
4. ✅ Выполняет **Фазы 4 → 10** как описано в `.claude/skills/autocreate/SKILL.md`
   (эти фазы — канонические спецификации; этот skill — драйвер их исполнения)
5. ✅ **Делегирует тяжёлые фазы суб-агентам** (см. карту ниже) — оркестратор НЕ читает весь
   `lib/` сам, а оперирует выводами команд (`dart analyze`/`flutter test`) и резюме агентов
6. ✅ В конце (Фаза 10.7) пишет `autocreate-handoff.md` и **spawn Сессии 3** через Agent tool

**Запрещено:**
- ❌ Переписывать концепт/ассеты/аудио/данные Сессии 1 (можно лишь дополнять `GameConfig`
  значениями из `assets/data/*.json`)
- ❌ Менять баланс/контент-данные кроме как через game-mathematician в Фазе 9
- ❌ Вызывать `flutter build apk/appbundle/web`, `adb`, `emulator` — это Сессия 3 / release-eng
- ❌ Отчитываться "готово" при `dart analyze` с errors или красном `flutter test`
- ❌ Завершиться без spawn Сессии 3 (Фаза 10.7)

---

## Стратегия защиты контекста (почему это отдельная сессия)

Полная игра = много кода (5 агентов × десятки файлов + тесты + аудит). Если оркестратор сам
прочитает всё это — контекст кончится до конца. Поэтому **оркестратор Сессии 2 в основном
координирует и запускает команды, а файловую работу делают суб-агенты**:

| Фаза | Что делает оркестратор | Кому делегирует (Agent tool, чистый контекст + handoff) |
|------|------------------------|------------------------------------------------|
| 4. Implementation | формирует контракт `lib/contracts.md`, запускает 5 агентов строго по одному | **A** mechanics → **E** meta-systems → **D** sound → **B** ui → **C** juice |
| 4.5. Content wiring | — | склейка данных↔код: **B** (level/mode select) + **E** (progression/economy) |
| 5. Integration | — | **lead-programmer**: читает все файлы, чинит cross-agent несоответствия, расставляет вызовы сервисов/аудио/VFX |
| 6. Build & Fix | запускает `dart analyze`, собирает список ошибок | если ошибок много — **mechanics-programmer**/**ui-programmer** чинит свои; оркестратор только повторяет analyze |
| 6.5. Feel Pass | — | **juice-artist** (живой геймплей, наполнение хуков) |
| 7. Tests | запускает `flutter test`, собирает падения | **qa-tester** пишет/чинит тесты |
| 8. UI Audit | — | `/ui-audit` (skill уже использует агентов) ИЛИ **ui-programmer** по 10 категориям |
| 9. Balance | запускает sim-скрипт | **game-mathematician** при выходе за окно (правит JSON) |
| 10. Crash Prevention | финальный `dart analyze`+`flutter test` | точечные фиксы — соответствующему агенту |

> **Правило оркестратора:** не открывай файлы `lib/` массово на чтение. Читай только: вывод
> `dart analyze`/`flutter test`, `design/structure.md`, `lib/contracts.md`, и КРАТКИЕ резюме,
> которые возвращают суб-агенты. Точечный Read 1–2 файлов допустим для диагностики. Это держит
> контекст Сессии 2 в бюджете даже для большой игры.

> **🤖 CODEX / среда без Agent tool:** делегирование из таблицы выше выполняется
> ПОСЛЕДОВАТЕЛЬНЫМИ persona-проходами (см. `AGENTS.md` → «Execution Model»):
> перед каждым проходом прочитать `.claude/agents/<роль>.md` + `lib/contracts.md`, выполнить
> зону ответственности этой роли, записать 3–5-строчное резюме прохода в
> `production/session-state/active.md`, и НЕ держать чужие файлы в контексте.
> Порядок Фазы 4: **A → E → D → B → C** (логика и сервисы раньше UI, чтобы B видел реальные
> сигнатуры). Правило «не читай lib/ массово» в Codex ещё важнее — контекст один на всё.

> **TPM-гейт:** одновременно активен максимум один subagent. Каждый получает только
> `lib/contracts.md`, нужные design/data-файлы, свою роль и краткий handoff. Никогда не
> передавать ему полный transcript родительской сессии.

---

## Фаза 0 — Preflight & Handoff Read [~30 сек]

```bash
test -f production/session-state/autocreate-handoff-1.md || {
  echo "❌ Нет handoff-1. Сессия 1 /autocreate не завершилась?"; exit 1; }
test -f pubspec.yaml || { echo "❌ Нет pubspec.yaml — проект не инициализирован"; exit 1; }
test -f design/structure.md || { echo "❌ Нет design/structure.md"; exit 1; }
ls assets/data/*.json   >/dev/null 2>&1 || echo "⚠️ нет assets/data/*.json — контент-данные отсутствуют"
ls assets/audio/sfx/*.wav >/dev/null 2>&1 || echo "⚠️ нет аудио — перезапусти tools/synth_sfx.py"

# Определение формата ассетов (PNG vs SVG). Нельзя молча откатываться в SVG:
# Session 1 обязана записать design/asset-format.md, а при сбое формат выводится
# из реально существующих ассетов.
ASSET_FORMAT=""
if [ -f design/asset-format.md ]; then
  ASSET_FORMAT=$(grep '^format:' design/asset-format.md | awk '{print $2}' | tr -d '[:space:]')
elif ls assets/images/sprites/*.png >/dev/null 2>&1 || ls assets/images/backgrounds/*.png >/dev/null 2>&1; then
  ASSET_FORMAT="png"
  echo "⚠️ design/asset-format.md отсутствует; inferred format=png from existing assets"
elif ls assets/images/sprites/*.svg >/dev/null 2>&1 || ls assets/images/backgrounds/*.svg >/dev/null 2>&1; then
  ASSET_FORMAT="svg"
  echo "⚠️ design/asset-format.md отсутствует; inferred format=svg from existing assets"
else
  echo "❌ Нет design/asset-format.md и не найдены ассеты PNG/SVG — Сессия 1 неполная"
  exit 1
fi
echo "🎨 Asset format: ${ASSET_FORMAT}"

# Валидация ассетов по формату
if [ "$ASSET_FORMAT" = "png" ]; then
  ls assets/images/sprites/*.png >/dev/null 2>&1 || echo "⚠️ нет PNG спрайтов — ожидались для Codex-режима"
  ls assets/images/backgrounds/*.png >/dev/null 2>&1 || echo "⚠️ нет PNG фонов"
  if find assets/images -name "*.svg" -print -quit | grep -q .; then
    echo "⚠️ PNG-режим, но найдены SVG. Не использовать их в коде; проверить, что это не результат ошибочной генерации."
  fi
else
  ls assets/images/sprites/*.svg >/dev/null 2>&1 || echo "⚠️ нет SVG спрайтов"
  ls assets/images/backgrounds/*.svg >/dev/null 2>&1 || echo "⚠️ нет SVG фонов"
fi
echo "✅ Preflight OK — Сессия 1 артефакты на месте"
```

Прочитать `autocreate-handoff-1.md`, `design/structure.md`, `design/art-direction.md`,
`design/asset-format.md` (формат ассетов: PNG или SVG — влияет на код Agent B),
`design/gdd/game-concept.md` (особенно Production Plan, Screen Map, Design DNA, ValueNotifier
контракты). Не читать `lib/` массово.

> **КРИТИЧЕСКИ для Asset Format:** Если `design/asset-format.md` содержит `format: png`:
> - Agent B использует `Image.asset('assets/images/sprites/name.png')`, НЕ `SvgPicture`
> - `flame_svg` НЕ используется в коде (может оставаться в pubspec как fallback)
> - Константы в `assets_constants` имеют расширение `.png`
> - Если `format: svg` — всё как раньше: `SvgPicture.asset()` + `flame_svg`

### `--resume` (после сбоя Сессии 2)
Определить, с какой фазы продолжить, по артефактам:
- нет `lib/main.dart`/мало файлов в `lib/` → начать с Фазы 4
- код есть, но `dart analyze` с errors → Фаза 6
- analyze чист, тестов нет/красные → Фаза 7
- тесты зелёные, аудит не проводился → Фаза 8
Не переделывать уже сделанное.

---

## Фазы 4 → 10 — исполнение по канону

Выполнить **Фазы 4, 4.5, 5, 6, 6.5, 7, 8, 9, 10** ровно как описано в
`.claude/skills/autocreate/SKILL.md` (раздел «Фазы 4–10 выполняются в Сессии 2»), применяя
карту делегирования выше. Критерии выхода каждой фазы — из таблицы Quality Gates автокрейта:

| Фаза | Критерий выхода | Итераций |
|------|----------------|----------|
| 4. Implementation | 5 агентов завершены (A/B/C/D/E) | 1 (Фаза 6 чинит) |
| 4.5. Content wiring | Game принимает (mode,levelId); Level/Mode Select ↔ data | 2 |
| 5. Integration | 18 связей (вкл. мета-сервисы) | 3 |
| 6. Build | `dart analyze lib/` 0 errors | 10 |
| 6.5. Feel Pass | поле живое (F1–F5), analyze+test чисты | 2 |
| 7. Tests | `flutter test` все зелёные (вкл. test/services/) | 5 |
| 8. UI Audit | 100+ проверок (вкл. compliance/content, кат. J) | 3 |
| 9. Balance | RTP/difficulty по ВСЕЙ кривой в норме | 3 |
| 10. Crash Prevention | 20/20 + (gambling) age-gate/disclaimer; analyze+test clean | 3 |

**АБСОЛЮТНЫЙ МИНИМУМ перед Фазой 10.7:** `dart analyze lib/` 0 errors, `flutter test` зелёные,
15+ экранов, навигация работает, основная механика + контент (N уровней/режимы) + мета-системы
на месте, (gambling) compliance-флаги расставлены.

---

## Фаза 10.7 — Handoff & Spawn Session 3 [~1 мин]

Выполнить **Фазу 10.7 из `.claude/skills/autocreate/SKILL.md`**: записать
`production/session-state/autocreate-handoff.md` (полный контекст для финализации) и
**spawn Сессии 3** через Agent tool (промпт — как в Фазе 10.7.2 автокрейта, он указывает
subagent-у выполнить `.claude/skills/autocreate-finalize/SKILL.md`: runtime+soak, session-state,
release-eng PREP без сборки AAB/APK, финальный отчёт).

После возврата subagent-а Сессии 3 — вернуть его финальный отчёт наверх (в Сессию 1 / пользователю).
Если Сессия 3 упала — сообщить причину и команду ручного перезапуска: `/autocreate-finalize`.

---

## Восстановление после сбоев

- **Сессия 2 упала** → пользователь запускает `/autocreate-implement --resume` в новой
  conversation; skill определяет фазу по артефактам и продолжает.
- **Сессия 1 не записала handoff-1** → Preflight падает с понятным сообщением; запустить
  `/autocreate` заново (или вручную дописать `assets/data/*.json` и handoff-1).
