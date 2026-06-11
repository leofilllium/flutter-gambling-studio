# Codex Agent Registry

В Codex эти роли не существуют как отдельная встроенная платформа, поэтому репозиторий задаёт их как operational personas. Если задача требует специализированного поведения, Codex должен:

1. Открыть соответствующий файл из `.claude/agents/`.
2. Принять описанную persona и рабочий протокол.
3. При необходимости делегировать часть работы sub-agent'у Codex с явным ownership.

| Роль | Файл | Когда применять |
|------|------|-----------------|
| `creative-director` | `.claude/agents/creative-director.md` | Концепт, pillars, визуальное направление |
| `technical-director` | `.claude/agents/technical-director.md` | ADR, архитектурные конфликты, выбор паттернов |
| `game-mathematician` | `.claude/agents/game-mathematician.md` | RTP, weights, difficulty, scoring |
| `game-designer` | `.claude/agents/game-designer.md` | GDD, правила механики, progression |
| `mechanics-programmer` | `.claude/agents/mechanics-programmer.md` | Flame game logic, RNG, physics, spawning |
| `meta-systems-programmer` | `.claude/agents/meta-systems-programmer.md` | SaveService, Economy, Progression, Achievements, Analytics/Ads/IAP abstractions (Agent E в /autocreate) |
| `art-director` | `.claude/agents/art-director.md` | Визуальная целостность набора ассетов: vision-ревью AR1–AR10, перегенерация бракованных (/asset-review, Фаза 3.6) |
| `juice-artist` | `.claude/agents/juice-artist.md` | VFX, particles, win feel, motion + Gameplay Feel Pass (Фаза 6.5) |
| `lead-programmer` | `.claude/agents/lead-programmer.md` | Архитектура, code review, refactoring control |
| `performance-analyst` | `.claude/agents/performance-analyst.md` | FPS, memory, batching, hot-path analysis |
| `ui-programmer` | `.claude/agents/ui-programmer.md` | Flutter screens, HUD, anti-slop UI |
| `sound-designer` | `.claude/agents/sound-designer.md` | SFX/BGM, flame_audio, pitch scaling |
| `qa-tester` | `.claude/agents/qa-tester.md` | Тест-планы, edge cases, validation |
| `release-manager` | `.claude/agents/release-manager.md` | Release gate, финальный checklist |

## Рекомендации для Codex

- Для короткой задачи достаточно локально принять роль без делегации.
- Многоролевые фазы (`/autocreate` Фаза 4, `/team-dev`) — **последовательные persona-проходы**:
  прочитать файл роли + `lib/contracts.md`, выполнить только СВОЮ зону файлов, записать
  3–5-строчное резюме прохода в `production/session-state/active.md`, перейти к следующей роли.
  Порядок Фазы 4: A (mechanics) → E (meta-systems) → D (sound) → B (ui) → C (juice).
- Все ответы пользователю и агентам остаются на русском языке.
- Доменные ограничения из `.claude/rules/` приоритетнее persona-инструкций.
- Эталон качества для всех ролей — `.claude/docs/quality-bar.md`.
