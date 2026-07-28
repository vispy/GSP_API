# M297 - S066 live flat-Lambert presentation polish

## Status

Owner-approved on 2026-07-28 for execution with the pinned
`codex-ucl-gpt-5.6-sol-medium` provider. This is a bounded VisPy2 producer/example mission; it does
not reopen S065 and does not expand GSP material semantics.

## Baseline and finding

- VisPy2 baseline `625279a` contains the owner-accepted S065 producer, gallery, and interaction
  review.
- Gallery 5 proves live Datoviz orbit, pan, zoom, reset, and cleanup, but its tetrahedron uses the
  default `MeshShading.UNLIT_RGBA` with one uniform blue color.
- The owner accepted the behavior but found the presentation unattractive.
- GSP already defines and both adapters already implement the strict S039 flat-Lambert path:
  `MeshShading.FLAT_LAMBERT`, face normals or `FACE_FLAT` generation,
  `View3D.ambient_light_intensity`, and one `DirectionalLight3D`.
- VisPy2 already exposes the canonical mesh shading/normal fields but has no concise high-level
  helper for View3D light state.

## Goal

Make the live camera example visibly convey 3D shape using the existing strict, backend-neutral
flat-Lambert contract, while keeping the public surface minimal and preserving all camera and
lifecycle behavior.

## Required implementation

### Typed VisPy2 lighting convenience

Add one typed `Axes3D.set_lighting(...) -> View3D` convenience that emits only accepted GSP fields.
Use protocol-aligned names and defaults:

- `ambient_light_intensity: float`;
- `direction_to_light: ArrayLike | None`;
- `directional_light_intensity: float = 1.0`.

When `direction_to_light` is not `None`, construct a canonical `DirectionalLight3D` after resolving
an exact finite float3. When it is `None`, store no directional light. Delegate range, finiteness,
and nonzero validation to accepted GSP constructors rather than duplicating or weakening it.
Increment `View3D.revision` exactly once and return the new semantic `View3D`. Do not expose backend
objects, material objects, shader names, or Datoviz concepts.

`reset_camera()` promises to restore camera and projection. Ensure it preserves the current
lighting fields, depth mode, identity, and other non-camera View3D semantics while restoring only
the construction camera/projection and incrementing revision. Orbit, pan, zoom, fit, scene
serialization, and session-driven navigation must likewise retain lighting.

### Gallery 5 presentation

Update `examples/gallery_05_datoviz_navigation.py` to:

- use `shading="flat_lambert"`;
- use generated canonical face normals with `normal_mode="face"` and
  `normal_generation="face_flat"`;
- set a restrained nonzero ambient term plus one directional light through the new VisPy2 helper;
- retain the existing tetrahedron geometry, camera fit, title, controls, experimental opt-in,
  bounded frame pumping, capability checks, interrupt handling, and cleanup.

Require the relevant flat-Lambert, normal-generation, ambient-light, and directional-light
capabilities before native resource creation if the current caller-owned session requirement API
supports exact capability names. Otherwise preserve existing provider selection and prove the
adapter capability snapshot explicitly before display. Fail closed with a useful diagnostic; never
silently fall back to unlit rendering.

### Tests and documentation

Add focused tests proving:

- exact ambient and directional protocol state;
- revision increments once;
- `None` clears the directional light;
- invalid ambient, intensity, non-finite, wrong-shape, and zero directions fail through canonical
  validation;
- scene serialization retains the light state;
- orbit/pan/zoom/fit retain light state;
- reset restores only camera/projection and retains light state;
- Gallery 5 emits flat Lambert, generated face normals, and explicit lighting without weakening its
  lifecycle tests.

Update the user-facing Gallery 5 documentation and example index to describe flat diffuse shading
and the intentionally narrow lighting model. Do not advertise smooth normals, Phong/specular,
colored/multiple lights, material objects, or native Datoviz lighting.

## Required validation

- Focused VisPy2 View3D and Gallery 5 tests.
- Full VisPy2 pytest.
- Strict mypy for `src`, `tests`, and `examples`.
- Ruff for `src`, `tests`, and `examples`.
- Documentation Python-block and local-link validation.
- `git diff --check`.
- Build the VisPy2 wheel and prove producer-only installation with `gsp-core`.
- Run a Matplotlib static render of the same lit scene and verify distinct deterministic face
  colors.
- Mission Control will perform the native Datoviz live-window and bounded-interrupt qualification
  outside the worker sandbox after integration.

## Acceptance

- Public VisPy2 lighting configuration is typed, backend-neutral, and limited to accepted S039
  fields.
- The live tetrahedron has visibly distinct flat-Lambert face intensities.
- Camera navigation and reset preserve light state.
- No GSP or Datoviz source change is needed.
- All required gates pass and independent review issues unconditional ACCEPT.

## Stop conditions

- Stop on any need for new GSP protocol fields, changed Lambert arithmetic, public material
  objects, smooth/vertex normals, multiple/colored lights, or backend-native lighting controls.
- Stop on a source/spec contradiction or if an adapter lacks the already advertised S039
  capabilities.
- Stop rather than silently falling back to unlit rendering or weakening lifecycle/capability
  checks.
- Do not edit GSP_API, GSP, or Datoviz from the worker.
- Do not push, merge, tag, release, publish packages, create a PR, or change versions.
