# S059 Texture2D nearest-or-linear filtering extension

Date: 2026-07-22

## Objective

Implement the P036 decision as the smallest source-compatible extension of the accepted S050
Texture2D contract: visual-owned `TextureFilter.NEAREST|LINEAR`, nearest by default, a separate
linear renderer capability, and no public sampler object or additional sampler controls.

## Proposed sequence

| Mission | State | Scope |
|---|---|---|
| M249 | ready | Convert P036 into ADR-0034 and the normative spec/capability/diagnostic baseline. |
| M250 | draft | Add the enum, appended MeshVisual field, validation, serialization behavior, and backend-neutral reference fixtures. |
| M251 | draft | Add the single VisPy2 `texture_filter` producer keyword and producer capability. |
| M252 | draft | Map nearest/linear to Datoviz field-slot state and promote only after real offscreen conformance. |
| M253 | draft | Update examples/docs/checkpoint coverage, run full validation, and close S059. |

## Accepted P036 direction

- Sampling state belongs to `MeshVisual`, not immutable `Texture2D` data.
- `texture_filter` is appended as a defaulted field and defaults to nearest.
- One enum controls matching minification and magnification.
- Linear means base-level bilinear interpolation of normalized unmanaged straight-alpha RGBA code
  values, followed by base-color multiplication, with `2/255` per-channel conformance tolerance.
- `meshvisual.material.texture2d_unlit.v1` retains its nearest guarantee.
- `meshvisual.texture_filter.linear.v1` is a separate renderer capability.
- Matplotlib remains explicitly unsupported for all textured meshes.

## Guardrails

- Preserve old payload decoding and nearest rendering exactly.
- Do not add resource-owned filtering, sampler resources, independent min/mag, wrap selection,
  mipmaps/LOD, anisotropy, color management, extra texture formats, or textured lighting.
- Do not advertise Datoviz linear support from symbols or mocks alone.
- Stop on any conflict with ADR-0029, ambiguous serialization compatibility, or native result
  outside the accepted tolerance.

## Approval

Awaiting project-owner approval in Mission Control.
