# P032 - Mesh culling and alpha semantics consultation

Use this as a single self-contained prompt for ChatGPT Pro.

```text
You are advising on GSP_API, a backend-neutral graphical scene protocol and Python producer API.
The project needs an architecture/spec decision for strict 3D mesh face culling and non-opaque alpha
semantics. Please answer as an API/protocol architect, not as an implementation coder.

The response must be self-contained and must not assume access to files. Use the facts and excerpts
below as the complete project context.

Project context
===============

GSP_API defines formal protocol models for visual scenes. It has multiple backends:

- Matplotlib: reference/publication backend, correctness over speed, uses CPU/projection and
  Matplotlib artists.
- Datoviz v0.4: high-performance retained-scene GPU backend, but only public Datoviz APIs count as
  evidence. Private Vulkan state, shader slots, mesh ids, and backend-native handles are not public
  GSP semantics.
- VisPy2: high-level Python producer API that emits GSP protocol records. It must not expose backend
  handles.

Authority order in the repo is:

1. PROJECT_CHARTER.md
2. ARCHITECTURE.md
3. SPEC_INDEX.md
4. spec/**
5. accepted ADRs and .agent/decisions/**
6. LEGACY_MAP.md
7. existing source code

Existing code is implementation material but not automatically authoritative. If code and spec
conflict, the spec wins.

Already accepted 3D/View3D facts
================================

Accepted S036 View3D baseline:

- `Camera3D`: finite `eye`, `target`, `up`.
- `OrthographicProjection3D`: explicit camera-plane `xlim`, `ylim`, `near_far`; reversed x/y bounds
  are valid; `near >= 0` and `far > near`.
- `View3D`: static 3D view attached to one panel.
- Orthographic projection maps DATA points into panel NDC3.
- `(N,3)` DATA mesh vertices are projected through `View3D`.
- `(N,3)` NDC mesh vertices are interpreted as panel NDC x/y/z.
- Panel NDC convention:
  - `x`: -1 left, +1 right
  - `y`: -1 bottom, +1 top
  - `z`: -1 near, +1 far
  - smaller z is closer
- Strict opaque depth is capability-gated as `meshvisual.positions3d.opaque_depth.v1`.
- Where strict opaque depth is claimed, nearer opaque fragment wins.
- Ray readback is a separate accepted target: `query.view3d.ray_readback.v1`.
- 3D mesh triangle picking is separately accepted after S044 as
  `query.view3d.mesh_triangle_pick.v1` for strict-scope opaque DATA-space mesh triangles.

Deferred S036/S037 concepts include:

- scene graphs
- mesh-local 3D transforms
- transparency sorting
- strict clipping of partially clipped triangles
- external model loading
- instancing
- backend-native public controllers
- non-mesh 3D visual families
- non-opaque strict 3D alpha behavior

Existing camera basis:

```text
forward = normalize(target - eye)
right   = normalize(cross(forward, up))
true_up = cross(right, forward)
```

Projection:

```text
p_rel = p - eye

camera_x = dot(p_rel, right)
camera_y = dot(p_rel, true_up)
camera_z = dot(p_rel, forward)

ndc_x = -1 + 2 * (camera_x - xlim[0]) / (xlim[1] - xlim[0])
ndc_y = -1 + 2 * (camera_y - ylim[0]) / (ylim[1] - ylim[0])
ndc_z = -1 + 2 * (camera_z - near) / (far - near)
```

Existing MeshVisual protocol fields
===================================

The current `MeshVisual` dataclass is:

```python
class MeshVisual:
    id: str
    positions: FloatArray
    faces: IndexArray
    coordinate_space: CoordinateSpace
    color: ColorArray | None = None
    color_mode: MeshColorMode | None = None
    face_color_encoding: ScalarColorEncoding | None = None
    normal_mode: MeshNormalMode | None = None
    normals: FloatArray | None = None
    normal_generation: MeshNormalGeneration = MeshNormalGeneration.NONE
    shading: MeshShading = MeshShading.UNLIT_RGBA
    texture2d_id: str | None = None
    uv_mode: MeshUVMode = MeshUVMode.NONE
    uvs: FloatArray | None = None
    face_culling: FaceCulling = FaceCulling.NONE
    depth_test: DepthMode = DepthMode.AUTO
    depth_write: DepthMode = DepthMode.AUTO
    order: float = 0.0
    opacity_policy: OpacityPolicy = OpacityPolicy.ORDINARY_ALPHA
    transform: VisualTransformBinding | None = None
```

Current relevant enum shapes:

```text
MeshShading: unlit_rgba, flat_lambert, texture2d_unlit
FaceCulling: none, back, front
DepthMode: auto, enabled, disabled
OpacityPolicy: ordinary_alpha
CoordinateSpace: data, ndc, screen
```

Current behavior and limitations:

- `MeshVisual.positions` accepts `(N,2)` or `(N,3)`.
- `faces` are indexed triangles `(M,3)`.
- degenerate faces are rejected.
- `color` may be uniform, per-face, or per-vertex depending on `color_mode`.
- non-opaque 3D meshes are currently rejected from strict depth paths with
  `mesh3d_alpha_not_strict`.
- existing 2D affine visual transforms do not apply to `(N,3)` geometry.
- specs currently do not define strict culling semantics, transparent 3D mesh semantics,
  alpha blending order, alpha test/discard, OIT, or how culling affects query results.

Existing diagnostics include:

```text
mesh3d_depth_unsupported
mesh3d_depth_adapted
mesh3d_alpha_not_strict
mesh3d_clipping_adapted
query_3d_visual_hit_deferred
query_3d_snapshot_mismatch
```

Accepted S039/S050 material facts
=================================

S038 accepted unlit RGBA mesh color semantics:

- `meshvisual.material.unlit_rgba.v1`
- rendered color must not be affected by lights, normals, view direction, texture sampling, or
  backend material tinting.

S039 accepted flat Lambert only for DATA-space 3D meshes:

- `meshvisual.material.flat_lambert.v1`
- `meshvisual.normals.face3d.v1`
- `meshvisual.normal_generation.face_flat.v1`
- `view3d.light.ambient.v1`
- `view3d.light.directional.v1`

S050 accepted unlit Texture2D only:

- immutable `Texture2D` RGBA8 resources
- per-vertex UVs only
- fixed nearest/clamp/no-mipmap sampling
- output is multiplicative unlit RGBA:

```text
output.rgb = clamp(base.rgb * tex.rgb, 0.0, 1.0)
output.a   = clamp(base.a * tex.a, 0.0, 1.0)
```

S050 explicitly kept alpha/culling expansion, transparency sorting, alpha test/discard, and OIT out
of scope. For strict opaque 3D conformance, `base.a == 1.0` and all texture alpha bytes must be
255; otherwise `mesh3d_alpha_not_strict` applies.

Current backend posture
=======================

Matplotlib:

- uses CPU projection and 2D `PolyCollection` for 3D mesh rendering.
- orders projected faces far-to-near by average panel-NDC z as adapted behavior for opaque,
  non-intersecting fixture triangles.
- does not advertise strict opaque depth.
- rejects non-opaque 3D mesh colors for strict-depth paths with `mesh3d_alpha_not_strict`.
- rejects S050 `texture2d_unlit` as unsupported.

Datoviz:

- has retained DATA-space View3D mesh rendering with native depth test/write when v0.4 binding
  exposes required public APIs.
- may claim `meshvisual.positions3d.opaque_depth.v1` only on retained DATA-space View3D path for
  fully opaque meshes with depth test/write enabled, based on face-order runtime evidence.
- does not yet expose public canonical mesh face/triangle identity for native mesh picking.
- Texture2D renderer support remains blocked by missing sampler/origin/color proof.

S050 scoping decisions already made
===================================

From the local S050 scoping note:

- Do not advertise strict Datoviz opaque depth until a strict less-depth runtime proof exists for
  retained DATA-space View3D mesh rendering.
- Keep Matplotlib 3D mesh raster behavior documented as adapted.
- Keep non-opaque alpha rejected for strict 3D mesh paths. There is no accepted alpha-blending or
  order-independent-transparency contract.
- Treat culling as protocol surface area without strict accepted semantics until a spec/ADR defines
  winding, front-face convention, interaction with transforms, and query behavior.
- Keep face/vertex query expansion out of implementation work until a consultation or accepted spec
  defines payload shape and capability names.

Question
========

Please recommend the next accepted protocol boundary for MeshVisual culling and alpha semantics.
The goal is not to design a full rendering engine. We need a minimal, backend-neutral, testable v1
contract that can support future renderer capability gates without overpromising.

Please answer these specific questions:

1. Face winding and front-face convention
   - Should GSP define front-facing triangles by canonical source face vertex order in DATA/object
     coordinates, after View3D projection into panel NDC, or after final screen-space mapping?
   - Should reversed `View3D.xlim` / `ylim`, camera orientation, or future transforms affect
     front/back classification?
   - What exact formula should define front-facing for DATA and NDC `(N,3)` meshes?

2. Face culling
   - Should `FaceCulling.NONE/BACK/FRONT` be accepted now, or should culling remain unsupported
     until stricter render/query evidence exists?
   - If accepted, what are the capability names and diagnostics?
   - How should culling interact with `depth_test`, `depth_write`, `order`, and strict opaque depth?
   - How should culled triangles affect `query.view3d.mesh_triangle_pick.v1` and future CPU query
     or GPU query paths?

3. Non-opaque alpha
   - Should GSP keep all non-opaque 3D mesh alpha as non-strict/unsupported for now?
   - Is there a minimal accepted alpha contract worth adopting now, such as:
       a. reject non-opaque 3D meshes for strict depth;
       b. allow adapted painter-sorted alpha only without strict capability;
       c. accept alpha test/discard threshold;
       d. accept premultiplied or straight alpha blending;
       e. defer all of the above?
   - If any alpha rendering is accepted, what exact blend equation, order, and capability names
     should be used?

4. Textured alpha
   - For S050 `texture2d_unlit`, should any texture alpha byte below 255 continue to trigger
     `mesh3d_alpha_not_strict` for 3D strict depth?
   - Should 2D/NDC textured meshes with alpha be allowed as non-strict ordinary alpha, or should
     renderer support remain explicit and separate?

5. Capability naming and diagnostics
   - Propose concrete capability names for any accepted culling or alpha features.
   - Propose concrete diagnostics for unsupported culling, unsupported alpha, ambiguous winding,
     transform/culling conflict, query/culling unsupported, and alpha/depth conflicts.

6. Fixture plan
   - Propose the minimal positive and negative fixtures needed before any backend advertises the
     accepted capabilities.
   - Include at least one fixture that distinguishes source-order winding from projected/screen-space
     winding if that distinction matters.

7. Implementation sequencing
   - Recommend which pieces should be protocol-only first, which should be Matplotlib reference or
     adapted behavior, and which should wait for Datoviz runtime evidence.
   - Identify anything that should explicitly remain deferred to a later consultation.

Expected output format
======================

Please respond in this exact structure:

1. Executive Decision
   - A short recommendation: accept/defer culling, accept/defer alpha, and why.

2. Accepted v1 Semantics
   - Bullet list of any semantics that should be accepted now.
   - Include exact front-face formula if culling is accepted.
   - Include exact alpha/blend/depth rule if any alpha behavior is accepted.

3. Deferred Semantics
   - Bullet list of concepts to keep out of v1.

4. Capability Names
   - Table: capability, meaning, strict requirements.

5. Diagnostics
   - Table: diagnostic, trigger, required behavior.

6. Query Semantics
   - Explain how culling/alpha affects `query.view3d.mesh_triangle_pick.v1` and future query payloads.

7. Fixture Plan
   - Positive fixtures.
   - Negative fixtures.
   - Runtime evidence required before backend promotion.

8. Implementation Plan
   - Protocol validation steps.
   - Matplotlib behavior.
   - Datoviz behavior.
   - VisPy2 producer behavior.

9. Risks / Non-Goals
   - Anything likely to cause accidental overclaiming.

Important constraints
=====================

- Do not recommend using existing source code as authority if specs are silent.
- Do not require public material objects, scene graphs, model loading, backend texture handles, or
  backend-native controller objects.
- Prefer small capability-gated semantics over broad graphics-engine behavior.
- Private Datoviz/Vulkan APIs are not acceptable evidence.
- Matplotlib painter sorting is adapted behavior unless the proposed semantics explicitly define it
  as a reference-only non-strict path.
- Do not couple culling/alpha decisions to expanded 3D query payloads unless unavoidable; expanded
  query payloads have a separate consultation track.
```
