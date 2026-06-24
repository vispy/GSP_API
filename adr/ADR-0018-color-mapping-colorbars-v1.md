# ADR-0018 - Color mapping and colorbars v1

## Status

Accepted

## Context

S026 follows the accepted visual-family baseline through S025. The project already supports scalar
`ImageVisual` data through a narrow gray/clim path, but broad color systems risk copying Matplotlib
`ScalarMappable`/`Normalize` internals or Datoviz shader/slot details into public GSP protocol.

Color mapping also affects query/readback: a hit must be able to report the source scalar value,
normalized/clipped value, and displayed RGBA without reverse-engineering backend colors.

## Decision

S026 accepts a small public scalar color system:

- `ColorScale` is the shared semantic mapping resource for scalar-to-color behavior.
- `ColorMapRef` v1 supports named canonical GSP colormaps only.
- Accepted colormap ids are `gray`, `viridis`, `magma`, `plasma`, `inferno`, and `cividis`.
- Each accepted colormap is defined by a canonical 256-entry RGBA uint8 lookup table.
- `LinearNormalize` is the only strict v1 normalization policy. It requires finite `vmin < vmax`
  and clipping to the endpoint colors.
- Protocol scenes must use explicit limits. Auto/percentile limits are producer conveniences only
  and must be resolved before emitting GSP.
- `ScalarColorEncoding` is an alternative encoding for a specific visual color slot. It is mutually
  exclusive with RGBA on that same slot.
- Strict v1 scalar visual slots are scalar `ImageVisual` texels, `PointVisual.color`, and
  `MarkerVisual.fill`.
- `MeshVisual.face_color` scalar encoding is capability-gated for strict 2D flat meshes.
- Segment/path scalar strokes, marker stroke scalar colors, text scalar colors, mesh vertex scalar
  colors, categorical palettes, legends, log/symlog/power/two-slope/boundary norms, NaN/masked/bad
  colors, custom under/over colors, and embedded/user LUT resources are deferred.
- `ColorbarGuide` is a semantic guide linked to a `ColorScale`, not a data visual, backend mappable,
  or layout object. It supports orientation, placement, label, explicit ticks, and explicit tick
  labels.
- Scalar query/readback uses `gsp.scalar-color-query@0.1`; colorbar ramp query uses
  `gsp.colorbar-query@0.1` when guide-query capability supports it.
- Backends may pre-map eager finite scalar arrays to RGBA as an explicit adaptation, but must retain
  scalar source values server-side if they claim scalar query/readback support.

## Consequences

Workers can implement deterministic validation, canonical LUT sampling, Matplotlib reference output,
scalar query/readback, visual QA cases, and Datoviz capability diagnostics without freezing a broad
backend-specific color architecture. Existing `ImageVisual(gray, clim)` behavior can be treated as a
compatibility mapping to `ColorScale(gray, LinearNormalize(vmin, vmax))`, while new S026 scenes use
explicit color scales.
