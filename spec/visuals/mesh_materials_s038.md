# MeshVisual Materials - S038 Unlit RGBA Boundary

Status: accepted S038 protocol boundary. S039 extends this boundary with
`spec/visuals/mesh_flat_lambert_s039.md` for flat Lambert face-normal shading only. S050 extends it
with `spec/visuals/mesh_texture2d_unlit_s050.md` for unlit Texture2D sampling only.

Semantic purpose: name the material behavior already required by accepted `MeshVisual` RGBA color
rendering without accepting a public material object, lighting model, normal model, texture model, or
scene graph.

## Scope

S038 accepts one public material concept:

| Concept | Public shape | Semantics |
|---|---|---|
| `unlit_rgba` | implicit protocol concept | Existing `MeshVisual` RGBA colors are the final material color. |

There is no S038 public `MeshMaterial3D`, `Material`, `View3D.lights`, `Texture2D`, UV, sampler, or
normal-bearing material API. Existing legacy or experimental material classes are implementation
material only and are not public protocol authority.

## Public Semantics

A color-bearing `MeshVisual` with no future accepted material field is interpreted as
`unlit_rgba`.

The base color source is the existing accepted `MeshVisual.color` input:

| Color source | Shape | Requirement |
|---|---|---|
| uniform RGBA | `(4,)` | Accepted where the current mesh color spec accepts uniform color. |
| per-face RGBA | `(F, 4)` | Accepted where the current mesh color spec accepts face color. |
| per-vertex RGBA | `(N, 4)` | Optional only where the current mesh color spec already accepts vertex color. |

S038 does not add new color cardinalities or scalar color behavior.

For strict opaque `unlit_rgba` rendering:

```text
output.rgb = base.rgb
output.a   = base.a
```

No normal, light, camera position, view direction, depth value, texture sample, generated backend
attribute, or backend-native material state may modify the color. Camera/projection affect geometry
placement and depth only.

## Alpha and Depth

Alpha is part of the RGBA color and is not multiplied by lighting. Strict 3D mesh material
conformance is claimed only for opaque alpha.

Non-opaque 3D mesh alpha remains non-strict and should keep using:

```text
mesh3d_alpha_not_strict
```

Depth behavior remains governed by existing 3D mesh capabilities and diagnostics, including
`meshvisual.positions3d.opaque_depth.v1` and `mesh3d_depth_adapted`. The material capability does not
upgrade adapted Matplotlib face sorting into strict fragment-depth semantics.

## Color-Space Boundary

S038 defines no strict linear RGB, sRGB conversion, tone mapping, gamma correction, or display
color-management behavior. This is acceptable for `unlit_rgba` because there is no lighting math.

A backend claiming strict `meshvisual.material.unlit_rgba.v1` must not apply implicit lighting or
backend material tinting, but the capability does not claim full display color-management
conformance.

## Capabilities

Accepted:

| Capability | Meaning | Strict requirements |
|---|---|---|
| `meshvisual.material.unlit_rgba.v1` | Existing `MeshVisual` RGBA colors are interpreted as unlit material color. | Accepted RGBA color source is rendered without lighting, normals, texture sampling, view-dependent color change, or backend material tinting. Opaque alpha only is strict. |

Deferred or reserved:

| Capability | S038 disposition |
|---|---|
| `meshvisual.material.flat_lambert.v1` | Deferred. Requires accepted normals, light-space, intensity/color, clamping, alpha, color-space, and fixture semantics. |
| `meshvisual.material.flat_phong.v1` | Deferred. Requires Lambert prerequisites plus view-vector, specular, shininess, interpolation, and shader-parity semantics. |
| `view3d.light.ambient.v1` | Deferred. No public lighting container exists in S038. |
| `view3d.light.directional.v1` | Deferred. A future direction-space rule is required. |
| `texture2d.rgba8.v1` | Accepted by S050 for immutable RGBA8 `Texture2D` resources. |
| `meshvisual.uv.vertex2d.v1` | Accepted by S050 for per-vertex UVs only. |
| `meshvisual.material.texture2d_unlit.v1` | Accepted by S050 for fixed-sampler unlit texture multiplication only. |

S038 does not introduce normal capabilities such as `meshvisual.normals.vertex3d.v1` or
`meshvisual.normals.face3d.v1`.

## Diagnostics

Recommended diagnostic codes for S038 material-boundary validation:

| Diagnostic | Trigger |
|---|---|
| `mesh3d_material_unsupported` | A public payload requests a material other than absent/implicit `unlit_rgba`, or a backend cannot support the requested material capability. |
| `mesh3d_material_object_unsupported` | A payload or producer attempts to pass a public material object or material resource such as `MeshMaterial3D`. |
| `mesh3d_normals_unsupported` | A public S038 payload includes normals or requests normal-based material behavior. |
| `mesh3d_normals_missing` | Future shaded material path is requested without required explicit normals. Not emitted for accepted S038 `unlit_rgba`. |
| `mesh3d_normals_nonfinite` | Future normal payload contains NaN or infinite components. S038 validation may instead stop earlier with `mesh3d_normals_unsupported`. |
| `mesh3d_normals_invalid_zero` | Future normal payload contains zero-length normals. Not required for accepted S038. |
| `view3d_light_unsupported` | A payload includes public `View3D` light state or requests ambient/directional lighting in S038. |
| `view3d_light_invalid` | Future/experimental light state has invalid parameters. Not required for accepted S038. |
| `texture2d_unsupported` | A payload declares or references a public `Texture2D`. |
| `mesh3d_uv_unsupported` | A mesh payload includes UV coordinates. |
| `mesh3d_texture_material_unsupported` | A material requests texture sampling, texture/color combination, or a sampler. |
| `mesh3d_color_space_not_strict` | A renderer or request tries to claim linear/sRGB/tone-mapped material semantics that S038 does not define. |
| `mesh3d_alpha_not_strict` | Existing diagnostic for non-opaque 3D mesh alpha where strict compositing is unsupported. |
| `mesh3d_depth_adapted` | Existing diagnostic for adapted 3D mesh depth ordering, such as Matplotlib face sorting. |

Unsupported material, light, normal, texture, or UV concepts must not be silently ignored when a
public payload requests them.

## Backend Conformance

Matplotlib may claim `meshvisual.material.unlit_rgba.v1` only for accepted `MeshVisual` color modes it
preserves. It must not use public lighting, generated normals, texture sampling, Phong calculation,
or backend material state to alter strict unlit colors. Matplotlib's 3D mesh output remains adapted:
3D vertices are CPU-projected to 2D collections and opaque depth is approximated by face sorting.

Datoviz may claim `meshvisual.material.unlit_rgba.v1` only when retained mesh colors are preserved
with implicit lighting disabled and without exposing Datoviz-native material structs, shader slots,
Vulkan state, or camera/controller objects. Datoviz native depth testing is separate from material
conformance.

VisPy2-style producers may offer helpers that emit canonical `MeshVisual` RGBA colors. They must not
define public `MeshMaterial3D`, Lambert, Phong, `Texture2D`, sampler, UV, or light semantics before a
later accepted spec.

## Fixtures

Before a backend advertises strict `meshvisual.material.unlit_rgba.v1`, conformance should include:

- a uniform opaque `(N, 3)` DATA triangle in `View3D` whose color is unchanged by camera orientation,
  depth, or private backend light state;
- a per-face opaque mesh whose faces keep their assigned colors without lighting gradients;
- a per-vertex color fixture only for renderers that already claim accepted per-vertex color support;
- overlapping opaque triangles proving material color is separate from existing depth behavior;
- a non-opaque alpha fixture that preserves `mesh3d_alpha_not_strict`;
- negative fixtures for material objects, Lambert/Phong requests, normals, lights, textures, UVs,
  samplers, and texture materials.

Adding S038 unlit material semantics must not perturb `View3DProjectionSnapshot` identity except
where accepted mesh visual payload serialization legitimately changes. View/projection query payloads
remain unaffected.

## Deferred Work

S039 accepts a narrow flat Lambert face-normal extension. S050 accepts a narrow unlit Texture2D/UV
extension. Concepts still deferred after S050 include vertex normals, smooth Lambert, Phong,
specular, shininess, public sampler objects, transparency sorting, culling expansion, shadows, PBR,
model loading, instancing, and scene graph semantics.

Any next material expansion must be a separate evidence-backed ADR and must not silently expand the
accepted S038/S039/S050 material boundaries.
