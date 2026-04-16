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
| `juice-artist` | `.claude/agents/juice-artist.md` | VFX, particles, win feel, motion |
| `lead-programmer` | `.claude/agents/lead-programmer.md` | Архитектура, code review, refactoring control |
| `performance-analyst` | `.claude/agents/performance-analyst.md` | FPS, memory, batching, hot-path analysis |
| `ui-programmer` | `.claude/agents/ui-programmer.md` | Flutter screens, HUD, anti-slop UI |
| `sound-designer` | `.claude/agents/sound-designer.md` | SFX/BGM, flame_audio, pitch scaling |
| `qa-tester` | `.claude/agents/qa-tester.md` | Тест-планы, edge cases, validation |
| `release-manager` | `.claude/agents/release-manager.md` | Release gate, финальный checklist |

## Рекомендации для Codex

- Для короткой задачи достаточно локально принять роль без делегации.
- Для сложной многошаговой задачи используйте sub-agents только с разделённой зоной ответственности.
- Все ответы пользователю и агентам остаются на русском языке.
- Доменные ограничения из `.claude/rules/` приоритетнее persona-инструкций.
