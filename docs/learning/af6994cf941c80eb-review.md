# Store panorama single-scene review

## Evidence reviewed

- User correction: the gameplay block belongs in image-generation context; a screenshot or its board crop must not be pasted into the carousel panorama. The whole panorama should be generated as one image with a natural three-quarter/3D gameplay view.
- Existing Phase 1 called `boardplate --from-shot` and offered a deterministic field compositing fallback after a failed generation. The focused topology guidance test encoded that fallback.

## Review findings

| Contract | Finding |
|---|---|
| Panorama production | PASS: Phase 1 requires one complete generated scene and bars a placeholder opening, screenshot crop, board plate, symbol grid, or other gameplay insert. |
| Reference use | PASS: Phase 0 and Phase 1 designate the active gameplay capture as context for real field dimensions, symbol identity, ordering, and resolving state. |
| Gameplay truth | PASS: The visual audit still counts topology and verifies the decisive outcome. A failed bounded generation is reported as a blocker instead of repaired by pasting a field. |
| Delivery review | PASS: Phase 2 checks for a visible capture boundary, preserved screenshot pixels, UI crop, placeholder, or pasted plate; Phase 6 records generation provenance. |
| Scope | PASS: Later showcase slides remain real captures, and the separately specified feature graphic retains its framed phone with a real capture. Runtime backgrounds and wiring are untouched. |
| Tests | PASS: The focused test now rejects the old boardplate invocation and deterministic layer guidance in Phase 1 while checking one-scene and visual review instructions. |

## Limit

This is guidance and a documentation regression check, not a generated image. A future store run still needs a visual comparison of the generated panorama with its runtime gameplay reference before delivery.

The Codex skill-creator quick validator rejects the existing Claude-specific `argument-hint`
and `user-invocable` frontmatter keys. They are retained for this repository's command routing.
YAML parsing and focused workflow checks validate the revised skill without altering those keys.
