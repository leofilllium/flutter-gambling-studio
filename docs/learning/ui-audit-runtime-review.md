# UI Audit Runtime-Proof Review

## Scope

This proposal strengthens the existing `ui-audit` skill. It does not add another skill and does
not include game or application code.

## Scenario review

- **Bottom-aligned gameplay with green source tests:** the audit remains `RUNTIME PENDING` or
  `NEEDS FIX` until a phone idle capture proves the field bounds and the usable HUD-to-field and
  field-to-controls gaps are compositionally justified.
- **Null asset IDs hidden by filtering:** A7 checks the complete configured ID set before any
  null/blank filtering, then requires the runtime map, `pubspec.yaml`, real files, and live outcomes
  to agree.
- **Intentionally typographic outcomes:** text-rendered glyphs remain valid when the game's art
  direction explicitly calls for them and runtime proof shows the intended result. The check does
  not outlaw concept-driven typography.
- **Capture with missing raster layers:** the capture is rejected as verification evidence; it
  cannot approve the product merely because the Flutter shell rendered.
- **Runtime unavailable:** source and widget findings may still be reported, but the overall verdict
  is `RUNTIME PENDING`, never `PASS`.

## Preserved invariants

The change does not alter RNG, mathematical-model, compliance, mobile-baseline,
expanded-viewport, or user-scope requirements. Human review and merge remain required.

## Validator note

The skill-creator quick validator could not start in this environment because its optional
`yaml` Python module is not installed. Repository-native validation therefore checks the unchanged
frontmatter, required contract language, linked documentation, proposal scope, and whitespace.
