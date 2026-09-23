# Gambling Game Concept: [Name]

## 0. Classification (MANDATORY — without it `/gate-check concept` returns FAIL)

- **Category**: [C1 Social Casino | C2 Originals | C3 Spin-to-Progress | C4 Gacha | C5 Roguelike | C6 Physics]
- **Archetype**: [A–AF | UNIQUE] — [name]
- **Mathematical model**: [M1 Paytable RTP | M2 Instant-Win | M3 Economy | M4 Gacha | M5 Run Win-Rate | M6 Physics RTP]
- **Target metric**: [e.g. "RTP 96.0% ±1%" / "hard pity 70, SSR 1.2%" / "run win-rate 32%"]
- **Model config**: `design/balance/[file].json`
- **Compliance profile**: [full (disclaimer) | relaxed C5 — with justification]
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
- **Board topology**: [classic unspecified slot = 3 reels × 3 visible rows; document explicit variants]
- **Round structure**: [reels/lines | cells and mines | multiplier curve | banner and pull | board | peg field]
- **Bet / cost of entry**: [range, step, what is spent]
- **Special elements**: [Wild, Scatter, Bonus | cash-out | pity | jokers | special buckets]
- **Bonus round**: [description of the feature]
- **Stop condition**: [end of animation | the player's cash-out | bust | end of the run]

## 4. Juiciness
What state change is the decisive feedback moment, and how does the player read it? Record the
feedback character for routine, notable, and major outcomes, including where motion/effects stay
absent. Do not assume an explosion, shake, particle shower, or full-screen takeover.

## 5. Full asset list
- `sprite_...`
- `ui_...`
- `background_...`

## 6. Asset/World Design DNA, Game UI Read, and Design Signature
> Every decision follows from this game's player, mechanic, state needs, world, and reference.
> See `.claude/rules/anti-slop-design.md`.
- **Asset/World Design DNA**: [fiction, subject cast, silhouette language, materials, lighting,
  illustration palette, and finish; no fixed color/font count]
- **Player/session and core decision**: [who, posture, duration, repeated choice]
- **Emotional arc and information pressure**: [setup -> anticipation -> result; now vs later]
- **Visual world and memorable interface idea**: [specific, mechanic-linked]
- **Field framing / controls / HUD / navigation**: [choice + reason for each]
- **Geometry / surface / type / color-value**: [semantic roles; no fixed token count]
- **Motion / depth / sound-haptics**: [what they communicate, and where they stay absent]

## 7. State composition and layout direction
> See `.claude/docs/mobile-first-contract.md` and `.claude/docs/layout-archetypes.md`.
- **State map**: [setup / commitment / anticipation / result / recovery attention order]
- **Per-screen recipes**: [main menu M/O/R; live states F/C/H/O/R; secondary screens]
- **Store lead and menu role**: [lead_kind: character | object | mechanic;
  menu_role: dominant | supporting | absent, with reason from the M recipe]
- **Primary field alignment**: [centered, or documented mechanic/recipe reason for an offset]
- **Phone-baseline proof**: [360×640 / 360×800 / 390×844 / 430×932; thumb reach; no core scroll]
- **Expanded proof**: [844×390 / 768×1024 / 1024×768 / 1440×900; full-viewport reflow strategy]
- **Similarity Check**: [neighbors, intentional repeats, at least four material differences,
  remaining risk/correction; skip anti-repeat drift for an exact mapped reference]
- **Non-targets**: no fixed-width phone wrapper, fake device frame, or pointer-only interaction.

## 8. Screen map (at least 12+, each with a job and appropriate recipe)
- Splash, main menu, game + HUD, paytable/rules, settings, help, win overlays (3 tiers),
  insufficient/out of chips, daily bonus, leaderboard, profile, loading.
- **The compliance layer** (`.claude/rules/responsible-gaming.md`): age gate, the disclaimer on
  the splash and in the rules, responsible play in settings, odds disclosure (mandatory for C4
  and for paid spins in C3).

## 9. Visual references and store direction
> Follow `.claude/docs/visual-context.md` and `.claude/docs/game-concept-examples.md`.
- **Lead kind / identity**: [character | object | mechanic; exact subject and runtime role]
- **Previews inspected**: [every mapped path and its role; exact traits, 2D/2.5D finish, and any deviations]
- **Reference ledger**: [character, every symbol, board, background, UI materials and composition;
  source path(s) for each; direct reuse versus high-fidelity image edit]
- **Character tone**: [if relevant; Joker = mischievous/slightly vicious, playful, not horror or an elegant host]
- **Multiplier coins**: [prefer x5/x10 when appropriate; exact config/paytable source and meaning, or omit]
- **Panorama map**: [anchors, gameplay location/span, critical regions and safe seam plan]
- **Feature graphic**: [independent horizontal composition; free or justified left-heavy arrangement; text-free, with one phone on the right holding a real capture]
- **Runtime continuity**: [asset identities, board topology, backgrounds and state to preserve]
