# Store panorama CLI review

## Source and workflow findings

- The user again specified a single generated panorama with gameplay captures used only as visual context. The current skill already states this, while the compositor still offered a `boardplate --from-shot` route and `triptych --sprite ...@board` inlay before writing panels.
- `cmd_triptych` now refuses both sprite input options before loading or writing art. Its export path grades, crops, checks and slices the supplied complete scene; it does not call the inlay helper.
- The CLI no longer advertises board construction. A legacy `boardplate` invocation routes to a retirement message. The internal renderer remains for old direct callers but is not connected to the store export command.
- The store skill names the retired route and directs both captures and shipped sprites into image generation as references. Its topology, outcome and final visual review requirements remain in force.
- Showcase slides still use real gameplay captures, and the feature graphic still places one real capture inside its framed phone. This change applies to carousel panorama panels only.

## Limit

No artwork was generated or visually reviewed in this proposal. A store kit still needs a scene-by-scene comparison with its actual runtime capture before delivery. Static composition gates cannot prove that a generated board preserves the true topology or outcome.
