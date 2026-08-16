# Gambling Game Concept: [Name]

## 0. Classification (MANDATORY — without it `/gate-check concept` returns FAIL)

- **Category**: [C1 Social Casino | C2 Originals | C3 Spin-to-Progress | C4 Gacha | C5 Roguelike | C6 Physics]
- **Archetype**: [A–AF | UNIQUE] — [name]
- **Mathematical model**: [M1 Paytable RTP | M2 Instant-Win | M3 Economy | M4 Gacha | M5 Run Win-Rate | M6 Physics RTP]
- **Target metric**: [e.g. "RTP 96.0% ±1%" / "hard pity 70, SSR 1.2%" / "run win-rate 32%"]
- **Model config**: `design/balance/[file].json`
- **Compliance profile**: [full (age gate + disclaimer + 18+) | relaxed C5 — with justification]
- **Game language**: English (default) | [another language, only if the user explicitly asked]
- **Product target**: mobile-first Android/iOS and responsive full-viewport Web

## 1. Elevator pitch
What is the main emotion this game delivers? Where is its hook?

## 2. Mathematical profile (filled in by game-mathematician)

Filled in according to the model from §0 — see `.claude/docs/math-models.md`:

- **M1/M2/M6**: base RTP, hit rate, volatility, maximum multiplier
- **M3**: energy regeneration, source/sink, progress pace, the spin event table
- **M4**: base rates by rarity, soft/hard pity, E[pulls], duplicate conversion
- **M5**: round thresholds, run win-rate, run economy, seed determinism

## 3. Core mechanic (filled in by game-designer)
- **Round structure**: [reels/lines | cells and mines | multiplier curve | banner and pull | board | peg field]
- **Bet / cost of entry**: [range, step, what is spent]
- **Special elements**: [Wild, Scatter, Bonus | cash-out | pity | jokers | special buckets]
- **Bonus round**: [description of the feature]
- **Stop condition**: [end of animation | the player's cash-out | bust | end of the run]

## 4. Juiciness
What is the main visual event? (An explosion? Screen shake? A golden waterfall?)
What does the player see on a "big win"?

## 5. Full asset list
- `sprite_...`
- `ui_...`
- `background_...`

## 6. Design DNA (visual identity — NOT default neon)
> Every decision is justified by THIS game's theme. See `.claude/rules/anti-slop-design.md`.
- **Emotional core**: [what the player feels]
- **Visual world**: [the world: underwater / space / Egypt / cosy / …]
- **Palette (5 colours with reasons)**: background / surface / primary / win / loss
- **Brightness**: [light / dark / twilight — driven by the theme]
- **Typography (via google_fonts)**: display + body — [specific fonts + why]
- **Shape language**: [the shape of buttons/panels — why]
- **Motion character**: [feedback / win celebration / transitions]
- **Depth strategy**: [glass / card / paper / flat — whatever fits]

## 7. Layout & composition direction
> See `.claude/docs/mobile-first-contract.md` and `.claude/docs/layout-archetypes.md` (L1–L6).
- **Layout archetype**: [L1–L6] — [why it fits]
- How it applies to the main menu / game screen + HUD / overlays / transitions.
- **Phone-baseline proof**: [360×640 / 360×800 / 390×844 / 430×932; thumb reach; no core scroll]
- **Expanded proof**: [844×390 / 768×1024 / 1024×768 / 1440×900; full-viewport reflow strategy]
- **Non-targets**: no fixed-width phone wrapper, fake device frame, or pointer-only interaction.

## 8. Screen map (at least 12+, composed per the chosen layout archetype)
- Splash, main menu, game + HUD, paytable/rules, settings, help, win overlays (3 tiers),
  insufficient/out of chips, daily bonus, leaderboard, profile, loading.
- **The compliance layer** (`.claude/rules/responsible-gaming.md`): age gate, the disclaimer on
  the splash and in the rules, responsible play in settings, odds disclosure (mandatory for C4
  and for paid spins in C3).
