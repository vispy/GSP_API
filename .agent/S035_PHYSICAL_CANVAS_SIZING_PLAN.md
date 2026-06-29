# S035 Physical Canvas Sizing Plan

Status: planning handoff, no implementation started.

Decision sources:

- `.agent/consultations/P018-physical-canvas-size-contract.md`
- `ANSWER`
- Live investigation of `DVZ_WINDOW_SIZE_SCALE` and marker-size parity
- Existing S034 layout work through `M145-s034-dataviz-grid-clip-unsupported.md`

The next available mission id appears to be `M146`. Do not reuse `M133`; that id is already used by S034.

## Problem

Matplotlib and Datoviz currently conflate at least four coordinate/size spaces:

- GSP canvas/reference px: semantic screen units for marker diameters, text sizes, stroke widths, guide offsets, and similar `_px` protocol fields.
- Host/window logical px: units accepted by the OS/window toolkit, such as GLFW window content size.
- Framebuffer px: actual device pixels used by GPU surfaces, screenshots, and image output.
- Physical units: mm/inches on a display, approximate for live windows and deterministic for export math.

`DVZ_WINDOW_SIZE_SCALE=1.45` masks one symptom by enlarging Datoviz live windows, but it is the wrong abstraction. It scales the host window extent without defining a coherent canvas/reference-px contract or scaling all `_px` visual attributes consistently. This creates live-window discrepancies such as marker sizes no longer matching Matplotlib, even when offscreen output can look close.

The user goal is not merely framebuffer parity. The goal is: a requested canvas such as `1280x720` should have approximately the same apparent physical size on macOS and Linux, both in GSP and in Datoviz standalone, while preserving deterministic offscreen/testing behavior.

## Architecture Target

Adopt an explicit size-policy model and a resolved canvas contract.

Public policies:

- `pixel_exact(width_px, height_px)`: deterministic framebuffer/output pixels; primarily tests, CI, screenshots, and offscreen exports.
- `host_logical_px(width, height)`: direct OS/toolkit logical window units; this is the explicit low-level version of current live-window behavior.
- `reference_px(width, height, reference_dpi=96)`: CSS-like physical target; `1280x720` means `1280 / reference_dpi` by `720 / reference_dpi` inches.
- `physical_mm(width_mm, height_mm, reference_dpi=96)`: direct physical target; the canvas/reference-px extent is derived from physical size and `reference_dpi`.

Resolved contract:

- `canvas_width_px`, `canvas_height_px`
- `host_logical_width`, `host_logical_height`
- `framebuffer_width`, `framebuffer_height`
- `device_scale_x`, `device_scale_y`
- `canvas_to_host_scale_x`, `canvas_to_host_scale_y`
- `framebuffer_per_canvas_px_x`, `framebuffer_per_canvas_px_y`
- target and estimated physical dimensions
- metrics source, exactness/warnings, strictness result

Core rule:

> Visual `_px` attributes are authored in GSP/Datoviz canvas/reference pixels, not raw framebuffer pixels and not backend-specific host logical pixels.

Every backend must lower marker sizes, text sizes, line widths, antialiasing radii, and guide offsets through the resolved `framebuffer_per_canvas_px` scale.

## User Knobs

`reference_dpi` is the correct user-facing knob for how physically large a reference pixel should be on a setup. Default to `96`, matching CSS-like semantics. Lower values make a given reference-px canvas physically larger; higher values make it physically smaller.

`user_scale` or `style_scale` must remain a visual styling multiplier inside an already resolved canvas. It should scale markers/text/strokes/offsets, not the requested window or canvas physical size. If the existing Datoviz `user_scale.c` example already demonstrates style scaling, keep it and cross-link it rather than creating redundant examples.

Optional advanced overrides:

- monitor DPI override for broken EDID/toolkit physical metrics
- requested device scale for tests/headless/debugging
- strict framebuffer size for live `pixel_exact`

These overrides should not replace the semantic size policies.

## API Breaks Allowed

The user explicitly approved aggressive refactor and API breakage.

Required removals:

- Delete all uses of `DVZ_WINDOW_SIZE_SCALE` from Datoviz.
- Delete the variable from repo-local and sibling `.envrc` files where present:
  - `../.envrc` currently contains `export DVZ_WINDOW_SIZE_SCALE=1.45`.
  - `./.envrc` was not found during initial inspection.
  - `../datoviz/.envrc` exists but did not appear to contain the variable.
  - Recheck before editing because these are outside the GSP repo.

Do not preserve hidden compatibility behavior around `DVZ_WINDOW_SIZE_SCALE`. If a compatibility note is needed, document the replacement: use `reference_px(..., reference_dpi=...)` or `physical_mm(...)`.

## Datoviz Work

Suggested commits in `../datoviz`, each independently reviewable:

1. `Remove DVZ_WINDOW_SIZE_SCALE`
   - Remove env var parsing and any runtime scaling based on it.
   - Remove docs/tests mentioning it.
   - Clean allowed `.envrc` occurrences after rechecking paths.

2. `Add view size policy descriptors`
   - Add `DvzViewSizePolicy`, `DvzViewSizeDesc`, `DvzResolvedViewSize`.
   - Add helpers for default descriptors:
     - framebuffer/pixel exact
     - host logical px
     - reference px with default `reference_dpi=96`
     - physical mm with default `reference_dpi=96`
   - Keep naming explicit: prefer `HOST_LOGICAL_PX` over ambiguous `LOGICAL_PX`.

3. `Resolve live and offscreen canvas sizes`
   - Implement a resolver that maps request policy to host logical size, framebuffer size, canvas/reference size, and physical estimates.
   - Live `reference_px` should target physical size using monitor/toolkit metrics and report approximation.
   - Offscreen `pixel_exact` should produce exact framebuffer/output dimensions.
   - Offscreen `reference_px`/`physical_mm` should make raster DPI explicit.

4. `Expose resolved size metrics`
   - Add C query APIs for resolved view/canvas size.
   - Expose metrics through Python bindings.
   - Ensure diagnostics include metric source and exactness/warnings.

5. `Apply canvas scale to screen-space visuals`
   - Route marker sizes, text sizes, line widths, guide offsets, and similar pixel-valued attributes through `framebuffer_per_canvas_px`.
   - Keep data-space transforms separate from screen-space lowering.
   - Audit retained visuals and any direct shader push constants that assume framebuffer pixels.

6. `Add Datoviz size policy tests`
   - Unit-test resolver math with fake monitor DPI/device scale.
   - Add live diagnostics tests where feasible.
   - Add offscreen exactness tests.
   - Add visual parity smoke tests for marker/text/stroke sizing across size policies.

7. `Add/merge Datoviz examples and docs`
   - Add a compact CLI example, likely `view_size_policies.c`, with modes for `pixel_exact`, `host_logical_px`, `reference_px`, and `physical_mm`.
   - Keep `user_scale.c`; update it only to clarify style scale versus canvas/window size.
   - Do not create five separate examples for this. One CLI policy example plus existing `user_scale.c` is enough.
   - Update API docs, migration notes, and troubleshooting docs.

## GSP Work

Suggested commits in this repo after the Datoviz contract exists, each independently reviewable:

1. `Document physical canvas sizing decision`
   - Add ADR/spec entry for the four-space model, size policies, and resolved canvas contract.
   - Reference P018/ANSWER as decision provenance if appropriate.
   - Update `SPEC_INDEX.md`.

2. `Add CanvasSize and ResolvedCanvas protocol models`
   - Add public `CanvasSize` constructors:
     - `pixel_exact`
     - `host_logical_px`
     - `reference_px`
     - `physical_mm`
   - Add `ResolvedCanvas`.
   - Add validation around positive sizes, `reference_dpi`, strictness, and override semantics.

3. `Refactor Matplotlib backend size resolution`
   - Use Matplotlib figure inches and DPI deliberately.
   - Formula for exports/live figures:
     - target inches from `reference_px`: `width / reference_dpi`, `height / reference_dpi`
     - figure size inches set from physical target
     - framebuffer/output px from figure inches times Matplotlib DPI
   - Lower visual `_px` to points with:
     - `points = canvas_px * framebuffer_per_canvas_px * 72 / output_dpi`
   - Ensure marker area/diameter semantics remain correct for Matplotlib's marker APIs.

4. `Refactor Datoviz backend size adapter`
   - Map GSP `CanvasSize` requests to Datoviz `DvzViewSizeDesc`.
   - Read back `DvzResolvedViewSize`.
   - Store resolved metrics in render results/query snapshots.
   - Scale GSP visual `_px` attributes through the resolved contract instead of ad hoc backend assumptions.

5. `Update review runners and examples`
   - Make examples request explicit canvas size policies.
   - Default review examples should use `reference_px(1280, 720, reference_dpi=96)` for live physical comparability unless they are deterministic image tests, which should use `pixel_exact`.
   - Keep examples dense and practical; no marketing-style pages or redundant examples.

6. `Add GSP tests and visual QA`
   - Unit-test policy validation and resolved canvas math.
   - Backend tests for Matplotlib DPI conversion and Datoviz adapter mapping.
   - Visual parity fixtures comparing Matplotlib/Datoviz marker, text, stroke, and guide sizes.
   - Include fake device-scale scenarios such as 1.0, 1.25, 1.45, 2.0.

7. `Update GSP docs`
   - Explain physical canvas size, framebuffer size, and host logical size separately.
   - Explain `reference_dpi` as the user's physical-size knob.
   - Explain `user_scale`/`style_scale` as visual styling only.
   - Add migration notes from older width/height behavior and from `DVZ_WINDOW_SIZE_SCALE`.

## Cross-Repo Commit Sequence

Recommended high-level sequence:

1. Datoviz: remove `DVZ_WINDOW_SIZE_SCALE`.
2. Datoviz: add request/resolved types.
3. Datoviz: implement resolver and expose metrics.
4. Datoviz: route screen-space visuals through resolved scale.
5. Datoviz: tests/docs/examples.
6. GSP: spec/ADR for physical canvas sizing.
7. GSP: protocol models and validation.
8. GSP: Matplotlib implementation.
9. GSP: Datoviz implementation against new Datoviz API.
10. GSP: examples/docs/tests/visual QA.
11. Cross-repo: render review pack and compare live/offscreen behavior.

Avoid interleaving GSP Datoviz adapter work before the Datoviz resolved metrics API is usable, except for stubs guarded by capability checks.

## Validation Gates

Datoviz:

- Build and test C library.
- Python bindings import and expose size descriptors/resolved metrics.
- Offscreen `pixel_exact(1280,720)` produces exact `1280x720`.
- Live `reference_px(1280,720,96)` reports target physical size and resolved host/framebuffer sizes.
- Marker/text/stroke visual sizes remain stable relative to canvas/reference px under device-scale changes.

GSP:

- `uv run pytest` targeted tests for canvas policy and both backends.
- `uv run mypy ... --strict` on touched modules.
- Review examples render side-by-side for Matplotlib and Datoviz.
- Visual QA includes marker-size parity case that originally exposed the discrepancy.
- Render results include resolved canvas metrics for debugging.

Manual review:

- On macOS Retina and Linux HiDPI, live `reference_px(1280,720,96)` should have approximately the same physical window size.
- On both platforms, visual `_px` attributes should look the same relative to the canvas.
- For deterministic PNGs, use `pixel_exact`, not `reference_px`.

## Mission-Control Setup For Next Conversation

Recommended new stage: `S035 Physical canvas sizing`.

Recommended mission ids, subject to `tools/agentctl` state at the time:

- `M146-s035-dataviz-window-scale-removal`
- `M147-s035-dataviz-view-size-policy-contract`
- `M148-s035-dataviz-resolved-size-runtime`
- `M149-s035-dataviz-screen-space-scale-lowering`
- `M150-s035-dataviz-tests-docs-examples`
- `M151-s035-gsp-canvas-size-spec`
- `M152-s035-gsp-canvas-size-protocol`
- `M153-s035-gsp-matplotlib-size-resolution`
- `M154-s035-gsp-dataviz-size-adapter`
- `M155-s035-gsp-review-examples-and-docs`
- `M156-s035-cross-backend-visual-qa`

Before launching workers, run:

```bash
tools/agentctl brief
tools/agentctl next
tools/agentctl mission list
tools/agentctl task list
```

Then create/approve S035 missions using the agent-control workflow. This plan is the current handoff source.

## Resume Prompt

Use this prompt in the next conversation:

```text
Continue from .agent/S035_PHYSICAL_CANVAS_SIZING_PLAN.md. Use Mission Control. Create the S035 mission/task files for the physical canvas sizing refactor, starting at the next available mission id after the existing S034 missions. Do not implement yet unless I approve the missions. The plan must cover Datoviz first, then GSP, and must remove DVZ_WINDOW_SIZE_SCALE entirely.
```
