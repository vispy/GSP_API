# M070 - ImageVisual v1 hardening

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Draft.

## Summary

Stabilize ImageVisual dtype/origin/extent/interpolation/colormap/clim behavior and the Datoviz
sampled-field path.

## Planned Deliverables

- Image spec update and colormap/clim decision.
- Validation for scalar/RGB/RGBA image forms.
- Matplotlib reference mapping.
- Datoviz v0.4 sampled-field or texture adapter with origin via texcoords.
- QA cases for checker/origin/scalar/RGBA and interpolation capability gates.

## Acceptance

Checker/origin/scalar/RGBA cases render in Matplotlib. Datoviz nearest/sampled-field cases render or
report field/scale/interpolation limitations.

## Stop Condition

Do not expand into tiled/virtual images, colorbars, volumes, remote data, or advanced normalization.
