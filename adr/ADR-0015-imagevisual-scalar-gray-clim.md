# ADR-0015 - ImageVisual scalar gray and clim baseline

## Status

Accepted

## Context

S023 ImageVisual hardening needed scalar image behavior without introducing a broad colormap,
normalization, or colorbar system.

## Decision

S023 accepts a conservative scalar image baseline:

- scalar images are eager `(H, W)` arrays;
- uint8 scalar images use native values;
- float scalar images may contain any finite values;
- `ImageColormap.GRAY` is the only accepted v1 colormap;
- `clim=(vmin, vmax)` is optional and applies only to scalar images;
- RGB/RGBA float images remain constrained to `[0, 1]`.

Matplotlib maps scalar images with gray colormap and optional clim. Datoviz v0.4 converts scalar
gray images to RGBA8 for sampled-field or texture upload.

## Consequences

Broader colormap registries, normalization modes, colorbars, tiled/remote images, and volumes remain
future work.
