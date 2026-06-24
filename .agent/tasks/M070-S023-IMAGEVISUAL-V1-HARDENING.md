# M070-S023-IMAGEVISUAL-V1-HARDENING - ImageVisual v1 hardening

## Mission

M070

## Goal

Turn the existing ImageVisual slice into an explicit v1 contract with QA-backed Matplotlib and
Datoviz behavior.

## Contract Starting Point

Fields:

```text
id
image
extent
coordinate_space
interpolation
origin
colormap
clim
```

For S023, keep scalar/RGB/RGBA images in memory. Remote, tiled, virtual, and chunked images remain
out of scope despite S020-S022 groundwork.

## Backend Mapping

- Matplotlib: `imshow` with explicit extent, origin, interpolation, colormap, and clim.
- Datoviz v0.4: use `dvz_image`, corner `"position"` plus `"texcoords"`; use sampled fields and
  scale/colormap APIs if available. Capability-gate interpolation when no sampler control is found.

## Acceptance

- Validation covers shape, dtype, finite values, origin, interpolation, scalar clim/colormap rules.
- QA cases cover nearest checkerboard, origin flip, scalar colormap/clim, RGBA alpha.
- Datoviz unsupported report is explicit for sampled-field, scale, or interpolation gaps.

## Stop Conditions

- Stop if implementation requires remote data, persistent caches, tiles, volumes, or colorbars.
- Stop if image work starts designing Text/Glyph or Mesh dependencies.

## Completion Notes

- Implemented bounded ImageVisual v1 hardening: scalar gray colormap, optional scalar clim, finite extent validation, scalar float finite values, and RGB/RGBA float `[0, 1]` validation.
- Kept broader colormap registries, normalization systems, colorbars, tiled/remote images, and volumes out of scope.
- Added visual QA cases:
  - `image/origin_lower_ndc`
  - `image/scalar_gray_clim_ndc`
  - `image/rgba_alpha_ndc`
- Regenerated `artifacts/visual_qa/s023/latest-local/contact_sheets/s023_all_cases.png`; all Matplotlib and Datoviz cases rendered.
- Validation passed:
  - `uv run pytest tests -q`
  - `uv run mypy src/ --strict --show-error-codes`
