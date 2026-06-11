---
name: playtest
description: "Глубокая ИГРОВАЯ верификация (не просто 'экраны открываются'): реально играет в игру через headless Chrome CDP — N игровых действий, проверка что счёт/баланс МЕНЯЮТСЯ, win-путь достижим, game-over обрабатывается, прогрессия работает, поле анимировано (vision-сравнение кадров), нет исключений и утечек. Выдаёт PLAYTEST REPORT с verdict и приоритизированными фиксами. Вызывается из /autocreate-finalize (Фаза 10.6) или вручную."
argument-hint: "[--rounds N] [--no-fix]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# Playtest — «В это вообще играбельно?»

`/emulator-test` проверяет, что экраны открываются и не падают. `/playtest` проверяет,
что **ИГРА ИГРАЕТСЯ**: действия дают результат, числа меняются, победы празднуются,
поражения обрабатываются, поле живое. Это последний фильтр между «компилируется» и
«профессиональная игра» (см. `.claude/docs/quality-bar.md`).

**Предусловия**: `dart analyze lib/` 0 errors; `node` ≥21 и Chrome/Chromium доступны
(иначе — честный SKIPPED, как в `/emulator-test`).

---

## Фаза 1 — Запуск игры (headless web) [~2 мин]

Тот же путь, что в `/autocreate-finalize` Фаза 10.5 (web-server + ожидание URL с ранним
выходом при ошибке сборки):

```bash
mkdir -p .claude/runtime-logs
WEB_PORT=8099
nohup flutter run -d web-server --web-port "$WEB_PORT" --web-hostname 127.0.0.1 \
  > .claude/runtime-logs/flutter-run.log 2>&1 &
echo $! > .claude/runtime-logs/flutter.pid
WEB_URL=""
for i in $(seq 1 120); do
  WEB_URL=$(grep -oE "http://127\.0\.0\.1:[0-9]+" .claude/runtime-logs/flutter-run.log 2>/dev/null | head -1)
  [ -n "$WEB_URL" ] && break
  grep -qE "Failed to compile|Target dart2js failed|Compilation failed|^Error: " \
    .claude/runtime-logs/flutter-run.log 2>/dev/null && break
  sleep 2
done
TS=$(date +%Y%m%d-%H%M%S); PT_DIR="production/playtest/$TS"; mkdir -p "$PT_DIR"
```

## Фаза 2 — Игровая сессия (CDP) [~4 мин]

Два прохода `tools/web_verify.mjs`:

```bash
# 2.1 Тур по экранам + базовые скрины (manifest.json: steps/semanticLabels/consoleErrors)
timeout 220 node tools/web_verify.mjs --url "$WEB_URL" --out "$PT_DIR" --budget 180 \
  2>&1 | tee "$PT_DIR/web_verify.log"

# 2.2 Игровая нагрузка: N повторов основного действия (default 60; --rounds задаёт)
timeout 240 node tools/web_verify.mjs --url "$WEB_URL" --out "$PT_DIR" --soak "${ROUNDS:-60}" \
  2>&1 | tee -a "$PT_DIR/web_verify.log"
```

После — остановить сервер: `kill "$(cat .claude/runtime-logs/flutter.pid)" 2>/dev/null`.

## Фаза 3 — Игровые проверки (P1–P10)

Источники: скриншоты (`Read` vision), `manifest.json` (`semanticLabels`, `consoleErrors`,
`soak.heapUsed*`, `soak.suspectLeak`), `.claude/runtime-logs/flutter-run.log`.

| # | Проверка | Как верифицировать | Severity при FAIL |
|---|----------|--------------------|-------------------|
| P1 | **Действие даёт результат** | Сравнить кадры до/после действия (vision): поле изменилось, не идентичные пиксели | CRITICAL |
| P2 | **Числа меняются** | Счёт/баланс на скриншоте ПОСЛЕ серии действий ≠ значению ДО (vision-чтение цифр HUD) | CRITICAL |
| P3 | **Win-путь достижим** | За N раундов хотя бы раз виден win-фидбек (оверлей/частицы/рост числа) | HIGH |
| P4 | **Проигрыш обрабатывается** | Game-over / insufficient-funds появляется и из него есть выход (рестарт/меню) | HIGH |
| P5 | **Поле живое** | Два кадра idle-состояния с интервалом различаются (idle-анимация) — vision | HIGH |
| P6 | **Прогрессия работает** | Level/Mode Select открывается, выбор уровня запускает игру с иным конфигом | HIGH |
| P7 | **Пауза/возврат** | Выход в меню и обратно не ломает состояние (баланс сохранён, нет красного экрана) | HIGH |
| P8 | **0 исключений за сессию** | `consoleErrors` пуст; нет EXCEPTION CAUGHT в flutter-run.log | CRITICAL |
| P9 | **Нет утечки** | `soak.suspectLeak == false`, heap не растёт монотонно | MEDIUM |
| P10 | **Стартовый опыт** | От запуска до первого игрового действия ≤ 3 тапов (splash→menu→play) | MEDIUM |

> Для P1/P2/P5: vision-сравнение — главный инструмент. Снимки в `$PT_DIR` нумерованы по
> шагам тура; soak добавляет кадры до/после серии. Если кадров для сравнения не хватает —
> прогнать 2.2 повторно с меньшим N и снять скрин до/после вручную через web_verify.

## Фаза 4 — Отчёт и автофиксы [~3 мин]

Записать `$PT_DIR/PLAYTEST-REPORT.md`:

```markdown
# Playtest Report — [игра], [дата]
## Verdict: PLAYABLE / PLAYABLE-WITH-ISSUES / NOT-PLAYABLE / SKIPPED
| # | Проверка | Результат | Доказательство |
|---|----------|-----------|----------------|
| P1 | Действие даёт результат | PASS | 04→05.png: поле изменилось |
...
## Приоритизированные фиксы
1. [CRITICAL] ...
```

- **NOT-PLAYABLE** = любой CRITICAL (P1/P2/P8). Без `--no-fix` — автофикс-цикл до 2
  итераций по таблице разрешённых фиксов из `/autocreate-finalize` 10.5.3 (только
  точечные правки: wiring ValueNotifier, недобавленный компонент в World, route,
  asset path; НЕ баланс, НЕ конфиги, НЕ переписывание экранов). После фикса —
  повторить Фазы 1–3.
- **PLAYABLE-WITH-ISSUES** = HIGH остались — перечислить в отчёте, не чинить молча.

## Критерии выхода

- `$PT_DIR/PLAYTEST-REPORT.md` с verdict и таблицей P1–P10
- 0 CRITICAL (или 2 итерации фиксов исчерпаны — verdict честно NOT-PLAYABLE)
- Сервер и headless Chrome остановлены (нет осиротевших процессов)
