# P025 - Datoviz S039 Flat Lambert Strict Promotion

This needs ChatGPT Pro consultation.

## Prompt

You are reviewing a backend architecture decision for `GSP_API`, a Python visualization
protocol/library with Matplotlib and Datoviz v0.4 backends plus a VisPy2-style producer API. The
question is whether the Datoviz v0.4 adapter should promote strict support for the already accepted
S039 flat Lambert face-normal material semantics, and if yes, which implementation route is safest.

Please answer as a protocol/backend architect, not as code generation. The expected output format is
at the end.

### Project Authority and Constraints

Authority order in this repo is:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/**`
5. accepted ADRs in `adr/**` and `.agent/decisions/**`
6. `LEGACY_MAP.md`
7. existing source code

Existing code is implementation material, not automatically authoritative. If code conflicts with
accepted specs, specs win.

The public protocol is backend-neutral. It must not expose backend-native Datoviz material structs,
Vulkan/draw-state names, shader slots, controller objects, Matplotlib artists/axes, or legacy GSP
material classes as public API.

### Accepted S039 Semantics

S039 accepted only a narrow flat Lambert diffuse shading model:

- `MeshVisual.shading = "flat_lambert"`;
- DATA-space `(N,3)` triangle meshes in a resolved `View3D`;
- face normals only;
- explicit `(F,3)` normals with `normal_mode="face"` and `normal_generation="none"`, or generated
  normals with `normal_mode="face"`, `normals is None`, and `normal_generation="face_flat"`;
- generated normals use `cross(p1 - p0, p2 - p0)` in DATA coordinates;
- generated normals fail on non-triangle, degenerate, or non-finite inputs;
- input normals are normalized by the protocol and fail if zero-length or non-finite;
- normals and directional lights are in DATA coordinates;
- `View3D.ambient_light_intensity` is a scalar white ambient term in `[0,1]`;
- `DirectionalLight3D.direction_to_light` is a finite non-zero DATA-space vector from shaded point
  toward the light;
- `DirectionalLight3D.intensity` is scalar in `[0,1]`;
- if no directional light exists, directional term is zero;
- `D = directional_light.intensity * max(0, dot(normalize(n), normalize(direction_to_light)))`;
- `L = clamp(ambient_light_intensity + D, 0, 1)`;
- `output.rgb = clamp(base.rgb * L, 0, 1)`;
- `output.a = base.a`;
- non-opaque 3D mesh alpha remains non-strict and reports `mesh3d_alpha_not_strict`;
- S039 does not define linear RGB, sRGB conversion, gamma correction, tone mapping, or display
  color-management semantics.

Accepted S039 capabilities:

```text
meshvisual.material.flat_lambert.v1
meshvisual.normals.face3d.v1
meshvisual.normal_generation.face_flat.v1
view3d.light.ambient.v1
view3d.light.directional.v1
```

Prerequisite capabilities:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
meshvisual.material.unlit_rgba.v1
```

Deferred concepts:

- vertex normals and smooth Lambert;
- Phong/specular/shininess;
- textures, UVs, samplers, normal maps;
- multiple lights, colored lights, point/spot lights, attenuation;
- scene graph or material resource system;
- backend-native material/shader/draw-state names in public API.

### Current Implementation State

Protocol and validation are implemented:

- `MeshShading.UNLIT_RGBA`;
- `MeshShading.FLAT_LAMBERT`;
- `MeshNormalMode.FACE`;
- `MeshNormalGeneration.FACE_FLAT`;
- `DirectionalLight3D`;
- `View3D.ambient_light_intensity`;
- `View3D.directional_light`;
- `validate_mesh_visual_flat_lambert(visual, view3d=...)`;
- `MeshVisual.normalized_face_normals()`.

Matplotlib/reference path is implemented by CPU-resolving face colors before the existing adapted 3D
mesh raster path. This is strict for the S039 material arithmetic, but the broader Matplotlib 3D
rendering path remains adapted/review-oriented.

VisPy2-style producer helpers emit canonical S039 fields.

Datoviz currently rejects S039 Lambert explicitly:

```python
def _validate_datoviz_mesh3d_visual(visual: MeshVisual, view3d: View3D | None) -> None:
    if visual.canonical_shading() is MeshShading.FLAT_LAMBERT:
        raise DatovizV04Unsupported(
            "flat_lambert_unsupported: Datoviz v0.4 strict S039 flat Lambert "
            "support is not implemented; native material semantics are not "
            "accepted as protocol evidence"
        )
```

The Datoviz capability snapshot intentionally does not advertise
`meshvisual.material.flat_lambert.v1`.

Existing Datoviz mesh path facts:

- Datoviz v0.4 path uses the C-shaped facade, not old `datoviz.App` wrappers.
- Required mesh functions include:

```text
dvz_mesh
dvz_visual_set_data
dvz_visual_set_index_data
dvz_visual_set_depth_test
```

- Static View3D DATA-space `(N,3)` mesh rendering is implemented for local v0.4-dev builds using
  Datoviz camera bindings and explicit orthographic bounds.
- Opaque depth is available through Datoviz depth testing.
- Existing 3D Datoviz validation rejects non-opaque mesh colors as non-strict.
- Per-face RGBA in 2D mesh paths has historically been adapted by duplicating vertices where
  necessary.
- Legacy/internal Datoviz renderer code in the repo references old wrapper APIs with
  `lighting=False`, `set_normal()`, and `set_color()`, but that legacy path is not public protocol
  authority and does not prove strict S039 support.

### Candidate S040 Routes

1. **CPU-resolved exact per-face colors**
   - Run the same accepted S039 material arithmetic in the Datoviz adapter.
   - Convert each canonical face to an unlit RGBA color.
   - If Datoviz interpolates vertex colors, duplicate vertices per face so every triangle vertex has
     the same resolved face color.
   - Keep Datoviz native lighting disabled or unused.
   - Advertise S039 capabilities only after fixtures prove exact face-level output and existing
     View3D/depth prerequisites are present.

2. **Native Datoviz lighting/material path**
   - Upload normals and use Datoviz v0.4 native material/light/lighting controls if they exist.
   - Claim strict support only if Datoviz native semantics exactly match S039: DATA-space normals,
     DATA-space direction-to-light, flat face normals, no vertex interpolation, exact scalar ambient
     plus directional formula, alpha passthrough, and no backend color-management surprises.
   - Avoid exposing native material names or fields publicly.

3. **Keep unsupported**
   - Preserve explicit `flat_lambert_unsupported`.
   - Do not advertise `meshvisual.material.flat_lambert.v1`.
   - Document Datoviz as unsupported for strict S039 until better API evidence exists.

### Questions To Answer

1. Should S040 promote Datoviz strict S039 flat Lambert support now, or keep it unsupported?
2. If promoted, should the implementation route be CPU-resolved exact face colors, native Datoviz
   lighting, or a hybrid?
3. Is CPU-resolved per-face color an acceptable strict implementation of S039 for Datoviz, given
   that S039 specifies output colors rather than requiring a live lighting engine?
4. What exact conditions must hold before CPU-resolved colors can advertise
   `meshvisual.material.flat_lambert.v1`?
5. How should per-face colors be uploaded to avoid Datoviz vertex-color interpolation changing S039
   face-level results?
6. Should generated face normals be computed before any Datoviz upload, using protocol code, rather
   than relying on Datoviz normal generation?
7. Should native Datoviz lighting be considered strict only after API probes prove exact matching
   semantics, or should it remain out of scope for S040?
8. What capability dependencies should Datoviz advertise if CPU-resolved S039 is implemented?
9. What diagnostics should distinguish CPU-resolved strict support, native-lighting unsupported, and
   alpha non-strict behavior?
10. What positive and negative fixtures are required before changing the current Datoviz gate?
11. What, if anything, needs an ADR/spec/backend-spec update rather than just implementation tests?
12. Under what conditions should S040 close with "keep unsupported" and move to release preparation?

### Decision Constraints

- Do not change accepted S039 public protocol semantics.
- Do not add vertex normals, smooth shading, Phong, textures, UVs, samplers, multiple lights, or a
  material object.
- Do not expose Datoviz native material/light/shader/draw-state names as public API.
- Prefer exact deterministic output over backend-native elegance.
- Distinguish strict support, adapted review support, and unsupported behavior.
- Capability advertisement must be conservative and fixture-backed.

## Expected Output Format

Please answer in this exact structure:

1. **Recommendation**
   - One paragraph choosing CPU-resolved strict support, native Datoviz lighting, hybrid, or keep
     unsupported.

2. **Promotion Criteria**
   - Bullet list of exact requirements before Datoviz may advertise S039 capabilities.

3. **Implementation Route**
   - Specific Datoviz adapter approach, including where normals and colors should be resolved.

4. **Capability Advertisement**
   - Table with capability string, whether Datoviz may advertise it under the recommended route,
     and prerequisites.

5. **Diagnostics**
   - Table with diagnostic code, trigger, and wording.

6. **Fixtures**
   - Positive fixtures and negative fixtures required before promotion.

7. **ADR/Spec Updates**
   - State whether a new ADR is required, whether backend spec docs are enough, and what files or
     sections should be updated.

8. **Risks and Stop Conditions**
   - Conditions that should keep Datoviz S039 Lambert unsupported.
