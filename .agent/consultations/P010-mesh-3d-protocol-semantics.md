# P010 - Mesh/3D protocol semantics

Status: awaiting ChatGPT Pro response.

This needs ChatGPT Pro consultation.

## Why This Is Needed

S023 completed Point, Marker, Segment, Path, and Image. S024 completed public TextVisual while
explicitly deferring public GlyphVisual. The next stage, S025, should cover Mesh/3D geometry, but
mesh semantics are architectural: indexed geometry ownership, vertex/face attributes, normals,
materials, lighting, depth/culling, camera/3D transforms, texture use, and query payloads can easily
leak backend-specific behavior into the public protocol.

Do not commit public MeshVisual semantics or implement renderer behavior until the response is
pasted or committed and converted into an ADR/spec baseline. Backend API evidence gathering is
allowed if it does not freeze protocol fields.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

```text
You are an architecture reviewer for GSP_API, a Python research prototype for a backend-independent
Graphics Server Protocol (GSP) for scientific visualization.

Your task is to recommend a narrow, durable Mesh/3D visual-family protocol for the next stage
(S025). This is a pre-implementation architecture review. Do not write implementation code. The
answer must be concrete enough for worker agents to create ADRs, specs, validation tests,
Matplotlib reference rendering, Datoviz capability gates, VisPy2 producer APIs, visual QA cases, and
query/readback tests without inventing protocol semantics.

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

Cross-cutting accepted rules:

- Every visual has a stable protocol id.
- Numeric arrays are finite; positions are float32/float64 shape (N, 2) or (N, 3).
- RGBA arrays are uint8 [0,255] or float [0,1].
- Point/marker sizes, text font sizes, and stroke widths are logical screen pixels.
- CoordinateSpace values are NDC and DATA.
- S023/S024 visual QA uses NDC fixtures over [-1,+1] for backend comparisons.
- Backend-native names, units, and resource handles stay internal unless accepted as semantic GSP concepts.
- Mesh, surface, volume, colorbars, broad colormap registries, advanced normalization, tiled/remote images, rich text, and public glyph resources remain deferred.

Current protocol implementation style uses frozen dataclasses with validation, small enums, NumPy
arrays for in-process paths, and sidecar NPZ arrays only for debug/replay fixtures.

## Current protocol/query/capability architecture

GSP has a unified panel-query model: “what rendered scene contribution is under this panel
coordinate?” Query results should carry identity, item/group/face/voxel/texel ids, visual/data/UVW
coordinates, displayed RGBA, depth/order, and optional value/readout payloads.

Capabilities are explicit. Unsupported behavior should be accepted, simplified with diagnostic,
deactivated with diagnostic, or rejected with fatal diagnostic. Datoviz support must produce
structured unsupported reports rather than hidden fallback approximations.

## Existing mesh-like code, not authoritative

The legacy implementation has mesh-related classes, but they are not accepted protocol authority:

- `Mesh` combines a `MeshGeometry` object and a `MeshMaterial` object.
- `MeshGeometry` carries positions shape (N, 3), triangular face indices shape (M, 3), normals shape (N, 3), and UVs shape (N, 2).
- Legacy material classes include Basic, Depth, Normal, Phong, and Textured material variants.
- Legacy material attributes include face/vertex colors, edge colors/widths, face sorting, face culling, diffuse/specular colors, shininess, lights, texture+tint, and normals/depth-derived colors.
- Some validation bodies are incomplete or stubbed.
- Existing examples include basic mesh, Phong, depth, normal, textured mesh, OBJ models, and manual Datoviz mesh experiments.

These facts are useful input, but S025 should define a small public protocol contract rather than
copying legacy material and lighting APIs wholesale.

## Datoviz v0.4 context

Datoviz v0.4 should be treated as a C-first retained scene API, not a v0.3 Python plotting
compatibility layer. Implementations use retained visual constructors plus generic attribute uploads,
explicit panel attachment descriptors, and capability reports. No worker should plan against v0.3
alloc/setter APIs.

Current sibling Datoviz v0.4-dev evidence shows:

- `dvz_mesh(DvzScene* scene, uint32_t flags)` creates a mesh visual.
- `dvz_mesh_set_geometry(DvzVisual* visual, const DvzGeometry* geometry)` uploads CPU geometry to a mesh visual.
- Scene documentation lists mesh slots: `position` (vec3f), optional `color` (RGBA8), optional `normal` (vec3f), optional `texcoords` (vec2f), optional `instance_transform` (mat4f per instance).
- Primitive and mesh visuals accept an `index` slot in the retained slice.
- `dvz_visual_set_material()` applies shared material parameters to primitive, mesh, or sphere visuals.
- `dvz_visual_set_depth()` configures depth cueing for point, pixel, primitive, mesh, or sphere visuals.
- `dvz_visual_set_texture()` can attach a 2D RGBA8 sRGB texture to image, glyph, or mesh visuals; for mesh it binds the `texture` slot.
- Datoviz examples include retained lit indexed mesh, builtin 2D/3D geometry rendered as mesh, OBJ loading, mesh texture, material mesh, transparency, controller+mesh examples, and mesh-instance selection/query examples.

This evidence suggests Datoviz can be a strong mesh backend, but GSP must not expose Datoviz slot
names, material structs, or helper APIs as public protocol unless they are semantically correct for
all backends.

## Desired S025 scope

The goal is a useful MeshVisual v1 that covers common scientific 2D/3D triangular geometry without
becoming a full scene graph, full material system, CAD mesh package, or game-engine renderer.

The first practical result should be:

- a narrow public MeshVisual protocol;
- deterministic validation of arrays and indices;
- Matplotlib reference rendering for a small conformance subset;
- Datoviz v0.4 support or structured unsupported reports;
- VisPy2 producer API for simple meshes;
- visual QA contact sheets;
- clear query/readback semantics for mesh hits if feasible.

## Design questions to answer

1. Should S025 define `MeshVisual` only, or also separate `GeometryResource`, `Material`, `SurfaceVisual`, or `VolumeVisual` concepts? Which are public v1 and which are deferred?
2. What fields should `MeshVisual` v1 expose? Please decide names and semantics for:
   - positions shape and dimensionality;
   - indices / faces representation;
   - triangle-only vs lines/quads/polygons;
   - colors: uniform, per-vertex, per-face, scalar-to-colormap, or which subset;
   - normals: required, optional, generated, or deferred;
   - UVs/textures: included, capability-gated, or deferred;
   - coordinate_space and relation to existing NDC/DATA rules;
   - model transforms, instancing, and 3D orientation;
   - z/depth/order and face culling;
   - edge/wireframe rendering;
   - alpha/transparency;
   - material/lighting scope.
3. Should S025 support 2D meshes in panel DATA/NDC coordinates, 3D meshes with camera projection, or both? How should workers avoid mixing 2D overlay mesh semantics with 3D world semantics?
4. What dtype/shape/index validation is required for v1? Include finite checks, index bounds, empty arrays, degenerate triangles, winding, and scalar/per-vertex/per-face broadcasting rules.
5. How should colors work in v1? Should the baseline be uniform RGBA, per-vertex RGBA, per-face RGBA, scalar `values` plus colormap, or a minimal combination? Remember that broad colormap registries and colorbars are deferred.
6. What is the minimal material policy? Should v1 be unlit flat color only, simple Lambert/Phong, normal/depth debug materials, or a small enum? How should Datoviz material support be capability-gated without freezing Datoviz material structs?
7. Should normals be part of v1? If yes, are they per-vertex or per-face, user-supplied or generated, and what happens when they are missing? If no, how can a 3D mesh render predictably?
8. Should textures/UVs be part of S025? Datoviz supports mesh textures, but ImageVisual color semantics are narrow and texture resource ownership may need more design. Should textured mesh be deferred to a later mission?
9. How should cameras/transforms relate to MeshVisual? Existing GSP has view/panel concepts and 2D examples, but a stable 3D camera/transform model may not yet be accepted. What narrow default is safe for QA?
10. What query/readback payload should mesh hits return? Candidate fields include visual id, item id, face index, vertex indices, barycentric coordinates, world/data position, interpolated color/value, depth, instance id. Which are v1 required/capability-gated/deferred?
11. How should Matplotlib act as reference backend for MeshVisual? Should it use mplot3d for 3D, PolyCollection for 2D, or restrict reference conformance to 2D/projected cases? What limitations/diagnostics are acceptable?
12. What Datoviz capability gates and diagnostics should be defined? Include missing mesh API, index support, per-face/per-vertex color mismatch, material unsupported, texture unsupported, query unsupported, depth/culling unsupported, and transform/camera limitations.
13. What visual QA cases are sufficient for v1? Candidate cases: single colored triangle, indexed square/two triangles, per-face colors, per-vertex color interpolation, cube with depth/culling, alpha overlap, wireframe edges, DATA vs NDC, simple 3D camera view, and mesh query/readback.
14. What should be explicitly deferred? Candidate deferrals: quads/polygons with holes, surface grids, volumes, splats, tessellation, subdivision, skeletal animation, instancing, PBR, lights, shadows, clipping planes, advanced transparency, texture atlases, OBJ loading as protocol, remote mesh chunks, LOD, topology editing, and GPU-side generated geometry.
15. What stage/mission sequence should follow the consultation? Please propose implementation order and stop conditions.

## Constraints

- Keep the v1 protocol backend-independent.
- Do not expose Datoviz slot names, material structs, geometry loaders, or draw calls as GSP fields unless they are semantically appropriate.
- Prefer a minimal accepted contract with explicit deferrals over an ambitious 3D/material system.
- Preserve S023/S024 style: deterministic validation, clear capability gates, Matplotlib reference first where feasible, Datoviz support or structured unsupported reports, visual QA contact sheets, manual review notes.
- Do not require network access, dynamic plugins, OBJ/PLY loading, or external model files for conformance.
- Do not require JSON/base64 for normal in-process arrays.
- Avoid creating a parallel scene graph or renderer architecture.

## Expected output format

Please produce exactly this markdown structure:

# Consultation Result: S025 Mesh/3D Protocol Semantics

## Executive recommendation

A concise decision on public v1 scope: MeshVisual only or additional concepts; first implementable slice.

## Protocol contract draft

A concrete table of fields with names, types, scalar/per-item/per-vertex/per-face rules, validation,
units, defaults, and whether each field is required or optional.

## Enums and units

List accepted enum values and units for coordinate behavior, color mode, normals, material/shading,
face culling, depth/order, and any transform/camera behavior.

## Geometry and resource policy

Decide what is inline MeshVisual data vs reusable resource vs deferred, including indices, normals,
UVs, textures, instancing, and external model files.

## Material, lighting, and color policy

Define the v1 material/color baseline and what is capability-gated or deferred.

## Transform, camera, and depth policy

Define how MeshVisual positions are interpreted in NDC/DATA/3D, how cameras enter the model, and how
depth/culling/order should behave in v1.

## Query/readback contract

Define required, optional, capability-gated, and deferred mesh query payload fields.

## Backend guidance

Separate Matplotlib reference guidance and Datoviz v0.4 guidance, including accepted limitations and
required structured diagnostics.

## Visual QA plan

List the minimal S025 visual QA cases, required artifacts, manual review criteria, and which cases
are strict vs optional/capability-gated.

## Explicit deferrals

List features that must not be included in S025 v1.

## Recommended mission sequence

Give mission-sized steps after consultation, including stop conditions.
```

## Expected Result Handling

After the response is pasted or committed:

1. Save it as `.agent/consultations/P010-response.md`.
2. Convert it into an ADR and `spec/visuals/mesh.md` during M083.
3. Update `SPEC_INDEX.md`, `spec/visual_families_v1.md`, `spec/visual_cross_cutting_rules.md`,
   `spec/backend_capabilities_visuals.md`, `spec/visual_qa_harness.md`, `spec/vispy2_visual_api.md`,
   and Datoviz backend boundary notes as needed.
4. Only then unblock MeshVisual implementation missions M084-M089.
