# M008 - VisPy2 producer MVP

## Goal

Add a minimal VisPy2 user-facing producer API that creates GSP scenes using the current protocol models and renders through the Matplotlib reference backend.

The MVP should prove that VisPy2 can be a high-level Python producer of GSP calls without becoming the protocol authority.

## State

Completed.

## Required reading

- PROJECT_CHARTER.md
- ARCHITECTURE.md
- spec/vispy2/api.md
- spec/protocol.md
- spec/visuals/point.md
- spec/visuals/image.md
- spec/backends/matplotlib.md
- LEGACY_MAP.md
- Existing src/vispy2/ files

## Expected tasks

- Define minimal VisPy2 API:
  - figure/subplots or equivalent;
  - scatter;
  - imshow;
  - show/render via Matplotlib protocol renderer;
  - optional savefig if already supported.
- Ensure VisPy2 emits GSP protocol objects, not backend-specific calls.
- Add examples:
  - scatter;
  - imshow;
  - point-over-image.
- Add tests ensuring VisPy2 output can be rendered by Matplotlib protocol renderer.
- Do not implement Datoviz-specific VisPy2 behavior yet.
- Do not claim Matplotlib compatibility beyond the explicit MVP.

## Allowed paths

- src/vispy2/
- tests/
- examples/
- spec/vispy2/api.md
- docs/ if needed
- .agent/status.json
- STATUS.md

## Forbidden paths

- src/gsp_datoviz/
- ../datoviz/
- Major changes to src/gsp/ protocol models unless a task explicitly requires it
- Full Matplotlib compatibility layer
- Extension/data-source architecture

## Acceptance criteria

- Minimal VisPy2 scatter/imshow examples exist.
- Tests prove VisPy2 emits GSP objects renderable by Matplotlib protocol renderer.
- No backend-specific Datoviz assumptions enter VisPy2.
- Documentation clearly labels the API as MVP/experimental.
- All tests pass.

## Stop conditions

Stop and create a consultation packet if:

- the API design expands toward full Matplotlib compatibility;
- the producer API needs new protocol concepts not covered by M006;
- there is disagreement between existing src/vispy2 sandbox and new GSP-first design.

## Notes

This is the first user-facing proof. Keep it small.
