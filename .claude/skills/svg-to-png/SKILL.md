---
name: svg-to-png
description: "Converts SVG assets to PNG. A straightforward pixel conversion runs locally; if a genuinely new raster asset is needed, the primary path under Codex is GPT Images 2.0, with GPT Images / the default Codex image generation as a fallback only on a technical failure."
allowed-tools: Write, Read, Bash, AskUserQuestion, Glob
argument-hint: "[path_to_svg] [--bulk folder] [--cheap POLL_API_TOKEN] [--free REMOVE_BG_TOKEN]"
user-invocable: true
---

# `svg-to-png` — the SVG → PNG converter

The agent analyses the SVG, builds a prompt from its content and generates a high-quality PNG.

---

## Choosing the mode

### The Codex default

Determine the goal first. If you only need a PNG of the same SVG with no new material, lighting
or detail, that is a local conversion and needs no image generation. If you need a genuinely new
material game asset, use **GPT Image 2** under Codex through the built-in image generation
capability, or — when that tool is absent in the headless Codex CLI — through
`python3 tools/gpt_image.py generate ...`. The absence of the built-in tool does not count as a
model failure. If both GPT Image 2 transports technically failed or did not produce a valid PNG,
retry the same prompt through **GPT Images / the default Codex image generation**.

- Do not ask for Google/Pollinations/remove.bg keys.
- Before a semantic upgrade, read `design/asset-manifest.md`: reuse a valid SHA-256 prompt
  match, and only allow a call for the `generate` class within its overall budget.
- One SVG → one image generation call → one PNG, and only for a semantic upgrade; do not use
  GPT Images 2.0 as an expensive raster converter for UI and already-finished icons.
- For `sprite`, `symbol`, `icon`, `wild`, `scatter`, `tile`, `item`, ask for a flat key
  background (`flat solid pure magenta #FF00FF background`, or `pure green #00FF00` if the
  palette contains magenta) with no shadows, gradients or scene.
- For `background`, `ui_panel` and full-screen scenes, do not cut the background out.
- If a simple asset ends up with a background anyway, cut it out with
  `python3 tools/cutout.py <file> --type sprite`.

#### Pixel conversion without image generation

If the SVG's shape does not change, use whatever local SVG renderer is available. For example,
with `rsvg-convert`:

```bash
rsvg-convert assets/images/sprites/sprite_cherry.svg -o assets/images/sprites/sprite_cherry.png
```

If there is no local renderer, stop and say so; do not substitute an extra GPT Images 2.0 call
for a technical conversion. The semantic upgrade remains a separate `generate` mode and works
through the manifest/budget above.

### Legacy flags:
- `--cheap POLL_API_TOKEN` → Pollinations.ai (only if the user explicitly asks for the legacy fallback)
- `--free REMOVE_BG_TOKEN` → remove.bg, only if the user explicitly passed a key and asked for that service
- With no flags under Codex → do not ask: use the local renderer for a pixel conversion and GPT
  Images 2.0 for a semantic upgrade; GPT Images/default only after a technical failure.

### If there are no flags and the agent is NOT running under Codex — ask:

> "How should the SVG → PNG conversion run?
>
> **1. Codex GPT Images 2.0 → GPT Images fallback** — if it is available in the current agent
> **2. A legacy external provider** — Pollinations.ai or Google; needs an API key / billing
> **3. Manual mode** — I will produce the prompt and you generate the PNG yourself
>
> Enter 1, 2 or 3:"

---

## Option A: a single file

```
/svg-to-png assets/images/sprites/sprite_cherry.svg --cheap pk_xxx --free xxx
```

### The procedure (the agent runs it itself):

**1. Read the SVG + the concept** for context:
- The asset's name from the file name (for example `sprite_cherry` → `cherry`)
- The colours, shape and purpose from the SVG's content
- If `design/gdd/game-concept.md` exists, read the **Design DNA** (world, materials, palette,
  render style). A conversion is not "tracing the picture" — it is an **upgrade** of a flat SVG
  into a cartoon volumetric 2.5D asset of the same object, faithful to the concept.

**2. Build the prompt** in English (concept-grounded cartoon 2.5D — NOT a cheap icon):

First derive from the SVG + concept: the **subject** (what this object is in the game's world),
the **material/texture** (metal/glass/stone/wood/neon/fabric), the **lighting** (consistent for
the set, e.g. a key light from the upper left + a rim), and the **render style** from the DNA.

```
Polished cartoon 2.5D game asset of [SUBJECT identity], single hero object centered,
bold rounded and slightly exaggerated silhouette, [MATERIAL/TEXTURE] simplified into
smooth modeled gradients, clean edging, glossy highlights and restrained star glints,
soft [LIGHTING] light, rich [DNA PALETTE] colors,
crisp clean silhouette, sharp focus, faithful to the original shape/colors,
isolated on flat solid single-colour [KEY COLOUR] background, no gradient, no scene, no ground shadow, no text,
no photorealism, no product photography, no flat vector clipart, transparent-ready, 1024x1024.
```

> The object in the PNG must match the source SVG in shape and composition (this is a
> conversion, not a new idea), but it must have volume and material rather than a flat fill.

**3. Generating the PNG:**

### Mode 1: Codex GPT Images 2.0 → GPT Images fallback

Under Codex, use GPT Images 2.0 first. On a technical failure (an error, no file, or an invalid
PNG), retry the same prompt through GPT Images / the default Codex image generation.

1. Pass the prompt from step 2 into Codex's built-in image generation capability. If it is not
   in the tool list, save the prompt to a UTF-8 file and run:

```bash
python3 tools/gpt_image.py generate \
  --prompt-file design/prompts/<logical_id>.txt \
  --out assets/images/pngs/<logical_id>.png \
  --size 1024x1024 \
  --quality high
```
2. Save the result next to the source, or in `assets/images/pngs/`.
3. If the asset type is simple and the PNG has a background, cut it out with `tools/cutout.py`
   (a manual `magick -fuzz` and a bare `rembg i` are forbidden: see `generate-png-asset/SKILL.md`):

```bash
python3 tools/cutout.py assets/images/sprites/cherry.png --type sprite
```

A non-zero exit code = check the source and the key colour first, then apply the one permitted
recovery call through GPT Images 2.0. Use GPT Images/default only on a technical error of GPT
Images 2.0, never because of a visual defect or a cutout error.

### Mode 2: legacy fallback Pollinations.ai (--cheap)

```bash
POLL_API_KEY="[the key from --cheap]"
ASSET_NAME="cherry"
PROMPT="Professional game asset: cherry. Red glossy cherries, single isolated object, clean edges, vibrant cartoon style, 2D game sprite, pure white background, 1024x1024"
OUTPUT_DIR="assets/images/sprites"
REMBG_KEY=""  # only if the user explicitly passed --free
MODEL="flux"  # flux | zimage | gptimage

echo "━━━ SVG→PNG: ${ASSET_NAME} (Pollinations, ${MODEL}) ━━━"

# Generate through Pollinations.ai
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${PROMPT}'))")
curl -s -L "https://gen.pollinations.ai/image/${ENCODED}?width=1024&height=1024&nologo=true&model=${MODEL}&seed=-1" \
  -H "Authorization: Bearer ${POLL_API_KEY}" \
  -o "${OUTPUT_DIR}/${ASSET_NAME}.png"

if [ ! -s "${OUTPUT_DIR}/${ASSET_NAME}.png" ]; then
  echo "✗ Pollinations returned no image"
  exit 1
fi

SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Generated: ${SIZE}"

# Remove the background for a simple asset
python3 tools/cutout.py "${OUTPUT_DIR}/${ASSET_NAME}.png" --type sprite

FINAL_SIZE=$(ls -lh "${OUTPUT_DIR}/${ASSET_NAME}.png" | awk '{print $5}')
echo "✓ Done: ${OUTPUT_DIR}/${ASSET_NAME}.png (${FINAL_SIZE})"
```

### Mode 3: legacy fallback Google Imagen API

```bash
API_KEY="[the user's key]"
ASSET_NAME="cherry"
PROMPT="Professional game asset: cherry. Single isolated object on flat solid pure magenta #FF00FF background, no gradient, 2D game sprite, vibrant style, no scene, no ground shadow, 512x512."
OUTPUT_DIR="assets/images/sprites"
mkdir -p "${OUTPUT_DIR}"

curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"instances\": [{\"prompt\": \"${PROMPT}\"}], \"parameters\": {\"sampleCount\": 1, \"aspectRatio\": \"1:1\"}}" \
  -o /tmp/imagen_response.json

# Decode base64 → PNG
python3 -c "
import json, base64, sys
with open('/tmp/imagen_response.json') as f:
    data = json.load(f)
if 'error' in data:
    print(f'✗ {data[\"error\"]}'); sys.exit(1)
img_b64 = data['predictions'][0]['bytesBase64Encoded']
path = '${OUTPUT_DIR}/${ASSET_NAME}.png'
open(path, 'wb').write(base64.b64decode(img_b64))
print(f'✓ {path}')
"
```

**4. Check the result:**
```bash
ls -lh ${OUTPUT_DIR}/${ASSET_NAME}.png
file ${OUTPUT_DIR}/${ASSET_NAME}.png
```

**5. Tell the user** where the finished file is.

---

## Option B: bulk mode (a whole folder)

```
/svg-to-png --bulk assets/images/svgs --cheap pk_xxx --free xxx
```

The agent:
1. Finds every `.svg` file in the folder through Glob
2. Determines the API keys from the flags, or asks **once**
3. For each file, first chooses between a local conversion and a semantic upgrade, and checks
   `design/asset-manifest.md`; a matching valid SHA-256 is reused.
4. Under Codex, uses GPT Images 2.0 only for a unique semantic upgrade of the `generate` class;
   GPT Images/default is permitted only after a technical failure.
5. For legacy Pollinations: a 3-second pause between requests.
6. For legacy Google Imagen: a 4-second pause (the free tier limit is 15 RPM).
7. Saves the PNGs to `assets/images/pngs/` or next to the sources

### Bulk through Codex GPT Images 2.0 → GPT Images fallback:

The agent makes a separate image-generation call only for each unique semantic upgrade, using
the template from mode 1. Straight shape copies are rendered locally, and `reuse` never calls
the model. Do not combine different game items into one request.

---

## Option C: manual mode (no API)

If the user does not want to use an API:

### Step 1: analyse the SVG
The agent reads the SVG and composes a detailed prompt in English.

### Step 2: the prompt for an external generator
```
Professional game asset: [name].
Single isolated object, clean edges, vibrant colors.
2D game sprite style, flat solid pure magenta #FF00FF background, no gradient, no scene, no ground shadow, 1024x1024 pixels.
[the colour and shape description from the SVG]
```

### Step 3: the user generates the PNG by hand and saves it into the project.

---

## Legacy Pollinations models for conversion

| Model | Recommendation | Why |
|-------|----------------|-----|
| `flux` | Legacy fallback | Good quality, fast, cheap |
| `zimage` | For large sprites | Built-in 2x upscale |
| `gptimage` | For complex assets | The best quality, transparency support (`transparent: true`) |

---

## Important rules

1. Under Codex, use GPT Images 2.0 first and only for a semantic upgrade; GPT Images/default is
   available exclusively after a technical failure of GPT Images 2.0.
2. **One image-generation call = one unique source asset** — do not combine different game
   objects into one request.
3. A legacy provider's API key is never written into a file.
4. If a legacy API returns an error, show the user the full response.
5. Save finished PNGs to `assets/images/sprites/` (single) or `assets/images/pngs/` (bulk).
6. When finished, show `ls -lh` with the results.

## Diagnostics

| Symptom | Cause | Fix |
|---------|-------|-----|
| HTTP 401 (Pollinations) | An invalid API key | Check the key at https://enter.pollinations.ai |
| HTTP 402 (Pollinations) | Not enough pollen | Top up, or use the free model (flux) |
| An empty PNG | The server returned no data | Try a different model or prompt |
| Poor quality | The prompt is too simple | Add detail from the SVG (colours, shape, style) |
| `cutout.py` returned FAIL | The background is not flat, or the key matched the object's palette | Check the source/key and re-cut; if the source is unusable, use one GPT Images 2.0 recovery, not a quality-driven fallback |
| `cutout.py: requires numpy + Pillow` | Missing dependencies | `apt-get install -y python3-numpy python3-pil` (or `pip install numpy pillow`) |
