# Gemini CLI / Antigravity Guide for Flutter Gambling Studio

> Управляйте гемблинг-студией через агента Gemini / Antigravity.
> Студия делает ТОЛЬКО гемблинг-игры: шесть категорий C1–C6, 32 архетипа A–AF.
> Этот файл адаптирует команды студии для запуска в `gemini` CLI.
>
> Для Claude: `CLAUDE.md` и `.claude/`
> Для Codex: `AGENTS.md` и `.codex/`
> Для Cursor: `.cursorrules`

## Установка и интеграция (Gemini CLI)

Для того, чтобы навыки (skills) и агенты отображались в Gemini / Antigravity:
```bash
./tools/setup-gemini-cli.sh link
```
Это добавит проектный плагин студии в директорию `~/.gemini/antigravity/plugins/flutter-gambling-studio/skills`. 

## Использование

Ваш бот (например, Antigravity) обучен запускать команды как "ручные ранбуки" или полноценные навыки.
Просто напишите в чат нужную команду (например, `/brainstorm`) или используйте упоминание агента.

### Доступные команды:

| Команда | Описание |
|---------|----------|
| `/brainstorm` | Интерактивный генератор концепта |
| `/auto-idea` | Автономный концепт (32 архетипа A–AF по 6 категориям + Variety Dimensions + Layout Archetype) |
| `/autocreate` | Полный цикл создания игры |
| `/team-dev` | Оркестрация команды разработчиков |
| `/ui-audit` | Выявление проблем anti-slop дизайна |
| `/emulator-test` | Тестирование в реальном Android эмуляторе через ADB (default). Скриншоты — `flutter screenshot` с fallback на `adb screencap` и валидацией PNG. Флаг `--no-impeller` если кадры невалидны. |
| `/code-review` | Ревью архитектуры Flame и Flutter |
| `/balance-check`| Верификация матмодели M1–M6 через `tools/simulate_math.py` |

Полный список см. в файле [CLAUDE.md](CLAUDE.md).

## Правила кодирования

При написании кода бот Gemini будет использовать стандарты, описанные в:
- `.claude/rules/game-code.md`
- `.claude/rules/engine-code.md`
- `.claude/rules/ui-code.md`

Всегда обращайте внимание на требования к `Random.secure()` и "stateless outcomes", а также избегайте магических чисел вне `game_config.dart`.

Обязательны к прочтению перед работой:
- `.claude/docs/gambling-categories.md` — шесть категорий и 32 архетипа
- `.claude/docs/math-models.md` — модели M1–M6 и пороги верификации
- `.claude/rules/responsible-gaming.md` — compliance-слой (release-блокер)
