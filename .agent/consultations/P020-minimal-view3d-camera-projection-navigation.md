# P020 - Minimal View3D, Camera, Projection, and Navigation Semantics

## Prompt for ChatGPT Pro

You are advising on the next architecture stage for GSP_API, a Python Graphics Server Protocol-style
scene-description API for backend-agnostic scientific visualization.

This prompt is self-contained. Do not assume access to repository files.

Project mission:

- GSP is a backend-independent Graphics Server Protocol for scientific visualization, paired with a
  new VisPy2 Python producer API.
- One semantic visualization description should target Matplotlib reference/publication rendering,
  fast local GPU rendering through Datoviz v0.4, future remote renderers, future browser/WebGPU
  paths, and extension/data-source systems for large distributed datasets.
- GSP is a server/session protocol inspired by LSP, not just a Python object graph.
- Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
- Capability discovery and explicit adaptation are mandatory.
- Visual families are semantic contracts, not backend draw calls.
- Query/readback is first-class and uses a unified panel-query model: "what rendered scene
  contribution is under this panel coordinate?"
- Matplotlib is the reference/conformance/publication backend.
- Datoviz v0.4 is the flagship GPU backend.
- VisPy2 is the high-level Python producer of GSP scenes.

Authority/order of design decisions:

1. Project charter and architecture principles.
2. Protocol/session specs.
3. Accepted ADRs and stage decisions.
4. Existing implementation.

Current project state:

- Stage S035, "Retained View2D Navigation and Pan/Zoom", is complete.
- The current system has a coherent static 2D API plus live/programmatic 2D navigation.
- The next recommended stage is S036: minimal public `View3D`, camera, projection, and possibly
  3D navigation semantics.
- Do not implement public 3D API or Datoviz camera bindings until this consultation is answered.

Existing accepted 2D/static baseline:

- Visual families already include point, marker, segment/path, image, text, mesh, color mapping,
  colorbars, and semantic guides/axes.
- Six small review examples exist and have been used to review the API shape:
  scatter, image, points-over-image, guides/ticks, color mapping with colorbar, and text labels.
- Resolved layout work separates semantic guide records from derived layout snapshots. Render/query
  results must carry matching layout snapshot ids when strict layout/readback is claimed.
- Physical canvas sizing distinguishes live reference-pixel sizing from deterministic offscreen
  pixel-exact capture.

Accepted S027 transform/view/query inverse baseline:

- The public transform model is currently 2D-first.
- Accepted public transforms are finite invertible 2D affine transforms only, as named resources or
  small inline visual transform bindings.
- Existing public visual coordinate spaces are only `DATA` and `NDC`.
- `View2D` is deterministic panel-level state with finite linear x/y limits.
- Reversed limits are valid. Equal endpoints, non-finite values, log scales, categorical/date/
  geospatial scales, equal-aspect constraints, fixed-aspect layout, and public `View3D` are deferred.
- For DATA visuals, `View2D` maps data to panel NDC:

```text
ndc_x = -1 + 2 * (x - xlim[0]) / (xlim[1] - xlim[0])
ndc_y = -1 + 2 * (y - ylim[0]) / (ylim[1] - ylim[0])
```

- The accepted transform order is:

```text
source/local positional coordinates
-> optional visual-local 2D affine transform
-> declared coordinate space (DATA or NDC)
-> View2D for DATA visuals
-> panel NDC
-> framebuffer pixels
```

- Query inverse/readout is part of the strict contract. Strict transformed query results report
  panel coordinates, declared-space coordinates, source/local coordinates when invertible, data
  coordinates for DATA visuals, transform identity, inverse status, and diagnostics.
- Public 3D camera/projection/controller semantics, depth ordering, and 3D mesh query are currently
  deferred.

Accepted S025 MeshVisual baseline:

- Public v1 defines only `MeshVisual`, not a full surface/volume/material/model system.
- Geometry is inline indexed triangles:
  - `positions`: finite float array, shape `(N,2)` or `(N,3)`, with `N >= 3`.
  - `faces`: integer array, shape `(M,3)`, with valid vertex indices.
- `(N,2)` positions are the strict 2D conformance path in `DATA` or `NDC`.
- `(N,3)` positions are valid protocol data but currently require an accepted 3D panel/view
  projection capability for rendering/query.
- Strict mesh v1 is flat filled triangles with uniform or per-face RGBA.
- Per-vertex color, normals, generated normals, Lambert shading, 3D rendering, culling, alpha, and
  mesh query beyond 2D face hit testing are capability-gated.
- `MeshVisual` currently does not define a camera or mesh-local transform.
- Public materials/lights, textures/UVs, geometry resources, instancing, external model loading,
  LOD/chunking, advanced transparency, wireframe conformance, and public Datoviz implementation names
  are deferred.

Accepted S035 View2D navigation baseline:

- S035 adds deterministic 2D pan/zoom navigation by applying semantic actions to `View2D` state.
- It does not define a general event system.
- Accepted public concepts:
  - `View2DNavigationController` targeting one panel and one `View2D`.
  - `pan_by`: pan by resolved logical-pixel delta.
  - `zoom_about`: zoom around a resolved logical-pixel anchor.
  - `set_view`: replace the target `View2D`.
  - `reset_view`: restore a configured home/default `View2D`.
  - `NavigationResult`: accepted/rejected result with updated `View2D`, revision, snapshot ids, and
    diagnostics.
- Coordinates are resolved panel logical pixels from the current layout snapshot.
- Accepted navigation returns explicit `View2D` state. The controller owns no hidden backend camera.
- Render/query/readback coherence is mandatory: after accepted navigation, render/query results must
  identify the view/layout snapshot used.
- Raw mouse/wheel/keyboard/touch events, pointer capture, hover, selection, brushing, linked views,
  kinetic scrolling, event propagation, focus/cursor semantics, backend-native controller objects,
  public `View3D`, camera/projection semantics, orbit/trackball controllers, and 3D picking remain
  deferred.
- Matplotlib supports programmatic and live drag/wheel review paths.
- Datoviz supports retained `View2D` update proof; unchanged visual-buffer uploads must remain zero
  during retained navigation.

Datoviz and Matplotlib backend constraints:

- Datoviz v0.4 should use retained-scene APIs where possible, but no Datoviz object model, slot
  names, material structs, or draw-state names should leak into public protocol semantics.
- Backend-native interaction can be used experimentally only when its resulting state is synchronized
  into canonical protocol state.
- Matplotlib 3D rendering is not necessarily strict protocol authority. It may be optional/adapted,
  useful for diagnostic/reference projection checks, or unsupported if exact semantics would be
  misleading.
- Datoviz may be the first meaningful runtime backend for 3D, but it must still be capability-gated.

Decision problem:

Define the minimal S036 public semantics for `View3D`, camera, projection, depth, and any first 3D
navigation boundary so that `(N,3)` `MeshVisual` data can become useful without freezing a full
graphics-engine object model.

We need a recommendation that answers:

1. Should S036 define static `View3D`/camera/projection only, or include first 3D navigation actions?
2. What exact fields should minimal `View3D` have?
3. Should camera be represented as `eye/target/up`, explicit matrices, or both?
4. Should the first projection support orthographic only, perspective only, or both?
5. What coordinate spaces should 3D visuals use without adding a broad coordinate-space taxonomy?
6. How should `(N,3)` `MeshVisual` with `CoordinateSpace.DATA` and `CoordinateSpace.NDC` be
   interpreted?
7. What is the minimal depth model for strict or capability-gated 3D rendering?
8. How should query/readback work for 3D in S036, if at all?
9. What should Matplotlib, Datoviz, and VisPy2 each be expected to implement in this first stage?
10. What conformance fixtures are mandatory, and which behavior should remain adapted/experimental?

Candidate design options:

Option A: Static orthographic `View3D` only.

- Define a `View3D` bound to one panel with finite camera basis or view matrix, orthographic bounds,
  near/far clipping, and deterministic world/data-to-panel projection.
- Make `(N,3)` `MeshVisual` useful for simple static 3D scenes.
- Defer perspective, orbit/trackball, 3D picking, lighting, materials, clipping planes, and public
  3D navigation.

Option B: Static orthographic plus perspective.

- Define `View3D` with projection mode `orthographic` or `perspective`, including exact FOV/aspect/
  near/far semantics.
- More useful for real 3D, but a larger conformance surface and more backend-specific pitfalls.

Option C: Matrix-first `View3D`.

- Define explicit finite view and projection matrices as the public contract.
- This may be precise and backend-neutral, but may expose too much engine math too early and make
  query/readback/camera UI harder to standardize.

Option D: Camera-parameter-first `View3D` with derived matrices.

- Define `eye`, `target` or `center`, `up`, projection parameters, and deterministic derived matrices.
- Easier for users and review examples, but needs careful degeneracy validation and convention
  choices.

Option E: Add `View3DNavigationController` now.

- Add orbit/pan/dolly/zoom/reset actions similar to S035, returning explicit `View3D` updates.
- Useful for live review, but risks overfreezing controller semantics before static projection/query
  semantics are proven.

Option F: Datoviz-native 3D camera demo only.

- Avoid public `View3D`; show 3D through backend-specific adapted examples.
- Fast to demonstrate, but does not satisfy the need to make `(N,3)` MeshVisual a protocol feature.

Constraints for your recommendation:

- Do not import Matplotlib, Datoviz, VisPy, Qt, browser, game-engine, or OpenGL/WebGPU object models
  wholesale into the public protocol.
- Do not add broad scene-graph, material, lighting, model-file, or full event-system semantics in S036.
- Preserve capability gating and structured unsupported diagnostics.
- Preserve render/query/readback coherence.
- Prefer a small releaseable stage with strict numeric fixtures over a broad architecture.
- Be explicit about whether public `View3D` navigation should be in S036 or deferred to S037.
- If navigation is deferred, say what interactive review/demo is still allowed.
- Identify exactly what is strict conformance, what is capability-gated, and what is adapted/
  experimental.
- Keep existing `CoordinateSpace.DATA` and `CoordinateSpace.NDC` if possible. If you recommend a new
  coordinate-space concept, justify why it is necessary and how to keep it narrow.
- Account for existing `MeshVisual.positions` supporting both `(N,2)` and `(N,3)`.
- Account for query/readback: either define minimal 3D query fields or explicitly keep 3D query
  unsupported with diagnostics while still preserving render/query snapshot coherence.

Recommended answer style:

- Be concrete. Name dataclasses/enums/fields if you recommend them.
- Avoid vague "future extensibility" language unless tied to a specific deferred field/capability.
- Use tables where useful.
- Call out any design that would be risky or premature.

Expected output format:

1. Recommendation summary: 4-8 bullets.
2. Stage plan table with columns:
   - Stage
   - Goal
   - Public semantics added
   - Backend obligations
   - Fixtures
   - Stop condition
3. Minimal S036 public model:
   - dataclasses/enums/fields;
   - validation rules;
   - coordinate conventions;
   - projection math/conventions at the level needed for conformance;
   - snapshot/revision fields;
   - diagnostics.
4. MeshVisual `(N,3)` integration:
   - how DATA and NDC positions are interpreted;
   - depth/culling defaults;
   - what happens without 3D capability;
   - what remains unsupported.
5. Query/readback policy:
   - strict S036 query fields, or explicit unsupported diagnostics;
   - how render/query snapshot coherence is maintained;
   - whether 3D picking/ray intersection is deferred.
6. Backend mapping:
   - Matplotlib reference/adapted/unsupported responsibilities;
   - Datoviz v0.4 responsibilities;
   - VisPy2 producer API responsibilities.
7. Required conformance fixtures and negative fixtures.
8. Explicit deferrals.
9. Risks and mitigations.
10. ADR/spec skeleton suitable for converting into repository files.
11. Mission Control recommendation:
   - 3-6 concrete missions for S036;
   - dependencies;
   - stop conditions;
   - which missions require another Pro consultation, if any.

## Local Mission Control Note

This needs ChatGPT Pro consultation.

Dependent implementation should pause until the response is pasted or committed as
`.agent/consultations/P020-response.md`.

