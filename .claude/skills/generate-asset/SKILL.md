---
name: generate-asset
description: "Generates assets for gambling games (categories C1-C6): SVG by default; PNG only on explicit request. Under Codex, PNG/image generation runs through GPT Images 2.0 with a fallback to GPT Images / the default Codex image generation."
allowed-tools: Write, Read, Bash, AskUserQuestion
argument-hint: "[type (symbol/ui/background)] [name] [--png]"
user-invocable: true
---

# `generate-asset` — the asset studio (SVG / PNG)

Handles requests to generate assets for the game.

## Step 0: choosing the format

**SVG is the default mode for a manual `/generate-asset`.** If the user did not specify a
format, do not ask — create SVG straight away.

**The exception:** when assets are being created from `/autocreate` under Codex, or the command
arrived as `--from-concept` for a complete project, PNG/image generation is the default. In that
case go straight to GPT Images 2.0 → the GPT Images/default fallback and the `generate-png-asset`
rules; do not choose SVG without an explicit `--svg`.

PNG/image generation is only enabled when:
- the user passed `--png`;
- the user explicitly asks for PNG, raster, bitmap, "image generation", "AI image", "generate it as a picture";
- the user says outright that they are working in Codex and image generation should be used;
- the call comes from `/autocreate` under Codex, or from `--from-concept` for a complete project.

If PNG/image generation is chosen:
- in the **Codex app**, use the built-in image generation capability: **GPT Image 2**;
- in the headless **Codex CLI**, where the built-in tool is absent, use the same
  `gpt-image-2` through `python3 tools/gpt_image.py generate ...`; the absence of the tool is
  not a model failure and does not license an SVG fallback;
- only after a documented technical failure of GPT Image 2, retry the same prompt through
  **GPT Images / the default Codex image generation**;
- do not ask for an API key for Google/Pollinations/remove.bg;
- follow the logic of the `generate-png-asset` skill;
- external providers are acceptable only if the user explicitly asked for a specific legacy
  provider, or both Codex image-generation paths are unavailable.

### The economical PNG mode

Before any image generation call, apply the budget and manifest from
`generate-png-asset/SKILL.md`. GPT Images 2.0 creates only unique visual sources
(`generate`): the key game symbols with distinct silhouettes, the hero object and the
full-screen scene. Do not spend calls on buttons, panels, typography, settings icons,
separators, shadows, glow, VFX or colour variants: those are the `code`, `derive` or
`reuse` classes and are produced by Flutter/SVG/local processing.

You may not produce variants locally that change a game symbol's meaning, rarity, payout or
probabilities. If a variant has to read as a different round outcome, it stays a separate
`generate`-class asset and goes through the usual Design DNA check.

For simple assets (`symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`) ask for a flat
key background (`flat solid pure magenta #FF00FF background`, or `pure green #00FF00` if the
palette contains magenta/pink) with no shadows, gradients or scene, then cut it out with
`python3 tools/cutout.py <file> --type sprite`. Do not use a white background for objects with
light areas. For `background` and full-screen scenes, do not remove the background.

---

## SVG mode (the default)

1. Establish the **Design DNA / palette** (if it was not passed as an argument, read it from
   `design/gdd/game-concept.md`; if there is no GDD, ask for the theme/palette). The world,
   shapes, materials, details and colours all derive from the DNA, **not from a casino/neon
   default**; the rendering finish is always polished cartoon 2.5D.
2. Choose the asset type (the look comes from the Design DNA, not from casino/neon):
   - `symbol` / `sprite`: a 64x64 or 96x96 game element (a reel symbol, card, chip, ball, mine,
     capsule). The render style is cartoon volumetric 2.5D: a rounded readable silhouette,
     smooth gradients, saturated colour, glossy highlights. Crisp on a phone.
   - `ui`: buttons / panels / frames / icons. The shape comes from the DNA's shape language (a
     rounded rectangle is fine). Effects (`<feDropShadow>` / glow) ONLY if the DNA has them;
     a flat/minimal style has none at all.
   - `background`: a full-screen (9:16 mobile) background. The theme, the pattern and the
     **brightness come from the DNA** (a warm light forest / cold space / pastel candy — NOT
     "always a dark casino"). It must not distract from the play field; make sure it contrasts
     with the HUD.

> **UNIFIED SVG STYLE CONSTRAINTS (MANDATORY)**:
> Every SVG asset must be perfectly consistent with the others.
> - **Style from the DNA**: the world, shapes, materials, palette and brightness come from the
>   Design DNA; the rendering finish is a single polished cartoon 2.5D.
> - **Unified `<defs>`**: use the same structure of gradients and effects across every file.
> - **Lighting**: fix the lighting angle (45 degrees from the upper left, say) and stick to it strictly.
> - **Shadows & strokes**: use the same stroke-width and IDENTICAL shadow parameters
>   (`<feDropShadow dx="0" dy="4" stdDeviation="4">`) across every file.
> - **Mix & match**: mixing cartoon 2.5D with flat clipart, emoji/sticker or photorealism inside
>   one set is FORBIDDEN.
> - **Icons**: one style (all outline OR all filled) and one stroke width across the whole set.

3. Save to `assets/images/sprites/` or `assets/images/ui/`. If the folder is new, be sure to add
   the path to `pubspec.yaml`.

> Do not forget `<svg viewBox="0 0 W H" xmlns="http://www.w3.org/2000/svg">`.

> Any text baked into an asset is written in English (unless the user explicitly asked for the
> game in another language). Prefer no baked-in text at all — render copy as Flutter widgets.
