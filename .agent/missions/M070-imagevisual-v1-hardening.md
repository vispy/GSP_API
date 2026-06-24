# M070 - ImageVisual v1 hardening

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Completed.

## Summary

Stabilize ImageVisual dtype/origin/extent/interpolation/colormap/clim behavior and the Datoviz
sampled-field path.

## Planned Deliverables

- Image spec update and colormap/clim decision.
- Validation for scalar/RGB/RGBA image forms.
- Matplotlib reference mapping.
- Datoviz v0.4 sampled-field or texture adapter with origin via texcoords.
- QA cases for checker/origin/scalar/RGBA and interpolation capability gates.

## Completed

- Added bounded `ImageColormap.GRAY` and scalar-image `clim` semantics to `ImageVisual`.
- Hardened ImageVisual validation for scalar/RGB/RGBA shapes, finite extents, scalar clim, and float ranges.
- Updated Matplotlib mapping for scalar gray colormap/clim.
- Updated Datoviz mapping to render scalar gray images and float RGB/RGBA through RGBA8 sampled-field/texture paths.
- Added S023 QA cases for lower origin, scalar gray/clim, and RGBA alpha.
- Updated image/backend/VisPy2 specs.

## Acceptance

Checker/origin/scalar/RGBA cases render in Matplotlib. Datoviz nearest/sampled-field cases render or
report field/scale/interpolation limitations.

## Stop Condition

Do not expand into tiled/virtual images, colorbars, volumes, remote data, or advanced normalization.
