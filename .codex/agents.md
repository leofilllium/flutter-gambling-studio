# Codex Agent Registry

Codex has no built-in platform for these roles, so the repository defines them as operational
personas. When a task needs specialised behaviour, Codex should:

1. Open the matching file in `.claude/agents/`.
2. Adopt the persona and working protocol it describes.
3. Where useful, delegate part of the work to a Codex sub-agent with explicit ownership.

| Role | File | When to use it |
|------|------|----------------|
| `creative-director` | `.claude/agents/creative-director.md` | Concept, pillars, visual direction |
| `technical-director` | `.claude/agents/technical-director.md` | ADRs, architectural conflicts, choosing patterns |
| `game-mathematician` | `.claude/agents/game-mathematician.md` | RTP, weights, difficulty, scoring |
| `game-designer` | `.claude/agents/game-designer.md` | GDD, mechanic rules, progression |
| `mechanics-programmer` | `.claude/agents/mechanics-programmer.md` | Flame game logic, RNG, physics, spawning |
| `meta-systems-programmer` | `.claude/agents/meta-systems-programmer.md` | SaveService, Economy, Progression, Achievements, Analytics/Ads/IAP abstractions (Agent E in /autocreate) |
| `art-director` | `.claude/agents/art-director.md` | Visual consistency of the asset set: AR1–AR10 vision review, regeneration of rejects (/asset-review, Phase 3.6) |
| `juice-artist` | `.claude/agents/juice-artist.md` | VFX, particles, win feel, motion + Gameplay Feel Pass (Phase 6.5) |
| `lead-programmer` | `.claude/agents/lead-programmer.md` | Architecture, code review, refactoring control |
| `performance-analyst` | `.claude/agents/performance-analyst.md` | FPS, memory, batching, hot-path analysis |
| `ui-programmer` | `.claude/agents/ui-programmer.md` | Flutter screens, HUD, anti-slop UI |
| `sound-designer` | `.claude/agents/sound-designer.md` | SFX/BGM, flame_audio, pitch scaling |
| `qa-tester` | `.claude/agents/qa-tester.md` | Test plans, edge cases, validation |
| `release-manager` | `.claude/agents/release-manager.md` | Release gate, final checklist |

## Recommendations for Codex

- For a short task it is enough to adopt the role locally, without delegating.
- Multi-role phases (`/autocreate` Phase 4, `/team-dev`) are **sequential persona passes**:
  read the role file plus `lib/contracts.md`, work only on YOUR file zone, write a
  3–5 line summary of the pass into `production/session-state/active.md`, then move on to
  the next role. The Phase 4 order is: A (mechanics) → E (meta-systems) → D (sound) →
  B (ui) → C (juice).
- All responses, to the user and between agents, stay in English.
- Domain constraints from `.claude/rules/` take priority over persona instructions.
- The quality benchmark for every role is `.claude/docs/quality-bar.md`.
