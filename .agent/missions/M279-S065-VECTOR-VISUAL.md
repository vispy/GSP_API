# M279 - S065 VectorVisual end-to-end

## Status

Draft; promote after M278. Target repositories: `gsp`, `vispy2`; Datoviz is read-only evidence.

## Goal

Implement straight semantic vectors with useful 2D/3D high-level APIs.

## Required scope

- Section 5 of `.agent/S065_TECHNICAL_BASELINE.md`.
- Protocol enums/dataclass/validation, capability IDs, fixtures, and exports.
- Datoviz `dvz_vector` plus public style descriptor mapping.
- Deterministic Matplotlib 2D/3D line/head adaptation.
- VisPy2 `vectors()` and bounded `quiver()` alias without Matplotlib API emulation.
- Tests for anchors, scale, caps, widths, zero/nonfinite vectors, dimensions, views, and capabilities.
- Installed-wheel vector-field examples in 2D and 3D.

## Acceptance

Tail/center/head placement and scale resolve identically before backend lowering. Datoviz preserves
item identity. Backend head-shape differences are declared. Full source/wheel gates pass.

## Stop conditions

Stop if implementation requires curved paths, per-item caps, raw Datoviz style structures, or
ambiguous DATA-vs-screen vector lengths.

