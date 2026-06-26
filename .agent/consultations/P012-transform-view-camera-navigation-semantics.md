# P012 - Transform, view, camera, and navigation semantics

Status: awaiting ChatGPT Pro response.

This needs ChatGPT Pro consultation.

## Why This Is Needed

S026 closed the current visual-family and scalar-color sequence. The next GSP lane should address
transform, view, camera, and navigation semantics because many deferred features depend on it:
mesh-local transforms, 3D camera behavior, instancing, query inverse transforms, richer data-space
axes, controller state, and future remote/WebGPU renderer parity.

This is architectural protocol work. Do not commit public transform, camera, view-controller,
navigation, layout, or query-inverse semantics until the response is pasted or committed and
converted into ADR/spec baselines. Implementation remains blocked pending that conversion.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

```text
You are an architecture reviewer for GSP_API, a Python research prototype for a backend-independent
Graphics Server Protocol (GSP) for scientific visualization.

Your task is to recommend a narrow, durable protocol stage for transform, view, camera, and
navigation semantics. This is a pre-implementation architecture review. Do not write implementation
code. The answer must be concrete enough for worker agents to create ADRs, specs, protocol
dataclasses/enums, validation tests, Matplotlib reference behavior, Datoviz capability gates,
VisPy2 producer APIs, visual QA fixtures, and query/readback tests without inventing protocol
semantics.

## Project principles

GSP should allow one semantic visualization description to target:

- fast local GPU rendering through Datoviz v0.4;
- reference/publication rendering through Matplotlib;
- remote renderers;
- future web/browser paths where available;
- extension/data-source systems for huge distributed datasets.

Non-negotiable principles:

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and uses a unified panel-query model.
7. Extensions are manifest-, version-, and capability-driven.
8. Huge datasets are virtual data sources, not ordinary eager buffers.
9. Datoviz v0.4 is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.
12. High-reasoning design work is captured in specs, ADRs, and task files.
13. Existing source code is implementation material, not protocol authority.

Authority order in this project:

1. PROJECT_CHARTER
2. ARCHITECTURE
3. SPEC_INDEX
4. accepted specs
5. accepted ADRs and decision records
6. legacy map
7. existing source code

If code and intended specs conflict, the design should stop and report instead of inventing a third
semantics.

## Accepted architecture baseline

The accepted architecture says GSP has this layered target:

VisPy2 / plotting APIs / domain libraries
  -> GSP producer API
    -> GSP session and protocol model
      -> backend adapters
        -> Matplotlib reference backend
        -> Datoviz v0.4 GPU backend
        -> future remote/web/specialized backends

The session model has servers that expose capabilities, accept scene/resource/visual commands,
execute frames, return query/readback results, and emit diagnostics.

The protocol semantics are independent from encoding. Supported transport classes include:

- in-process direct Python/ctypes/memoryview paths;
- binary IPC / shared memory / binary chunks;
- network remote commands plus server-side data fetch;
- debug-json fixtures and replay.

The local desktop path must not require JSON or base64.

The architecture already names transform creation/update as control-plane work. It proposes a
declarative staged transform model:

1. source/data transforms;
2. attribute transforms;
3. coordinate transforms;
4. controller/navigation transforms;
5. material/shading transforms;
6. query/readout inverse transforms.

Placement may be CPU, GPU, client-side, server-side, or backend-defined, but semantics must be
stable.

## Current completed stage sequence

Completed stages through S026:

| Stage | Title | Result |
|---|---|---|
| S001-S006 | control plane, protocol spine, Matplotlib slice, query proof, conformance hardening | Established protocol dataclasses, capability/adaptation model, Matplotlib reference path, and query baseline. |
| S007-S010 | Datoviz v0.4 adapter and provider hardening | Added bounded Datoviz point/image path, query handoffs, provider control plane. |
| S011 | Extensions and virtual data-source architecture proof | Added manifest/capability-driven extension and virtual data-source proof. |
| S012-S013 | Semantic guide API growth | Added strict tick resolver, AxisGuide/PanelTextGuide rendering, VisPy2 guide APIs. |
| S014-S016 | Datoviz binding/query parity | Refreshed Datoviz v0.4 evidence, query scopes/capabilities, Datoviz query/capture/runtime proof work. |
| S017-S018 | Extension/data-source hardening and conformance replay | Added tiled-source semantics, static manifest validation, replay harness, fixture schemas. |
| S019 | Packaging, docs, and examples | Cleaned package/import/docs surface and release checklist. |
| S020-S022 | Remote data/security pre-design and first source family | Added no-network security baseline, preconfigured-source resolver proof, HTTP `.npy` descriptor validation/mock fixtures. |
| S023 | Visual Families v1 and Manual Visual QA | Accepted Point, Marker, Segment, Path, Image visual families and visual QA foundation. |
| S024 | Text/Glyph Visuals v1 | Accepted public TextVisual only; glyph resources remain internal/deferred. |
| S025 | Mesh and 3D Geometry Visuals v1 | Accepted public MeshVisual only; strict 2D flat indexed triangles; 3D/normals/shading/query capability-gated. |
| S026 | Color Mapping, Colorbars, and Scalar Data Semantics | Accepted ColorScale, canonical named colormaps, explicit linear normalization, scalar image/point/marker encodings, semantic ColorbarGuide, scalar query payloads; Datoviz scalar image/point CPU pre-map exists; colorbar/marker/mesh gates remain. |

## Current accepted visual baseline

Accepted visual families:

| Family | Protocol model | Important accepted semantics |
|---|---|---|
| Point | PointVisual | finite 2D/3D positions; RGBA or scalar color encoding; sizes are rendered screen-pixel diameters; coordinate_space is NDC or DATA. |
| Marker | MarkerVisual | shaped markers; fill/stroke RGBA; scalar/per-marker pixel diameters; angles are radians; stroke width is screen pixels; scalar fill exists in protocol but Datoviz remains gated. |
| Segment | SegmentVisual | independent line segments; RGBA colors; widths are screen-pixel stroke widths; conservative cap enum. |
| Path | PathVisual | open polyline/subpath visual; path_lengths partition vertices; per-subpath RGBA and width; conservative cap/join/miter fields. |
| Image | ImageVisual | 2D scalar/RGB/RGBA arrays; extent; origin upper/lower; nearest/linear interpolation; scalar images may link to ColorScale. |
| Text | TextVisual | public TextVisual only; renderer-internal glyphs/atlases; strings plus finite 2D/3D anchor positions; screen-pixel font sizes; RGBA; generic font roles; radians rotation; explicit anchors; ASCII strict, Unicode capability-dependent; item-level query. |
| Mesh | MeshVisual | public MeshVisual only; inline indexed triangles; strict 2D flat uniform/per-face RGBA conformance; face-level query/readback for strict 2D; per-vertex color, 3D rendering/query, normals, shading, culling, alpha, materials, textures, resources, instancing, and advanced query are capability-gated or deferred. |

Cross-cutting accepted rules:

- Every visual has a stable protocol id.
- Numeric arrays are finite; positions are float32/float64 shape (N, 2) or (N, 3).
- RGBA arrays are uint8 [0,255] or float [0,1].
- Point/marker sizes, text font sizes, and stroke widths are logical screen pixels.
- CoordinateSpace values are currently NDC and DATA.
- Visual QA uses deterministic NDC fixtures over [-1,+1] where practical for backend comparisons.
- Datoviz maps NDC fixtures to a data-coordinate panel domain configured to [-1,+1] with equal
  aspect where available.
- Backend-native names, units, resource handles, material structs, and draw calls stay internal
  unless accepted as semantic GSP concepts.

## Accepted query/capability baseline

GSP has a unified panel-query model: "what rendered scene contribution is under this panel
coordinate?"

Query results carry identity, item/group/face/texel ids, visual/data coordinates, displayed RGBA,
value/readout payloads, and optional extension payloads.

Existing query payload examples:

- ImageVisual query reports texel coordinates, displayed RGBA, and source value.
- TextVisual query is item-level and uses `gsp.text-query@0.1`.
- MeshVisual query is face-level for strict 2D uniform/per-face RGBA and uses
  `gsp.mesh-query@0.1`.
- Scalar/color query uses `gsp.scalar-color-query@0.1`.
- Colorbar ramp query uses `gsp.colorbar-query@0.1` when supported.

Capabilities are explicit. Unsupported behavior should be accepted, simplified with diagnostic,
deactivated with diagnostic, or rejected with fatal diagnostic. Datoviz support must produce
structured unsupported reports rather than hidden fallback approximations.

## Datoviz and Matplotlib context

Matplotlib is the reference/conformance/publication backend. It has a rich transform stack, axes,
projection, and navigation ecosystem, but GSP must not copy Matplotlib object graphs blindly.

Datoviz v0.4 is the flagship GPU backend. It exposes retained scene/facade/raw APIs and GPU-oriented
visual transforms internally, but GSP must not expose Datoviz slot names, shader internals, or
private transform structs as public semantics.

Current Datoviz support:

- renders accepted point/marker/segment/path/image slices where facade symbols exist;
- supports bounded query/capture paths where runtime bindings expose them;
- CPU pre-maps finite eager scalar ImageVisual and PointVisual values to canonical RGBA8 while
  retaining source scalar data for semantic query payloads;
- keeps ColorbarGuide rendering/query, marker scalar fill, mesh face scalar colors, TextVisual,
  and advanced MeshVisual behavior capability-gated with structured diagnostics.

## Current VisPy2 producer state

VisPy2 is the high-level Python producer of GSP scenes. It currently exposes bounded APIs for:

- scatter -> PointVisual;
- markers -> MarkerVisual;
- segments -> SegmentVisual;
- path/plot -> PathVisual;
- imshow -> ImageVisual;
- text -> TextVisual;
- mesh -> MeshVisual;
- color_scale/colorbar -> ColorScale/ColorbarGuide;
- semantic guide methods for view limits, labels, title, ticks, and grid.

VisPy2 should target GSP, not Datoviz or Matplotlib directly.

## Why S027 should probably be transforms/views/cameras

After S023-S026, visual contracts are broad enough for useful scientific scenes, but there is no
accepted transform/view/controller model. This blocks or weakens:

- mesh-local transforms;
- instancing;
- 3D camera behavior and 3D mesh query semantics;
- query inverse transforms and readout coordinates;
- richer data-space axes;
- pan/zoom/navigation/controller state;
- future remote/WebGPU renderer parity;
- layout/colorbar placement precision;
- scalable source/data transforms.

The next stage should be narrow. It should avoid trying to solve every transform, layout, animation,
interaction, shader/material, and remote-renderer problem at once.

## Candidate S027 deliverables

Potential deliverables:

- accepted protocol vocabulary for transform spaces and transform nodes/resources;
- accepted split between data transforms, coordinate/view transforms, model/local transforms,
  camera/projection, and controller/navigation state;
- minimal 2D affine/view-limits model for existing data-space visuals and guide/query behavior;
- narrow 3D camera baseline for MeshVisual if safe, or explicit deferral;
- query inverse semantics: what coordinates and values must be reported after transforms;
- Matplotlib reference behavior for accepted transform subset;
- Datoviz capability gates and minimal runtime mapping;
- VisPy2 producer APIs for accepted transform/view/camera controls;
- visual QA fixtures for deterministic transformed scenes and queries.

## Design questions to answer

1. What should S027 define as public v1 concepts: `Transform`, `TransformRef`,
   `CoordinateSpace`, `ViewTransform`, `Camera`, `View2D`, `View3D`, `ControllerState`,
   `Projection`, `TransformStack`, or something else?
2. Which transform stages are in v1 and which are deferred? Consider source/data transforms,
   attribute transforms, visual-local/model transforms, data-to-panel/view transforms,
   camera/projection transforms, controller/navigation transforms, material/shading transforms,
   and query/readout inverse transforms.
3. Should S027 start with only 2D affine/data-view semantics, or include a minimal 3D camera for
   MeshVisual? If 3D is included, define exactly the narrow baseline and capability gates.
4. How should existing `CoordinateSpace.NDC` and `CoordinateSpace.DATA` evolve? Should more spaces
   be added now, or should they remain stable with transforms referenced separately?
5. Should transforms be inline on visuals, separate named resources, panel/view properties, or a
   combination? Recommend the smallest durable model.
6. What is the relationship between semantic guides (axes, ticks, grid, titles, colorbars) and
   view transforms? Which parts are conformance semantics and which are backend/layout policy?
7. What should query/readback report after transforms? Define required fields for source/data
   coordinate, visual-local coordinate, transformed coordinate, panel coordinate, depth/order,
   and inverse-transform diagnostics.
8. How should pan/zoom/navigation be represented? Is controller state part of protocol v1, or
   should S027 define only deterministic view state and defer interactive events/controllers?
9. How should transform placement be expressed in capabilities? Include CPU/GPU/client/server
   placement without making placement part of the semantic result.
10. What should Matplotlib be required to implement as the strict reference behavior?
11. What should Datoviz be allowed to claim, simplify, deactivate, or reject? Include diagnostic
    codes for unsupported transform/camera/projection/query-inverse cases.
12. What should VisPy2 expose in v1 without leaking Matplotlib transforms or Datoviz draw calls?
13. What fixture and QA cases are sufficient for v1? Include positive and negative cases.
14. What are the exact non-goals? Explicitly address general layout engines, animation timelines,
    arbitrary shader/material transforms, nonlinear/log transforms, CRS/geospatial transforms,
    categorical transforms, full event systems, constraints/auto-layout, 3D lighting/materials,
    and remote renderer scheduling.
15. What stop conditions should worker agents follow if backend behavior or existing code conflicts
    with the accepted model?

## Required output format

Respond with these sections.

### 1. Recommendation Summary

Give 5-12 concrete bullets with the strategic sequencing for S027.

### 2. Accepted S027 Scope

Provide a table:

| Concept | Include in S027? | Public protocol shape | Why / notes |

Include at least: transform resources, inline visual transforms, View2D, View3D/camera, projection,
controller/navigation state, query inverse, guide interaction, transform capabilities.

### 3. Protocol Model

Define the exact recommended dataclasses/enums at the conceptual level. For each, list fields,
required/optional status, validation rules, and defaults.

Do not write implementation code. Be concrete enough that a worker can implement the dataclasses.

### 4. Coordinate Spaces And Transform Order

Define:

- accepted coordinate spaces;
- transform order from source/visual data to panel/framebuffer;
- how NDC and DATA existing visuals map into the new model;
- how query inverse/readout maps back.

### 5. Query/Readback Semantics

Define required and optional query fields and extension payloads for transformed visuals. Include
failure/unsupported diagnostics.

### 6. Backend Requirements

Split into:

- Matplotlib strict reference requirements;
- Datoviz capability-gated requirements;
- behavior for remote/web renderers.

### 7. VisPy2 Producer API

Recommend a minimal public VisPy2 API shape for accepted S027 behavior. State what must remain
private or deferred.

### 8. Visual QA And Conformance Fixtures

List deterministic QA cases and negative validation fixtures. Include expected artifact/report
behavior.

### 9. ADR/Spec Updates

List exact ADR/spec files that should be created or updated and what each should contain.

### 10. Mission Breakdown

Provide mission-sized tasks starting at M099, with this table:

| Mission | Title | Goal | Deliverables | Acceptance | Stop Conditions |

Assume M098 already created this consultation packet. Include ADR/spec, protocol validation,
Matplotlib reference, Datoviz capability gates, VisPy2 API, QA fixtures, and closeout missions.

### 11. Non-Goals And Boundaries

List explicit do-not-do rules for S027. Be strict about avoiding scope creep.

### 12. Open Questions

Separate:

- questions that truly require human decision;
- questions agents can answer by inspecting code or backend examples.

Be concrete. Prefer implementable contracts and mission acceptance criteria over abstract guidance.
```

## Expected Handling

- Paste the exact prompt above into ChatGPT Pro.
- Commit the response as `.agent/consultations/P012-response.md` or paste it back into Mission
  Control.
- Do not implement S027 protocol objects until the response is converted into ADR/spec baselines.
