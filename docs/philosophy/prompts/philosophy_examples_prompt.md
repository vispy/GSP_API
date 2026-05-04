# Prompt Examples Philosophy: Common Patterns and Principles
Look at all the example in ./examples
- extract the common patterns and the phylosophy behind it
- generate a documents explaining it

## Result

---

# Plan: Document the philosophy and common patterns of GSP_API examples

## Context

The `examples/` directory contains 50+ scripts that have grown organically over months and now constitute the de-facto user-facing tutorial surface for GSP_API. There is no single document explaining the conventions every example follows, so a new reader has to reverse-engineer the canonical structure (canvas → viewport → buffers → visual → camera → renderer → save+show) by reading several files. The task is to produce a single, detailed reference that names the patterns, explains *why* the API is shaped this way, and gives readers a mental model strong enough to write a new example from scratch.

The document goes to `docs/examples_philosophy.md` (alongside `docs/whitepaper/` and `docs/api_comparison/`). Target depth is a **detailed pattern catalog (~600 lines)** with code excerpts and cross-references to specific example files.

## Sources of truth (what was read)

Verified directly:
- [examples/README.md](examples/README.md) — existing high-level index
- [examples/points_example.py](examples/points_example.py) — canonical small visual
- [examples/common/example_helper.py](examples/common/example_helper.py) — `ExampleHelper` factory
- `examples/common/` directory listing (asset_downloader, big_tester_helper, example_helper)
- `docs/` directory listing — confirms the destination tree

Surveyed via Explore agents (findings in conversation, files not all individually re-read by me):
- Basic visuals: `markers_example.py`, `segments_example.py`, `paths_example.py`, `pixels_example.py`, `image_example.py`, `texts_example.py`, `buffer_example.py`, `transform_example.py`, `transform_build_sample.py`, `_mesh_example.py`
- Viewports/axes/cameras: `viewport_*_example.py`, `camera_control_example.py`, `vispy_basic_example.py`, `vispy_imshow_example.py`, `vispy_axes_*_example.py`, `simple_model_matrix.py`, `object3d_example.py`
- Advanced: `animator_example.py`, `groups_example.py`, `dynamic_groups_example.py`, `texts_animated_example.py`, `session_record_example.py`, `session_player_example.py`, `transform_serialization_example.py`, `transform_visual_example.py`, `pydantic_cycle_example.py`, `network_client_example.py`, `svg_pdf_example.py`

## Approach

Create one new file: `docs/examples_philosophy.md`. No code changes, no edits to existing examples or sources.

Verification before publishing:
- Re-open 1–2 of the agent-reported files I didn't read myself (e.g. `animator_example.py`, `viewport_multi_example.py`, `object3d_example.py`) to confirm the snippets I quote actually appear there. Adjust wording if the agent paraphrased.
- Confirm `GSP_BACKEND` vs `GSP_RENDERER` — `examples/README.md` says `GSP_BACKEND`, but `ExampleHelper.get_renderer_name()` reads `GSP_RENDERER`. The doc must reflect the **code's** behavior (`GSP_RENDERER`) and call out the README inconsistency rather than propagate it.

## Document outline (`docs/examples_philosophy.md`)

### 1. Preamble (~30 lines)
- One-paragraph summary: examples are a teaching surface, every example follows the same skeleton, the skeleton encodes the library's design.
- Who this doc is for: someone reading examples to learn GSP, or writing a new example.
- How to use it: each section names a pattern, shows the canonical snippet, points to the example files that demonstrate it.

### 2. The Five Design Principles (~80 lines)
The "why" before the "what". Each principle gets a short paragraph and a concrete payoff.
1. **Backend independence** — same example runs under matplotlib, datoviz, or network; selection via `GSP_RENDERER`. Payoff: examples double as cross-backend conformance tests.
2. **Data first, render last** — buffers and visuals are pure data structures; rendering is a single terminal call. Payoff: scenes are inspectable, serializable, and renderer-swappable.
3. **Parallel-list rendering API** — `render([viewports], [visuals], [model_matrices], [cameras])`. One position per item. Payoff: composing N panels is the same code as composing one.
4. **Typed GPU buffers, not opaque arrays** — `Bufferx.from_numpy(arr, BufferType.vec3)` etc. Payoff: shape/type errors surface at construction, not deep in the renderer.
5. **Save + show, always both** — every example writes a PNG to `examples/output/` *and* opens an interactive window. Payoff: examples are CI-friendly and human-friendly with one code path.

### 3. The Canonical Skeleton (~70 lines)
The seven-step structure that ~every example follows, presented as an annotated `points_example.py` walkthrough:
1. Imports (stdlib, numpy, `common.example_helper`, `gsp.core`, `gsp.visuals`, `gsp.types`, `gsp_extra.bufferx`)
2. Canvas creation (`Canvas(width, height, dpi, background_color)`)
3. Viewport creation (`Viewport(x, y, w, h, background_color)`)
4. Data preparation (numpy → `Bufferx.from_numpy` for arrays; `Buffer(...).set_data(...)` for constant fills; `CmapUtils.get_color_map(...)` for gradients)
5. Visual instantiation (`Points(...)`, `Markers(...)`, etc. — buffers in, visual out)
6. Camera + model matrix (`Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())`, `Bufferx.mat4_identity()`)
7. Render + save + show (`ExampleHelper.create_renderer` → `render(...)` → `save_output_image` → `renderer.show()`)

Include the full `points_example.py` body inline as the reference template.

### 4. Pattern Catalog (~280 lines)
One subsection per pattern. Each subsection: 1-paragraph description, canonical snippet, list of example files that demonstrate it.

#### 4.1 Buffer construction patterns
- From numpy: `Bufferx.from_numpy(arr, BufferType.vec3)`
- Constant fill: `Buffer(count, BufferType.rgba8); buf.set_data(bytes_pattern * count, 0, count)`
- Colormap: `CmapUtils.get_color_map("plasma", normalized_values)`
- DPI-aware sizes: `UnitUtils.pixel_to_point(1, canvas.get_dpi())`
- Files: `points_example.py`, `markers_example.py`, `buffer_example.py`

#### 4.2 Multi-viewport composition
- Parallel-list pattern with N viewports, N visuals, N model matrices, N cameras
- Tile / overlap / stack layouts
- Files: `viewport_multi_example.py`, `viewport_overlapping_example.py`, `viewport_events_example.py`

#### 4.3 Interaction: ViewportEvents + AxesPanZoom
- `ExampleHelper.create_viewport_events(...)` → subscribe to `mouse_move_event`, `button_press_event`, `mouse_scroll_event`
- `AxesPanZoom(viewport_events, base_scale, axes_display)` as a reusable controller
- `new_limits_event` triggers re-render when axes limits change
- Files: `viewport_events_example.py`, `vispy_axes_panzoom_example.py`, `vispy_axes_multiple_panzoom_example.py`

#### 4.4 Axes layers (managed → display → panzoom)
- `AxesManaged` (auto-everything) for tutorial code
- `AxesDisplay` + `AxesPanZoom` (decoupled) for full control
- Files: `vispy_axes_managed_example.py`, `vispy_axes_display_example.py`, `vispy_axes_panzoom_example.py`

#### 4.5 3D scenes: manual matrices vs Object3D hierarchies
- Manual: `model_matrix = glm.zrotate(20.0)`
- Hierarchy: `Object3D` parent/child, `Object3D.pre_render(viewport, scene, camera)` flattens to parallel lists
- Files: `simple_model_matrix.py`, `object3d_example.py`, `camera_control_example.py`

#### 4.6 Animation: `@animator.event_listener`
- Callback receives `delta_time`, mutates buffers in place, returns the changed visuals only (delta rendering)
- `animator.start([viewport], [visual], [model_matrix], [camera])`
- Video export via `ExampleHelper.create_animator_with_video(...)`
- Files: `animator_example.py`, `texts_animated_example.py`, `dynamic_groups_example.py`

#### 4.7 Groups: index → attribute association
- `groups: list[list[int]]` maps vertex indices to attribute slots
- `visual.set_attributes(colors=color_buf, groups=groups)` for dynamic re-styling without recreating the visual
- Files: `groups_example.py`, `dynamic_groups_example.py`

#### 4.8 Sessions: timestamped Pydantic snapshots
- Recording: `PydanticSerializer(canvas).serialize(...)` per frame, accumulate into `gsp_session.items` with `relative_timestamp`
- Skip-redundant: equality check on serialized data avoids duplicate snapshots
- Playback: `PydanticParser().parse(...)` → `renderer.render(...)`
- Files: `session_record_example.py`, `session_player_example.py`

#### 4.9 Transforms and serialization
- `TransformChain.serialize()` / `TransformChain.deserialize()` — JSON-friendly data pipelines
- Pydantic full-scene serialization for round-trip
- Files: `transform_example.py`, `transform_build_sample.py`, `transform_serialization_example.py`, `transform_visual_example.py`, `pydantic_cycle_example.py`

#### 4.10 Vector and remote output
- Format-agnostic render: `renderer.render(..., image_format="svg" | "pdf" | "png")` (matplotlib renderer)
- Network rendering: `NetworkRenderer(canvas, "http://localhost:5000", "datoviz")` — same `render(...)` surface, scene goes over HTTP
- Files: `svg_pdf_example.py`, `network_client_example.py`

### 5. The `common/` Helpers Reference (~60 lines)
Inventory of what's in `examples/common/`, since these are central to every pattern above.

- **`ExampleHelper`** ([example_helper.py](examples/common/example_helper.py))
  - `get_renderer_name()` — reads `GSP_RENDERER` env var (note: README says `GSP_BACKEND`; the code says `GSP_RENDERER` — flag this discrepancy)
  - `get_remote_renderer_name()` — for the `network` renderer, picks the upstream backend
  - `create_renderer(name, canvas)` → `MatplotlibRenderer | DatovizRenderer | NetworkRenderer`
  - `create_animator(renderer)` / `create_animator_with_video(renderer, path, fps, duration)`
  - `create_viewport_events(renderer, viewport)`
  - `save_output_image(bytes, basename)` → writes to `examples/output/`
- **`Bufferx`** ([gsp_extra/bufferx](src/gsp_extra/bufferx.py)) — `from_numpy`, `to_numpy`, `mat4_identity`
- **`CmapUtils`**, **`TextureUtils`**, **`UnitUtils`** — colormap sampling, image loading, DPI-aware unit conversion
- **`asset_downloader.py`**, **`big_tester_helper.py`** — narrower helpers, called out briefly

### 6. Writing a New Example: A Checklist (~40 lines)
The "now you do it" section. Structured as a checklist that mirrors the canonical skeleton:
- [ ] One feature per file, named `<feature>_example.py`
- [ ] Module docstring explaining what's demonstrated
- [ ] `main()` function, `if __name__ == "__main__": main()` guard
- [ ] Use `ExampleHelper.create_renderer` — never instantiate `MatplotlibRenderer` etc. directly
- [ ] Both save and show — `save_output_image(...)` then `renderer.show()`
- [ ] Verify under both backends: `GSP_RENDERER=matplotlib python …` and `GSP_RENDERER=datoviz python …`
- [ ] Add an entry to the right table in `examples/README.md`

### 7. Appendix: Naming and Filename Conventions (~30 lines)
- Suffix `_example.py` is canonical
- Underscore prefix `_` marks experimental/internal (e.g. `_axes_image_pyramid_*`, `_mesh_dvz_manual.py`)
- `vispy_` prefix denotes axes-managed examples that exercise the axes/pan-zoom stack specifically
- Output goes to `examples/output/<example_stem>_<renderer_name>.png`

### 8. Verification & how to read this doc against the code (~20 lines)
For each pattern named, the doc lists at least one example file. To verify a claim, open that file. To run a pattern under both backends:

```bash
GSP_RENDERER=matplotlib python examples/<file>.py
GSP_RENDERER=datoviz python examples/<file>.py
```

Output PNGs land in `examples/output/`.

## Critical files

- **Create:** [docs/examples_philosophy.md](docs/examples_philosophy.md)
- **Reference (read-only) during writing:** [examples/README.md](examples/README.md), [examples/points_example.py](examples/points_example.py), [examples/common/example_helper.py](examples/common/example_helper.py), and the example files cited in each pattern subsection — open each one when drafting its subsection to confirm the snippet matches reality.
- **Do not modify:** anything else.

## Verification

This is a documentation deliverable, so verification is primarily manual:

1. **Snippet accuracy** — for each code excerpt in the doc, grep the cited example file to confirm the call appears verbatim (or near-verbatim with elision marked by `...`):
   ```bash
   grep -n "ExampleHelper.create_renderer" examples/*.py
   grep -n "@animator.event_listener" examples/animator_example.py
   grep -n "Object3D.pre_render" examples/object3d_example.py
   ```
2. **Env-var name** — confirm `GSP_RENDERER` (not `GSP_BACKEND`) is what the code actually reads:
   ```bash
   grep -rn "GSP_RENDERER\|GSP_BACKEND" examples/ src/
   ```
3. **File list completeness** — confirm every `*_example.py` in `examples/` appears in at least one pattern subsection or is explicitly noted as out-of-scope (e.g. underscore-prefixed experimental files):
   ```bash
   ls examples/*example*.py | wc -l   # compare against doc's reference count
   ```
4. **Render the doc** — open `docs/examples_philosophy.md` in a markdown previewer and confirm code blocks render, internal links resolve, and the table of contents (if added) matches sections.
5. **Smoke test the "writing a new example" checklist** — pick one cited example (e.g. `points_example.py`) and walk through the checklist; every box should be tickable. If not, the checklist is wrong.
