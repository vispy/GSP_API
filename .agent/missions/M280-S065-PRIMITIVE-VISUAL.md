# M280 - S065 bounded PrimitiveVisual end-to-end

## Status

Draft; promote after M279. Target repositories: `gsp`, `vispy2`; Datoviz is read-only evidence.

## Goal

Add a capability-gated generic geometry escape hatch without weakening GSP's semantic boundary.

## Required scope

- Section 6 of `.agent/S065_TECHNICAL_BASELINE.md`.
- Exact topology/cardinality/index validation and stable diagnostics.
- Datoviz public primitive constructor/index lowering.
- Matplotlib deterministic point/line/triangle lowering with explicit adaptation.
- VisPy2 2D/3D/module-level producers.
- Tests for every topology, indexed/unindexed input, malformed cardinality, range, dimensions,
  colors, views, capability rejection, and no raw GPU keywords.
- Installed-wheel topology gallery.

## Acceptance

All five bounded topologies work. Public signatures contain no shader, pipeline, slot, material,
depth, culling, instance, or native-handle escape. Full source/wheel gates pass.

## Stop conditions

Stop if a topology cannot be defined without raw backend state or if a proposed convenience
duplicates a richer semantic visual with conflicting meaning.

