# S026 Color Mapping Contract Decisions

Status: accepted by M091 from P011 response.

## Accepted

- Public v1 defines `ColorScale`, named `ColorMapRef`, `LinearNormalize`, `ScalarColorEncoding`,
  and `ColorbarGuide`.
- Canonical named colormaps are `gray`, `viridis`, `magma`, `plasma`, `inferno`, and `cividis`.
- Accepted colormaps are defined by canonical 256-entry RGBA uint8 LUTs.
- Strict normalization is explicit linear `vmin < vmax` with clipping.
- Strict scalar visual slots are scalar `ImageVisual` texels, `PointVisual.color`, and
  `MarkerVisual.fill`.
- `ColorbarGuide` is a semantic guide linked to a `ColorScale`, not a visual.
- Scalar query/readback reports source scalar value, raw/clipped normalized value, range class,
  LUT index, and displayed RGBA.

## Capability-Gated

- `MeshVisual` per-face scalar color for strict 2D flat meshes.
- Datoviz GPU normalization and canonical LUT upload.
- Non-Matplotlib colorbar rendering.
- Scalar/colorbar query where the backend cannot reconstruct source scalar values.

## Deferred

Arbitrary Matplotlib colormap names, user-defined continuous colormaps, embedded public LUT
resources, categorical palettes, legends, log/symlog/power/two-slope/boundary norms, auto/percentile
limits as protocol semantics, NaN/masked/bad colors, custom under/over colors, segment/path scalar
strokes, text scalar colors, marker scalar stroke, mesh vertex scalar colors, volume transfer
functions, and remote chunk-wise dynamic normalization.

## Source

`.agent/consultations/P011-response.md` converted into ADR-0018 and `spec/color_mapping.md`.
