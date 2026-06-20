# Legacy Map

Status: completed by M001.

This repository is a useful prototype and implementation seed, but the existing Python object model is not the final GSP protocol authority. Future agents should follow the authority order in `AGENTS.md`: charter, architecture, spec files, ADRs, then this map, then source code.

## Summary

The current codebase implements an object-oriented scene API with renderer adapters for Matplotlib, Datoviz, a JSON/HTTP network path, and a small `vispy2` plotting layer. It is best reused as working renderer knowledge, example coverage, visual-family vocabulary, transform math, and test fixtures. It should not be treated as the final session protocol, resource model, capability model, or extension model.

## Directory Classification

| Path | Classification | Reuse guidance |
|---|---|---|
| `src/gsp/` | keep and refactor | Mine and refactor core concepts: `Canvas`, `Viewport`, `Camera`, `Texture`, `Buffer`, `TransBuf`, visual classes, transform chain utilities, unit/color/group helpers, and UUID handling. Replace ad hoc object mutation with explicit protocol/session commands as M002 evolves. |
| `src/gsp_matplotlib/` | keep and refactor | Treat as the reference backend seed. Reuse renderer-specific visual mapping, Matplotlib artist lifecycle patterns, point/image/path/mesh/text implementations, PNG output behavior, and converter utilities. Adapt it to consume formal GSP models after M002 rather than current object classes directly. |
| `src/gsp_datoviz/` | mine for ideas | Use as Datoviz API reconnaissance and adapter seed. It contains practical panel/visual/texture mappings and Datoviz offscreen caveats, but targets `datoviz >=0.3.2,<0.4.0` and uses private Datoviz imports in places, so M004 must reassess against Datoviz v0.4 before implementation. |
| `src/gsp_pydantic/` | mine for ideas | Useful for JSON fixture shape, Pydantic schemas, and current scene serialization. Do not preserve base64-heavy serialization as the default local path. Reuse only for debug-json fixtures, replay, network compatibility, and schema migration ideas. |
| `src/gsp_network/` | legacy only for now | Demonstrates an HTTP render server/client around `PydanticSerializer`, but it is a renderer remoting experiment rather than the final session protocol. Mine endpoint flow and failure modes later when designing remote transports. |
| `src/gsp_extra/` | mine for ideas | Contains helpers for buffers, camera controls, object/mesh utilities, MPL3D experiments, and transform links. Reuse selectively after ownership is clarified; avoid importing this as a dependency layer in protocol code. |
| `src/vispy2/` | keep and refactor | Important seed for the future high-level Python producer API: `plot`, `scatter`, `imshow`, and axes helpers. Keep the user-facing ergonomic lessons, but route future output through formal GSP producer/session models rather than directly constructing legacy visuals. |
| `docs/` | mine for ideas | Contains philosophy docs, API comparisons, personas, prompts, and notes. Use it as design history, not authority. Reconcile useful claims into `spec/**`, ADRs, or mission files before treating them as requirements. |
| `mkdocs_source/` and `mkdocs_build/` | mine for ideas / delete generated later | `mkdocs_source/` is useful documentation source. `mkdocs_build/` appears generated and should not be a design authority; consider cleaning generated output in a later housekeeping mission. |
| `examples/` | keep as behavioral fixtures | Strong source of visual coverage and expected workflows across buffers, groups, images, meshes, network, pydantic cycles, transforms, viewports, and VisPy2 helpers. Future missions should convert focused examples into conformance fixtures rather than running all examples as broad regression tests. |
| `tests/` | keep and expand | Only `test_buffer.py` and `test_mesh_textured_material.py` exist. Keep them, but coverage is far too small for protocol work. M002-M003 should add focused model/renderer tests around new protocol objects and point/image fixtures. |
| `.claude/` | mine for ideas | Contains prior analysis notes for text rendering, scatter, imshow, and alignment. Use as background only; promote durable conclusions into specs or ADRs before implementation. |
| `tmp/` | unknown/requires review | Appears to contain experimental Datoviz, Matplotlib, DPI, and pyramid work. Do not rely on it without manual review. Consider deletion or archival in a later cleanup mission. |
| `my_doc/` | unknown/requires review | Looks like duplicate or legacy documentation material. Review before reuse; avoid treating it as authoritative. |

## Package Notes

### `src/gsp/`

Important reusable concepts:

- `core/`: current canvas, viewport, camera, texture, and event objects.
- `types/`: buffer types, renderer/serializer bases, visual base, color/enums, groups, and viewport event types.
- `visuals/`: visual-family vocabulary for image, markers, mesh, paths, pixels, points, segments, and texts.
- `transforms/`: transform chains and registry mechanisms.
- `utils/`: math, grouping, unit, colormap, buffer, and UUID helpers.

Risks:

- The model is an in-memory object graph, not a session protocol.
- Mutable setters and direct class references should not become protocol semantics by accident.
- Some utility duplication is visible, for example multiple `math_utils` variants and copied files.
- The current render call couples viewports, visuals, model matrices, and cameras by parallel sequences; M002 should replace this with explicit IDs, resources, and command batches.

### `src/gsp_matplotlib/`

Important reusable concepts:

- `MatplotlibRenderer` creates figures, maps viewports to axes, caches artists per viewport/visual key, and returns PNG bytes.
- Per-visual renderer modules show concrete Matplotlib mappings for points, images, pixels, paths, markers, meshes, segments, and texts.
- Converter utilities encode color and coordinate adaptation knowledge.

Risks:

- It performs CPU-side MVP transforms before calling Matplotlib; future semantics should clarify where transforms are applied.
- It consumes legacy classes directly.
- It is a reference renderer, not the source of protocol truth.

### `src/gsp_datoviz/`

Important reusable concepts:

- `DatovizRenderer` maps GSP canvas/viewports to Datoviz app/figure/panels and caches Datoviz visuals/textures.
- Per-visual renderer modules document practical Datoviz calls and gaps.
- Offscreen screenshots and clearing behavior already have caveats worth preserving for M004.

Risks:

- The dependency currently targets Datoviz pre-0.4.
- Some imports use private Datoviz modules such as `_panel`, `_figure`, and `_texture`.
- Query/readback and capability discovery are not yet first-class.

### `src/gsp_pydantic/` and `src/gsp_network/`

Important reusable concepts:

- Existing Pydantic scene structure can seed debug-json fixtures.
- Network renderer/server flow can inform later remote transport work.

Risks:

- The current serializer encodes buffers as base64 and should not define the fast local path.
- The network layer sends full render requests, not incremental session commands.

### `src/vispy2/`

Important reusable concepts:

- `plot`, `scatter`, and `imshow` show the desired high-level API direction.
- Format parsing and visual generation logic are useful producer-side behavior.
- Axes modules provide experience around managed axes, pan/zoom, display, and tick helpers.

Risks:

- Current functions create legacy `gsp.visuals` directly.
- Axes/navigation semantics need alignment with the future controller and query models.

## Recommended Mission Inputs

### M002 Protocol Spine

Use these legacy inputs:

- `src/gsp/types/buffer.py`, `buffer_type.py`, `transbuf.py`
- `src/gsp/types/visual_base.py`
- `src/gsp/core/canvas.py`, `viewport.py`, `camera.py`, `texture.py`
- `src/gsp_pydantic/types/pydantic_types.py`
- `src/gsp_pydantic/serializer/pydantic_serializer.py`

Expected output should be a minimal protocol model that can coexist beside the legacy object graph. Do not rewrite renderers in M002 unless the mission is explicitly expanded.

### M003 Matplotlib Point/Image Slice

Use these legacy inputs:

- `src/gsp_matplotlib/renderer/matplotlib_renderer.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_points.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_image.py`
- `examples/points_example.py`
- `examples/image_example.py`
- `examples/expected/`

Focus on small conformance fixtures and keep Matplotlib as the reference backend.

### M004 Datoviz v0.4 Assessment

Use these legacy inputs:

- `src/gsp_datoviz/renderer/datoviz_renderer.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_points.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_image.py`
- Datoviz-related examples under `examples/`

Do not port code blindly. First compare the current imports and calls against Datoviz v0.4 public APIs and document gaps.

## Cleanup Candidates For Later

Do not delete these in M001. Consider a separate housekeeping mission for:

- generated documentation output in `mkdocs_build/`;
- experimental `tmp/` content;
- duplicate `README copy.md`;
- duplicate or obsolete math utility copies under `src/gsp/utils/`;
- reviewed migration or archival of `.claude/` notes and `my_doc/`.
