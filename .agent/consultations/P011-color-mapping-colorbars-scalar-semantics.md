# P011 - Color mapping, colorbars, and scalar data semantics

Status: awaiting ChatGPT Pro response.

This needs ChatGPT Pro consultation.

## Why This Is Needed

S025 closed the MeshVisual stage. The next stage should address color mapping, colorbars, and
advanced scalar/image data semantics, but this is architectural protocol work: colormap identity,
normalization, scalar value ownership, displayed color/readback, legends/colorbars, backend
capabilities, and VisPy2 API shape can easily leak Matplotlib or Datoviz implementation details into
GSP.

Do not commit public colormap, normalization, colorbar, scalar-mesh, or scalar-image semantics until
the response is pasted or committed and converted into an ADR/spec baseline. Implementation remains
blocked pending that conversion.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

```text
You are an architecture reviewer for GSP_API, a Python research prototype for a backend-independent
Graphics Server Protocol (GSP) for scientific visualization.

Your task is to recommend a narrow, durable protocol stage for color mapping, colorbars, and
advanced scalar/image data semantics. This is a pre-implementation architecture review. Do not write
implementation code. The answer must be concrete enough for worker agents to create ADRs, specs,
validation tests, Matplotlib reference behavior, Datoviz capability gates, VisPy2 producer APIs,
visual QA cases, and query/readback tests without inventing protocol semantics.

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

## Current accepted visual baseline

Accepted visual families:

| Family | Protocol model | Important accepted semantics |
|---|---|---|
| Point | PointVisual | finite 2D/3D positions; RGBA colors; sizes are rendered screen-pixel diameters; coordinate_space is NDC or DATA. |
| Marker | MarkerVisual | shaped markers; fill/stroke RGBA; scalar/per-marker pixel diameters; angles are radians; stroke width is screen pixels. |
| Segment | SegmentVisual | independent line segments; RGBA colors; widths are screen-pixel stroke widths; conservative cap enum. |
| Path | PathVisual | open polyline/subpath visual; path_lengths partition vertices; per-subpath RGBA and width; conservative cap/join/miter fields. |
| Image | ImageVisual | 2D scalar/RGB/RGBA arrays; extent; origin upper/lower; nearest/linear interpolation; scalar gray colormap and clim only. |
| Text | TextVisual | public TextVisual only; renderer-internal glyphs/atlases; strings plus finite 2D/3D anchor positions; screen-pixel font sizes; RGBA; generic font roles; radians rotation; explicit anchors; ASCII required, Unicode capability-dependent; item-level query. |
| Mesh | MeshVisual | public MeshVisual only; inline indexed triangles; strict 2D flat uniform/per-face RGBA conformance; face-level query/readback for strict 2D; per-vertex color, 3D rendering/query, normals, shading, culling, alpha, and advanced query are capability-gated or deferred. |

Cross-cutting accepted rules:

- Every visual has a stable protocol id.
- Numeric arrays are finite; positions are float32/float64 shape (N, 2) or (N, 3).
- RGBA arrays are uint8 [0,255] or float [0,1].
- Point/marker sizes, text font sizes, and stroke widths are logical screen pixels.
- CoordinateSpace values are NDC and DATA.
- Visual QA uses deterministic NDC fixtures over [-1,+1] where practical for backend comparisons.
- Backend-native names, units, and resource handles stay internal unless accepted as semantic GSP concepts.
- Broad colormap registries, colorbars, scalar-to-color for most visuals, advanced normalization,
  tiled/remote images, public glyph resources, mesh materials/lights/textures, and volume/surface
  visuals remain deferred.

Current protocol implementation style uses frozen dataclasses with validation, small enums, NumPy
arrays for in-process paths, and sidecar NPZ arrays only for debug/replay fixtures.

## Current protocol/query/capability architecture

GSP has a unified panel-query model: “what rendered scene contribution is under this panel
coordinate?” Query results carry identity, item/group/face/texel ids, coordinates, displayed RGBA,
value/readout payloads, and optional extension payloads.

Existing query payload examples:

- ImageVisual query reports texel coordinates, displayed RGBA, and source value.
- TextVisual query is item-level and uses `gsp.text-query@0.1`.
- MeshVisual query is face-level for strict 2D uniform/per-face RGBA and uses
  `gsp.mesh-query@0.1`.
- Tiled-image extension query uses a typed payload and explicit extension kind.

Capabilities are explicit. Unsupported behavior should be accepted, simplified with diagnostic,
deactivated with diagnostic, or rejected with fatal diagnostic. Datoviz support must produce
structured unsupported reports rather than hidden fallback approximations.

## Current accepted image/scalar baseline

ImageVisual currently accepts:

- image arrays shaped (H, W), (H, W, 3), or (H, W, 4);
- extent;
- origin upper/lower;
- interpolation nearest/linear;
- coordinate_space NDC or DATA;
- colormap limited to gray for scalar images;
- optional clim for scalar images.

ADR-0015 accepted scalar gray/clim as the narrow first scalar image slice. It did not define a
broad colormap registry, norm objects, colorbars, masked/NaN semantics beyond current validation,
categorical palettes, or scalar-to-color for point/marker/path/mesh families.

## Current VisPy2 producer state

VisPy2 is the high-level Python producer of GSP scenes. It currently exposes bounded APIs for:

- scatter -> PointVisual;
- markers -> MarkerVisual;
- segments -> SegmentVisual;
- path/plot -> PathVisual;
- imshow -> ImageVisual, including scalar gray/clim;
- text -> TextVisual;
- mesh -> MeshVisual;
- semantic guide methods for view limits, labels, title, ticks, and grid.

VisPy2 should target GSP, not Datoviz or Matplotlib directly.

## Datoviz and Matplotlib context

Matplotlib is the reference/conformance/publication backend. It has rich colormap, normalization,
colorbar, masked array, and ScalarMappable concepts, but GSP must not copy Matplotlib object graphs
blindly.

Datoviz v0.4 is the flagship GPU backend. It can render GPU colors and textures and should be
capability-gated. The protocol should not expose Datoviz slot names, shader internals, or material
structs as public GSP semantics.

## Desired next-stage scope

The likely stage is S026: Color Mapping, Colorbars, and Scalar Data Semantics.

Potential deliverables:

- accepted protocol model for colormap references and normalization;
- scalar-to-RGBA rules for a narrow set of visual families;
- colorbar/legend/guide semantics if they belong in this stage;
- query/readback behavior that distinguishes source scalar values from displayed RGBA;
- Matplotlib reference implementation;
- Datoviz support or structured unsupported diagnostics;
- VisPy2 producer API updates;
- visual QA cases for deterministic scalar/colorbar output.

## Design questions to answer

1. Should S026 define shared `ColorMap`, `Normalize`, `ColorEncoding`, `ColorScale`, `ColorbarGuide`,
   or similar protocol concepts? Which are public v1 and which are deferred?
2. What is the minimal durable colormap vocabulary? Should v1 support only `gray` plus a small named
   scientific set such as `viridis`, `magma`, `plasma`, `inferno`, `cividis`, or should arbitrary
   colormap names/lookup tables be deferred?
3. Should colormaps be referenced by enum/name, embedded lookup tables, resource ids, or both? How
   should backend availability and approximation be reported?
4. What normalization semantics should v1 expose? Decide whether to support only linear clim, or
   also log, symlog, power/gamma, centered/diverging, categorical/boundary, percentile/auto, and
   NaN/masked handling.
5. Should auto clim/normalization be protocol semantics or producer convenience? If supported, what
   exact data-dependent behavior is deterministic enough for conformance?
6. Which visual families should accept scalar values in S026? Candidate families: ImageVisual scalar
   enhancement only; PointVisual/MarkerVisual scalar colors; MeshVisual face/vertex scalar colors;
   Segment/Path scalar stroke colors. Recommend the narrow first slice.
7. Should scalar-to-color be represented as replacing RGBA fields, as alternate `values +
   color_mapping` fields, or as a separate visual/resource attachment?
8. How should query/readback report scalar values and displayed colors? Include fields for source
   value, normalized value, colormap id, over/under/bad handling, and displayed RGBA if appropriate.
9. Should colorbars be semantic guides attached to panels/views, independent visuals, layout
   objects, or out of scope? How should ticks/labels and existing guide semantics interact with
   colorbars?
10. What is the minimal colorbar API and protocol contract if colorbars are included? Include id,
    linked visual/color scale, orientation, label, tick policy, range, and placement/layout policy.
11. How should Matplotlib act as reference backend for S026? Which exact behavior should be
    conformance, and which Matplotlib capabilities should remain richer than GSP v1?
12. What Datoviz capability gates and diagnostics should be defined? Include missing colormap
    support, LUT upload, GPU normalization, colorbar rendering, readback of normalized/scalar
    values, and approximated colormap differences.
13. How should NaN, masked, under, over, and alpha behavior work for scalar data? Which are required
    for strict conformance and which are deferred?
14. Should categorical/discrete palettes and legends be in this stage or a later legend/annotation
    stage?
15. What visual QA cases are sufficient for v1? Candidate cases: scalar image gray with clim,
    viridis scalar image, over/under/bad colors, marker scalar colors, mesh per-face scalar colors,
    colorbar with label/ticks, query returns source value and displayed RGBA.
16. What should be explicitly deferred? Candidate deferrals: arbitrary Matplotlib colormap names,
    user-defined continuous colormap transfer functions, categorical legends, histogram equalization,
    automatic percentile limits, multi-channel compositing, volume transfer functions, Datoviz shader
    APIs, and remote chunk-wise dynamic normalization.
17. What stage/mission sequence should follow the consultation? Please propose implementation order
    and stop conditions.

## Constraints

- Keep the v1 protocol backend-independent.
- Do not expose Matplotlib ScalarMappable internals, Datoviz slot names, shader APIs, or backend
  draw calls as GSP fields unless they are semantically appropriate.
- Prefer a minimal accepted contract with explicit deferrals over a broad color system.
- Preserve current style: deterministic validation, clear capability gates, Matplotlib reference
  first where feasible, Datoviz support or structured unsupported reports, visual QA contact sheets,
  manual review notes.
- Do not require network access, dynamic plugins, external colormap packages, or remote data for
  conformance.
- Do not require JSON/base64 for normal in-process arrays.
- Do not create a parallel scene graph or renderer architecture.

## Expected output format

Please produce exactly this markdown structure:

# Consultation Result: S026 Color Mapping and Colorbars

## Executive recommendation

A concise decision on public v1 scope and the first implementable slice.

## Protocol contract draft

A concrete table of fields/concepts with names, types, validation, defaults, required/optional
status, and whether each item is strict v1, capability-gated, producer convenience, or deferred.

## Colormap and normalization policy

List accepted colormap identifiers, LUT/resource policy, normalization modes, clim/auto behavior,
NaN/masked/under/over behavior, and alpha behavior.

## Visual-family integration

State exactly which existing visual families gain scalar color support in v1 and how scalar fields
coexist with existing RGBA fields.

## Colorbar and guide policy

State whether colorbars are in S026 v1. If yes, define their semantic relation to panels/views,
color scales, ticks, labels, layout, and queries. If no, define the deferral boundary.

## Query/readback semantics

Define required and optional query payload fields for scalar/color-mapped visuals and colorbars.

## Backend mapping guidance

Separate Matplotlib reference behavior from Datoviz capability-gated behavior and list required
diagnostics.

## Visual QA plan

List required strict cases and optional/capability-gated cases.

## Explicit deferrals

List features that must not be implemented as public protocol in S026.

## Implementation mission sequence

A numbered mission plan after the consultation response, including dependencies and stop
conditions.

## Risks and review checklist

Concise risks and checks for ADR/spec authors and implementation agents.
```

## Expected Handling

After the user pastes or commits the ChatGPT Pro response:

1. Convert the response into an accepted ADR and specs.
2. Update `SPEC_INDEX.md` and decision records.
3. Only then promote implementation missions from blocked/draft.
