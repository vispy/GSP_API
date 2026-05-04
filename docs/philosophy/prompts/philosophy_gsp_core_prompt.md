## Prompt
i would like to document the GSP core package in ./src/gsp
- describe the architecture of this package
- its design phylosophy
- each of the core concept: Buffer, Visual, Transform
- its relations with other packages

Any other sections you may find relevant

## Plan

---

# Plan: Document the GSP core package

## Context

`/Users/jetienne/work/GSP_API/src/gsp/` is the contract layer of the GSP_API ecosystem — the abstract protocol that the three rendering backends (`gsp_matplotlib`, `gsp_datoviz`, `gsp_network`) and three convenience layers (`gsp_extra`, `gsp_pydantic`, `vispy2`) all build on. Two companion docs already exist:

- [philosophy_packages.md](../../work/GSP_API/docs/philosophy/philosophy_packages.md) — covers the seven-package split, with §3.1 a one-page sketch of `gsp`.
- [philosophy_renderers.md](../../work/GSP_API/docs/philosophy/philosophy_renderers.md) — covers backends and the `RendererBase` contract.

What's missing is a focused, internal-perspective document about `gsp` itself: the architecture inside the package, its design philosophy, and the three load-bearing concepts the user named (Buffer, Visual, Transform). The existing §3.1 is a stub; this doc replaces it with a full treatment.

**Scope note from the user.** Skip Mesh — exclude `Mesh` from the visuals catalogue and exclude `MeshGeometry` / `Material` / `MeshBasicMaterial` from the architecture tour. Document the remaining seven visuals (Points, Markers, Pixels, Paths, Segments, Texts, Image) and the bare `Geometry` base if relevant, but do not give Mesh/Material their own sections.

**Audience.** A contributor opening `src/gsp/` for the first time, or one who has read `philosophy_packages.md` and wants a deeper drill into the contract layer.

**Output file.** `/Users/jetienne/work/GSP_API/docs/philosophy/philosophy_gsp_core.md` (companion to `philosophy_gsp_core_prompt.md` — same naming pattern as `philosophy_packages.md` / `philosophy_packages_prompt.md`).

## Document outline

```
# Philosophy of the GSP Core Package

## 1. Preamble
   - What `gsp` is in one paragraph: the abstract contract layer
   - The "two-sentence rule" reused from philosophy_packages.md (each subpackage understandable alone)
   - Audience + verification recipe (grep for sibling imports = zero matches)

## 2. Design Philosophy (the "why")
   2.1 Contract, not implementation — zero rendering code, zero backend awareness
   2.2 Data, not commands — Visuals, Buffers, Geometry are inert containers; rendering is a separate verb
   2.3 Lazy data via TransBuf — every Buffer slot also accepts a TransformChain that runs at render time
   2.4 Self-registration over manifests — RendererRegistry / TransformRegistry let backends and links plug in by import
   2.5 Numpy + stdlib only — verifiable: `grep -rn "^from gsp_\|^import gsp_" src/gsp/` = empty

## 3. Architecture: the seven subpackages
   - Map of src/gsp/{core, types, visuals, transforms, geometry, materials, utils} + constants.py + __init__.py
   - One-paragraph each describing role + key exports + dependency direction
   - The internal dependency picture: types is the lowest layer; core/visuals/transforms/geometry depend on types; utils sits aside as helpers
   - The deliberate non-re-export of RendererBase / SerializerBase from gsp.types.__init__.py
     (circular-import avoidance — quote the comment at types/__init__.py:16-18)

## 4. Core Concept: Buffer
   - What Buffer is: typed 1-D array, immutable in count+type, mutable in content
     Source: src/gsp/types/buffer.py:13-30
   - The 12 BufferType variants (scalars, vectors, mat4, rgba8) — short table
     Source: src/gsp/types/buffer_type.py:15-36
   - Numpy bridge: BufferType.to_numpy_dtype() and from_numpy() — gsp/types/buffer_type.py:78-132
   - Note: Buffer is bytes-on-the-CPU; the numpy adapter Bufferx lives in gsp_extra (cross-package pointer)
   - Where Buffer is consumed: by every TransBuf slot on every Visual, Camera, Texture, Geometry

## 5. Core Concept: Visual
   - The data-not-command interpretation, with evidence:
     - VisualBase has no render() method (src/gsp/types/visual_base.py)
     - Rendering is in RendererBase.render(viewports, visuals, ...) — visuals are arguments, not actors
     - philosophy_packages.md §3.1 already labels visuals "data containers, not draw commands"
   - VisualBase shape: __slots__ = ["_uuid", "userData"]; UUID + userData metadata
     Source: src/gsp/types/visual_base.py:15-48
   - The seven visuals (Mesh skipped per scope):
     | Visual    | Adds                                                          | File                       |
     |-----------|---------------------------------------------------------------|----------------------------|
     | Points    | positions, sizes, face_colors, edge_colors, edge_widths       | src/gsp/visuals/points.py  |
     | Markers   | + marker_shape (enum)                                         | src/gsp/visuals/markers.py |
     | Pixels    | positions, colors, groups                                     | src/gsp/visuals/pixels.py  |
     | Paths     | positions, path_sizes, colors, line_widths, cap/join styles   | src/gsp/visuals/paths.py   |
     | Segments  | positions, line_widths, cap_style, colors                     | src/gsp/visuals/segments.py|
     | Texts     | positions, strings, colors, font_sizes, textAligns, angles    | src/gsp/visuals/texts.py   |
     | Image     | texture, position, image_extent, image_interpolation          | src/gsp/visuals/image.py   |
   - Universal pattern: every field accepts TransBuf; every visual has set_attributes / check_attributes / sanity_check_attributes
   - Anchor: `_render_visual()` in each backend dispatches by isinstance over these visual classes

## 6. Core Concept: Transform
   - The lazy-data motivation: a TransBuf slot is `TransformChain | Buffer` (src/gsp/types/transbuf.py:11)
   - TransformChain — ordered list of TransformLinkBase; .run() pipes Buffer through each link
     Source: src/gsp/transforms/transform_chain.py:18, .run() at 126-149
   - TransformLinkBase — three abstract methods: apply, serialize, deserialize
     Source: src/gsp/transforms/transform_link_base.py:16-48
   - TransformRegistry — string→class registry mirroring RendererRegistry, used for deserialization
     Source: src/gsp/transforms/transform_registry.py:26-51
   - Concrete links:
     - In-core: `TransformLinkImmediate` (returns a fixed Buffer)
     - In gsp_extra: `TransformLoad` (URI → Buffer)
   - Where the chain runs: backends call `TransBufUtils.to_buffer(trans_buf)` at render time
     (src/gsp/utils/transbuf_utils.py:17-30) — pass-through if Buffer, else `chain.run()`
   - Why this matters: chains are serialisable, so a scene can travel through gsp_pydantic / gsp_network and re-execute on the other side

## 7. The other contracts (one-paragraph each)
   - RendererBase — six abstract methods (cross-link to philosophy_renderers.md §4 rather than re-explain)
   - AnimatorBase — frame-loop contract; AnimatorFunc callback shape; on_video_saved Event
     Source: src/gsp/types/animator_base.py:17-104
   - ViewportEventsBase — seven public Event slots for keyboard / mouse / resize
     Source: src/gsp/types/viewport_events_base.py:13-51
   - SerializerBase — single serialize(...) method consumed by gsp_pydantic
     Source: src/gsp/types/serializer_base.py:15-51
   - The Event helper class — generic pub/sub, typed callbacks, .event_listener decorator form
     Source: src/gsp/core/event.py:10-69

## 8. The scene-graph containers (gsp.core)
   - Canvas: root surface — width, height, dpi, background_color
   - Viewport: rectangular sub-region of the canvas
   - Camera: view + projection matrices (both TransBuf)
   - Texture: pixel data (TransBuf) + dimensions
   - Event: generic pub-sub primitive used by ViewportEventsBase / AnimatorBase
   - All are pure data; no methods that draw or mutate render state

## 9. Value types and enums (gsp.types value layer)
   - Color (= bytearray alias), Groups (= int|list[int]|list[list[int]] alias)
   - Enums: MarkerShape, CapStyle, JoinStyle, TextAlign (IntEnum with v*10+h scheme), ImageInterpolation
   - One-line each, table form

## 10. Utils (gsp.utils — free functions and registries)
   - RendererRegistry — already covered in philosophy_renderers.md §6, recap in one paragraph + pointer
   - CmapUtils, GroupUtils, UnitUtils, ViewportUnitUtils, MathUtils, UuidUtils, LogUtils, TransBufUtils
   - One-line each
   - Constants module: FaceCulling enum + named Color presets

## 11. Relations with other packages
   - Reuse the dependency table from philosophy_packages.md §2.4 but pivot to "what gsp gives each consumer":
     - gsp_matplotlib / gsp_datoviz / gsp_network → subclass RendererBase + AnimatorBase + ViewportEventsBase, register triad
     - gsp_pydantic → walks the data tree; subclasses SerializerBase
     - gsp_extra → builds Object3D, Bufferx, camera controls *on top of* the abstract types
     - vispy2 → builds the matplotlib-like facade on `gsp` + `gsp_extra`
   - The contract surface a consumer touches is small — point at the abstract bases as the documented seam
   - Verification: `grep -rn "^from gsp_\|^import gsp_" src/gsp/` returns nothing

## 12. Verification checklist
   - Mirror philosophy_packages.md §7 / philosophy_renderers.md §9 — every claim grounded in a grep or file pointer:
     - `grep -rn "class.*VisualBase" src/gsp/visuals/` → seven matches (Mesh skipped from doc, but the grep will still find eight)
     - `grep -rn "TransformLinkBase" src/gsp/` → registry + base + immediate link
     - `grep -rn "TransBufUtils.to_buffer" src/` → confirms backends are the ones that actually run chains
     - `grep -rn "^from gsp_\|^import gsp_" src/gsp/` → empty (independence proof)
```

## Critical files referenced

- `/Users/jetienne/work/GSP_API/src/gsp/types/buffer.py` — Buffer
- `/Users/jetienne/work/GSP_API/src/gsp/types/buffer_type.py` — BufferType enum
- `/Users/jetienne/work/GSP_API/src/gsp/types/transbuf.py` — TransBuf alias
- `/Users/jetienne/work/GSP_API/src/gsp/utils/transbuf_utils.py` — chain execution adapter
- `/Users/jetienne/work/GSP_API/src/gsp/types/visual_base.py` — VisualBase
- `/Users/jetienne/work/GSP_API/src/gsp/visuals/{points,markers,pixels,paths,segments,texts,image}.py` — seven visuals (skip mesh.py)
- `/Users/jetienne/work/GSP_API/src/gsp/transforms/transform_chain.py` — TransformChain
- `/Users/jetienne/work/GSP_API/src/gsp/transforms/transform_link_base.py` — TransformLinkBase
- `/Users/jetienne/work/GSP_API/src/gsp/transforms/transform_registry.py` — TransformRegistry
- `/Users/jetienne/work/GSP_API/src/gsp/transforms/links/transform_link_immediate.py` — only in-core link
- `/Users/jetienne/work/GSP_API/src/gsp/types/{renderer_base,animator_base,viewport_events_base,serializer_base}.py` — abstract contracts
- `/Users/jetienne/work/GSP_API/src/gsp/core/{canvas,viewport,camera,texture,event}.py` — scene-graph containers
- `/Users/jetienne/work/GSP_API/src/gsp/utils/renderer_registery.py` — registry (recap; full coverage in philosophy_renderers.md)
- `/Users/jetienne/work/GSP_API/src/gsp/types/__init__.py:16-18` — the deliberate non-re-export comment
- `/Users/jetienne/work/GSP_API/src/gsp/constants.py` — Constants.Color and Constants.FaceCulling

## Style and conventions to match

- Same tone as `philosophy_packages.md` and `philosophy_renderers.md`: numbered top-level sections, terse markdown tables, `file.py:line` references rendered as relative-path markdown links (e.g. `[buffer.py:13](../../src/gsp/types/buffer.py#L13)`), grep recipes inline, short quoted code snippets
- 8 top-level numbered sections plus a verification appendix
- Avoid duplicating prose from the two existing docs — link to them where they cover the topic better (registry mechanics, render contract, backend dispatch)
- No emojis. No filler. Every section ends with a way to verify the claim against the code

## Verification (how to test the deliverable)

1. Read the produced doc top-to-bottom; every cited file:line should resolve in the editor.
2. Run the four grep recipes from §12; outputs should match the document's claims.
3. Cross-check: open the existing `philosophy_packages.md` §3.1 (the gsp stub) and confirm the new doc subsumes it without duplicating its content one-for-one — they should be readable together, not redundantly.
4. Confirm Mesh is absent from §5 visuals table and §3 architecture map (per user's "skip the mesh" instruction).
