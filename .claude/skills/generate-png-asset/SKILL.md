---
name: generate-png-asset
description: "Generation of PNG assets. In Codex, the main path is GPT Image 2: built-in image generation tool, and in the headless Codex CLI - direct Images API via tools/gpt_image.py. SVG is only allowed as the last explicit fallback. Simple assets are generated on a flat key background and cut via tools/cutout.py."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[description] | [--batch list] | [--from-concept] | [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `generate-png-asset` - PNG assets for mini-games

## Default rule

1. **Exception for `/autocreate`:** if the call comes from `/autocreate` or `--from-concept`
   of a complete project in Codex, PNG/image generation is default even without `--png`; SVG
   prohibited without an explicit `--svg`.
2. If the user did not request PNG/image generation and this is not `/autocreate`, use
   `/generate-asset` to create **SVG**.
3. If the user explicitly requested PNG/image generation and the agent works in **Codex** -
   use **GPT Image 2 (`gpt-image-2`)** first:
   - if the built-in image-generation tool is available, call it;
   - if tool is not in the headless Codex CLI - call
     `python3 tools/gpt_image.py generate ...`. Lack of built-in tool **is not**
     a GPT Image 2 failure and does not justify switching to SVG.
   If both GPT Image 2 transports have a documented technical failure or fail to create a
   valid PNG, only then is GPT Images/default Codex image generation allowed.
   The SVG remains the last fallback and is not automatically selected in `/autocreate`.
4. Don't ask for Google, Pollinations or remove.bg keys in the Codex path.
5. The external providers below are considered legacy fallback and are used only at the explicit request of the user or if Codex image generation is not available.

## Generation services

| Service | When to use | Requirements |
|--------|--------------------|------------|
| **Codex GPT Image 2** | Main PNG/image-generation path in Codex app | Built-in Codex image generation tool |
| **GPT Image 2 API bridge** | The main path in headless is `codex exec` when the built-in tool is not exposed | `python3 tools/gpt_image.py`; in web-service `OPENAI_API_KEY` is injected automatically |
| **Codex GPT Images / default image generation** | First fallback after a documented GPT Image 2 failure | Built-in Codex image generation tool |
| **SVG** | Only manual default outside `/autocreate` or last explicitly committed fallback | Nothing |
| **Pollinations.ai / Google Gemini** | Only legacy fallback or explicit user request | External API key / billing |

**Background removal:** `python3 tools/cutout.py` only. Manual `magick -fuzz`, naked `rembg i`
and `remove.bg` are prohibited (see "Local background removal" below).

---

## Budget manifesto and cache (MANDATORY)

Savings are achieved not by simplifying the prompt, but by eliminating repeated and unnecessary calls.
GPT Images 2.0 remains the only standard raster source generator in Codex.

Before the first generation, create `design/asset-manifest.md`; `design/asset-prompts.md`
remains a detailed artistic ledger. A manifest is a machine-readable record for an agent.
decisions on the flow of each call:

```markdown
# Asset Manifest — Budgeted GPT Images 2.0

budget: unique_sources=12, technical_recovery_calls=2

| logical_id | class | target_path | prompt_sha256 | source_id | attempts | validation | status |
|------------|-------|-------------|---------------|-----------|----------|------------|--------|
```

Manifest classes:

| Class | When to use | Consumption GPT Images 2.0 |
|-------|-----------------|-----------------------|
| `generate` | Unique silhouette of game symbol, hero object or full screen scene | 1 successful source |
| `derive` | Crop, scale, safe color option or local animation phase of an existing asset | 0 |
| `code` | UI, text, buttons, panels, icons, frames, shadows, glow, particles and VFX | 0 |
| `reuse` | Already validated source without changing its game meaning | 0 |

For each `generate` before the call, construct a normalized prompt (including type, Design DNA,
key color and path) and write it SHA-256. If the manifest already has the same
`prompt_sha256`, the file exists, is valid and passed `cutout.py --check` for a simple asset,
reuse it without calling again. For example:

```bash
printf '%s' "$NORMALIZED_PROMPT" | shasum -a 256
```

Standard budget for `/autocreate` and `--from-concept`: no more than **12 unique successful
source codes** and no more than **2 technical recovery calls** per game. Inside these 12
By default, 5-8 unique game symbols and a maximum of two full-screen scenes are allowed.
Exceeding the limit is not done silently: a manual command requires an explicit user request, and
the autopipe is required to first reclassify the element to `derive`, `code` or `reuse`.

Color variations are allowed only if they do not change the recognizable result of the round,
rarity, payout or probability. Otherwise it is a separate `generate` asset.

### Fallback at no extra cost

GPT Images / default Codex image generation is allowed **only** after documented
technical failure of GPT Image 2 through both available transports: built-in tool (if it
exposed) and `tools/gpt_image.py` (headless CLI). The very absence of a built-in tool is not
failure: use API bridge immediately. Record the HTTP/validation reason in
`attempts`/`status` manifest and repeat **same** prompt. Visual taste, AR1–AR10,
an unsuitable composition or an unsuccessful chroma-key are not grounds for changing the model:
apply local processing first, then use one of the two if necessary
recovery calls again via GPT Image 2. SVG are not created silently.

---

## Key background color (chroma key) - select BEFORE generation

The white background cannot be cut out from a white object: chicken, feather, ice, glass, chrome, foam, snow
They blend into the background and leave holes behind. Therefore, simple assets are generated on
**flat key color, as far from the object’s palette as possible**.

Selection rule (perform for EVERY asset, write selection in `design/asset-prompts.md`):

| Object Palette (Design DNA) | Key | In prompt |
|------------------------------|------|-----------|
| no magenta/pink/violet | **magenta** (default) | `flat solid pure magenta #FF00FF background` |
| there is purple/pink/violet, no green | **green** | `flat solid pure green #00FF00 background` |
| there are both purple and green | **blue** | `flat solid pure blue #0000FF background` |
| the object is bright, saturated, without white and light reflections | white (let's say) | `flat solid pure white background` |

Always add to the prompt: `flat solid single-color background, no gradient, no vignette,
no shadow on the background, subject fully inside frame`.

The key is detected automatically when cutting - but choose it correctly anyway
mandatory: measured cutting error with bad key (background of the same tone as the subject)
many times higher than with the correct one.

---

## Step 0: Determine the mode

### If the agent works in Codex

- Always select Codex image-generation chain:
  **built-in GPT Image 2 (if available) → `tools/gpt_image.py` (`gpt-image-2`) →
  GPT Images/default Codex fallback**.
- First create/read `design/asset-manifest.md`, check SHA-256 prompt and limits;
  create a PNG only for class `generate` without a valid cached match.
- Create one PNG per image generation call.
- Save the result in `assets/images/pngs/`, `assets/images/sprites/`, `assets/images/ui/` or `assets/images/backgrounds/` by asset type.
- For `symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item` ask for a **flat key background** (see "Key background color" above) without shadows, gradients or scene; transparency appears only after `tools/cutout.py`.
- For `background`, `main_menu_bg`, `game_bg`, full-screen illustrations, DO NOT cut out the background.
- For `/autocreate` create/update `design/asset-prompts.md`: full prompt, subject,
  material, lighting, render style, file path and post-processing verdict for each asset.

### If legacy flags are passed:
- `--cheap POLL_API_TOKEN` → Pollinations.ai with key (legacy fallback)
- `--cheap POLL_API_TOKEN --free REMOVE_BG_TOKEN` → Pollinations + remove.bg only if the user explicitly requests this service
- Without legacy flags in Codex → ​​do not ask for foreign keys; use GPT Image 2.
  In flutter-game-web-service per-user `OPENAI_API_KEY` is already passed to the bridge process.

### If there are no flags and the agent does NOT work in Codex, ask:

> "How to generate PNG assets?
>
> **1. SVG** - default mode, via /generate-asset
> **2. External PNG provider** – Pollinations.ai or Google Gemini, API key / billing required
> **3. Manual prompt** - the agent will prepare the prompt, the user generates it outside the studio
>
>Enter 1, 2 or 3:"

---

## Codex mode: GPT Image 2 tool/API → GPT Images fallback

**Use `gpt-image-2` first in Codex.** In Codex app, call built-in image-generation
tool. In headless `codex exec`, where this tool is not in the list, use the standard bridge:

```bash
python3 tools/gpt_image.py probe
python3 tools/gpt_image.py generate \
  --prompt-file design/prompts/<logical_id>.txt \
  --out assets/images/sprites/<logical_id>.png \
  --size 1024x1024 \
  --quality high
```

One `generate` = one asset. Bridge strictly uses the `gpt-image-2` model, checks
`data[0].b64_json`, PNG signature/IHDR and writes the file atomically. In web-service user key
is transmitted automatically only to the child `codex exec`; do not print or save it.
In standalone Codex CLI, the user himself sets `OPENAI_API_KEY` in the environment - never
ask to insert the key into the prompt or chat.

If the API returned `403`, check OpenAI organization access/verification; `429` — rate limit;
show other errors verbatim without secret. Do not automatically replace such a failure with SVG.
GPT Images/default or legacy provider are allowed only after fixed technical
failure of GPT Image 2 or at the explicit request of the user.

### Cartoon finish & concept fidelity (read BEFORE building the prompt)

> The goal is NOT “draw an abstract icon.” The goal is an **expressive cartoon 2.5D asset,
> which unmistakably belongs to the world of THIS game**. Before generating each asset
> independently derive from the concept (`design/gdd/game-concept.md`) and Design DNA four
> things and substitute them in the prompt:

1. **Subject identity** - what exactly is this object in the game world (not “heme”, but “faceted”
   amethyst with inner glow"; not a “button”, but a “brass key with engraving”).
2. **Material & texture** - what it is made of: metal/glass/wood/gem/neon/fabric;
   how the material is simplified into pure cartoon volume, gradients and glossy highlights.
3. **Lighting** - a single source for the ENTIRE set (for example, soft upper-left key light
   + light rim). Light = the main sign of an “expensive” asset.
4. **Render style** — polished cartoon 2.5D casual-game art: bold rounded/exaggerated
   silhouette, smooth modeled gradients, saturated theme-aware colors, clean edging,
   glossy highlights and restrained star glints. DNA determines the world, forms, materials,
   palette and details. Keep the finish the same throughout the entire set.

**Hard quality floor for `/autocreate`:** photorealistic/product-shot render, flat
vector icon, emoji/sticker, generic logo, cheap clipart, random neon/casino asset without
connections to a concept, sprite sheet, text within an image, or an object with a different light pattern
considered FAIL.
First eliminate locally correctable defects (cutout, frame normalization, reclassification
in `code`/`derive`); one recovery call to GPT Images 2.0 is allowed for a source generation defect
to `logical_id`. You cannot automatically switch to fallback due to aesthetic considerations.

### Prompt for a simple asset (concept-grounded, cartoon 2.5D)

```
Polished cartoon 2.5D mobile game asset of [SUBJECT IDENTITY from concept],
single hero object centered, bold rounded and slightly exaggerated silhouette,
[MATERIAL/TEXTURE] simplified into smooth modeled gradients, clean gold or color edging
where appropriate, glossy specular highlights and restrained star glints,
shared soft [LIGHTING: key from top-left + subtle rim], rich [DNA PALETTE] colors,
crisp clean silhouette readable at 64 px, premium casual-game illustration,
flat solid single-colour [KEY COLOUR] background, no gradient, no vignette, subject fully
inside frame, transparent-ready cutout, NO scene, NO ground shadow, NO shadow on the
background, NO text, NO border, NO logo, NO sprite sheet, NO photorealism,
NO product photography, NO flat vector clipart, NO emoji/sticker, 1024x1024 PNG.
[TYPE_DETAILS]
```

> `[KEY COLOUR]` is substituted according to the table from “Key background color” (default
> `pure magenta #FF00FF`). Immediately after generation - `python3 tools/cutout.py <file>
> --type sprite`. Never ask for a complex scene, a shadow under an object, or a gradient
> background for a simple asset - this breaks the cut, and cutout.py will reject such an asset.

### Prompt for background (without cutting out the background)

```
Polished cartoon 2.5D 9:16 mobile game background: [SCENE from concept & DNA].
Full atmospheric scene with saturated layered depth (foreground / midground / sky layers),
[DNA mood & palette], volumetric light, no foreground characters, no UI, no text,
calm readable empty area in the vertical center for gameplay, high quality PNG.
```

### After generation

1. Save the PNG to the target folder.
2. Check the file using `file path/to/asset.png`.
3. If this is a simple asset, apply local removal of the key background.
4. Add the folder to `pubspec.yaml` if it is new.

### Local background removal - ONLY via `tools/cutout.py`

Only for `symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`.
Do not apply to `background`, `ui_panel`, full screen scenes and artwork
(the skill itself will skip these types).

> **It is forbidden to cut out the background manually** - neither `magick -fuzz ... -transparent white`,
> neither naked `rembg i`. Global fuzz match punches holes in white highlights, eyes,
> chrome and foam, gives a binary (torn) alpha and leaves a white halo around the edge.
> `tools/cutout.py` does what a composer does: fill the background from the edge of the frame
> (inner white pixels not touched), fractional alpha on edge, decantation
> (removing background color from translucent pixels), despill, cropping to content and
> frame normalization. `rembg`, if set, is used as an assist.

```bash
python3 tools/cutout.py assets/images/pngs/cherry.png --type sprite
```

Conclusion: `✅ cherry.png 512×512 flood+matte` - the background has been removed and checked.
`✗` means the asset is unusable (the background is not flat / the key color is not the same) -
first check the source and key, then use only authorized recovery GPT Images
2.0; don’t “press” manually and don’t switch to fallback in terms of quality.

| Flag | Why |
|------|-------|
| `--type sprite\|icon\|ui\|tile\|background` | canvas and margin preset; `background`/`ui_panel` skipped |
| `--key auto\|magenta\|green\|blue\|white\|#RRGGBB` | key color; `auto` identifies it by frame |
| `--dir assets/images/sprites` | batch by folder |
| `--check` | alpha audit only, no recording (used in `/asset-review`) |
| `--no-trim` | do not reframe (when the original composition is important) |
| `--backup` | save original as `*.orig.png` |

One call per asset immediately after generation; for the entire set - `--dir` at the end.

---

## Legacy fallback: Pollinations.ai

### Image Models (Pollinations)

| Model | Quality | Price | Features |
|--------|---------|------|-------------|
| `flux` | good | Cheap | Fast |
| `zimage` | Good + 2x upscale | Cheap | Fast 6B Flux with upscale |
| `gptimage` | High | Paid (pollen) | OpenAI image gen, transparency support |
| `gptimage-large` | Very high | Paid | HD, transparency |
| `klein` | Average | Cheap | FLUX.2 Klein 4B, fast |

### Removing background in legacy fallback

The same `python3 tools/cutout.py` - it does not depend on the generation provider.
`remove.bg` and manual ImageMagick are not used even in the legacy path.

---

### Single character pattern (one Bash call):

Assets like `symbol`, `icon`, `wild`, `scatter` → **background is removed automatically**.
Assets like `background`, `ui_panel` → background are NOT removed.

```bash
POLL_API_KEY="[key from --cheap or from user]"
ASSET_NAME="cherry"
ASSET_TYPE="symbol"   # symbol | icon | wild | scatter | background | ui_panel
PROMPT="red glossy cherries fruit, game sprite icon, flat solid pure magenta #FF00FF background, no gradient, vibrant colors, cartoon style, isolated object"
OUTPUT_DIR="assets/images/pngs"
MODEL="flux"          # legacy: flux | zimage | gptimage | klein
mkdir -p "${OUTPUT_DIR}"

echo "━━━ [${ASSET_TYPE}] Generating: ${ASSET_NAME} (model: ${MODEL}) ━━━"

#1. Generation via Pollinations.ai (new API)
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${PROMPT}'))")
curl -s -L "https://gen.pollinations.ai/image/${ENCODED}?width=1024&height=1024&nologo=true&model=${MODEL}&seed=-1" \
  -H "Authorization: Bearer ${POLL_API_KEY}" \
  -o "${OUTPUT_DIR}/${ASSET_NAME}.png"

if [ ! -s "${OUTPUT_DIR}/${ASSET_NAME}.png" ]; then
  echo "✗ Pollinations did not return the image"
  exit 1
fi

SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Generated: ${SIZE}"

# 2. Removing the background (only for symbol/icon/wild/scatter)
if [[ "${ASSET_TYPE}" == "symbol" || "${ASSET_TYPE}" == "icon" || "${ASSET_TYPE}" == "wild" || "${ASSET_TYPE}" == "scatter" ]]; then
  python3 tools/cutout.py "${OUTPUT_DIR}/${ASSET_NAME}.png" --type sprite
else
  echo "⏭ Type '${ASSET_TYPE}' - background removal skipped"
fi

FINAL_SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Done: ${OUTPUT_DIR}/${ASSET_NAME}.png (${FINAL_SIZE})"
```

### Alternative: OpenAI-compatible endpoint (POST)

For more complex scenarios (transparency, editing):

```bash
POLL_API_KEY="[key]"
ASSET_NAME="cherry"
PROMPT="red glossy cherries fruit, game sprite icon, flat solid pure magenta #FF00FF background, no gradient"
OUTPUT_DIR="assets/images/pngs"
mkdir -p "${OUTPUT_DIR}"

# POST /v1/images/generations (OpenAI-compatible)
RESPONSE=$(curl -s -X POST "https://gen.pollinations.ai/v1/images/generations" \
  -H "Authorization: Bearer ${POLL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"${PROMPT}\",\"model\":\"flux\",\"size\":\"1024x1024\",\"response_format\":\"url\"}")

# Extract URL and download
IMG_URL=$(echo "${RESPONSE}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['url'])")
curl -s -L "${IMG_URL}" -o "${OUTPUT_DIR}/${ASSET_NAME}.png"
echo "✓ ${OUTPUT_DIR}/${ASSET_NAME}.png"
```

---

### Prompts - derived from Design DNA (example below - for ONE specific slot)

> ⚠️ The table below is an illustration for a classic fruit slot. **For THIS game
> symbols, palette and style are taken from the Design DNA concept** (`design/gdd/game-concept.md`),
> and NOT casino/neon by default. For `/autocreate` the basic style is polished cartoon
> 2.5D casual-game art. Substitute theme/world, palette, shapes, materials, single
> light and brightness from DNA.
> Egyptian slot → scarabs/ankhi with the texture of gold and lapis lazuli; space → crystals/
> alloys/stellar ceramics in cold temperatures; etc. Maintain a consistent style throughout the entire set.

| Symbol (example-slot) | ASSET_TYPE | Prompt (style/palette - substitute from DNA) |
|--------|-----------|--------|
| cherry | symbol | `red glossy cherries fruit, game sprite, flat solid [KEY] background, vibrant cartoon` |
| bar | symbol | `chrome metallic BAR text, slot machine symbol, flat solid [KEY] background, shiny 3D` |
| seven | symbol | `lucky number seven, red with gold outline, bold game icon, flat solid [KEY] background` |
| diamond | symbol | `blue diamond gemstone, crystal faceted, game icon, flat solid green #00FF00 background, glossy` |
| wild | wild | `golden star wild, glowing rainbow aura, game icon, flat solid green #00FF00 background` |
| scatter | scatter | `purple hexagon lightning bolt, scatter symbol, game icon, flat solid green #00FF00 background` |
| main_menu_bg | background | `[DNA theme] background, [DNA palette], atmospheric, no characters` - brightness and peace from DNA, not an “always dark casino” |

### Peculiarities:
- In Codex, for simple assets, ask for a flat key background immediately, then `tools/cutout.py`
- A transparent background is not directly a default: a flat key gives a predictably clean alpha,
  and “transparent background” models are performed every other time and often produce a white JPEG-like background
- Legacy fallback models: `flux`, `zimage`, `gptimage`
- Each Bash call = one asset (do not loop)
- `seed=-1` for random result every time

---

## Legacy fallback: Google Gemini - requires billing

### Step 1: Checking the key (quick diagnostics)

Run it before generating - make sure the key is working:

```bash
API_KEY="[user key]"

PROBE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${API_KEY}" -H "Content-Type: application/json" -d '{"contents":[{"parts":[{"text":"red dot"}]}],"generationConfig":{"responseModalities":["IMAGE"]}}')

echo "HTTP status: ${PROBE}"

if [ "$PROBE" = "200" ]; then
  echo "✓ The key works, gemini-2.5-flash-image is available"
elif [ "$PROBE" = "403" ]; then
  echo "✗ 403 - invalid API key or Gemini API is not included in AI Studio"
elif [ "$PROBE" = "404" ]; then
  echo "✗ 404 - try an alternative model name (see Diagnostics)"
else
  echo "✗ HTTP ${PROBE} - check the key and connection"
fi
```

---

## Step 2: Game Context

Read if available:
- `design/gdd/game-concept.md` → theme, colors, style
- `design/balance/rtp-config.json` → list of symbols (gambling)

---

## Step 3: Building a prompt

> Style, palette and brightness are taken from the **Design DNA** concept - NOT casino/neon
> default. For `/autocreate` `[ART-STYLE]` = polished cartoon 2.5D casual-game art.
> First output **Subject / Material / Lighting** (see “Cartoon finish & concept
> fidelity" above) - without them you will get a cheap flat icon.

```
Polished cartoon 2.5D mobile game asset of [SUBJECT IDENTITY from concept],
single hero object centered, bold rounded and slightly exaggerated silhouette,
[MATERIAL/TEXTURE: metal/glass/stone/wood/neon] simplified into smooth modeled
gradients, glossy highlights and restrained star glints, [ART STYLE] render,
soft [LIGHTING: key top-left + light rim], rich [PALETTE from DNA] colors,
crisp clean silhouette, sharp focus, isolated on flat solid single-colour [KEY COLOUR]
background, no gradient, no scene, no ground shadow, no text, no photorealism,
no product photography, no flat vector clipart, transparent-ready, 1024x1024.
[TYPE-DETAILS]
```

### Details by type (effects - only if they are in DNA):
| Type | Add (substitute under DNA) |
|-----|---------|
| `symbol` / `sprite` | polished cartoon 2.5D: theme/shapes/materials/palette from DNA, single finish for the set |
| `wild` (gambling) | premium accent symbol; effect (glow/shine/no) - from DNA |
| `scatter` (gambling) | a special trigger symbol, visually highlighted using DNA |
| `ui` button | shape from shape language DNA; effect (glow/shadow/flat) from DNA, no text |
| `background` | peace and **brightness** from DNA (not “always dark casino”), does not distract from the playing field |

> **Important for transparent backgrounds:** legacy Imagen/Gemini does not always generate RGBA.
> If alpha doesn't work, cut out the background using `tools/cutout.py` in Step 5.

---

## Step 4: Generating via gemini-2.5-flash-image

**API Format:** `generateContent` with `responseModalities: ["IMAGE"]`
**Answer:** `candidates[0].content.parts[n].inlineData.data`
**Resolution:** 1024×1024

```bash
API_KEY="[key]"
ASSET_NAME="[name]"
PROMPT="[prompt from Step 3]"
OUTPUT_DIR="assets/images/pngs"
mkdir -p "${OUTPUT_DIR}"

# IMPORTANT: URL and -d on ONE line each, no hyphens inside
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${API_KEY}" -H "Content-Type: application/json" -d "{\"contents\":[{\"parts\":[{\"text\":\"${PROMPT}\"}]}],\"generationConfig\":{\"responseModalities\":[\"IMAGE\"]}}" -o "/tmp/gemini_resp_${ASSET_NAME}.json"

# Validation + decoding (python3 stdlib, no pip)
python3 - <<PYEOF
import json, base64

name = "${ASSET_NAME}"
out_dir = "${OUTPUT_DIR}"

with open(f"/tmp/gemini_resp_{name}.json") as f:
    data = json.load(f)

# API error
if "error" in data:
    print(f"✗ API error: {data['error'].get('message', data['error'])}")
    exit(1)

# Find inlineData
for candidate in data.get("candidates", []):
    for part in candidate.get("content", {}).get("parts", []):
        if "inlineData" in part:
            img_bytes = base64.b64decode(part["inlineData"]["data"])
            out_path = f"{out_dir}/{name}.png"
            with open(out_path, "wb") as out:
                out.write(img_bytes)
            print(f"✓ {out_path} ({len(img_bytes) // 1024} KB)")
            exit(0)

print(f"✗ No inlineData in response. Keys: {list(data.keys())}")
PYEOF
```

---

## Step 5: Removing backgrounds for simple assets

Don't ask for a separate service. Apply only to simple assets (`symbol`, `sprite`, `icon`, `wild`, `scatter`, `tile`, `item`). For `background` / full-screen illustration, skip.

```bash
python3 tools/cutout.py "${OUTPUT_DIR}/${ASSET_NAME}.png" --type sprite
```

Non-zero return code = check source and key, then recut/normalize locally.
If the source is truly unusable, use one enabled GPT recovery call
Images 2.0 with flat key background; do not switch to fallback due to a cutout error.

---

## Generation: STRICTLY ONE ASSET AT A TIME

### CRITICAL RULE FOR AGENT

**FORBIDDEN:**
- Run multiple Bash calls in a row without waiting
- Make the next API request before the previous bash has completed completely
- Use background processes (`&`) or parallel calls

**NECESSARILY:**
- One Bash tool call = one asset
- For Gemini: `sleep 65` after each (rate limit 10 RPM)
- For Pollinations: `sleep 3` after each (faster)
- For Codex GPT Images 2.0 / GPT Images fallback: one image generation call = one asset
- The next Bash tool call only AFTER the previous one has returned a result

---

### Legacy template for one asset - Gemini (copy and change ASSET_NAME + PROMPT):

```bash
API_KEY="[key]"
ASSET_NAME="cherry"
PROMPT="Red glossy cherries fruit, game sprite icon, white background, vibrant colors, cartoon style, 1024x1024"
OUTPUT_DIR="assets/images/pngs"
mkdir -p "${OUTPUT_DIR}"

echo "━━━ Generating: ${ASSET_NAME} ━━━"

curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${API_KEY}" -H "Content-Type: application/json" -d "{\"contents\":[{\"parts\":[{\"text\":\"${PROMPT}\"}]}],\"generationConfig\":{\"responseModalities\":[\"IMAGE\"]}}" -o "/tmp/g_${ASSET_NAME}.json"

python3 - <<PYEOF
import json, base64, sys
name = "${ASSET_NAME}"
out_dir = "${OUTPUT_DIR}"
with open(f"/tmp/g_{name}.json") as f:
    data = json.load(f)
if "error" in data:
    print(f"✗ {data['error'].get('message', str(data['error']))}")
    sys.exit(1)
for c in data.get("candidates", []):
    for p in c.get("content", {}).get("parts", []):
        if "inlineData" in p:
            img = base64.b64decode(p["inlineData"]["data"])
            path = f"{out_dir}/{name}.png"
            open(path, "wb").write(img)
            print(f"✓ {path} ({len(img)//1024} KB)")
            sys.exit(0)
print(f"✗ No inlineData. Keys: {list(data.keys())}")
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
  echo "⏳ Wait 65 seconds (rate limit)..."
  sleep 65
  echo "Done. You can generate the next one."
else
  echo "✗ Error. Full answer:"
  cat "/tmp/g_${ASSET_NAME}.json"
  echo "DO NOT CONTINUE - inform the user of an error."
fi
```

---

### Sequence for 6 characters (the agent makes 6 separate Bash calls):

**Call 1:** cherry → waiting for completion → reports "✓ cherry ready (1/6)"
**Call 2:** bar → waiting for completion → "✓ bar ready (2/6)"
**Call 3:** seven → waiting for completion → "✓ seven ready (3/6)"
**Call 4:** diamond → waiting for completion → "✓ diamond ready (4/6)"
**Call 5:** wild → waiting for completion → "✓ wild ready (5/6)"
**Call 6:** scatter → "✓ scatter ready (6/6)"

If there is an error, stop, show the answer, ask the user.

---

## --from-concept: from rtp-config.json automatically

1. Read `design/balance/rtp-config.json` → list `symbols[].name`
2. Read `design/gdd/game-concept.md` → theme and colors
3. We build `ASSETS=()` dynamically and run the batch cycle above

---

## After generation

Add to `pubspec.yaml` if the folder is new:
```yaml
flutter:
  assets:
    - assets/images/pngs/
```

---

## Error diagnosis

### Pollinations.ai

| Symptom | Reason | Solution |
|---------|---------|---------|
| HTTP 401 | Missing or invalid API key | Check key for https://enter.pollinations.ai |
| HTTP 402 | Not enough pollen balance | Top up your balance or switch to a free model (flux, zimage) |
| HTTP 403 | No permissions (permission denied) | Check key type (pk_ vs sk_) and permissions |
| Empty file | The server did not return the image | Try a different model or simplify the prompt |
| Long answer | The gptimage model is slower | Switch to flux or zimage for speed |

### Google Gemini

| Symptom | Reason | Solution |
|---------|---------|---------|
| HTTP 403 | Invalid key or Gemini API not activated | AI Studio → API Keys → make sure Gemini API is enabled |
| HTTP 404 `model not found` | Invalid model name | Try `gemini-2.5-flash-preview-image-generation` |
| HTTP 400 `responseModalities` | Model does not support IMAGE | Add `"TEXT"` to the list: `["IMAGE","TEXT"]` |
| HTTP 429 | 10 RPM limit exceeded | Increase sleep to 65+ sec |
| `inlineData` not found | Gemini returned only text | Change prompt: start with "Create an image of..." |
| PNG file empty | base64 error | Show user full JSON from `/tmp/g_*.json` |

**Rule:** For ANY error, show the user the full API response. Never hide.
